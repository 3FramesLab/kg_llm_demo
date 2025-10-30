"""
Graphiti backend service for temporal knowledge graph operations.
"""
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from kg_builder.models import KnowledgeGraph, GraphNode, GraphRelationship
from kg_builder.config import GRAPHITI_STORAGE_PATH

logger = logging.getLogger(__name__)

try:
    from graphiti_core import Graphiti
    GRAPHITI_AVAILABLE = True
except ImportError:
    GRAPHITI_AVAILABLE = False
    logger.warning("Graphiti not installed. Install with: pip install graphiti-core")


class GraphitiBackend:
    """Graphiti backend for temporal knowledge graph storage and querying."""
    
    def __init__(self):
        """Initialize Graphiti backend."""
        self.available = GRAPHITI_AVAILABLE
        self.graphs = {}
        self.storage_path = GRAPHITI_STORAGE_PATH
        self.storage_path.mkdir(exist_ok=True)
        
        if self.available:
            logger.info("Graphiti backend initialized")
        else:
            logger.warning("Graphiti not available - using file-based storage fallback")
    
    def is_available(self) -> bool:
        """Check if Graphiti is available."""
        return self.available
    
    def create_graph(self, kg: KnowledgeGraph) -> bool:
        """Create a knowledge graph in Graphiti."""
        try:
            if self.available:
                # Use Graphiti if available
                graphiti = Graphiti()
                
                # Add nodes
                for node in kg.nodes:
                    graphiti.add_node(
                        node_id=node.id,
                        node_type=node.label,
                        properties=node.properties,
                        timestamp=kg.created_at
                    )
                
                # Add relationships
                for rel in kg.relationships:
                    graphiti.add_edge(
                        source_id=rel.source_id,
                        target_id=rel.target_id,
                        edge_type=rel.relationship_type,
                        properties=rel.properties,
                        timestamp=kg.created_at
                    )
                
                self.graphs[kg.name] = graphiti
                logger.info(f"Created graph '{kg.name}' in Graphiti")
            else:
                # Fallback: Store as JSON files
                self._store_graph_locally(kg)
            
            return True
        
        except Exception as e:
            logger.error(f"Error creating graph in Graphiti: {e}")
            # Fallback to local storage
            try:
                self._store_graph_locally(kg)
                return True
            except Exception as e2:
                logger.error(f"Fallback storage also failed: {e2}")
                return False
    
    def _store_graph_locally(self, kg: KnowledgeGraph) -> None:
        """Store graph as JSON files (fallback)."""
        graph_dir = self.storage_path / kg.name
        graph_dir.mkdir(exist_ok=True)
        
        # Store nodes
        nodes_data = [
            {
                "id": node.id,
                "label": node.label,
                "properties": node.properties,
                "source_table": node.source_table,
                "source_column": node.source_column,
            }
            for node in kg.nodes
        ]
        
        with open(graph_dir / "nodes.json", "w") as f:
            json.dump(nodes_data, f, indent=2, default=str)
        
        # Store relationships
        rels_data = [
            {
                "source_id": rel.source_id,
                "target_id": rel.target_id,
                "relationship_type": rel.relationship_type,
                "properties": rel.properties,
                "source_column": rel.source_column,
                "target_column": rel.target_column,
            }
            for rel in kg.relationships
        ]
        
        with open(graph_dir / "relationships.json", "w") as f:
            json.dump(rels_data, f, indent=2, default=str)
        
        # Store metadata (including field_preferences and table_aliases)
        metadata = {
            "name": kg.name,
            "schema_file": kg.schema_file,
            "created_at": kg.created_at.isoformat(),
            "nodes_count": len(kg.nodes),
            "relationships_count": len(kg.relationships),
            "table_aliases": kg.table_aliases,  # ✅ Include LLM-learned table aliases
            **kg.metadata  # ✅ Include KG metadata (field_preferences, etc.)
        }

        logger.info(f"💾 Storing metadata for KG '{kg.name}':")
        logger.info(f"   - table_aliases from kg: {kg.table_aliases}")
        logger.info(f"   - kg.metadata: {kg.metadata}")
        logger.info(f"   - Final metadata to store: {metadata}")

        with open(graph_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2, default=str)

        logger.info(f"✅ Stored graph '{kg.name}' locally at {graph_dir}")
    
    def query(self, kg_name: str, query_str: str) -> List[Dict[str, Any]]:
        """Execute a query on a graph."""
        try:
            if self.available and kg_name in self.graphs:
                graphiti = self.graphs[kg_name]
                # Graphiti query execution
                results = graphiti.query(query_str)
                return results if isinstance(results, list) else [results]
            else:
                # Fallback: Query local storage
                return self._query_local(kg_name, query_str)
        
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []
    
    def _query_local(self, kg_name: str, query_str: str) -> List[Dict[str, Any]]:
        """Query local storage (fallback)."""
        graph_dir = self.storage_path / kg_name
        
        if not graph_dir.exists():
            logger.warning(f"Graph '{kg_name}' not found locally")
            return []
        
        try:
            # Load nodes and relationships
            with open(graph_dir / "nodes.json", "r") as f:
                nodes = json.load(f)
            
            with open(graph_dir / "relationships.json", "r") as f:
                relationships = json.load(f)
            
            # Simple pattern matching for queries
            results = []
            
            if "nodes" in query_str.lower():
                results = nodes
            elif "relationships" in query_str.lower() or "edges" in query_str.lower():
                results = relationships
            elif "match" in query_str.lower():
                # Simple pattern matching
                results = self._pattern_match(nodes, relationships, query_str)
            
            return results
        
        except Exception as e:
            logger.error(f"Local query failed: {e}")
            return []
    
    def _pattern_match(self, nodes: List[Dict], rels: List[Dict], pattern: str) -> List[Dict]:
        """Simple pattern matching for queries."""
        results = []
        
        # Extract entity ID from pattern if present
        if "id:" in pattern.lower():
            entity_id = pattern.split("id:")[-1].strip().strip("'\"")
            results = [n for n in nodes if n["id"] == entity_id]
        
        return results
    
    def get_entities(self, kg_name: str) -> List[Dict[str, Any]]:
        """Get all entities from a graph."""
        graph_dir = self.storage_path / kg_name
        
        if graph_dir.exists():
            try:
                with open(graph_dir / "nodes.json", "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading entities: {e}")
        
        return []
    
    def get_relationships(self, kg_name: str) -> List[Dict[str, Any]]:
        """Get all relationships from a graph."""
        graph_dir = self.storage_path / kg_name
        
        if graph_dir.exists():
            try:
                with open(graph_dir / "relationships.json", "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading relationships: {e}")
        
        return []
    
    def list_graphs(self) -> List[dict]:
        """List all graphs with their metadata, sorted by created_at (latest first)."""
        try:
            graphs = []
            for d in self.storage_path.iterdir():
                if d.is_dir():
                    metadata_file = d / "metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                                # Add backends information
                                metadata['backends'] = ['graphiti']
                                graphs.append(metadata)
                        except Exception as e:
                            logger.warning(f"Could not read metadata for {d.name}: {e}")
                            # Fallback: add basic info
                            graphs.append({
                                'name': d.name,
                                'backends': ['graphiti'],
                                'created_at': None
                            })
                    else:
                        # No metadata file, add basic info
                        graphs.append({
                            'name': d.name,
                            'backends': ['graphiti'],
                            'created_at': None
                        })

            # Sort by created_at timestamp (latest first)
            # Handle None values by putting them at the end
            def sort_key(graph):
                created_at = graph.get('created_at')
                if created_at is None:
                    return datetime.min  # Put None values at the end
                try:
                    # Parse ISO format timestamp
                    return datetime.fromisoformat(created_at)
                except (ValueError, TypeError):
                    return datetime.min  # Put invalid timestamps at the end

            graphs.sort(key=sort_key, reverse=True)
            return graphs
        except Exception as e:
            logger.error(f"Error listing graphs: {e}")
            return []

    def get_kg_metadata(self, kg_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific knowledge graph."""
        try:
            graph_dir = self.storage_path / kg_name
            metadata_file = graph_dir / "metadata.json"

            logger.info(f"📖 Reading metadata for KG '{kg_name}' from {metadata_file}")

            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                logger.info(f"✅ Loaded metadata for KG '{kg_name}':")
                logger.info(f"   - table_aliases: {metadata.get('table_aliases', {})}")
                logger.info(f"   - Full metadata keys: {list(metadata.keys())}")
                return metadata
            else:
                logger.warning(f"❌ No metadata file found for KG '{kg_name}' at {metadata_file}")
                return None
        except Exception as e:
            logger.error(f"❌ Error retrieving metadata for KG '{kg_name}': {e}")
            return None
    
    def delete_graph(self, kg_name: str) -> bool:
        """Delete a graph."""
        try:
            graph_dir = self.storage_path / kg_name
            if graph_dir.exists():
                import shutil
                shutil.rmtree(graph_dir)
                if kg_name in self.graphs:
                    del self.graphs[kg_name]
                logger.info(f"Deleted graph '{kg_name}'")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting graph: {e}")
            return False


# Global instance
_graphiti_instance: Optional[GraphitiBackend] = None


def get_graphiti_backend() -> GraphitiBackend:
    """Get or create Graphiti backend instance."""
    global _graphiti_instance
    if _graphiti_instance is None:
        _graphiti_instance = GraphitiBackend()
    return _graphiti_instance

