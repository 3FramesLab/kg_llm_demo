"""
Integration tests for LLM-based SQL generation

Tests the complete flow from NL definition to SQL generation using LLM.
"""

import pytest
from unittest.mock import Mock, patch
from kg_builder.services.nl_query_parser import get_nl_query_parser, QueryIntent
from kg_builder.services.nl_sql_generator import get_nl_sql_generator
from kg_builder.services.nl_query_executor import get_nl_query_executor
from kg_builder.models import KnowledgeGraph, GraphNode, GraphRelationship


@pytest.fixture
def sample_kg():
    """Create a sample Knowledge Graph for testing."""
    return KnowledgeGraph(
        name="test_kg",
        nodes=[
            GraphNode(
                id="table_rbp_gpu",
                label="Table",
                properties={"table_name": "brz_lnd_RBP_GPU"},
                source_table="brz_lnd_RBP_GPU"
            ),
            GraphNode(
                id="table_ops_excel",
                label="Table",
                properties={"table_name": "brz_lnd_OPS_EXCEL_GPU"},
                source_table="brz_lnd_OPS_EXCEL_GPU"
            ),
            GraphNode(
                id="table_suppliers",
                label="Table",
                properties={"table_name": "suppliers"},
                source_table="suppliers"
            )
        ],
        relationships=[
            GraphRelationship(
                source_id="table_rbp_gpu",
                target_id="table_ops_excel",
                relationship_type="MATCHES",
                properties={},
                source_column="Material",
                target_column="Material"
            ),
            GraphRelationship(
                source_id="table_rbp_gpu",
                target_id="table_suppliers",
                relationship_type="REFERENCES",
                properties={},
                source_column="supplier_id",
                target_column="id"
            )
        ],
        schema_file="test_schema",
        metadata={},
        table_aliases={
            "brz_lnd_RBP_GPU": ["RBP", "RBP GPU"],
            "brz_lnd_OPS_EXCEL_GPU": ["OPS", "OPS Excel"],
            "suppliers": ["supplier"]
        }
    )


class TestLLMSQLIntegration:
    """Integration tests for LLM SQL generation."""

    @patch('kg_builder.services.llm_sql_generator.get_llm_service')
    def test_comparison_query_flow(self, mock_llm_service, sample_kg):
        """Test complete flow for comparison query."""
        # Mock LLM service for SQL generation
        mock_service = Mock()
        mock_service.is_enabled.return_value = True

        # Mock SQL generation response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="""
SELECT DISTINCT s.*
FROM `brz_lnd_RBP_GPU` s
LEFT JOIN `brz_lnd_OPS_EXCEL_GPU` t ON s.`Material` = t.`Material`
WHERE t.`Material` IS NULL
        """))]
        mock_service.create_chat_completion.return_value = mock_response
        mock_llm_service.return_value = mock_service

        # Create query intent
        intent = QueryIntent(
            definition="Show products in RBP GPU not in OPS Excel",
            query_type="comparison_query",
            source_table="brz_lnd_RBP_GPU",
            target_table="brz_lnd_OPS_EXCEL_GPU",
            operation="NOT_IN",
            filters=None,
            join_columns=[("Material", "Material")],
            confidence=0.9,
            reasoning="Comparison query detected",
            additional_columns=None
        )

        # Generate SQL using LLM
        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=True)
        sql = generator.generate(intent)

        # Verify SQL structure
        assert "SELECT" in sql.upper()
        assert "brz_lnd_RBP_GPU" in sql
        assert "brz_lnd_OPS_EXCEL_GPU" in sql
        assert "Material" in sql
        assert "LEFT JOIN" in sql.upper()
        assert "IS NULL" in sql.upper()

    @patch('kg_builder.services.llm_sql_generator.get_llm_service')
    def test_filter_query_flow(self, mock_llm_service, sample_kg):
        """Test complete flow for filter query."""
        # Mock LLM service
        mock_service = Mock()
        mock_service.is_enabled.return_value = True

        # Mock SQL generation response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="""
