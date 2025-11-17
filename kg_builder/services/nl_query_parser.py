"""
Natural Language Query Parser

Parses NL definitions into executable query intents.
Uses Knowledge Graph to infer join columns.
"""

import json
import logging
import re
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any, Tuple

from kg_builder.models import KnowledgeGraph, AdditionalColumn, JoinPath
from kg_builder.services.nl_query_classifier import (
    NLQueryClassifier, DefinitionType, get_nl_query_classifier
)
from kg_builder.services.llm_service import get_llm_service
from kg_builder.services.table_name_mapper import get_table_name_mapper

logger = logging.getLogger(__name__)


class ColumnInclusionError(Exception):
    """Error during column inclusion processing."""
    pass


class JoinPathNotFoundError(ColumnInclusionError):
    """Error when no join path exists between tables."""
    pass


class ColumnNotFoundError(ColumnInclusionError):
    """Error when requested column doesn't exist in table."""
    pass


class TableNotFoundError(ColumnInclusionError):
    """Error when requested table doesn't exist."""
    pass


@dataclass
class QueryIntent:
    """Parsed intent from NL definition."""
    definition: str
    query_type: str  # DefinitionType.value
    source_table: Optional[str] = None
    target_table: Optional[str] = None
    operation: Optional[str] = None  # NOT_IN, IN, EQUALS, CONTAINS, AGGREGATE
    filters: List[Dict[str, Any]] = None
    join_columns: Optional[List[Tuple[str, str]]] = None  # [(source_col, target_col), ...]
    confidence: float = 0.75
    reasoning: str = ""
    additional_columns: List[AdditionalColumn] = None  # NEW: Columns from related tables

    def __post_init__(self):
        """Initialize default values."""
        if self.filters is None:
            self.filters = []
        if self.join_columns is None:
            self.join_columns = []
        if self.additional_columns is None:
            self.additional_columns = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        # Convert AdditionalColumn objects to dicts for serialization
        if self.additional_columns:
            data['additional_columns'] = [
                col.dict() if hasattr(col, 'dict') else asdict(col)
                for col in self.additional_columns
            ]
        return data


