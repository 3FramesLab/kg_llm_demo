# TableSchema 'name' Attribute Error - Fix Summary

## Problem

The Natural Language Relationships creation API was failing with the error:

```
Failed to load schemas: 'TableSchema' object has no attribute 'name'
```

## Root Cause

The code was incorrectly accessing attributes of `TableSchema` and `ColumnSchema` models:

### Issue 1: Using `table.name` instead of `table_name`

**Location:** `kg_builder/routes.py` (lines 1210, 1318)

```python
# ❌ WRONG
"columns": {
    table.name: list(table.columns.keys())  # table.name doesn't exist!
    for table in schema.tables.values()
}
```

**Problem:** `TableSchema` has a `table_name` attribute, not `name`.

### Issue 2: Using `table.columns.keys()` on a List

**Location:** Multiple files

```python
# ❌ WRONG
return list(table.columns.keys())  # columns is a List, not a Dict!
```

**Problem:** `TableSchema.columns` is a `List[ColumnSchema]`, not a dictionary. Lists don't have a `.keys()` method.

---

## Data Structure

### TableSchema Model

```python
class TableSchema(BaseModel):
    table_name: str                      # ✅ Use this, not .name
    columns: List[ColumnSchema]          # ✅ This is a List, not Dict
    primary_keys: List[str] = []
    foreign_keys: List[Dict[str, Any]] = []
    indexes: List[Dict[str, Any]] = []
```

### ColumnSchema Model

```python
class ColumnSchema(BaseModel):
    name: str           # ✅ Each column has a name
    type: str
    nullable: bool
    default: Optional[Any] = None
    primary_key: bool = False
```

### DatabaseSchema Model

```python
class DatabaseSchema(BaseModel):
    database: str
    tables: Dict[str, TableSchema]  # ✅ Dictionary: {table_name: TableSchema}
    total_tables: int
```

---

## Solution

### Fix 1: Iterate over `.items()` to get table names

**Before:**
```python
"columns": {
    table.name: list(table.columns.keys())
    for table in schema.tables.values()
}
```

**After:**
```python
"columns": {
    table_name: [col.name for col in table.columns]
    for table_name, table in schema.tables.items()  # ✅ Get both key and value
}
```

### Fix 2: Extract column names from List

**Before:**
```python
return list(table.columns.keys())  # ❌ columns is a List, not Dict
```

**After:**
```python
return [col.name for col in table.columns]  # ✅ Extract name from each ColumnSchema
```

---

## Files Fixed

### 1. `kg_builder/routes.py` (Line ~1210)
**Endpoint:** `POST /v1/kg/relationships/natural-language`

```python
# Fixed schema loading for NL relationship parsing
schemas_info[schema_name] = {
    "tables": list(schema.tables.keys()),
    "columns": {
        table_name: [col.name for col in table.columns]
        for table_name, table in schema.tables.items()
    }
}
```

### 2. `kg_builder/routes.py` (Line ~1318)
**Endpoint:** `POST /v1/kg/integrate-nl-relationships`

```python
# Fixed schema loading for NL relationship integration
schemas_info[schema_name] = {
    "tables": list(schema.tables.keys()),
    "columns": {
        table_name: [col.name for col in table.columns]
        for table_name, table in schema.tables.items()
    }
}
```

### 3. `kg_builder/services/rule_storage.py` (Line ~245)
**Function:** `export_ruleset_to_sql()`

```python
# Fixed column extraction for SQL generation
table = schema.tables.get(table_name)
if table:
    return [col.name for col in table.columns]  # ✅ Extract from List
```

---

## Impact

This fix resolves errors in the following features:

✅ **Natural Language Relationships** - Now correctly loads schemas
✅ **SQL Export** - Now correctly retrieves column names from schema
✅ **Knowledge Graph Integration** - Schema parsing works correctly

---

## Testing

To verify the fix works:

### Test 1: Natural Language Relationships

```bash
curl -X POST http://localhost:8000/v1/kg/relationships/natural-language \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "test_kg",
    "schemas": ["orderMgmt-catalog", "vendorDB-suppliers"],
    "definitions": ["Products are supplied by Vendors"],
    "use_llm": false,
    "min_confidence": 0.7
  }'
```

**Expected:** Should return parsed relationships, not schema loading error.

### Test 2: SQL Export with Specific Columns

```bash
# Generate rules first
curl -X POST http://localhost:8000/v1/reconciliation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "test_kg",
    "schema_names": ["orderMgmt-catalog"]
  }'

# Then export SQL
curl http://localhost:8000/v1/reconciliation/rulesets/{ruleset_id}/export/sql
```

**Expected:** SQL should have specific column names (e.g., `s.product_id, s.product_name`) instead of `s.*`.

---

## Key Learnings

1. **Always check model definitions** before accessing attributes
2. **TableSchema.columns is a List**, not a Dict - use list comprehension
3. **Use `.items()`** when you need both dictionary keys and values
4. **Column names** are accessed via `col.name` from `ColumnSchema` objects

---

## Related Files

- `kg_builder/models.py` - Schema model definitions
- `kg_builder/services/schema_parser.py` - Schema loading logic
- `kg_builder/routes.py` - API endpoints using schemas
- `kg_builder/services/rule_storage.py` - SQL generation from rules

---

## Date Fixed

2025-10-27

## Status

✅ **Fixed and Tested**
