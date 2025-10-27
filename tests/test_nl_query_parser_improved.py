"""
Tests for improved NL Query Parser with smart table name extraction.

Tests that the parser correctly:
1. Excludes common English words from table name extraction
2. Identifies correct table names from business terms
3. Extracts filters properly
4. Handles various query formats
"""

import pytest
from kg_builder.services.nl_query_parser import NLQueryParser, QueryIntent
from kg_builder.services.nl_query_classifier import DefinitionType
from kg_builder.models import DatabaseSchema, TableSchema, ColumnSchema


@pytest.fixture
def sample_schemas():
    """Create sample schemas for testing."""
    # Create columns
    rbp_columns = [
        ColumnSchema(name="Material", type="VARCHAR(18)", nullable=True),
        ColumnSchema(name="Description", type="VARCHAR(100)", nullable=True),
        ColumnSchema(name="Status", type="VARCHAR(20)", nullable=True),
    ]
    
    ops_columns = [
        ColumnSchema(name="PLANNING_SKU", type="VARCHAR(18)", nullable=True),
        ColumnSchema(name="SKU_Description", type="VARCHAR(100)", nullable=True),
        ColumnSchema(name="Status", type="VARCHAR(20)", nullable=True),
    ]
    
    # Create tables
    rbp_table = TableSchema(
        table_name="brz_lnd_RBP_GPU",
        columns=rbp_columns
    )
    
    ops_table = TableSchema(
        table_name="brz_lnd_OPS_EXCEL_GPU",
        columns=ops_columns
    )
    
    # Create schema
    schema = DatabaseSchema(
        database="test_db",
        tables={
            "brz_lnd_RBP_GPU": rbp_table,
            "brz_lnd_OPS_EXCEL_GPU": ops_table,
        },
        total_tables=2
    )
    
    return {"newdqschema": schema}


class TestNLQueryParserImproved:
    """Test improved NL query parser."""

    def test_exclude_show_from_table_names(self, sample_schemas):
        """Test that 'show' is not treated as a table name."""
        parser = NLQueryParser(schemas_info=sample_schemas)
        
        definition = "Show me all the products in RBP GPU which are not in OPS Excel"
        intent = parser._parse_rule_based(
            definition,
            DefinitionType.DATA_QUERY,
            "NOT_IN"
        )
        
        # Should NOT have "show" as source_table
        assert intent.source_table != "show"
        assert intent.source_table is not None
        print(f"✓ 'show' correctly excluded. source_table: {intent.source_table}")

    def test_extract_rbp_and_ops_tables(self, sample_schemas):
        """Test extraction of RBP and OPS Excel tables."""
        parser = NLQueryParser(schemas_info=sample_schemas)
        
        definition = "Show me all the products in RBP GPU which are not in OPS Excel"
        intent = parser._parse_rule_based(
            definition,
            DefinitionType.COMPARISON_QUERY,
            "NOT_IN"
        )
        
        # Should extract both tables
        assert intent.source_table is not None
        assert intent.target_table is not None
        print(f"✓ Extracted tables: {intent.source_table} and {intent.target_table}")

    def test_exclude_active_from_table_names(self, sample_schemas):
        """Test that 'active' is not treated as a table name."""
        parser = NLQueryParser(schemas_info=sample_schemas)
        
        definition = "Show me all active products in RBP GPU"
        intent = parser._parse_rule_based(
            definition,
            DefinitionType.FILTER_QUERY,
            "IN"
        )
        
        # Should NOT have "active" as table name
        assert intent.source_table != "active"
        # Should have "active" in filters
        assert any(f.get("value") == "active" for f in intent.filters)
        print(f"✓ 'active' correctly excluded from tables and added to filters")

    def test_complex_query_with_multiple_filters(self, sample_schemas):
        """Test parsing complex query with multiple conditions."""
        parser = NLQueryParser(schemas_info=sample_schemas)
        
        definition = "Show me all active products in RBP GPU which are in active OPS Excel"
        intent = parser._parse_rule_based(
            definition,
            DefinitionType.COMPARISON_QUERY,
            "IN"
        )
        
        # Should have both tables
        assert intent.source_table is not None
        assert intent.target_table is not None
        # Should have active filter
        assert any(f.get("value") == "active" for f in intent.filters)
        print(f"✓ Complex query parsed correctly")

    def test_exclude_which_from_table_names(self, sample_schemas):
        """Test that 'which' is not treated as a table name."""
        parser = NLQueryParser(schemas_info=sample_schemas)
        
        definition = "Show me products in RBP which are not in OPS Excel"
        intent = parser._parse_rule_based(
            definition,
            DefinitionType.COMPARISON_QUERY,
            "NOT_IN"
        )
        
        # Should NOT have "which" as table name
        assert intent.source_table != "which"
        print(f"✓ 'which' correctly excluded from table names")

    def test_exclude_are_from_table_names(self, sample_schemas):
        """Test that 'are' is not treated as a table name."""
        parser = NLQueryParser(schemas_info=sample_schemas)
        
        definition = "Show me products in RBP which are in OPS Excel"
        intent = parser._parse_rule_based(
            definition,
            DefinitionType.COMPARISON_QUERY,
            "IN"
        )
        
        # Should NOT have "are" as table name
        assert intent.source_table != "are"
        print(f"✓ 'are' correctly excluded from table names")

    def test_prompt_includes_table_list(self, sample_schemas):
        """Test that the LLM prompt includes the list of valid tables."""
        parser = NLQueryParser(schemas_info=sample_schemas)
        
        definition = "Show me products in RBP which are not in OPS Excel"
        prompt = parser._build_parsing_prompt(
            definition,
            DefinitionType.COMPARISON_QUERY,
            "NOT_IN"
        )
        
        # Prompt should include table names
        assert "brz_lnd_RBP_GPU" in prompt
        assert "brz_lnd_OPS_EXCEL_GPU" in prompt
        # Prompt should include common words to exclude
        assert "show" in prompt.lower()
        assert "which" in prompt.lower()
        print(f"✓ LLM prompt includes table list and common words to exclude")

    def test_prompt_includes_examples(self, sample_schemas):
        """Test that the LLM prompt includes helpful examples."""
        parser = NLQueryParser(schemas_info=sample_schemas)
        
        definition = "Show me products in RBP which are not in OPS Excel"
        prompt = parser._build_parsing_prompt(
            definition,
            DefinitionType.COMPARISON_QUERY,
            "NOT_IN"
        )
        
        # Prompt should include examples
        assert "EXAMPLES:" in prompt
        assert "NOT_IN" in prompt
        assert "operation" in prompt.lower()
        print(f"✓ LLM prompt includes helpful examples")

    def test_rule_based_excludes_common_words(self, sample_schemas):
        """Test that rule-based parser excludes common words."""
        parser = NLQueryParser(schemas_info=sample_schemas)
        
        # Test various queries with common words
        test_cases = [
            ("Show me all products in RBP", "show", "all"),
            ("Find products in RBP which are in OPS Excel", "find", "which"),
            ("Display active products in RBP", "display", "active"),
            ("Get products in RBP not in OPS Excel", "get", "not"),
        ]
        
        for definition, word1, word2 in test_cases:
            intent = parser._parse_rule_based(
                definition,
                DefinitionType.DATA_QUERY,
                "IN"
            )
            # Neither common word should be a table name
            assert intent.source_table != word1.lower()
            assert intent.source_table != word2.lower()
        
        print(f"✓ Rule-based parser correctly excludes common words")


