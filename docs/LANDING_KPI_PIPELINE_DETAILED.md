# Landing KPI Execution Pipeline - Detailed Flow

## Complete End-to-End Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LANDING KPI EXECUTION PIPELINE                           │
└─────────────────────────────────────────────────────────────────────────────┘

INPUT: KPI Execution Request
{
  "kg_name": "KG_102",
  "schemas": ["newdqschema"],
  "definitions": ["Show me all products in RBP GPU which are inactive OPS Excel"],
  "use_llm": true,
  "min_confidence": 0.7,
  "limit": 1000,
  "db_type": "sqlserver"
}

                                    ↓

┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: LOAD KNOWLEDGE GRAPH                                                │
│ File: landing_kpi_executor.py (lines 113-148)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Load entities from Graphiti backend                                       │
│ • Load relationships from Graphiti backend                                  │
│ • Load table aliases (business names → actual table names)                  │
│ • Create KnowledgeGraph object                                              │
│                                                                              │
│ OUTPUT: KnowledgeGraph                                                       │
│ {                                                                            │
│   "name": "KG_102",                                                         │
│   "nodes": [45 entities],                                                   │
│   "relationships": [120 relationships],                                     │
│   "table_aliases": {"RBP GPU": "rbp_gpu_table", ...}                       │
│ }                                                                            │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ↓

┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: CLASSIFY QUERY                                                      │
│ File: nl_query_classifier.py                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ INPUT: "Show me all products in RBP GPU which are inactive OPS Excel"      │
│                                                                              │
│ • Analyze NL definition                                                     │
│ • Identify query type                                                       │
│ • Identify operation type (NOT_IN, IN, EQUALS, etc.)                       │
│                                                                              │
│ OUTPUT: query_type = "comparison_query"                                     │
│         operation = "NOT_IN"                                                │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ↓

┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: PARSE QUERY (WITH LLM)                                              │
│ File: nl_query_parser.py (lines 71-121)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ INPUT: NL definition + KnowledgeGraph + use_llm=true                        │
│                                                                              │
│ • If use_llm=true AND llm_service.is_enabled():                             │
│   └─→ Call LLM to extract structured information                            │
│ • Else:                                                                      │
│   └─→ Use rule-based parsing                                                │
│                                                                              │
│ • Resolve table names using aliases                                         │
│ • Find join columns from KG relationships                                   │
│ • Extract filters                                                           │
│                                                                              │
│ OUTPUT: QueryIntent                                                          │
│ {                                                                            │
│   "definition": "Show me all products...",                                  │
│   "query_type": "comparison_query",                                         │
│   "source_table": "rbp_gpu_table",                                          │
│   "target_table": "ops_excel_table",                                        │
│   "operation": "NOT_IN",                                                    │
│   "join_columns": [("gpu_id", "product_id")],                              │
│   "filters": [{"column": "status", "operator": "equals", "value": "inactive"}],
│   "confidence": 0.85                                                        │
│ }                                                                            │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ↓

┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: GENERATE SQL                                                        │
│ File: nl_sql_generator.py (lines 32-59)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ INPUT: QueryIntent                                                          │
│                                                                              │
│ • Determine SQL generation strategy based on query_type                     │
│ • For comparison_query:                                                     │
│   └─→ _generate_comparison_query()                                          │
│ • For filter_query:                                                         │
│   └─→ _generate_filter_query()                                              │
│ • For aggregation_query:                                                    │
│   └─→ _generate_aggregation_query()                                         │
│ • For data_query:                                                           │
│   └─→ _generate_data_query()                                                │
│                                                                              │
│ • Apply filters to WHERE clause                                             │
│ • Quote identifiers for database type                                       │
│                                                                              │
│ OUTPUT: SQL Query String                                                    │
│ SELECT DISTINCT s.*                                                         │
│ FROM rbp_gpu_table s                                                        │
│ LEFT JOIN ops_excel_table t ON s.gpu_id = t.product_id                     │
│ WHERE t.product_id IS NULL                                                  │
│ AND t.status = 'inactive'                                                   │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ↓

┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: ADD LIMIT CLAUSE                                                    │
│ File: nl_query_executor.py (lines 233-266)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Database-specific LIMIT syntax                                            │
│ • SQL Server: TOP clause                                                    │
│ • MySQL/PostgreSQL/Oracle: LIMIT clause                                     │
│                                                                              │
│ OUTPUT: SQL with LIMIT                                                      │
│ SELECT DISTINCT TOP 1000 s.*                                                │
│ FROM rbp_gpu_table s                                                        │
│ LEFT JOIN ops_excel_table t ON s.gpu_id = t.product_id                     │
│ WHERE t.product_id IS NULL                                                  │
│ AND t.status = 'inactive'                                                   │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ↓

┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 6: EXECUTE SQL ON DATABASE                                             │
│ File: nl_query_executor.py (lines 126-146)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Get database connection (JDBC)                                            │
│ • Execute SQL query                                                         │
│ • Fetch results                                                             │
│ • Convert rows to dictionaries                                              │
│                                                                              │
│ OUTPUT: QueryResult                                                          │
│ {                                                                            │
│   "sql": "SELECT DISTINCT TOP 1000 s.* FROM ...",                          │
│   "record_count": 42,                                                       │
│   "records": [                                                              │
│     {"id": 1, "name": "Product A", "status": "inactive"},                  │
│     {"id": 2, "name": "Product B", "status": "inactive"},                  │
│     ...                                                                      │
│   ],                                                                         │
│   "confidence": 0.85,                                                       │
│   "execution_time_ms": 234.56                                               │
│ }                                                                            │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ↓

┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 7: FORMAT AND RETURN RESULTS                                           │
│ File: landing_kpi_executor.py (lines 174-190)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Format QueryResult for API response                                       │
│ • Include metadata (confidence, execution time, etc.)                       │
│                                                                              │
│ OUTPUT: KPI Execution Result                                                │
│ {                                                                            │
│   "generated_sql": "SELECT DISTINCT TOP 1000 s.* FROM ...",                │
│   "number_of_records": 42,                                                  │
│   "sql_query_type": "comparison_query",                                     │
│   "operation": "NOT_IN",                                                    │
│   "execution_status": "success",                                            │
│   "execution_time_ms": 234.56,                                              │
│   "confidence_score": 0.85,                                                 │
│   "result_data": [                                                          │
│     {"id": 1, "name": "Product A", "status": "inactive"},                  │
│     ...                                                                      │
│   ]                                                                          │
│ }                                                                            │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ↓

OUTPUT: API Response (200 OK)
```

## Key Components and Their Roles

| Component | File | Role |
|-----------|------|------|
| **Landing KPI Executor** | `landing_kpi_executor.py` | Orchestrates entire pipeline |
| **NL Query Classifier** | `nl_query_classifier.py` | Classifies query type |
| **NL Query Parser** | `nl_query_parser.py` | Parses NL to QueryIntent (with LLM) |
| **NL SQL Generator** | `nl_sql_generator.py` | Generates SQL from QueryIntent |
| **NL Query Executor** | `nl_query_executor.py` | Executes SQL and returns results |
| **LLM Service** | `llm_service.py` | Provides LLM parsing (optional) |
| **Graphiti Backend** | `graphiti_backend.py` | Stores/retrieves KG data |

## Data Flow Summary

```
NL Definition
    ↓
Classifier → Query Type
    ↓
Parser (+ LLM) → QueryIntent
    ↓
SQL Generator → SQL Query
    ↓
Query Executor → Database Results
    ↓
Formatter → API Response
```

## Error Handling at Each Step

1. **KG Loading**: Verify KG exists and has data
2. **Classification**: Verify query type is recognized
3. **Parsing**: Verify tables and columns are resolved
4. **SQL Generation**: Verify SQL is syntactically correct
5. **Execution**: Verify database connection and permissions
6. **Formatting**: Verify results are properly formatted

## Performance Metrics

- **KG Loading**: ~100-500ms
- **Classification**: ~10-50ms
- **Parsing (with LLM)**: ~500-2000ms
- **SQL Generation**: ~10-50ms
- **SQL Execution**: ~100-5000ms (depends on query complexity)
- **Total**: ~700-7600ms

## Status

✅ **Complete Pipeline** - All components working together
✅ **LLM Integration** - Optional LLM parsing enabled
✅ **Error Handling** - Comprehensive error messages
✅ **Performance** - Optimized for typical queries

