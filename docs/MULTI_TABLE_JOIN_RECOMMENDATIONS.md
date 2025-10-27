# Multi-Table Join: Recommendations & Action Plan

## 🎯 Your Scenario

You want to join 4 tables:
```
brz_lnd_RBP_GPU 
  ↓ JOIN on (material, planning_sku, active_inactive)
brz_lnd_OPS_EXCEL_GPU
  ↓ JOIN on (material, planning_sku, active_inactive)
brz_lnd_SKU_LIFNR_Excel
  ↓ JOIN on (material)
hana_material_master (enrichment)
```

**Current Result**: Only 2 tables are joined
**Expected Result**: All 4 tables should be joined together

---

## 🔍 Analysis Summary

### What's Working ✅
1. **Knowledge Graph** - Correctly identifies all relationships
2. **NL Relationships** - Correctly parses relationship definitions
3. **Field Preferences** - Correctly parsed and stored

### What's Not Working ❌
1. **Rule Generation** - Only creates 2-table rules
2. **SQL Generation** - Only generates 2-table INNER JOINs
3. **LLM Prompt** - Doesn't ask for multi-table joins
4. **Field Preferences Usage** - Not used to determine join order

---

## 🎯 Improvement Areas (Priority Order)

### 1. **SQL Generation** (HIGHEST PRIORITY)
**File**: `kg_builder/services/reconciliation_executor.py` (lines 435-502)

**Current**:
```python
# Only 2 tables
SELECT s.*, t.*
FROM source s
INNER JOIN target t ON ...
```

**Needed**:
```python
# Support N tables
SELECT t1.*, t2.*, t3.*, t4.*
FROM table1 t1
INNER JOIN table2 t2 ON ...
INNER JOIN table3 t3 ON ...
LEFT JOIN table4 t4 ON ...
```

**Impact**: HIGH - Enables multi-table joins

---

### 2. **Rule Model** (HIGH PRIORITY)
**File**: `kg_builder/models.py` (ReconciliationRule class)

**Current**:
```python
source_table: str
target_table: str
```

**Needed**:
```python
# Keep current for backward compatibility
source_table: Optional[str]
target_table: Optional[str]

# Add multi-table support
join_tables: Optional[List[str]]  # [table1, table2, table3]
join_conditions: Optional[List[Dict]]  # Join conditions
join_order: Optional[List[str]]  # Order to join
join_type: Optional[List[str]]  # INNER, LEFT, RIGHT
```

**Impact**: HIGH - Enables rule model to represent multi-table joins

---

### 3. **Rule Generation** (HIGH PRIORITY)
**File**: `kg_builder/services/reconciliation_service.py` (lines 208-364)

**Current**:
```python
# Creates separate 2-table rules
for rel in relationships:
    rules.append(ReconciliationRule(
        source_table=rel['source_table'],
        target_table=rel['target_table']
    ))
```

**Needed**:
```python
# Group related tables and create multi-table rules
table_groups = self._group_tables_by_join_fields(field_preferences)
for group in table_groups:
    rule = ReconciliationRule(
        join_tables=group['tables'],
        join_conditions=group['conditions'],
        join_order=group['order']
    )
```

**Impact**: HIGH - Enables creation of multi-table rules

---

### 4. **LLM Prompt** (MEDIUM PRIORITY)
**File**: `kg_builder/services/multi_schema_llm_service.py` (lines 544-678)

**Current**:
```python
"sql_template": "SELECT * FROM table1 t1 JOIN table2 t2 ON t1.col1 = t2.col1"
```

**Needed**:
```python
# Add multi-table examples
"sql_template_multi": """
SELECT t1.*, t2.*, t3.*, t4.*
FROM brz_lnd_RBP_GPU t1
INNER JOIN brz_lnd_OPS_EXCEL_GPU t2 ON ...
INNER JOIN brz_lnd_SKU_LIFNR_Excel t3 ON ...
LEFT JOIN hana_material_master t4 ON ...
"""

# Add instructions
"MULTI-TABLE JOINS: If multiple tables share common join fields, 
create a single rule that joins all of them together."
```