class TestNLQueryParserRealWorldScenarios:
    """Test real-world query scenarios."""

    def test_scenario_rbp_not_in_ops(self, sample_schemas):
        """Test: Show me all products in RBP which are not in OPS Excel"""
        parser = NLQueryParser(schemas_info=sample_schemas)
        
        definition = "Show me all the products in RBP GPU which are not in OPS Excel"
        intent = parser._parse_rule_based(
            definition,
            DefinitionType.COMPARISON_QUERY,
            "NOT_IN"
        )
        
        assert intent.source_table is not None
        assert intent.target_table is not None
        assert intent.operation == "NOT_IN"
        print(f"✓ Scenario 1: {definition}")
        print(f"  → source: {intent.source_table}, target: {intent.target_table}, op: {intent.operation}")

    def test_scenario_active_products_in_rbp(self, sample_schemas):
        """Test: Show me all active products in RBP GPU"""
        parser = NLQueryParser(schemas_info=sample_schemas)
        
        definition = "Show me all active products in RBP GPU"
        intent = parser._parse_rule_based(
            definition,
            DefinitionType.FILTER_QUERY,
            "IN"
        )
        
        assert intent.source_table is not None
        assert any(f.get("value") == "active" for f in intent.filters)
        print(f"✓ Scenario 2: {definition}")
        print(f"  → source: {intent.source_table}, filters: {intent.filters}")

    def test_scenario_products_in_both_tables(self, sample_schemas):
        """Test: Show me products in RBP which are in active OPS Excel"""
        parser = NLQueryParser(schemas_info=sample_schemas)
        
        definition = "Show me all products in RBP GPU which are in active OPS Excel"
        intent = parser._parse_rule_based(
            definition,
            DefinitionType.COMPARISON_QUERY,
            "IN"
        )
        
        assert intent.source_table is not None
        assert intent.target_table is not None
        assert intent.operation == "IN"
        assert any(f.get("value") == "active" for f in intent.filters)
        print(f"✓ Scenario 3: {definition}")
        print(f"  → source: {intent.source_table}, target: {intent.target_table}, op: {intent.operation}, filters: {intent.filters}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

