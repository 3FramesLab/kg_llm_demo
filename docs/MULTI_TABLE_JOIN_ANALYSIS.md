# Multi-Table Join Analysis: Why Only hana_material_master is Being Joined

## 🔴 Problem Statement

You want:
```
brz_lnd_RBP_GPU 
  ↓ JOIN on (material, planning_sku, active_inactive)
brz_lnd_OPS_EXCEL_GPU
  ↓ JOIN on (material, planning_sku, active_inactive)
brz_lnd_SKU_LIFNR_Excel
  ↓ JOIN on (material)
hana_material_master (for enrichment)
```

But you're getting:
```
Only hana_material_master is being joined
Other tables are not being joined together
```

---

## 🔍 Root Cause Analysis

### Issue 1: Reconciliation Rules Only Support 2-Table Joins

**Location**: `kg_builder/services/reconciliation_executor.py` (lines 435-502)

The SQL generation logic only creates **INNER JOIN** between 2 tables:

```python
# BROKEN: Only 2-table join
query = f"""
SELECT s.*, t.*
FROM {source_table} s
INNER JOIN {target_table} t
    ON {join_condition}
"""
```

**Problem**: This is a **binary join** - it can only join source to target. It cannot chain multiple tables.

### Issue 2: Rule Generation Creates Single-Pair Rules

**Location**: `kg_builder/services/reconciliation_service.py` (lines 208-364)

Rules are generated as **source → target pairs**:

```python
# BROKEN: Only creates 2-table rules
rules.append(ReconciliationRule(
    source_table=source_table,
    target_table=target_table,
    source_columns=[column_name],
    target_columns=[target_column],
    # ... only 2 tables!
))
```

**Problem**: Each rule only knows about 2 tables. It doesn't know about other tables that should also be joined.

### Issue 3: LLM Prompt Doesn't Specify Multi-Table Joins

**Location**: `kg_builder/services/multi_schema_llm_service.py` (lines 544-678)

The LLM prompt for rule generation doesn't ask for multi-table joins:

```python
# BROKEN: Prompt only shows 2-table examples
"sql_template": "SELECT * FROM table1 t1 JOIN table2 t2 ON t1.col1 = t2.col1"
```

**Problem**: LLM generates 2-table rules because that's what the prompt shows.

### Issue 4: Field Preferences Not Used for Multi-Table Joins

**Location**: `kg_builder/services/multi_schema_llm_service.py` (lines 558-594)

Field preferences are parsed but not used to determine **join order** or **which tables to join**:

```python
# Field preferences show:
# - brz_lnd_RBP_GPU: priority_fields = ["Material"]
# - brz_lnd_OPS_EXCEL_GPU: priority_fields = ["PLANNING_SKU"]
# - brz_lnd_SKU_LIFNR_Excel: priority_fields = ["Material"]
# - hana_material_master: for enrichment

# But LLM doesn't know to:
# 1. Join these 3 tables together first
# 2. Then join to hana_material_master for enrichment
```

---

## 🎯 Where to Improve

### 1. **Knowledge Graph (KG)** ✅ Likely OK
- KG correctly identifies relationships between tables
- Issue is NOT in KG generation

### 2. **NL Relationships** ✅ Likely OK
- NL parser correctly converts natural language to relationships
- Issue is NOT in NL parsing

### 3. **SQL Generation** ❌ **NEEDS IMPROVEMENT**
- **Problem**: Only generates 2-table INNER JOINs
- **Solution**: Support multi-table joins with proper join order

### 4. **Rule Generation** ❌ **NEEDS IMPROVEMENT**
- **Problem**: Creates single-pair rules (source → target)
- **Solution**: Create composite rules that specify multiple tables and join order

### 5. **LLM Prompt** ❌ **NEEDS IMPROVEMENT**
- **Problem**: Doesn't ask for multi-table join rules
- **Solution**: Add examples and instructions for multi-table joins

### 6. **Field Preferences Usage** ❌ **NEEDS IMPROVEMENT**
- **Problem**: Not used to determine join order or table grouping
- **Solution**: Use field preferences to guide multi-table join generation

---

## 📊 Current Architecture

```
KG Relationships
  ↓
Rule Generation (2-table pairs)
  ↓
SQL Generation (INNER JOIN only)
  ↓
Execution (Only 2 tables joined)
```

---

## 🚀 Proposed Solution

### Step 1: Enhance Rule Model
Add support for multi-table rules:

```python
class ReconciliationRule:
    # Current (2-table)
    source_table: str
    target_table: str
    
    # NEW (multi-table)
    join_tables: List[str]  # [table1, table2, table3]
    join_conditions: List[Dict]  # [{table1: table2, on: "col1=col2"}, ...]
    join_order: List[str]  # Order to join tables
```

### Step 2: Enhance SQL Generation
Support multi-table joins:

```sql
SELECT t1.*, t2.*, t3.*, t4.*
FROM brz_lnd_RBP_GPU t1
INNER JOIN brz_lnd_OPS_EXCEL_GPU t2 
    ON t1.material = t2.material 
    AND t1.planning_sku = t2.planning_sku
    AND t1.active_inactive = t2.active_inactive
INNER JOIN brz_lnd_SKU_LIFNR_Excel t3
    ON t1.material = t3.material
LEFT JOIN hana_material_master t4
    ON t1.material = t4.material
```

### Step 3: Use Field Preferences for Join Order
- Priority fields → join first
- Exclude fields → skip
- Filter hints → WHERE clause

### Step 4: Update LLM Prompt
- Show multi-table join examples
- Ask for join order
- Use field preferences to guide generation

---

## 📋 Implementation Checklist

- [ ] Enhance ReconciliationRule model to support multi-table joins
- [ ] Update SQL generation to handle multi-table joins
- [ ] Modify rule generation to create multi-table rules
- [ ] Update LLM prompt with multi-table examples
- [ ] Use field preferences to determine join order
- [ ] Add tests for multi-table join scenarios
- [ ] Update documentation

---

## 🔗 Related Files

1. `kg_builder/models.py` - ReconciliationRule model
2. `kg_builder/services/reconciliation_executor.py` - SQL generation
3. `kg_builder/services/reconciliation_service.py` - Rule generation
4. `kg_builder/services/multi_schema_llm_service.py` - LLM prompts
5. `kg_builder/services/landing_query_builder.py` - Query building

---

## 💡 Key Insights

1. **KG is working correctly** - It identifies all relationships
2. **Rule generation is too simplistic** - Only creates 2-table rules
3. **SQL generation is limited** - Only supports 2-table INNER JOINs
4. **Field preferences are underutilized** - Should guide join order
5. **LLM needs better prompts** - Should ask for multi-table rules

---

## 🎯 Priority

**HIGH**: This is a significant limitation that prevents complex data reconciliation scenarios.