**Impact**: MEDIUM - Helps LLM generate multi-table rules

---

### 5. **Field Preferences Usage** (MEDIUM PRIORITY)
**File**: `kg_builder/services/multi_schema_llm_service.py` (lines 558-594)

**Current**:
```python
# Field preferences only mentioned in prompt
# Not used to determine join order
```

**Needed**:
```python
# Use field preferences to guide multi-table joins
def _determine_join_order(self, field_preferences):
    # Priority fields → INNER JOIN first
    # Enrichment tables → LEFT JOIN last
    # Filter hints → WHERE clause
    
    join_order = []
    for pref in field_preferences:
        table = pref['table_name']
        priority = pref.get('priority_fields', [])
        if priority:
            join_order.append((table, 'INNER'))
    
    # Enrichment tables → LEFT JOIN
    for table in all_tables:
        if table not in join_order:
            join_order.append((table, 'LEFT'))
    
    return join_order
```

**Impact**: MEDIUM - Improves join order determination

---

## 📋 Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Extend ReconciliationRule model
- [ ] Update SQL generation for multi-table joins
- [ ] Add tests for multi-table scenarios

### Phase 2: Enhancement (Week 2)
- [ ] Modify rule generation to create multi-table rules
- [ ] Update LLM prompt with multi-table examples
- [ ] Add field preferences usage for join order

### Phase 3: Validation (Week 3)
- [ ] Test with your 4-table scenario
- [ ] Validate SQL generation
- [ ] Performance testing

### Phase 4: Documentation (Week 4)
- [ ] Update API documentation
- [ ] Create user guide for multi-table joins
- [ ] Add examples

---

## 🚀 Quick Win (Immediate)

If you need a quick solution now:

1. **Manually create multi-table rules** using the API
2. **Specify join order** in the rule definition
3. **Use composite keys** for join conditions

Example:
```json
{
  "join_tables": ["brz_lnd_RBP_GPU", "brz_lnd_OPS_EXCEL_GPU", "brz_lnd_SKU_LIFNR_Excel", "hana_material_master"],
  "join_conditions": [
    {"table1": "brz_lnd_RBP_GPU", "table2": "brz_lnd_OPS_EXCEL_GPU", "on": "material=material AND planning_sku=planning_sku"},
    {"table1": "brz_lnd_OPS_EXCEL_GPU", "table2": "brz_lnd_SKU_LIFNR_Excel", "on": "material=material"},
    {"table1": "brz_lnd_RBP_GPU", "table2": "hana_material_master", "on": "material=material"}
  ]
}
```

---

## 📊 Impact Assessment

| Component | Current | Proposed | Impact |
|-----------|---------|----------|--------|
| **Max tables per rule** | 2 | N | HIGH |
| **Join types** | INNER | INNER, LEFT, RIGHT | HIGH |
| **Join order** | N/A | Configurable | HIGH |
| **Field preferences** | Unused | Used | MEDIUM |
| **Complexity** | Low | Medium | MEDIUM |

---

## 💡 Key Takeaways

1. **KG is working correctly** - No changes needed
2. **NL relationships are working** - No changes needed
3. **SQL generation needs enhancement** - Support multi-table joins
4. **Rule generation needs enhancement** - Create multi-table rules
5. **LLM prompt needs enhancement** - Add multi-table examples
6. **Field preferences need better usage** - Guide join order

---

## 🎯 Next Steps

1. Review this analysis with your team
2. Prioritize improvements based on your needs
3. Start with Phase 1 (Foundation)
4. Test with your 4-table scenario
5. Iterate and refine

---

## 📚 Related Documentation

- `docs/MULTI_TABLE_JOIN_ANALYSIS.md` - Detailed analysis
- `docs/MULTI_TABLE_JOIN_TECHNICAL_DETAILS.md` - Technical deep dive
- `docs/MULTI_TABLE_JOIN_SUMMARY.md` - Executive summary


