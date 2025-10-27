# Testing: Invalid Column 'status' Fix

## 🧪 How to Test the Fix

### Test Environment Setup

1. **Start the backend**:
   ```bash
   cd d:\learning\dq-poc
   python -m uvicorn kg_builder.main:app --reload
   ```

2. **Start the web app**:
   ```bash
   cd web-app
   npm start
   ```

3. **Navigate to**: `http://localhost:3000/natural-language`

---

## 📋 Test Cases

### Test Case 1: Query with "active" keyword (Single Table)

**Query**:
```
Show me all active products in RBP GPU
```

**Expected Behavior**:
- ✅ No "Invalid column name 'status'" error
- ✅ Query executes successfully
- ✅ Returns records from brz_lnd_RBP_GPU
- ✅ No hardcoded status filter applied

**How to Test**:
1. Go to Natural Language → Execute Queries
2. Select Knowledge Graph: KG_101 (or any available)
3. Select Schemas: hana_material_master, brz_lnd_RBP_GPU, brz_lnd_OPS_EXCEL_GPU
4. Enter query: "Show me all active products in RBP GPU"
5. Click "Execute Queries"
6. ✅ Should execute without "Invalid column name" error

---

### Test Case 2: Query with "inactive" keyword

**Query**:
```
Show me inactive products in OPS Excel
```

**Expected Behavior**:
- ✅ No "Invalid column name 'status'" error
- ✅ Query executes successfully
- ✅ Returns records from brz_lnd_OPS_EXCEL_GPU
- ✅ No hardcoded status filter applied

---

### Test Case 3: Multi-table query with "active" keyword

**Query**:
```
Show me all products in RBP which are in active OPS Excel
```

**Expected Behavior**:
- ✅ No "Invalid column name 'status'" error
- ✅ Query executes successfully
- ✅ Joins brz_lnd_RBP_GPU with brz_lnd_OPS_EXCEL_GPU
- ✅ Returns matching records
- ✅ No hardcoded status filter applied

---

### Test Case 4: Query without status keywords (Control Test)

**Query**:
```
Show me all products in RBP which are in OPS Excel
```

**Expected Behavior**:
- ✅ Query executes successfully
- ✅ Returns matching records
- ✅ No filters applied

---

## 🔍 What to Look For

### In the Web UI

1. **No Error Messages**:
   - ❌ Should NOT see: "Invalid column name 'status'"
   - ❌ Should NOT see: "Comparison query requires join columns"

2. **Query Execution**:
   - ✅ Should see: "✅ SQL executed successfully"
   - ✅ Should see: Record count > 0 (if data exists)

3. **SQL Generated**:
   - ✅ Should NOT contain: `WHERE status = 'active'`
   - ✅ Should NOT contain: `WHERE status = 'inactive'`

### In the Backend Logs

Look for these log messages:

```
✅ GOOD:
- "🔧 Generating SQL for: Show me all active products in RBP GPU"
- "✅ SQL executed successfully"
- "📝 Query Definition: Show me all active products in RBP GPU"

❌ BAD (should NOT see):
- "Invalid column name 'status'"
- "Comparison query requires join columns to compare 'show' and 'brz_lnd_RBP_GPU'"
```

---

## 🐛 Troubleshooting

### If you still see "Invalid column name 'status'" error:

1. **Clear browser cache**:
   - Press `Ctrl+Shift+Delete`
   - Clear all cache
   - Refresh page

2. **Restart backend**:
   ```bash
   # Kill the running process
   # Restart with:
   python -m uvicorn kg_builder.main:app --reload
   ```

3. **Check file was modified**:
   ```bash
   # Verify the fix is in place:
   grep -n "Removed hardcoded" kg_builder/services/nl_query_parser.py
   # Should show line 219
   ```

4. **Check Python cache**:
   ```bash
   # Remove Python cache files
   find . -type d -name __pycache__ -exec rm -r {} +
   find . -type f -name "*.pyc" -delete
   ```

---

## ✅ Success Criteria

All of the following should be true:

- [ ] Query with "active" keyword executes without error
- [ ] Query with "inactive" keyword executes without error
- [ ] Multi-table query with "active" keyword executes without error
- [ ] No "Invalid column name 'status'" error appears
- [ ] SQL generated does NOT contain hardcoded "status" filter
- [ ] Records are returned (if data exists in tables)
- [ ] Backend logs show successful execution

---

## 📊 Expected Results

### Before Fix ❌
```
Query: "Show me all active products in RBP GPU"
Error: Invalid column name 'status'
Status: FAILED
```

### After Fix ✅
```
Query: "Show me all active products in RBP GPU"
Records: 1,234 (example)
Status: SUCCESS
```

---

## 🚀 Next Steps

Once all tests pass:

1. ✅ Verify with different queries
2. ✅ Test with different Knowledge Graphs
3. ✅ Test with different database types (if applicable)
4. ✅ Monitor production for any issues

---

**Test Status**: Ready to test ✅

