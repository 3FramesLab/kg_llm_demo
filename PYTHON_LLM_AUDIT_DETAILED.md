# Python vs LLM Usage - Detailed Audit

## Overview
This document lists ALL places where Python code is used instead of LLM for SQL query logic.

---

## 1. QUERY CLASSIFICATION (100% Python)

### 1.1 Query Type Classification
**File**: `kg_builder/services/nl_query_classifier.py`
**Lines**: 61-100
**Function**: `classify(definition: str) -> DefinitionType`
**What it does**: Determines if query is comparison, filter, aggregation, or data query
**Method**: Keyword matching (hardcoded lists)
**Why problematic**: 
- Misses nuanced queries
- Cannot handle domain-specific terminology
- Requires manual keyword updates

**Hardcoded Keywords**:
```python
comparison_keywords = ["compare", "difference", "not in", "missing", ...]
aggregation_keywords = ["count", "sum", "average", "total", ...]
filter_keywords = ["active", "inactive", "status", "where", ...]
```

### 1.2 Operation Type Extraction
**File**: `kg_builder/services/nl_query_classifier.py`
**Lines**: 102-126
**Function**: `get_operation_type(definition: str) -> Optional[str]`
**What it does**: Extracts operation (NOT_IN, IN, EQUALS, CONTAINS, AGGREGATE)
**Method**: Keyword matching
**Why problematic**: Same as above

---

## 2. TABLE NAME RESOLUTION (Hybrid)

### 2.1 Rule-Based Table Extraction
**File**: `kg_builder/services/nl_query_parser.py`
**Lines**: 201-284
**Function**: `_parse_rule_based()`
**What it does**: Extracts source and target table names from NL
**Method**: 
- Looks for capitalized words
- Matches against known tables
- Excludes common English words
**Why problematic**:
- Brittle pattern matching
- Fails on lowercase table names
- Cannot handle aliases or abbreviations

### 2.2 LLM-Based Table Extraction
**File**: `kg_builder/services/nl_query_parser.py`
**Lines**: 164-199
**Function**: `_parse_with_llm()`
**What it does**: Uses LLM to extract tables and filters
**Method**: Calls OpenAI with structured prompt
**Status**: ✅ LLM-based (good)

---

## 3. JOIN COLUMN RESOLUTION (100% Python)

### 3.1 KG-Based Join Column Finding
**File**: `kg_builder/services/nl_query_parser.py`
**Lines**: 362-419
**Function**: `_find_join_columns_from_kg(source: str, target: str)`
**What it does**: Searches KG relationships for join columns
**Method**: 
- Iterates through all relationships
- Matches table IDs (case-insensitive)
- Extracts source_column and target_column properties
**Why problematic**:
- O(n) search through all relationships
- Brittle string matching with "table_" prefix
- No scoring or ranking of multiple possible joins
- Fails if KG format changes

**Code**:
```python
for rel in self.kg.relationships:
    source_id = rel.source_id.lower()
    target_id = rel.target_id.lower()
    if (source_id == source.lower() and target_id == target.lower()):
        source_col = rel.properties.get("source_column")
        target_col = rel.properties.get("target_column")
        return [(source_col, target_col)]
```

### 3.2 Schema-Based Join Inference
**File**: `kg_builder/services/nl_query_parser.py`
**Lines**: 421-499
**Function**: `_infer_join_columns_from_schema()`
**What it does**: Finds join columns by matching column names
**Method**:
- Looks for exact column name matches
- Looks for ID pattern matches (e.g., product_id)
- Filters excluded fields
**Why problematic**:
- Assumes column names are meaningful
- Fails on renamed columns
- No semantic understanding

---

## 4. JOIN PATH FINDING (100% Python - BFS)

### 4.1 BFS Path Finding
**File**: `kg_builder/services/nl_query_parser.py`
**Lines**: 772-888
**Function**: `_find_join_path_to_table(source: str, target: str)`
**What it does**: Finds optimal path between two tables using BFS
**Method**:
- Breadth-first search through KG nodes
- Scores paths by confidence and length
- Returns best path
**Why problematic**:
- BFS may not find optimal path for complex graphs
- Scoring is simplistic: `(confidence * 0.7) + ((1/length) * 0.3)`
- No consideration of join selectivity or cardinality
- Depth limit of 5 may be too restrictive

**Code**:
```python
queue = deque([(source, [source], 1.0)])
while queue:
    current, path, conf = queue.popleft()
    if current.lower() == target.lower():
        all_paths.append((path, conf))
    # Find next tables...
```

