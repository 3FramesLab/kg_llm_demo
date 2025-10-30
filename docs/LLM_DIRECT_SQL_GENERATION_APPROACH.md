# LLM Direct SQL Generation Approach

## Current Architecture vs Proposed Architecture

### Current Flow (Template-Based)
```
Natural Language Query
    ↓
[LLM] Parse → Extract tables, filters, operations
    ↓
[Python] Template-Based SQL Generation (nl_sql_generator.py)
    ↓
Generated SQL Query
```

**Problem:** Python templates are rigid and limited to predefined patterns.

---

### Proposed Flow (LLM Direct Generation)
```
Natural Language Query
    ↓
[LLM] Direct SQL Generation with Full Schema Context
    ↓
Generated SQL Query
```

**Benefit:** LLM understands context and can generate complex SQL directly.

---

## Architecture Comparison

| Aspect | Current (Template-Based) | Proposed (LLM Direct) |
|--------|-------------------------|---------------------|
| **SQL Generation** | Python hardcoded templates | LLM generates entire SQL |
| **Flexibility** | Limited to predefined patterns | Handles any query complexity |
| **Schema Context** | Minimal (only join columns) | Full context (tables, columns, relationships) |
| **Complex Queries** | Requires new templates | Automatic |
| **Accuracy** | 100% (if template exists) | 90-95% (with validation) |
| **Fallback** | None | Can fallback to templates |

---

## Implementation Approach

### Step 1: Create `LLMSQLGenerator` Class

**File:** `kg_builder/services/llm_sql_generator.py`

```python
class LLMSQLGenerator:
    """Generate SQL directly using LLM with full schema context."""

    def __init__(self, db_type: str, kg: KnowledgeGraph):
        self.db_type = db_type
        self.kg = kg
        self.llm_service = get_llm_service()

    def generate_sql(self, nl_query: str) -> Dict[str, Any]:
        """
        Generate SQL directly from natural language.

        Returns:
        {
            "sql": "SELECT ...",
            "confidence": 0.95,
            "explanation": "...",
            "error": None
        }
        """
```

---

### Step 2: Build Schema Context

The LLM needs **full visibility** into:

1. **Available Tables**
   - Table names
   - Column names (all columns)
   - Table aliases (business names)

2. **Relationships**
   - Which tables can be joined
   - Join columns (source_column ←→ target_column)
   - Relationship types (MATCHES, REFERENCES, etc.)

3. **Database Type**
   - Syntax rules (MySQL vs SQL Server vs Oracle)
   - Quoting rules (backticks vs brackets vs quotes)

**Example Schema Context:**
```json
{
  "database_type": "sqlserver",
  "tables": [
    {
      "name": "brz_lnd_RBP_GPU",
      "aliases": ["RBP", "RBP GPU"],
      "columns": ["Material", "Material_Desc", "Status", "Quantity"]
    },
    {
      "name": "brz_lnd_OPS_EXCEL_GPU",
      "aliases": ["OPS", "OPS Excel"],
      "columns": ["PLANNING_SKU", "GPU_MODEL", "Status"]
    }
  ],
  "relationships": [
    {
      "source_table": "brz_lnd_RBP_GPU",
      "source_column": "Material",
      "target_table": "brz_lnd_OPS_EXCEL_GPU",
      "target_column": "PLANNING_SKU",
      "type": "MATCHES"
    }
  ]
}
```

---

### Step 3: Build LLM Prompt

**Prompt Template:**
```
Generate a SQL query for the following natural language request:

**Natural Language Query:**
"Show me all products in RBP but not in OPS where status is active"

**Database Type:** SQL Server
**Use these quote characters:** [brackets]

**Available Tables:**
  - brz_lnd_RBP_GPU (also called: RBP, RBP GPU)
    Columns: [Material, Material_Desc, Status, Quantity, ...]

  - brz_lnd_OPS_EXCEL_GPU (also called: OPS, OPS Excel)
    Columns: [PLANNING_SKU, GPU_MODEL, Status, ...]

**Known Relationships (JOIN conditions):**
  - brz_lnd_RBP_GPU.Material ←→ brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU

**Requirements:**
1. Generate a complete, executable SQL query
2. Use the EXACT table and column names from the schema
3. For "not in" queries, use LEFT JOIN with IS NULL
4. For "in both" queries, use INNER JOIN
5. Use SQL Server syntax with [brackets] for identifiers
6. Add WHERE clauses for filters

**Output Format (JSON only, no markdown):**
{
    "sql": "SELECT ... FROM ...",
    "confidence": 0.95,
    "explanation": "This query finds...",
    "tables_used": ["brz_lnd_RBP_GPU", "brz_lnd_OPS_EXCEL_GPU"],
    "join_columns": ["Material", "PLANNING_SKU"]
}
```

---

### Step 4: LLM Response Example

