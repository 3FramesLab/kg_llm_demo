"""
Unit tests for LLM SQL Generator

Tests the LLM-based SQL generation with validation and fallback mechanisms.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from kg_builder.services.llm_sql_generator import LLMSQLGenerator
from kg_builder.services.nl_query_parser import QueryIntent
from kg_builder.models import KnowledgeGraph, GraphNode, GraphRelationship


@pytest.fixture
def mock_kg():
    """Create a mock Knowledge Graph."""
    return KnowledgeGraph(
        name="test_kg",
        nodes=[
            GraphNode(
                id="table_products",
                label="Table",
                properties={"table_name": "products"},
                source_table="products"
            ),
            GraphNode(
                id="table_orders",
                label="Table",
                properties={"table_name": "orders"},
                source_table="orders"
            )
        ],
        relationships=[
            GraphRelationship(
                source_id="table_products",
                target_id="table_orders",
                relationship_type="REFERENCES",
                properties={},
                source_column="product_id",
                target_column="product_id"
            )
        ],
        schema_file="test_schema",
        metadata={},
        table_aliases={"products": ["prod"], "orders": ["ord"]}
    )


@pytest.fixture
def comparison_intent():
    """Create a comparison query intent."""
    return QueryIntent(
        definition="Show products in table_a not in table_b",
        query_type="comparison_query",
        source_table="table_a",
        target_table="table_b",
        operation="NOT_IN",
        filters=None,
        join_columns=[("id", "id")],
        confidence=0.9,
        reasoning="Comparison query detected",
        additional_columns=None
    )


@pytest.fixture
def filter_intent():
    """Create a filter query intent."""
    return QueryIntent(
        definition="Show active products",
        query_type="filter_query",
        source_table="products",
        target_table=None,
        operation="FILTER",
        filters=[{"column": "status", "value": "active", "operator": "="}],
        join_columns=None,
        confidence=0.85,
        reasoning="Filter query detected",
        additional_columns=None
    )


class TestLLMSQLGenerator:
    """Test LLM SQL Generator."""

    def test_initialization(self, mock_kg):
        """Test generator initialization."""
        generator = LLMSQLGenerator(db_type="mysql", kg=mock_kg)
        assert generator.db_type == "mysql"
        assert generator.kg == mock_kg
        assert generator.llm_service is not None

    def test_initialization_without_kg(self):
        """Test generator initialization without KG."""
        generator = LLMSQLGenerator(db_type="postgresql")
        assert generator.db_type == "postgresql"
        assert generator.kg is None

    @patch('kg_builder.services.llm_sql_generator.get_llm_service')
    def test_generate_comparison_query(self, mock_llm_service, comparison_intent, mock_kg):
        """Test generating comparison query with LLM."""
        # Mock LLM service
        mock_service = Mock()
        mock_service.is_enabled.return_value = True

        # Mock LLM response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="""
SELECT DISTINCT s.*
FROM `table_a` s
LEFT JOIN `table_b` t ON s.`id` = t.`id`
WHERE t.`id` IS NULL
        """))]
        mock_service.create_chat_completion.return_value = mock_response
        mock_llm_service.return_value = mock_service

        generator = LLMSQLGenerator(db_type="mysql", kg=mock_kg)
        sql = generator.generate(comparison_intent)

        assert "SELECT" in sql.upper()
        assert "table_a" in sql
        assert "table_b" in sql
        assert "LEFT JOIN" in sql.upper()
        assert "IS NULL" in sql.upper()

    @patch('kg_builder.services.llm_sql_generator.get_llm_service')
    def test_generate_filter_query(self, mock_llm_service, filter_intent, mock_kg):
        """Test generating filter query with LLM."""
        # Mock LLM service
        mock_service = Mock()
        mock_service.is_enabled.return_value = True

        # Mock LLM response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="""
SELECT * FROM `products`
WHERE `status` = 'active'
        """))]
        mock_service.create_chat_completion.return_value = mock_response
        mock_llm_service.return_value = mock_service

        generator = LLMSQLGenerator(db_type="mysql", kg=mock_kg)
        sql = generator.generate(filter_intent)

        assert "SELECT" in sql.upper()
        assert "products" in sql
        assert "WHERE" in sql.upper()
        assert "status" in sql

    def test_clean_sql_response_with_markdown(self):
        """Test cleaning SQL response with markdown."""
        generator = LLMSQLGenerator(db_type="mysql")

        # Test with markdown code block
        sql_with_markdown = """```sql
SELECT * FROM products
WHERE status = 'active'
```"""
        cleaned = generator._clean_sql_response(sql_with_markdown)
        assert "```" not in cleaned
        assert "SELECT" in cleaned

        # Test with explanation
        sql_with_explanation = """SELECT * FROM products
