# Role of NL SQL Generator in Landing KPI Service

## Overview

`nl_sql_generator.py` is a **critical component** in the Landing KPI execution pipeline. It's responsible for converting parsed natural language intents into executable SQL queries.

## Position in the Pipeline

```
Landing KPI Executor
    ↓
1. Classify NL Definition
    ↓
2. Parse NL Definition (with LLM)
    ↓
3. Get QueryIntent
    ↓
4. Execute Query
    ├─→ NL Query Executor
    │   ├─→ NL SQL Generator ← YOU ARE HERE
    │   │   └─→ Generate SQL from QueryIntent
    │   ├─→ Execute SQL on Database
    │   └─→ Return QueryResult
    ↓
5. Format and Return Results
```

## What NL SQL Generator Does

### **Input**: QueryIntent Object
```python
QueryIntent(
    definition="Show me all products in RBP GPU which are inactive OPS Excel",
    query_type="comparison_query",
    source_table="rbp_gpu_table",
    target_table="ops_excel_table",
    operation="NOT_IN",
    join_columns=[("gpu_id", "product_id")],
    filters=[{"column": "status", "operator": "equals", "value": "inactive"}],
    confidence=0.85
)
```

### **Output**: SQL Query String
```sql
SELECT DISTINCT s.*
FROM rbp_gpu_table s
LEFT JOIN ops_excel_table t ON s.gpu_id = t.product_id
WHERE t.product_id IS NULL
AND t.status = 'inactive'
```

## Supported Query Types

### 1. **Comparison Query** (NOT_IN, IN)
**Purpose**: Compare two datasets and find differences or intersections

**Example NL**: "Show me products in RBP GPU which are NOT in OPS Excel"

**Generated SQL**:
```sql
-- NOT_IN: Products in source but not in target
SELECT DISTINCT s.*
FROM source_table s
LEFT JOIN target_table t ON s.join_col = t.join_col
WHERE t.join_col IS NULL
```

**Operations**:
- `NOT_IN`: Products in A but not in B (LEFT JOIN with NULL check)
- `IN`: Products in both A and B (INNER JOIN)

### 2. **Filter Query**
**Purpose**: Filter data based on conditions

**Example NL**: "Show me all inactive products"

**Generated SQL**:
```sql
SELECT * FROM products
WHERE status = 'inactive'
```

**Features**:
- Single table filters
- Multi-table filters with joins
- Multiple conditions (AND/OR)

### 3. **Aggregation Query**
**Purpose**: Aggregate data (COUNT, SUM, AVG, etc.)

**Example NL**: "Count products by category"

**Generated SQL**:
```sql
SELECT category, COUNT(*) as count
FROM products
GROUP BY category
```

### 4. **Data Query**
**Purpose**: Simple SELECT queries

**Example NL**: "Show me all products"

**Generated SQL**:
```sql
SELECT * FROM products
```

## Key Features

### 1. **Database-Specific SQL Generation**
Supports different SQL dialects:
- ✅ MySQL
- ✅ PostgreSQL
- ✅ SQL Server
- ✅ Oracle

### 2. **Intelligent Identifier Quoting**
Handles special characters in table/column names:
```python
# Input: "RBP GPU" (with space)
# Output: `RBP GPU` (quoted for MySQL)
# Output: [RBP GPU] (quoted for SQL Server)
```

### 3. **Filter Application**
Applies WHERE clauses intelligently:
- Single table: Applies to source table
- Multi-table: Applies to target table (for comparisons)
- Supports multiple filters with AND/OR logic

### 4. **Join Column Handling**
Uses join columns from QueryIntent:
```python
join_columns = [("source_col", "target_col")]
# Generates: ON s.source_col = t.target_col
```

## Integration with Landing KPI Executor

### **Step-by-Step Flow**

```
1. Landing KPI Executor receives NL definition:
   "Show me all products in RBP GPU which are inactive OPS Excel"

2. Classifier identifies: comparison_query

3. Parser (with LLM) extracts:
   - source_table: "rbp_gpu_table"
   - target_table: "ops_excel_table"
   - operation: "NOT_IN"
   - join_columns: [("gpu_id", "product_id")]
   - filters: [{"column": "status", "value": "inactive"}]

4. NL Query Executor receives QueryIntent

5. NL SQL Generator generates SQL:
   SELECT DISTINCT s.*
   FROM rbp_gpu_table s
   LEFT JOIN ops_excel_table t ON s.gpu_id = t.product_id
   WHERE t.product_id IS NULL
   AND t.status = 'inactive'

6. SQL is executed on database

7. Results are returned to Landing KPI Executor

8. Results are formatted and returned to API
```

## Code Example

### Using NL SQL Generator Directly

```python
from kg_builder.services.nl_sql_generator import NLSQLGenerator
from kg_builder.services.nl_query_parser import QueryIntent

# Create generator for SQL Server
generator = NLSQLGenerator(db_type="sqlserver")

# Create intent
intent = QueryIntent(
    definition="Show inactive products",
    query_type="filter_query",
    source_table="products",
    filters=[{"column": "status", "operator": "equals", "value": "inactive"}]
)

# Generate SQL
sql = generator.generate(intent)
print(sql)
# Output: SELECT * FROM products WHERE status = 'inactive'
```

### In Landing KPI Executor

```python
# This happens automatically in the pipeline:
executor = get_nl_query_executor(db_type="sqlserver")
query_result = executor.execute(intent, connection, limit=1000)
# Internally calls: sql = generator.generate(intent)
```

## Error Handling

### Common Errors

1. **Missing Join Columns for Comparison Query**
   ```
   Error: Comparison query requires join columns to compare 'table1' and 'table2'
   Solution: Ensure KG has relationships between tables
   ```

2. **Missing Source Table**
   ```
   Error: Filter query requires source table
   Solution: Verify parser correctly identified source table
   ```

3. **Unsupported Query Type**
   ```
   Error: Unsupported query type: unknown_type
   Solution: Verify classifier correctly classified the query
   ```

## Performance Considerations

1. **LIMIT Clause**: Added by NL Query Executor (not generator)
2. **DISTINCT**: Used to avoid duplicates in joins
3. **Index Usage**: Depends on database optimization
4. **Query Complexity**: Comparison queries with filters are most complex

## Files Involved

| File | Role |
|------|------|
| `nl_sql_generator.py` | Generates SQL from QueryIntent |
| `nl_query_executor.py` | Uses generator to execute queries |
| `landing_kpi_executor.py` | Orchestrates entire pipeline |
| `nl_query_parser.py` | Creates QueryIntent from NL definition |
| `nl_query_classifier.py` | Classifies query type |

## Status

✅ **Fully Integrated** - NL SQL Generator is a core component of the Landing KPI pipeline
✅ **Database Agnostic** - Supports multiple database types
✅ **Error Handling** - Provides detailed error messages

## Next Steps

1. Verify QueryIntent is correctly parsed
2. Check generated SQL is syntactically correct
3. Verify SQL executes successfully on database
4. Review results are returned correctly

