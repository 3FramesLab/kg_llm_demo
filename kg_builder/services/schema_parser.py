"""
Service for parsing JSON schema files and extracting entities and relationships.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from kg_builder.models import (
    DatabaseSchema, TableSchema, ColumnSchema,
    GraphNode, GraphRelationship, KnowledgeGraph,
    RelationshipDefinition
)
from kg_builder.config import SCHEMAS_DIR
from datetime import datetime

logger = logging.getLogger(__name__)


class SchemaParser:
    """Parses JSON schema files and extracts graph structures."""
    
    @staticmethod
    def load_schema(schema_name: str) -> DatabaseSchema:
        """Load a schema from JSON file."""
        schema_path = SCHEMAS_DIR / f"{schema_name}.json"
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        try:
            with open(schema_path, 'r') as f:
                data = json.load(f)
            
            # Parse tables
            tables = {}
            for table_name, table_data in data.get("tables", {}).items():
                columns = [
                    ColumnSchema(**col) for col in table_data.get("columns", [])
                ]
                tables[table_name] = TableSchema(
                    table_name=table_data.get("table_name", table_name),
                    columns=columns,
                    primary_keys=table_data.get("primary_keys", []),
                    foreign_keys=table_data.get("foreign_keys", []),
                    indexes=table_data.get("indexes", [])
                )
            
            return DatabaseSchema(
                database=data.get("database", ""),
                tables=tables,
                total_tables=data.get("total_tables", len(tables)),
                metadata=data.get("metadata", {})
            )
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schema file: {e}")
            raise ValueError(f"Invalid JSON schema: {e}")
        except Exception as e:
            logger.error(f"Error loading schema: {e}")
            raise
    
    @staticmethod
    def extract_entities(schema: DatabaseSchema) -> List[GraphNode]:
        """Extract entities (nodes) from schema - only tables, not columns."""
        nodes = []

        for table_name, table in schema.tables.items():
            # Create node for the table itself with all column metadata
            columns_metadata = [
                {
                    "name": col.name,
                    "type": col.type,
                    "nullable": col.nullable,
                    "primary_key": col.primary_key
                }
                for col in table.columns
            ]

            table_node = GraphNode(
                id=f"table_{table_name}",
                label=table_name,
                properties={
                    "type": "Table",
                    "column_count": len(table.columns),
                    "primary_keys": table.primary_keys,
                    "foreign_keys": [fk for fk in table.foreign_keys],  # Store foreign key info
                    "columns": columns_metadata,  # Store all column info as table properties
                },
                source_table=table_name
            )
            nodes.append(table_node)

        return nodes
    
    @staticmethod
    def extract_relationships(schema: DatabaseSchema, nodes: List[GraphNode]) -> List[GraphRelationship]:
        """Extract relationships from schema - only table-to-table relationships."""
        relationships = []

        for table_name, table in schema.tables.items():
            # Relationships from foreign keys
            for fk in table.foreign_keys:
                source_id = f"table_{table_name}"
                target_table = fk.get("referred_table", fk.get("target_table"))
                if target_table:
                    target_id = f"table_{target_table}"
                    rel = GraphRelationship(
                        source_id=source_id,
                        target_id=target_id,
                        relationship_type="FOREIGN_KEY",
                        properties={
                            "source_columns": fk.get("columns", []),
                            "target_columns": fk.get("referred_columns", []),
                        },
                        source_column=fk.get("columns", [None])[0]
                    )
                    relationships.append(rel)

            # Relationships from UID/ID columns (inferred)
            for column in table.columns:
                if SchemaParser._is_reference_column(column):
                    # Try to infer target table from column name
                    target_table = SchemaParser._infer_target_table(column.name, schema)
                    if target_table and target_table != table_name:
                        source_id = f"table_{table_name}"
                        target_id = f"table_{target_table}"
                        rel = GraphRelationship(
                            source_id=source_id,
                            target_id=target_id,
                            relationship_type="REFERENCES",
                            properties={
                                "inferred": True,
                                "column_name": column.name,
                            },
                            source_column=column.name
                        )
                        relationships.append(rel)

        return relationships
    
    @staticmethod
    def _is_important_column(column: ColumnSchema) -> bool:
        """Check if a column is important enough to create a node."""
        important_keywords = ["uid", "id", "code", "key", "ref"]
        col_name_lower = column.name.lower()
        return any(keyword in col_name_lower for keyword in important_keywords)
    
    @staticmethod
    def _is_reference_column(column: ColumnSchema) -> bool:
        """Check if a column appears to be a reference to another table."""
        reference_keywords = ["uid", "_id", "_ref", "_code"]
        col_name_lower = column.name.lower()
        return any(keyword in col_name_lower for keyword in reference_keywords)
    
    @staticmethod
    def _infer_target_table(column_name: str, schema: DatabaseSchema) -> Optional[str]:
        """Infer target table from column name."""
        col_lower = column_name.lower()
        
        # Remove common suffixes
        for suffix in ["_uid", "_id", "_ref", "_code"]:
            if col_lower.endswith(suffix):
                potential_table = col_lower[:-len(suffix)]
                # Check if table exists
                for table_name in schema.tables.keys():
                    if table_name.lower() == potential_table or potential_table in table_name.lower():
                        return table_name
        
        return None
    
    @staticmethod
    def build_knowledge_graph(
        schema_name: str,
        kg_name: str,
        schema: DatabaseSchema,
        use_llm: bool = False,
        field_preferences: Optional[List[Any]] = None
    ) -> KnowledgeGraph:
        """Build a complete knowledge graph from schema.

        Args:
            schema_name: Name of the schema
            kg_name: Name for the knowledge graph
            schema: Parsed database schema
            use_llm: Whether to use LLM for relationship enhancement
            field_preferences: User-specific field hints to guide LLM

        Returns:
            Knowledge graph with entities and relationships
        """
        nodes = SchemaParser.extract_entities(schema)
        relationships = SchemaParser.extract_relationships(schema, nodes)

        # Enhance relationships with LLM if enabled
        if use_llm:
            # Prepare schema in dict format for LLM enhancement
            schemas_dict = {schema_name: schema}
            relationships = SchemaParser._enhance_relationships_with_llm(
                relationships, schemas_dict, field_preferences=field_preferences
            )

        # Store field_preferences in metadata for later use
        metadata = {}
        if field_preferences:
            metadata['field_preferences'] = field_preferences

        kg = KnowledgeGraph(
            name=kg_name,
            nodes=nodes,
            relationships=relationships,
            schema_file=schema_name,
            metadata=metadata
        )

        logger.info(f"Built KG '{kg_name}' with {len(nodes)} nodes and {len(relationships)} relationships")
        return kg

    @staticmethod
    def build_merged_knowledge_graph(
        schema_names: List[str],
        kg_name: str,
        use_llm: bool = True,
        field_preferences: Optional[List[Any]] = None
    ) -> KnowledgeGraph:
        """Build a unified knowledge graph from multiple schemas with cross-schema relationships.

        Args:
            schema_names: List of schema names to merge
            kg_name: Name for the generated KG
            use_llm: Whether to use LLM for relationship enhancement
            field_preferences: User-specific field hints to guide LLM

        Returns:
            Unified knowledge graph with cross-schema relationships
        """
        all_nodes = []
        all_relationships = []
        all_schemas = {}

        # Load all schemas
        for schema_name in schema_names:
            try:
                schema = SchemaParser.load_schema(schema_name)
                all_schemas[schema_name] = schema
                logger.info(f"Loaded schema: {schema_name}")
            except FileNotFoundError as e:
                logger.error(f"Failed to load schema {schema_name}: {e}")
                raise

        # Extract entities and relationships from each schema
        for schema_name, schema in all_schemas.items():
            nodes = SchemaParser.extract_entities(schema)
            relationships = SchemaParser.extract_relationships(schema, nodes)

            all_nodes.extend(nodes)
            all_relationships.extend(relationships)

        # Detect and create cross-schema relationships
        cross_schema_rels = SchemaParser._detect_cross_schema_relationships(
            all_schemas, all_nodes
        )
        all_relationships.extend(cross_schema_rels)

        # Enhance relationships with LLM if enabled
        if use_llm:
            all_relationships = SchemaParser._enhance_relationships_with_llm(
                all_relationships, all_schemas, field_preferences=field_preferences
            )

        # Store field_preferences in metadata for later use
        metadata = {}
        if field_preferences:
            metadata['field_preferences'] = field_preferences

        kg = KnowledgeGraph(
            name=kg_name,
            nodes=all_nodes,
            relationships=all_relationships,
            schema_file=",".join(schema_names),
            metadata=metadata
        )

        logger.info(
            f"Built merged KG '{kg_name}' from {len(schema_names)} schemas "
            f"with {len(all_nodes)} nodes and {len(all_relationships)} relationships"
        )
        return kg

    @staticmethod
    def _detect_cross_schema_relationships(
        schemas: Dict[str, DatabaseSchema],
        nodes: List[GraphNode]
    ) -> List[GraphRelationship]:
        """Detect relationships between tables across different schemas."""
        cross_schema_rels = []

        # Create a mapping of table names to schema names
        table_to_schema = {}
        for schema_name, schema in schemas.items():
            for table_name in schema.tables.keys():
                table_to_schema[table_name] = schema_name

        # Check for common naming patterns that indicate relationships
        for schema_name, schema in schemas.items():
            for table_name, table in schema.tables.items():
                for column in table.columns:
                    # Look for foreign key patterns
                    if SchemaParser._is_reference_column(column):
                        # Try to find matching table in other schemas
                        for other_schema_name, other_schema in schemas.items():
                            if other_schema_name == schema_name:
                                continue

                            # Try to infer target table
                            target_table = SchemaParser._infer_target_table_across_schemas(
                                column.name, other_schema
                            )

                            if target_table:
                                source_id = f"table_{table_name}"
                                target_id = f"table_{target_table}"

                                # Avoid duplicate relationships
                                rel_exists = any(
                                    r.source_id == source_id and r.target_id == target_id
                                    for r in cross_schema_rels
                                )

                                if not rel_exists:
                                    rel = GraphRelationship(
                                        source_id=source_id,
                                        target_id=target_id,
                                        relationship_type="CROSS_SCHEMA_REFERENCE",
                                        properties={
                                            "source_schema": schema_name,
                                            "target_schema": other_schema_name,
                                            "column_name": column.name,
                                            "inferred": True,
                                        },
                                        source_column=column.name
                                    )
                                    cross_schema_rels.append(rel)
                                    logger.debug(
                                        f"Detected cross-schema relationship: "
                                        f"{schema_name}.{table_name} -> {other_schema_name}.{target_table}"
                                    )

        return cross_schema_rels

    @staticmethod
    def _infer_target_table_across_schemas(
        column_name: str,
        schema: DatabaseSchema
    ) -> Optional[str]:
        """Infer target table from column name within a specific schema."""
        col_lower = column_name.lower()

        # Remove common suffixes
        for suffix in ["_uid", "_id", "_ref", "_code"]:
            if col_lower.endswith(suffix):
                potential_table = col_lower[:-len(suffix)]
                # Check if table exists in this schema
                for table_name in schema.tables.keys():
                    if table_name.lower() == potential_table or potential_table in table_name.lower():
                        return table_name

        return None

    @staticmethod
    def _enhance_relationships_with_llm(
        relationships: List[GraphRelationship],
        schemas: Dict[str, DatabaseSchema],
        field_preferences: Optional[List[Any]] = None
    ) -> List[GraphRelationship]:
        """Enhance relationships with LLM analysis (inference, descriptions, confidence scoring).

        Args:
            relationships: List of relationships to enhance
            schemas: Dictionary of schemas
            field_preferences: User-specific field hints to guide LLM

        Returns:
            Enhanced relationships with LLM analysis
        """
        try:
            from kg_builder.services.multi_schema_llm_service import get_multi_schema_llm_service

            llm_service = get_multi_schema_llm_service()

            if not llm_service.is_enabled():
                logger.info("LLM service not enabled, skipping relationship enhancement")
                return relationships

            # Prepare schemas info for LLM
            schemas_info = SchemaParser._prepare_schemas_info(schemas)

            # Convert relationships to dict format for LLM
            rels_dict = [
                {
                    "source_table": rel.source_id.replace("table_", ""),
                    "target_table": rel.target_id.replace("table_", ""),
                    "relationship_type": rel.relationship_type,
                    "properties": rel.properties
                }
                for rel in relationships
            ]

            logger.info("Starting LLM relationship enhancement...")

            # Step 1: Infer additional relationships
            logger.info("Step 1: Inferring additional relationships...")
            inferred_rels = llm_service.infer_relationships(schemas_info, rels_dict, field_preferences=field_preferences)

            # Step 2: Enhance descriptions
            logger.info("Step 2: Enhancing relationship descriptions...")
            enhanced_rels = llm_service.enhance_relationships(inferred_rels, schemas_info)

            # Step 3: Score relationships
            logger.info("Step 3: Scoring relationships with confidence...")
            scored_rels = llm_service.score_relationships(enhanced_rels, schemas_info)

            # Convert back to GraphRelationship objects with LLM metadata
            enhanced_relationships = []

            # Add original relationships with LLM enhancements
            for rel in relationships:
                source_table = rel.source_id.replace("table_", "")
                target_table = rel.target_id.replace("table_", "")

                # Find matching scored relationship
                scored = next(
                    (r for r in scored_rels
                     if r.get('source_table') == source_table and r.get('target_table') == target_table),
                    None
                )

                # Find matching enhanced relationship
                enhanced = next(
                    (r for r in enhanced_rels
                     if r.get('source_table') == source_table and r.get('target_table') == target_table),
                    None
                )

                # Update relationship properties with LLM data
                updated_props = rel.properties.copy() if rel.properties else {}

                # Get source and target columns from scored data if not present in original relationship
                source_col = rel.source_column
                target_col = rel.target_column

                if scored:
                    updated_props['llm_confidence'] = scored.get('confidence', 0.0)
                    updated_props['llm_reasoning'] = scored.get('reasoning', '')
                    updated_props['llm_validation_status'] = scored.get('validation_status', '')
                    updated_props['llm_risk_factors'] = scored.get('risk_factors', [])
                    updated_props['llm_recommendation'] = scored.get('recommendation', '')
                    # Use column info from scored relationship if not already set
                    if not source_col and scored.get('source_column'):
                        source_col = scored.get('source_column')
                    if not target_col and scored.get('target_column'):
                        target_col = scored.get('target_column')

                if enhanced:
                    updated_props['llm_description'] = enhanced.get('description', '')

                # Create updated relationship
                updated_rel = GraphRelationship(
                    source_id=rel.source_id,
                    target_id=rel.target_id,
                    relationship_type=rel.relationship_type,
                    properties=updated_props,
                    source_column=source_col,
                    target_column=target_col
                )
                enhanced_relationships.append(updated_rel)

            # Add inferred relationships
            for inferred in inferred_rels:
                if inferred.get('inferred_by_llm'):
                    source_id = f"table_{inferred.get('source_table')}"
                    target_id = f"table_{inferred.get('target_table')}"

                    inferred_rel = GraphRelationship(
                        source_id=source_id,
                        target_id=target_id,
                        relationship_type=inferred.get('relationship_type', 'INFERRED'),
                        properties={
                            'llm_inferred': True,
                            'llm_confidence': inferred.get('confidence', 0.0),
                            'llm_reasoning': inferred.get('reasoning', ''),
                            'llm_description': f"Inferred: {inferred.get('reasoning', '')}",
                            'data_type_match': inferred.get('data_type_match')
                        },
                        source_column=inferred.get('source_column'),
                        target_column=inferred.get('target_column')
                    )
                    enhanced_relationships.append(inferred_rel)

            logger.info(
                f"LLM enhancement complete: {len(enhanced_relationships)} relationships "
                f"({len(enhanced_relationships) - len(relationships)} inferred)"
            )

            return enhanced_relationships

        except Exception as e:
            logger.error(f"Error in LLM relationship enhancement: {e}")
            return relationships

    @staticmethod
    def _prepare_schemas_info(schemas: Dict[str, DatabaseSchema]) -> Dict[str, Any]:
        """Prepare schema information for LLM analysis."""
        schemas_info = {}

        for schema_name, schema in schemas.items():
            tables_info = {}

            for table_name, table in schema.tables.items():
                columns_info = [
                    {
                        "name": col.name,
                        "type": col.type,
                        "nullable": col.nullable,
                        "primary_key": col.primary_key
                    }
                    for col in table.columns
                ]

                tables_info[table_name] = {
                    "columns": columns_info,
                    "primary_keys": table.primary_keys,
                    "foreign_keys": table.foreign_keys
                }

            schemas_info[schema_name] = {
                "tables": tables_info,
                "total_tables": len(schema.tables)
            }

        return schemas_info

    @staticmethod
    def add_nl_relationships_to_kg(
        kg: KnowledgeGraph,
        nl_relationships: List[RelationshipDefinition]
    ) -> KnowledgeGraph:
        """
        Add natural language-defined relationships to an existing knowledge graph.

        This method:
        1. Converts NL relationships to GraphRelationship objects
        2. Merges with existing relationships
        3. Handles duplicates
        4. Tracks relationship source

        Args:
            kg: Existing knowledge graph
            nl_relationships: List of NL-defined relationships

        Returns:
            Updated knowledge graph with NL relationships added
        """
        logger.info(f"Adding {len(nl_relationships)} NL relationships to KG '{kg.name}'")

        # Convert NL relationships to GraphRelationship objects
        new_relationships = []
        duplicates_found = 0

        for nl_rel in nl_relationships:
            # Skip if validation failed
            if nl_rel.validation_status != "VALID":
                logger.warning(f"Skipping invalid relationship: {nl_rel.source_table} -> {nl_rel.target_table}")
                continue

            # Create source and target IDs
            source_id = f"table_{nl_rel.source_table}"
            target_id = f"table_{nl_rel.target_table}"

            # Check if relationship already exists
            existing = any(
                r.source_id == source_id and
                r.target_id == target_id and
                r.relationship_type == nl_rel.relationship_type
                for r in kg.relationships
            )

            if existing:
                duplicates_found += 1
                logger.debug(f"Duplicate relationship found: {source_id} -> {target_id}")
                continue

            # Create GraphRelationship with NL metadata
            graph_rel = GraphRelationship(
                source_id=source_id,
                target_id=target_id,
                relationship_type=nl_rel.relationship_type,
                properties={
                    "source": "natural_language",
                    "confidence": nl_rel.confidence,
                    "reasoning": nl_rel.reasoning,
                    "cardinality": nl_rel.cardinality,
                    "input_format": nl_rel.input_format,
                    "nl_defined": True
                }
            )
            new_relationships.append(graph_rel)

        # Add new relationships to KG
        kg.relationships.extend(new_relationships)

        logger.info(
            f"Added {len(new_relationships)} NL relationships to KG '{kg.name}' "
            f"({duplicates_found} duplicates skipped)"
        )

        return kg

    @staticmethod
    def merge_relationships(
        kg: KnowledgeGraph,
        strategy: str = "union"
    ) -> KnowledgeGraph:
        """
        Merge and deduplicate relationships in a knowledge graph.

        Strategies:
        - "union": Keep all relationships (default)
        - "high_confidence": Keep only high-confidence relationships
        - "deduplicate": Remove exact duplicates

        Args:
            kg: Knowledge graph to process
            strategy: Merge strategy

        Returns:
            Knowledge graph with merged relationships
        """
        logger.info(f"Merging relationships in KG '{kg.name}' using strategy: {strategy}")

        if strategy == "deduplicate":
            # Remove exact duplicates
            seen = set()
            unique_rels = []

            for rel in kg.relationships:
                key = (rel.source_id, rel.target_id, rel.relationship_type)
                if key not in seen:
                    seen.add(key)
                    unique_rels.append(rel)

            kg.relationships = unique_rels
            logger.info(f"Deduplicated relationships: {len(kg.relationships)} unique relationships")

        elif strategy == "high_confidence":
            # Keep only high-confidence relationships
            high_conf_rels = []

            for rel in kg.relationships:
                confidence = rel.properties.get("confidence", 0.75)
                if confidence >= 0.7:
                    high_conf_rels.append(rel)

            kg.relationships = high_conf_rels
            logger.info(f"Filtered by confidence: {len(kg.relationships)} high-confidence relationships")

        # "union" strategy: keep all (no action needed)

        return kg

    @staticmethod
    def get_relationship_statistics(kg: KnowledgeGraph) -> Dict[str, Any]:
        """
        Get statistics about relationships in a knowledge graph.

        Args:
            kg: Knowledge graph to analyze

        Returns:
            Dictionary with relationship statistics
        """
        stats = {
            "total_relationships": len(kg.relationships),
            "by_type": {},
            "by_source": {},
            "nl_defined": 0,
            "auto_detected": 0,
            "average_confidence": 0.0,
            "high_confidence_count": 0
        }

        total_confidence = 0.0
        confidence_count = 0

        for rel in kg.relationships:
            # Count by type
            rel_type = rel.relationship_type
            stats["by_type"][rel_type] = stats["by_type"].get(rel_type, 0) + 1

            # Count by source
            source = rel.source_id
            stats["by_source"][source] = stats["by_source"].get(source, 0) + 1

            # Count NL vs auto-detected
            if rel.properties.get("nl_defined", False):
                stats["nl_defined"] += 1
            else:
                stats["auto_detected"] += 1

            # Track confidence
            confidence = rel.properties.get("confidence", 0.75)
            total_confidence += confidence
            confidence_count += 1

            if confidence >= 0.7:
                stats["high_confidence_count"] += 1

        # Calculate average confidence
        if confidence_count > 0:
            stats["average_confidence"] = total_confidence / confidence_count

        logger.info(f"KG '{kg.name}' statistics: {stats['total_relationships']} relationships, "
                   f"{stats['nl_defined']} NL-defined, {stats['auto_detected']} auto-detected")

        return stats

