"""
Tests for Knowledge Graph Integration with Natural Language Relationships.

Tests the integration of NL-defined relationships into existing knowledge graphs.
"""

import pytest
from kg_builder.models import (
    GraphNode, GraphRelationship, KnowledgeGraph, 
    RelationshipDefinition, NLInputFormat
)
from kg_builder.services.schema_parser import SchemaParser
from datetime import datetime


class TestKGIntegration:
    """Test KG integration with NL relationships."""
    
    @pytest.fixture
    def sample_kg(self):
        """Create a sample knowledge graph for testing."""
        nodes = [
            GraphNode(id="table_products", label="products", properties={"type": "Table"}),
            GraphNode(id="table_vendors", label="vendors", properties={"type": "Table"}),
            GraphNode(id="table_orders", label="orders", properties={"type": "Table"}),
        ]
        
        relationships = [
            GraphRelationship(
                source_id="table_orders",
                target_id="table_products",
                relationship_type="FOREIGN_KEY",
                properties={"source": "auto_detected", "confidence": 0.95}
            ),
        ]
        
        kg = KnowledgeGraph(
            name="test_kg",
            nodes=nodes,
            relationships=relationships,
            schema_file="test_schema"
        )
        return kg
    
    @pytest.fixture
    def sample_nl_relationships(self):
        """Create sample NL-defined relationships."""
        return [
            RelationshipDefinition(
                source_table="products",
                target_table="vendors",
                relationship_type="SUPPLIED_BY",
                properties=["vendor_id"],
                cardinality="N:1",
                confidence=0.85,
                reasoning="Products are supplied by vendors",
                input_format=NLInputFormat.NATURAL_LANGUAGE,
                validation_status="VALID"
            ),
            RelationshipDefinition(
                source_table="orders",
                target_table="vendors",
                relationship_type="PLACED_BY",
                properties=["vendor_id"],
                cardinality="N:1",
                confidence=0.80,
                reasoning="Orders are placed by vendors",
                input_format=NLInputFormat.NATURAL_LANGUAGE,
                validation_status="VALID"
            ),
        ]
    
    def test_add_nl_relationships_to_kg(self, sample_kg, sample_nl_relationships):
        """Test adding NL relationships to KG."""
        initial_count = len(sample_kg.relationships)
        
        updated_kg = SchemaParser.add_nl_relationships_to_kg(
            sample_kg, 
            sample_nl_relationships
        )
        
        assert len(updated_kg.relationships) == initial_count + 2
        assert updated_kg.name == "test_kg"
        
        # Check that NL relationships were added
        nl_rels = [r for r in updated_kg.relationships if r.properties.get("nl_defined")]
        assert len(nl_rels) == 2
    
    def test_add_nl_relationships_marks_source(self, sample_kg, sample_nl_relationships):
        """Test that NL relationships are marked with source."""
        updated_kg = SchemaParser.add_nl_relationships_to_kg(
            sample_kg, 
            sample_nl_relationships
        )
        
        nl_rels = [r for r in updated_kg.relationships if r.properties.get("nl_defined")]
        
        for rel in nl_rels:
            assert rel.properties["source"] == "natural_language"
            assert "confidence" in rel.properties
            assert "reasoning" in rel.properties
    
    def test_add_nl_relationships_skips_invalid(self, sample_kg):
        """Test that invalid relationships are skipped."""
        invalid_rel = RelationshipDefinition(
            source_table="products",
            target_table="vendors",
            relationship_type="SUPPLIED_BY",
            confidence=0.85,
            reasoning="Test",
            input_format=NLInputFormat.NATURAL_LANGUAGE,
            validation_status="INVALID",
            validation_errors=["Table not found"]
        )
        
        initial_count = len(sample_kg.relationships)
        updated_kg = SchemaParser.add_nl_relationships_to_kg(sample_kg, [invalid_rel])
        
        assert len(updated_kg.relationships) == initial_count
    
    def test_add_nl_relationships_avoids_duplicates(self, sample_kg, sample_nl_relationships):
        """Test that duplicate relationships are not added."""
        # Add relationships once
        updated_kg = SchemaParser.add_nl_relationships_to_kg(
            sample_kg, 
            sample_nl_relationships
        )
        
        count_after_first = len(updated_kg.relationships)
        
        # Try to add the same relationships again
        updated_kg = SchemaParser.add_nl_relationships_to_kg(
            updated_kg, 
            sample_nl_relationships
        )
        
        # Count should not increase
        assert len(updated_kg.relationships) == count_after_first
    
    def test_merge_relationships_deduplicate(self, sample_kg):
        """Test deduplication merge strategy."""
        # Add duplicate relationships
        dup_rel = GraphRelationship(
            source_id="table_orders",
            target_id="table_products",
            relationship_type="FOREIGN_KEY",
            properties={"source": "auto_detected"}
        )
        sample_kg.relationships.append(dup_rel)
        
        initial_count = len(sample_kg.relationships)
        merged_kg = SchemaParser.merge_relationships(sample_kg, strategy="deduplicate")
        
        assert len(merged_kg.relationships) < initial_count
    
    def test_merge_relationships_high_confidence(self, sample_kg):
        """Test high confidence merge strategy."""
        # Add low confidence relationship
        low_conf_rel = GraphRelationship(
            source_id="table_vendors",
            target_id="table_orders",
            relationship_type="INFERRED",
            properties={"confidence": 0.5}
        )
        sample_kg.relationships.append(low_conf_rel)
        
        merged_kg = SchemaParser.merge_relationships(sample_kg, strategy="high_confidence")
        
        # Should only have high confidence relationships
        for rel in merged_kg.relationships:
            confidence = rel.properties.get("confidence", 0.75)
            assert confidence >= 0.7
    
    def test_merge_relationships_union(self, sample_kg):
        """Test union merge strategy (keep all)."""
        initial_count = len(sample_kg.relationships)
        
        merged_kg = SchemaParser.merge_relationships(sample_kg, strategy="union")
        
        assert len(merged_kg.relationships) == initial_count
    
    def test_get_relationship_statistics(self, sample_kg, sample_nl_relationships):
        """Test relationship statistics calculation."""
        updated_kg = SchemaParser.add_nl_relationships_to_kg(
            sample_kg, 
            sample_nl_relationships
        )
        
        stats = SchemaParser.get_relationship_statistics(updated_kg)
        
        assert stats["total_relationships"] == 3
        assert stats["nl_defined"] == 2
        assert stats["auto_detected"] == 1
        assert "by_type" in stats
        assert "by_source" in stats
        assert "average_confidence" in stats
        assert stats["average_confidence"] > 0
    
    def test_get_relationship_statistics_by_type(self, sample_kg, sample_nl_relationships):
        """Test relationship statistics by type."""
        updated_kg = SchemaParser.add_nl_relationships_to_kg(
            sample_kg, 
            sample_nl_relationships
        )
        
        stats = SchemaParser.get_relationship_statistics(updated_kg)
        
        assert "FOREIGN_KEY" in stats["by_type"]
        assert "SUPPLIED_BY" in stats["by_type"]
        assert "PLACED_BY" in stats["by_type"]
    
    def test_get_relationship_statistics_high_confidence(self, sample_kg):
        """Test high confidence count in statistics."""
        # Add mix of high and low confidence relationships
        high_conf = GraphRelationship(
            source_id="table_vendors",
            target_id="table_orders",
            relationship_type="TEST",
            properties={"confidence": 0.9}
        )
        low_conf = GraphRelationship(
            source_id="table_products",
            target_id="table_orders",
            relationship_type="TEST2",
            properties={"confidence": 0.5}
        )
        
        sample_kg.relationships.extend([high_conf, low_conf])
        
        stats = SchemaParser.get_relationship_statistics(sample_kg)
        
        assert stats["high_confidence_count"] >= 1
        assert stats["total_relationships"] == 3
    
    def test_integration_workflow(self, sample_kg, sample_nl_relationships):
        """Test complete integration workflow."""
        # Step 1: Add NL relationships
        updated_kg = SchemaParser.add_nl_relationships_to_kg(
            sample_kg, 
            sample_nl_relationships
        )
        
        # Step 2: Merge relationships
        merged_kg = SchemaParser.merge_relationships(updated_kg, strategy="deduplicate")
        
        # Step 3: Get statistics
        stats = SchemaParser.get_relationship_statistics(merged_kg)
        
        # Verify workflow
        assert len(merged_kg.relationships) >= 3
        assert stats["nl_defined"] == 2
        assert stats["auto_detected"] == 1
        assert stats["total_relationships"] == len(merged_kg.relationships)


