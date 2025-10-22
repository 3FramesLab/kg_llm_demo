"""
API Integration Tests for Knowledge Graph Integration Endpoints.

Tests the API endpoints for integrating NL relationships into knowledge graphs.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from kg_builder.models import (
    KnowledgeGraph, GraphNode, GraphRelationship,
    RelationshipDefinition, NLInputFormat
)


@pytest.fixture
def client():
    """Create a test client."""
    from kg_builder.main import app
    return TestClient(app)


@pytest.fixture
def mock_kg():
    """Create a mock knowledge graph."""
    nodes = [
        GraphNode(id="table_products", label="products", properties={"type": "Table"}),
        GraphNode(id="table_vendors", label="vendors", properties={"type": "Table"}),
    ]
    
    relationships = [
        GraphRelationship(
            source_id="table_products",
            target_id="table_vendors",
            relationship_type="FOREIGN_KEY",
            properties={"source": "auto_detected", "confidence": 0.95}
        ),
    ]
    
    return KnowledgeGraph(
        name="test_kg",
        nodes=nodes,
        relationships=relationships,
        schema_file="test_schema"
    )


class TestKGIntegrationAPI:
    """Test KG integration API endpoints."""
    
    @patch('kg_builder.routes.SchemaParser.build_merged_knowledge_graph')
    @patch('kg_builder.routes.get_nl_relationship_parser')
    def test_integrate_nl_relationships_success(self, mock_parser, mock_build_kg, client, mock_kg):
        """Test successful NL relationship integration."""
        # Mock the parser
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance

        nl_rel = RelationshipDefinition(
            source_table="products",
            target_table="vendors",
            relationship_type="SUPPLIED_BY",
            confidence=0.85,
            reasoning="Products are supplied by vendors",
            input_format=NLInputFormat.NATURAL_LANGUAGE,
            validation_status="VALID"
        )
        mock_parser_instance.parse.return_value = [nl_rel]

        # Mock KG building
        mock_build_kg.return_value = mock_kg

        response = client.post(
            "/api/v1/kg/integrate-nl-relationships",
            json={
                "kg_name": "test_kg",
                "nl_definitions": ["Products are supplied by Vendors"],
                "schemas": ["schema1"],
                "use_llm": True,
                "min_confidence": 0.7,
                "merge_strategy": "union"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["kg_name"] == "test_kg"
        assert "statistics" in data
        assert "processing_time_ms" in data
    
    @patch('kg_builder.routes.SchemaParser.build_merged_knowledge_graph')
    @patch('kg_builder.routes.get_nl_relationship_parser')
    def test_integrate_nl_relationships_with_errors(self, mock_parser, mock_build_kg, client, mock_kg):
        """Test NL relationship integration with parsing errors."""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance

        # Simulate parsing error
        mock_parser_instance.parse.side_effect = Exception("Parse error")

        mock_build_kg.return_value = mock_kg

        response = client.post(
            "/api/v1/kg/integrate-nl-relationships",
            json={
                "kg_name": "test_kg",
                "nl_definitions": ["Invalid definition"],
                "schemas": ["schema1"],
                "use_llm": True,
                "min_confidence": 0.7,
                "merge_strategy": "union"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["errors"]) > 0
    
    @patch('kg_builder.routes.SchemaParser.build_merged_knowledge_graph')
    def test_integrate_nl_relationships_kg_build_failure(self, mock_build_kg, client):
        """Test handling of KG build failure."""
        mock_build_kg.side_effect = Exception("Schema not found")

        response = client.post(
            "/api/v1/kg/integrate-nl-relationships",
            json={
                "kg_name": "test_kg",
                "nl_definitions": ["Products are supplied by Vendors"],
                "schemas": ["nonexistent_schema"],
                "use_llm": True,
                "min_confidence": 0.7,
                "merge_strategy": "union"
            }
        )

        assert response.status_code == 400

    @patch('kg_builder.routes.SchemaParser.build_merged_knowledge_graph')
    def test_integrate_nl_relationships_merge_strategies(self, mock_build_kg, client, mock_kg):
        """Test different merge strategies."""
        mock_build_kg.return_value = mock_kg

        strategies = ["union", "deduplicate", "high_confidence"]

        for strategy in strategies:
            response = client.post(
                "/api/v1/kg/integrate-nl-relationships",
                json={
                    "kg_name": "test_kg",
                    "nl_definitions": [],
                    "schemas": ["schema1"],
                    "use_llm": False,
                    "min_confidence": 0.7,
                    "merge_strategy": strategy
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["kg_name"] == "test_kg"
    
    @patch('kg_builder.routes.SchemaParser.build_merged_knowledge_graph')
    @patch('kg_builder.routes.get_nl_relationship_parser')
    def test_integrate_nl_relationships_confidence_filtering(self, mock_parser, mock_build_kg, client, mock_kg):
        """Test confidence-based filtering."""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        
        # Create relationships with different confidence levels
        high_conf = RelationshipDefinition(
            source_table="products",
            target_table="vendors",
            relationship_type="SUPPLIED_BY",
            confidence=0.9,
            reasoning="High confidence",
            input_format=NLInputFormat.NATURAL_LANGUAGE,
            validation_status="VALID"
        )
        
        low_conf = RelationshipDefinition(
            source_table="orders",
            target_table="vendors",
            relationship_type="PLACED_BY",
            confidence=0.5,
            reasoning="Low confidence",
            input_format=NLInputFormat.NATURAL_LANGUAGE,
            validation_status="VALID"
        )
        
        mock_parser_instance.parse.return_value = [high_conf, low_conf]
        mock_build_kg.return_value = mock_kg

        response = client.post(
            "/api/v1/kg/integrate-nl-relationships",
            json={
                "kg_name": "test_kg",
                "nl_definitions": ["Test definition"],
                "schemas": ["schema1"],
                "use_llm": False,
                "min_confidence": 0.7,
                "merge_strategy": "union"
            }
        )

        assert response.status_code == 200
        data = response.json()
        # Only high confidence relationship should be added
        assert data["nl_relationships_added"] == 1

    @patch('kg_builder.routes.SchemaParser.build_merged_knowledge_graph')
    def test_get_kg_statistics_success(self, mock_build_kg, client, mock_kg):
        """Test getting KG statistics."""
        mock_build_kg.return_value = mock_kg

        response = client.post(
            "/api/v1/kg/statistics",
            json={"kg_name": "test_kg", "nl_definitions": [], "schemas": ["schema1"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["kg_name"] == "test_kg"
        assert data["nodes_count"] == 2
        assert data["relationships_count"] == 1
        assert "statistics" in data

    @patch('kg_builder.routes.SchemaParser.build_merged_knowledge_graph')
    def test_get_kg_statistics_failure(self, mock_build_kg, client):
        """Test getting statistics with error."""
        mock_build_kg.side_effect = Exception("Schema not found")

        response = client.post(
            "/api/v1/kg/statistics",
            json={"kg_name": "test_kg", "nl_definitions": [], "schemas": ["nonexistent"]}
        )
        
        assert response.status_code == 500


class TestKGIntegrationAPIValidation:
    """Test API parameter validation."""

    @patch('kg_builder.routes.SchemaParser.build_merged_knowledge_graph')
    def test_integrate_nl_relationships_empty_definitions(self, mock_build_kg, client, mock_kg):
        """Test with empty definitions list."""
        mock_build_kg.return_value = mock_kg

        response = client.post(
            "/api/v1/kg/integrate-nl-relationships",
            json={
                "kg_name": "test_kg",
                "nl_definitions": [],
                "schemas": ["schema1"],
                "use_llm": True,
                "min_confidence": 0.7,
                "merge_strategy": "union"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nl_relationships_added"] == 0

    @patch('kg_builder.routes.SchemaParser.build_merged_knowledge_graph')
    def test_integrate_nl_relationships_empty_schemas(self, mock_build_kg, client, mock_kg):
        """Test with empty schemas list."""
        mock_build_kg.return_value = mock_kg

        response = client.post(
            "/api/v1/kg/integrate-nl-relationships",
            json={
                "kg_name": "test_kg",
                "nl_definitions": ["Test"],
                "schemas": [],
                "use_llm": False,
                "min_confidence": 0.7,
                "merge_strategy": "union"
            }
        )

        assert response.status_code == 200

    @patch('kg_builder.routes.SchemaParser.build_merged_knowledge_graph')
    def test_integrate_nl_relationships_invalid_confidence(self, mock_build_kg, client, mock_kg):
        """Test with invalid confidence threshold."""
        mock_build_kg.return_value = mock_kg

        # Test with confidence > 1.0
        response = client.post(
            "/api/v1/kg/integrate-nl-relationships",
            json={
                "kg_name": "test_kg",
                "nl_definitions": ["Test"],
                "schemas": ["schema1"],
                "use_llm": False,
                "min_confidence": 1.5,
                "merge_strategy": "union"
            }
        )

        # Should still work (filtering will just exclude everything)
        assert response.status_code == 200

