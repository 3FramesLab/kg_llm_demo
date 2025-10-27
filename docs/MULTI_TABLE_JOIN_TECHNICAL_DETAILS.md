# Multi-Table Join: Technical Deep Dive

## 🔴 Issue: Only 2-Table Joins Supported

Your scenario requires:
```
brz_lnd_RBP_GPU (source)
  ↓ JOIN on (material, planning_sku, active_inactive)
brz_lnd_OPS_EXCEL_GPU
  ↓ JOIN on (material, planning_sku, active_inactive)
brz_lnd_SKU_LIFNR_Excel
  ↓ JOIN on (material)
hana_material_master (enrichment)
```

But system only generates:
```
brz_lnd_RBP_GPU → hana_material_master
```

---

## 🔍 Code Analysis

### 1. SQL Generation (reconciliation_executor.py:435-502)

**Current Code**:
```python
def _execute_matched_query(self, source_conn, target_conn, rule, limit):
    # Build JOIN query
    join_conditions = []
    for src_col, tgt_col in zip(rule.source_columns, rule.target_columns):
        join_conditions.append(f"s.{src_col} = t.{tgt_col}")
    
    join_condition = ' AND '.join(join_conditions)
    
    # ONLY 2 tables: source (s) and target (t)
    query = f"""
    SELECT s.*, t.*
    FROM {source_table} s
    INNER JOIN {target_table} t
        ON {join_condition}
    LIMIT {limit}
    """
```

**Problem**: 
- Only `s` (source) and `t` (target) aliases
- Cannot reference additional tables
- No support for chaining joins

**What's Needed**:
```python
# Support multiple tables
query = f"""
SELECT t1.*, t2.*, t3.*, t4.*
FROM table1 t1
INNER JOIN table2 t2 ON t1.col = t2.col
INNER JOIN table3 t3 ON t2.col = t3.col
LEFT JOIN table4 t4 ON t1.col = t4.col
"""
```

---

### 2. Rule Model (models.py:ReconciliationRule)

**Current Structure**:
```python
class ReconciliationRule(BaseModel):
    source_schema: str
    source_table: str
    source_columns: List[str]
    target_schema: str
    target_table: str
    target_columns: List[str]
    # Only 2 tables!
```

**Problem**:
- Only stores source and target
- Cannot represent multi-table joins
- No join order information

**What's Needed**:
```python
class ReconciliationRule(BaseModel):
    # Current 2-table fields (keep for backward compatibility)
    source_table: str
    target_table: str
    
    # NEW: Multi-table support
    join_tables: Optional[List[str]] = None  # [table1, table2, table3]
    join_conditions: Optional[List[Dict]] = None  # Join conditions
    join_order: Optional[List[str]] = None  # Order to join
    join_type: Optional[List[str]] = None  # INNER, LEFT, RIGHT for each join
```

---

### 3. Rule Generation (reconciliation_service.py:208-364)

**Current Logic**:
```python
def _generate_pattern_based_rules(self, relationships, schemas_info, schema_names):
    for rel in relevant_rels:
        source_table = rel.get('source_table')
        target_table = rel.get('target_table')
        
        # Creates single rule: source → target
        rules.append(ReconciliationRule(
            source_table=source_table,
            target_table=target_table,
            # ...
        ))
```

**Problem**:
- Iterates through relationships one by one
- Each relationship becomes a separate 2-table rule
- Doesn't group related tables

**What's Needed**:
```python
# Group related tables based on field preferences
# Example: If field_preferences says:
# - brz_lnd_RBP_GPU: priority_fields = ["Material"]
# - brz_lnd_OPS_EXCEL_GPU: priority_fields = ["PLANNING_SKU"]
# - brz_lnd_SKU_LIFNR_Excel: priority_fields = ["Material"]
# Then create a multi-table rule joining all 3

def _generate_multi_table_rules(self, relationships, field_preferences):
    # Group tables by common join fields
    table_groups = self._group_tables_by_join_fields(field_preferences)
    
    for group in table_groups:
        # Create multi-table rule
        rule = ReconciliationRule(
            join_tables=group['tables'],
            join_conditions=group['conditions'],
            join_order=group['order']
        )
```

---

### 4. LLM Prompt (multi_schema_llm_service.py:544-678)

**Current Prompt**:
```python
"sql_template": "SELECT * FROM table1 t1 JOIN table2 t2 ON t1.col1 = t2.col1"
```

**Problem**:
- Only shows 2-table example
- LLM generates 2-table rules
- Doesn't mention multi-table joins

**What's Needed**:
```python
# Add multi-table examples to prompt
"sql_template_multi": """
SELECT t1.*, t2.*, t3.*, t4.*
FROM brz_lnd_RBP_GPU t1
INNER JOIN brz_lnd_OPS_EXCEL_GPU t2 
    ON t1.material = t2.material 
    AND t1.planning_sku = t2.planning_sku
INNER JOIN brz_lnd_SKU_LIFNR_Excel t3
    ON t1.material = t3.material
LEFT JOIN hana_material_master t4
    ON t1.material = t4.material
"""

# Add instructions
"MULTI-TABLE JOINS: If multiple tables share common join fields, create a single rule that joins all of them together. This is more efficient than creating separate 2-table rules."
```

---

### 5. Field Preferences Not Used for Join Order

**Current Usage** (multi_schema_llm_service.py:558-594):
```python
# Field preferences are parsed but only used for:
# - Priority fields (mentioned in prompt)
# - Exclude fields (mentioned in prompt)
# - Filter hints (mentioned in prompt)

# NOT used for:
# - Determining which tables to join together
# - Determining join order
# - Determining join type (INNER vs LEFT)
```

**What's Needed**:
```python
# Use field preferences to guide multi-table joins
def _determine_join_order(self, field_preferences, relationships):
    # Priority fields → join first
    # Common fields → join together
    # Enrichment tables → join last with LEFT JOIN
    
    join_order = []
    for pref in field_preferences:
        table = pref['table_name']
        priority = pref.get('priority_fields', [])
        if priority:
            join_order.append((table, 'INNER'))  # High priority = INNER JOIN
    
    # Enrichment tables (hana_material_master) → LEFT JOIN
    for table in all_tables:
        if table not in join_order:
            join_order.append((table, 'LEFT'))
    
    return join_order
```

---

## 📊 Comparison: Current vs Proposed

| Aspect | Current | Proposed |
|--------|---------|----------|
| **Tables per rule** | 2 (source, target) | N (unlimited) |
| **Join types** | INNER only | INNER, LEFT, RIGHT, FULL |
| **Join order** | N/A | Configurable |
| **Field preferences** | Mentioned in prompt | Used to determine joins |
| **SQL complexity** | Simple 2-table | Complex multi-table |
| **Rule model** | Simple | Extended |

---

## 🎯 Implementation Priority

1. **HIGH**: Extend ReconciliationRule model
2. **HIGH**: Update SQL generation for multi-table joins
3. **MEDIUM**: Enhance rule generation logic
4. **MEDIUM**: Update LLM prompt with examples
5. **LOW**: Use field preferences for join order

---

## 🔗 Files to Modify

1. `kg_builder/models.py` - Add multi-table fields
2. `kg_builder/services/reconciliation_executor.py` - Multi-table SQL
3. `kg_builder/services/reconciliation_service.py` - Multi-table rules
4. `kg_builder/services/multi_schema_llm_service.py` - LLM prompt
5. `kg_builder/services/landing_query_builder.py` - Query building


