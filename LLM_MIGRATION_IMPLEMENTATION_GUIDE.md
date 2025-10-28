# LLM Migration Implementation Guide

## Phase 1: Direct SQL Generation via LLM (Week 1)

### 1.1 Create LLMSQLGenerator Class

**File**: `kg_builder/services/llm_sql_generator.py` (NEW)

```python
class LLMSQLGenerator:
    """Generate SQL queries using LLM instead of hardcoded templates."""
    
    def __init__(self, db_type: str = "mysql", kg: Optional["KnowledgeGraph"] = None):
        self.db_type = db_type
        self.kg = kg
        self.llm_service = get_llm_service()
    
    def generate(self, intent: QueryIntent) -> str:
        """Generate SQL using LLM."""
        if not self.llm_service.is_enabled():
            raise ValueError("LLM service not enabled")
        
        prompt = self._build_sql_generation_prompt(intent)
        response = self.llm_service.create_chat_completion(
            messages=[
                {"role": "system", "content": "You are an expert SQL developer..."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        
        sql = response.choices[0].message.content.strip()
        
        # Validate SQL
        self._validate_sql(sql, intent)
        
        return sql
    
    def _build_sql_generation_prompt(self, intent: QueryIntent) -> str:
        """Build prompt for SQL generation."""
        kg_context = self._format_kg_context()
        
        return f"""Generate a SQL query for this intent:

Query Type: {intent.query_type}
Source Table: {intent.source_table}
Target Table: {intent.target_table}
Operation: {intent.operation}
Filters: {intent.filters}
Additional Columns: {intent.additional_columns}

Knowledge Graph Context:
{kg_context}

Database Type: {self.db_type}

Requirements:
1. Use exact table names from KG
2. Use exact column names from schema
3. Use correct join conditions from KG relationships
4. Support complex WHERE clauses
5. Return ONLY valid SQL, no explanation

SQL:"""
    
    def _format_kg_context(self) -> str:
        """Format KG relationships for prompt."""
        if not self.kg:
            return "No KG available"
        
        relationships = []
        for rel in self.kg.relationships:
            relationships.append({
                "source": rel.source_id,
                "target": rel.target_id,
                "source_column": rel.properties.get("source_column"),
                "target_column": rel.properties.get("target_column"),
                "type": rel.relationship_type
            })
        
        return json.dumps(relationships, indent=2)
    
    def _validate_sql(self, sql: str, intent: QueryIntent) -> None:
        """Validate generated SQL."""
        # Check for required tables
        for table in [intent.source_table, intent.target_table]:
            if table and table.lower() not in sql.lower():
                raise ValueError(f"Generated SQL missing table: {table}")
        
        # Check for SQL injection patterns
        dangerous_patterns = ["DROP", "DELETE", "TRUNCATE", "ALTER"]
        for pattern in dangerous_patterns:
            if pattern in sql.upper():
                raise ValueError(f"Dangerous SQL pattern detected: {pattern}")
```

### 1.2 Update NLSQLGenerator to Support Fallback

**File**: `kg_builder/services/nl_sql_generator.py`

```python
class NLSQLGenerator:
    def __init__(self, db_type: str = "mysql", kg: Optional["KnowledgeGraph"] = None, use_llm: bool = False):
        self.db_type = db_type
        self.kg = kg
        self.use_llm = use_llm
        
        if use_llm:
            from kg_builder.services.llm_sql_generator import LLMSQLGenerator
            self.llm_generator = LLMSQLGenerator(db_type, kg)
        else:
            self.llm_generator = None
    
    def generate(self, intent: QueryIntent) -> str:
        """Generate SQL with optional LLM fallback."""
        if self.use_llm and self.llm_generator:
            try:
                return self.llm_generator.generate(intent)
            except Exception as e:
                logger.warning(f"LLM generation failed, falling back to Python: {e}")
                return self._generate_python(intent)
        else:
            return self._generate_python(intent)
    
    def _generate_python(self, intent: QueryIntent) -> str:
        """Original Python-based generation."""
        # ... existing code ...
```

### 1.3 Update Routes to Use LLM Generator

**File**: `kg_builder/routes.py`

```python
@app.post("/v1/landing-kpi/execute-nl-query")
async def execute_nl_query(request: NLQueryRequest):
    # ... existing code ...
    
    # Use LLM generator if enabled
    use_llm = request.use_llm if hasattr(request, 'use_llm') else False
    generator = get_nl_sql_generator(db_type, kg=kg, use_llm=use_llm)
    
    # ... rest of code ...
```

---

## Phase 2: WHERE Clause Intelligence (Week 2)

### 2.1 Extend QueryIntent for Operators

**File**: `kg_builder/models.py`

```python
@dataclass
class Filter:
    column: str
    operator: str  # =, >, <, >=, <=, LIKE, IN, BETWEEN, IS NULL
    value: Any
    logic: str = "AND"  # AND, OR

@dataclass
class QueryIntent:
    # ... existing fields ...
    filters: List[Filter] = None  # Changed from Dict to Filter objects
```

### 2.2 Update LLM Parser to Extract Operators

**File**: `kg_builder/services/nl_query_parser.py`

```python
def _build_parsing_prompt(self, definition: str, ...) -> str:
    """Updated prompt to extract operators."""
    return f"""...
FILTER EXTRACTION:
For each filter, extract:
- column: The column name
- operator: =, >, <, >=, <=, LIKE, IN, BETWEEN, IS NULL
- value: The filter value
- logic: AND or OR

Example:
"Show active products created after 2024-01-01"
→ filters: [
    {{"column": "status", "operator": "=", "value": "active", "logic": "AND"}},
    {{"column": "created_date", "operator": ">", "value": "2024-01-01", "logic": "AND"}}
  ]
..."""
```

