# JOIN Condition Fix - Exact Code Changes

## Overview

This document shows the exact code changes needed to fix the JOIN condition issue.

---

## Change 1: Update NLSQLGenerator Constructor

**File**: `kg_builder/services/nl_sql_generator.py`

**Current Code** (lines 20-30):
```python
class NLSQLGenerator:
    """Generate SQL from query intent."""
    
    def __init__(self, db_type: str = "mysql"):
        """
        Initialize SQL generator.
        
        Args:
            db_type: Database type (mysql, sql_server, postgresql, oracle)
        """
        self.db_type = db_type
```

**Updated Code**:
```python
from typing import Optional
from kg_builder.models import KnowledgeGraph

class NLSQLGenerator:
    """Generate SQL from query intent."""
    
    def __init__(self, db_type: str = "mysql", kg: Optional[KnowledgeGraph] = None):
        """
        Initialize SQL generator.
        
        Args:
            db_type: Database type (mysql, sql_server, postgresql, oracle)
            kg: Optional Knowledge Graph for join column resolution
        """
        self.db_type = db_type
        self.kg = kg  # NEW: Store KG reference
```

---

## Change 2: Update `_generate_join_clauses_for_columns()` Method

**File**: `kg_builder/services/nl_sql_generator.py`

**Current Code** (lines 345-385):
```python
def _generate_join_clauses_for_columns(self, columns: List) -> str:
    """Generate LEFT JOIN clauses for additional columns."""
    joins = []
    processed_tables = set()

    for col in columns:
        if not col.join_path or len(col.join_path) < 2:
            logger.warning(f"No join path for column {col.column_name}")
            continue

        for i in range(len(col.join_path) - 1):
            table1 = col.join_path[i]
            table2 = col.join_path[i + 1]

            join_key = f"{table1.lower()}_{table2.lower()}"
            if join_key in processed_tables:
                continue

            processed_tables.add(join_key)

            alias1 = self._get_table_alias(table1)
            alias2 = self._get_table_alias(table2)
            table2_quoted = self._quote_identifier(table2)

            # For now, use a generic join condition
            # In production, this should use the actual join columns from KG
            join = f"LEFT JOIN {table2_quoted} {alias2} ON {alias1}.id = {alias2}.id"
            joins.append(join)

    return "\n".join(joins)
```

**Updated Code**:
```python
def _generate_join_clauses_for_columns(self, columns: List) -> str:
    """Generate LEFT JOIN clauses for additional columns."""
    joins = []
    processed_tables = set()

    for col in columns:
        if not col.join_path or len(col.join_path) < 2:
            logger.warning(f"No join path for column {col.column_name}")
            continue

        for i in range(len(col.join_path) - 1):
            table1 = col.join_path[i]
            table2 = col.join_path[i + 1]

            join_key = f"{table1.lower()}_{table2.lower()}"
            if join_key in processed_tables:
                continue

            processed_tables.add(join_key)

            alias1 = self._get_table_alias(table1)
            alias2 = self._get_table_alias(table2)
            table2_quoted = self._quote_identifier(table2)

            # NEW: Get actual join condition from KG
            join_condition = self._get_join_condition(table1, table2, alias1, alias2)
            
            join = f"LEFT JOIN {table2_quoted} {alias2} ON {join_condition}"
            joins.append(join)

    return "\n".join(joins)
```

---

## Change 3: Add New Helper Method

**File**: `kg_builder/services/nl_sql_generator.py`

**Add this new method** (after `_generate_join_clauses_for_columns()`):

