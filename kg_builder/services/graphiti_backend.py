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

    def save_kg_metadata(self, kg_name: str, metadata: Dict[str, Any]) -> bool:
        """Save metadata for a specific knowledge graph."""
        try:
            graph_dir = self.storage_path / kg_name
            metadata_file = graph_dir / "metadata.json"

            logger.info(f"💾 Saving metadata for KG '{kg_name}' to {metadata_file}")

            # Ensure directory exists
            graph_dir.mkdir(parents=True, exist_ok=True)

            # Save metadata
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)

            logger.info(f"✅ Saved metadata for KG '{kg_name}'")
            logger.info(f"   - table_aliases: {metadata.get('table_aliases', {})}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving metadata for KG '{kg_name}': {e}")
            return False

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

    # CRUD operations for entities
    def create_entity(self, kg_name: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new entity in the knowledge graph.

        Args:
            kg_name: Name of the knowledge graph
            entity_data: Entity data including id, name, labels, properties

        Returns:
            Created entity data
        """
        try:
            graph_dir = self.storage_path / kg_name
            graph_dir.mkdir(parents=True, exist_ok=True)

            # Load existing entities
            entities = self.get_entities(kg_name)

            # Generate ID if not provided
            if not entity_data.get('id'):
                import uuid
                entity_data['id'] = f"entity_{uuid.uuid4().hex[:12]}"

            # Check for duplicate ID
            if any(e.get('id') == entity_data['id'] for e in entities):
                raise ValueError(f"Entity with ID '{entity_data['id']}' already exists")

            # Build entity object
            new_entity = {
                'id': entity_data['id'],
                'name': entity_data.get('name', entity_data['id']),
                'labels': entity_data.get('labels', []),
                'primaryLabel': entity_data.get('labels', ['Node'])[0],
                'type': entity_data.get('labels', ['Node'])[0],
                'properties': entity_data.get('properties', {}),
                'source_table': entity_data.get('source_table'),
                'source_column': entity_data.get('source_column'),
            }

            # Add metadata
            new_entity['properties']['created_at'] = datetime.utcnow().isoformat()
            new_entity['properties']['source'] = 'manual'

            # Add to entities list
            entities.append(new_entity)

            # Save back to file
            with open(graph_dir / "nodes.json", "w") as f:
                json.dump(entities, f, indent=2, default=str)

            logger.info(f"Created entity '{new_entity['id']}' in KG '{kg_name}'")
            return new_entity

        except Exception as e:
            logger.error(f"Error creating entity: {e}")
            raise

    def update_entity(self, kg_name: str, entity_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing entity in the knowledge graph.

        Args:
            kg_name: Name of the knowledge graph
            entity_id: ID of the entity to update
            update_data: Data to update (name, labels, properties, etc.)

        Returns:
            Updated entity data
        """
        try:
            graph_dir = self.storage_path / kg_name

            if not graph_dir.exists():
                raise ValueError(f"Knowledge graph '{kg_name}' not found")

            # Load existing entities
            entities = self.get_entities(kg_name)

            # Find entity to update
            entity_index = None
            for i, entity in enumerate(entities):
                if entity.get('id') == entity_id:
                    entity_index = i
                    break

            if entity_index is None:
                raise ValueError(f"Entity with ID '{entity_id}' not found")

            # Update entity fields
            entity = entities[entity_index]

            if 'name' in update_data and update_data['name']:
                entity['name'] = update_data['name']

            if 'labels' in update_data and update_data['labels']:
                entity['labels'] = update_data['labels']
                entity['primaryLabel'] = update_data['labels'][0]
                entity['type'] = update_data['labels'][0]

            if 'properties' in update_data and update_data['properties']:
                # Merge properties
                entity['properties'].update(update_data['properties'])

            if 'source_table' in update_data:
                entity['source_table'] = update_data['source_table']

            if 'source_column' in update_data:
                entity['source_column'] = update_data['source_column']

            # Add update metadata
            entity['properties']['updated_at'] = datetime.utcnow().isoformat()

            # Save back to file
            with open(graph_dir / "nodes.json", "w") as f:
                json.dump(entities, f, indent=2, default=str)

            logger.info(f"Updated entity '{entity_id}' in KG '{kg_name}'")
            return entity

        except Exception as e:
            logger.error(f"Error updating entity: {e}")
            raise

    def delete_entity(self, kg_name: str, entity_id: str) -> bool:
        """
        Delete an entity from the knowledge graph.
        Also deletes all relationships connected to this entity.

        Args:
            kg_name: Name of the knowledge graph
            entity_id: ID of the entity to delete

        Returns:
            True if successful
        """
        try:
            graph_dir = self.storage_path / kg_name

            if not graph_dir.exists():
                raise ValueError(f"Knowledge graph '{kg_name}' not found")

            # Load existing entities
            entities = self.get_entities(kg_name)

            # Find and remove entity
            entity_found = False
            entities = [e for e in entities if e.get('id') != entity_id or (entity_found := True, False)[1]]

            if not entity_found:
                raise ValueError(f"Entity with ID '{entity_id}' not found")

            # Save updated entities
            with open(graph_dir / "nodes.json", "w") as f:
                json.dump(entities, f, indent=2, default=str)

            # Also delete related relationships
            relationships = self.get_relationships(kg_name)
            relationships = [
                r for r in relationships
                if r.get('source_id') != entity_id and r.get('target_id') != entity_id
            ]

            with open(graph_dir / "relationships.json", "w") as f:
                json.dump(relationships, f, indent=2, default=str)

            logger.info(f"Deleted entity '{entity_id}' and its relationships from KG '{kg_name}'")
            return True

        except Exception as e:
            logger.error(f"Error deleting entity: {e}")
            raise

    # CRUD operations for relationships
    def create_relationship(self, kg_name: str, relationship_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new relationship in the knowledge graph.

        Args:
            kg_name: Name of the knowledge graph
            relationship_data: Relationship data including source_id, target_id, type, properties

        Returns:
            Created relationship data
        """
        try:
            graph_dir = self.storage_path / kg_name
            graph_dir.mkdir(parents=True, exist_ok=True)

            # Validate source and target entities exist
            entities = self.get_entities(kg_name)
            entity_ids = {e.get('id') for e in entities}

            source_id = relationship_data.get('source_id')
            target_id = relationship_data.get('target_id')

            if source_id not in entity_ids:
                raise ValueError(f"Source entity '{source_id}' not found")

            if target_id not in entity_ids:
                raise ValueError(f"Target entity '{target_id}' not found")

            # Load existing relationships
            relationships = self.get_relationships(kg_name)

            # Generate ID if not provided
            if not relationship_data.get('id'):
                import uuid
                relationship_data['id'] = f"rel_{uuid.uuid4().hex[:12]}"

            # Check for duplicate ID
            if any(r.get('id') == relationship_data['id'] for r in relationships):
                raise ValueError(f"Relationship with ID '{relationship_data['id']}' already exists")

            # Build relationship object
            new_relationship = {
                'id': relationship_data['id'],
                'source': source_id,
                'target': target_id,
                'source_id': source_id,
                'target_id': target_id,
                'type': relationship_data.get('relationship_type', 'RELATED_TO'),
                'relationship_type': relationship_data.get('relationship_type', 'RELATED_TO'),
                'properties': relationship_data.get('properties', {}),
                'source_column': relationship_data.get('source_column'),
                'target_column': relationship_data.get('target_column'),
            }

            # Add metadata
            new_relationship['properties']['created_at'] = datetime.utcnow().isoformat()
            new_relationship['properties']['source'] = 'manual'

            # Add to relationships list
            relationships.append(new_relationship)

            # Save back to file
            with open(graph_dir / "relationships.json", "w") as f:
                json.dump(relationships, f, indent=2, default=str)

            logger.info(f"Created relationship '{new_relationship['id']}' in KG '{kg_name}'")
            return new_relationship

        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            raise

    def update_relationship(self, kg_name: str, relationship_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing relationship in the knowledge graph.

        Args:
            kg_name: Name of the knowledge graph
            relationship_id: ID of the relationship to update
            update_data: Data to update (type, properties, etc.)

        Returns:
            Updated relationship data
        """
        try:
            graph_dir = self.storage_path / kg_name

            if not graph_dir.exists():
                raise ValueError(f"Knowledge graph '{kg_name}' not found")

            # Load existing relationships
            relationships = self.get_relationships(kg_name)

            # Find relationship to update
            relationship_index = None
            for i, rel in enumerate(relationships):
                if rel.get('id') == relationship_id:
                    relationship_index = i
                    break

            if relationship_index is None:
                raise ValueError(f"Relationship with ID '{relationship_id}' not found")

            # Update relationship fields
            relationship = relationships[relationship_index]

            if 'relationship_type' in update_data and update_data['relationship_type']:
                relationship['type'] = update_data['relationship_type']
                relationship['relationship_type'] = update_data['relationship_type']

            if 'properties' in update_data and update_data['properties']:
                # Merge properties
                relationship['properties'].update(update_data['properties'])

            if 'source_column' in update_data:
                relationship['source_column'] = update_data['source_column']

            if 'target_column' in update_data:
                relationship['target_column'] = update_data['target_column']

            # Add update metadata
            relationship['properties']['updated_at'] = datetime.utcnow().isoformat()

            # Save back to file
            with open(graph_dir / "relationships.json", "w") as f:
                json.dump(relationships, f, indent=2, default=str)

            logger.info(f"Updated relationship '{relationship_id}' in KG '{kg_name}'")
            return relationship

        except Exception as e:
            logger.error(f"Error updating relationship: {e}")
            raise

    def delete_relationship(self, kg_name: str, relationship_id: str) -> bool:
        """
        Delete a relationship from the knowledge graph.

        Args:
            kg_name: Name of the knowledge graph
            relationship_id: ID of the relationship to delete

        Returns:
            True if successful
        """
        try:
            graph_dir = self.storage_path / kg_name

            if not graph_dir.exists():
                raise ValueError(f"Knowledge graph '{kg_name}' not found")

            # Load existing relationships
            relationships = self.get_relationships(kg_name)

            # Find and remove relationship
            relationship_found = False
            relationships = [r for r in relationships if r.get('id') != relationship_id or (relationship_found := True, False)[1]]

            if not relationship_found:
                raise ValueError(f"Relationship with ID '{relationship_id}' not found")

            # Save updated relationships
            with open(graph_dir / "relationships.json", "w") as f:
                json.dump(relationships, f, indent=2, default=str)

            logger.info(f"Deleted relationship '{relationship_id}' from KG '{kg_name}'")
            return True

        except Exception as e:
            logger.error(f"Error deleting relationship: {e}")
            raise


# Global instance
_graphiti_instance: Optional[GraphitiBackend] = None


def get_graphiti_backend() -> GraphitiBackend:
    """Get or create Graphiti backend instance."""
    global _graphiti_instance
    if _graphiti_instance is None:
        _graphiti_instance = GraphitiBackend()
    return _graphiti_instance

