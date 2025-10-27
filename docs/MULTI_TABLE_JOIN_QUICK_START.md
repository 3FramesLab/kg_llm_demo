# Multi-Table Join: Quick Start Guide

## 🚀 Quick Start

### Option 1: Simple 2-Table Join (Backward Compatible)

```python
from kg_builder.models import ReconciliationRule, ReconciliationMatchType

rule = ReconciliationRule(
    rule_id="rule_1",
    rule_name="Simple Join",
    source_schema="schema1",
    source_table="table1",
    source_columns=["id"],
    target_schema="schema2",
    target_table="table2",
    target_columns=["id"],
    match_type=ReconciliationMatchType.EXACT,
    confidence_score=0.95,
    reasoning="Simple join",
    validation_status="VALID"
)

# Works exactly as before!
```

---

### Option 2: 3-Table Join

```python
rule = ReconciliationRule(
    rule_id="rule_3table",
    rule_name="Three-Table Join",
    source_schema="db",
    source_table="table1",
    source_columns=["id"],
    target_schema="db",
    target_table="table3",
    target_columns=["id"],
    match_type=ReconciliationMatchType.COMPOSITE,
    confidence_score=0.90,
    reasoning="Join 3 tables",
    validation_status="VALID",
    
    # Multi-table configuration
    join_tables=["table1", "table2", "table3"],
    
    join_conditions=[
        {"table1": "table1", "table2": "table2", "on": "table1.id = table2.id"},
        {"table1": "table2", "table2": "table3", "on": "table2.id = table3.id"}
    ],
    
    join_order=["table1", "table2", "table3"],
    join_type=["INNER", "INNER"]
)
```

---

### Option 3: 4-Table Join with Column Selection

```python
rule = ReconciliationRule(
    rule_id="rule_4table",
    rule_name="Four-Table Join",
    source_schema="landing",
    source_table="brz_lnd_RBP_GPU",
    source_columns=["material"],
    target_schema="landing",
    target_table="hana_material_master",
    target_columns=["material"],
    match_type=ReconciliationMatchType.COMPOSITE,
    confidence_score=0.90,
    reasoning="Join 4 tables",
    validation_status="VALID",
    
    # Multi-table configuration
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
            "on": "brz_lnd_RBP_GPU.material = brz_lnd_OPS_EXCEL_GPU.material AND brz_lnd_RBP_GPU.planning_sku = brz_lnd_OPS_EXCEL_GPU.planning_sku"
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
    
    # Column selection - ONLY show these columns
    select_columns={
        "brz_lnd_RBP_GPU": ["material", "planning_sku", "active_inactive"],
        "brz_lnd_OPS_EXCEL_GPU": ["material", "planning_sku"],
        "brz_lnd_SKU_LIFNR_Excel": ["material"],
        "hana_material_master": ["material", "description", "product_line"]
    },
    
    # Filter conditions
    filter_conditions={"active_inactive": "Active"}
)
```

---

## 📊 Generated SQL

The above rule generates:

```sql
SELECT 
    t1.`material`, t1.`planning_sku`, t1.`active_inactive`,
    t2.`material`, t2.`planning_sku`,
    t3.`material`,
    t4.`material`, t4.`description`, t4.`product_line`
FROM brz_lnd_RBP_GPU t1
INNER JOIN brz_lnd_OPS_EXCEL_GPU t2 
    ON brz_lnd_RBP_GPU.material = brz_lnd_OPS_EXCEL_GPU.material 
    AND brz_lnd_RBP_GPU.planning_sku = brz_lnd_OPS_EXCEL_GPU.planning_sku
INNER JOIN brz_lnd_SKU_LIFNR_Excel t3
    ON brz_lnd_OPS_EXCEL_GPU.material = brz_lnd_SKU_LIFNR_Excel.material
LEFT JOIN hana_material_master t4
    ON brz_lnd_RBP_GPU.material = hana_material_master.material
WHERE t1.`active_inactive` = 'Active'
LIMIT 1000
```

---

## 🔑 Key Concepts

### join_tables
List of all tables to join:
```python
join_tables=["table1", "table2", "table3", "table4"]
```

### join_conditions
How to join each pair of tables:
```python
join_conditions=[
    {"table1": "table1", "table2": "table2", "on": "table1.id = table2.id"},
    {"table1": "table2", "table2": "table3", "on": "table2.id = table3.id"}
]
```

### join_order
Order in which to join tables:
```python
join_order=["table1", "table2", "table3"]
```

### join_type
Type of join for each join (INNER, LEFT, RIGHT, FULL):
```python
join_type=["INNER", "INNER", "LEFT"]
# Length = len(join_tables) - 1
```

### select_columns
Which columns to select from each table:
```python
select_columns={
    "table1": ["id", "name"],
    "table2": ["id", "value"],
    "table3": ["id", "description"]
}
# If not specified, selects all columns (*)
```

### filter_conditions
WHERE clause conditions:
```python
filter_conditions={"active_inactive": "Active", "deleted": False}
```

---

## ✅ Helper Methods

### Check if multi-table rule
```python
if rule.is_multi_table():
    print("This is a multi-table rule")
```

### Get join tables
```python
tables = rule.get_join_tables()
# Returns: ["table1", "table2", "table3"]
```

### Get join order
```python
order = rule.get_join_order()
# Returns: ["table1", "table2", "table3"]
```

### Get join types
```python
types = rule.get_join_types()
# Returns: ["INNER", "INNER", "LEFT"]
```

---

## 🎯 Common Patterns

### Pattern 1: Star Join
One central table joined to multiple tables:
```python
join_order=["central_table", "table2", "table3", "table4"]
join_type=["INNER", "LEFT", "LEFT"]
```

### Pattern 2: Chain Join
Tables joined in sequence:
```python
join_order=["table1", "table2", "table3", "table4"]
join_type=["INNER", "INNER", "INNER"]
```

### Pattern 3: Enrichment Join
Main tables joined, then enrichment table:
```python
join_order=["table1", "table2", "table3", "enrichment_table"]
join_type=["INNER", "INNER", "LEFT"]
```

---

## 🔄 Backward Compatibility

All existing 2-table rules work without any changes:

```python
# Old code still works!
rule = ReconciliationRule(
    rule_id="rule_1",
    rule_name="Old Rule",
    source_schema="s1",
    source_table="t1",
    source_columns=["id"],
    target_schema="s2",
    target_table="t2",
    target_columns=["id"],
    match_type=ReconciliationMatchType.EXACT,
    confidence_score=0.95,
    reasoning="Old rule",
    validation_status="VALID"
)
```

---

## 📚 More Information

- `docs/PHASE_1_MULTI_TABLE_IMPLEMENTATION.md` - Full implementation details
- `docs/MULTI_TABLE_JOIN_CODE_EXAMPLES.md` - Code examples
- `tests/test_multi_table_joins.py` - Test suite


