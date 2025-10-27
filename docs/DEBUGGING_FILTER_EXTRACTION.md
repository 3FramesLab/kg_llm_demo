# Debugging Filter Extraction Issues

## 🔍 Problem

Filters are not being extracted during Execute NL Queries, so WHERE clauses are missing from generated SQL.

---

## 📊 Debugging Steps

### Step 1: Check Backend Logs

When you execute a query, look for these log messages:

#### ✅ GOOD - Filters Extracted

```
INFO: Parsing definition: Show me all products in RBP which are in active OPS Excel
INFO: ✓ Extracted filters from LLM: [{'column': 'Active_Inactive', 'value': 'Active'}]
INFO: Parsed intent: query_type=comparison_query, source=brz_lnd_rbp_gpu, target=brz_lnd_ops_excel_gpu, join_cols=[('Material', 'PLANNING_SKU')], filters=[{'column': 'Active_Inactive', 'value': 'Active'}]
INFO: 🔧 Generating SQL for: Show me all products in RBP which are in active OPS Excel
INFO:    Query Type: comparison_query, Operation: IN
INFO:    Filters: [{'column': 'Active_Inactive', 'value': 'Active'}]
INFO:    Adding filters to WHERE clause: [{'column': 'Active_Inactive', 'value': 'Active'}]
INFO:    WHERE clause (new): t.[Active_Inactive] = 'Active'
```

#### ❌ BAD - Filters NOT Extracted

```
INFO: Parsing definition: Show me all products in RBP which are in active OPS Excel
INFO: No filters extracted from LLM response
INFO: Parsed intent: query_type=comparison_query, source=brz_lnd_rbp_gpu, target=brz_lnd_ops_excel_gpu, join_cols=[('Material', 'PLANNING_SKU')], filters=[]
INFO: 🔧 Generating SQL for: Show me all products in RBP which are in active OPS Excel
INFO:    Query Type: comparison_query, Operation: IN
INFO:    No filters to apply
```

---

### Step 2: Check LLM Response

If filters are not being extracted, check what the LLM is returning:

#### Enable Debug Logging

In your backend, set log level to DEBUG:

```python
# In kg_builder/main.py or your logging config
logging.basicConfig(level=logging.DEBUG)
```

#### Look for LLM Response

```
DEBUG: LLM Parsing Prompt:
You are an expert data analyst. Parse this natural language query...
[Full prompt shown]

DEBUG: LLM Response:
{
  "definition": "Show me all products in RBP which are in active OPS Excel",
  "source_table": "brz_lnd_RBP_GPU",
  "target_table": "brz_lnd_OPS_EXCEL_GPU",
  "operation": "IN",
  "filters": [{"column": "Active_Inactive", "value": "Active"}],
  "confidence": 0.85,
  "reasoning": "..."
}
```

---

### Step 3: Verify LLM is Enabled

Check if LLM parsing is actually being used:

```python
# In nl_query_parser.py line 86
if use_llm and self.llm_service.is_enabled():
    intent = self._parse_with_llm(definition, def_type, operation)
else:
    intent = self._parse_rule_based(definition, def_type, operation)
```

**Check**:
- ✅ Is `use_llm=true` being passed from the frontend?
- ✅ Is `self.llm_service.is_enabled()` returning True?
- ✅ Is the LLM API key configured?

---

### Step 4: Check LLM Prompt

The LLM prompt is critical. It should include filter extraction examples.

**Location**: `kg_builder/services/nl_query_parser.py` lines 493-518

**Check**:
- ✅ Does the prompt include "FILTER EXTRACTION GUIDE"?
- ✅ Does the prompt show examples with filters extracted?
- ✅ Does the prompt mention "Active_Inactive" column?

**Example Good Prompt**:
```
FILTER EXTRACTION GUIDE:
- "active" or "inactive" → Look for columns like: Active_Inactive, Status, State, Flag, etc.
- For target table in multi-table queries, check its columns for status-related fields

EXAMPLES:
- Query: "Show me products in RBP which are in active OPS Excel"
  → filters: [{"column": "Active_Inactive", "value": "Active"}]
```

---

### Step 5: Check SQL Generation

If filters are extracted but WHERE clause is missing:

**Location**: `kg_builder/services/nl_sql_generator.py` lines 122-138

**Check**:
- ✅ Is `intent.filters` populated?
- ✅ Is the WHERE clause being added?
- ✅ Is the table alias correct ("t" for target)?

**Expected Log**:
```
INFO:    Adding filters to WHERE clause: [{'column': 'Active_Inactive', 'value': 'Active'}]
INFO:    WHERE clause (new): t.[Active_Inclusive] = 'Active'
```

---

## 🐛 Common Issues & Solutions

### Issue 1: LLM Not Extracting Filters

**Symptom**: `No filters extracted from LLM response`

**Causes**:
1. LLM prompt doesn't show filter examples
2. LLM API key not configured
3. LLM service disabled

**Solution**:
1. Check prompt includes filter extraction guide
2. Verify LLM API key in environment
3. Check `llm_service.is_enabled()` returns True

### Issue 2: Filters Extracted but WHERE Clause Missing

**Symptom**: 
- Logs show: `✓ Extracted filters from LLM: [...]`
- But SQL has no WHERE clause

**Causes**:
1. SQL generator not checking filters
2. Filters applied to wrong table
3. WHERE clause not being appended

**Solution**:
1. Check `nl_sql_generator.py` lines 122-138
2. Verify table alias is "t" (target)
3. Check WHERE clause is being appended

### Issue 3: Wrong Column Name in WHERE Clause

**Symptom**: 
- SQL has WHERE clause but with wrong column name
- Error: "Invalid column name 'status'"

**Causes**:
1. LLM using generic column name instead of actual
2. Schema not provided to LLM
3. LLM prompt not showing correct column names

**Solution**:
1. Update LLM prompt with actual column names
2. Ensure schema info is passed to parser
3. Check LLM response for correct column name

---

## 🧪 Testing Filter Extraction

### Test 1: Simple Filter Query

**Query**:
```
Show me all products in RBP which are in active OPS Excel
```

**Expected Logs**:
```
✓ Extracted filters from LLM: [{'column': 'Active_Inactive', 'value': 'Active'}]
WHERE clause (new): t.[Active_Inclusive] = 'Active'
```

**Expected SQL**:
```sql
SELECT DISTINCT s.* 
FROM [brz_lnd_RBP_GPU] s
INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
WHERE t.[Active_Inclusive] = 'Active'
```

### Test 2: Query Without Filter

**Query**:
```
Show me all products in RBP which are in OPS Excel
```

**Expected Logs**:
```
No filters extracted from LLM response
No filters to apply
```

**Expected SQL**:
```sql
SELECT DISTINCT s.* 
FROM [brz_lnd_RBP_GPU] s
INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
```

---

## 📋 Checklist

- [ ] Backend logs show "✓ Extracted filters from LLM"
- [ ] Filters are in the parsed intent
- [ ] SQL generator receives filters
- [ ] WHERE clause is added to SQL
- [ ] WHERE clause uses correct table alias ("t")
- [ ] WHERE clause uses correct column name
- [ ] WHERE clause uses correct value
- [ ] Query executes without errors
- [ ] Results are filtered correctly

---

## 🚀 Next Steps

1. **Check logs** - Run query and check backend logs
2. **Verify LLM** - Ensure LLM is enabled and API key configured
3. **Test prompt** - Verify LLM prompt includes filter examples
4. **Test SQL** - Check generated SQL has WHERE clause
5. **Test execution** - Run query and verify results are filtered

---

**Status**: Ready to debug ✅

