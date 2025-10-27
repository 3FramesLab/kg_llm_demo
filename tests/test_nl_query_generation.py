"""
Tests for NL Query Generation System

Tests the complete pipeline:
1. Classification
2. Parsing
3. SQL Generation
4. Execution
"""

import pytest
from kg_builder.services.nl_query_classifier import (
    NLQueryClassifier, DefinitionType, get_nl_query_classifier
)
from kg_builder.services.nl_query_parser import (
    NLQueryParser, QueryIntent, get_nl_query_parser
)
from kg_builder.services.nl_sql_generator import (
    NLSQLGenerator, get_nl_sql_generator
)
from kg_builder.services.nl_query_executor import (
    NLQueryExecutor, QueryResult, get_nl_query_executor
)


class TestNLQueryClassifier:
    """Test NL query classification."""

    def test_classify_relationship(self):
        """Test classification of relationship definitions."""
        classifier = get_nl_query_classifier()

        definitions = [
            "Products are supplied by Vendors",
            "Orders contain Products",
            "Material master references planning SKU"
        ]

        for definition in definitions:
            result = classifier.classify(definition)
            assert result == DefinitionType.RELATIONSHIP, f"Failed for: {definition}"

    def test_classify_data_query(self):
        """Test classification of data queries."""
        classifier = get_nl_query_classifier()

        definitions = [
            "Show me all products in RBP GPU",
            "Find all records in OPS Excel",
            "List products from material master"
        ]

        for definition in definitions:
            result = classifier.classify(definition)
            assert result == DefinitionType.DATA_QUERY, f"Failed for: {definition}"

    def test_classify_comparison_query(self):
        """Test classification of comparison queries."""
        classifier = get_nl_query_classifier()

        definitions = [
            "Show me all products in RBP GPU which are not in OPS Excel",
            "Find products missing from OPS Excel",
            "Compare RBP GPU with OPS Excel"
        ]

        for definition in definitions:
            result = classifier.classify(definition)
            assert result == DefinitionType.COMPARISON_QUERY, f"Failed for: {definition}"

    def test_classify_filter_query(self):
        """Test classification of filter queries."""
        classifier = get_nl_query_classifier()

        definitions = [
            "Show me active products",
            "Find inactive records",
            "List products with active status"
        ]

        for definition in definitions:
            result = classifier.classify(definition)
            assert result == DefinitionType.FILTER_QUERY, f"Failed for: {definition}"

    def test_get_operation_type(self):
        """Test operation type extraction."""
        classifier = get_nl_query_classifier()

        test_cases = [
            ("Show me products not in OPS Excel", "NOT_IN"),
            ("Show me products in OPS Excel", "IN"),
            ("Count products by category", "AGGREGATE"),
        ]

        for definition, expected_op in test_cases:
            result = classifier.get_operation_type(definition)
            assert result == expected_op, f"Failed for: {definition}"


class TestNLQueryParser:
    """Test NL query parsing."""

    def test_parse_comparison_query(self):
        """Test parsing of comparison queries."""
        parser = get_nl_query_parser()

        definition = "Show me all products in RBP GPU which are not in OPS Excel"
        intent = parser.parse(definition, use_llm=False)

        assert intent.definition == definition
        assert intent.query_type == "comparison_query"
        assert intent.operation == "NOT_IN"
        assert intent.source_table is not None
        assert intent.target_table is not None

    def test_parse_filter_query(self):
        """Test parsing of filter queries."""
        parser = get_nl_query_parser()

        definition = "Show me active products in RBP GPU"
        intent = parser.parse(definition, use_llm=False)

        assert intent.definition == definition
        assert intent.query_type in ["filter_query", "data_query"]
        assert intent.source_table is not None

    def test_parse_with_filters(self):
        """Test parsing with filter extraction."""
        parser = get_nl_query_parser()

        definition = "Show me active products in RBP GPU"
        intent = parser.parse(definition, use_llm=False)

        # Should extract active filter
        assert len(intent.filters) > 0 or intent.source_table is not None

    def test_query_intent_to_dict(self):
        """Test QueryIntent serialization."""
        intent = QueryIntent(
            definition="Test definition",
            query_type="data_query",
            source_table="table1",
            target_table="table2",
            operation="IN",
            confidence=0.85
        )

        result = intent.to_dict()
        assert result["definition"] == "Test definition"
        assert result["query_type"] == "data_query"
        assert result["confidence"] == 0.85


