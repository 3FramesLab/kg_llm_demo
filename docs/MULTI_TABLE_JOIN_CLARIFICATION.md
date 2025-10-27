# Multi-Table Join: Clarification - Will All 4 Tables Be Used Every Time?

## ❓ Question
"Is it all 4 tables will used everytime?"

## ✅ Answer
**NO** - Only the tables you specify in the rule will be used.

---

## 🎯 How It Works

### Each Rule Defines Its Own Tables

When you create a reconciliation rule, you explicitly specify:
```python
join_tables = ["table1", "table2", "table3", "table4"]
```

**Only these tables will be used for that rule.**

---

## 📊 Example: Your 4 Tables

You have 4 tables:
1. `brz_lnd_RBP_GPU`
2. `brz_lnd_OPS_EXCEL_GPU`
3. `brz_lnd_SKU_LIFNR_Excel`
4. `hana_material_master`

---

## 🎯 Scenario 1: Use All 4 Tables

```python
rule_all_4 = ReconciliationRule(
    rule_id="rule_all_4",
    rule_name="All Four Tables",
    # ... basic fields ...
    join_tables=[
        "brz_lnd_RBP_GPU",
        "brz_lnd_OPS_EXCEL_GPU",
        "brz_lnd_SKU_LIFNR_Excel",
        "hana_material_master"
    ],
    # ... join conditions ...
)
```

**Result**: All 4 tables are joined
```sql
FROM brz_lnd_RBP_GPU t1
INNER JOIN brz_lnd_OPS_EXCEL_GPU t2 ON ...
INNER JOIN brz_lnd_SKU_LIFNR_Excel t3 ON ...
LEFT JOIN hana_material_master t4 ON ...
```

---

## 🎯 Scenario 2: Use Only 2 Tables

```python
rule_2_tables = ReconciliationRule(
    rule_id="rule_2_tables",
    rule_name="Only Two Tables",
    # ... basic fields ...
    join_tables=[
        "brz_lnd_RBP_GPU",
        "hana_material_master"
    ],
    # ... join conditions ...
)
```

**Result**: Only 2 tables are joined
```sql
FROM brz_lnd_RBP_GPU t1
LEFT JOIN hana_material_master t4 ON ...
```

---

## 🎯 Scenario 3: Use Only 3 Tables

```python
rule_3_tables = ReconciliationRule(
    rule_id="rule_3_tables",
    rule_name="Three Tables",
    # ... basic fields ...
    join_tables=[
        "brz_lnd_RBP_GPU",
        "brz_lnd_OPS_EXCEL_GPU",
        "brz_lnd_SKU_LIFNR_Excel"
    ],
    # ... join conditions ...
)
```

**Result**: Only 3 tables are joined
```sql
FROM brz_lnd_RBP_GPU t1
INNER JOIN brz_lnd_OPS_EXCEL_GPU t2 ON ...
INNER JOIN brz_lnd_SKU_LIFNR_Excel t3 ON ...
```

---

## 🎯 Scenario 4: Use Different 2 Tables

```python
rule_different_2 = ReconciliationRule(
    rule_id="rule_different_2",
    rule_name="Different Two Tables",
    # ... basic fields ...
    join_tables=[
        "brz_lnd_OPS_EXCEL_GPU",
        "brz_lnd_SKU_LIFNR_Excel"
    ],
    # ... join conditions ...
)
```

**Result**: Different 2 tables are joined
```sql
FROM brz_lnd_OPS_EXCEL_GPU t1
INNER JOIN brz_lnd_SKU_LIFNR_Excel t2 ON ...
```

---

## 📋 Summary Table

| Rule | Tables Used | SQL |
|------|-------------|-----|
| **rule_all_4** | 4 tables | `FROM t1 JOIN t2 JOIN t3 JOIN t4` |
| **rule_2_tables** | 2 tables | `FROM t1 JOIN t4` |
| **rule_3_tables** | 3 tables | `FROM t1 JOIN t2 JOIN t3` |
| **rule_different_2** | 2 tables | `FROM t2 JOIN t3` |

---

## 🔑 Key Points

### 1. **You Control Which Tables**
```python
join_tables = ["table1", "table2"]  # Only these 2 tables
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
join_type = ["INNER", "LEFT"]  # First INNER, second LEFT
```

---

## ❓ FAQ

### Q: Will all 4 tables be used every time?
**A**: No. Only the tables you specify in `join_tables` will be used.

### Q: Can I create multiple rules with different tables?
**A**: Yes! You can create as many rules as you need, each with different tables.

### Q: What if I only want to use 2 of the 4 tables?
**A**: Just specify those 2 tables in `join_tables`.

### Q: Can I change which tables are used?
**A**: Yes! Create a new rule with different `join_tables`.

### Q: Do I have to use all 4 tables together?
**A**: No! You can create separate rules for different combinations.

### Q: What's the maximum number of tables?
**A**: Theoretically unlimited, but practically depends on your database performance.

---

## 🎯 Your Use Case

For your scenario, you have options:

### Option 1: One Rule with All 4 Tables
```python
rule = ReconciliationRule(
    # ...
    join_tables=[
        "brz_lnd_RBP_GPU",
        "brz_lnd_OPS_EXCEL_GPU",
        "brz_lnd_SKU_LIFNR_Excel",
        "hana_material_master"
    ]
)
```

### Option 2: Multiple Rules with Different Combinations
```python
# Rule 1: Join the 3 main tables
rule1 = ReconciliationRule(
    # ...
    join_tables=[
        "brz_lnd_RBP_GPU",
        "brz_lnd_OPS_EXCEL_GPU",
        "brz_lnd_SKU_LIFNR_Excel"
    ]
)

# Rule 2: Join with enrichment table
rule2 = ReconciliationRule(
    # ...
    join_tables=[
        "brz_lnd_RBP_GPU",
        "hana_material_master"
    ]
)

# Rule 3: Join OPS and SKU
rule3 = ReconciliationRule(
    # ...
    join_tables=[
        "brz_lnd_OPS_EXCEL_GPU",
        "brz_lnd_SKU_LIFNR_Excel"
    ]
)
```

---

## ✅ Conclusion

- ✅ You have full control over which tables are used
- ✅ Each rule specifies its own tables
- ✅ Not all 4 tables have to be used every time
- ✅ You can create multiple rules with different table combinations
- ✅ The system only joins the tables you specify