**LLM Returns:**
```json
{
    "sql": "SELECT DISTINCT s.* FROM [brz_lnd_RBP_GPU] s LEFT JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU] WHERE t.[PLANNING_SKU] IS NULL AND s.[Status] = 'active'",
    "confidence": 0.95,
    "explanation": "This query finds all products that exist in RBP table but not in OPS table by using a LEFT JOIN and checking for NULL values in the target table. Additionally filters for active status.",
    "tables_used": ["brz_lnd_RBP_GPU", "brz_lnd_OPS_EXCEL_GPU"],
    "join_columns": ["Material", "PLANNING_SKU"]
}
```

---

### Step 5: Validation & Fallback

**Validation Steps:**
1. Check SQL is not empty
2. Verify contains SELECT and FROM
3. Check for dangerous keywords (DROP, DELETE, TRUNCATE)
4. Verify confidence score > 0.7

**Fallback Strategy:**
```python
def generate_sql_with_fallback(nl_query: str, kg: KnowledgeGraph):
    # Try LLM first
    llm_result = llm_sql_generator.generate_sql(nl_query)

    if llm_result["sql"] and llm_result["confidence"] > 0.7:
        # Validate
        validation = validate_sql(llm_result["sql"])
        if validation["is_valid"]:
            return llm_result["sql"]  # ✅ Use LLM-generated SQL

    # Fallback to template-based if LLM fails
    logger.warning("LLM SQL generation failed, falling back to templates")
    intent = parse_query(nl_query)  # Parse using existing logic
    return template_sql_generator.generate(intent)  # 🔄 Use old templates
```

---

## Integration Points

### Option 1: Add to Landing KPI Executor (Recommended)

**File:** `kg_builder/services/landing_kpi_executor.py`

**Change:**
```python
# Current (Line ~188)
executor = get_nl_query_executor(db_type, kg=kg)
query_result = executor.execute(intent, connection, limit=limit)

# Proposed
if use_llm and llm_service.is_enabled():
    # Use LLM direct SQL generation
    llm_generator = get_llm_sql_generator(db_type, kg=kg)
    sql_result = llm_generator.generate_sql(nl_definition)

    if sql_result["sql"] and sql_result["confidence"] > 0.7:
        # Execute LLM-generated SQL directly
        query_result = execute_sql_directly(sql_result["sql"], connection, limit)
    else:
        # Fallback to template-based
        logger.warning("LLM confidence too low, using templates")
        executor = get_nl_query_executor(db_type, kg=kg)
        query_result = executor.execute(intent, connection, limit=limit)
else:
    # Use template-based (existing logic)
    executor = get_nl_query_executor(db_type, kg=kg)
    query_result = executor.execute(intent, connection, limit=limit)
```

---

### Option 2: Add to NL Query Executor

**File:** `kg_builder/services/nl_query_executor.py`

**Change:**
```python
class NLQueryExecutor:
    def execute(self, intent: QueryIntent, connection, limit: int):
        # NEW: Try LLM direct SQL first
        if self.use_llm and self.llm_service.is_enabled():
            sql = self._generate_sql_with_llm(intent.definition)
            if sql:
                return self._execute_sql(sql, connection, limit)

        # Fallback to template-based
        sql = self.generator.generate(intent)  # Old way
        return self._execute_sql(sql, connection, limit)
```

---

## Benefits

### ✅ Advantages

1. **Flexibility**
   - Handles complex queries without new templates
   - Understands context and nuance
   - Adapts to different query styles

2. **Natural Language Understanding**
   - Better interpretation of user intent
   - Handles synonyms and variations
   - Can infer implicit requirements

3. **Reduced Maintenance**
   - No need to create new templates for each query type
   - LLM adapts to new requirements automatically

4. **Better Explanations**
   - LLM provides explanations of what the SQL does
   - Helps users understand the query logic

### ⚠️ Challenges

1. **Accuracy**
   - LLM might generate incorrect SQL (90-95% accuracy)
   - Need validation and testing

2. **Cost**
   - More LLM API calls = higher costs
   - Consider caching common queries

3. **Latency**
   - LLM calls take 1-3 seconds
   - Template-based is instant

4. **Dependency**
   - Requires LLM service to be available
   - Need fallback for when LLM is down

---

## Recommended Implementation Plan

### Phase 1: Core Implementation (Week 1)
- [ ] Create `llm_sql_generator.py` with `LLMSQLGenerator` class
- [ ] Implement schema context building from KG
- [ ] Build LLM prompt template
- [ ] Add response parsing and validation

### Phase 2: Integration (Week 1)
- [ ] Add LLM SQL generation option to `landing_kpi_executor.py`
- [ ] Implement fallback to template-based generator
- [ ] Add confidence threshold configuration
- [ ] Update execution parameters to include `use_llm_direct_sql` flag

### Phase 3: Testing & Validation (Week 2)
- [ ] Test with existing KPI definitions
- [ ] Compare LLM-generated SQL vs template-based SQL
- [ ] Measure accuracy and performance
- [ ] Tune confidence thresholds

### Phase 4: UI Updates (Week 2)
- [ ] Add toggle in UI: "Use LLM Direct SQL Generation"
- [ ] Show LLM-generated SQL with explanation
- [ ] Add option to edit LLM-generated SQL before execution
- [ ] Display confidence scores

