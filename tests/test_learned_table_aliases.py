"""
Test suite for LLM-learned table aliases feature.

Tests the complete flow:
1. Extract table aliases during KG generation
2. Store aliases in KG metadata
3. Load aliases from storage
4. Use aliases in query parsing
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from kg_builder.models import KnowledgeGraph, GraphNode, GraphRelationship, DatabaseSchema, TableSchema, ColumnSchema
from kg_builder.services.table_name_mapper import TableNameMapper, get_table_name_mapper
from kg_builder.services.nl_query_parser import NLQueryParser
from kg_builder.services.schema_parser import SchemaParser


class TestTableAliasExtraction:
    """Test table alias extraction from LLM."""

    def test_llm_service_extract_table_aliases_method_exists(self):
        """Test LLM service has extract_table_aliases method."""
        from kg_builder.services.llm_service import LLMService

        # Check method exists
        assert hasattr(LLMService, 'extract_table_aliases')

        # Check method signature
        import inspect
        sig = inspect.signature(LLMService.extract_table_aliases)
        params = list(sig.parameters.keys())
        assert 'table_name' in params
        assert 'table_description' in params
        assert 'columns' in params


class TestTableNameMapperWithLearnedAliases:
    """Test TableNameMapper with learned aliases."""

    def test_mapper_initialization_with_learned_aliases(self):
        """Test mapper can be initialized with learned aliases."""
        learned_aliases = {
            "brz_lnd_RBP_GPU": ["RBP", "RBP GPU"],
            "brz_lnd_OPS_EXCEL_GPU": ["OPS", "OPS Excel"]
        }
        
        mapper = TableNameMapper(schemas_info={}, learned_aliases=learned_aliases)
        
        assert mapper.learned_aliases == learned_aliases
        assert len(mapper.table_aliases) > 0

    def test_mapper_resolves_learned_aliases(self):
        """Test mapper can resolve learned aliases."""
        learned_aliases = {
            "brz_lnd_RBP_GPU": ["RBP", "RBP GPU", "GPU"],
            "brz_lnd_OPS_EXCEL_GPU": ["OPS", "OPS Excel"]
        }
        
        mapper = TableNameMapper(schemas_info={}, learned_aliases=learned_aliases)
        
        # Test learned aliases
        assert mapper.resolve_table_name("RBP") == "brz_lnd_RBP_GPU"
        assert mapper.resolve_table_name("rbp") == "brz_lnd_RBP_GPU"
        assert mapper.resolve_table_name("RBP GPU") == "brz_lnd_RBP_GPU"
        assert mapper.resolve_table_name("OPS") == "brz_lnd_OPS_EXCEL_GPU"
        assert mapper.resolve_table_name("OPS Excel") == "brz_lnd_OPS_EXCEL_GPU"

    def test_learned_aliases_override_hardcoded(self):
        """Test that learned aliases take priority over hardcoded ones."""
        learned_aliases = {
            "brz_lnd_RBP_GPU": ["RBP", "RBP_CUSTOM"]
        }
        
        mapper = TableNameMapper(schemas_info={}, learned_aliases=learned_aliases)
        
        # Learned alias should work
        assert mapper.resolve_table_name("RBP_CUSTOM") == "brz_lnd_RBP_GPU"


class TestKnowledgeGraphWithAliases:
    """Test KnowledgeGraph model with table_aliases field."""

    def test_kg_model_has_table_aliases_field(self):
        """Test KG model includes table_aliases field."""
        kg = KnowledgeGraph(
            name="test_kg",
            nodes=[],
            relationships=[],
            schema_file="test_schema",
            table_aliases={
                "brz_lnd_RBP_GPU": ["RBP", "RBP GPU"],
                "brz_lnd_OPS_EXCEL_GPU": ["OPS", "OPS Excel"]
            }
        )
        
        assert kg.table_aliases is not None
        assert len(kg.table_aliases) == 2
        assert "brz_lnd_RBP_GPU" in kg.table_aliases

    def test_kg_model_table_aliases_default_empty(self):
        """Test KG model table_aliases defaults to empty dict."""
        kg = KnowledgeGraph(
            name="test_kg",
            nodes=[],
            relationships=[],
            schema_file="test_schema"
        )
        
        assert kg.table_aliases == {}


class TestNLQueryParserWithLearnedAliases:
    """Test NLQueryParser uses learned aliases."""

    def test_parser_uses_kg_learned_aliases(self):
        """Test parser initializes with KG learned aliases."""
        kg = KnowledgeGraph(
            name="test_kg",
            nodes=[],
            relationships=[],
            schema_file="test_schema",
            table_aliases={
                "brz_lnd_RBP_GPU": ["RBP", "RBP GPU"],
                "brz_lnd_OPS_EXCEL_GPU": ["OPS", "OPS Excel"]
            }
        )
        
        parser = NLQueryParser(kg=kg, schemas_info={})
        
        # Parser should have learned aliases in its mapper
        assert parser.table_mapper.learned_aliases == kg.table_aliases

    def test_parser_resolves_with_learned_aliases(self):
        """Test parser can resolve table names using learned aliases."""
        kg = KnowledgeGraph(
            name="test_kg",
            nodes=[],
            relationships=[],
            schema_file="test_schema",
            table_aliases={
                "brz_lnd_RBP_GPU": ["RBP", "RBP GPU"],
                "brz_lnd_OPS_EXCEL_GPU": ["OPS", "OPS Excel"]
            }
        )
        
        parser = NLQueryParser(kg=kg, schemas_info={})
        
        # Test resolution
        resolved = parser.table_mapper.resolve_table_name("RBP")
        assert resolved == "brz_lnd_RBP_GPU"


class TestSchemaParserAliasExtraction:
    """Test SchemaParser extracts aliases during KG generation."""

    def test_schema_parser_has_extract_aliases_method(self):
        """Test SchemaParser has _extract_table_aliases method."""
        # Check method exists
        assert hasattr(SchemaParser, '_extract_table_aliases')

        # Check method signature
        import inspect
        sig = inspect.signature(SchemaParser._extract_table_aliases)
        params = list(sig.parameters.keys())
        assert 'schemas' in params

    def test_schema_parser_extract_aliases_returns_dict(self):
        """Test SchemaParser._extract_table_aliases returns dict."""
        # Create mock schemas
        schemas = {
            "test_schema": DatabaseSchema(
                database="test_db",
                tables={
                    "brz_lnd_RBP_GPU": TableSchema(
                        table_name="brz_lnd_RBP_GPU",
                        columns=[
                            ColumnSchema(name="Material", type="VARCHAR", nullable=False),
                            ColumnSchema(name="Quantity", type="INT", nullable=True)
                        ]
                    )
                },
                total_tables=1
            )
        }

        # Call the method (will return empty dict if LLM disabled)
        aliases = SchemaParser._extract_table_aliases(schemas)

        # Should return a dict
        assert isinstance(aliases, dict)


class TestAliasStorageAndRetrieval:
    """Test aliases are stored and retrieved correctly."""

    def test_kg_serialization_includes_aliases(self):
        """Test KG can be serialized with aliases."""
        kg = KnowledgeGraph(
            name="test_kg",
            nodes=[],
            relationships=[],
            schema_file="test_schema",
            table_aliases={
                "brz_lnd_RBP_GPU": ["RBP", "RBP GPU"]
            }
        )
        
        # Serialize to dict
        kg_dict = kg.model_dump()
        
        assert "table_aliases" in kg_dict
        assert kg_dict["table_aliases"]["brz_lnd_RBP_GPU"] == ["RBP", "RBP GPU"]

    def test_kg_deserialization_includes_aliases(self):
        """Test KG can be deserialized with aliases."""
        kg_dict = {
            "name": "test_kg",
            "nodes": [],
            "relationships": [],
            "schema_file": "test_schema",
            "table_aliases": {
                "brz_lnd_RBP_GPU": ["RBP", "RBP GPU"]
            }
        }
        
        kg = KnowledgeGraph(**kg_dict)
        
        assert kg.table_aliases["brz_lnd_RBP_GPU"] == ["RBP", "RBP GPU"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