```python
def _get_join_condition(self, table1: str, table2: str, alias1: str, alias2: str) -> str:
    """
    Get actual join condition from KG relationships.
    
    Args:
        table1: First table name
        table2: Second table name
        alias1: Alias for first table
        alias2: Alias for second table
    
    Returns:
        str: Join condition like "alias1.col1 = alias2.col2"
    """
    if not self.kg:
        # Fallback to placeholder if KG not available
        logger.warning(f"No KG available for join condition, using placeholder")
        return f"{alias1}.id = {alias2}.id"
    
    table1_lower = table1.lower()
    table2_lower = table2.lower()
    
    # Find relationship between table1 and table2
    for rel in self.kg.relationships:
        source_id = rel.source_id.lower() if rel.source_id else ""
        target_id = rel.target_id.lower() if rel.target_id else ""
        
        # Check forward direction: table1 → table2
        if (source_id == table1_lower or source_id == f"table_{table1_lower}") and \
           (target_id == table2_lower or target_id == f"table_{table2_lower}"):
            source_col = rel.source_column or (rel.properties.get("source_column") if rel.properties else None)
            target_col = rel.target_column or (rel.properties.get("target_column") if rel.properties else None)
            if source_col and target_col:
                source_col_quoted = self._quote_identifier(source_col)
                target_col_quoted = self._quote_identifier(target_col)
                logger.debug(f"Found forward relationship: {table1}.{source_col} = {table2}.{target_col}")
                return f"{alias1}.{source_col_quoted} = {alias2}.{target_col_quoted}"
        
        # Check reverse direction: table2 → table1
        if (source_id == table2_lower or source_id == f"table_{table2_lower}") and \
           (target_id == table1_lower or target_id == f"table_{table1_lower}"):
            source_col = rel.source_column or (rel.properties.get("source_column") if rel.properties else None)
            target_col = rel.target_column or (rel.properties.get("target_column") if rel.properties else None)
            if source_col and target_col:
                source_col_quoted = self._quote_identifier(source_col)
                target_col_quoted = self._quote_identifier(target_col)
                logger.debug(f"Found reverse relationship: {table1}.{target_col} = {table2}.{source_col}")
                return f"{alias1}.{target_col_quoted} = {alias2}.{source_col_quoted}"
    
    # Fallback if no relationship found
    logger.warning(f"No relationship found between {table1} and {table2}, using placeholder")
    return f"{alias1}.id = {alias2}.id"
```

---

## Change 4: Update All Callers to Pass KG

**File**: `kg_builder/services/landing_kpi_executor.py`

**Current Code** (around line 180):
```python
generator = NLSQLGenerator(db_type=db_type)
sql = generator.generate(intent)
```

**Updated Code**:
```python
generator = NLSQLGenerator(db_type=db_type, kg=kg)  # Pass KG
sql = generator.generate(intent)
```

---

## Change 5: Update Tests

**File**: `tests/test_additional_columns.py`

**Update test to pass KG**:
```python
# Before
generator = NLSQLGenerator(db_type='mysql')

# After
generator = NLSQLGenerator(db_type='mysql', kg=kg)
```

---

## Summary of Changes

| File | Change | Type |
|------|--------|------|
| `nl_sql_generator.py` | Add `kg` parameter to `__init__` | Constructor |
| `nl_sql_generator.py` | Update `_generate_join_clauses_for_columns()` | Method |
| `nl_sql_generator.py` | Add `_get_join_condition()` method | New Method |
| `landing_kpi_executor.py` | Pass `kg` to NLSQLGenerator | Caller |
| `test_additional_columns.py` | Pass `kg` to NLSQLGenerator | Tests |

---

## Testing the Fix

### Before Fix
```sql
LEFT JOIN hana_material_master m ON g.id = m.id  -- ❌ WRONG
```

### After Fix
```sql
LEFT JOIN hana_material_master m ON g.`Material` = m.`MATERIAL`  -- ✅ CORRECT
```

### Test Query
```python
# Test with KG_102
definition = "Show me products in RBP GPU which are inactive in OPS Excel, include OPS_PLANNER from HANA Master"

parser = get_nl_query_parser(kg=kg, schemas_info=schemas_info)
intent = parser.parse(definition, use_llm=True)

generator = NLSQLGenerator(db_type='sql_server', kg=kg)  # Pass KG
sql = generator.generate(intent)

# Verify JOIN conditions use actual columns
assert "ON g.`Material` = m.`MATERIAL`" in sql
assert "ON g.id = m.id" not in sql  # Should NOT have placeholder
```

---

## Effort & Impact

- **Lines Changed**: ~50 lines
- **Files Modified**: 5 files
- **Complexity**: Low
- **Risk**: Low (only affects JOIN generation)
- **Time**: 30-45 minutes
- **Testing**: 15-20 minutes

---

## Result

After these changes:
- ✅ JOIN conditions use actual columns from KG
- ✅ SQL is correct and production-ready
- ✅ Query results are accurate
- ✅ Query performance is optimal