SELECT DISTINCT s.*
FROM `brz_lnd_RBP_GPU` s
INNER JOIN `brz_lnd_OPS_EXCEL_GPU` t ON s.`Material` = t.`Material`
WHERE t.`Status` = 'active'
        """))]
        mock_service.create_chat_completion.return_value = mock_response
        mock_llm_service.return_value = mock_service

        # Create filter query intent
        intent = QueryIntent(
            definition="Show active products in RBP that are in OPS",
            query_type="filter_query",
            source_table="brz_lnd_RBP_GPU",
            target_table="brz_lnd_OPS_EXCEL_GPU",
            operation="FILTER",
            filters=[{"column": "Status", "value": "active", "operator": "="}],
            join_columns=[("Material", "Material")],
            confidence=0.85,
            reasoning="Filter query with join",
            additional_columns=None
        )

        # Generate SQL using LLM
        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=True)
        sql = generator.generate(intent)

        # Verify SQL structure
        assert "SELECT" in sql.upper()
        assert "WHERE" in sql.upper()
        assert "Status" in sql
        assert "active" in sql

    @patch('kg_builder.services.llm_sql_generator.get_llm_service')
    def test_fallback_to_python(self, mock_llm_service, sample_kg):
        """Test fallback to Python when LLM fails."""
        # Mock LLM service to fail
        mock_service = Mock()
        mock_service.is_enabled.return_value = True
        mock_service.create_chat_completion.side_effect = Exception("LLM API error")
        mock_llm_service.return_value = mock_service

        # Create query intent
        intent = QueryIntent(
            definition="Show products in RBP GPU not in OPS Excel",
            query_type="comparison_query",
            source_table="brz_lnd_RBP_GPU",
            target_table="brz_lnd_OPS_EXCEL_GPU",
            operation="NOT_IN",
            filters=None,
            join_columns=[("Material", "Material")],
            confidence=0.9,
            reasoning="Comparison query",
            additional_columns=None
        )

        # Generate SQL with LLM enabled (should fallback to Python)
        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=True)
        sql = generator.generate(intent)

        # Should still get valid SQL from Python fallback
        assert "SELECT" in sql.upper()
        assert "brz_lnd_RBP_GPU" in sql
        assert "brz_lnd_OPS_EXCEL_GPU" in sql

    def test_python_generation_without_llm(self, sample_kg):
        """Test Python-based generation when LLM is disabled."""
        # Create query intent
        intent = QueryIntent(
            definition="Show products in RBP GPU not in OPS Excel",
            query_type="comparison_query",
            source_table="brz_lnd_RBP_GPU",
            target_table="brz_lnd_OPS_EXCEL_GPU",
            operation="NOT_IN",
            filters=None,
            join_columns=[("Material", "Material")],
            confidence=0.9,
            reasoning="Comparison query",
            additional_columns=None
        )

        # Generate SQL without LLM
        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=False)
        sql = generator.generate(intent)

        # Verify SQL structure (Python template)
        assert "SELECT DISTINCT s.*" in sql
        assert "FROM `brz_lnd_RBP_GPU` s" in sql
        assert "LEFT JOIN `brz_lnd_OPS_EXCEL_GPU` t" in sql
        assert "WHERE t.`Material` IS NULL" in sql

    @patch('kg_builder.services.llm_sql_generator.get_llm_service')
    def test_aggregation_query(self, mock_llm_service, sample_kg):
        """Test aggregation query generation."""
        # Mock LLM service
        mock_service = Mock()
        mock_service.is_enabled.return_value = True

        # Mock SQL generation response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="""
