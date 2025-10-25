"""
Reconciliation service for generating data matching rules from knowledge graphs.

This service analyzes knowledge graphs to automatically generate reconciliation rules
that can be used to match, link, and validate data across different schemas/systems.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from kg_builder.models import (
    ReconciliationRule,
    ReconciliationRuleSet,
    ReconciliationMatchType,
    DatabaseSchema
)
from kg_builder.services.schema_parser import SchemaParser
from kg_builder.services.falkordb_backend import FalkorDBBackend
from kg_builder.config import FALKORDB_HOST, FALKORDB_PORT, FALKORDB_PASSWORD

logger = logging.getLogger(__name__)


def generate_uid() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())[:8].upper()


class ReconciliationRuleGenerator:
    """Generate reconciliation rules from knowledge graph analysis."""

    def __init__(self):
        """Initialize the rule generator."""
        self.schema_parser = SchemaParser()
        from kg_builder.services.falkordb_backend import get_falkordb_backend
        from kg_builder.services.graphiti_backend import get_graphiti_backend
        self.falkordb = get_falkordb_backend()
        self.graphiti = get_graphiti_backend()

    def generate_from_knowledge_graph(
        self,
        kg_name: str,
        schema_names: List[str],
        use_llm: bool = True,
        min_confidence: float = 0.7,
        field_preferences: Optional[List[Dict[str, Any]]] = None
    ) -> ReconciliationRuleSet:
        """
        Main entry point for rule generation from a knowledge graph.

        Args:
            kg_name: Name of the knowledge graph to analyze
            schema_names: List of schema names involved
            use_llm: Whether to use LLM for semantic rule generation
            min_confidence: Minimum confidence score for rules (0.0-1.0)
            field_preferences: User-specific field preferences for rule generation

        Returns:
            ReconciliationRuleSet containing generated rules
        """
        logger.info(f"Generating reconciliation rules from KG '{kg_name}'")

        # Auto-load field_preferences from KG metadata if not provided
        if not field_preferences:
            kg_metadata = self.graphiti.get_kg_metadata(kg_name)
            if kg_metadata and 'field_preferences' in kg_metadata:
                field_preferences = kg_metadata['field_preferences']
                logger.info(f"Auto-loaded field_preferences from KG metadata: {len(field_preferences)} preference(s)")

        # 1. Load schemas
        schemas_info = self._load_schemas(schema_names)

        # 2. Query KG for relationships
        relationships = self._get_kg_relationships(kg_name)

        # 3. Generate basic rules from patterns
        basic_rules = self._generate_pattern_based_rules(
            relationships, schemas_info, schema_names
        )

        # 4. Enhance with LLM if enabled
        if use_llm:
            llm_rules = self._generate_llm_rules(relationships, schemas_info, field_preferences=field_preferences)
            all_rules = basic_rules + llm_rules
        else:
            all_rules = basic_rules

        # 5. Filter by confidence
        filtered_rules = [r for r in all_rules if r.confidence_score >= min_confidence]

        # 6. Remove duplicates
        unique_rules = self._deduplicate_rules(filtered_rules)

        # 7. Create ruleset
        ruleset = ReconciliationRuleSet(
            ruleset_id=f"RECON_{generate_uid()}",
            ruleset_name=f"Reconciliation_{kg_name}",
            schemas=schema_names,
            rules=unique_rules,
            created_at=datetime.utcnow(),
            generated_from_kg=kg_name
        )

        logger.info(
            f"Generated {len(unique_rules)} reconciliation rules "
            f"({len(basic_rules)} pattern-based, {len(llm_rules) if use_llm else 0} LLM-based)"
        )

        return ruleset

    def _load_schemas(self, schema_names: List[str]) -> Dict[str, DatabaseSchema]:
        """Load schema information for analysis."""
        schemas = {}
        for schema_name in schema_names:
            try:
                schema = self.schema_parser.load_schema(schema_name)
                schemas[schema_name] = schema
                logger.debug(f"Loaded schema: {schema_name}")
            except Exception as e:
                logger.error(f"Failed to load schema {schema_name}: {e}")
                raise
        return schemas

    @staticmethod
    def _extract_database_name(database_url: str) -> str:
        """
        Extract database name from connection URL.

        Supports:
        - MySQL: mysql+mysqlconnector://user:pass@host:port/database?charset=utf8mb4
        - Oracle: oracle://user:pass@host:port/database
        - PostgreSQL: postgresql://user:pass@host:port/database
        - SQL Server: mssql+pyodbc://user:pass@host:port/database

        Args:
            database_url: Database connection URL

        Returns:
            Database name or empty string if not found
        """
        if not database_url:
            return ""

        try:
            # Remove query parameters
            url_without_params = database_url.split('?')[0]

            # Extract the part after the last slash
            parts = url_without_params.split('/')
            if len(parts) > 0:
                db_name = parts[-1]
                return db_name if db_name else ""

            return ""
        except Exception as e:
            logger.warning(f"Failed to extract database name from URL: {database_url}, error: {e}")
            return ""

    def _get_kg_relationships(self, kg_name: str) -> List[Dict[str, Any]]:
        """Query knowledge graph for all relationships."""
        try:
            # Query all relationships from FalkorDB including source/target columns
            query = """
            MATCH (source)-[r]->(target)
            RETURN
                source.label AS source_table,
                target.label AS target_table,
                type(r) AS relationship_type,
                properties(r) AS properties,
                r.source_column AS source_column,
                r.target_column AS target_column
            """

            # Execute query against FalkorDB (use generic 'query' method)
            result = self.falkordb.query(kg_name, query)

            relationships = []
            for record in result:
                props = record.get('properties', {})

                # Add source_column and target_column to properties if available
                source_col = record.get('source_column')
                target_col = record.get('target_column')

                if source_col and 'source_column' not in props:
                    props['source_column'] = source_col
                if target_col and 'target_column' not in props:
                    props['target_column'] = target_col

                relationships.append({
                    'source_table': record.get('source_table'),
                    'target_table': record.get('target_table'),
                    'relationship_type': record.get('relationship_type'),
                    'properties': props,
                    'source_column': source_col,
                    'target_column': target_col
                })

            logger.debug(f"Retrieved {len(relationships)} relationships from KG '{kg_name}'")
            return relationships

        except Exception as e:
            logger.error(f"Error querying KG relationships: {e}")
            return []

    def _generate_pattern_based_rules(
        self,
        relationships: List[Dict[str, Any]],
        schemas_info: Dict[str, DatabaseSchema],
        schema_names: List[str]
    ) -> List[ReconciliationRule]:
        """Generate rules from naming patterns and structural analysis."""
        rules = []

        # For single schema: use all relationships (intra-schema joins)
        # For multiple schemas: use cross-schema relationships
        if len(schema_names) == 1:
            # Single schema: include all relationship types from KG
            relevant_rels = [
                rel for rel in relationships
                if rel.get('relationship_type') in ['REFERENCES', 'FOREIGN_KEY', 'CROSS_SCHEMA_REFERENCE',
                                                     'SEMANTIC_REFERENCE', 'INFERRED']
            ]
        else:
            # Multiple schemas: only cross-schema relationships
            relevant_rels = [
                rel for rel in relationships
                if rel.get('relationship_type') in ['CROSS_SCHEMA_REFERENCE', 'FOREIGN_KEY']
            ]

        for rel in relevant_rels:
            source_table = rel.get('source_table')
            target_table = rel.get('target_table')
            properties = rel.get('properties', {})

            # Skip if tables are not found
            if not source_table or not target_table:
                continue

            # For single schema, both source and target schema are the same
            # For multiple schemas, extract from properties
            if len(schema_names) == 1:
                source_schema = schema_names[0]
                target_schema = schema_names[0]
            else:
                # Extract source and target schemas
                source_schema = properties.get('source_schema', schema_names[0] if len(schema_names) > 0 else '')
                target_schema = properties.get('target_schema', schema_names[1] if len(schema_names) > 1 else '')

            # Pattern 1: Foreign Key relationships
            if rel.get('relationship_type') == 'FOREIGN_KEY':
                source_cols = properties.get('source_columns', [])
                target_cols = properties.get('target_columns', [])

                if source_cols and target_cols:
                    rules.append(ReconciliationRule(
                        rule_id=f"RULE_{generate_uid()}",
                        rule_name=f"FK_{source_table}_{target_table}",
                        source_schema=source_schema,
                        source_table=source_table,
                        source_columns=source_cols if isinstance(source_cols, list) else [source_cols],
                        target_schema=target_schema,
                        target_table=target_table,
                        target_columns=target_cols if isinstance(target_cols, list) else [target_cols],
                        match_type=ReconciliationMatchType.EXACT,
                        transformation=None,
                        confidence_score=0.95,
                        reasoning="Foreign key constraint implies exact match relationship",
                        validation_status="VALID",
                        llm_generated=False,
                        created_at=datetime.utcnow(),
                        metadata={'relationship_type': 'FOREIGN_KEY'}
                    ))

            # Pattern 2: Cross-schema UID/ID references
            elif rel.get('relationship_type') == 'CROSS_SCHEMA_REFERENCE':
                column_name = properties.get('column_name')

                if column_name and self._is_uid_pattern(column_name):
                    # Try to infer the target column
                    target_column = self._infer_matching_column(
                        source_table, column_name, target_table, schemas_info.get(target_schema)
                    )

                    if target_column:
                        rules.append(ReconciliationRule(
                            rule_id=f"RULE_{generate_uid()}",
                            rule_name=f"UID_Match_{source_table}_{column_name}",
                            source_schema=source_schema,
                            source_table=source_table,
                            source_columns=[column_name],
                            target_schema=target_schema,
                            target_table=target_table,
                            target_columns=[target_column],
                            match_type=ReconciliationMatchType.EXACT,
                            transformation=None,
                            confidence_score=0.85,
                            reasoning=f"UID naming pattern suggests unique identifier match between {column_name} and {target_column}",
                            validation_status="LIKELY",
                            llm_generated=False,
                            created_at=datetime.utcnow(),
                            metadata={'relationship_type': 'CROSS_SCHEMA_REFERENCE', 'inferred': True}
                        ))

            # Pattern 2b: REFERENCES and LLM-inferred relationships (SEMANTIC_REFERENCE, INFERRED)
            elif rel.get('relationship_type') in ['REFERENCES', 'SEMANTIC_REFERENCE', 'INFERRED']:
                # Try to get column info from multiple sources
                # Priority: 1. Direct fields, 2. Properties, 3. Infer
                column_name = rel.get('source_column') or properties.get('column_name') or properties.get('source_column')
                target_column = rel.get('target_column') or properties.get('target_column')

                # Check if this is an LLM-inferred relationship
                is_llm_inferred = properties.get('llm_inferred', False)
                llm_confidence = properties.get('llm_confidence', 0.75)
                llm_reasoning = properties.get('llm_reasoning', '')

                if column_name:
                    # If target_column not provided, try to infer it
                    if not target_column:
                        # For single schema, get the schema object
                        schema_obj = schemas_info.get(schema_names[0]) if len(schema_names) == 1 else schemas_info.get(target_schema)
                        target_column = self._infer_matching_column(
                            source_table, column_name, target_table, schema_obj
                        )

                    if target_column:
                        # Determine match type based on relationship type
                        if rel.get('relationship_type') == 'SEMANTIC_REFERENCE':
                            match_type = ReconciliationMatchType.SEMANTIC
                        else:
                            match_type = ReconciliationMatchType.EXACT

                        rules.append(ReconciliationRule(
                            rule_id=f"RULE_{generate_uid()}",
                            rule_name=f"{rel.get('relationship_type')}_{source_table}_{target_table}",
                            source_schema=source_schema,
                            source_table=source_table,
                            source_columns=[column_name],
                            target_schema=target_schema,
                            target_table=target_table,
                            target_columns=[target_column],
                            match_type=match_type,
                            transformation=None,
                            confidence_score=llm_confidence if is_llm_inferred else 0.80,
                            reasoning=llm_reasoning if llm_reasoning else f"Relationship inferred from column {column_name}",
                            validation_status="LIKELY" if is_llm_inferred else "VALID",
                            llm_generated=is_llm_inferred,
                            created_at=datetime.utcnow(),
                            metadata={
                                'relationship_type': rel.get('relationship_type'),
                                'llm_inferred': is_llm_inferred,
                                'data_type_match': properties.get('data_type_match', '')
                            }
                        ))

        # Pattern 3: Look for matching column names across schemas
        if len(schema_names) >= 2:
            name_based_rules = self._generate_name_matching_rules(schemas_info, schema_names)
            rules.extend(name_based_rules)

        logger.debug(f"Generated {len(rules)} pattern-based rules")
        return rules

    def _generate_name_matching_rules(
        self,
        schemas_info: Dict[str, DatabaseSchema],
        schema_names: List[str]
    ) -> List[ReconciliationRule]:
        """Generate rules based on matching column names across schemas."""
        rules = []

        # Compare schemas pairwise
        for i, schema1_name in enumerate(schema_names):
            for schema2_name in schema_names[i+1:]:
                schema1 = schemas_info.get(schema1_name)
                schema2 = schemas_info.get(schema2_name)

                if not schema1 or not schema2:
                    continue

                # Extract database names from connection URLs
                db1_name = self._extract_database_name(schema1.database)
                db2_name = self._extract_database_name(schema2.database)

                # Use database names if available, otherwise fall back to schema names
                source_schema = db1_name if db1_name else schema1_name
                target_schema = db2_name if db2_name else schema2_name

                # Compare all table pairs
                for table1_name, table1 in schema1.tables.items():
                    for table2_name, table2 in schema2.tables.items():
                        # Look for matching UID/ID columns
                        for col1 in table1.columns:
                            if not self._is_uid_pattern(col1.name):
                                continue

                            for col2 in table2.columns:
                                if not self._is_uid_pattern(col2.name):
                                    continue

                                # Check if column names suggest a match
                                if self._columns_likely_match(col1.name, col2.name):
                                    rules.append(ReconciliationRule(
                                        rule_id=f"RULE_{generate_uid()}",
                                        rule_name=f"Name_Match_{table1_name}_{col1.name}",
                                        source_schema=source_schema,
                                        source_table=table1_name,
                                        source_columns=[col1.name],
                                        target_schema=target_schema,
                                        target_table=table2_name,
                                        target_columns=[col2.name],
                                        match_type=ReconciliationMatchType.EXACT,
                                        transformation=None,
                                        confidence_score=0.75,
                                        reasoning=f"Column name similarity suggests matching: {col1.name} ≈ {col2.name}",
                                        validation_status="LIKELY",
                                        llm_generated=False,
                                        created_at=datetime.utcnow(),
                                        metadata={'match_method': 'name_similarity'}
                                    ))

        return rules

    def _generate_llm_rules(
        self,
        relationships: List[Dict[str, Any]],
        schemas_info: Dict[str, DatabaseSchema],
        field_preferences: Optional[List[Dict[str, Any]]] = None
    ) -> List[ReconciliationRule]:
        """Generate semantic rules using LLM analysis."""
        try:
            from kg_builder.services.multi_schema_llm_service import get_multi_schema_llm_service

            llm_service = get_multi_schema_llm_service()

            if not llm_service.is_enabled():
                logger.info("LLM service not enabled, skipping LLM rule generation")
                return []

            # Prepare schemas info for LLM
            schemas_dict = SchemaParser._prepare_schemas_info(schemas_info)

            # Generate rules using LLM
            llm_rules_dict = llm_service.generate_reconciliation_rules(
                relationships, schemas_dict, field_preferences=field_preferences
            )

            # Convert to ReconciliationRule objects and validate
            rules = []
            for rule_dict in llm_rules_dict:
                try:
                    # Validate that columns exist in schemas before creating rule
                    if not self._validate_rule_columns(rule_dict, schemas_info):
                        logger.warning(
                            f"Skipping invalid LLM rule '{rule_dict.get('rule_name')}': "
                            f"columns {rule_dict.get('source_columns')} or {rule_dict.get('target_columns')} "
                            f"do not exist in schemas"
                        )
                        continue

                    rule = ReconciliationRule(
                        rule_id=f"RULE_{generate_uid()}",
                        rule_name=rule_dict.get('rule_name', f"LLM_Rule_{generate_uid()}"),
                        source_schema=rule_dict.get('source_schema', ''),
                        source_table=rule_dict.get('source_table', ''),
                        source_columns=rule_dict.get('source_columns', []),
                        target_schema=rule_dict.get('target_schema', ''),
                        target_table=rule_dict.get('target_table', ''),
                        target_columns=rule_dict.get('target_columns', []),
                        match_type=ReconciliationMatchType(rule_dict.get('match_type', 'semantic')),
                        transformation=rule_dict.get('transformation'),
                        filter_conditions=rule_dict.get('filter_conditions'),  # ✅ Add filter conditions
                        confidence_score=rule_dict.get('confidence', 0.7),
                        reasoning=rule_dict.get('reasoning', 'LLM-inferred relationship'),
                        validation_status=rule_dict.get('validation_status', 'UNCERTAIN'),
                        llm_generated=True,
                        created_at=datetime.utcnow(),
                        metadata={'example_match': rule_dict.get('example_match', '')}
                    )
                    rules.append(rule)
                except Exception as e:
                    logger.error(f"Error creating rule from LLM response: {e}")
                    continue

            # If no LLM rules were produced and this is a single-schema scenario,
            # fall back to generating simple rules from user-provided field hints.
            if len(rules) == 0 and len(schemas_info) == 1 and field_preferences:
                try:
                    schema_name, schema_obj = next(iter(schemas_info.items()))
                    # Build quick lookup maps
                    table_columns_map = {
                        t_name: {col.name.lower(): col.name for col in t_schema.columns}
                        for t_name, t_schema in schema_obj.tables.items()
                    }

                    fallback_count = 0
                    for pref in field_preferences:
                        # Support both dict and Pydantic model objects
                        src_table = pref.get('table_name') if isinstance(pref, dict) else getattr(pref, 'table_name', None)
                        hints = pref.get('field_hints', {}) if isinstance(pref, dict) else getattr(pref, 'field_hints', {})
                        if not src_table or not hints:
                            continue

                        src_cols_lower = set(table_columns_map.get(src_table, {}).keys())
                        for src_col, tgt_col in hints.items():
                            src_col_l = str(src_col).lower()
                            tgt_col_l = str(tgt_col).lower()

                            # Ensure source column exists in the source table
                            if src_col_l not in src_cols_lower:
                                continue

                            # Search for target column in other tables within the same schema
                            for tgt_table, cols_map in table_columns_map.items():
                                if tgt_table == src_table:
                                    continue
                                if tgt_col_l in cols_map:
                                    # Use original-cased column names
                                    resolved_src_col = table_columns_map[src_table][src_col_l]
                                    resolved_tgt_col = cols_map[tgt_col_l]

                                    rules.append(ReconciliationRule(
                                        rule_id=f"RULE_{generate_uid()}",
                                        rule_name=f"Hint_Match_{src_table}_{resolved_src_col}_to_{tgt_table}_{resolved_tgt_col}",
                                        source_schema=schema_name,
                                        source_table=src_table,
                                        source_columns=[resolved_src_col],
                                        target_schema=schema_name,
                                        target_table=tgt_table,
                                        target_columns=[resolved_tgt_col],
                                        match_type=ReconciliationMatchType.EXACT,
                                        transformation=None,
                                        confidence_score=0.8,
                                        reasoning="Derived from user-provided field_hints within single schema",
                                        validation_status="LIKELY",
                                        llm_generated=False,
                                        created_at=datetime.utcnow(),
                                        metadata={"source": "fallback_field_hints"}
                                    ))
                                    fallback_count += 1
                    if fallback_count > 0:
                        logger.info(f"LLM produced no rules; generated {fallback_count} fallback rule(s) from field_hints for single schema '{schema_name}'")
                except Exception as e:
                    logger.error(f"Error generating fallback rules from field_hints: {e}")

            logger.debug(f"Generated {len(rules)} LLM-based rules (including any single-schema fallback)")
            return rules

        except Exception as e:
            logger.error(f"Error in LLM rule generation: {e}")
            return []

    def _validate_rule_columns(
        self,
        rule_dict: Dict[str, Any],
        schemas_info: Dict[str, DatabaseSchema]
    ) -> bool:
        """
        Validate that all columns referenced in a rule actually exist in the schemas.

        Args:
            rule_dict: Rule dictionary from LLM
            schemas_info: Schema information

        Returns:
            True if all columns exist, False otherwise
        """
        try:
            source_schema_name = rule_dict.get('source_schema', '')
            source_table_name = rule_dict.get('source_table', '')
            source_columns = rule_dict.get('source_columns', [])
            target_schema_name = rule_dict.get('target_schema', '')
            target_table_name = rule_dict.get('target_table', '')
            target_columns = rule_dict.get('target_columns', [])

            # Find matching schema (handle both schema name and database name)
            source_schema = None
            for schema_name, schema in schemas_info.items():
                db_name = self._extract_database_name(schema.database)
                if schema_name == source_schema_name or db_name == source_schema_name:
                    source_schema = schema
                    break

            target_schema = None
            for schema_name, schema in schemas_info.items():
                db_name = self._extract_database_name(schema.database)
                if schema_name == target_schema_name or db_name == target_schema_name:
                    target_schema = schema
                    break

            if not source_schema or not target_schema:
                logger.debug(f"Schema not found: source={source_schema_name}, target={target_schema_name}")
                return False

            # Validate source columns exist
            source_table = source_schema.tables.get(source_table_name)
            if not source_table:
                logger.debug(f"Source table '{source_table_name}' not found in schema '{source_schema_name}'")
                return False

            source_column_names = [col.name.lower() for col in source_table.columns]
            for col in source_columns:
                if col.lower() not in source_column_names:
                    logger.debug(
                        f"Source column '{col}' not found in table '{source_table_name}'. "
                        f"Available columns: {source_column_names}"
                    )
                    return False

            # Validate target columns exist
            target_table = target_schema.tables.get(target_table_name)
            if not target_table:
                logger.debug(f"Target table '{target_table_name}' not found in schema '{target_schema_name}'")
                return False

            target_column_names = [col.name.lower() for col in target_table.columns]
            for col in target_columns:
                if col.lower() not in target_column_names:
                    logger.debug(
                        f"Target column '{col}' not found in table '{target_table_name}'. "
                        f"Available columns: {target_column_names}"
                    )
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating rule columns: {e}")
            return False

    def _is_uid_pattern(self, column_name: str) -> bool:
        """Check if column follows UID/ID naming pattern."""
        if not column_name:
            return False
        col_lower = column_name.lower()
        uid_patterns = ['_uid', '_id', '_code', '_key', '_ref']
        return any(pattern in col_lower for pattern in uid_patterns) or col_lower in ['id', 'uid', 'code']

    def _columns_likely_match(self, col1: str, col2: str) -> bool:
        """Determine if two column names likely represent the same data."""
        col1_lower = col1.lower()
        col2_lower = col2.lower()

        # Exact match
        if col1_lower == col2_lower:
            return True

        # Remove common suffixes and compare
        suffixes = ['_uid', '_id', '_code', '_key', '_ref']
        col1_base = col1_lower
        col2_base = col2_lower

        for suffix in suffixes:
            col1_base = col1_base.replace(suffix, '')
            col2_base = col2_base.replace(suffix, '')

        # Check if base names are similar
        if col1_base == col2_base and col1_base:
            return True

        # Check if one contains the other
        if col1_base in col2_base or col2_base in col1_base:
            if len(col1_base) > 3 and len(col2_base) > 3:  # Avoid short matches
                return True

        return False

    def _infer_matching_column(
        self,
        source_table: str,
        source_column: str,
        target_table: str,
        target_schema: Optional[DatabaseSchema]
    ) -> Optional[str]:
        """Infer the matching column in the target table."""
        if not target_schema:
            return None

        # Find the target table
        target_table_obj = None
        for table_name, table in target_schema.tables.items():
            if table_name.lower() == target_table.lower():
                target_table_obj = table
                break

        if not target_table_obj:
            return None

        # Look for columns with similar names
        for column in target_table_obj.columns:
            if self._columns_likely_match(source_column, column.name):
                return column.name

        # Look for primary key columns if source column looks like an ID
        if self._is_uid_pattern(source_column):
            if target_table_obj.primary_keys:
                return target_table_obj.primary_keys[0]

        return None

    def _deduplicate_rules(self, rules: List[ReconciliationRule]) -> List[ReconciliationRule]:
        """Remove duplicate rules, keeping the highest confidence version."""
        unique_rules = {}

        for rule in rules:
            # Create a key based on source/target tables and columns
            key = (
                rule.source_schema, rule.source_table, tuple(sorted(rule.source_columns)),
                rule.target_schema, rule.target_table, tuple(sorted(rule.target_columns))
            )

            # Keep the rule with higher confidence
            if key not in unique_rules or rule.confidence_score > unique_rules[key].confidence_score:
                unique_rules[key] = rule

        return list(unique_rules.values())


# Singleton instance
_reconciliation_service: Optional[ReconciliationRuleGenerator] = None


def get_reconciliation_service() -> ReconciliationRuleGenerator:
    """Get or create the singleton reconciliation service instance."""
    global _reconciliation_service
    if _reconciliation_service is None:
        _reconciliation_service = ReconciliationRuleGenerator()
    return _reconciliation_service
