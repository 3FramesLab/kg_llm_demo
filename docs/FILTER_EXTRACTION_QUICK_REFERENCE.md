# Filter Extraction - Quick Reference

## 🎯 What Should Happen

### Query
```
Show me all products in RBP which are in active OPS Excel
```

### Expected Flow

```
1. PARSING
   ✓ Extracted filters from LLM: [{'column': 'Active_Inactive', 'value': 'Active'}]
   ✓ Parsed intent: filters=[{'column': 'Active_Inactive', 'value': 'Active'}]

2. SQL GENERATION
   ✓ Adding filters to WHERE clause: [{'column': 'Active_Inactive', 'value': 'Active'}]
   ✓ WHERE clause (new): t.[Active_Inclusive] = 'Active'

3. GENERATED SQL
   SELECT DISTINCT s.* 
   FROM [brz_lnd_RBP_GPU] s
   INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
   WHERE t.[Active_Inclusive] = 'Active'

4. EXECUTION
   ✓ Query executes successfully
   ✓ Returns only active products (filtered)
```

---

## 🔍 What to Check in Backend Logs

### ✅ GOOD Signs

```
✓ Extracted filters from LLM: [...]
✓ Parsed intent: ... filters=[...]
✓ Adding filters to WHERE clause: [...]
✓ WHERE clause (new): t.[Active_Inclusive] = 'Active'
```

### ❌ BAD Signs

```
No filters extracted from LLM response
Parsed intent: ... filters=[]
No filters to apply
```

---

## 🛠️ Quick Fixes

### If Filters Not Extracted

**Check 1**: Is LLM enabled?
```python
# In web UI, check "Use LLM Parsing" checkbox
```

**Check 2**: Is LLM API key configured?
```bash
# Check environment variable
echo $OPENAI_API_KEY
```

**Check 3**: Does LLM prompt include filter examples?
```python
# File: kg_builder/services/nl_query_parser.py
# Lines: 493-518
# Should include: "FILTER EXTRACTION GUIDE"
```

### If WHERE Clause Missing

**Check 1**: Are filters in the intent?
```
Look for: "Parsed intent: ... filters=[...]"
```

**Check 2**: Is SQL generator receiving filters?
```
Look for: "Filters: [...]" in SQL generation logs
```

**Check 3**: Is WHERE clause being added?
```
Look for: "Adding filters to WHERE clause"
```

### If Wrong Column Name

**Check 1**: What column name is in the WHERE clause?
```
Look for: "WHERE clause (new): t.[ColumnName]"
```

**Check 2**: Is it the correct column?
```
Should be: t.[Active_Inclusive]
Not: t.[status]
```

**Check 3**: Update LLM prompt with correct column names
```python
# File: kg_builder/services/nl_query_parser.py
# Lines: 493-518
# Add column name to examples
```

---

## 📊 Log Locations

### Parser Logs
```
File: kg_builder/services/nl_query_parser.py
Lines: 79, 117, 148, 276
```

### SQL Generator Logs
```
File: kg_builder/services/nl_sql_generator.py
Lines: 42-45, 125-137
```

---

## 🧪 Test Query

Use this query to test:
```
Show me all products in RBP which are in active OPS Excel
```

**Expected Result**:
- ✅ WHERE clause in SQL
- ✅ WHERE clause references target table (t)
- ✅ Column name is Active_Inclusive
- ✅ Value is Active
- ✅ Record count is lower than without filter

---

## 📋 Verification Checklist

- [ ] Backend logs show "✓ Extracted filters from LLM"
- [ ] Filters are in parsed intent
- [ ] SQL includes WHERE clause
- [ ] WHERE clause uses table alias "t"
- [ ] WHERE clause uses correct column name
- [ ] Query executes without errors
- [ ] Results are filtered (lower record count)

---

## 🚀 Next Steps

1. **Run test query** - Execute the test query above
2. **Check logs** - Look for the expected log messages
3. **Verify SQL** - Check generated SQL has WHERE clause
4. **Test results** - Verify results are filtered

---

**Status**: Ready to test ✅

