# Multi-Table Join: Code Examples

## 🎯 Your Scenario

```
brz_lnd_RBP_GPU 
  ↓ JOIN on (material, planning_sku, active_inactive)
brz_lnd_OPS_EXCEL_GPU
  ↓ JOIN on (material, planning_sku, active_inactive)
brz_lnd_SKU_LIFNR_Excel
  ↓ JOIN on (material)
hana_material_master (enrichment)
```

---

## 📝 Current Code (2-Table Only)

### SQL Generation (reconciliation_executor.py:435-502)

```python
def _execute_matched_query(self, source_conn, target_conn, rule, limit):
    """Execute query to find matched records."""
    
    # Build JOIN query
    join_conditions = []
    for src_col, tgt_col in zip(rule.source_columns, rule.target_columns):
        join_conditions.append(f"s.{src_col} = t.{tgt_col}")
    
    join_condition = ' AND '.join(join_conditions)
    
    # PROBLEM: Only 2 tables (s and t)
    query = f"""
    SELECT s.*, t.*
    FROM {source_table} s
    INNER JOIN {target_table} t
        ON {join_condition}
    LIMIT {limit}
    """
    
    cursor = source_conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()
```

---

## ✅ Proposed Code (Multi-Table)

### 1. Enhanced Rule Model

```python
# kg_builder/models.py

class ReconciliationRule(BaseModel):
    # Keep existing fields for backward compatibility
    source_table: Optional[str] = None
    target_table: Optional[str] = None
    source_columns: Optional[List[str]] = None
    target_columns: Optional[List[str]] = None
    
    # NEW: Multi-table support
    join_tables: Optional[List[str]] = None
    join_conditions: Optional[List[Dict[str, Any]]] = None
    join_order: Optional[List[str]] = None
    join_type: Optional[List[str]] = None  # INNER, LEFT, RIGHT
    
    def is_multi_table(self) -> bool:
        """Check if this is a multi-table rule."""
        return self.join_tables is not None and len(self.join_tables) > 2
```

---

### 2. Enhanced SQL Generation

```python
# kg_builder/services/reconciliation_executor.py

def _execute_matched_query(self, source_conn, target_conn, rule, limit):
    """Execute query to find matched records (multi-table support)."""
    
    if rule.is_multi_table():
        return self._execute_multi_table_query(source_conn, rule, limit)
    else:
        return self._execute_two_table_query(source_conn, target_conn, rule, limit)

def _execute_multi_table_query(self, source_conn, rule, limit):
    """Execute multi-table join query."""
    
    # Build SELECT clause
    select_parts = []
    for i, table in enumerate(rule.join_order, 1):
        select_parts.append(f"t{i}.*")
    select_clause = ", ".join(select_parts)
    
    # Build FROM clause
    from_clause = f"FROM {rule.join_tables[0]} t1"
    
    # Build JOIN clauses
    join_clauses = []
    for i, condition in enumerate(rule.join_conditions, 1):
        table1_idx = rule.join_order.index(condition['table1']) + 1
        table2_idx = rule.join_order.index(condition['table2']) + 1
        join_type = rule.join_type[i-1] if rule.join_type else "INNER"
        
        join_clauses.append(
            f"{join_type} JOIN {condition['table2']} t{table2_idx} "
            f"ON {condition['on']}"
        )
    
    join_clause = "\n".join(join_clauses)
    
    # Build complete query
    query = f"""
    SELECT {select_clause}
    {from_clause}
    {join_clause}
    LIMIT {limit}
    """
    
    cursor = source_conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()
```

---

### 3. Enhanced Rule Generation

