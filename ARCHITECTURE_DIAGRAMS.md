# Architecture Diagrams

## 1. Current Architecture (Python-Based)

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INPUT (NL Definition)                   │
│              "Show products in RBP not in OPS"                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│         NLQueryClassifier (100% Python - Hardcoded)             │
│  - Keyword matching: "not in" → COMPARISON_QUERY                │
│  - Operation: "not in" → NOT_IN                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              NLQueryParser (Hybrid - Python + LLM)              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ LLM Parsing (if enabled)                                │   │
│  │ - Extract: source_table, target_table, filters          │   │
│  │ - Extract: additional columns                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Python-Based Join Finding (BFS Algorithm)               │   │
│  │ - Search KG for relationships                           │   │
│  │ - Find join columns: Material ←→ PLANNING_SKU           │   │
│  │ - Find join path: RBP → OPS → HANA                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Output: QueryIntent {                                         │
│    source_table: "brz_lnd_RBP_GPU"                             │
│    target_table: "brz_lnd_OPS_EXCEL_GPU"                       │
│    join_columns: [("Material", "PLANNING_SKU")]                │
│    operation: "NOT_IN"                                         │
│  }                                                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│        NLSQLGenerator (100% Python - Hardcoded Templates)       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ _generate_comparison_query()                            │   │
│  │ - Hardcoded: SELECT DISTINCT s.*                        │   │
│  │ - Hardcoded: FROM source s                              │   │
│  │ - Hardcoded: LEFT JOIN target t ON ...                  │   │
│  │ - Hardcoded: WHERE t.col IS NULL                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ _build_where_clause()                                   │   │
│  │ - Only supports: column = value                         │   │
│  │ - No: >, <, LIKE, IN, BETWEEN, IS NULL                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ _get_join_condition()                                   │   │
│  │ - Searches KG for relationships                         │   │
│  │ - Extracts join columns                                 │   │
│  │ - Constructs: alias1.col1 = alias2.col2                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Output: SQL String                                            │
│  SELECT DISTINCT s.* FROM `brz_lnd_RBP_GPU` s                 │
│  LEFT JOIN `brz_lnd_OPS_EXCEL_GPU` t                           │
│  ON s.`Material` = t.`PLANNING_SKU`                            │
│  WHERE t.`PLANNING_SKU` IS NULL                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              NLQueryExecutor (Python)                           │
│  - Execute SQL against database                                │
│  - Return results                                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUERY RESULTS                                │
│              [Product1, Product2, ...]                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Proposed Architecture (LLM-Based)

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INPUT (NL Definition)                   │
│              "Show products in RBP not in OPS"                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│         NLQueryClassifier (100% Python - Hardcoded)             │
│  - Keyword matching: "not in" → COMPARISON_QUERY                │
│  - Operation: "not in" → NOT_IN                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              NLQueryParser (Hybrid - Python + LLM)              │
│  - Same as current (no changes needed)                          │
│  - Output: QueryIntent                                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│        NLSQLGenerator (NEW - LLM-Based with Fallback)           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ LLMSQLGenerator (NEW)                                   │   │
│  │ - Pass QueryIntent + KG context to LLM                  │   │
│  │ - LLM generates complete SQL                            │   │
│  │ - Validate SQL (schema check)                           │   │
│  │ - Return SQL                                            │   │
│  │                                                         │   │
│  │ Prompt:                                                 │   │
│  │ "Generate SQL for:                                      │   │
│  │  - Query Type: comparison_query                         │   │
│  │  - Source: brz_lnd_RBP_GPU                              │   │
│  │  - Target: brz_lnd_OPS_EXCEL_GPU                        │   │
│  │  - Operation: NOT_IN                                    │   │
│  │  - KG Relationships: [...]                              │   │
│  │  - Available columns: [...]"                            │   │
│  │                                                         │   │
│  │ LLM Response:                                           │   │
│  │ SELECT DISTINCT s.* FROM `brz_lnd_RBP_GPU` s           │   │
│  │ LEFT JOIN `brz_lnd_OPS_EXCEL_GPU` t                     │   │
│  │ ON s.`Material` = t.`PLANNING_SKU`                      │   │
│  │ WHERE t.`PLANNING_SKU` IS NULL                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Fallback to Python (if LLM fails)                       │   │
│  │ - Log fallback event                                    │   │
│  │ - Use original Python generator                         │   │
│  │ - Monitor fallback rate                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Output: SQL String (from LLM or Python)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              NLQueryExecutor (Python)                           │
│  - Execute SQL against database                                │
│  - Return results                                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUERY RESULTS                                │
│              [Product1, Product2, ...]                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Comparison

