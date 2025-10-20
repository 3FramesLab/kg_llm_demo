"""
Service for parsing JSON schema files and extracting entities and relationships.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from kg_builder.models import (
    DatabaseSchema, TableSchema, ColumnSchema, 
    GraphNode, GraphRelationship, KnowledgeGraph
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
        """Extract entities (nodes) from schema."""
        nodes = []
        
        for table_name, table in schema.tables.items():
            # Create node for the table itself
            table_node = GraphNode(
                id=f"table_{table_name}",
                label=table_name,
                properties={
                    "type": "Table",
                    "column_count": len(table.columns),
                    "primary_keys": table.primary_keys,
                },
                source_table=table_name
            )
            nodes.append(table_node)
            
            # Create nodes for important columns (UIDs, IDs, foreign keys)
            for column in table.columns:
                if SchemaParser._is_important_column(column):
                    col_node = GraphNode(
                        id=f"column_{table_name}_{column.name}",
                        label=f"{table_name}.{column.name}",
                        properties={
                            "type": "Column",
                            "column_type": column.type,
                            "nullable": column.nullable,
                            "primary_key": column.primary_key,
                        },
                        source_table=table_name,
                        source_column=column.name
                    )
                    nodes.append(col_node)
        
        return nodes
    
    @staticmethod
    def extract_relationships(schema: DatabaseSchema, nodes: List[GraphNode]) -> List[GraphRelationship]:
        """Extract relationships from schema."""
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
            
            # Column belongs to table relationships
            for column in table.columns:
                if SchemaParser._is_important_column(column):
                    source_id = f"column_{table_name}_{column.name}"
                    target_id = f"table_{table_name}"
                    rel = GraphRelationship(
                        source_id=source_id,
                        target_id=target_id,
                        relationship_type="BELONGS_TO",
                        properties={"column_name": column.name},
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
        schema: DatabaseSchema
    ) -> KnowledgeGraph:
        """Build a complete knowledge graph from schema."""
        nodes = SchemaParser.extract_entities(schema)
        relationships = SchemaParser.extract_relationships(schema, nodes)
        
        kg = KnowledgeGraph(
            name=kg_name,
            nodes=nodes,
            relationships=relationships,
            schema_file=schema_name
        )
        
        logger.info(f"Built KG '{kg_name}' with {len(nodes)} nodes and {len(relationships)} relationships")
        return kg