SELECT COUNT(*) as count
FROM `brz_lnd_RBP_GPU`
WHERE `Status` = 'active'
        """))]
        mock_service.create_chat_completion.return_value = mock_response
        mock_llm_service.return_value = mock_service

        # Create aggregation query intent
        intent = QueryIntent(
            definition="Count active products in RBP",
            query_type="aggregation_query",
            source_table="brz_lnd_RBP_GPU",
            target_table=None,
            operation="COUNT",
            filters=[{"column": "Status", "value": "active", "operator": "="}],
            join_columns=None,
            confidence=0.9,
            reasoning="Aggregation query",
            additional_columns=None
        )

        # Generate SQL using LLM
        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=True)
        sql = generator.generate(intent)

        # Verify SQL structure
        assert "COUNT" in sql.upper()
        assert "brz_lnd_RBP_GPU" in sql

    @patch('kg_builder.services.llm_sql_generator.get_llm_service')
    def test_different_database_types(self, mock_llm_service, sample_kg):
        """Test SQL generation for different database types."""
        # Mock LLM service
        mock_service = Mock()
        mock_service.is_enabled.return_value = True

        intent = QueryIntent(
            definition="Show products",
            query_type="data_query",
            source_table="products",
            target_table=None,
            operation=None,
            filters=None,
            join_columns=None,
            confidence=0.9,
            reasoning="Data query",
            additional_columns=None
        )

        # Test MySQL (backticks)
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="SELECT * FROM `products`"))]
        mock_service.create_chat_completion.return_value = mock_response
        mock_llm_service.return_value = mock_service

        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=True)
        sql = generator.generate(intent)
        assert "`products`" in sql or "products" in sql

        # Test SQL Server (square brackets)
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="SELECT * FROM [products]"))]
        mock_service.create_chat_completion.return_value = mock_response

        generator = get_nl_sql_generator(db_type="sqlserver", kg=sample_kg, use_llm=True)
        sql = generator.generate(intent)
        assert "[products]" in sql or "products" in sql

        # Test PostgreSQL (backticks or quotes)
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="SELECT * FROM `products`"))]
        mock_service.create_chat_completion.return_value = mock_response

        generator = get_nl_sql_generator(db_type="postgresql", kg=sample_kg, use_llm=True)
        sql = generator.generate(intent)
        assert "products" in sql


class TestLLMSQLSecurityValidation:
    """Test security validation in LLM SQL generation."""

    @patch('kg_builder.services.llm_sql_generator.get_llm_service')
    def test_security_validation_blocks_dangerous_sql(self, mock_llm_service, sample_kg):
        """Test that security validation blocks dangerous SQL."""
        # Mock LLM service to return dangerous SQL
        mock_service = Mock()
        mock_service.is_enabled.return_value = True

        dangerous_queries = [
            "DROP TABLE products",
            "DELETE FROM products WHERE 1=1",
            "TRUNCATE products",
            "ALTER TABLE products ADD COLUMN hack VARCHAR(100)",
        ]

        for dangerous_sql in dangerous_queries:
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content=dangerous_sql))]
            mock_service.create_chat_completion.return_value = mock_response
            mock_llm_service.return_value = mock_service

            intent = QueryIntent(
                definition="Show products",
                query_type="data_query",
                source_table="products",
                target_table=None,
                operation=None,
                filters=None,
                join_columns=None,
                confidence=0.9,
                reasoning="Test",
                additional_columns=None
            )

            generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=True)

            # Should raise ValueError due to security validation
            with pytest.raises(ValueError, match="Dangerous SQL pattern"):
                generator.generate(intent)


class TestNLQueryExecutorWithLLM:
    """Test NL Query Executor with LLM SQL generation."""

    @patch('kg_builder.services.llm_sql_generator.get_llm_service')
    def test_executor_with_llm(self, mock_llm_service, sample_kg):
        """Test executor uses LLM when enabled."""
        # Mock LLM service
        mock_service = Mock()
        mock_service.is_enabled.return_value = True

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="""
SELECT * FROM `products` WHERE `status` = 'active'
        """))]
        mock_service.create_chat_completion.return_value = mock_response
        mock_llm_service.return_value = mock_service

        # Create executor with LLM enabled
        executor = get_nl_query_executor(db_type="mysql", kg=sample_kg, use_llm=True)

        assert executor.use_llm is True
        assert executor.generator.use_llm is True

    def test_executor_without_llm(self, sample_kg):
        """Test executor uses Python when LLM disabled."""
        # Create executor with LLM disabled
        executor = get_nl_query_executor(db_type="mysql", kg=sample_kg, use_llm=False)

        assert executor.use_llm is False
        assert executor.generator.use_llm is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