```
┌──────────────────────────────────────────────────────────────────┐
│                    CURRENT vs PROPOSED                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ CLASSIFICATION                                                   │
│ Current:  Python (hardcoded keywords)                           │
│ Proposed: Python (hardcoded keywords) - NO CHANGE               │
│                                                                  │
│ PARSING                                                          │
│ Current:  Hybrid (LLM + Python BFS)                             │
│ Proposed: Hybrid (LLM + Python BFS) - NO CHANGE                 │
│                                                                  │
│ SQL GENERATION                                                   │
│ Current:  Python (hardcoded templates)                          │
│ Proposed: LLM (with Python fallback) ← MAJOR CHANGE             │
│                                                                  │
│ EXECUTION                                                        │
│ Current:  Python (execute SQL)                                  │
│ Proposed: Python (execute SQL) - NO CHANGE                      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. SQL Generation Comparison

```
CURRENT (Python-Based):
┌─────────────────────────────────────────────────────────────────┐
│ Supported:                                                      │
│ ✅ SELECT, FROM, WHERE, JOIN                                    │
│ ✅ Simple operators: =                                          │
│ ✅ DISTINCT, LIMIT                                              │
│                                                                 │
│ NOT Supported:                                                  │
│ ❌ Complex operators: >, <, LIKE, IN, BETWEEN, IS NULL         │
│ ❌ GROUP BY, HAVING                                             │
│ ❌ ORDER BY                                                     │
│ ❌ Subqueries, CTEs                                             │
│ ❌ Window functions                                             │
│ ❌ Multiple joins (only 2 tables)                               │
│ ❌ Complex WHERE conditions (no OR)                             │
└─────────────────────────────────────────────────────────────────┘

PROPOSED (LLM-Based):
┌─────────────────────────────────────────────────────────────────┐
│ Phase 1 (Week 1):                                               │
│ ✅ All current features                                         │
│ ✅ Complex operators: >, <, LIKE, IN, BETWEEN, IS NULL         │
│ ✅ Multiple joins (unlimited tables)                            │
│ ✅ Complex WHERE conditions (with OR)                           │
│                                                                 │
│ Phase 2 (Week 2):                                               │
│ ✅ GROUP BY, HAVING                                             │
│ ✅ ORDER BY                                                     │
│                                                                 │
│ Phase 3 (Week 3):                                               │
│ ✅ Subqueries, CTEs                                             │
│ ✅ Window functions                                             │
│                                                                 │
│ Phase 4 (Week 4):                                               │
│ ✅ Advanced features (stored procedures, etc.)                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Rollout Timeline

```
Week 1: Phase 1 - Direct SQL Generation
┌─────────────────────────────────────────────────────────────────┐
│ Mon-Tue: Implement LLMSQLGenerator                              │
│ Wed:     Add validation layer                                   │
│ Thu:     Deploy to 10% traffic                                  │
│ Fri:     Monitor metrics                                        │
│                                                                 │
│ Metrics:                                                        │
│ - Success rate: 95%+                                            │
│ - Fallback rate: <5%                                            │
│ - Performance: <2s per query                                    │
└─────────────────────────────────────────────────────────────────┘

Week 2: Phase 2 - WHERE Clause Intelligence
┌─────────────────────────────────────────────────────────────────┐
│ Mon-Tue: Extend QueryIntent for operators                       │
│ Wed:     Update LLM parser                                      │
│ Thu:     Deploy to 50% traffic                                  │
│ Fri:     Monitor metrics                                        │
│                                                                 │
│ Metrics:                                                        │
│ - Complex WHERE support: 90%+                                   │
│ - Success rate: 95%+                                            │
└─────────────────────────────────────────────────────────────────┘

Week 3: Phase 3 - JOIN Optimization
┌─────────────────────────────────────────────────────────────────┐
│ Mon-Tue: Create LLMPathOptimizer                                │
│ Wed:     Integrate with parser                                  │
│ Thu:     Deploy to 100% traffic                                 │
│ Fri:     Monitor metrics                                        │
│                                                                 │
│ Metrics:                                                        │
│ - Path optimization: 85%+                                       │
│ - Query performance: +20%                                       │
└─────────────────────────────────────────────────────────────────┘

Week 4: Phase 4 - Complex Queries
┌─────────────────────────────────────────────────────────────────┐
│ Mon-Tue: Extend QueryIntent for GROUP BY, ORDER BY             │
│ Wed:     Update LLM parser                                      │
│ Thu:     Deploy and monitor                                     │
│ Fri:     Finalize and document                                  │
│                                                                 │
│ Metrics:                                                        │
│ - Complex query support: 90%+                                   │
│ - Overall success rate: 95%+                                    │
└─────────────────────────────────────────────────────────────────┘
```