Note: This query filters active products"""
        cleaned = generator._clean_sql_response(sql_with_explanation)
        assert "Note:" not in cleaned
        assert "SELECT" in cleaned

    def test_validate_sql_security(self, comparison_intent):
        """Test SQL validation catches dangerous patterns."""
        generator = LLMSQLGenerator(db_type="mysql")

        # Test DROP TABLE
        with pytest.raises(ValueError, match="Dangerous SQL pattern"):
            generator._validate_sql("DROP TABLE products", comparison_intent)

        # Test DELETE
        with pytest.raises(ValueError, match="Dangerous SQL pattern"):
            generator._validate_sql("DELETE FROM products", comparison_intent)

        # Test TRUNCATE
        with pytest.raises(ValueError, match="Dangerous SQL pattern"):
            generator._validate_sql("TRUNCATE products", comparison_intent)

    def test_validate_sql_missing_tables(self, comparison_intent):
        """Test SQL validation catches missing tables."""
        generator = LLMSQLGenerator(db_type="mysql")

        # Missing source table
        with pytest.raises(ValueError, match="missing source table"):
            generator._validate_sql("SELECT * FROM wrong_table", comparison_intent)

    def test_validate_sql_must_be_select(self, comparison_intent):
        """Test SQL validation requires SELECT."""
        generator = LLMSQLGenerator(db_type="mysql")

        with pytest.raises(ValueError, match="must be a SELECT query"):
            generator._validate_sql("UPDATE products SET status = 'active'", comparison_intent)

    def test_validate_sql_balanced_quotes(self, comparison_intent):
        """Test SQL validation checks balanced quotes."""
        generator = LLMSQLGenerator(db_type="mysql")

        with pytest.raises(ValueError, match="Unbalanced single quotes"):
            generator._validate_sql("SELECT * FROM table_a WHERE name = 'test", comparison_intent)

    def test_validate_sql_balanced_parentheses(self, comparison_intent):
        """Test SQL validation checks balanced parentheses."""
        generator = LLMSQLGenerator(db_type="mysql")

        with pytest.raises(ValueError, match="Unbalanced parentheses"):
            generator._validate_sql("SELECT * FROM table_a WHERE id IN (1, 2", comparison_intent)

    def test_format_kg_context_with_relationships(self, comparison_intent, mock_kg):
        """Test formatting KG context with relationships."""
        generator = LLMSQLGenerator(db_type="mysql", kg=mock_kg)
        context = generator._format_kg_context(comparison_intent)

        # Should contain relationship information
        assert "products" in context.lower() or "orders" in context.lower()

    def test_format_kg_context_without_kg(self, comparison_intent):
        """Test formatting KG context without KG."""
        generator = LLMSQLGenerator(db_type="mysql", kg=None)
        context = generator._format_kg_context(comparison_intent)

        # Should use join_columns from intent
        assert "table_a" in context or "id" in context

    def test_quoting_rules_mysql(self):
        """Test identifier quoting for MySQL."""
        generator = LLMSQLGenerator(db_type="mysql")
        rules = generator._get_quoting_rules()
        assert "backticks" in rules.lower()
        assert "`" in rules

    def test_quoting_rules_sqlserver(self):
        """Test identifier quoting for SQL Server."""
        generator = LLMSQLGenerator(db_type="sqlserver")
        rules = generator._get_quoting_rules()
        assert "square brackets" in rules.lower()
        assert "[" in rules

    def test_quoting_rules_oracle(self):
        """Test identifier quoting for Oracle."""
        generator = LLMSQLGenerator(db_type="oracle")
        rules = generator._get_quoting_rules()
        assert "double quotes" in rules.lower()
        assert '"' in rules

    @patch('kg_builder.services.llm_sql_generator.get_llm_service')
    def test_generate_raises_when_llm_disabled(self, mock_llm_service, comparison_intent):
        """Test that generate raises error when LLM is disabled."""
        mock_service = Mock()
        mock_service.is_enabled.return_value = False
        mock_llm_service.return_value = mock_service

        generator = LLMSQLGenerator(db_type="mysql")

        with pytest.raises(ValueError, match="LLM service not enabled"):
            generator.generate(comparison_intent)

    def test_format_filters(self):
        """Test formatting filters for prompt."""
        generator = LLMSQLGenerator(db_type="mysql")

        filters = [
            {"column": "status", "value": "active", "operator": "="},
            {"column": "price", "value": 100, "operator": ">"}
        ]

        formatted = generator._format_filters(filters)
        assert "status" in formatted
        assert "active" in formatted
        assert "price" in formatted
        assert "100" in formatted

    def test_format_additional_columns(self):
        """Test formatting additional columns for prompt."""
        from kg_builder.services.nl_query_parser import AdditionalColumn

        generator = LLMSQLGenerator(db_type="mysql")

        columns = [
            AdditionalColumn(
                column_name="supplier_name",
                source_table="suppliers",
                alias="supplier",
                confidence=0.9,
                join_path=["products", "suppliers"]
            )
        ]

        formatted = generator._format_additional_columns(columns)
        assert "supplier_name" in formatted
        assert "suppliers" in formatted
        assert "supplier" in formatted


class TestLLMSQLGeneratorIntegration:
    """Integration tests for LLM SQL Generator."""

    @pytest.mark.integration
    @patch('kg_builder.services.llm_sql_generator.get_llm_service')
    def test_end_to_end_comparison_query(self, mock_llm_service, mock_kg):
        """Test end-to-end comparison query generation."""
        # Mock LLM service
        mock_service = Mock()
        mock_service.is_enabled.return_value = True

        # Mock realistic LLM response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="""
SELECT DISTINCT s.*
FROM `table_a` s
LEFT JOIN `table_b` t ON s.`id` = t.`id`
WHERE t.`id` IS NULL
        """))]
        mock_service.create_chat_completion.return_value = mock_response
        mock_llm_service.return_value = mock_service

        generator = LLMSQLGenerator(db_type="mysql", kg=mock_kg)

        intent = QueryIntent(
            definition="Show records in table_a not in table_b",
            query_type="comparison_query",
            source_table="table_a",
            target_table="table_b",
            operation="NOT_IN",
            filters=None,
            join_columns=[("id", "id")],
            confidence=0.9,
            reasoning="Comparison query",
            additional_columns=None
        )

        sql = generator.generate(intent)

        # Validate structure
        assert "SELECT" in sql.upper()
        assert "FROM" in sql.upper()
        assert "LEFT JOIN" in sql.upper()
        assert "WHERE" in sql.upper()
        assert "IS NULL" in sql.upper()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
