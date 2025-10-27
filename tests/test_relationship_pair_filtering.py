"""
Tests for relationship pair filtering to exclude unwanted fields.

Tests that relationship pairs with excluded fields (Product_Line, Business_Unit, etc.)
are properly filtered out during KG creation.
"""

import pytest
from kg_builder.services.schema_parser import (
    filter_relationship_pairs,
    is_excluded_field,
    DEFAULT_EXCLUDED_FIELDS
)


class TestExcludedFieldDetection:
    """Test detection of excluded fields."""

    def test_product_line_variations(self):
        """Test that all Product_Line variations are excluded."""
        assert is_excluded_field("Product_Line")
        assert is_excluded_field("product_line")
        assert is_excluded_field("PRODUCT_LINE")
        assert is_excluded_field("Product Line")
        print("✓ All Product_Line variations correctly excluded")

    def test_business_unit_variations(self):
        """Test that all Business_Unit variations are excluded."""
        assert is_excluded_field("Business_Unit")
        assert is_excluded_field("business_unit")
        assert is_excluded_field("BUSINESS_UNIT")
        assert is_excluded_field("Business Unit")
        assert is_excluded_field("[Business Unit]")
        print("✓ All Business_Unit variations correctly excluded")

    def test_product_type_variations(self):
        """Test that all Product Type variations are excluded."""
        assert is_excluded_field("[Product Type]")
        assert is_excluded_field("Product Type")
        assert is_excluded_field("product_type")
        assert is_excluded_field("PRODUCT_TYPE")
        print("✓ All Product Type variations correctly excluded")

    def test_valid_fields_not_excluded(self):
        """Test that valid fields are NOT excluded."""
        assert not is_excluded_field("MATERIAL")
        assert not is_excluded_field("PLANNING_SKU")
        assert not is_excluded_field("Material")
        assert not is_excluded_field("SKU")
        print("✓ Valid fields correctly NOT excluded")


class TestRelationshipPairFiltering:
    """Test filtering of relationship pairs."""

    def test_filter_pair_with_excluded_source_column(self):
        """Test filtering pair with excluded source column."""
        pairs = [
            {
                "source_table": "hana_material_master",
                "source_column": "Product_Line",  # EXCLUDED
                "target_table": "brz_lnd_OPS_EXCEL_GPU",
                "target_column": "PLANNING_SKU"
            }
        ]
        
        filtered = filter_relationship_pairs(pairs)
        assert len(filtered) == 0
        print("✓ Pair with excluded source column correctly filtered")

    def test_filter_pair_with_excluded_target_column(self):
        """Test filtering pair with excluded target column."""
        pairs = [
            {
                "source_table": "hana_material_master",
                "source_column": "MATERIAL",
                "target_table": "brz_lnd_OPS_EXCEL_GPU",
                "target_column": "Business_Unit"  # EXCLUDED
            }
        ]
        
        filtered = filter_relationship_pairs(pairs)
        assert len(filtered) == 0
        print("✓ Pair with excluded target column correctly filtered")

    def test_keep_pair_with_valid_columns(self):
        """Test that pairs with valid columns are kept."""
        pairs = [
            {
                "source_table": "hana_material_master",
                "source_column": "MATERIAL",
                "target_table": "brz_lnd_OPS_EXCEL_GPU",
                "target_column": "PLANNING_SKU"
            }
        ]
        
        filtered = filter_relationship_pairs(pairs)
        assert len(filtered) == 1
        assert filtered[0]["source_column"] == "MATERIAL"
        print("✓ Pair with valid columns correctly kept")

    def test_filter_mixed_pairs(self):
        """Test filtering with mix of valid and invalid pairs."""
        pairs = [
            {
                "source_table": "hana_material_master",
                "source_column": "MATERIAL",
                "target_table": "brz_lnd_OPS_EXCEL_GPU",
                "target_column": "PLANNING_SKU"
            },
            {
                "source_table": "brz_lnd_OPS_EXCEL_GPU",
                "source_column": "PLANNING_SKU",
                "target_table": "brz_lnd_RBP_GPU",
                "target_column": "Product_Line"  # EXCLUDED
            },
            {
                "source_table": "brz_lnd_RBP_GPU",
                "source_column": "Material",
                "target_table": "brz_lnd_SKU_LIFNR_Excel",
                "target_column": "Material"
            }
        ]
        
        filtered = filter_relationship_pairs(pairs)
        assert len(filtered) == 2
        assert filtered[0]["source_column"] == "MATERIAL"
        assert filtered[1]["source_column"] == "Material"
        print("✓ Mixed pairs correctly filtered (2 kept, 1 excluded)")

    def test_filter_all_excluded_pairs(self):
        """Test filtering when all pairs have excluded fields."""
        pairs = [
            {
                "source_table": "table1",
                "source_column": "Product_Line",
                "target_table": "table2",
                "target_column": "PLANNING_SKU"
            },
            {
                "source_table": "table2",
                "source_column": "PLANNING_SKU",
                "target_table": "table3",
                "target_column": "Business_Unit"
            }
        ]
        
        filtered = filter_relationship_pairs(pairs)
        assert len(filtered) == 0
        print("✓ All excluded pairs correctly filtered out")

    def test_filter_preserves_pair_structure(self):
        """Test that filtering preserves all pair attributes."""
        pairs = [
            {
                "source_table": "hana_material_master",
                "source_column": "MATERIAL",
                "target_table": "brz_lnd_OPS_EXCEL_GPU",
                "target_column": "PLANNING_SKU",
                "relationship_type": "MATCHES",
                "confidence": 0.98,
                "bidirectional": True,
                "metadata": {"source": "manual"}
            }
        ]
        
        filtered = filter_relationship_pairs(pairs)
        assert len(filtered) == 1
        assert filtered[0]["relationship_type"] == "MATCHES"
        assert filtered[0]["confidence"] == 0.98
        assert filtered[0]["bidirectional"] is True
        assert filtered[0]["metadata"]["source"] == "manual"
        print("✓ Pair structure correctly preserved after filtering")


