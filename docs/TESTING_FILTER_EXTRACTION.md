# Testing: Filter Extraction & WHERE Clause Fix

## 🧪 How to Test

### Step 1: Start the Application

```bash
# Terminal 1: Start backend
cd d:\learning\dq-poc
python -m uvicorn kg_builder.main:app --reload

# Terminal 2: Start web app
cd web-app
npm start
```

### Step 2: Navigate to Natural Language Page

1. Open: `http://localhost:3000/natural-language`
2. Click: **Execute Queries** tab
3. Select: Knowledge Graph (e.g., KG_101)
4. Select: Schemas (hana_material_master, brz_lnd_RBP_GPU, brz_lnd_OPS_EXCEL_GPU)

---

## 📋 Test Cases

### Test Case 1: Multi-table with "active" filter ✅

**Query**:
```
Show me all products in RBP which are in active OPS Excel
```

**Expected Behavior**:
- ✅ SQL includes WHERE clause
- ✅ WHERE clause filters on target table (t)
- ✅ Column name is "Active_Inactive" (not "status")
- ✅ Value is "Active"

**Expected SQL**:
```sql
SELECT DISTINCT s.* 
FROM [brz_lnd_RBP_GPU] s
INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
WHERE t.[Active_Inactive] = 'Active'
```

**How to Verify**:
1. Enter the query
2. Click "Execute Queries"
3. Look at "Generated SQL" section
4. ✅ Should see `WHERE t.[Active_Inactive] = 'Active'`

---

### Test Case 2: Multi-table with "inactive" filter ✅

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

**How to Verify**:
1. Enter the query
2. Look at "Generated SQL"
3. ✅ Should see `WHERE t.[Active_Inactive] = 'Inactive'`

---

### Test Case 3: NOT_IN with filter ✅

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

**How to Verify**:
1. Enter the query
2. Look at "Generated SQL"
3. ✅ Should see both `WHERE t.[PLANNING_SKU] IS NULL` AND `AND t.[Active_Inactive] = 'Active'`

---

### Test Case 4: No filter (control) ✅

**Query**:
```
Show me all products in RBP which are in OPS Excel
```

**Expected SQL**:
```sql
SELECT DISTINCT s.* 
FROM [brz_lnd_RBP_GPU] s
INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
```

**How to Verify**:
1. Enter the query
2. Look at "Generated SQL"
3. ✅ Should NOT have WHERE clause (or only have join condition)

---

## 🔍 What to Look For

### In the Web UI

#### Generated SQL Section
- ✅ Should include WHERE clause for filtered queries
- ✅ Should reference target table alias "t"
- ✅ Should use correct column name (Active_Inactive, not status)
- ✅ Should use correct value (Active, Inactive)

#### Results Section
- ✅ Record count should be lower for filtered queries
- ✅ No errors about "Invalid column name"
- ✅ Query executes successfully

### In Backend Logs

Look for these messages:

```
✅ GOOD:
- "🔧 Generating SQL for: Show me all products in RBP which are in active OPS Excel"
- "✅ SQL executed successfully"
- "WHERE t.[Active_Inactive] = 'Active'" (in SQL output)

❌ BAD (should NOT see):
- "Invalid column name 'status'"
- "Invalid column name 'active'"
- SQL without WHERE clause (for filtered queries)
```

---

## 📊 Expected Results

### Before Fix ❌
```
Query: "Show me all products in RBP which are in active OPS Excel"
Generated SQL: SELECT ... FROM ... INNER JOIN ... (NO WHERE)
Records: 10,000 (all products, not filtered)
```

### After Fix ✅
```
Query: "Show me all products in RBP which are in active OPS Excel"
Generated SQL: SELECT ... FROM ... INNER JOIN ... WHERE t.[Active_Inactive] = 'Active'
Records: 5,000 (only active products)
```

---

## ✅ Success Criteria

All of the following should be true:

- [ ] Query with "active" keyword includes WHERE clause
- [ ] Query with "inactive" keyword includes WHERE clause
- [ ] WHERE clause references target table (t)
- [ ] Column name is correct (Active_Inactive, not status)
- [ ] Value is correct (Active, Inactive)
- [ ] NOT_IN queries include both join condition and filter
- [ ] No "Invalid column name" errors
- [ ] Record count is lower for filtered queries
- [ ] Queries execute successfully

---

## 🐛 Troubleshooting

### If WHERE clause is missing:

1. **Check LLM is enabled**:
   - In Execute Queries tab, check "Use LLM Parsing" checkbox
   - If unchecked, LLM won't extract filters

2. **Check backend logs**:
   - Look for "LLM Response" in logs
   - Should show filters being extracted

3. **Restart backend**:
   ```bash
   # Kill and restart
   python -m uvicorn kg_builder.main:app --reload
   ```

### If column name is wrong:

1. **Check schema**:
   - Verify actual column name in brz_lnd_OPS_EXCEL_GPU
   - Should be "Active_Inactive"

2. **Check LLM response**:
   - Look at backend logs for LLM response
   - Should show correct column name

---

## 🚀 Next Steps

Once all tests pass:

1. ✅ Test with different queries
2. ✅ Test with different Knowledge Graphs
3. ✅ Monitor for any issues
4. ✅ Deploy to production

---

**Test Status**: Ready to test ✅

