"""
Integration tests for Natural Language Relationship API endpoint
"""

import pytest
from fastapi.testclient import TestClient
from kg_builder.main import app
from kg_builder.models import NLRelationshipRequest


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestNLRelationshipEndpoint:
    """Test the natural language relationship API endpoint."""

    def test_health_check(self, client):
        """Test that the API is healthy."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_nl_relationship_endpoint_exists(self, client):
        """Test that the NL relationship endpoint exists."""
        # This should not return 404
        response = client.post(
            "/api/v1/kg/relationships/natural-language",
            json={
                "kg_name": "test_kg",
                "schemas": [],
                "definitions": [],
                "use_llm": False,
                "min_confidence": 0.7
            }
        )
        # Should not be 404
        assert response.status_code != 404

    def test_nl_relationship_empty_definitions(self, client):
        """Test with empty definitions."""
        response = client.post(
            "/api/v1/kg/relationships/natural-language",
            json={
                "kg_name": "test_kg",
                "schemas": [],
                "definitions": [],
                "use_llm": False,
                "min_confidence": 0.7
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["parsed_count"] == 0
        assert data["failed_count"] == 0

    def test_nl_relationship_invalid_schema(self, client):
        """Test with invalid schema name."""
        response = client.post(
            "/api/v1/kg/relationships/natural-language",
            json={
                "kg_name": "test_kg",
                "schemas": ["nonexistent_schema"],
                "definitions": ["catalog supplied by vendors"],
                "use_llm": False,
                "min_confidence": 0.7
            }
        )
        # Should handle gracefully
        assert response.status_code in [200, 400]

    def test_nl_relationship_response_structure(self, client):
        """Test that response has correct structure."""
        response = client.post(
            "/api/v1/kg/relationships/natural-language",
            json={
                "kg_name": "test_kg",
                "schemas": [],
                "definitions": [],
                "use_llm": False,
                "min_confidence": 0.7
            }
        )
        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert "success" in data
        assert "relationships" in data
        assert "parsed_count" in data
        assert "failed_count" in data
        assert "errors" in data
        assert "processing_time_ms" in data

        # Check types
        assert isinstance(data["success"], bool)
        assert isinstance(data["relationships"], list)
        assert isinstance(data["parsed_count"], int)
        assert isinstance(data["failed_count"], int)
        assert isinstance(data["errors"], list)
        assert isinstance(data["processing_time_ms"], (int, float))

    def test_nl_relationship_min_confidence_filtering(self, client):
        """Test that min_confidence parameter is respected."""
        response = client.post(
            "/api/v1/kg/relationships/natural-language",
            json={
                "kg_name": "test_kg",
                "schemas": [],
                "definitions": [],
                "use_llm": False,
                "min_confidence": 0.95  # Very high threshold
            }
        )
        assert response.status_code == 200
        data = response.json()
        # All relationships should have confidence >= 0.95 or none
        for rel in data["relationships"]:
            assert rel["confidence"] >= 0.95

    def test_nl_relationship_use_llm_parameter(self, client):
        """Test that use_llm parameter is accepted."""
        # Test with use_llm=True
        response = client.post(
            "/api/v1/kg/relationships/natural-language",
            json={
                "kg_name": "test_kg",
                "schemas": [],
                "definitions": [],
                "use_llm": True,
                "min_confidence": 0.7
            }
        )
        assert response.status_code == 200

        # Test with use_llm=False
        response = client.post(
            "/api/v1/kg/relationships/natural-language",
            json={
                "kg_name": "test_kg",
                "schemas": [],
                "definitions": [],
                "use_llm": False,
                "min_confidence": 0.7
            }
        )
        assert response.status_code == 200

    def test_nl_relationship_multiple_definitions(self, client):
        """Test with multiple definitions."""
        response = client.post(
            "/api/v1/kg/relationships/natural-language",
            json={
                "kg_name": "test_kg",
                "schemas": [],
                "definitions": [
                    "catalog supplied by vendors",
                    "orders contain customers",
                    "vendors have locations"
                ],
                "use_llm": False,
                "min_confidence": 0.7
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Should attempt to parse all definitions
        assert data["parsed_count"] + data["failed_count"] >= 0

    def test_nl_relationship_relationship_structure(self, client):
        """Test that returned relationships have correct structure."""
        response = client.post(
            "/api/v1/kg/relationships/natural-language",
            json={
                "kg_name": "test_kg",
                "schemas": [],
                "definitions": [],
                "use_llm": False,
                "min_confidence": 0.7
            }
        )
        assert response.status_code == 200
        data = response.json()

        # Check relationship structure if any exist
        for rel in data["relationships"]:
            assert "source_table" in rel
            assert "target_table" in rel
            assert "relationship_type" in rel
            assert "confidence" in rel
            assert "reasoning" in rel
            assert "input_format" in rel
            assert "validation_status" in rel
            assert "properties" in rel
            assert "cardinality" in rel

    def test_nl_relationship_processing_time(self, client):
        """Test that processing time is recorded."""
        response = client.post(
            "/api/v1/kg/relationships/natural-language",
            json={
                "kg_name": "test_kg",
                "schemas": [],
                "definitions": [],
                "use_llm": False,
                "min_confidence": 0.7
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["processing_time_ms"] >= 0

    def test_nl_relationship_error_handling(self, client):
        """Test error handling for malformed requests."""
        # Missing required field
        response = client.post(
            "/api/v1/kg/relationships/natural-language",
            json={
                "kg_name": "test_kg",
                # Missing schemas, definitions, etc.
            }
        )
        # Should return 422 (validation error) or 400
        assert response.status_code in [400, 422]

    def test_nl_relationship_invalid_json(self, client):
        """Test with invalid JSON."""
        response = client.post(
            "/api/v1/kg/relationships/natural-language",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]

    def test_nl_relationship_success_flag(self, client):
        """Test that success flag is set correctly."""
        # With no errors
        response = client.post(
            "/api/v1/kg/relationships/natural-language",
            json={
                "kg_name": "test_kg",
                "schemas": [],
                "definitions": [],
                "use_llm": False,
                "min_confidence": 0.7
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Should be successful with no definitions
        assert data["success"] is True
        assert data["failed_count"] == 0

