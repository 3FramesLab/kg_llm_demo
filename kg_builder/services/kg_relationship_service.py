"""
Service for processing explicit relationship pairs and adding them to Knowledge Graphs.

This service handles the v2 relationship-centric approach for KG creation,
where users explicitly define source→target relationships instead of ambiguous field hints.
"""

import logging
from typing import Dict, List, Any, Tuple
from kg_builder.models import RelationshipPair, KnowledgeGraph, GraphRelationship, KGRelationshipType

logger = logging.getLogger(__name__)

# Import the relationship normalizer
try:
    from kg_builder.table_name_normalizer import CombinedNormalizer

    # Initialize the normalizer with remove_prefix strategy
    relationship_normalizer = CombinedNormalizer(table_strategy='remove_prefix')
    logger.info("✅ Relationship normalizer initialized in kg_relationship_service")
except ImportError as e:
    logger.warning(f"⚠️ Could not import relationship normalizer in kg_relationship_service: {e}")
    relationship_normalizer = None


def normalize_explicit_relationship(relationship: GraphRelationship) -> GraphRelationship:
    """
    Normalize an explicit GraphRelationship using the global normalizer.

    Args:
        relationship: Original GraphRelationship

    Returns:
        Normalized GraphRelationship
    """
    if relationship_normalizer is None:
        logger.warning("Relationship normalizer not available, returning original relationship")
        return relationship

    try:
        # Convert GraphRelationship to dict for normalization
        rel_dict = {
            'source_id': relationship.source_id,
            'target_id': relationship.target_id,
            'relationship_type': relationship.relationship_type,
            'source_column': relationship.source_column,
            'target_column': relationship.target_column,
            'properties': relationship.properties
        }

        # Normalize the relationship
        normalized_dict = relationship_normalizer.normalize_relationship(rel_dict)

        # Convert back to GraphRelationship
        normalized_relationship = GraphRelationship(
            source_id=normalized_dict['source_id'],
            target_id=normalized_dict['target_id'],
            relationship_type=normalized_dict['relationship_type'],
            source_column=normalized_dict.get('source_column'),
            target_column=normalized_dict.get('target_column'),
            properties=normalized_dict.get('properties', {})
        )

        return normalized_relationship

    except Exception as e:
        logger.error(f"Error normalizing explicit relationship: {e}")
        return relationship


def add_explicit_relationships_to_kg(
    kg: KnowledgeGraph,
    pairs: List[RelationshipPair],
    schemas_info: Dict[str, Any]
) -> Tuple[KnowledgeGraph, int]:
    """
    Add explicit relationship pairs to a Knowledge Graph.

    Args:
        kg: Knowledge Graph to add relationships to
        pairs: List of RelationshipPair objects
        schemas_info: Schema information for validation

    Returns:
        Tuple of (updated_kg, count_of_added_relationships)
    """
    added_count = 0

    for pair in pairs:
        try:
            # Validate the pair
            if not _validate_relationship_pair(pair, schemas_info):
                logger.warning(
                    f"Skipping invalid relationship pair: {pair.source_table}.{pair.source_column} → "
                    f"{pair.target_table}.{pair.target_column}"
                )
                continue

            # Add the relationship to KG
            relationship = _create_graph_relationship(pair, forward=True)
            kg.relationships.append(relationship)
            added_count += 1

            logger.debug(
                f"Added relationship: {pair.source_table}.{pair.source_column} → "
                f"{pair.target_table}.{pair.target_column} ({pair.relationship_type})"
            )

            # Add reverse relationship if bidirectional
            if pair.bidirectional:
                reverse_rel = _create_graph_relationship(pair, forward=False)
                kg.relationships.append(reverse_rel)
                added_count += 1

                logger.debug(
                    f"Added reverse relationship: {pair.target_table}.{pair.target_column} → "
                    f"{pair.source_table}.{pair.source_column}"
                )

        except Exception as e:
            logger.error(
                f"Error adding relationship pair {pair.source_table}.{pair.source_column} → "
                f"{pair.target_table}.{pair.target_column}: {e}"
            )
            continue

    logger.info(f"Added {added_count} explicit relationship(s) to KG")
    return kg, added_count