### 4.2 Column Name-Based Join Inference
**File**: `kg_builder/services/nl_query_parser.py`
**Lines**: 890-979
**Function**: `_infer_join_from_column_names()`
**What it does**: Infers join when no KG relationship exists
**Method**:
- Finds common columns between tables
- Prioritizes ID-like columns
- Returns direct join path
**Why problematic**:
- Assumes common columns are join keys
- Hardcoded priority: material > product > sku > id_columns > generic
- No validation that join makes sense

---

## 5. SQL GENERATION (100% Python - HARDCODED)

### 5.1 Comparison Query Generation
**File**: `kg_builder/services/nl_sql_generator.py`
**Lines**: 74-151
**Function**: `_generate_comparison_query(intent)`
**What it does**: Generates NOT_IN or IN queries
**Method**: String formatting with hardcoded SQL template
**Why problematic**:
- Only supports two tables
- Hardcoded: `SELECT DISTINCT s.* FROM source LEFT/INNER JOIN target`
- Cannot handle multiple joins
- Cannot handle complex filters

**Hardcoded SQL**:
```python
sql = f"""
SELECT DISTINCT s.*
FROM {source} s
LEFT JOIN {target} t ON s.{source_col} = t.{target_col}
WHERE t.{target_col} IS NULL
"""
```

### 5.2 Filter Query Generation
**File**: `kg_builder/services/nl_sql_generator.py`
**Lines**: 153-199
**Function**: `_generate_filter_query(intent)`
**What it does**: Generates queries with WHERE conditions
**Method**: String formatting
**Why problematic**: Same as above

### 5.3 Aggregation Query Generation
**File**: `kg_builder/services/nl_sql_generator.py`
**Lines**: 201-222
**Function**: `_generate_aggregation_query(intent)`
**What it does**: Generates COUNT queries
**Method**: Hardcoded `SELECT COUNT(*) as count FROM source`
**Why problematic**:
- Only supports COUNT(*)
- No support for SUM, AVG, MIN, MAX
- No support for GROUP BY
- No support for HAVING

### 5.4 Data Query Generation
**File**: `kg_builder/services/nl_sql_generator.py`
**Lines**: 224-262
**Function**: `_generate_data_query(intent)`
**What it does**: Generates simple SELECT queries
**Method**: String formatting
**Why problematic**: Same as comparison queries

---

## 6. WHERE CLAUSE CONSTRUCTION (100% Python)

### 6.1 WHERE Clause Builder
**File**: `kg_builder/services/nl_sql_generator.py`
**Lines**: 264-297
**Function**: `_build_where_clause(filters, table_alias)`
**What it does**: Constructs WHERE conditions from filters
**Method**: Hardcoded equality: `column = value`
**Why problematic**:
- Only supports `=` operator
- No support for: >, <, >=, <=, LIKE, IN, BETWEEN, IS NULL
- No support for: OR conditions, complex expressions
- No support for: date functions, string functions
- No parameterized queries (SQL injection risk)

**Code**:
```python
for filter_item in filters:
    column = filter_item.get("column", "")
    value = filter_item.get("value", "")
    conditions.append(f"{column} = {value}")  # ONLY EQUALITY!
```

---

## 7. ADDITIONAL COLUMNS (100% Python - String Manipulation)

### 7.1 Additional Columns Addition
**File**: `kg_builder/services/nl_sql_generator.py`
**Lines**: 299-348
**Function**: `_add_additional_columns_to_sql(base_sql, intent)`
**What it does**: Adds columns from related tables to SQL
**Method**: Regex parsing and string manipulation
**Why problematic**:
- Fragile regex: `r'SELECT\s+(.*?)\s+FROM'`
- Cannot handle complex SELECT clauses
- Risk of SQL injection
- Difficult to maintain

**Code**:
```python
select_match = re.search(r'SELECT\s+(.*?)\s+FROM', base_sql, re.IGNORECASE | re.DOTALL)
select_clause = select_match.group(1).strip()
new_select = select_clause + ", " + ", ".join(additional_cols_sql)
```

### 7.2 JOIN Clause Generation for Additional Columns
**File**: `kg_builder/services/nl_sql_generator.py`
**Lines**: 350-400
**Function**: `_generate_join_clauses_for_columns(columns)`
**What it does**: Generates LEFT JOIN clauses for additional columns
**Method**: Iterates through join paths, generates JOIN strings
**Why problematic**:
- Hardcoded LEFT JOIN
- No support for INNER JOIN, RIGHT JOIN, FULL OUTER JOIN
- No optimization of join order
- Duplicate join detection is simplistic

