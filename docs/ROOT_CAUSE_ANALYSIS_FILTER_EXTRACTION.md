# Root Cause Analysis: Filter Extraction Not Working ❌

## 🎯 The Problem

Query: `Show me all products in RBP which are in active OPS Excel`

**Expected**: WHERE clause with filter
```sql
WHERE t.[Active_Inclusive] = 'Active'
```

**Actual**: No WHERE clause
```sql
SELECT DISTINCT TOP 1000 s.*
FROM [brz_lnd_RBP_GPU] s
INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
```

---

## 🔍 Root Cause Found!

### The Issue: LLM Temperature Parameter Error

**Error Message from Logs**:
```
Error code: 400 - {'error': {'message': "Unsupported value: 'temperature' does not 
support 0.3 with this model. Only the default (1) value is supported.", 
'type': 'invalid_request_error', 'param': 'temperature', 'code': 'unsupported_value'}}
```

### What Happened

1. **LLM Call Failed**
   - Code tried to call LLM with `temperature=0.3`
   - Model (gpt-5) doesn't support this parameter
   - API returned 400 Bad Request error

2. **Fallback to Rule-Based Parsing**
   - LLM parsing failed, so code fell back to rule-based parsing
   - Rule-based parser doesn't extract filters
   - Result: `filters=[]` (empty)

3. **No WHERE Clause Generated**
   - SQL generator received empty filters
   - No WHERE clause was added
   - Query returned ALL 145 products instead of filtered results

---

## 📊 Execution Flow (What Actually Happened)

```
Query: "Show me all products in RBP which are in active OPS Excel"
    ↓
LLM Parsing Attempt
    ├─ Call: POST https://api.openai.com/v1/chat/completions
    ├─ Parameters: temperature=0.3
    └─ Response: 400 Bad Request ❌
    ↓
Fallback to Rule-Based Parsing
    ├─ Extract tables: ['RBP', 'OPS', 'Excel']
    ├─ Set source_table: rbp
    ├─ Set target_table: ops
    ├─ Resolve: rbp → brz_lnd_RBP_GPU
    ├─ Resolve: ops → brz_lnd_OPS_EXCEL_GPU
    ├─ Find join columns: Material ←→ PLANNING_SKU
    └─ Result: filters=[] ❌ (No filters extracted)
    ↓
SQL Generation
    ├─ Query Type: comparison_query
    ├─ Operation: IN
    ├─ Filters: [] (empty)
    └─ SQL: SELECT ... FROM ... INNER JOIN ... (NO WHERE CLAUSE)
    ↓
Execution
    ├─ Query executed successfully
    ├─ Records returned: 145 (ALL products, not filtered)
    └─ Result: ❌ WRONG (should be filtered)
```

---

## 🔧 The Fix

### Problem Location

**File**: `kg_builder/services/nl_query_parser.py`

**Lines**: 132-145 (in `_parse_with_llm` method)

```python
response = self.llm_service.create_chat_completion(
    messages=[...],
    max_tokens=500,
    temperature=0.3  # ❌ THIS IS THE PROBLEM
)
```

### Solution

Remove the `temperature=0.3` parameter. The model will use its default temperature (1).

**File**: `kg_builder/services/nl_query_parser.py`

**Change**:
```python
# BEFORE (Wrong)
response = self.llm_service.create_chat_completion(
    messages=[...],
    max_tokens=500,
    temperature=0.3  # ❌ Not supported by gpt-5
)

# AFTER (Correct)
response = self.llm_service.create_chat_completion(
    messages=[...],
    max_tokens=500
    # temperature removed - will use default
)
```

---

## 🧪 Expected Result After Fix

### Query
```
Show me all products in RBP which are in active OPS Excel
```

### Expected Logs
```
✓ Extracted filters from LLM: [{'column': 'Active_Inclusive', 'value': 'Active'}]
Parsed intent: ... filters=[{'column': 'Active_Inclusive', 'value': 'Active'}]
Adding filters to WHERE clause: [...]
WHERE clause (new): t.[Active_Inclusive] = 'Active'
```

### Expected SQL
```sql
SELECT DISTINCT TOP 1000 s.*
FROM [brz_lnd_RBP_GPU] s
INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
WHERE t.[Active_Inclusive] = 'Active'
```

### Expected Result
- ✅ Records returned: ~70 (only active products)
- ✅ WHERE clause present
- ✅ Filters applied correctly

---

## 📋 Summary

| Aspect | Before | After |
|--------|--------|-------|
| **LLM Call** | Fails with 400 error | Succeeds |
| **Parsing Method** | Rule-based (fallback) | LLM-based |
| **Filters Extracted** | No (empty) | Yes |
| **WHERE Clause** | Missing | Present |
| **Records Returned** | 145 (all) | ~70 (filtered) |
| **Accuracy** | ❌ Wrong | ✅ Correct |

---

## 🚀 Next Steps

1. **Remove temperature parameter** from LLM call
2. **Test the query** again
3. **Verify filters** are extracted
4. **Check WHERE clause** is in SQL
5. **Verify results** are filtered

---

**Status**: Root cause identified ✅ Ready to fix!

