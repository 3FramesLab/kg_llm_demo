# Filter Extraction Debugging - Complete Setup ✅

## 🎯 What I Did

I've added comprehensive logging to help debug why filters aren't being extracted during Execute NL Queries.

---

## 📝 Changes Made

### 1. Enhanced Parser Logging

**File**: `kg_builder/services/nl_query_parser.py`

#### Change 1: Log filters in _parse_llm_response (Lines 241-289)
```python
# Extract filters
filters = data.get("filters", [])

# Log extracted filters
if filters:
    logger.info(f"✓ Extracted filters from LLM: {filters}")
else:
    logger.debug(f"No filters extracted from LLM response")
```

#### Change 2: Log filters in parse method (Line 117)
```python
logger.info(f"Parsed intent: query_type={intent.query_type}, source={intent.source_table}, target={intent.target_table}, join_cols={intent.join_columns}, filters={intent.filters}")
```

### 2. Enhanced SQL Generator Logging

**File**: `kg_builder/services/nl_sql_generator.py`

#### Change 1: Log filters in generate method (Lines 32-45)
```python
if intent.filters:
    logger.info(f"   Filters: {intent.filters}")
```

#### Change 2: Log WHERE clause in _generate_comparison_query (Lines 122-138)
```python
if intent.filters:
    logger.info(f"   Adding filters to WHERE clause: {intent.filters}")
    where_clause = self._build_where_clause(intent.filters, "t")
    if intent.operation == "NOT_IN":
        sql += f"\nAND {where_clause}"
        logger.info(f"   WHERE clause (appended): {where_clause}")
    else:
        sql += f"\nWHERE {where_clause}"
        logger.info(f"   WHERE clause (new): {where_clause}")
else:
    logger.debug(f"   No filters to apply")
```

---

## 🔍 What to Look For in Logs

### ✅ GOOD - Filters Extracted

```
INFO: Parsing definition: Show me all products in RBP which are in active OPS Excel
INFO: ✓ Extracted filters from LLM: [{'column': 'Active_Inclusive', 'value': 'Active'}]
INFO: Parsed intent: query_type=comparison_query, source=brz_lnd_rbp_gpu, target=brz_lnd_ops_excel_gpu, join_cols=[('Material', 'PLANNING_SKU')], filters=[{'column': 'Active_Inclusive', 'value': 'Active'}]
INFO: 🔧 Generating SQL for: Show me all products in RBP which are in active OPS Excel
INFO:    Query Type: comparison_query, Operation: IN
INFO:    Filters: [{'column': 'Active_Inclusive', 'value': 'Active'}]
INFO:    Adding filters to WHERE clause: [{'column': 'Active_Inclusive', 'value': 'Active'}]
INFO:    WHERE clause (new): t.[Active_Inclusive] = 'Active'
```

### ❌ BAD - Filters NOT Extracted

```
INFO: Parsing definition: Show me all products in RBP which are in active OPS Excel
INFO: No filters extracted from LLM response
INFO: Parsed intent: query_type=comparison_query, source=brz_lnd_rbp_gpu, target=brz_lnd_ops_excel_gpu, join_cols=[('Material', 'PLANNING_SKU')], filters=[]
INFO: 🔧 Generating SQL for: Show me all products in RBP which are in active OPS Excel
INFO:    Query Type: comparison_query, Operation: IN
INFO:    No filters to apply
```

---

## 🧪 How to Test

### Step 1: Run Backend with Logs

```bash
cd d:\learning\dq-poc
python -m uvicorn kg_builder.main:app --reload
```

### Step 2: Execute Query

1. Go to: `http://localhost:3000/natural-language`
2. Click: **Execute Queries** tab
3. Enter query: `Show me all products in RBP which are in active OPS Excel`
4. Click: **Execute Queries**

### Step 3: Check Backend Logs

Look for the log messages above. You should see:
- ✅ "✓ Extracted filters from LLM"
- ✅ "Adding filters to WHERE clause"
- ✅ "WHERE clause (new): t.[Active_Inclusive] = 'Active'"

### Step 4: Check Generated SQL

In the web UI, look at the "Generated SQL" section. Should show:
```sql
SELECT DISTINCT s.* 
FROM [brz_lnd_RBP_GPU] s
INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
WHERE t.[Active_Inclusive] = 'Active'
```

---

## 📊 Debugging Workflow

### If Filters NOT Extracted

1. **Check LLM is enabled**
   - In web UI, verify "Use LLM Parsing" checkbox is checked
   - In backend logs, look for "LLM Response:"

2. **Check LLM prompt**
   - File: `kg_builder/services/nl_query_parser.py` lines 493-518
   - Should include "FILTER EXTRACTION GUIDE"
   - Should show filter examples

3. **Check LLM API key**
   - Verify OPENAI_API_KEY environment variable is set
   - Check LLM service is enabled

### If WHERE Clause NOT Generated

1. **Verify filters are extracted**
   - Look for "✓ Extracted filters from LLM"
   - Check parsed intent has filters

2. **Check SQL generator**
   - File: `kg_builder/services/nl_sql_generator.py` lines 122-138
   - Should add WHERE clause if filters present

3. **Check table alias**
   - WHERE clause should use "t" (target table)
   - Not "s" (source table)

---

## 📁 Files Modified

| File | Lines | Change |
|------|-------|--------|
| `kg_builder/services/nl_query_parser.py` | 117, 241-289 | Added filter logging |
| `kg_builder/services/nl_sql_generator.py` | 32-45, 122-138 | Added WHERE clause logging |

---

## 📚 Documentation Created

1. **`DEBUGGING_FILTER_EXTRACTION.md`**
   - Comprehensive debugging guide
   - Step-by-step troubleshooting
   - Common issues and solutions

2. **`FILTER_EXTRACTION_QUICK_REFERENCE.md`**
   - Quick reference for what to look for
   - Expected log messages
   - Quick fixes

3. **`FILTER_EXTRACTION_DEBUGGING_COMPLETE.md`**
   - This file
   - Summary of changes
   - Testing workflow

---

## 🚀 Next Steps

1. **Test the query** - Run the test query and check logs
2. **Verify filters** - Look for "✓ Extracted filters from LLM"
3. **Check SQL** - Verify WHERE clause is in generated SQL
4. **Verify results** - Check results are filtered correctly

---

## 💡 Key Points

✅ **Logging Added**: Comprehensive logging at every step

✅ **Easy Debugging**: Clear log messages show what's happening

✅ **Quick Reference**: Quick reference guide for common issues

✅ **Troubleshooting**: Step-by-step debugging workflow

---

**Status**: ✅ **DEBUGGING SETUP COMPLETE**

Now you can easily see what's happening with filter extraction!

