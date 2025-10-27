# 🔴 CRITICAL ISSUE: NL Definitions Processing

## The Problem

You've identified a **critical architectural issue** with how NL definitions are being processed:

### Your Example
```json
{
  "kg_name": "KG_101",
  "schemas": ["newdqschema"],
  "definitions": [
    "Show me all the products in RBP GPU which are not in OPS Excel",
    "Show me all the products in RBP GPU which are in active OPS Excel"
  ],
  "use_llm": true,
  "min_confidence": 0.7
}
```

### What's Happening (WRONG)
1. **Each definition is treated as a RELATIONSHIP definition**
   - System tries to parse: "Show me all products in RBP GPU which are not in OPS Excel"
   - Looks for: source_table, target_table, relationship_type
   - Result: Confused/incorrect parsing

2. **Definitions are NOT converted to separate queries**
   - They're added to the Knowledge Graph as relationships
   - Not executed as SQL queries
   - Not used to find data mismatches

3. **KG relationships are NOT used to understand context**
   - System doesn't leverage existing KG relationships
   - Doesn't understand that RBP GPU and OPS Excel are related
   - Doesn't use join paths from KG

---

## What SHOULD Happen

### For Each Definition
```
Definition 1: "Show me all products in RBP GPU which are not in OPS Excel"
    ↓
Parse as DATA QUERY (not relationship)
    ↓
Understand: 
  - Source table: RBP GPU
  - Target table: OPS Excel
  - Operation: LEFT JOIN with NOT EXISTS
  - Join path: Use KG relationships to find join columns
    ↓
Generate SQL:
  SELECT DISTINCT r.* 
  FROM rbp_gpu r
  LEFT JOIN ops_excel o ON r.material = o.planning_sku
  WHERE o.planning_sku IS NULL
    ↓
Execute query
    ↓
Return results

Definition 2: "Show me all products in RBP GPU which are in active OPS Excel"
    ↓
Parse as DATA QUERY
    ↓
Understand:
  - Source table: RBP GPU
  - Target table: OPS Excel
  - Filter: active status
  - Operation: INNER JOIN
    ↓
Generate SQL:
  SELECT DISTINCT r.* 
  FROM rbp_gpu r
  INNER JOIN ops_excel o ON r.material = o.planning_sku
  WHERE o.status = 'active'
    ↓
Execute query
    ↓
Return results
```

---

## Current Architecture vs. Needed Architecture

### Current (WRONG)
```
NL Definition
    ↓
Parse as Relationship Definition
    ↓
Extract: source_table, target_table, relationship_type
    ↓
Add to Knowledge Graph
    ↓
(No query execution)
    ↓
(No data results)
```

### Needed (CORRECT)
```
NL Definition
    ↓
Classify: Is this a RELATIONSHIP or a DATA QUERY?
    ↓
If RELATIONSHIP:
  Parse as relationship definition
  Add to KG
    ↓
If DATA QUERY:
  Parse as query intent
  Use KG to find join paths
  Generate SQL for each definition
  Execute SQL
  Return results
```

---

## Key Issues to Fix

### Issue 1: Definition Classification
**Current**: All definitions treated as relationships
**Needed**: Classify each definition as:
- `RELATIONSHIP` - "Products are supplied by Vendors"
- `DATA_QUERY` - "Show me products not in OPS Excel"
- `FILTER_QUERY` - "Show me active products"
- `COMPARISON_QUERY` - "Show me differences between tables"

### Issue 2: KG Relationship Usage
**Current**: KG relationships not used during parsing
**Needed**: 
- Load existing KG relationships
- Use them to understand table connections
- Infer join columns from KG
- Build join paths automatically

### Issue 3: SQL Generation
**Current**: No SQL generation from definitions
**Needed**:
- Generate SQL for each data query definition
- Support different query types:
  - Set difference: `LEFT JOIN ... WHERE IS NULL`
  - Set intersection: `INNER JOIN`
  - Filtered join: `INNER JOIN ... WHERE condition`
  - Multi-table: Chain joins using KG paths

### Issue 4: Query Execution
**Current**: Definitions added to KG, not executed
**Needed**:
- Execute generated SQL
- Return actual data results
- Show matched/unmatched records
- Provide statistics

---

## Example: How It Should Work

### Input
```json
{
  "kg_name": "KG_101",
  "schemas": ["newdqschema"],
  "definitions": [
    "Show me all the products in RBP GPU which are not in OPS Excel",
    "Show me all the products in RBP GPU which are in active OPS Excel"
  ]
}
```

### Processing

**Step 1: Load KG**
```
KG has relationships:
- RBP GPU.material ←→ OPS Excel.planning_sku (MATCHES)
- RBP GPU.material ←→ SKU LIFNR.material (MATCHES)
```

**Step 2: Classify Definitions**
```
Definition 1: DATA_QUERY (Set Difference)
Definition 2: DATA_QUERY (Filtered Join)
```

**Step 3: Parse Each Definition**
```
Definition 1:
  - Source: RBP GPU
  - Target: OPS Excel
  - Operation: NOT IN
  - Join column: material = planning_sku (from KG)

Definition 2:
  - Source: RBP GPU
  - Target: OPS Excel
  - Filter: active status
  - Operation: IN
  - Join column: material = planning_sku (from KG)
```

**Step 4: Generate SQL**
```sql
-- Definition 1
SELECT DISTINCT r.* 
FROM rbp_gpu r
LEFT JOIN ops_excel o ON r.material = o.planning_sku
WHERE o.planning_sku IS NULL

-- Definition 2
SELECT DISTINCT r.* 
FROM rbp_gpu r
INNER JOIN ops_excel o ON r.material = o.planning_sku
WHERE o.status = 'active'
```

**Step 5: Execute & Return Results**
```json
{
  "definition_1": {
    "query": "SELECT DISTINCT r.* FROM rbp_gpu r LEFT JOIN ops_excel o...",
    "matched_count": 0,
    "unmatched_count": 245,
    "records": [...]
  },
  "definition_2": {
    "query": "SELECT DISTINCT r.* FROM rbp_gpu r INNER JOIN ops_excel o...",
    "matched_count": 1523,
    "records": [...]
  }
}
```

---

## Summary

### What's Wrong
1. ❌ Definitions treated as relationships, not queries
2. ❌ No separate query generation per definition
3. ❌ KG relationships not used for join path inference
4. ❌ No SQL execution
5. ❌ No data results returned

### What's Needed
1. ✅ Classify definitions as relationships vs. queries
2. ✅ Generate separate SQL for each query definition
3. ✅ Use KG relationships to infer join columns
4. ✅ Execute SQL and return results
5. ✅ Support multiple query types (difference, intersection, filtered, etc.)

### Impact
- **Current**: Definitions are added to KG but don't produce actionable results
- **Needed**: Definitions generate executable queries with actual data insights


