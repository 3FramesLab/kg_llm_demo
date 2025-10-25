# Field Hints Single-Schema Fix

## Issue Identified

**Problem**: Field hints were being checked across schemas, but when using a single schema with multiple tables, field hints should be interpreted as **intra-table mappings** (table1.field → table2.field within the same schema), not cross-schema mappings.

**Example**:
```
Single Schema: "catalog" with tables: [orders, customers, products]

Field Hint: "customer_id" → "cust_id"

WRONG: Treat as cross-schema mapping (schema1.customer_id → schema2.cust_id)
RIGHT: Treat as intra-table mapping (orders.customer_id → customers.cust_id)
```

---

## Root Cause

The LLM prompt was treating all field hints the same way, regardless of whether it was:
- **Single-schema**: Multiple tables in ONE database
- **Multi-schema**: Tables across DIFFERENT databases

For single-schema, the field hints should guide the LLM to find which tables contain these fields and generate join rules.

---

## Solution Implemented

### 1. Updated `_build_reconciliation_rules_prompt()` (Line 615)

**Before**:
```python
if pref.get('field_hints'):
    field_preferences_str += f"  → FIELD HINTS (suggested matches):\n"
    for source, target in pref['field_hints'].items():
        field_preferences_str += f"    - {source} → {target}\n"
```

**After**:
```python
if pref.get('field_hints'):
    field_preferences_str += f"  → FIELD HINTS (suggested matches):\n"
    for source, target in pref['field_hints'].items():
        if is_single_schema:
            # For single-schema: hints are intra-table mappings
            field_preferences_str += f"    - {table_name}.{source} → (other_table).{target}\n"
        else:
            # For multi-schema: hints are cross-schema mappings
            field_preferences_str += f"    - {source} → {target}\n"
```

**Impact**: LLM now understands that for single-schema, it should find which table has the target field.

---

### 2. Updated `_build_inference_prompt()` (Line 265)

**Before**:
```python
if pref.get('field_hints'):
    field_preferences_str += f"  → FIELD HINTS (suggested matches):\n"
    for source, target in pref['field_hints'].items():
        field_preferences_str += f"    - {source} → {target}\n"
```

**After**:
```python
if pref.get('field_hints'):
    field_preferences_str += f"  → FIELD HINTS (suggested matches):\n"
    for source, target in pref['field_hints'].items():
        if is_single_schema:
            # For single-schema: hints are intra-table mappings
            field_preferences_str += f"    - {table_name}.{source} → (other_table).{target}\n"
        else:
            # For multi-schema: hints are cross-schema mappings
            field_preferences_str += f"    - {source} → {target}\n"
```

**Impact**: Relationship inference now correctly handles single-schema field hints.

---

### 3. Enhanced Prompt Instructions (Line 657)

**Added for Single-Schema**:
```
IMPORTANT FOR SINGLE-SCHEMA:
- Field hints specify which fields in different tables should be matched
- Example: If hint says "MATERIAL → PLANNING_SKU", find which table has MATERIAL and which has PLANNING_SKU
- Generate rules that JOIN these tables on these field mappings
- Use the SAME schema name for both source_schema and target_schema
```

**Added for Multi-Schema**:
```
IMPORTANT FOR MULTI-SCHEMA:
- Field hints specify which fields across different schemas should be matched
- Example: If hint says "MATERIAL → PLANNING_SKU", match MATERIAL in source schema with PLANNING_SKU in target schema
```

**Impact**: LLM gets explicit instructions on how to interpret field hints based on schema type.

---

### 4. Updated Context in Inference Prompt (Line 304)

**Before**:
```
You are analyzing schemas from different systems that may share data.
```

**After**:
```
You are analyzing schemas {within a single database schema (intra-schema) | across different database schemas (cross-schema)} that may share data.
```

**Impact**: LLM knows whether it's doing intra-schema or cross-schema relationship inference.

---

## How It Works Now

### Single-Schema Example

