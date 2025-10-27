# Web App User Guide - Execute NL Queries

## 🎯 New Feature: Execute Queries Tab

The Natural Language page now has a new "Execute Queries" tab that allows you to execute natural language definitions as data queries and see the actual results.

---

## 📍 Where to Find It

1. **Open the web app**: `http://localhost:3000`
2. **Click "Natural Language"** in the left sidebar
3. **Click "Execute Queries"** tab (next to "Integrate Relationships")

---

## 🎬 Step-by-Step Guide

### Step 1: Select Knowledge Graph
```
┌─────────────────────────────────────┐
│ Knowledge Graph: [KG_101 ▼]         │
└─────────────────────────────────────┘
```
Choose the Knowledge Graph you want to query.

### Step 2: Select Schemas
```
┌─────────────────────────────────────┐
│ Select Schemas                      │
│ ┌──────────┐ ┌──────────┐          │
│ │newdqschema│ │ schema2  │          │
│ └──────────┘ └──────────┘          │
└─────────────────────────────────────┘
```
Click on schema chips to select them (they turn blue when selected).

### Step 3: Enter Query Definitions
```
┌─────────────────────────────────────┐
│ Query Definitions                   │
│ ┌─────────────────────────────────┐ │
│ │Show me all products in RBP GPU  │ │
│ │which are not in OPS Excel       │ │
│ └─────────────────────────────────┘ │
│ ┌─────────────────────────────────┐ │
│ │Show me all products in RBP GPU  │ │
│ │which are in active OPS Excel    │ │
│ └─────────────────────────────────┘ │
│ [+ Add Definition]                  │
└─────────────────────────────────────┘
```
Enter your natural language queries. You can add multiple definitions.

### Step 4: Configure Options
```
┌─────────────────────────────────────┐
│ Database Type: [mysql ▼]            │
│ Result Limit: [1000]                │
│ ☑ Use LLM for Enhanced Parsing      │
│ Minimum Confidence: [====●====] 0.70│
└─────────────────────────────────────┘
```
- **Database Type**: Select your database (MySQL, PostgreSQL, SQL Server, Oracle)
- **Result Limit**: Max records to return (1-10000)
- **LLM Parsing**: Enable for better parsing accuracy
- **Confidence**: Minimum confidence threshold (0-1)

### Step 5: Execute
```
┌─────────────────────────────────────┐
│ [▶ Execute Queries]                 │
└─────────────────────────────────────┘
```
Click the "Execute Queries" button to run your queries.

---

## 📊 Results Display

### Query Statistics
```
┌─────────────────────────────────────┐
│ Total Queries: 2                    │
│ Successful: 2                       │
│ Failed: 0                           │
│                                     │
│ Statistics                          │
│ Total Records: 1,768                │
│ Execution Time: 325.50ms            │
│ Avg Confidence: 0.85                │
└─────────────────────────────────────┘
```

### Per-Query Results
```
┌─────────────────────────────────────┐
│ Query 1: Show me all products in    │
│ RBP GPU which are not in OPS Excel  │
│                                     │
│ [Type: comparison_query]            │
│ [Operation: NOT_IN]                 │
│ [Confidence: 0.85]                  │
│                                     │
│ Records Found: 245                  │
│ Join Columns: material ← → planning_sku
│ Execution Time: 125.50ms            │
│                                     │
│ SQL:                                │
│ SELECT DISTINCT s.* FROM `rbp_gpu` s
│ LEFT JOIN `ops_excel` t ON          │
│ s.`material` = t.`planning_sku`     │
│ WHERE t.`planning_sku` IS NULL      │
│                                     │
│ Sample Records (first 5):           │
│ ┌──────────┬──────────┬──────────┐ │
│ │ material │ product  │ quantity │ │
│ ├──────────┼──────────┼──────────┤ │
│ │ MAT001   │ Product A│ 100      │ │
│ │ MAT002   │ Product B│ 200      │ │
│ │ MAT003   │ Product C│ 150      │ │
│ └──────────┴──────────┴──────────┘ │
└─────────────────────────────────────┘
```

---

## 💡 Example Queries

### Example 1: Find Missing Products
```
Definition: "Show me all products in RBP GPU which are not in OPS Excel"

Result:
- Query Type: comparison_query
- Operation: NOT_IN
- Records: 245 products
- SQL: LEFT JOIN with IS NULL
```

