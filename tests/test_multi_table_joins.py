"""
Tests for multi-table join functionality in reconciliation rules.

This test suite verifies:
1. ReconciliationRule model supports multi-table joins
2. SQL generation for multi-table joins
3. Column selection in multi-table joins
4. Join order and join types
"""

import pytest
from datetime import datetime
from kg_builder.models import ReconciliationRule, ReconciliationMatchType


class TestReconciliationRuleMultiTable:
    """Test ReconciliationRule model with multi-table support."""
    
    def test_two_table_rule_backward_compatibility(self):
        """Test that 2-table rules still work (backward compatibility)."""
        rule = ReconciliationRule(
            rule_id="rule_1",
            rule_name="Test Rule",
            source_schema="schema1",
            source_table="table1",
            source_columns=["id"],
            target_schema="schema2",
            target_table="table2",
            target_columns=["id"],
            match_type=ReconciliationMatchType.EXACT,
            confidence_score=0.95,
            reasoning="Test",
            validation_status="VALID"
        )
        
        assert not rule.is_multi_table()
        assert rule.get_join_tables() == ["table1", "table2"]
        assert rule.get_join_order() == ["table1", "table2"]
        assert rule.get_join_types() == ["INNER"]
    
    def test_multi_table_rule_creation(self):
        """Test creating a multi-table rule."""
        rule = ReconciliationRule(
            rule_id="rule_multi_1",
            rule_name="Multi-Table Rule",
            source_schema="schema1",
            source_table="table1",
            source_columns=["id"],
            target_schema="schema1",
            target_table="table2",
            target_columns=["id"],
            match_type=ReconciliationMatchType.EXACT,
            confidence_score=0.95,
            reasoning="Test",
            validation_status="VALID",
            # Multi-table fields
            join_tables=["table1", "table2", "table3", "table4"],
            join_conditions=[
                {"table1": "table1", "table2": "table2", "on": "table1.id = table2.id"},
                {"table1": "table2", "table2": "table3", "on": "table2.id = table3.id"},
                {"table1": "table1", "table2": "table4", "on": "table1.id = table4.id"}
            ],
            join_order=["table1", "table2", "table3", "table4"],
            join_type=["INNER", "INNER", "LEFT"]
        )
        
        assert rule.is_multi_table()
        assert len(rule.get_join_tables()) == 4
        assert rule.get_join_order() == ["table1", "table2", "table3", "table4"]
        assert rule.get_join_types() == ["INNER", "INNER", "LEFT"]
    
    def test_multi_table_rule_with_column_selection(self):
        """Test multi-table rule with specific column selection."""
        rule = ReconciliationRule(
            rule_id="rule_cols_1",
            rule_name="Multi-Table with Columns",
            source_schema="schema1",
            source_table="table1",
            source_columns=["id"],
            target_schema="schema1",
            target_table="table2",
            target_columns=["id"],
            match_type=ReconciliationMatchType.EXACT,
            confidence_score=0.95,
            reasoning="Test",
            validation_status="VALID",
            join_tables=["table1", "table2", "table3"],
            join_conditions=[
                {"table1": "table1", "table2": "table2", "on": "table1.id = table2.id"},
                {"table1": "table2", "table2": "table3", "on": "table2.id = table3.id"}
            ],
            join_order=["table1", "table2", "table3"],
            join_type=["INNER", "INNER"],
            select_columns={
                "table1": ["id", "name", "material"],
                "table2": ["id", "planning_sku"],
                "table3": ["id", "material"]
            }
        )
        
        assert rule.is_multi_table()
        assert rule.select_columns is not None
        assert "table1" in rule.select_columns
        assert rule.select_columns["table1"] == ["id", "name", "material"]
        assert rule.select_columns["table2"] == ["id", "planning_sku"]
    
    def test_multi_table_rule_with_filter_conditions(self):
        """Test multi-table rule with filter conditions."""
        rule = ReconciliationRule(
            rule_id="rule_filter_1",
            rule_name="Multi-Table with Filters",
            source_schema="schema1",
            source_table="table1",
            source_columns=["id"],
            target_schema="schema1",
            target_table="table2",
            target_columns=["id"],
            match_type=ReconciliationMatchType.EXACT,
            confidence_score=0.95,
            reasoning="Test",
            validation_status="VALID",
            join_tables=["table1", "table2"],
            join_conditions=[
                {"table1": "table1", "table2": "table2", "on": "table1.id = table2.id"}
            ],
            join_order=["table1", "table2"],
            join_type=["INNER"],
            filter_conditions={"active_inactive": "Active", "deleted": False}
        )
        
        assert rule.filter_conditions is not None
        assert rule.filter_conditions["active_inactive"] == "Active"
        assert rule.filter_conditions["deleted"] is False
    
    def test_default_join_types(self):
        """Test that default join types are INNER."""
        rule = ReconciliationRule(
            rule_id="rule_default_1",
            rule_name="Default Join Types",
            source_schema="schema1",
            source_table="table1",
            source_columns=["id"],
            target_schema="schema1",
            target_table="table2",
            target_columns=["id"],
            match_type=ReconciliationMatchType.EXACT,
            confidence_score=0.95,
            reasoning="Test",
            validation_status="VALID",
            join_tables=["table1", "table2", "table3"],
            join_conditions=[
                {"table1": "table1", "table2": "table2", "on": "table1.id = table2.id"},
                {"table1": "table2", "table2": "table3", "on": "table2.id = table3.id"}
            ]
            # No join_type specified
        )
        
        join_types = rule.get_join_types()
        assert len(join_types) == 2  # 3 tables = 2 joins
        assert all(jt == "INNER" for jt in join_types)
    
    def test_scenario_four_table_join(self):
        """Test the exact scenario from user requirements."""
        # Scenario: brz_lnd_RBP_GPU, brz_lnd_OPS_EXCEL_GPU, brz_lnd_SKU_LIFNR_Excel, hana_material_master
        rule = ReconciliationRule(
            rule_id="rule_scenario_1",
            rule_name="Four-Table Join Scenario",
            source_schema="landing",
            source_table="brz_lnd_RBP_GPU",
            source_columns=["material"],
            target_schema="landing",
            target_table="hana_material_master",
            target_columns=["material"],
            match_type=ReconciliationMatchType.COMPOSITE,
            confidence_score=0.90,
            reasoning="Join RBP_GPU with OPS_EXCEL_GPU, SKU_LIFNR, and hana_material_master",
            validation_status="VALID",
            join_tables=[
                "brz_lnd_RBP_GPU",
                "brz_lnd_OPS_EXCEL_GPU",
                "brz_lnd_SKU_LIFNR_Excel",
                "hana_material_master"
            ],
            join_conditions=[
                {
                    "table1": "brz_lnd_RBP_GPU",
                    "table2": "brz_lnd_OPS_EXCEL_GPU",
                    "on": "brz_lnd_RBP_GPU.material = brz_lnd_OPS_EXCEL_GPU.material AND brz_lnd_RBP_GPU.planning_sku = brz_lnd_OPS_EXCEL_GPU.planning_sku AND brz_lnd_RBP_GPU.active_inactive = brz_lnd_OPS_EXCEL_GPU.active_inactive"
                },
                {
                    "table1": "brz_lnd_OPS_EXCEL_GPU",
                    "table2": "brz_lnd_SKU_LIFNR_Excel",
                    "on": "brz_lnd_OPS_EXCEL_GPU.material = brz_lnd_SKU_LIFNR_Excel.material"
                },
                {
                    "table1": "brz_lnd_RBP_GPU",
                    "table2": "hana_material_master",
                    "on": "brz_lnd_RBP_GPU.material = hana_material_master.material"
                }
            ],
            join_order=[
                "brz_lnd_RBP_GPU",
                "brz_lnd_OPS_EXCEL_GPU",
                "brz_lnd_SKU_LIFNR_Excel",
                "hana_material_master"
            ],
            join_type=["INNER", "INNER", "LEFT"],
            select_columns={
                "brz_lnd_RBP_GPU": ["material", "planning_sku", "active_inactive"],
                "brz_lnd_OPS_EXCEL_GPU": ["material", "planning_sku", "active_inactive"],
                "brz_lnd_SKU_LIFNR_Excel": ["material"],
                "hana_material_master": ["material", "description", "product_line"]
            },
            filter_conditions={"active_inactive": "Active"}
        )
        
        assert rule.is_multi_table()
        assert len(rule.get_join_tables()) == 4
        assert rule.get_join_types() == ["INNER", "INNER", "LEFT"]
        assert rule.select_columns["brz_lnd_RBP_GPU"] == ["material", "planning_sku", "active_inactive"]
        assert rule.select_columns["hana_material_master"] == ["material", "description", "product_line"]
        assert rule.filter_conditions["active_inactive"] == "Active"