class TestRealWorldScenarios:
    """Test real-world relationship pair scenarios."""

    def test_scenario_four_way_material_kg(self):
        """Test the four-way material KG scenario from your JSON."""
        pairs = [
            {
                "source_table": "hana_material_master",
                "source_column": "MATERIAL",
                "target_table": "brz_lnd_OPS_EXCEL_GPU",
                "target_column": "PLANNING_SKU",
                "bidirectional": True
            },
            {
                "source_table": "brz_lnd_OPS_EXCEL_GPU",
                "source_column": "PLANNING_SKU",
                "target_table": "brz_lnd_RBP_GPU",
                "target_column": "Material"
            },
            {
                "source_table": "brz_lnd_RBP_GPU",
                "source_column": "Material",
                "target_table": "brz_lnd_SKU_LIFNR_Excel",
                "target_column": "Material"
            }
        ]
        
        filtered = filter_relationship_pairs(pairs)
        assert len(filtered) == 3
        print("✓ Four-way material KG scenario: all valid pairs kept")

    def test_scenario_with_product_line_exclusion(self):
        """Test scenario where Product_Line should be excluded."""
        pairs = [
            {
                "source_table": "hana_material_master",
                "source_column": "MATERIAL",
                "target_table": "brz_lnd_OPS_EXCEL_GPU",
                "target_column": "PLANNING_SKU"
            },
            {
                "source_table": "hana_material_master",
                "source_column": "Product_Line",
                "target_table": "brz_lnd_OPS_EXCEL_GPU",
                "target_column": "Product_Line"
            }
        ]
        
        filtered = filter_relationship_pairs(pairs)
        assert len(filtered) == 1
        assert filtered[0]["source_column"] == "MATERIAL"
        print("✓ Product_Line pair correctly excluded")

    def test_scenario_with_business_unit_exclusion(self):
        """Test scenario where Business_Unit should be excluded."""
        pairs = [
            {
                "source_table": "table1",
                "source_column": "ID",
                "target_table": "table2",
                "target_column": "ID"
            },
            {
                "source_table": "table1",
                "source_column": "Business_Unit",
                "target_table": "table2",
                "target_column": "Business_Unit"
            }
        ]
        
        filtered = filter_relationship_pairs(pairs)
        assert len(filtered) == 1
        assert filtered[0]["source_column"] == "ID"
        print("✓ Business_Unit pair correctly excluded")


class TestExcludedFieldsList:
    """Test the excluded fields list."""

    def test_excluded_fields_defined(self):
        """Test that DEFAULT_EXCLUDED_FIELDS is properly defined."""
        assert len(DEFAULT_EXCLUDED_FIELDS) > 0
        print(f"✓ DEFAULT_EXCLUDED_FIELDS defined with {len(DEFAULT_EXCLUDED_FIELDS)} entries")

    def test_excluded_fields_contains_required_fields(self):
        """Test that all required fields are in DEFAULT_EXCLUDED_FIELDS."""
        required_fields = [
            "Product_Line", "product_line", "PRODUCT_LINE", "Product Line",
            "Business_Unit", "business_unit", "BUSINESS_UNIT",
            "[Product Type]", "Product Type", "product_type", "PRODUCT_TYPE",
            "[Business Unit]", "business unit", "BUSINESS_UNIT_CODE"
        ]

        for field in required_fields:
            assert field in DEFAULT_EXCLUDED_FIELDS, f"Missing field: {field}"

        print(f"✓ All {len(required_fields)} required fields in DEFAULT_EXCLUDED_FIELDS")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

