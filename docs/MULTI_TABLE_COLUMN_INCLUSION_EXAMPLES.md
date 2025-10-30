# Multi-Table Column Inclusion - Examples & Architecture

## Example 1: Simple Column Inclusion

### Input Query
```
"Show me all the products in RBP GPU which are inactive in OPS Excel, include planner from HANA Master"
```

### Processing Flow

```
1. CLASSIFICATION
   ├─ Query Type: comparison_query
   └─ Operation: NOT_IN

2. PARSING
   ├─ Source Table: brz_lnd_RBP_GPU
   ├─ Target Table: brz_lnd_OPS_EXCEL_GPU
   ├─ Operation: NOT_IN
   ├─ Filters: [{"column": "Active_Inactive", "value": "Inactive"}]
   └─ Additional Columns:
      └─ column_name: "planner"
         source_table: "hana_material_master"
         alias: "hana_planner"

3. VALIDATION
   ├─ ✓ Column "planner" exists in "hana_material_master"
   └─ ✓ Join path found: brz_lnd_RBP_GPU → hana_material_master

4. JOIN PATH DISCOVERY
   ├─ Path: brz_lnd_RBP_GPU → hana_material_master
   ├─ Join Columns: (Material, MATERIAL)
   └─ Confidence: 0.85

5. SQL GENERATION
   ├─ Base Query: SELECT DISTINCT s.* FROM brz_lnd_RBP_GPU s ...
   ├─ Additional Columns: hm.planner AS hana_planner
   └─ Additional Joins: LEFT JOIN hana_material_master hm ON s.Material = hm.MATERIAL

6. FINAL SQL
   SELECT DISTINCT 
       s.*,
       hm.planner AS hana_planner
   FROM brz_lnd_RBP_GPU s
   LEFT JOIN brz_lnd_OPS_EXCEL_GPU t ON s.gpu_id = t.product_id
   LEFT JOIN hana_material_master hm ON s.Material = hm.MATERIAL
   WHERE t.product_id IS NULL
     AND s.Active_Inactive = 'Inactive'
```

### QueryIntent Object
```python
QueryIntent(
    definition="Show me all the products in RBP GPU which are inactive in OPS Excel, include planner from HANA Master",
    query_type="comparison_query",
    source_table="brz_lnd_RBP_GPU",
    target_table="brz_lnd_OPS_EXCEL_GPU",
    operation="NOT_IN",
    filters=[{"column": "Active_Inactive", "value": "Inactive"}],
    join_columns=[("gpu_id", "product_id")],
    confidence=0.85,
    additional_columns=[
        AdditionalColumn(
            column_name="planner",
            source_table="hana_material_master",
            alias="hana_planner",
            confidence=0.85,
            join_path=["brz_lnd_RBP_GPU", "hana_material_master"]
        )
    ]
)
```

---

## Example 2: Multiple Column Inclusion

### Input Query
```
"Show me all the products in RBP GPU which are inactive in OPS Excel, include planner from HANA Master and category from Product Master"
```

### Processing

```
Additional Columns Extracted:
1. column_name: "planner"
   source_table: "hana_material_master"
   
2. column_name: "category"
   source_table: "product_master"

Join Paths Found:
1. brz_lnd_RBP_GPU → hana_material_master (confidence: 0.85)
2. brz_lnd_RBP_GPU → product_master (confidence: 0.78)

Generated SQL:
SELECT DISTINCT 
    s.*,
    hm.planner AS hana_planner,
    pm.category AS product_category
FROM brz_lnd_RBP_GPU s
LEFT JOIN brz_lnd_OPS_EXCEL_GPU t ON s.gpu_id = t.product_id
LEFT JOIN hana_material_master hm ON s.Material = hm.MATERIAL
LEFT JOIN product_master pm ON s.product_id = pm.product_id
WHERE t.product_id IS NULL
  AND s.Active_Inactive = 'Inactive'
```

---

## Example 3: Error Handling

### Scenario 1: Column Doesn't Exist

**Input Query**:
```
"Show me products in RBP, include invalid_column from HANA Master"
```