### 2.3 Update WHERE Clause Builder

**File**: `kg_builder/services/nl_sql_generator.py`

```python
def _build_where_clause(self, filters: List[Filter], table_alias: Optional[str] = None) -> str:
    """Build WHERE clause with operator support."""
    conditions = []
    
    for filter_item in filters:
        column = self._quote_identifier(filter_item.column)
        operator = filter_item.operator
        value = filter_item.value
        
        if table_alias:
            column = f"{table_alias}.{column}"
        
        # Handle different operators
        if operator == "=":
            condition = f"{column} = '{value}'"
        elif operator == ">":
            condition = f"{column} > '{value}'"
        elif operator == "<":
            condition = f"{column} < '{value}'"
        elif operator == "LIKE":
            condition = f"{column} LIKE '%{value}%'"
        elif operator == "IN":
            values = ",".join([f"'{v}'" for v in value])
            condition = f"{column} IN ({values})"
        elif operator == "BETWEEN":
            condition = f"{column} BETWEEN '{value[0]}' AND '{value[1]}'"
        elif operator == "IS NULL":
            condition = f"{column} IS NULL"
        else:
            condition = f"{column} = '{value}'"
        
        conditions.append(condition)
    
    logic = filters[0].logic if filters else "AND"
    return f" {logic} ".join(conditions) if conditions else "1=1"
```

---

## Phase 3: JOIN Path Optimization (Week 3)

### 3.1 Create LLM-Based Path Scorer

**File**: `kg_builder/services/llm_path_optimizer.py` (NEW)

```python
class LLMPathOptimizer:
    """Use LLM to optimize join paths."""
    
    def __init__(self, kg: Optional["KnowledgeGraph"] = None):
        self.kg = kg
        self.llm_service = get_llm_service()
    
    def score_paths(self, source: str, target: str, paths: List[List[str]]) -> List[str]:
        """Score and rank paths using LLM."""
        if not self.llm_service.is_enabled():
            # Fallback to BFS scoring
            return self._score_paths_python(paths)
        
        prompt = f"""Score these join paths from {source} to {target}:

Paths:
{json.dumps(paths, indent=2)}

Knowledge Graph:
{self._format_kg_context()}

Score each path 0-100 based on:
1. Relationship strength
2. Column cardinality
3. Query performance
4. Semantic correctness

Return JSON:
[
  {{"path": [...], "score": 85, "reason": "..."}},
  ...
]
"""
        
        response = self.llm_service.create_chat_completion(
            messages=[
                {"role": "system", "content": "You are a SQL optimization expert..."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        
        # Parse and return best path
        result = json.loads(response.choices[0].message.content)
        best = max(result, key=lambda x: x["score"])
        return best["path"]
```

---

## Phase 4: Complex Query Support (Week 4)

### 4.1 Extend QueryIntent for Complex Queries

**File**: `kg_builder/models.py`

```python
@dataclass
class QueryIntent:
    # ... existing fields ...
    group_by_columns: List[str] = None
    having_conditions: List[Filter] = None
    order_by: List[Dict[str, str]] = None  # [{"column": "name", "direction": "ASC"}]
    limit: int = None
    offset: int = None
```

### 4.2 Update LLM Parser

**File**: `kg_builder/services/nl_query_parser.py`

```python
def _build_parsing_prompt(self, definition: str, ...) -> str:
    """Updated prompt for complex queries."""
    return f"""...
COMPLEX QUERY EXTRACTION:
- group_by_columns: Columns to group by
- having_conditions: Conditions on aggregates
- order_by: Sort order
- limit: Result limit

Example:
"Show top 10 products by sales, ordered by revenue descending"
→ group_by_columns: ["product_id"]
→ order_by: [{{"column": "revenue", "direction": "DESC"}}]
→ limit: 10
..."""
```

---

## Testing Strategy

### Unit Tests
```python
def test_llm_sql_generation():
    intent = QueryIntent(
        query_type="comparison_query",
        source_table="table_a",
        target_table="table_b",
        operation="NOT_IN"
    )
    generator = LLMSQLGenerator(kg=kg)
    sql = generator.generate(intent)
    assert "SELECT" in sql
    assert "table_a" in sql
    assert "table_b" in sql

def test_llm_fallback():
    generator = NLSQLGenerator(use_llm=True)
    # Simulate LLM failure
    sql = generator.generate(intent)
    # Should fall back to Python
    assert sql is not None
```

### Integration Tests
```python
def test_end_to_end_llm():
    definition = "Show products in RBP not in OPS"
    parser = NLQueryParser(kg=kg, use_llm=True)
    intent = parser.parse(definition)
    
    generator = NLSQLGenerator(use_llm=True, kg=kg)
    sql = generator.generate(intent)
    
    executor = NLQueryExecutor(kg=kg)
    result = executor.execute(intent, connection)
    assert result.record_count >= 0
```

---

## Rollout Plan

1. **Week 1**: Deploy LLMSQLGenerator with fallback, 10% traffic
2. **Week 2**: Monitor performance, increase to 50% traffic
3. **Week 3**: Add WHERE clause intelligence, 100% traffic
4. **Week 4**: Add complex query support, full rollout

---

## Success Metrics

- SQL generation accuracy: >95%
- Fallback rate: <5%
- Query execution success rate: >90%
- Performance: <500ms per query
- Cost: <$0.01 per query