---

## 8. JOIN CONDITION EXTRACTION (100% Python)

### 8.1 Join Condition Builder
**File**: `kg_builder/services/nl_sql_generator.py`
**Lines**: 402-455
**Function**: `_get_join_condition(table1, table2, alias1, alias2)`
**What it does**: Extracts join columns from KG and constructs JOIN condition
**Method**: Searches KG relationships, extracts columns
**Why problematic**:
- Brittle string matching
- Requires KG to be perfectly formatted
- No error handling for missing relationships
- Falls back to placeholder: `alias1.id = alias2.id` (WRONG!)

**Code**:
```python
for rel in self.kg.relationships:
    source_id = rel.source_id.lower()
    target_id = rel.target_id.lower()
    if (source_id == table1_lower or source_id == f"table_{table1_lower}"):
        source_col = rel.properties.get("source_column")
        target_col = rel.properties.get("target_column")
        return f"{alias1}.{source_col_quoted} = {alias2}.{target_col_quoted}"
```

---

## 9. IDENTIFIER QUOTING (100% Python)

### 9.1 Database-Specific Quoting
**File**: `kg_builder/services/nl_sql_generator.py`
**Lines**: 471-486
**Function**: `_quote_identifier(identifier)`
**What it does**: Quotes identifiers based on database type
**Method**: Hardcoded quoting rules
**Why problematic**:
- Limited database support
- No handling of reserved keywords
- No escaping of quotes in identifiers

**Code**:
```python
if self.db_type == "sqlserver":
    return f"[{identifier}]"
elif self.db_type == "oracle":
    return f'"{identifier}"'
else:  # mysql, postgresql
    return f"`{identifier}"`
```

---

## 10. LIMIT CLAUSE HANDLING (100% Python)

### 10.1 Database-Specific LIMIT
**File**: `kg_builder/services/nl_query_executor.py`
**Lines**: 238-271
**Function**: `_add_limit_clause(sql, limit)`
**What it does**: Adds LIMIT or TOP clause based on database
**Method**: String manipulation
**Why problematic**:
- Hardcoded SQL Server TOP syntax
- No support for OFFSET/FETCH
- Fragile string manipulation

---

## SUMMARY TABLE

| Component | File | Lines | Python | LLM | Issue |
|-----------|------|-------|--------|-----|-------|
| Classification | nl_query_classifier.py | 61-100 | ✅ | ❌ | Hardcoded keywords |
| Operation Type | nl_query_classifier.py | 102-126 | ✅ | ❌ | Hardcoded keywords |
| Table Extraction | nl_query_parser.py | 201-284 | ✅ | ❌ | Brittle patterns |
| Table Extraction (LLM) | nl_query_parser.py | 164-199 | ❌ | ✅ | Good |
| Join Columns (KG) | nl_query_parser.py | 362-419 | ✅ | ❌ | O(n) search |
| Join Columns (Schema) | nl_query_parser.py | 421-499 | ✅ | ❌ | Assumes column names |
| Join Path (BFS) | nl_query_parser.py | 772-888 | ✅ | ❌ | Simplistic scoring |
| Comparison Query | nl_sql_generator.py | 74-151 | ✅ | ❌ | Hardcoded template |
| Filter Query | nl_sql_generator.py | 153-199 | ✅ | ❌ | Hardcoded template |
| Aggregation Query | nl_sql_generator.py | 201-222 | ✅ | ❌ | Only COUNT(*) |
| Data Query | nl_sql_generator.py | 224-262 | ✅ | ❌ | Hardcoded template |
| WHERE Clause | nl_sql_generator.py | 264-297 | ✅ | ❌ | Only = operator |
| Additional Columns | nl_sql_generator.py | 299-348 | ✅ | ❌ | Regex manipulation |
| JOIN Clauses | nl_sql_generator.py | 350-400 | ✅ | ❌ | Hardcoded LEFT JOIN |
| JOIN Condition | nl_sql_generator.py | 402-455 | ✅ | ❌ | Brittle matching |
| Identifier Quoting | nl_sql_generator.py | 471-486 | ✅ | ❌ | Limited support |
| LIMIT Clause | nl_query_executor.py | 238-271 | ✅ | ❌ | String manipulation |

**Total**: 16 components, 15 Python-based, 1 LLM-based


