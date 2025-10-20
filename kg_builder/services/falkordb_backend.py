"""
FalkorDB backend service for knowledge graph operations.
"""
import logging
import time
from typing import List, Dict, Any, Optional
from kg_builder.models import KnowledgeGraph, GraphNode, GraphRelationship
from kg_builder.config import FALKORDB_HOST, FALKORDB_PORT, FALKORDB_PASSWORD

logger = logging.getLogger(__name__)

try:
    from falkordb import FalkorDB
    FALKORDB_AVAILABLE = True
except ImportError:
    FALKORDB_AVAILABLE = False
    logger.warning("FalkorDB not installed. Install with: pip install falkordb")


class FalkorDBBackend:
    """FalkorDB backend for knowledge graph storage and querying."""
    
    def __init__(self):
        """Initialize FalkorDB connection."""
        self.available = FALKORDB_AVAILABLE
        self.client = None
        self.graphs = {}
        
        if self.available:
            try:
                self.client = FalkorDB(
                    host=FALKORDB_HOST,
                    port=FALKORDB_PORT,
                    password=FALKORDB_PASSWORD
                )
                logger.info(f"Connected to FalkorDB at {FALKORDB_HOST}:{FALKORDB_PORT}")
            except Exception as e:
                logger.error(f"Failed to connect to FalkorDB: {e}")
                self.available = False
    
    def is_connected(self) -> bool:
        """Check if FalkorDB is connected."""
        if not self.available or not self.client:
            return False
        
        try:
            # Try to ping the server
            self.client.list_graphs()
            return True
        except Exception as e:
            logger.error(f"FalkorDB connection check failed: {e}")
            return False
    
    def create_graph(self, kg: KnowledgeGraph) -> bool:
        """Create a knowledge graph in FalkorDB."""
        if not self.available or not self.client:
            logger.error("FalkorDB not available")
            return False
        
        try:
            # Get or create graph
            graph = self.client.select_graph(kg.name)
            
            # Add nodes
            for node in kg.nodes:
                self._add_node(graph, node)
            
            # Add relationships
            for rel in kg.relationships:
                self._add_relationship(graph, rel)
            
            self.graphs[kg.name] = graph
            logger.info(f"Created graph '{kg.name}' in FalkorDB")
            return True
        
        except Exception as e:
            logger.error(f"Error creating graph in FalkorDB: {e}")
            return False
    
    def _add_node(self, graph, node: GraphNode) -> None:
        """Add a node to the graph."""
        try:
            # Create Cypher query for node creation
            props_str = ", ".join([
                f"{k}: '{v}'" if isinstance(v, str) else f"{k}: {v}"
                for k, v in node.properties.items()
            ])
            
            if props_str:
                query = f"CREATE (n:{node.label} {{id: '{node.id}', {props_str}}})"
            else:
                query = f"CREATE (n:{node.label} {{id: '{node.id}'}})"
            
            graph.query(query)
        except Exception as e:
            logger.debug(f"Note: Node may already exist or query syntax issue: {e}")
    
    def _add_relationship(self, graph, rel: GraphRelationship) -> None:
        """Add a relationship to the graph."""
        try:
            # Create Cypher query for relationship
            props_str = ", ".join([
                f"{k}: '{v}'" if isinstance(v, str) else f"{k}: {v}"
                for k, v in rel.properties.items()
            ])
            
            if props_str:
                query = f"""
                MATCH (a {{id: '{rel.source_id}'}}), (b {{id: '{rel.target_id}'}})
                CREATE (a)-[r:{rel.relationship_type} {{{props_str}}}]->(b)
                """
            else:
                query = f"""
                MATCH (a {{id: '{rel.source_id}'}}), (b {{id: '{rel.target_id}'}})
                CREATE (a)-[r:{rel.relationship_type}]->(b)
                """
            
            graph.query(query)
        except Exception as e:
            logger.debug(f"Note: Relationship creation issue: {e}")
    
    def query(self, kg_name: str, query_str: str) -> List[Dict[str, Any]]:
        """Execute a Cypher query on a graph."""
        if not self.available or not self.client:
            logger.error("FalkorDB not available")
            return []
        
        try:
            if kg_name not in self.graphs:
                graph = self.client.select_graph(kg_name)
                self.graphs[kg_name] = graph
            else:
                graph = self.graphs[kg_name]
            
            result = graph.query(query_str)
            return self._format_results(result)
        
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []
    
    def get_entities(self, kg_name: str) -> List[Dict[str, Any]]:
        """Get all entities from a graph."""
        query = "MATCH (n) RETURN n.id as id, labels(n) as labels, properties(n) as properties"
        return self.query(kg_name, query)
    
    def get_relationships(self, kg_name: str) -> List[Dict[str, Any]]:
        """Get all relationships from a graph."""
        query = """
        MATCH (a)-[r]->(b) 
        RETURN a.id as source, type(r) as relationship_type, b.id as target, properties(r) as properties
        """
        return self.query(kg_name, query)
    
    def get_entity_relationships(self, kg_name: str, entity_id: str) -> List[Dict[str, Any]]:
        """Get relationships for a specific entity."""
        query = f"""
        MATCH (a {{id: '{entity_id}'}})-[r]->(b)
        RETURN a.id as source, type(r) as relationship_type, b.id as target, properties(r) as properties
        """
        return self.query(kg_name, query)
    
    def _format_results(self, result) -> List[Dict[str, Any]]:
        """Format query results."""
        try:
            results = []
            if hasattr(result, 'result_set'):
                for row in result.result_set:
                    results.append(dict(row))
            return results
        except Exception as e:
            logger.debug(f"Result formatting note: {e}")
            return []
    
    def delete_graph(self, kg_name: str) -> bool:
        """Delete a graph from FalkorDB."""
        if not self.available or not self.client:
            return False
        
        try:
            self.client.delete_graph(kg_name)
            if kg_name in self.graphs:
                del self.graphs[kg_name]
            logger.info(f"Deleted graph '{kg_name}' from FalkorDB")
            return True
        except Exception as e:
            logger.error(f"Error deleting graph: {e}")
            return False
    
    def list_graphs(self) -> List[str]:
        """List all graphs in FalkorDB."""
        if not self.available or not self.client:
            return []
        
        try:
            graphs = self.client.list_graphs()
            return [g for g in graphs]
        except Exception as e:
            logger.error(f"Error listing graphs: {e}")
            return []


# Global instance
_falkordb_instance: Optional[FalkorDBBackend] = None


def get_falkordb_backend() -> FalkorDBBackend:
    """Get or create FalkorDB backend instance."""
    global _falkordb_instance
    if _falkordb_instance is None:
        _falkordb_instance = FalkorDBBackend()
    return _falkordb_instance

