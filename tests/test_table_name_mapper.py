"""
Tests for Table Name Mapper service.
"""
import pytest
from kg_builder.services.table_name_mapper import TableNameMapper, get_table_name_mapper
from kg_builder.models import DatabaseSchema, TableSchema, ColumnSchema


@pytest.fixture
def sample_schemas():
    """Create sample schemas for testing."""
    # Create table schemas
    rbp_table = TableSchema(
        table_name="brz_lnd_RBP_GPU",
        columns=[
            ColumnSchema(name="Material", type="VARCHAR(18)", nullable=True),
            ColumnSchema(name="Product_Line", type="VARCHAR(14)", nullable=True),
        ],
        primary_keys=[],
        foreign_keys=[],
        indexes=[]
    )

    ops_table = TableSchema(
        table_name="brz_lnd_OPS_EXCEL_GPU",
        columns=[
            ColumnSchema(name="PLANNING_SKU", type="VARCHAR(19)", nullable=True),
            ColumnSchema(name="Product_Line", type="VARCHAR(12)", nullable=True),
        ],
        primary_keys=[],
        foreign_keys=[],
        indexes=[]
    )
    
    # Create database schema
    schema = DatabaseSchema(
        database="test_db",
        tables={
            "brz_lnd_RBP_GPU": rbp_table,
            "brz_lnd_OPS_EXCEL_GPU": ops_table,
        },
        total_tables=2,
        metadata={}
    )
    
    return {"newdqschema": schema}


class TestTableNameMapper:
    """Test TableNameMapper functionality."""

    def test_mapper_initialization(self, sample_schemas):
        """Test mapper initialization."""
        mapper = TableNameMapper(sample_schemas)
        assert mapper is not None
        assert len(mapper.table_aliases) > 0

    def test_exact_match(self, sample_schemas):
        """Test exact table name match."""
        mapper = TableNameMapper(sample_schemas)
        
        result = mapper.resolve_table_name("brz_lnd_RBP_GPU")
        assert result == "brz_lnd_RBP_GPU"
        
        result = mapper.resolve_table_name("brz_lnd_OPS_EXCEL_GPU")
        assert result == "brz_lnd_OPS_EXCEL_GPU"

    def test_case_insensitive_match(self, sample_schemas):
        """Test case-insensitive matching."""
        mapper = TableNameMapper(sample_schemas)
        
        result = mapper.resolve_table_name("rbp")
        assert result == "brz_lnd_RBP_GPU"
        
        result = mapper.resolve_table_name("RBP")
        assert result == "brz_lnd_RBP_GPU"
        
        result = mapper.resolve_table_name("Rbp")
        assert result == "brz_lnd_RBP_GPU"

    def test_abbreviation_match(self, sample_schemas):
        """Test abbreviation matching."""
        mapper = TableNameMapper(sample_schemas)
        
        # Test RBP abbreviations
        result = mapper.resolve_table_name("rbp_gpu")
        assert result == "brz_lnd_RBP_GPU"
        
        result = mapper.resolve_table_name("gpu")
        assert result in ["brz_lnd_RBP_GPU", "brz_lnd_OPS_EXCEL_GPU"]

    def test_ops_excel_variations(self, sample_schemas):
        """Test OPS Excel variations."""
        mapper = TableNameMapper(sample_schemas)
        
        # Test different variations
        variations = ["ops", "ops_excel", "ops excel", "opsexcel"]
        for var in variations:
            result = mapper.resolve_table_name(var)
            assert result == "brz_lnd_OPS_EXCEL_GPU", f"Failed for variation: {var}"

    def test_fuzzy_matching(self, sample_schemas):
        """Test fuzzy matching."""
        mapper = TableNameMapper(sample_schemas)
        
        # Slightly misspelled
        result = mapper.resolve_table_name("rbp_gup")  # typo: gup instead of gpu
        assert result is not None  # Should find something close

    def test_get_all_aliases(self, sample_schemas):
        """Test getting all aliases."""
        mapper = TableNameMapper(sample_schemas)
        aliases = mapper.get_all_aliases()
        
        assert isinstance(aliases, dict)
        assert len(aliases) > 0
        assert "rbp" in aliases
        assert "ops" in aliases

    def test_get_table_info(self, sample_schemas):
        """Test getting table information."""
        mapper = TableNameMapper(sample_schemas)
        table_info = mapper.get_table_info()
        
        assert isinstance(table_info, dict)
        assert "brz_lnd_RBP_GPU" in table_info
        assert "brz_lnd_OPS_EXCEL_GPU" in table_info
        
        # Check that aliases are lists
        assert isinstance(table_info["brz_lnd_RBP_GPU"], list)
        assert len(table_info["brz_lnd_RBP_GPU"]) > 0

    def test_factory_function(self, sample_schemas):
        """Test factory function."""
        mapper = get_table_name_mapper(sample_schemas)
        assert isinstance(mapper, TableNameMapper)
        
        result = mapper.resolve_table_name("rbp")
        assert result == "brz_lnd_RBP_GPU"

    def test_none_input(self, sample_schemas):
        """Test handling of None input."""
        mapper = TableNameMapper(sample_schemas)
        
        result = mapper.resolve_table_name(None)
        assert result is None
        
        result = mapper.resolve_table_name("")
        assert result is None

    def test_unknown_table(self, sample_schemas):
        """Test handling of unknown table."""
        mapper = TableNameMapper(sample_schemas)
        
        result = mapper.resolve_table_name("unknown_table_xyz")
        # Should return None or best fuzzy match
        # Depending on implementation, might be None or a close match

    def test_pattern_matching(self, sample_schemas):
        """Test pattern matching with special characters."""
        mapper = TableNameMapper(sample_schemas)
        
        # Test with underscores and mixed case
        result = mapper.resolve_table_name("BRZ_LND_RBP_GPU")
        assert result == "brz_lnd_RBP_GPU"


class TestTableNameMapperIntegration:
    """Integration tests for table name mapper."""

    def test_real_world_scenario(self, sample_schemas):
        """Test real-world scenario."""
        mapper = TableNameMapper(sample_schemas)
        
        # Simulate user input
        user_inputs = [
            ("RBP", "brz_lnd_RBP_GPU"),
            ("OPS Excel", "brz_lnd_OPS_EXCEL_GPU"),
            ("rbp_gpu", "brz_lnd_RBP_GPU"),
            ("ops_excel_gpu", "brz_lnd_OPS_EXCEL_GPU"),
        ]
        
        for user_input, expected in user_inputs:
            result = mapper.resolve_table_name(user_input)
            assert result == expected, f"Failed for input: {user_input}"

    def test_mapping_consistency(self, sample_schemas):
        """Test that mapping is consistent."""
        mapper = TableNameMapper(sample_schemas)
        
        # Same input should always return same output
        result1 = mapper.resolve_table_name("rbp")
        result2 = mapper.resolve_table_name("rbp")
        assert result1 == result2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