class TestSQLGeneration:
    """Test SQL generation for multi-table joins."""
    
    def test_select_clause_all_columns(self):
        """Test SELECT clause generation with all columns."""
        from kg_builder.services.reconciliation_executor import ReconciliationExecutor
        
        executor = ReconciliationExecutor()
        
        rule = ReconciliationRule(
            rule_id="rule_1",
            rule_name="Test",
            source_schema="s1",
            source_table="t1",
            source_columns=["id"],
            target_schema="s1",
            target_table="t2",
            target_columns=["id"],
            match_type=ReconciliationMatchType.EXACT,
            confidence_score=0.95,
            reasoning="Test",
            validation_status="VALID",
            join_tables=["table1", "table2", "table3"]
        )
        
        select_clause = executor._build_select_clause(rule, "mysql", "")
        assert "t1.*" in select_clause
        assert "t2.*" in select_clause
        assert "t3.*" in select_clause
        assert select_clause.startswith("SELECT")
    
    def test_select_clause_specific_columns(self):
        """Test SELECT clause generation with specific columns."""
        from kg_builder.services.reconciliation_executor import ReconciliationExecutor
        
        executor = ReconciliationExecutor()
        
        rule = ReconciliationRule(
            rule_id="rule_1",
            rule_name="Test",
            source_schema="s1",
            source_table="t1",
            source_columns=["id"],
            target_schema="s1",
            target_table="t2",
            target_columns=["id"],
            match_type=ReconciliationMatchType.EXACT,
            confidence_score=0.95,
            reasoning="Test",
            validation_status="VALID",
            join_tables=["table1", "table2"],
            select_columns={
                "table1": ["id", "name"],
                "table2": ["id", "value"]
            }
        )
        
        select_clause = executor._build_select_clause(rule, "mysql", "")
        assert "t1.`id`" in select_clause
        assert "t1.`name`" in select_clause
        assert "t2.`id`" in select_clause
        assert "t2.`value`" in select_clause


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