def _validate_relationship_pair(
    pair: RelationshipPair,
    schemas_info: Dict[str, Any]
) -> bool:
    """
    Validate that a relationship pair references valid tables and columns.

    Args:
        pair: RelationshipPair to validate
        schemas_info: Schema information

    Returns:
        True if valid, False otherwise
    """
    try:
        # Find which schema contains source table
        source_schema = None
        for schema_name, schema_data in schemas_info.items():
            if pair.source_table in schema_data.get("tables", []):
                source_schema = schema_name
                break

        if not source_schema:
            logger.debug(f"Source table '{pair.source_table}' not found in any schema")
            return False

        # Validate source column exists
        source_columns = schemas_info[source_schema]["columns"].get(pair.source_table, [])
        if pair.source_column not in source_columns:
            logger.debug(
                f"Source column '{pair.source_column}' not found in {pair.source_table}. "
                f"Available: {source_columns}"
            )
            return False

        # Find which schema contains target table
        target_schema = None
        for schema_name, schema_data in schemas_info.items():
            if pair.target_table in schema_data.get("tables", []):
                target_schema = schema_name
                break

        if not target_schema:
            logger.debug(f"Target table '{pair.target_table}' not found in any schema")
            return False

        # Validate target column exists
        target_columns = schemas_info[target_schema]["columns"].get(pair.target_table, [])
        if pair.target_column not in target_columns:
            logger.debug(
                f"Target column '{pair.target_column}' not found in {pair.target_table}. "
                f"Available: {target_columns}"
            )
            return False

        return True

    except Exception as e:
        logger.error(f"Error validating relationship pair: {e}")
        return False


def _create_graph_relationship(
    pair: RelationshipPair,
    forward: bool = True
) -> GraphRelationship:
    """
    Create a GraphRelationship from a RelationshipPair.

    Args:
        pair: RelationshipPair to convert
        forward: If True, create forward relationship; if False, create reverse

    Returns:
        GraphRelationship object
    """
    if forward:
        source_id = f"{pair.source_table}"
        target_id = f"{pair.target_table}"
        source_column = pair.source_column
        target_column = pair.target_column
        relationship_type = pair.relationship_type.value
    else:
        # Reverse: swap source and target
        source_id = f"{pair.target_table}"
        target_id = f"{pair.source_table}"
        source_column = pair.target_column
        target_column = pair.source_column
        # Reverse relationship type if applicable
        relationship_type = _get_reverse_relationship_type(pair.relationship_type).value

    # Build metadata
    metadata = pair.metadata or {}
    metadata.update({
        "source": "explicit_pair_v2",
        "confidence": pair.confidence,
        "bidirectional": pair.bidirectional,
        "forward": forward
    })

    # Create the explicit relationship
    relationship = GraphRelationship(
        source_id=source_id,
        target_id=target_id,
        relationship_type=relationship_type,
        source_column=source_column,
        target_column=target_column,
        properties={
            "confidence": pair.confidence,
            "source_column": source_column,
            "target_column": target_column,
            "llm_inferred": False,
            "explicit": True,
            **metadata
        }
    )

    # Apply normalization to the explicit relationship
    normalized_relationship = normalize_explicit_relationship(relationship)
    return normalized_relationship


def _get_reverse_relationship_type(rel_type: KGRelationshipType) -> KGRelationshipType:
    """
    Get the reverse relationship type for bidirectional relationships.

    Args:
        rel_type: Original relationship type

    Returns:
        Reversed relationship type
    """
    reverse_map = {
        KGRelationshipType.CONTAINS: KGRelationshipType.BELONGS_TO,
        KGRelationshipType.BELONGS_TO: KGRelationshipType.CONTAINS,
        # Symmetric relationships stay the same
        KGRelationshipType.MATCHES: KGRelationshipType.MATCHES,
        KGRelationshipType.REFERENCES: KGRelationshipType.REFERENCES,
        KGRelationshipType.RELATED_TO: KGRelationshipType.RELATED_TO,
        # For FK and cross-schema, use generic REFERENCES in reverse
        KGRelationshipType.FOREIGN_KEY: KGRelationshipType.REFERENCES,
        KGRelationshipType.CROSS_SCHEMA_REFERENCE: KGRelationshipType.REFERENCES,
        KGRelationshipType.SEMANTIC_REFERENCE: KGRelationshipType.REFERENCES,
    }

    return reverse_map.get(rel_type, rel_type)