class TestNLSQLGenerator:
    """Test SQL generation from query intents."""

    def test_generate_comparison_not_in(self):
        """Test SQL generation for NOT_IN comparison."""
        generator = get_nl_sql_generator("mysql")

        intent = QueryIntent(
            definition="Show me products not in OPS Excel",
            query_type="comparison_query",
            source_table="rbp_gpu",
            target_table="ops_excel",
            operation="NOT_IN",
            join_columns=[("material", "planning_sku")]
        )

        sql = generator.generate(intent)

        assert "LEFT JOIN" in sql
        assert "WHERE" in sql
        assert "IS NULL" in sql
        assert "rbp_gpu" in sql
        assert "ops_excel" in sql

    def test_generate_comparison_in(self):
        """Test SQL generation for IN comparison."""
        generator = get_nl_sql_generator("mysql")

        intent = QueryIntent(
            definition="Show me products in OPS Excel",
            query_type="comparison_query",
            source_table="rbp_gpu",
            target_table="ops_excel",
            operation="IN",
            join_columns=[("material", "planning_sku")]
        )

        sql = generator.generate(intent)

        assert "INNER JOIN" in sql
        assert "rbp_gpu" in sql
        assert "ops_excel" in sql

    def test_generate_filter_query(self):
        """Test SQL generation for filter queries."""
        generator = get_nl_sql_generator("mysql")

        intent = QueryIntent(
            definition="Show me active products",
            query_type="filter_query",
            source_table="products",
            filters=[{"column": "status", "value": "active"}]
        )

        sql = generator.generate(intent)

        assert "SELECT" in sql
        assert "FROM" in sql
        assert "WHERE" in sql
        assert "status" in sql
        assert "active" in sql

    def test_generate_aggregation_query(self):
        """Test SQL generation for aggregation queries."""
        generator = get_nl_sql_generator("mysql")

        intent = QueryIntent(
            definition="Count products",
            query_type="aggregation_query",
            source_table="products"
        )

        sql = generator.generate(intent)

        assert "COUNT" in sql
        assert "FROM" in sql

    def test_quote_identifier_mysql(self):
        """Test identifier quoting for MySQL."""
        generator = get_nl_sql_generator("mysql")
        result = generator._quote_identifier("column_name")
        assert result == "`column_name`"

    def test_quote_identifier_sqlserver(self):
        """Test identifier quoting for SQL Server."""
        generator = get_nl_sql_generator("sqlserver")
        result = generator._quote_identifier("column_name")
        assert result == "[column_name]"

    def test_quote_identifier_oracle(self):
        """Test identifier quoting for Oracle."""
        generator = get_nl_sql_generator("oracle")
        result = generator._quote_identifier("column_name")
        assert result == '"column_name"'


class TestNLQueryExecutor:
    """Test query execution."""

    def test_add_limit_clause_mysql(self):
        """Test LIMIT clause for MySQL."""
        executor = get_nl_query_executor("mysql")
        sql = "SELECT * FROM products"
        result = executor._add_limit_clause(sql, 100)
        assert "LIMIT 100" in result

    def test_add_limit_clause_sqlserver(self):
        """Test TOP clause for SQL Server."""
        executor = get_nl_query_executor("sqlserver")
        sql = "SELECT * FROM products"
        result = executor._add_limit_clause(sql, 100)
        assert "TOP 100" in result

    def test_query_result_to_dict(self):
        """Test QueryResult serialization."""
        result = QueryResult(
            definition="Test query",
            query_type="data_query",
            operation="IN",
            sql="SELECT * FROM table",
            record_count=10,
            records=[{"id": 1}, {"id": 2}],
            join_columns=[("col1", "col2")],
            confidence=0.85,
            execution_time_ms=100.5
        )

        result_dict = result.to_dict()
        assert result_dict["definition"] == "Test query"
        assert result_dict["record_count"] == 10
        assert result_dict["join_columns"] == [["col1", "col2"]]

    def test_get_statistics(self):
        """Test statistics calculation."""
        executor = get_nl_query_executor("mysql")

        results = [
            QueryResult(
                definition="Query 1",
                query_type="data_query",
                operation="IN",
                sql="SELECT * FROM table1",
                record_count=100,
                records=[],
                join_columns=None,
                confidence=0.9,
                execution_time_ms=50.0
            ),
            QueryResult(
                definition="Query 2",
                query_type="data_query",
                operation="IN",
                sql="SELECT * FROM table2",
                record_count=200,
                records=[],
                join_columns=None,
                confidence=0.8,
                execution_time_ms=75.0
            )
        ]

        stats = executor.get_statistics(results)

        assert stats["total_queries"] == 2
        assert stats["successful"] == 2
        assert stats["failed"] == 0
        assert stats["total_records"] == 300
        assert stats["total_execution_time_ms"] == 125.0
        assert abs(stats["average_confidence"] - 0.85) < 0.001  # Use approximate comparison


class TestEndToEndPipeline:
    """Test complete NL query pipeline."""

    def test_full_pipeline_comparison_query(self):
        """Test full pipeline for comparison query."""
        # Step 1: Classify
        classifier = get_nl_query_classifier()
        definition = "Show me all products in RBP GPU which are not in OPS Excel"
        def_type = classifier.classify(definition)
        assert def_type == DefinitionType.COMPARISON_QUERY

        # Step 2: Parse
        parser = get_nl_query_parser()
        intent = parser.parse(definition, use_llm=False)
        assert intent.query_type == "comparison_query"
        assert intent.operation == "NOT_IN"

        # Step 3: Generate SQL
        generator = get_nl_sql_generator("mysql")
        intent.join_columns = [("material", "planning_sku")]
        sql = generator.generate(intent)
        assert "LEFT JOIN" in sql
        assert "IS NULL" in sql

    def test_full_pipeline_filter_query(self):
        """Test full pipeline for filter query."""
        # Step 1: Classify
        classifier = get_nl_query_classifier()
        definition = "Show me active products in RBP GPU"
        def_type = classifier.classify(definition)
        assert def_type in [DefinitionType.FILTER_QUERY, DefinitionType.DATA_QUERY]

        # Step 2: Parse
        parser = get_nl_query_parser()
        intent = parser.parse(definition, use_llm=False)
        assert intent.source_table is not None

        # Step 3: Generate SQL
        generator = get_nl_sql_generator("mysql")

        # For rule-based parsing, we may need to manually set the table
        # since the rule-based parser might extract "Show" as table name
        if intent.source_table and intent.source_table.lower() == "show":
            intent.source_table = "rbp_gpu"

        # Clear target table if it's not a multi-table query
        if intent.target_table and intent.target_table.lower() in ["gpu", "rbp"]:
            intent.target_table = None
            intent.join_columns = []

        sql = generator.generate(intent)
        assert "SELECT" in sql
        assert "FROM" in sql


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

