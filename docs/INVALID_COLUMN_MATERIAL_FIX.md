# Error Fixed: "Invalid column name 'Material'" ✅

## The Error

```
2025-10-28 19:45:15 - kg_builder.services.nl_query_executor - ERROR - [nl_query_executor.py:165] - ⚠️  Error: Error executing query: com.microsoft.sqlserver.jdbc.SQLServerException: Invalid column name 'Material'.
```

### Generated SQL (WRONG)
```sql
LEFT JOIN [brz_lnd_ops_excel_gpu] g ON g.[Material] = g.[PLANNING_SKU]
```

**Problem**: The table `brz_lnd_ops_excel_gpu` doesn't have a `Material` column. It has `PLANNING_SKU` as the key column.

---

## Root Cause Analysis

### Issue 1: Self-Join Bug
The join path was trying to join a table to itself:
```
join_path = ["brz_lnd_ops_excel_gpu", "brz_lnd_ops_excel_gpu"]
```

This caused:
- `table1` = `brz_lnd_ops_excel_gpu`
- `table2` = `brz_lnd_ops_excel_gpu` (SAME!)
- Join condition: `g.id = g.id` → then `g.Material = g.PLANNING_SKU` (WRONG!)

### Issue 2: Case Sensitivity in Table Name Matching
The `_find_join_path_to_table()` method was extracting table names from KG relationships but not preserving the original case from the KG nodes. This caused:
- KG has: `brz_lnd_OPS_EXCEL_GPU` (uppercase)
- Code was using: `brz_lnd_ops_excel_gpu` (lowercase)
- Case-sensitive comparison failed to find the correct relationship

---

## Fixes Applied

### Fix 1: Skip Self-Joins in SQL Generator

**File**: `kg_builder/services/nl_sql_generator.py` (line 350)

**Added**:
```python
# Skip if same table (self-join not needed)
if table1.lower() == table2.lower():
    logger.debug(f"Skipping self-join: {table1} = {table2}")
    continue
```

This prevents generating invalid JOIN clauses when the join path contains duplicate tables.

---

### Fix 2: Preserve Original Table Case from KG

**File**: `kg_builder/services/nl_query_parser.py` (line 826)

**Before**:
```python
if source_id == f"table_{current_lower}" or source_id == current_lower:
    next_table = target_id.replace("table_", "")
```

**After**:
```python
if source_id == f"table_{current_lower}" or source_id == current_lower:
    next_table = target_id.replace("table_", "")
    # Preserve original case from KG
    for node in self.kg.nodes:
        if node.id.lower() == f"table_{next_table.lower()}" or node.id.lower() == next_table.lower():
            next_table = node.label
            break
```

This ensures that table names in the join path match the exact case used in the KG, allowing proper relationship lookups.

---

## How It Works Now

### Step 1: Find Join Path
```
source: brz_lnd_RBP_GPU
target: hana_material_master

BFS finds path:
brz_lnd_RBP_GPU → brz_lnd_OPS_EXCEL_GPU → hana_material_master
```

### Step 2: Preserve Case
```
KG nodes have:
- brz_lnd_RBP_GPU (exact case)
- brz_lnd_OPS_EXCEL_GPU (exact case)
- hana_material_master (exact case)

join_path = ["brz_lnd_RBP_GPU", "brz_lnd_OPS_EXCEL_GPU", "hana_material_master"]
```

### Step 3: Generate JOINs
```
For each pair in path:
1. brz_lnd_RBP_GPU → brz_lnd_OPS_EXCEL_GPU
   - Find relationship in KG
   - Extract: source_column="Material", target_column="PLANNING_SKU"
   - Generate: ON s.[Material] = t.[PLANNING_SKU]

2. brz_lnd_OPS_EXCEL_GPU → hana_material_master
   - Find relationship in KG
   - Extract: source_column="PLANNING_SKU", target_column="MATERIAL"
   - Generate: ON t.[PLANNING_SKU] = m.[MATERIAL]
```

### Step 4: Skip Self-Joins
```
If join_path contains duplicates (e.g., same table twice):
- Skip the self-join
- Continue to next pair
```

---

## Result

### Generated SQL (CORRECT) ✅
```sql
SELECT DISTINCT s.*, m.[ops_planner] AS master_ops_planner
FROM [brz_lnd_RBP_GPU] s
INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
LEFT JOIN [hana_material_master] m ON t.[PLANNING_SKU] = m.[MATERIAL]
WHERE t.[Active_Inactive] = 'Inactive'
```

✅ **Query executes successfully**
✅ **Correct column names used**
✅ **No more "Invalid column name" errors**

---

## Test Results

✅ **All 14 tests passing**

```
14 passed in 1.42s
```

---

## Summary

Two critical bugs fixed:

1. ✅ **Self-join prevention**: Skip JOINs when table1 = table2
2. ✅ **Case preservation**: Use exact table names from KG nodes

The system now correctly:
- Finds join paths between tables
- Preserves original table name casing
- Extracts correct join columns from KG relationships
- Generates valid SQL with proper column names
- Skips invalid self-joins

**Production ready!** 🚀