### Phase 5: Optimization (Week 3)
- [ ] Add SQL caching for common queries
- [ ] Implement query result caching
- [ ] Add metrics tracking (accuracy, latency, cost)
- [ ] Create monitoring dashboard

---

## Configuration

Add to execution parameters:

```python
{
    "kg_name": "material_kg",
    "schemas": ["schema1"],
    "use_llm": true,
    "use_llm_direct_sql": true,  # NEW FLAG
    "llm_sql_confidence_threshold": 0.7,  # Minimum confidence
    "fallback_to_templates": true,  # Enable fallback
    "db_type": "sqlserver",
    "limit": 1000
}
```

---

## Example End-to-End Flow

### Input
```
Natural Language: "Show me all inactive products in RBP but not in OPS"
KG: material_kg (with RBP ←→ OPS relationships)
DB Type: SQL Server
```

### Step 1: Build Context
```json
{
  "tables": ["brz_lnd_RBP_GPU", "brz_lnd_OPS_EXCEL_GPU"],
  "relationships": [
    {"source": "brz_lnd_RBP_GPU.Material", "target": "brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU"}
  ]
}
```

### Step 2: LLM Generates SQL
```sql
SELECT DISTINCT s.*
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_OPS_EXCEL_GPU] t
  ON s.[Material] = t.[PLANNING_SKU]
WHERE t.[PLANNING_SKU] IS NULL
  AND s.[Status] = 'inactive'
```

### Step 3: Validate & Execute
- ✅ Validation passes
- ✅ Confidence: 0.95
- ✅ Execute on database
- ✅ Return 42 records

### Step 4: Store Results
```json
{
  "execution_id": 123,
  "sql_query": "SELECT DISTINCT s.* FROM ...",
  "record_count": 42,
  "execution_time_ms": 1234.56,
  "status": "success",
  "llm_generated": true,
  "llm_confidence": 0.95,
  "llm_explanation": "This query finds inactive products..."
}
```

---

## Code Files to Create/Modify

### New Files
1. **`kg_builder/services/llm_sql_generator.py`**
   - `LLMSQLGenerator` class
   - `generate_sql()` method
   - `_build_schema_context()` method
   - `_build_sql_generation_prompt()` method
   - `validate_sql()` method

### Modified Files
1. **`kg_builder/services/landing_kpi_executor.py`**
   - Add LLM SQL generation path
   - Add fallback logic
   - Update execution flow

2. **`kg_builder/services/landing_kpi_service.py`**
   - Add `llm_generated` field to execution results
   - Add `llm_confidence` field
   - Add `llm_explanation` field

3. **`web-app/src/pages/LandingKPI.js`**
   - Add "Use LLM Direct SQL" checkbox
   - Show LLM confidence and explanation
   - Allow SQL editing before execution

---

## Testing Strategy

### Unit Tests
```python
def test_llm_sql_generator():
    kg = load_test_kg()
    generator = LLMSQLGenerator(db_type="sqlserver", kg=kg)

    result = generator.generate_sql("Show products in RBP but not in OPS")

    assert result["sql"] is not None
    assert "LEFT JOIN" in result["sql"]
    assert "IS NULL" in result["sql"]
    assert result["confidence"] > 0.7
```

### Integration Tests
```python
def test_kpi_execution_with_llm_sql():
    kpi = create_test_kpi("Products not in both systems")
    params = {
        "kg_name": "test_kg",
        "use_llm_direct_sql": True
    }

    result = execute_kpi(kpi, params)

    assert result["execution_status"] == "success"
    assert result["llm_generated"] == True
    assert result["record_count"] > 0
```

---

## Monitoring & Metrics

Track these metrics:

1. **Accuracy**
   - % of LLM-generated SQL that executes successfully
   - % of queries that fallback to templates
   - User corrections needed

2. **Performance**
   - LLM generation time (avg, p95, p99)
   - SQL execution time
   - End-to-end latency

3. **Cost**
   - LLM API calls per day
   - Tokens used per query
   - Total monthly cost

4. **Quality**
   - Confidence score distribution
   - User satisfaction ratings
   - Query result accuracy

---

## Future Enhancements

1. **Query Optimization**
   - LLM suggests indexes
   - Identifies slow queries
   - Recommends query improvements

2. **Multi-Step Queries**
   - Break complex queries into steps
   - Use CTEs and subqueries
   - Handle aggregations better

3. **Query Learning**
   - Store successful LLM-generated queries
   - Build a query cache
   - Learn from user corrections

4. **Interactive Refinement**
   - User reviews LLM SQL before execution
   - User can modify and re-submit
   - System learns from modifications

---

## Conclusion

**Recommendation:** Implement LLM Direct SQL Generation with fallback to templates.

This approach provides:
- ✅ Maximum flexibility for complex queries
- ✅ Better natural language understanding
- ✅ Reduced maintenance overhead
- ✅ Safe fallback mechanism
- ✅ Gradual migration path (can run both approaches in parallel)

**Next Steps:**
1. Create `llm_sql_generator.py` implementation
2. Integrate into `landing_kpi_executor.py`
3. Test with existing KPIs
4. Monitor accuracy and performance
5. Iterate based on results
