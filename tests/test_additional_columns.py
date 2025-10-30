"""
Tests for multi-table column inclusion feature.

Tests the following components:
- AdditionalColumn model
- JoinPath model
- NL Query Parser column extraction
- NL Query Parser column validation
- NL Query Parser join path discovery
- NL SQL Generator additional columns handling
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass

from kg_builder.models import AdditionalColumn, JoinPath, GraphNode, GraphRelationship, KnowledgeGraph
from kg_builder.services.nl_query_parser import (
    NLQueryParser, QueryIntent, ColumnInclusionError, 
    ColumnNotFoundError, JoinPathNotFoundError, TableNotFoundError
)
from kg_builder.services.nl_sql_generator import NLSQLGenerator


class TestAdditionalColumnModel:
    """Test AdditionalColumn model."""
    
    def test_additional_column_creation(self):
        """Test creating an AdditionalColumn."""
        col = AdditionalColumn(
            column_name="planner",
            source_table="hana_material_master"
        )
        assert col.column_name == "planner"
        assert col.source_table == "hana_material_master"
        assert col.alias == "master_planner"  # Auto-generated
    
    def test_additional_column_with_custom_alias(self):
        """Test creating an AdditionalColumn with custom alias."""
        col = AdditionalColumn(
            column_name="planner",
            source_table="hana_material_master",
            alias="custom_planner"
        )
        assert col.alias == "custom_planner"
    
    def test_additional_column_with_join_path(self):
        """Test AdditionalColumn with join path."""
        col = AdditionalColumn(
            column_name="planner",
            source_table="hana_material_master",
            join_path=["brz_lnd_RBP_GPU", "hana_material_master"],
            confidence=0.85
        )
        assert col.join_path == ["brz_lnd_RBP_GPU", "hana_material_master"]
        assert col.confidence == 0.85


class TestJoinPathModel:
    """Test JoinPath model."""
    
    def test_join_path_creation(self):
        """Test creating a JoinPath."""
        path = JoinPath(
            source_table="brz_lnd_RBP_GPU",
            target_table="hana_material_master",
            path=["brz_lnd_RBP_GPU", "hana_material_master"],
            confidence=0.85,
            length=1
        )
        assert path.source_table == "brz_lnd_RBP_GPU"
        assert path.target_table == "hana_material_master"
        assert path.length == 1
    
    def test_join_path_scoring(self):
        """Test join path scoring."""
        path = JoinPath(
            source_table="brz_lnd_RBP_GPU",
            target_table="hana_material_master",
            path=["brz_lnd_RBP_GPU", "hana_material_master"],
            confidence=0.85,
            length=1
        )
        score = path.score()
        # Score = (0.85 * 0.7) + (1/1 * 0.3) = 0.595 + 0.3 = 0.895
        assert 0.89 < score < 0.90


class TestQueryIntentExtension:
    """Test QueryIntent with additional_columns field."""
    
    def test_query_intent_with_additional_columns(self):
        """Test QueryIntent with additional columns."""
        col = AdditionalColumn(
            column_name="planner",
            source_table="hana_material_master"
        )
        intent = QueryIntent(
            definition="Show products, include planner from HANA",
            query_type="comparison_query",
            source_table="brz_lnd_RBP_GPU",
            additional_columns=[col]
        )
        assert len(intent.additional_columns) == 1
        assert intent.additional_columns[0].column_name == "planner"
    
    def test_query_intent_to_dict_with_additional_columns(self):
        """Test QueryIntent.to_dict() with additional columns."""
        col = AdditionalColumn(
            column_name="planner",
            source_table="hana_material_master"
        )
        intent = QueryIntent(
            definition="Show products, include planner from HANA",
            query_type="comparison_query",
            source_table="brz_lnd_RBP_GPU",
            additional_columns=[col]
        )
        data = intent.to_dict()
        assert "additional_columns" in data
        assert len(data["additional_columns"]) == 1


class TestNLQueryParserColumnExtraction:
    """Test NL Query Parser column extraction."""
    
    @pytest.fixture
    def mock_parser(self):
        """Create a mock parser."""
        parser = NLQueryParser(kg=None, schemas_info={})
        parser.llm_service = Mock()
        parser.llm_service.is_enabled.return_value = True
        return parser
    
    def test_extract_additional_columns_single(self, mock_parser):
        """Test extracting a single additional column."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '[{"column_name": "planner", "source_table": "HANA Master"}]'
        mock_parser.llm_service.create_chat_completion.return_value = mock_response
        
        columns = mock_parser._extract_additional_columns(
            "Show products in RBP, include planner from HANA Master"
        )
        
        assert len(columns) == 1
        assert columns[0]["column_name"] == "planner"
        assert columns[0]["source_table"] == "HANA Master"
    
    def test_extract_additional_columns_multiple(self, mock_parser):
        """Test extracting multiple additional columns."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''[
            {"column_name": "planner", "source_table": "HANA Master"},
            {"column_name": "category", "source_table": "Product Master"}
        ]'''
        mock_parser.llm_service.create_chat_completion.return_value = mock_response
        
        columns = mock_parser._extract_additional_columns(
            "Show products, include planner from HANA and category from Product Master"
        )
        
        assert len(columns) == 2
        assert columns[0]["column_name"] == "planner"
        assert columns[1]["column_name"] == "category"
    
    def test_extract_additional_columns_none(self, mock_parser):
        """Test when no additional columns are requested."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '[]'
        mock_parser.llm_service.create_chat_completion.return_value = mock_response
        
        columns = mock_parser._extract_additional_columns(
            "Show products in RBP not in OPS"
        )
        
        assert len(columns) == 0


