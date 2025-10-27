# Natural Language Page - Workflow Clarification

## 🎯 Quick Answer

**NO, you do NOT need to run "Integrate Relationships" first to use "Execute Queries".**

These are **two independent workflows** with different purposes:

---

## 📊 Two Independent Tabs

### Tab 1: "Integrate Relationships" 
**Purpose**: Add relationship definitions to the Knowledge Graph

**Workflow**:
1. Define relationships in natural language
2. System parses them and adds to KG
3. Generate reconciliation rules from relationships
4. Rules are stored in the system

**Output**: Reconciliation ruleset (for rule-based reconciliation)

**Example**:
```
Definition: "Products are supplied by Vendors"
↓
Added to Knowledge Graph as relationship
↓
Generates rule: "IF product has vendor_id THEN it's valid"
```

---

### Tab 2: "Execute Queries" 
**Purpose**: Execute natural language definitions as data queries

**Workflow**:
1. Define data queries in natural language
2. System parses them and generates SQL
3. Execute SQL against database
4. Return actual data results

**Output**: Query results with actual data (for data reconciliation)

**Example**:
```
Definition: "Show me all products in RBP GPU which are not in OPS Excel"
↓
Generates SQL: SELECT ... LEFT JOIN ... WHERE IS NULL
↓
Returns 245 products that are missing
```

---

## 🔄 Relationship Between Tabs

```
┌─────────────────────────────────────────────────────────┐
│         Natural Language Page                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐    ┌──────────────────┐          │
│  │ Integrate        │    │ Execute          │          │
│  │ Relationships    │    │ Queries          │          │
│  │                  │    │                  │          │
│  │ Purpose:         │    │ Purpose:         │          │
│  │ Add to KG        │    │ Query Data       │          │
│  │ Generate Rules   │    │ Get Results      │          │
│  │                  │    │                  │          │
│  │ Output:          │    │ Output:          │          │
│  │ Ruleset          │    │ Data Records     │          │
│  └──────────────────┘    └──────────────────┘          │
│         ↓                        ↓                      │
│    Independent           Independent                   │
│    (No dependency)       (No dependency)               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ When to Use Each Tab

### Use "Integrate Relationships" When:
- ✅ You want to define business relationships
- ✅ You want to generate reconciliation rules
- ✅ You want to add knowledge to the Knowledge Graph
- ✅ You want rule-based reconciliation

**Example Use Cases**:
- "Products are supplied by Vendors"
- "Orders contain Products"
- "Customers have Addresses"

---

### Use "Execute Queries" When:
- ✅ You want to find specific data
- ✅ You want to compare two datasets
- ✅ You want to identify missing or extra records
- ✅ You want actual data results (not rules)

**Example Use Cases**:
- "Show me products in RBP GPU not in OPS Excel"
- "Show me active products in both systems"
- "Count products by category"

---

## 🎓 Real-World Scenario

### Scenario: Data Reconciliation Project

**Step 1: Define Relationships** (Optional)
```
Tab: "Integrate Relationships"
Definitions:
- "Products are identified by SKU"
- "Products belong to Categories"
- "Vendors supply Products"

Output: Reconciliation rules for validation
```

**Step 2: Execute Queries** (Independent)
```
Tab: "Execute Queries"
Definitions:
- "Show me all products in RBP GPU which are not in OPS Excel"
- "Show me all products in RBP GPU which are in active OPS Excel"

Output: Actual data - 245 missing products, 1,523 matching products
```

**Both steps are independent!**
- You can do Step 1 without Step 2
- You can do Step 2 without Step 1
- You can do both in any order

---

## 🔗 How They Work Together (Optional)

While independent, they can complement each other:

```
Integrate Relationships
    ↓
    Creates rules: "Products must have valid SKU"
    ↓
Execute Queries
    ↓
    Finds: "245 products with invalid SKU"
    ↓
    Validates against rules
```

But this is **optional** - you can use either tab alone.

---

## 📋 Knowledge Graph Usage

### In "Integrate Relationships" Tab:
- Adds new relationships to KG
- Uses KG to generate rules
- Modifies the Knowledge Graph

### In "Execute Queries" Tab:
- **Reads** existing KG relationships
- Uses KG to infer join columns
- Does NOT modify the Knowledge Graph

**Key Point**: "Execute Queries" uses the KG to understand how tables are related, but doesn't require you to have added relationships first. It can infer joins from existing KG data.

---

## 🎯 Recommended Workflow

### Option 1: Just Execute Queries (Simplest)
```
1. Go to "Execute Queries" tab
2. Select KG and schemas
3. Enter your data query definitions
4. Click "Execute Queries"
5. Get results
```

**No need to integrate relationships first!**

---

### Option 2: Both Tabs (Complete)
```
1. Go to "Integrate Relationships" tab
2. Define business relationships
3. Generate reconciliation rules
4. Go to "Execute Queries" tab
5. Execute data queries
6. Compare results with rules
```

**Both tabs work together for complete reconciliation**

---

### Option 3: Just Integrate Relationships
```
1. Go to "Integrate Relationships" tab
2. Define business relationships
3. Generate reconciliation rules
4. Use rules for validation
```

**No need to execute queries if you only want rules**

---

## ❓ FAQ

### Q: Do I need to integrate relationships before executing queries?
**A**: No. They are independent. You can execute queries without integrating relationships.

### Q: Will executing queries modify the Knowledge Graph?
**A**: No. Execute Queries only reads the KG, it doesn't modify it.

### Q: Can I use Execute Queries without a Knowledge Graph?
**A**: Yes, but the system won't be able to infer join columns automatically. You'll need to specify them in your query definitions.

### Q: What if I integrate relationships and then execute queries?
**A**: The Execute Queries tab will use the relationships you added to better understand table joins and infer join columns more accurately.

### Q: Can I execute the same query multiple times?
**A**: Yes. Execute Queries doesn't store anything - it just runs the query and returns results.

### Q: Do I need to select the same schemas in both tabs?
**A**: No. Each tab is independent. You can select different schemas in each tab.

---

## 🚀 Quick Start

### Just Want to Execute Queries?
```
1. Click "Execute Queries" tab
2. Select KG: "KG_101"
3. Select Schemas: "newdqschema"
4. Enter Definition: "Show me all products in RBP GPU which are not in OPS Excel"
5. Click "Execute Queries"
6. View results!
```

**That's it! No need to integrate relationships first.**

---

## 📊 Comparison Table

| Feature | Integrate Relationships | Execute Queries |
|---------|------------------------|-----------------|
| Purpose | Add to KG, Generate Rules | Query Data |
| Modifies KG | Yes | No |
| Returns Data | No (returns rules) | Yes (returns records) |
| Requires KG | No | No (but helpful) |
| Requires Relationships | No | No |
| Independent | Yes | Yes |
| Can run first | Yes | Yes |
| Can run alone | Yes | Yes |

---

## ✨ Summary

**The two tabs are completely independent:**

- ✅ Use "Integrate Relationships" to add knowledge and generate rules
- ✅ Use "Execute Queries" to find and compare data
- ✅ You don't need to run one before the other
- ✅ You can use either tab alone or both together
- ✅ Each tab serves a different purpose

**Choose based on what you need:**
- Need rules? → Use "Integrate Relationships"
- Need data? → Use "Execute Queries"
- Need both? → Use both tabs (in any order)

---

## 🎯 Bottom Line

**NO, you do NOT need to integrate relationships first.**

Just go to "Execute Queries" tab and start executing your data queries!