**Error Response**:
```json
{
    "success": false,
    "error": "Column validation failed",
    "details": [
        "Column 'invalid_column' not found in table 'hana_material_master'",
        "Available columns: MATERIAL, PLANT, STORAGE_LOCATION, PLANNER, CATEGORY"
    ]
}
```

### Scenario 2: No Relationship Path

**Input Query**:
```
"Show me products in RBP, include column from unrelated_table"
```

**Error Response**:
```json
{
    "success": false,
    "error": "Join path not found",
    "details": [
        "No relationship path found between 'brz_lnd_RBP_GPU' and 'unrelated_table'",
        "Please ensure the Knowledge Graph has relationships between these tables"
    ]
}
```

### Scenario 3: Table Not Found

**Input Query**:
```
"Show me products in RBP, include planner from NonExistentTable"
```

**Error Response**:
```json
{
    "success": false,
    "error": "Table not found",
    "details": [
        "Table 'NonExistentTable' not found in schema",
        "Did you mean: 'hana_material_master'?"
    ]
}
```

---

## Architecture Diagram

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    NL Query Definition                          │
│  "Show products in RBP not in OPS, include planner from HANA"   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              NL Query Classifier                                │
│  ├─ Classify: comparison_query                                 │
│  └─ Operation: NOT_IN                                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              NL Query Parser                                    │
│  ├─ Extract main tables (RBP, OPS)                             │
│  ├─ Extract filters (inactive)                                 │
│  ├─ [NEW] Extract additional columns (planner from HANA)       │
│  ├─ Resolve table names (business → actual)                    │
│  ├─ Find join columns from KG                                  │
│  └─ [NEW] Find join paths for additional columns               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              QueryIntent Object                                 │
│  ├─ source_table: brz_lnd_RBP_GPU                              │
│  ├─ target_table: brz_lnd_OPS_EXCEL_GPU                        │
│  ├─ operation: NOT_IN                                          │
│  ├─ filters: [...]                                             │
│  ├─ join_columns: [(gpu_id, product_id)]                       │
│  └─ [NEW] additional_columns: [                                │
│      {                                                          │
│        column_name: "planner",                                 │
│        source_table: "hana_material_master",                   │
│        alias: "hana_planner",                                  │
│        join_path: [...]                                        │
│      }                                                          │
│    ]                                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              NL SQL Generator                                   │
│  ├─ Generate base SQL (comparison query)                       │
│  ├─ [NEW] Add additional column JOINs                          │
│  ├─ [NEW] Add additional columns to SELECT                     │
│  └─ Add filters and WHERE clause                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Generated SQL Query                                │
│  SELECT DISTINCT s.*, hm.planner AS hana_planner               │
│  FROM brz_lnd_RBP_GPU s                                         │
│  LEFT JOIN brz_lnd_OPS_EXCEL_GPU t ON ...                       │
│  LEFT JOIN hana_material_master hm ON ...                       │
│  WHERE ...                                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Query Executor                                     │
│  ├─ Execute SQL on database                                    │
│  └─ Return results with column metadata                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Results with Metadata                              │
│  {                                                              │
│    "results": [...],                                           │
│    "column_metadata": {                                        │
│      "hana_planner": {                                         │
│        "original_column": "planner",                           │
│        "source_table": "hana_material_master",                 │
│        "join_path": [...]                                      │
│      }                                                          │
│    }                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Interaction Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    NL Query Parser                               │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ _extract_additional_columns()                              │ │
│  │ ├─ Call LLM with "include" clause prompt                  │ │
│  │ ├─ Parse JSON response                                    │ │
│  │ └─ Return List[Dict[column_name, source_table]]           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ _validate_additional_columns()                             │ │
│  │ ├─ Resolve table names using table_mapper                 │ │
│  │ ├─ Check columns exist in schemas_info                    │ │
│  │ └─ Return (valid_columns, errors)                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ _find_join_path_to_table()                                 │ │
│  │ ├─ Use BFS to find all paths in KG                        │ │
│  │ ├─ Score paths (confidence * 0.7 + length * 0.3)          │ │
│  │ └─ Return best JoinPath                                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ _resolve_join_paths()                                      │ │
│  │ ├─ For each column, find join path                        │ │
│  │ ├─ Update confidence and join_path                        │ │
│  │ └─ Return List[AdditionalColumn]                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                    NL SQL Generator                              │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ _add_additional_columns_to_sql()                           │ │
│  │ ├─ Extract SELECT clause from base SQL                    │ │
│  │ ├─ Add additional columns with aliases                    │ │
│  │ └─ Return modified SQL                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ _generate_join_clauses()                                   │ │
│  │ ├─ For each additional column                             │ │
│  │ ├─ Generate JOIN for each step in path                    │ │
│  │ └─ Return JOIN clause string                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Knowledge Graph Relationship Example

```
Knowledge Graph Structure:

Nodes:
├─ table_brz_lnd_RBP_GPU
│  └─ properties: {columns: [gpu_id, Material, ...]}
├─ table_brz_lnd_OPS_EXCEL_GPU
│  └─ properties: {columns: [product_id, PLANNING_SKU, ...]}
└─ table_hana_material_master
   └─ properties: {columns: [MATERIAL, PLANNER, ...]}

Relationships:
├─ brz_lnd_RBP_GPU → brz_lnd_OPS_EXCEL_GPU
│  ├─ source_column: gpu_id
│  ├─ target_column: product_id
│  └─ confidence: 0.95
├─ brz_lnd_RBP_GPU → hana_material_master
│  ├─ source_column: Material
│  ├─ target_column: MATERIAL
│  └─ confidence: 0.85
└─ brz_lnd_OPS_EXCEL_GPU → hana_material_master
   ├─ source_column: PLANNING_SKU
   ├─ target_column: MATERIAL
   └─ confidence: 0.78

Join Path Selection:
Query: "include planner from HANA Master"
Source: brz_lnd_RBP_GPU
Target: hana_material_master

Paths Found:
1. Direct: brz_lnd_RBP_GPU → hana_material_master
   Score: (0.85 * 0.7) + (1/1 * 0.3) = 0.895 ✓ SELECTED

2. Via OPS: brz_lnd_RBP_GPU → brz_lnd_OPS_EXCEL_GPU → hana_material_master
   Score: (0.95*0.78 * 0.7) + (1/2 * 0.3) = 0.465
```

---

## Response Format

### Success Response

```json
{
    "success": true,
    "results": [
        {
            "gpu_id": "GPU001",
            "product_name": "A100",
            "Active_Inactive": "Inactive",
            "hana_planner": "John Smith",
            "product_category": "High-End"
        },
        {
            "gpu_id": "GPU002",
            "product_name": "V100",
            "Active_Inactive": "Inactive",
            "hana_planner": "Jane Doe",
            "product_category": "Mid-Range"
        }
    ],
    "column_metadata": {
        "hana_planner": {
            "original_column": "planner",
            "source_table": "hana_material_master",
            "join_path": ["brz_lnd_RBP_GPU", "hana_material_master"],
            "join_confidence": 0.85
        },
        "product_category": {
            "original_column": "category",
            "source_table": "product_master",
            "join_path": ["brz_lnd_RBP_GPU", "product_master"],
            "join_confidence": 0.78
        }
    },
    "execution_stats": {
        "record_count": 2,
        "execution_time_ms": 1234.56,
        "additional_columns_included": 2
    }
}
```

---

## Performance Considerations

### Caching Strategy

```python
# Cache join paths to avoid repeated BFS
@lru_cache(maxsize=1000)
def _find_join_path_cached(self, source: str, target: str) -> Optional[JoinPath]:
    return self._find_join_path_to_table(source, target)

# Cache column existence checks
@lru_cache(maxsize=5000)
def _column_exists_cached(self, table: str, column: str) -> bool:
    return self._column_exists_in_table(table, column)
```

### Optimization Tips

1. **Limit BFS Depth**: Don't search beyond 5 hops
2. **Early Termination**: Stop BFS once target found
3. **Batch Validation**: Validate all columns before path finding
4. **Lazy Loading**: Only load KG relationships when needed
5. **Index Relationships**: Create index on (source_id, target_id) for faster lookup

