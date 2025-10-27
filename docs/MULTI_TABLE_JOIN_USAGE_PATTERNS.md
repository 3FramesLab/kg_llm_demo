# Multi-Table Join: Usage Patterns & When Tables Are Used

## 🎯 Key Question: Will All 4 Tables Be Used Every Time?

**Answer**: NO - Only the tables you specify in `join_tables` will be used.

---

## 📋 How It Works

### Rule Definition Controls Which Tables Are Used

When you create a rule, you explicitly specify:
1. **Which tables to join** (`join_tables`)
2. **How to join them** (`join_conditions`)
3. **In what order** (`join_order`)
4. **What type of join** (`join_type`)

**Only these specified tables will be used.**

---

## 🎯 Scenario 1: Use All 4 Tables

```python
rule = ReconciliationRule(
    rule_id="rule_all_4",
    rule_name="All Four Tables",
    # ... basic fields ...
    
    # Use ALL 4 tables
    join_tables=[
        "brz_lnd_RBP_GPU",
        "brz_lnd_OPS_EXCEL_GPU",
        "brz_lnd_SKU_LIFNR_Excel",
        "hana_material_master"
    ],
    
    join_conditions=[
        {"table1": "brz_lnd_RBP_GPU", "table2": "brz_lnd_OPS_EXCEL_GPU", 
         "on": "brz_lnd_RBP_GPU.material = brz_lnd_OPS_EXCEL_GPU.material"},
        {"table1": "brz_lnd_OPS_EXCEL_GPU", "table2": "brz_lnd_SKU_LIFNR_Excel",
         "on": "brz_lnd_OPS_EXCEL_GPU.material = brz_lnd_SKU_LIFNR_Excel.material"},
        {"table1": "brz_lnd_RBP_GPU", "table2": "hana_material_master",
         "on": "brz_lnd_RBP_GPU.material = hana_material_master.material"}
    ],
    
    join_order=[
        "brz_lnd_RBP_GPU",
        "brz_lnd_OPS_EXCEL_GPU",
        "brz_lnd_SKU_LIFNR_Excel",
        "hana_material_master"
    ],
    
    join_type=["INNER", "INNER", "LEFT"]
)
```

**Generated SQL**:
```sql
SELECT t1.*, t2.*, t3.*, t4.*
FROM brz_lnd_RBP_GPU t1
INNER JOIN brz_lnd_OPS_EXCEL_GPU t2 ON ...
INNER JOIN brz_lnd_SKU_LIFNR_Excel t3 ON ...
LEFT JOIN hana_material_master t4 ON ...
```

---

## 🎯 Scenario 2: Use Only 2 Tables

```python
rule = ReconciliationRule(
    rule_id="rule_2_tables",
    rule_name="Only Two Tables",
    # ... basic fields ...
    
    # Use ONLY 2 tables
    join_tables=[
        "brz_lnd_RBP_GPU",
        "hana_material_master"
    ],
    
    join_conditions=[
        {"table1": "brz_lnd_RBP_GPU", "table2": "hana_material_master",
         "on": "brz_lnd_RBP_GPU.material = hana_material_master.material"}
    ],
    
    join_order=[
        "brz_lnd_RBP_GPU",
        "hana_material_master"
    ],
    
    join_type=["LEFT"]
)
```

**Generated SQL**:
```sql
SELECT t1.*, t2.*
FROM brz_lnd_RBP_GPU t1
LEFT JOIN hana_material_master t2 ON ...
```

---

## 🎯 Scenario 3: Use Only 3 Tables

```python
rule = ReconciliationRule(
    rule_id="rule_3_tables",
    rule_name="Three Tables",
    # ... basic fields ...
    
    # Use ONLY 3 tables
    join_tables=[
        "brz_lnd_RBP_GPU",
        "brz_lnd_OPS_EXCEL_GPU",
        "brz_lnd_SKU_LIFNR_Excel"
    ],
    
    join_conditions=[
        {"table1": "brz_lnd_RBP_GPU", "table2": "brz_lnd_OPS_EXCEL_GPU",
         "on": "brz_lnd_RBP_GPU.material = brz_lnd_OPS_EXCEL_GPU.material"},
        {"table1": "brz_lnd_OPS_EXCEL_GPU", "table2": "brz_lnd_SKU_LIFNR_Excel",
         "on": "brz_lnd_OPS_EXCEL_GPU.material = brz_lnd_SKU_LIFNR_Excel.material"}
    ],
    
    join_order=[
        "brz_lnd_RBP_GPU",
        "brz_lnd_OPS_EXCEL_GPU",
        "brz_lnd_SKU_LIFNR_Excel"
    ],
    
    join_type=["INNER", "INNER"]
)
```

**Generated SQL**:
```sql
SELECT t1.*, t2.*, t3.*
FROM brz_lnd_RBP_GPU t1
INNER JOIN brz_lnd_OPS_EXCEL_GPU t2 ON ...
INNER JOIN brz_lnd_SKU_LIFNR_Excel t3 ON ...
```

---