class TestNLSQLGeneratorAdditionalColumns:
    """Test NL SQL Generator with additional columns."""

    def _create_test_kg(self):
        """Create a test Knowledge Graph with relationships."""
        # Create nodes
        node1 = GraphNode(
            id="brz_lnd_rbp_gpu",
            label="brz_lnd_RBP_GPU",
            properties={"type": "Table", "columns": ["Material", "Product_Line"]}
        )
        node2 = GraphNode(
            id="hana_material_master",
            label="hana_material_master",
            properties={"type": "Table", "columns": ["MATERIAL", "planner"]}
        )

        # Create relationship with join columns
        rel = GraphRelationship(
            source_id="brz_lnd_rbp_gpu",
            target_id="hana_material_master",
            relationship_type="REFERENCES",
            source_column="Material",
            target_column="MATERIAL",
            properties={"llm_confidence": 0.95}
        )

        kg = KnowledgeGraph(
            name="test_kg",
            nodes=[node1, node2],
            relationships=[rel],
            schema_file="test_schema"
        )
        return kg

    def test_add_additional_columns_to_sql(self):
        """Test adding additional columns to SQL."""
        kg = self._create_test_kg()
        generator = NLSQLGenerator(db_type="mysql", kg=kg)

        base_sql = "SELECT DISTINCT s.* FROM brz_lnd_RBP_GPU s"

        col = AdditionalColumn(
            column_name="planner",
            source_table="hana_material_master",
            alias="hana_planner",
            join_path=["brz_lnd_RBP_GPU", "hana_material_master"]
        )

        intent = QueryIntent(
            definition="Show products, include planner",
            query_type="filter_query",
            source_table="brz_lnd_RBP_GPU",
            additional_columns=[col]
        )

        result_sql = generator._add_additional_columns_to_sql(base_sql, intent)

        # Check that additional column is in SELECT
        assert "hana_planner" in result_sql
        assert "planner" in result_sql

    def test_get_table_alias(self):
        """Test table alias generation."""
        generator = NLSQLGenerator()

        alias1 = generator._get_table_alias("brz_lnd_RBP_GPU")
        assert alias1 == "g"  # Last part is GPU

        alias2 = generator._get_table_alias("hana_material_master")
        assert alias2 == "m"  # Last part is master


class TestBackwardCompatibility:
    """Test that existing flows are not broken."""
    
    def test_query_intent_without_additional_columns(self):
        """Test QueryIntent works without additional columns."""
        intent = QueryIntent(
            definition="Show products in RBP not in OPS",
            query_type="comparison_query",
            source_table="brz_lnd_RBP_GPU",
            target_table="brz_lnd_OPS_EXCEL_GPU"
        )
        
        # Should have empty list, not None
        assert intent.additional_columns == []
        assert isinstance(intent.additional_columns, list)
    
    def test_sql_generator_without_additional_columns(self):
        """Test SQL generator works without additional columns."""
        generator = NLSQLGenerator()
        
        intent = QueryIntent(
            definition="Show products in RBP not in OPS",
            query_type="comparison_query",
            source_table="brz_lnd_RBP_GPU",
            target_table="brz_lnd_OPS_EXCEL_GPU",
            operation="NOT_IN",
            join_columns=[("gpu_id", "product_id")]
        )
        
        # Should not raise error
        sql = generator._generate_comparison_query(intent)
        assert "SELECT" in sql
        assert "FROM" in sql


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

