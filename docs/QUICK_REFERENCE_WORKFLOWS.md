# Quick Reference - Natural Language Page Workflows

## 🎯 TL;DR

**NO, you do NOT need to integrate relationships first to execute queries.**

The two tabs are **completely independent**.

---

## 📋 Quick Comparison

| Aspect | Integrate Relationships | Execute Queries |
|--------|------------------------|-----------------|
| **What it does** | Adds relationships to KG | Executes data queries |
| **Output** | Reconciliation rules | Data records |
| **Modifies KG** | Yes | No |
| **Requires other tab** | No | No |
| **Use when** | You want rules | You want data |

---

## 🚀 Three Ways to Use the Page

### Option 1: Just Execute Queries ⭐ (Most Common)
```
1. Click "Execute Queries" tab
2. Select KG and schemas
3. Enter query definitions
4. Click "Execute Queries"
5. Get results!

✅ No need to integrate relationships first
✅ Fastest way to get data
✅ Perfect for data reconciliation
```

### Option 2: Just Integrate Relationships
```
1. Click "Integrate Relationships" tab
2. Define relationships
3. Click "Integrate & Generate Rules"
4. Get reconciliation ruleset

✅ No need to execute queries
✅ Perfect for rule-based reconciliation
✅ Adds knowledge to system
```

### Option 3: Use Both Tabs
```
1. Integrate relationships (optional)
2. Execute queries (independent)
3. Compare results with rules

✅ Complete reconciliation workflow
✅ Can do in any order
✅ Each tab is independent
```

---

## 💡 When to Use Each Tab

### Use "Integrate Relationships" When:
- You want to define business relationships
- You want to generate reconciliation rules
- You want to add knowledge to the Knowledge Graph
- You want rule-based validation

**Examples**:
- "Products are supplied by Vendors"
- "Orders contain Products"
- "Customers have Addresses"

### Use "Execute Queries" When:
- You want to find specific data
- You want to compare two datasets
- You want to identify missing records
- You want actual data results

**Examples**:
- "Show me products in RBP GPU not in OPS Excel"
- "Show me active products in both systems"
- "Count products by category"

---

## 🎓 Real Examples

### Example 1: Find Missing Products
```
Tab: Execute Queries
Definition: "Show me all products in RBP GPU which are not in OPS Excel"

Result: 245 products found
SQL: SELECT ... LEFT JOIN ... WHERE IS NULL

✅ No need to integrate relationships first!
```

### Example 2: Find Matching Products
```
Tab: Execute Queries
Definition: "Show me all products in RBP GPU which are in OPS Excel"

Result: 1,523 products found
SQL: SELECT ... INNER JOIN ...

✅ No need to integrate relationships first!
```

### Example 3: Define Business Rules
```
Tab: Integrate Relationships
Definition: "Products are identified by SKU"

Result: Rule added to system
Ruleset: "IF product has SKU THEN it's valid"

✅ Independent from Execute Queries
```

---

## ❓ Common Questions

**Q: Do I need to integrate relationships before executing queries?**
A: No. They are completely independent.

**Q: Will executing queries modify the Knowledge Graph?**
A: No. Execute Queries only reads the KG.

**Q: Can I execute queries without integrating relationships?**
A: Yes. Execute Queries works independently.

**Q: What if I integrate relationships first?**
A: Execute Queries will use them to better infer join columns, but it's not required.

**Q: Can I use just Execute Queries?**
A: Yes. That's the most common use case.

**Q: Can I use just Integrate Relationships?**
A: Yes. That's also a valid use case.

---

## 🎯 Recommended Starting Point

### If you're new:
```
Start with "Execute Queries" tab
- Simpler to understand
- Immediate results
- No dependencies
```

### If you want complete reconciliation:
```
Use both tabs
- Integrate relationships for rules
- Execute queries for data
- Compare results
```

---

## 📊 Workflow Diagram

```
Natural Language Page
│
├─ Tab 1: Integrate Relationships
│  ├─ Define relationships
│  ├─ Add to KG
│  └─ Generate rules
│  
└─ Tab 2: Execute Queries
   ├─ Define data queries
   ├─ Generate SQL
   └─ Return data results

⚠️ NO DEPENDENCY - Use either or both!
```

---

## ✨ Key Takeaways

1. **Two independent tabs** - No dependency between them
2. **Use Execute Queries alone** - Most common use case
3. **Use Integrate Relationships alone** - Also valid
4. **Use both together** - For complete reconciliation
5. **Any order** - Do them in any order you want

---

## 🚀 Get Started Now

### To Execute Queries:
```
1. Go to Natural Language page
2. Click "Execute Queries" tab
3. Select KG: "KG_101"
4. Select Schemas: "newdqschema"
5. Enter Definition: "Show me all products in RBP GPU which are not in OPS Excel"
6. Click "Execute Queries"
7. View results!
```

**That's it! No need to integrate relationships first.**

---

## 📞 Summary

**The answer to your question:**

> "Do I need to first run integrates relationships and then execute queries?"

**NO.** You do NOT need to integrate relationships first. The two tabs are completely independent. You can:

- ✅ Use Execute Queries alone
- ✅ Use Integrate Relationships alone
- ✅ Use both in any order

Choose based on what you need!

