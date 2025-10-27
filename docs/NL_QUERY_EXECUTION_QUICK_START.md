# Natural Language Query Execution - Quick Start Guide

## What's New?

A new endpoint that executes natural language definitions as **data queries** (not relationship definitions).

**Old Behavior**: "Show me products not in OPS Excel" → Added as a relationship to KG
**New Behavior**: "Show me products not in OPS Excel" → Generates SQL, executes it, returns data results

---

## Quick Start

### 1. Via API

```bash
curl -X POST http://localhost:8000/v1/kg/nl-queries/execute \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "KG_101",
    "schemas": ["newdqschema"],
    "definitions": [
      "Show me all products in RBP GPU which are not in OPS Excel",
      "Show me all products in RBP GPU which are in active OPS Excel"
    ],
    "use_llm": true,
    "min_confidence": 0.7,
    "limit": 1000,
    "db_type": "mysql"
  }'
```

### 2. Response

```json
{
  "success": true,
  "kg_name": "KG_101",
  "total_definitions": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "definition": "Show me all products in RBP GPU which are not in OPS Excel",
      "query_type": "comparison_query",
      "operation": "NOT_IN",
      "sql": "SELECT DISTINCT s.* FROM `rbp_gpu` s LEFT JOIN `ops_excel` t ON s.`material` = t.`planning_sku` WHERE t.`planning_sku` IS NULL",
      "record_count": 245,
      "join_columns": [["material", "planning_sku"]],
      "confidence": 0.85,
      "execution_time_ms": 125.5,
      "records": [
        {"material": "MAT001", "product_name": "Product A", ...},
        {"material": "MAT002", "product_name": "Product B", ...},
        ...
      ]
    },
    {
      "definition": "Show me all products in RBP GPU which are in active OPS Excel",
      "query_type": "comparison_query",
      "operation": "IN",
      "sql": "SELECT DISTINCT s.* FROM `rbp_gpu` s INNER JOIN `ops_excel` t ON s.`material` = t.`planning_sku` WHERE t.`status` = 'active'",
      "record_count": 1523,
      "join_columns": [["material", "planning_sku"]],
      "confidence": 0.85,
      "execution_time_ms": 200.0,
      "records": [...]
    }
  ],
  "statistics": {
    "total_queries": 2,
    "successful": 2,
    "failed": 0,
    "total_records": 1768,
    "total_execution_time_ms": 325.5,
    "average_confidence": 0.85,
    "records_by_query": [
      {
        "definition": "Show me all products in RBP GPU which are not in OPS Excel",
        "record_count": 245,
        "execution_time_ms": 125.5
      },
      {
        "definition": "Show me all products in RBP GPU which are in active OPS Excel",
        "record_count": 1523,
        "execution_time_ms": 200.0
      }
    ]
  }
}
```

---

## Supported Query Types

### 1. Comparison Queries
Compare two tables and find differences.

**Examples**:
- "Show me all products in RBP GPU which are not in OPS Excel" → NOT_IN
- "Show me all products in RBP GPU which are in OPS Excel" → IN
- "Find products missing from OPS Excel" → NOT_IN
- "Compare RBP GPU with OPS Excel" → IN

**Generated SQL**:
```sql
-- NOT_IN (set difference)
SELECT DISTINCT s.* FROM `rbp_gpu` s 
LEFT JOIN `ops_excel` t ON s.`material` = t.`planning_sku` 
WHERE t.`planning_sku` IS NULL

-- IN (set intersection)
SELECT DISTINCT s.* FROM `rbp_gpu` s 
INNER JOIN `ops_excel` t ON s.`material` = t.`planning_sku`
```

### 2. Filter Queries
Filter records by conditions.

**Examples**:
- "Show me active products"
- "Find inactive records"
- "List products with status = 'active'"

**Generated SQL**:
```sql
SELECT * FROM `products` 
WHERE `status` = 'active'
```

### 3. Data Queries
Simple SELECT from one or more tables.

**Examples**:
- "Show me all products in RBP GPU"
- "Find all records in OPS Excel"
- "List products from material master"

**Generated SQL**:
```sql
SELECT * FROM `rbp_gpu`
```

### 4. Aggregation Queries
Count, sum, or aggregate data.

**Examples**:
- "Count products by category"
- "Total quantity by supplier"

**Generated SQL**:
```sql
SELECT COUNT(*) as count FROM `products`
```

---

## Key Features

### ✅ Automatic Join Inference
The system uses the Knowledge Graph to automatically find join columns:

```
Definition: "Show me products in RBP GPU not in OPS Excel"
↓
KG finds relationship: RBP_GPU.material ←→ OPS_EXCEL.planning_sku
↓
Generated SQL uses: ON s.`material` = t.`planning_sku`
```

### ✅ Separate Query Per Definition
Each definition generates its own SQL query and returns separate results:

```json
{
  "definitions": [
    "Query 1",
    "Query 2",
    "Query 3"
  ],
  "results": [
    { "definition": "Query 1", "record_count": 100, ... },
    { "definition": "Query 2", "record_count": 200, ... },
    { "definition": "Query 3", "record_count": 50, ... }
  ]
}
```

### ✅ Multi-Database Support
Works with MySQL, PostgreSQL, SQL Server, Oracle:

```python
# MySQL
db_type: "mysql"  # Uses `column` syntax

# SQL Server
db_type: "sqlserver"  # Uses [column] syntax

# Oracle
db_type: "oracle"  # Uses "column" syntax
```

### ✅ Confidence Scoring
Each query gets a confidence score:
- Base: 0.6 (rule-based parsing)
- +0.15 if LLM parsing used
- +0.1 if KG relationship found
- Max: 0.95

### ✅ Batch Processing
Execute multiple definitions in one request with individual error handling.

---

## Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `kg_name` | string | required | Knowledge graph name |
| `schemas` | array | required | List of schema names |
| `definitions` | array | required | List of NL definitions |
| `use_llm` | boolean | true | Use LLM for parsing |
| `min_confidence` | float | 0.7 | Minimum confidence threshold |
| `limit` | integer | 1000 | Max records per query |
| `db_type` | string | mysql | Database type |

---

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Overall success status |
| `kg_name` | string | Knowledge graph name |
| `total_definitions` | integer | Total definitions processed |
| `successful` | integer | Number of successful queries |
| `failed` | integer | Number of failed queries |
| `results` | array | Array of QueryResult objects |
| `statistics` | object | Aggregate statistics |

### QueryResult Fields

| Field | Type | Description |
|-------|------|-------------|
| `definition` | string | Original definition |
| `query_type` | string | Type of query |
| `operation` | string | Operation (NOT_IN, IN, etc.) |
| `sql` | string | Generated SQL |
| `record_count` | integer | Number of records returned |
| `records` | array | Actual data records |
| `join_columns` | array | Join columns used |
| `confidence` | float | Confidence score (0-1) |
| `execution_time_ms` | float | Execution time in ms |
| `error` | string | Error message if any |

---

## Examples

### Example 1: Find Missing Products
```bash
curl -X POST http://localhost:8000/v1/kg/nl-queries/execute \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "KG_101",
    "schemas": ["newdqschema"],
    "definitions": [
      "Show me all products in RBP GPU which are not in OPS Excel"
    ],
    "use_llm": true
  }'
```

**Result**: 245 products in RBP GPU but not in OPS Excel

### Example 2: Find Active Products
```bash
curl -X POST http://localhost:8000/v1/kg/nl-queries/execute \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "KG_101",
    "schemas": ["newdqschema"],
    "definitions": [
      "Show me all active products in RBP GPU"
    ],
    "use_llm": true
  }'
```

**Result**: All active products from RBP GPU table

### Example 3: Batch Comparison
```bash
curl -X POST http://localhost:8000/v1/kg/nl-queries/execute \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "KG_101",
    "schemas": ["newdqschema"],
    "definitions": [
      "Show me products in RBP GPU not in OPS Excel",
      "Show me products in OPS Excel not in RBP GPU",
      "Show me products in both RBP GPU and OPS Excel"
    ],
    "use_llm": true
  }'
```

**Result**: Three separate queries with all comparisons

---

## Troubleshooting

### Issue: "No database connection available"
**Solution**: Make sure database is configured and running

### Issue: Low confidence scores
**Solution**: Enable LLM parsing with `"use_llm": true`

### Issue: Wrong join columns
**Solution**: Check Knowledge Graph relationships are correct

### Issue: No records returned
**Solution**: Check table names and filters are correct

---

## Next Steps

1. Try the API with your own definitions
2. Check the generated SQL in the response
3. Verify the join columns are correct
4. Review the confidence scores
5. Adjust `min_confidence` if needed

---

## Related Documentation

- [NL Query Generation Implementation](./NL_QUERY_GENERATION_IMPLEMENTATION_COMPLETE.md)
- [Knowledge Graph Guide](./KG_VISUALIZATION_FIX.md)
- [API Documentation](../README.md)