class TestKGIntegrationEdgeCases:
    """Test edge cases in KG integration."""
    
    def test_add_nl_relationships_empty_list(self):
        """Test adding empty list of NL relationships."""
        kg = KnowledgeGraph(
            name="test_kg",
            nodes=[],
            relationships=[],
            schema_file="test"
        )
        
        updated_kg = SchemaParser.add_nl_relationships_to_kg(kg, [])
        
        assert len(updated_kg.relationships) == 0
    
    def test_add_nl_relationships_to_empty_kg(self):
        """Test adding NL relationships to empty KG."""
        kg = KnowledgeGraph(
            name="test_kg",
            nodes=[],
            relationships=[],
            schema_file="test"
        )
        
        nl_rel = RelationshipDefinition(
            source_table="products",
            target_table="vendors",
            relationship_type="SUPPLIED_BY",
            confidence=0.85,
            reasoning="Test",
            input_format=NLInputFormat.NATURAL_LANGUAGE,
            validation_status="VALID"
        )
        
        updated_kg = SchemaParser.add_nl_relationships_to_kg(kg, [nl_rel])
        
        assert len(updated_kg.relationships) == 1
    
    def test_statistics_empty_kg(self):
        """Test statistics for empty KG."""
        kg = KnowledgeGraph(
            name="test_kg",
            nodes=[],
            relationships=[],
            schema_file="test"
        )
        
        stats = SchemaParser.get_relationship_statistics(kg)
        
        assert stats["total_relationships"] == 0
        assert stats["nl_defined"] == 0
        assert stats["auto_detected"] == 0
        assert stats["average_confidence"] == 0.0