```python
# kg_builder/services/reconciliation_service.py

def _generate_multi_table_rules(self, relationships, field_preferences):
    """Generate multi-table rules from field preferences."""
    
    rules = []
    
    # Group tables by common join fields
    table_groups = self._group_tables_by_join_fields(
        relationships, field_preferences
    )
    
    for group in table_groups:
        # Determine join order (priority fields first)
        join_order = self._determine_join_order(group['tables'], field_preferences)
        
        # Build join conditions
        join_conditions = []
        for i in range(len(join_order) - 1):
            table1 = join_order[i]
            table2 = join_order[i + 1]
            
            # Find relationship between these tables
            rel = self._find_relationship(table1, table2, relationships)
            if rel:
                join_conditions.append({
                    'table1': table1,
                    'table2': table2,
                    'on': self._build_join_condition(rel)
                })
        
        # Determine join types
        join_types = []
        for i, table in enumerate(join_order):
            if i == 0:
                join_types.append('INNER')  # First table
            elif self._is_enrichment_table(table, field_preferences):
                join_types.append('LEFT')  # Enrichment tables
            else:
                join_types.append('INNER')  # Regular tables
        
        # Create multi-table rule
        rule = ReconciliationRule(
            rule_id=f"RULE_{generate_uid()}",
            rule_name=f"MultiTable_{'_'.join(join_order)}",
            join_tables=group['tables'],
            join_conditions=join_conditions,
            join_order=join_order,
            join_type=join_types,
            confidence_score=0.85,
            reasoning="Multi-table join rule",
            validation_status="VALID",
            llm_generated=False
        )
        
        rules.append(rule)
    
    return rules

def _group_tables_by_join_fields(self, relationships, field_preferences):
    """Group tables that share common join fields."""
    
    groups = []
    
    # Extract priority fields from field preferences
    priority_tables = {}
    for pref in field_preferences:
        table = pref['table_name']
        priority_fields = pref.get('priority_fields', [])
        if priority_fields:
            priority_tables[table] = priority_fields
    
    # Group tables by common fields
    for table1, fields1 in priority_tables.items():
        group = {'tables': [table1], 'fields': fields1}
        
        for table2, fields2 in priority_tables.items():
            if table1 != table2:
                # Check if tables share common fields
                common_fields = set(fields1) & set(fields2)
                if common_fields:
                    group['tables'].append(table2)
        
        # Add enrichment tables
        for pref in field_preferences:
            table = pref['table_name']
            if table not in group['tables'] and 'enrichment' in pref.get('type', ''):
                group['tables'].append(table)
        
        groups.append(group)
    
    return groups
```

---

### 4. Enhanced LLM Prompt

```python
# kg_builder/services/multi_schema_llm_service.py

def _build_reconciliation_rules_prompt(self, relationships, schemas_info, field_preferences):
    """Build prompt for reconciliation rule generation (multi-table support)."""
    
    # ... existing code ...
    
    # Add multi-table examples
    multi_table_example = """
    MULTI-TABLE JOIN EXAMPLE:
    If you have these tables with common fields:
    - brz_lnd_RBP_GPU (material, planning_sku)
    - brz_lnd_OPS_EXCEL_GPU (material, planning_sku)
    - brz_lnd_SKU_LIFNR_Excel (material)
    - hana_material_master (material) [enrichment]
    
    Create a SINGLE multi-table rule:
    {
      "join_tables": ["brz_lnd_RBP_GPU", "brz_lnd_OPS_EXCEL_GPU", "brz_lnd_SKU_LIFNR_Excel", "hana_material_master"],
      "join_conditions": [
        {"table1": "brz_lnd_RBP_GPU", "table2": "brz_lnd_OPS_EXCEL_GPU", "on": "material=material AND planning_sku=planning_sku"},
        {"table1": "brz_lnd_OPS_EXCEL_GPU", "table2": "brz_lnd_SKU_LIFNR_Excel", "on": "material=material"},
        {"table1": "brz_lnd_RBP_GPU", "table2": "hana_material_master", "on": "material=material"}
      ],
      "join_order": ["brz_lnd_RBP_GPU", "brz_lnd_OPS_EXCEL_GPU", "brz_lnd_SKU_LIFNR_Excel", "hana_material_master"],
      "join_type": ["INNER", "INNER", "INNER", "LEFT"]
    }
    """
    
    return f"""... existing prompt ...
    
    {multi_table_example}
    
    IMPORTANT: If multiple tables share common join fields, create a SINGLE multi-table rule
    instead of multiple 2-table rules. This is more efficient and accurate.
    """
```

---

## 🎯 Expected Output

### Generated SQL

```sql
SELECT t1.*, t2.*, t3.*, t4.*
FROM brz_lnd_RBP_GPU t1
INNER JOIN brz_lnd_OPS_EXCEL_GPU t2 
    ON t1.material = t2.material 
    AND t1.planning_sku = t2.planning_sku
    AND t1.active_inactive = t2.active_inactive
INNER JOIN brz_lnd_SKU_LIFNR_Excel t3
    ON t2.material = t3.material
LEFT JOIN hana_material_master t4
    ON t1.material = t4.material
LIMIT 1000
```

---

## 📊 Comparison

| Aspect | Current | Proposed |
|--------|---------|----------|
| **Tables** | 2 | N |
| **Join types** | INNER | INNER, LEFT, RIGHT |
| **Join order** | Fixed | Configurable |
| **SQL complexity** | Simple | Complex |
| **Efficiency** | Low | High |