**Input**:
```json
{
  "table_name": "orders",
  "field_hints": {
    "customer_id": "cust_id",
    "product_code": "sku"
  }
}
```

**Prompt Now Shows**:
```
Table: orders
  → FIELD HINTS (suggested matches):
    - orders.customer_id → (other_table).cust_id
    - orders.product_code → (other_table).sku
```

**LLM Reasoning**:
1. "User says orders.customer_id should match with cust_id in another table"
2. "Let me find which table has cust_id field"
3. "Found: customers.cust_id"
4. "Generate rule: orders.customer_id → customers.cust_id"
5. "Use same schema name for both source_schema and target_schema"

**Result**:
```json
{
  "rule_name": "Orders_Customers_Join",
  "source_schema": "catalog",
  "source_table": "orders",
  "source_columns": ["customer_id"],
  "target_schema": "catalog",
  "target_table": "customers",
  "target_columns": ["cust_id"],
  "match_type": "exact",
  "confidence": 0.95
}
```

---

### Multi-Schema Example

**Input**:
```json
{
  "table_name": "hana_material_master",
  "field_hints": {
    "MATERIAL": "PLANNING_SKU"
  }
}
```

**Prompt Now Shows**:
```
Table: hana_material_master
  → FIELD HINTS (suggested matches):
    - MATERIAL → PLANNING_SKU
```

**LLM Reasoning**:
1. "User says MATERIAL should match with PLANNING_SKU"
2. "These are in different schemas"
3. "MATERIAL is in hana_material_master (source schema)"
4. "PLANNING_SKU is in brz_lnd_OPS_EXCEL_GPU (target schema)"
5. "Generate rule: hana_material_master.MATERIAL → brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU"

**Result**:
```json
{
  "rule_name": "Material_Planning_SKU_Match",
  "source_schema": "hana",
  "source_table": "hana_material_master",
  "source_columns": ["MATERIAL"],
  "target_schema": "ops",
  "target_table": "brz_lnd_OPS_EXCEL_GPU",
  "target_columns": ["PLANNING_SKU"],
  "match_type": "exact",
  "confidence": 0.95
}
```

---

## Testing the Fix

### Test Case 1: Single-Schema with Multiple Tables

**Setup**:
```json
{
  "schema_names": ["catalog"],
  "field_hints": {
    "table_name": "orders",
    "field_hints": {
      "customer_id": "cust_id",
      "product_code": "sku"
    }
  }
}
```

**Expected Result**:
- Rules generated for orders → customers (on customer_id ↔ cust_id)
- Rules generated for orders → products (on product_code ↔ sku)
- Both rules use same schema name for source and target

### Test Case 2: Multi-Schema

**Setup**:
```json
{
  "schema_names": ["hana", "ops"],
  "field_hints": {
    "table_name": "hana_material_master",
    "field_hints": {
      "MATERIAL": "PLANNING_SKU"
    }
  }
}
```

**Expected Result**:
- Rules generated for hana.hana_material_master → ops.brz_lnd_OPS_EXCEL_GPU
- Rule uses different schema names for source and target

---

## Files Modified

1. **kg_builder/services/multi_schema_llm_service.py**
   - Line 265: Updated `_build_inference_prompt()` to handle single-schema field hints
   - Line 304: Added schema context to prompt
   - Line 615: Updated `_build_reconciliation_rules_prompt()` to handle single-schema field hints
   - Line 657: Added explicit instructions for single vs multi-schema

---

## Backward Compatibility

✅ **Fully backward compatible**
- Multi-schema field hints work exactly as before
- Single-schema field hints now work correctly
- No API changes
- No breaking changes

---

## Summary

**Before**: Field hints were treated the same for single and multi-schema
**After**: Field hints are now correctly interpreted based on schema type

- **Single-Schema**: Field hints guide intra-table joins (table1.field → table2.field)
- **Multi-Schema**: Field hints guide cross-schema matches (schema1.field → schema2.field)

This fix ensures that field hints work correctly for both single-schema with multiple tables and multi-schema scenarios.


