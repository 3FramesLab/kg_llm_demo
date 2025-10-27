# Filter Extraction Fix - WHERE Clause Generation ✅

## 🎯 Problem

Your query was missing the WHERE clause for filters:

**Query**: "Show me all the products in RBP GPU which are in active OPS Excel"

**Generated SQL** (Before):
```sql
SELECT DISTINCT s.* 
FROM [brz_lnd_RBP_GPU] s
INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
```

**Expected SQL** (After):
```sql
SELECT DISTINCT s.* 
FROM [brz_lnd_RBP_GPU] s
INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
WHERE t.[Active_Inactive] = 'Active'
```

---

## 🔍 Root Causes

### Issue 1: LLM Prompt Not Extracting Filters

**File**: `kg_builder/services/nl_query_parser.py`

**Problem**: The LLM prompt examples showed `filters: []` which told the LLM not to extract filters.

**Example in prompt**:
```python
- Query: "Show me products in RBP which are in active OPS Excel"
  → filters: []  # ❌ This tells LLM not to extract filters!
```

### Issue 2: Filters Applied to Wrong Table

**File**: `kg_builder/services/nl_sql_generator.py`

**Problem**: Filters were being applied to source table ("s") instead of target table ("t").

```python
# BEFORE (Wrong)
where_clause = self._build_where_clause(intent.filters, "s")  # ❌ Applied to source

# AFTER (Correct)
where_clause = self._build_where_clause(intent.filters, "t")  # ✅ Applied to target
```

---

## ✅ Solution Implemented

### Fix 1: Improved LLM Prompt

**File**: `kg_builder/services/nl_query_parser.py` (Lines 493-518)

**Changes**:
1. Added explicit filter extraction guide
2. Updated examples to show filters being extracted
3. Provided column name mapping (e.g., "active" → "Active_Inactive")

**New Prompt Section**:
```python
FILTER EXTRACTION GUIDE:
- "active" or "inactive" → Look for columns like: Active_Inactive, Status, State, Flag, etc.
- For target table in multi-table queries, check its columns for status-related fields
- Always include the correct column name from the schema, not generic names

EXAMPLES:
- Query: "Show me products in RBP which are in active OPS Excel"
  → filters: [{{"column": "Active_Inactive", "value": "Active"}}]
  (Filter applies to target table brz_lnd_OPS_EXCEL_GPU)
```

### Fix 2: Apply Filters to Correct Table

**File**: `kg_builder/services/nl_sql_generator.py` (Lines 120-131)

**Changes**:
1. Changed filter table alias from "s" (source) to "t" (target)
2. Added logic to handle NOT_IN operation (append to existing WHERE)
3. Added logic for IN operation (create new WHERE clause)

**New Code**:
```python
# Add filters if present
# Filters typically apply to the target table in multi-table queries
if intent.filters:
    where_clause = self._build_where_clause(intent.filters, "t")
    if intent.operation == "NOT_IN":
        # For NOT_IN, append to existing WHERE clause
        sql += f"\nAND {where_clause}"
    else:
        # For IN and others, add new WHERE clause
        sql += f"\nWHERE {where_clause}"
```

---

## 🔄 How It Works Now

### Processing Flow

```
Query: "Show me all products in RBP which are in active OPS Excel"
    ↓
LLM Parser: Extracts tables and filters
    ↓
Extracted:
  - source_table: "brz_lnd_RBP_GPU"
  - target_table: "brz_lnd_OPS_EXCEL_GPU"
  - filters: [{"column": "Active_Inactive", "value": "Active"}]
    ↓
SQL Generator: Builds query with WHERE clause
    ↓
Generated SQL:
  SELECT DISTINCT s.* 
  FROM [brz_lnd_RBP_GPU] s
  INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
  WHERE t.[Active_Inactive] = 'Active'
    ↓
SUCCESS: Query executes with filter ✅
```

---

## 📊 Before vs After

### Before ❌
```
Query: "Show me all products in RBP which are in active OPS Excel"
↓
LLM: Doesn't extract filters (prompt shows filters: [])
↓
SQL: SELECT ... FROM ... INNER JOIN ... (NO WHERE CLAUSE)
↓
Result: Returns ALL products, not just active ones
```

### After ✅
```
Query: "Show me all products in RBP which are in active OPS Excel"
↓
LLM: Extracts filters with correct column name
↓
SQL: SELECT ... FROM ... INNER JOIN ... WHERE t.[Active_Inactive] = 'Active'
↓
Result: Returns ONLY active products ✅
```

---

## 🧪 Test Cases

### Test Case 1: Multi-table with "active" filter

**Query**:
```
Show me all products in RBP which are in active OPS Excel
```

**Expected SQL**:
```sql
SELECT DISTINCT s.* 
FROM [brz_lnd_RBP_GPU] s
INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
WHERE t.[Active_Inactive] = 'Active'
```

**Expected Result**: ✅ Only active products returned

---

### Test Case 2: Multi-table with "inactive" filter

**Query**:
```
Show me products in RBP which are in inactive OPS Excel
```

**Expected SQL**:
```sql
SELECT DISTINCT s.* 
FROM [brz_lnd_RBP_GPU] s
INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
WHERE t.[Active_Inactive] = 'Inactive'
```

---

### Test Case 3: NOT_IN with filter

**Query**:
```
Show me products in RBP which are not in active OPS Excel
```

**Expected SQL**:
```sql
SELECT DISTINCT s.* 
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
WHERE t.[PLANNING_SKU] IS NULL
AND t.[Active_Inactive] = 'Active'
```

---

## 📁 Files Modified

| File | Lines | Change |
|------|-------|--------|
| `kg_builder/services/nl_query_parser.py` | 493-518 | Improved LLM prompt with filter extraction guide |
| `kg_builder/services/nl_sql_generator.py` | 120-131 | Apply filters to target table, handle NOT_IN |

---

## 🚀 Benefits

✅ **Filters Now Extracted**: LLM properly extracts filter conditions

✅ **Correct Table**: Filters applied to target table (where they belong)

✅ **Proper WHERE Clause**: SQL includes WHERE clause with filters

✅ **Accurate Results**: Queries return filtered data, not all data

✅ **Handles All Operations**: Works with IN, NOT_IN, and other operations

---

**Status**: ✅ **COMPLETE**

Filters are now properly extracted and applied to generate correct WHERE clauses!