### Example 2: Find Active Products
```
Definition: "Show me all active products in RBP GPU"

Result:
- Query Type: filter_query
- Records: 1,523 products
- SQL: WHERE status = 'active'
```

### Example 3: Find Matching Products
```
Definition: "Show me all products in RBP GPU which are in OPS Excel"

Result:
- Query Type: comparison_query
- Operation: IN
- Records: 1,523 products
- SQL: INNER JOIN
```

---

## 🎨 Color Coding

### Confidence Scores
- 🟢 **Green** (≥ 0.80): High confidence
- 🟡 **Yellow** (< 0.80): Medium confidence
- 🔴 **Red**: Error

### Status Indicators
- ✅ **Green**: Success
- ⚠️ **Orange**: Warning
- ❌ **Red**: Error

---

## ⚙️ Configuration Tips

### For Best Results
1. **Enable LLM**: Check "Use LLM for Enhanced Parsing" for better accuracy
2. **Set Confidence**: Use 0.7-0.8 for balanced results
3. **Limit Results**: Set limit to 1000 for faster execution
4. **Select Correct DB**: Choose the database type matching your data

### For Large Datasets
1. **Reduce Limit**: Set to 500-1000 for faster results
2. **Use Filters**: Add status or date filters to narrow results
3. **Check Confidence**: Higher confidence = more accurate joins

---

## 🔍 Understanding Results

### Query Type
- **comparison_query**: Comparing two tables (NOT_IN, IN)
- **filter_query**: Filtering with WHERE conditions
- **data_query**: Simple SELECT
- **aggregation_query**: COUNT, SUM, AVG

### Operation
- **NOT_IN**: Products in A but not in B
- **IN**: Products in both A and B
- **EQUALS**: Exact match
- **CONTAINS**: Contains value
- **AGGREGATE**: Count/sum/average

### Join Columns
Shows which columns are used to join tables:
```
material ← → planning_sku
```
This means: `rbp_gpu.material` joins with `ops_excel.planning_sku`

### Confidence Score
- **0.95**: Perfect (LLM + KG relationship found)
- **0.85**: Very good (LLM parsing + KG join)
- **0.75**: Good (Rule-based parsing)
- **0.60**: Fair (Basic rule-based)

---

## 🐛 Troubleshooting

### Issue: "No records returned"
**Solution**: 
- Check table names are correct
- Verify filters are appropriate
- Check database connection

### Issue: "Low confidence score"
**Solution**:
- Enable LLM parsing
- Check Knowledge Graph relationships
- Verify table names match

### Issue: "Wrong join columns"
**Solution**:
- Check Knowledge Graph relationships
- Verify column names in tables
- Try different definitions

### Issue: "Query execution failed"
**Solution**:
- Check database is running
- Verify database credentials
- Check table names exist

---

## 📋 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Tab` | Move to next field |
| `Shift+Tab` | Move to previous field |
| `Enter` | Submit (when in button) |
| `Ctrl+A` | Select all text |

---

## 📱 Mobile Support

The Execute Queries tab is fully responsive:
- **Desktop**: Side-by-side layout (input left, results right)
- **Tablet**: Stacked layout
- **Mobile**: Full-width layout

---

## 💾 Exporting Results

### Copy SQL
1. Click on the SQL code block
2. Right-click and select "Copy"
3. Paste into your SQL editor

### Export Records
1. Right-click on the results table
2. Select "Copy table"
3. Paste into Excel/Google Sheets

---

## 🎓 Best Practices

1. **Start Simple**: Begin with simple queries, then add complexity
2. **Use Filters**: Add status/date filters to narrow results
3. **Check SQL**: Always review the generated SQL
4. **Verify Joins**: Confirm join columns are correct
5. **Test Limits**: Start with small limits, increase as needed

---

## 📞 Need Help?

1. **Check Documentation**: See `docs/NL_QUERY_EXECUTION_QUICK_START.md`
2. **Review Examples**: Check example queries above
3. **Check Logs**: Look at browser console for errors
4. **Contact Support**: Check error messages for details

---

## ✨ Summary

The "Execute Queries" tab allows you to:
✅ Execute natural language definitions as data queries
✅ See actual data results
✅ Review generated SQL
✅ Check join columns and confidence scores
✅ Export results for further analysis

**Start using it now!**