## 🎯 Scenario 4: Use 5+ Tables

```python
rule = ReconciliationRule(
    rule_id="rule_5_tables",
    rule_name="Five Tables",
    # ... basic fields ...
    
    # Use 5 tables (or more!)
    join_tables=[
        "brz_lnd_RBP_GPU",
        "brz_lnd_OPS_EXCEL_GPU",
        "brz_lnd_SKU_LIFNR_Excel",
        "hana_material_master",
        "another_table"
    ],
    
    join_conditions=[
        # ... 4 join conditions for 5 tables ...
    ],
    
    join_order=[
        "brz_lnd_RBP_GPU",
        "brz_lnd_OPS_EXCEL_GPU",
        "brz_lnd_SKU_LIFNR_Excel",
        "hana_material_master",
        "another_table"
    ],
    
    join_type=["INNER", "INNER", "LEFT", "LEFT"]
)
```

---

## 📊 Comparison: Different Rules

| Rule | Tables | SQL |
|------|--------|-----|
| **Rule 1** | 4 tables | `FROM t1 JOIN t2 JOIN t3 JOIN t4` |
| **Rule 2** | 2 tables | `FROM t1 JOIN t2` |
| **Rule 3** | 3 tables | `FROM t1 JOIN t2 JOIN t3` |
| **Rule 4** | 5 tables | `FROM t1 JOIN t2 JOIN t3 JOIN t4 JOIN t5` |

---

## 🔑 Key Points

### 1. **You Control Which Tables Are Used**
```python
join_tables = ["table1", "table2", "table3"]  # Only these 3 tables
```

### 2. **You Control the Join Order**
```python
join_order = ["table1", "table2", "table3"]  # Join in this order
```

### 3. **You Control the Join Conditions**
```python
join_conditions = [
    {"table1": "table1", "table2": "table2", "on": "..."},
    {"table1": "table2", "table2": "table3", "on": "..."}
]
```

### 4. **You Control the Join Types**
```python
join_type = ["INNER", "LEFT"]  # First join is INNER, second is LEFT
```

---

## 💡 Common Patterns

### Pattern 1: Progressive Enrichment
Start with main table, add enrichment tables one by one:

```python
join_tables = ["main_table", "enrichment1", "enrichment2", "enrichment3"]
join_type = ["INNER", "LEFT", "LEFT", "LEFT"]  # Main is INNER, enrichments are LEFT
```

### Pattern 2: Data Quality Check
Join main table with validation tables:

```python
join_tables = ["main_table", "validation_table1", "validation_table2"]
join_type = ["INNER", "INNER", "INNER"]  # All INNER - strict matching
```

### Pattern 3: Reconciliation
Join source and target with reference tables:

```python
join_tables = ["source_table", "target_table", "reference_table"]
join_type = ["INNER", "LEFT"]  # Source-Target INNER, Reference LEFT
```

---

## ❓ FAQ

### Q: Will all 4 tables be used every time?
**A**: No. Only the tables you specify in `join_tables` will be used.

### Q: Can I create multiple rules with different tables?
**A**: Yes! You can create:
- Rule 1: Uses 4 tables
- Rule 2: Uses 2 tables
- Rule 3: Uses 3 tables
- etc.

### Q: What if I only want to use 2 of the 4 tables?
**A**: Just specify those 2 tables in `join_tables`:
```python
join_tables = ["brz_lnd_RBP_GPU", "hana_material_master"]
```

### Q: Can I change which tables are used?
**A**: Yes! Create a new rule with different `join_tables`.

### Q: What's the maximum number of tables?
**A**: Theoretically unlimited, but practically depends on your database performance.

### Q: Do I have to use all 4 tables together?
**A**: No! You can create separate rules for different combinations:
- Rule A: brz_lnd_RBP_GPU + brz_lnd_OPS_EXCEL_GPU
- Rule B: brz_lnd_OPS_EXCEL_GPU + brz_lnd_SKU_LIFNR_Excel
- Rule C: brz_lnd_RBP_GPU + hana_material_master
- Rule D: All 4 tables together

---

## 🎯 Your Scenario

For your specific case:

**Option 1: One rule with all 4 tables**
```python
join_tables = [
    "brz_lnd_RBP_GPU",
    "brz_lnd_OPS_EXCEL_GPU",
    "brz_lnd_SKU_LIFNR_Excel",
    "hana_material_master"
]
```

**Option 2: Multiple rules with different combinations**
```python
# Rule 1: Join the 3 main tables
join_tables = [
    "brz_lnd_RBP_GPU",
    "brz_lnd_OPS_EXCEL_GPU",
    "brz_lnd_SKU_LIFNR_Excel"
]

# Rule 2: Join with enrichment table
join_tables = [
    "brz_lnd_RBP_GPU",
    "hana_material_master"
]
```

---

## ✅ Summary

- ✅ You control which tables are used
- ✅ You control the join order
- ✅ You control the join conditions
- ✅ You control the join types
- ✅ You can create multiple rules with different tables
- ✅ Not all 4 tables have to be used every time