class NLQueryParser:
    """Parse NL definitions into executable query intents."""

    def __init__(self, kg: Optional[KnowledgeGraph] = None, schemas_info: Optional[Dict] = None, excluded_fields: Optional[List[str]] = None):
        """
        Initialize parser.

        Args:
            kg: Knowledge graph for join inference (SINGLE SOURCE OF TRUTH)
            schemas_info: Schema information (for table/column validation only)
            excluded_fields: DEPRECATED - exclusions should be applied during KG generation
        """
        self.kg = kg
        self.schemas_info = schemas_info or {}
        self.excluded_fields = set(excluded_fields) if excluded_fields else None  # Kept for backward compatibility
        self.classifier = get_nl_query_classifier()
        self.llm_service = get_llm_service()

        # Initialize table mapper with learned aliases from KG if available
        learned_aliases = kg.table_aliases if kg else {}
        self.table_mapper = get_table_name_mapper(schemas_info, learned_aliases)

    def parse(self, definition: str, use_llm: bool = True) -> QueryIntent:
        """
        Parse definition into query intent.

        Args:
            definition: Natural language definition
            use_llm: Whether to use LLM for parsing

        Returns:
            QueryIntent: Parsed query intent
        """
        import time
        parse_start_time = time.time()

        logger.info("="*120)
        logger.info(f"📝 NL QUERY PARSER: STARTING DEFINITION PARSING")
        logger.info(f"   Definition: '{definition}'")
        logger.info(f"   Use LLM: {use_llm}")
        logger.info(f"   LLM Service Enabled: {self.llm_service.is_enabled() if hasattr(self, 'llm_service') else 'Unknown'}")
        logger.info(f"   KG Available: {self.kg is not None}")
        if self.kg:
            logger.info(f"   KG Name: {self.kg.name}")
            logger.info(f"   KG Tables: {len(self.kg.nodes)} nodes")
        logger.info(f"   Schemas Available: {list(self.schemas_info.keys()) if self.schemas_info else 'None'}")
        logger.info("="*120)

        # STEP 1: Classify the definition
        logger.info(f"🔍 STEP 1: CLASSIFYING DEFINITION")
        classify_start = time.time()

        logger.info(f"   Classifier Type: {type(self.classifier).__name__}")
        logger.info(f"   Classifying definition...")

        def_type = self.classifier.classify(definition)
        operation = self.classifier.get_operation_type(definition)

        classify_time = (time.time() - classify_start) * 1000
        logger.info(f"✅ Definition classified in {classify_time:.2f}ms")
        logger.info(f"   Definition Type: {def_type}")
        logger.info(f"   Operation Type: {operation}")

        # STEP 2: Extract tables and details
        logger.info(f"🤖 STEP 2: EXTRACTING TABLES AND DETAILS")
        extract_start = time.time()

        if use_llm and self.llm_service.is_enabled():
            logger.info(f"   Using LLM-based parsing...")
            logger.info(f"   LLM Service: {type(self.llm_service).__name__}")
            intent = self._parse_with_llm(definition, def_type, operation)
            parsing_method = "LLM"
        else:
            logger.info(f"   Using rule-based parsing...")
            logger.info(f"   Reason: use_llm={use_llm}, llm_enabled={self.llm_service.is_enabled()}")
            intent = self._parse_rule_based(definition, def_type, operation)
            parsing_method = "Rule-based"

        extract_time = (time.time() - extract_start) * 1000
        logger.info(f"✅ Tables extracted in {extract_time:.2f}ms using {parsing_method}")
        logger.info(f"   Source Table: {intent.source_table}")
        logger.info(f"   Target Table: {intent.target_table}")
        logger.info(f"   Operation: {intent.operation}")
        logger.info(f"   Confidence: {intent.confidence}")
        logger.info(f"   Filters: {intent.filters}")

        # STEP 2.5: Resolve table names using mapper
        logger.info(f"🔄 STEP 2.5: RESOLVING TABLE NAMES")
        resolve_start = time.time()

        logger.info(f"   Table Mapper Type: {type(self.table_mapper).__name__}")
        logger.info(f"   Original Source: {intent.source_table}")
        logger.info(f"   Original Target: {intent.target_table}")

        intent = self._resolve_table_names(intent)

        resolve_time = (time.time() - resolve_start) * 1000
        logger.info(f"✅ Table names resolved in {resolve_time:.2f}ms")
        logger.info(f"   Resolved Source: {intent.source_table}")
        logger.info(f"   Resolved Target: {intent.target_table}")

        # STEP 3: Find join columns from Knowledge Graph
        logger.info(f"🔗 STEP 3: FINDING JOIN COLUMNS FROM KNOWLEDGE GRAPH")
        join_start = time.time()

        if intent.source_table and intent.target_table:
            logger.info(f"   Both source and target tables available")
            logger.info(f"   Current join columns: {intent.join_columns}")

            if not intent.join_columns or len(intent.join_columns) == 0:
                logger.info(f"   No join columns found, searching in KG...")
                join_cols = self._find_join_columns_from_kg(
                    intent.source_table,
                    intent.target_table
                )
                if join_cols:
                    intent.join_columns = join_cols
                    intent.confidence = min(0.95, intent.confidence + 0.1)
                    logger.info(f"✅ Successfully found join columns: {join_cols}")
                else:
                    error_msg = f"No valid KG relationships found for {intent.source_table} ←→ {intent.target_table}"
                    logger.error(f"❌ {error_msg}")

                    # For comparison queries, this is critical - FAIL immediately
                    if intent.query_type == "comparison_query":
                        detailed_error = (
                            f"Cannot execute comparison query: {error_msg}. "
                            f"All relationships may be marked as excluded (is_excluded: true). "
                            f"Please add non-excluded relationships to the KG between "
                            f"'{intent.source_table}' and '{intent.target_table}' with "
                            f"'source_column' and 'target_column' properties."
                        )
                        logger.error(f"CRITICAL: {detailed_error}")
                        raise ValueError(detailed_error)
                    else:
                        # For other query types, set very low confidence but continue
                        logger.warning(f"⚠️ Proceeding with very low confidence due to missing join columns")
                        intent.confidence = 0.1  # Very low confidence

        # Step 4: NEW - Extract and resolve additional columns from related tables
        if use_llm and self.llm_service.is_enabled() and intent.source_table:
            col_requests = self._extract_additional_columns(definition)
            if col_requests:
                valid_cols, errors = self._validate_and_resolve_columns(col_requests, intent.source_table)
                if errors:
                    logger.warning(f"Column validation errors: {errors}")
                if valid_cols:
                    intent.additional_columns = valid_cols
                    logger.info(f"✓ Resolved {len(intent.additional_columns)} additional columns")

        logger.info(f"Parsed intent: query_type={intent.query_type}, source={intent.source_table}, target={intent.target_table}, join_cols={intent.join_columns}, filters={intent.filters}, additional_cols={len(intent.additional_columns)}")
        return intent

    def _parse_with_llm(
        self,
        definition: str,
        def_type: DefinitionType,
        operation: Optional[str]
    ) -> QueryIntent:
        """Parse using LLM."""
        try:
            prompt = self._build_parsing_prompt(definition, def_type, operation)
            logger.debug(f"LLM Parsing Prompt:\n{prompt}")

            # Use the LLM service's helper method that handles parameter compatibility
            response = self.llm_service.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert data analyst. Parse natural language queries and extract structured information. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500
                # Note: temperature parameter removed - gpt-5 doesn't support temperature=0.3
                # Will use model's default temperature
            )

            result_text = response.choices[0].message.content
            logger.info(f"LLM Response:\n{result_text}")

            return self._parse_llm_response(result_text, def_type, operation)

        except Exception as e:
            logger.error(f"Error in LLM-based parsing: {e}")
            return self._parse_rule_based(definition, def_type, operation)

    def _parse_rule_based(
        self,
        definition: str,
        def_type: DefinitionType,
        operation: Optional[str]
    ) -> QueryIntent:
        """Parse using rule-based approach."""
        intent = QueryIntent(
            definition=definition,
            query_type=def_type.value,
            operation=operation or "IN"
        )

        # Common English words to exclude from table name extraction
        common_words = {
            "show", "me", "all", "the", "which", "are", "is", "a", "an",
            "and", "or", "not", "be", "have", "has", "do", "does", "did",
            "can", "could", "will", "would", "should", "may", "might",
            "active", "inactive", "status", "where", "that", "this", "these",
            "those", "from", "to", "for", "with", "by", "on", "at", "of",
            "find", "get", "list", "display", "retrieve", "fetch", "select",
            "give", "compare", "difference", "missing", "mismatch", "unmatched",
            "count", "sum", "average", "total", "group", "aggregate", "statistics",
            "in", "products", "product", "data", "records", "items", "entries"
        }

        # Extract table names from known tables in schemas
        potential_tables = []

        if self.schemas_info:
            # Collect all known table names from schemas
            known_tables = []
            for schema_name, schema in self.schemas_info.items():
                if hasattr(schema, 'tables'):
                    for table_name in schema.tables.keys():
                        known_tables.append(table_name)

            # Find which known tables appear in the definition
            definition_lower = definition.lower()
            for table_name in known_tables:
                if table_name.lower() in definition_lower:
                    potential_tables.append(table_name)
                    logger.info(f"Found table in definition: {table_name}")

        # Fallback: Look for capitalized words or quoted strings, but exclude common words
        if not potential_tables:
            words = definition.split()
            for w in words:
                cleaned = w.strip('",')
                if len(cleaned) > 0 and (cleaned[0].isupper() or w.startswith('"')):
                    # Exclude common English words
                    if cleaned.lower() not in common_words:
                        potential_tables.append(cleaned)
            logger.info(f"Fallback table extraction found: {potential_tables}")

        if len(potential_tables) >= 1:
            intent.source_table = potential_tables[0].lower()
            logger.info(f"Set source_table: {intent.source_table}")
        if len(potential_tables) >= 2:
            intent.target_table = potential_tables[1].lower()
            logger.info(f"Set target_table: {intent.target_table}")

        # Extract filters (simple pattern)
        # NOTE: Removed hardcoded "status" column assumption
        # The actual status/active column names vary by table (e.g., Active_Inactive, Status, etc.)
        # Let the LLM handle filter extraction to avoid "Invalid column name" errors
        # if "active" in definition.lower():
        #     intent.filters.append({"column": "status", "value": "active"})
        # if "inactive" in definition.lower():
        #     intent.filters.append({"column": "status", "value": "inactive"})

        # Reclassify if we have two tables and IN/NOT_IN operation
        if intent.source_table and intent.target_table and operation in ["IN", "NOT_IN"]:
            logger.info(f"Reclassifying as comparison_query: has 2 tables and operation={operation}")
            intent.query_type = "comparison_query"
            intent.confidence = 0.7
        else:
            intent.confidence = 0.6

        intent.reasoning = "Extracted using rule-based pattern matching"

        logger.info(f"Rule-based parsing result: query_type={intent.query_type}, source={intent.source_table}, target={intent.target_table}, operation={intent.operation}")

        return intent

    def _parse_llm_response(
        self,
        response_text: str,
        def_type: DefinitionType,
        operation: Optional[str]
    ) -> QueryIntent:
        """Parse LLM response."""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                logger.warning(f"No JSON found in LLM response. Response text: {response_text[:500]}")
                return QueryIntent(
                    definition="",
                    query_type=def_type.value,
                    operation=operation or "IN",
                    confidence=0.5
                )

            data = json.loads(json_match.group())

            filters = data.get("filters", [])
            intent = QueryIntent(
                definition=data.get("definition", ""),
                query_type=def_type.value,
                source_table=data.get("source_table", "").lower() if data.get("source_table") else None,
                target_table=data.get("target_table", "").lower() if data.get("target_table") else None,
                operation=operation or data.get("operation", "IN"),
                filters=filters,
                confidence=float(data.get("confidence", 0.75)),
                reasoning=data.get("reasoning", "LLM-inferred query intent")
            )

            # Log extracted filters
            if filters:
                logger.info(f"✓ Extracted filters from LLM: {filters}")
            else:
                logger.debug(f"No filters extracted from LLM response")

            return intent

        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return QueryIntent(
                definition="",
                query_type=def_type.value,
                operation=operation or "IN",
                confidence=0.5
            )

    def _resolve_table_names(self, intent: QueryIntent) -> QueryIntent:
        """
        Resolve business terms to actual table names with domain validation.

        Args:
            intent: Query intent with potentially unresolved table names

        Returns:
            Query intent with resolved table names
        """
        if intent.source_table:
            resolved = self.table_mapper.resolve_table_name(intent.source_table)
            if resolved and resolved != intent.source_table:
                logger.info(f"Resolved source table: '{intent.source_table}' → '{resolved}'")
                intent.source_table = resolved
                intent.confidence = min(0.95, intent.confidence + 0.05)

        if intent.target_table:
            resolved = self.table_mapper.resolve_table_name(intent.target_table)
            if resolved and resolved != intent.target_table:
                logger.info(f"Resolved target table: '{intent.target_table}' → '{resolved}'")
                intent.target_table = resolved
                intent.confidence = min(0.95, intent.confidence + 0.05)

        # Validate domain consistency between source and target tables
        if intent.source_table and intent.target_table:
            self._validate_table_domain_consistency(intent)

        # Apply table priority logic - ensure main tables are prioritized
        intent = self._apply_table_priority_logic(intent)

        return intent

    def _validate_table_domain_consistency(self, intent: QueryIntent):
        """
        Validate that source and target tables belong to compatible domains.

        Args:
            intent: Query intent with resolved table names
        """
        if not intent.source_table or not intent.target_table:
            return

        # Define domain patterns
        # Note: NBU = Network Business Unit, GPU = Graphics Processing Unit
        # These are compatible hardware business domains
        domain_patterns = {
            'HARDWARE_PRODUCTS': ['_NBU', '_nbu', '_GPU', '_gpu'],  # Hardware business units (compatible)
            'CPU': ['_CPU', '_cpu'],  # Central Processing Unit
            'BANKING': ['_BANK', '_bank', '_FINANCE', '_finance'],
            'GENERAL_HARDWARE': ['_HARDWARE', '_hardware', '_DEVICE', '_device']
        }

        # Get domains for both tables
        source_domain = None
        target_domain = None

        for domain, patterns in domain_patterns.items():
            if any(pattern in intent.source_table for pattern in patterns):
                source_domain = domain
            if any(pattern in intent.target_table for pattern in patterns):
                target_domain = domain

        # Check for domain conflicts
        if source_domain and target_domain and source_domain != target_domain:
            logger.error(f"❌ Domain mismatch detected!")
            logger.error(f"   Source table '{intent.source_table}' is {source_domain} domain")
            logger.error(f"   Target table '{intent.target_table}' is {target_domain} domain")
            logger.error(f"   These domains should not be joined together")

            # Significantly reduce confidence for domain mismatches
            intent.confidence = 0.1

            # Add warning to the intent
            if not hasattr(intent, 'warnings'):
                intent.warnings = []
            intent.warnings.append(
                f"Domain mismatch: {source_domain} table '{intent.source_table}' "
                f"should not be joined with {target_domain} table '{intent.target_table}'"
            )

    def _apply_table_priority_logic(self, intent: QueryIntent) -> QueryIntent:
        """
        Apply table priority logic to ensure proper main table selection.

        Args:
            intent: Query intent with resolved table names

        Returns:
            Query intent with corrected table priorities
        """
        # Define table priorities (higher = more preferred as main table)
        table_priorities = {
            'brz_lnd_IBP_Product_Master': 10,
            'brz_lnd_RBP_GPU': 9,
            'brz_lnd_OPS_EXCEL_GPU': 8,
            'brz_lnd_SKU_LIFNR_Excel': 7,
            'hana_material_master': 1  # Low priority - should be enrichment only
        }

        # If hana_material_master is the source table, try to swap with target
        if (intent.source_table == 'hana_material_master' and
            intent.target_table and
            table_priorities.get(intent.target_table, 0) > table_priorities.get(intent.source_table, 0)):

            logger.info(f"🔄 Swapping tables for better priority: {intent.source_table} ↔ {intent.target_table}")
            intent.source_table, intent.target_table = intent.target_table, intent.source_table

            # Also swap join columns if they exist
            if intent.join_columns:
                swapped_joins = [(target_col, source_col) for source_col, target_col in intent.join_columns]
                intent.join_columns = swapped_joins
                logger.info(f"🔄 Swapped join columns: {intent.join_columns}")

        return intent

    def _find_join_columns_from_kg(self, source: str, target: str) -> Optional[List[Tuple[str, str]]]:
        """
        Find join columns using KG relationships, strictly respecting is_excluded flags.

        Args:
            source: Source table name
            target: Target table name

        Returns:
            List of (source_col, target_col) tuples for valid (non-excluded) relationships
        """
        if not self.kg:
            logger.error("No KG available for join column inference")
            return None

        try:
            logger.info(f"🔍 Searching KG for valid join columns between '{source}' and '{target}'")
            logger.info(f"KG has {len(self.kg.relationships)} relationships")

            # Collect all relationships between tables, checking exclusion status
            valid_relationships = []
            excluded_relationships = []

            for rel in self.kg.relationships:
                source_id = rel.source_id.lower() if rel.source_id else ""
                target_id = rel.target_id.lower() if rel.target_id else ""

                # Check if relationship matches in forward or reverse direction
                is_forward = (source_id == source.lower() and target_id == target.lower())
                is_reverse = (source_id == target.lower() and target_id == source.lower())

                logger.debug(f"Checking relationship: {source_id} → {target_id}")
                logger.debug(f"  Looking for: {source.lower()} → {target.lower()}")
                logger.debug(f"  is_forward={is_forward}, is_reverse={is_reverse}")

                if is_forward or is_reverse:
                    logger.debug(f"Found matching relationship: {rel.source_id} → {rel.target_id} (type: {rel.relationship_type})")
                    logger.debug(f"Relationship properties: {rel.properties}")

                    # Extract column names from relationship
                    source_col = rel.source_column or (rel.properties.get("source_column") if rel.properties else None)
                    target_col = rel.target_column or (rel.properties.get("target_column") if rel.properties else None)
                    logger.debug(f"Resolved columns: source_col={source_col}, target_col={target_col}")

                    if source_col and target_col:
                        # Check if relationship is excluded
                        is_excluded = rel.properties.get('is_excluded', False) if rel.properties else False
                        priority = rel.properties.get('priority', 0) if rel.properties else 0

                        relationship_info = {
                            'relationship': rel,
                            'is_forward': is_forward,
                            'is_reverse': is_reverse,
                            'source_col': source_col,
                            'target_col': target_col,
                            'is_excluded': is_excluded,
                            'priority': priority
                        }

                        if is_excluded:
                            excluded_relationships.append(relationship_info)
                            logger.debug(f"⚠️ Skipping excluded relationship: {source_col} ←→ {target_col} (priority: {priority})")
                        else:
                            valid_relationships.append(relationship_info)
                            logger.debug(f"✅ Found valid relationship: {source_col} ←→ {target_col} (priority: {priority})")
                    else:
                        logger.warning(f"Relationship found but missing columns: source_column={source_col}, target_column={target_col}")

            # If no valid relationships found, provide detailed error
            if not valid_relationships:
                if excluded_relationships:
                    logger.error(f"❌ No valid join columns found for {source} ←→ {target}")
                    logger.error(f"   All {len(excluded_relationships)} relationships are marked as excluded:")
                    for rel_info in excluded_relationships:
                        logger.error(f"   - {rel_info['source_col']} ←→ {rel_info['target_col']} (priority: {rel_info['priority']}, excluded: true)")
                    logger.error(f"")
                    logger.error(f"   To fix this:")
                    logger.error(f"   1. Mark an existing relationship as non-excluded (is_excluded: false)")
                    logger.error(f"   2. Add a new non-excluded relationship to the KG")
                else:
                    logger.error(f"❌ No relationships found in KG between '{source}' and '{target}'")
                    logger.error(f"   To fix this: Add a relationship between these tables to the KG")

                return None

            # Select the best valid relationship (highest priority)
            best_relationship = max(valid_relationships, key=lambda r: r['priority'])

            # Return columns in correct order based on direction
            if best_relationship['is_reverse']:
                result = [(best_relationship['target_col'], best_relationship['source_col'])]
                logger.info(f"✅ Found join columns from KG (reversed): {best_relationship['target_col']} ←→ {best_relationship['source_col']}")
            else:
                result = [(best_relationship['source_col'], best_relationship['target_col'])]
                logger.info(f"✅ Found join columns from KG: {best_relationship['source_col']} ←→ {best_relationship['target_col']}")

            logger.info(f"   Priority: {best_relationship['priority']}, Excluded: {best_relationship['is_excluded']}")
            return result

        except Exception as e:
            logger.error(f"Error finding join columns from KG: {e}")
            return None

    def _infer_join_columns_from_schema(self, source: str, target: str) -> Optional[List[Tuple[str, str]]]:
        """
        Infer join columns by looking for matching column names in schemas.

        Args:
            source: Source table name
            target: Target table name

        Returns:
            List of (source_col, target_col) tuples
        """
        if not self.schemas_info:
            return None

        try:
            source_cols = []
            target_cols = []

            # Find columns in source and target tables
            for schema_name, schema in self.schemas_info.items():
                if hasattr(schema, 'tables') and schema.tables:
                    for table_name, table in schema.tables.items():
                        if table_name.lower() == source.lower():
                            source_cols = [col.name for col in table.columns] if hasattr(table, 'columns') else []
                        elif table_name.lower() == target.lower():
                            target_cols = [col.name for col in table.columns] if hasattr(table, 'columns') else []

            if not source_cols or not target_cols:
                logger.debug(f"Could not find columns for {source} or {target}")
                return None

            # Look for matching column names (case-insensitive)
            source_cols_lower = {col.lower(): col for col in source_cols}
            target_cols_lower = {col.lower(): col for col in target_cols}

            # Find exact matches
            matching_cols = []
            for src_col_lower, src_col in source_cols_lower.items():
                if src_col_lower in target_cols_lower:
                    tgt_col = target_cols_lower[src_col_lower]

                    # Filter out excluded fields
                    if self.excluded_fields:
                        from kg_builder.services.schema_parser import is_excluded_field
                        if is_excluded_field(src_col, self.excluded_fields) or is_excluded_field(tgt_col, self.excluded_fields):
                            logger.debug(f"⛔ Skipping matching column (excluded field): {src_col} ←→ {tgt_col}")
                            continue

                    matching_cols.append((src_col, tgt_col))

            if matching_cols:
                logger.info(f"Found {len(matching_cols)} matching column(s) after filtering")
                return matching_cols

            # Look for common ID patterns
            id_patterns = ['_id', '_uid', '_key', '_code', 'id', 'uid', 'code', 'key']
            for src_col_lower, src_col in source_cols_lower.items():
                if any(pattern in src_col_lower for pattern in id_patterns):
                    for tgt_col_lower, tgt_col in target_cols_lower.items():
                        if any(pattern in tgt_col_lower for pattern in id_patterns):
                            # Check if they share a base name
                            src_base = src_col_lower.replace('_id', '').replace('_uid', '').replace('_key', '').replace('_code', '')
                            tgt_base = tgt_col_lower.replace('_id', '').replace('_uid', '').replace('_key', '').replace('_code', '')
                            if src_base and tgt_base and (src_base == tgt_base or src_base in tgt_base or tgt_base in src_base):
                                # Filter out excluded fields
                                if self.excluded_fields:
                                    from kg_builder.services.schema_parser import is_excluded_field
                                    if is_excluded_field(src_col, self.excluded_fields) or is_excluded_field(tgt_col, self.excluded_fields):
                                        logger.debug(f"⛔ Skipping ID match (excluded field): {src_col} ←→ {tgt_col}")
                                        continue

                                logger.info(f"Found potential ID match: {src_col} ←→ {tgt_col}")
                                return [(src_col, tgt_col)]

            return None

        except Exception as e:
            logger.error(f"Error inferring join columns from schema: {e}")
            return None

    def _build_parsing_prompt(
        self,
        definition: str,
        def_type: DefinitionType,
        operation: Optional[str]
    ) -> str:
        """Build prompt for LLM parsing."""
        # Convert schemas_info to JSON-serializable format
        if self.schemas_info:
            schemas_dict = {}
            table_names_list = []
            for schema_name, schema in self.schemas_info.items():
                if hasattr(schema, 'tables'):
                    # Extract table names and columns
                    tables = {}
                    for table_name, table in schema.tables.items():
                        table_names_list.append(table_name)
                        if hasattr(table, 'columns'):
                            columns = [col.name for col in table.columns]
                            tables[table_name] = {"columns": columns}
                        else:
                            tables[table_name] = {"columns": []}
                    schemas_dict[schema_name] = {"tables": tables}
                else:
                    schemas_dict[schema_name] = {}
            schemas_str = json.dumps(schemas_dict, indent=2)
            table_names_str = ", ".join(table_names_list)
        else:
            schemas_str = "No schemas provided"
            table_names_str = "No tables available"

        # Build list of common English words to exclude
        common_words = [
            "show", "me", "all", "the", "which", "are", "in", "is", "a", "an",
            "and", "or", "not", "be", "have", "has", "do", "does", "did",
            "can", "could", "will", "would", "should", "may", "might",
            "active", "inactive", "status", "where", "that", "this", "these",
            "those", "from", "to", "for", "with", "by", "on", "at", "of",
            "find", "get", "list", "display", "retrieve", "fetch", "select",
            "give", "compare", "difference", "missing", "mismatch", "unmatched",
            "count", "sum", "average", "total", "group", "aggregate", "statistics"
        ]
        common_words_str = ", ".join(common_words)

        return f"""You are an expert data analyst. Parse this natural language query and extract table names and filters.

QUERY: "{definition}"

IMPORTANT RULES:
1. ONLY extract table names from this list: {table_names_str}
2. NEVER treat common English words as table names. Exclude: {common_words_str}
3. Look for business terms that might map to table names (e.g., "RBP" → "brz_lnd_RBP_GPU", "OPS Excel" → "brz_lnd_OPS_EXCEL_GPU")
4. EXTRACT FILTERS: Look for keywords like "active", "inactive", "status", and map them to actual column names in the target table
5. Identify the operation: NOT_IN (not in), IN (in), EQUALS (equals), CONTAINS (contains), AGGREGATE (count/sum/etc)

FILTER EXTRACTION GUIDE:
- "active" or "inactive" → Look for columns like: Active_Inactive, Status, State, Flag, etc.
- For target table in multi-table queries, check its columns for status-related fields
- Always include the correct column name from the schema, not generic names

EXAMPLES:
- Query: "Show me all products in RBP which are not in OPS Excel"
  → source_table: "brz_lnd_RBP_GPU", target_table: "brz_lnd_OPS_EXCEL_GPU", operation: "NOT_IN", filters: []

- Query: "Show me all active products in RBP GPU"
  → source_table: "brz_lnd_RBP_GPU", target_table: null, operation: "IN", filters: []

- Query: "Show me products in RBP which are in active OPS Excel"
  → source_table: "brz_lnd_RBP_GPU", target_table: "brz_lnd_OPS_EXCEL_GPU", operation: "IN", filters: [{{"column": "Active_Inactive", "value": "Active"}}]
  (Filter applies to target table brz_lnd_OPS_EXCEL_GPU which has Active_Inactive column)

Definition Type: {def_type.value}
Operation Type: {operation or "Unknown"}

Available schemas and tables:
{schemas_str}

Extract and return ONLY valid JSON with this structure (no other text):
{{
    "definition": "original definition",
    "source_table": "table_name from the list above",
    "target_table": "table_name from the list above or null",
    "operation": "NOT_IN|IN|EQUALS|CONTAINS|AGGREGATE",
    "filters": [
        {{"column": "column_name", "value": "value"}},
        ...
    ],
    "confidence": 0.85,
    "reasoning": "Why this parsing makes sense"
}}"""


    def _extract_additional_columns(self, definition: str) -> List[Dict[str, str]]:
        """
        Extract 'include column from table' clauses from definition using LLM.

        Supports patterns like:
        - "include X from Y"
        - "add X column from Y"
        - "also show X from Y"
        - "with X from Y"
        - "plus X from Y"
        """
        if not self.llm_service.is_enabled():
            return []

        try:
            prompt = self._build_additional_columns_prompt(definition)
            logger.debug(f"Additional Columns Extraction Prompt:\n{prompt}")

            response = self.llm_service.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert data analyst. Extract column inclusion requests from natural language queries. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300
            )

            result_text = response.choices[0].message.content
            logger.debug(f"Additional Columns LLM Response:\n{result_text}")

            # Parse JSON response
            json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
            if json_match:
                columns = json.loads(json_match.group())
                logger.info(f"✓ Extracted {len(columns)} additional column requests")
                return columns

            return []

        except Exception as e:
            logger.warning(f"Failed to extract additional columns: {e}")
            return []

    def _validate_and_resolve_columns(
        self,
        columns: List[Dict[str, str]],
        source_table: str
    ) -> Tuple[List[AdditionalColumn], List[str]]:
        """
        Validate and resolve all additional columns.

        Returns:
            Tuple of (valid_columns, error_messages)
        """
        valid_columns = []
        errors = []

        for col_req in columns:
            try:
                col_name = col_req.get("column_name", "").strip()
                table_name = col_req.get("source_table", "").strip()

                # Validation 1: Check column name
                if not col_name:
                    errors.append("❌ Column name is empty in request")
                    continue

                # Validation 2: Check table name
                if not table_name:
                    errors.append(f"❌ Table name is empty for column '{col_name}'")
                    continue

                # Validation 3: Resolve table name using mapper
                resolved_table = self.table_mapper.resolve_table_name(table_name)
                if not resolved_table:
                    available_tables = self._get_available_tables()
                    suggestions = self._find_similar_tables(table_name, available_tables)
                    suggestion_str = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
                    errors.append(
                        f"❌ Table '{table_name}' not found in schema.{suggestion_str}"
                    )
                    continue

                # Validation 4: Check if column exists in table
                matched_col_name = self._find_matching_column_name(resolved_table, col_name)
                if not matched_col_name:
                    available_cols = self._get_available_columns(resolved_table)
                    errors.append(
                        f"❌ Column '{col_name}' not found in table '{resolved_table}'. "
                        f"Available columns: {', '.join(available_cols[:5])}"
                        + (f" ... and {len(available_cols) - 5} more" if len(available_cols) > 5 else "")
                    )
                    continue

                # Validation 5: Find join path from source to target table
                path = self._find_join_path_to_table(source_table, resolved_table)
                if not path:
                    errors.append(
                        f"❌ No relationship path found between '{source_table}' "
                        f"and '{resolved_table}' for column '{col_name}'. "
                        f"Please ensure the Knowledge Graph has relationships between these tables."
                    )
                    continue

                # All validations passed - create AdditionalColumn object
                # Use the actual matched column name from the schema
                col = AdditionalColumn(
                    column_name=matched_col_name,
                    source_table=resolved_table,
                    confidence=path.confidence,
                    join_path=path.path
                )
                valid_columns.append(col)
                logger.info(f"✓ Validated column '{col_name}' -> '{matched_col_name}' from '{resolved_table}'")

            except Exception as e:
                errors.append(f"❌ Error processing column request {col_req}: {str(e)}")
                logger.exception(f"Exception during column validation: {e}")

        return valid_columns, errors

    def _column_exists_in_table(self, table_name: str, column_name: str) -> bool:
        """Check if column exists in table schema with fuzzy matching."""
        if not self.schemas_info:
            return True  # Can't validate without schemas_info

        for schema_name, schema in self.schemas_info.items():
            if hasattr(schema, 'tables'):
                for tbl_name, table in schema.tables.items():
                    if tbl_name.lower() == table_name.lower():
                        if hasattr(table, 'columns'):
                            col_names = [col.name for col in table.columns]
                            return self._fuzzy_match_column_name(column_name, col_names)

        return False

    def _fuzzy_match_column_name(self, requested_col: str, available_cols: List[str]) -> bool:
        """
        Fuzzy match column name against available columns.

        Handles common naming pattern differences:
        - Case insensitive matching
        - Space to underscore conversion
        - Underscore to space conversion
        - Removal of common prefixes/suffixes
        """
        requested_lower = requested_col.lower().strip()

        for available_col in available_cols:
            available_lower = available_col.lower().strip()

            # Exact match (case insensitive)
            if requested_lower == available_lower:
                return True

            # Space to underscore conversion
            if requested_lower.replace(' ', '_') == available_lower:
                return True

            # Underscore to space conversion
            if requested_lower.replace('_', ' ') == available_lower:
                return True

            # Both directions for robustness
            if requested_lower == available_lower.replace('_', ' '):
                return True

            if requested_lower == available_lower.replace(' ', '_'):
                return True

        return False

    def _find_matching_column_name(self, table_name: str, column_name: str) -> Optional[str]:
        """
        Find the actual column name that matches the requested column name.

        Returns the actual column name from the schema if found, None otherwise.
        """
        if not self.schemas_info:
            return column_name  # Can't validate without schemas_info, return as-is

        for schema_name, schema in self.schemas_info.items():
            if hasattr(schema, 'tables'):
                for tbl_name, table in schema.tables.items():
                    if tbl_name.lower() == table_name.lower():
                        if hasattr(table, 'columns'):
                            col_names = [col.name for col in table.columns]
                            return self._get_fuzzy_matched_column_name(column_name, col_names)

        return None

    def _get_fuzzy_matched_column_name(self, requested_col: str, available_cols: List[str]) -> Optional[str]:
        """
        Get the actual column name that fuzzy matches the requested column name.

        Returns the actual column name from the schema if found, None otherwise.
        """
        requested_lower = requested_col.lower().strip()

        for available_col in available_cols:
            available_lower = available_col.lower().strip()

            # Exact match (case insensitive)
            if requested_lower == available_lower:
                return available_col

            # Space to underscore conversion
            if requested_lower.replace(' ', '_') == available_lower:
                return available_col

            # Underscore to space conversion
            if requested_lower.replace('_', ' ') == available_lower:
                return available_col

            # Both directions for robustness
            if requested_lower == available_lower.replace('_', ' '):
                return available_col

            if requested_lower == available_lower.replace(' ', '_'):
                return available_col

        return None

    def _get_available_columns(self, table_name: str) -> List[str]:
        """Get list of available columns in a table."""
        if not self.schemas_info:
            return []

        for schema_name, schema in self.schemas_info.items():
            if hasattr(schema, 'tables'):
                for tbl_name, table in schema.tables.items():
                    if tbl_name.lower() == table_name.lower():
                        if hasattr(table, 'columns'):
                            return [col.name for col in table.columns]

        return []

    def _get_available_tables(self) -> List[str]:
        """Get list of all available tables in schemas."""
        tables = []
        if not self.schemas_info:
            return tables

        for schema_name, schema in self.schemas_info.items():
            if hasattr(schema, 'tables'):
                for tbl_name in schema.tables.keys():
                    tables.append(tbl_name)

        return tables

    def _find_similar_tables(self, table_name: str, available_tables: List[str], max_suggestions: int = 3) -> List[str]:
        """Find similar table names using simple string matching."""
        table_lower = table_name.lower()
        similar = []

        for tbl in available_tables:
            tbl_lower = tbl.lower()
            # Check if table name contains the search term or vice versa
            if table_lower in tbl_lower or tbl_lower in table_lower:
                similar.append(tbl)

        return similar[:max_suggestions]

    def _find_join_path_to_table(
        self,
        source: str,
        target: str
    ) -> Optional[JoinPath]:
        """
        Find optimal join path between source and target tables using BFS.

        Returns:
            JoinPath with highest composite score, or None if no path found
        """
        if not self.kg:
            logger.warning("No KG available for path finding")
            return None

        logger.debug(f"BFS: Starting path finding from {source} to {target}")
        logger.debug(f"BFS: KG has {len(self.kg.nodes)} nodes and {len(self.kg.relationships)} relationships")

        if source.lower() == target.lower():
            # Same table, no join needed
            return JoinPath(
                source_table=source,
                target_table=target,
                path=[source],
                confidence=1.0,
                length=0
            )

        from collections import deque

        # BFS to find all paths
        queue = deque([(source, [source], 1.0)])  # (current_table, path, confidence)
        all_paths = []
        visited_at_depth = {}

        while queue:
            current, path, conf = queue.popleft()
            logger.debug(f"BFS: Processing current={current}, path={path}")

            if current.lower() == target.lower():
                all_paths.append((path, conf))
                logger.debug(f"BFS: Found target! path={path}, conf={conf}")
                continue

            # Limit search depth to avoid infinite loops
            if len(path) > 5:
                logger.debug(f"BFS: Depth limit reached for path={path}")
                continue

            # Find relationships from current table, prioritizing non-excluded ones
            relationships_from_current = []

            for rel in self.kg.relationships:
                source_id = rel.source_id.lower() if rel.source_id else ""
                target_id = rel.target_id.lower() if rel.target_id else ""

                next_table = None
                rel_conf = rel.properties.get("confidence", 0.75) if rel.properties else 0.75
                is_excluded = rel.properties.get('is_excluded', False) if rel.properties else False
                priority = rel.properties.get('priority', 0) if rel.properties else 0

                # Handle both formats: "table_tablename" and "tablename"
                current_lower = current.lower()

                # Check if source matches current table (with or without "table_" prefix)
                if source_id == f"table_{current_lower}" or source_id == current_lower:
                    next_table = target_id.replace("table_", "")
                    logger.debug(f"BFS: Source match! {source_id} == {current_lower}, next_table={next_table}")
                    # Preserve original case from KG
                    for node in self.kg.nodes:
                        if node.id.lower() == f"table_{next_table.lower()}" or node.id.lower() == next_table.lower():
                            next_table = node.label
                            logger.debug(f"BFS: Found node label: {next_table}")
                            break
                # Check if target matches current table (with or without "table_" prefix)
                elif target_id == f"table_{current_lower}" or target_id == current_lower:
                    next_table = source_id.replace("table_", "")
                    logger.debug(f"BFS: Target match! {target_id} == {current_lower}, next_table={next_table}")
                    # Preserve original case from KG
                    for node in self.kg.nodes:
                        if node.id.lower() == f"table_{next_table.lower()}" or node.id.lower() == next_table.lower():
                            next_table = node.label
                            logger.debug(f"BFS: Found node label: {next_table}")
                            break

                if next_table and next_table.lower() not in [t.lower() for t in path]:
                    # Calculate effective priority (non-excluded gets bonus)
                    effective_priority = priority + (100 if not is_excluded else 0)

                    relationships_from_current.append({
                        'next_table': next_table,
                        'path': path + [next_table],
                        'confidence': conf * rel_conf,
                        'is_excluded': is_excluded,
                        'priority': priority,
                        'effective_priority': effective_priority,
                        'relationship': rel
                    })

            # Sort relationships by effective priority (non-excluded first, then by priority)
            relationships_from_current.sort(key=lambda x: (-x['effective_priority'], -x['confidence']))

            # Add relationships to queue, prioritizing non-excluded ones
            for rel_info in relationships_from_current:
                queue.append((rel_info['next_table'], rel_info['path'], rel_info['confidence']))

                if rel_info['is_excluded']:
                    logger.debug(f"BFS: Added {current} → {rel_info['next_table']} (conf={rel_info['confidence']:.2f}, EXCLUDED)")
                else:
                    logger.debug(f"BFS: Added {current} → {rel_info['next_table']} (conf={rel_info['confidence']:.2f}, non-excluded)")

        if not all_paths:
            logger.error(f"❌ No valid join path found in KG between {source} and {target}")
            logger.error(f"   This may be because:")
            logger.error(f"   1. No relationships exist between these tables in the KG")
            logger.error(f"   2. All relationships are marked as excluded (is_excluded: true)")
            logger.error(f"   3. Tables are not connected through valid intermediate tables")
            logger.error(f"")
            logger.error(f"   To fix this:")
            logger.error(f"   1. Add non-excluded relationships to the KG between '{source}' and '{target}'")
            logger.error(f"   2. Mark existing relationships as non-excluded (is_excluded: false)")
            logger.error(f"   3. Ensure table names in KG match exactly: '{source}', '{target}'")

            # DO NOT fall back to column name inference - strict KG adherence
            return None

        # Score and select best path
        best_path = max(
            all_paths,
            key=lambda p: (p[1] * 0.7) + ((1 / len(p[0])) * 0.3)
        )

        path_tables, confidence = best_path

        logger.info(f"✓ Found join path: {' → '.join(path_tables)}")
        logger.info(f"  Confidence: {confidence:.2f}, Length: {len(path_tables)-1}")

        return JoinPath(
            source_table=source,
            target_table=target,
            path=path_tables,
            confidence=confidence,
            length=len(path_tables) - 1
        )

    def _infer_join_from_column_names(
        self,
        source: str,
        target: str
    ) -> Optional[JoinPath]:
        """
        Infer direct join between tables based on common column names.

        When no explicit relationship exists in KG, try to find common columns
        that could be used for joining (e.g., "Material" column in both tables).

        Args:
            source: Source table name
            target: Target table name

        Returns:
            JoinPath with inferred connection, or None if no common columns found
        """
        if not self.schemas_info:
            logger.debug("No schemas_info available for column name matching")
            return None

        logger.info(f"🔍 Attempting to infer join between {source} and {target} from column names")

        # Get columns for both tables
        source_cols = []
        target_cols = []

        for schema_name, schema_data in self.schemas_info.items():
            columns_dict = schema_data.get("columns", {})

            # Find source table columns
            for table_name, cols in columns_dict.items():
                if table_name.lower() == source.lower():
                    source_cols = cols
                if table_name.lower() == target.lower():
                    target_cols = cols

        if not source_cols or not target_cols:
            logger.debug(f"Could not find columns for {source} or {target}")
            return None

        logger.debug(f"Source columns: {source_cols[:10]}...")
        logger.debug(f"Target columns: {target_cols[:10]}...")

        # Find common columns (case-insensitive) and categorize by exclusion status
        non_excluded_columns = []
        excluded_columns = []

        for s_col in source_cols:
            for t_col in target_cols:
                if s_col.lower() == t_col.lower():
                    # Check if either column is excluded
                    is_excluded = self._is_column_excluded(s_col) or self._is_column_excluded(t_col)

                    if is_excluded:
                        excluded_columns.append((s_col, t_col))
                        logger.debug(f"Found excluded common column: {s_col} ←→ {t_col}")
                    else:
                        non_excluded_columns.append((s_col, t_col))
                        logger.debug(f"Found non-excluded common column: {s_col} ←→ {t_col}")

        # Prioritize columns (prefer ID-like columns, avoid generic names)
        def column_priority(col_pair):
            col_name = col_pair[0].lower()

            # High priority: ID-like columns
            if any(keyword in col_name for keyword in ["material", "product", "sku", "item", "code"]):
                return 3
            if col_name.endswith("_id") or col_name.endswith("_uid"):
                return 2
            # Medium priority: business columns
            if any(keyword in col_name for keyword in ["number", "ref", "key"]):
                return 1
            # Low priority: generic columns
            return 0

        # Prefer non-excluded columns
        if non_excluded_columns:
            # Sort non-excluded columns by priority
            non_excluded_columns.sort(key=column_priority, reverse=True)
            best_match = non_excluded_columns[0]
            confidence = 0.65  # Standard confidence for non-excluded inferred joins
            logger.info(f"✅ Using non-excluded inferred join: {source}.{best_match[0]} ←→ {target}.{best_match[1]}")

        elif excluded_columns:
            # Fall back to excluded columns if no alternatives
            excluded_columns.sort(key=column_priority, reverse=True)
            best_match = excluded_columns[0]
            confidence = 0.35  # Lower confidence for excluded field joins
            logger.warning(f"⚠️ Using excluded field join (no alternatives): {source}.{best_match[0]} ←→ {target}.{best_match[1]}")

        else:
            logger.debug("No common columns found")
            return None

        source_col, target_col = best_match

        logger.info(f"  Confidence: {confidence:.2f} (inferred from column names)")

        # Create a synthetic join path
        return JoinPath(
            source_table=source,
            target_table=target,
            path=[source, target],  # Direct join
            confidence=confidence,
            length=1
        )

    def _is_column_excluded(self, column_name: str) -> bool:
        """Check if a column name is in the excluded fields list."""
        if not hasattr(self, 'excluded_fields') or not self.excluded_fields:
            # Fall back to default excluded fields
            from kg_builder.services.schema_parser import DEFAULT_EXCLUDED_FIELDS
            excluded_set = DEFAULT_EXCLUDED_FIELDS
        else:
            excluded_set = self.excluded_fields

        from kg_builder.services.schema_parser import is_excluded_field
        return is_excluded_field(column_name, excluded_set)

    def _build_additional_columns_prompt(self, definition: str) -> str:
        """Build LLM prompt to extract 'include' clauses."""
        return f"""Extract all "include column from table" clauses from this query definition.

QUERY: "{definition}"

INSTRUCTIONS:
1. Look for patterns like:
   - "include X from Y"
   - "add X column from Y"
   - "also show X from Y"
   - "with X from Y"
   - "plus X from Y"

2. For each match, extract:
   - column_name: The column being requested (e.g., "planner", "category", "ops planner")
   - source_table: The table it comes from (business term or actual name, e.g., "HANA Master", "Product Master")

3. IMPORTANT: Extract column names as they appear in natural language. The system will handle:
   - Case differences (e.g., "planner" vs "PLANNER")
   - Space/underscore differences (e.g., "ops planner" vs "OPS_PLANNER")
   - Common naming variations

4. Return JSON array:
[
  {{
    "column_name": "planner",
    "source_table": "HANA Master"
  }},
  {{
    "column_name": "ops planner",
    "source_table": "HANA Master"
  }}
]

5. If no "include" clauses found, return empty array: []

RESPONSE:
Return ONLY valid JSON, no other text."""


def get_nl_query_parser(
    kg: Optional[KnowledgeGraph] = None,
    schemas_info: Optional[Dict] = None,
    excluded_fields: Optional[List[str]] = None
) -> NLQueryParser:
    """Get or create NL query parser instance."""
    return NLQueryParser(kg, schemas_info, excluded_fields)

