# Field Hints Single-Schema Verification & Fix

## Your Concern

**"Field hints implementation seem to be incorrect because hints are checked across schema but am using single schema with multiple tables."**

## Verification Result

✅ **Issue Confirmed and Fixed**

The field hints were indeed being treated as cross-schema mappings even for single-schema scenarios. This has been corrected.

---

## What Was Wrong

### Before Fix
```
Single Schema: "catalog" with tables [orders, customers, products]

Field Hint: "customer_id" → "cust_id"

WRONG INTERPRETATION:
- Treated as: schema1.customer_id → schema2.cust_id
- LLM looked for customer_id in one schema and cust_id in another schema
- Failed to find matches because both fields are in the SAME schema
```

### After Fix
```
Single Schema: "catalog" with tables [orders, customers, products]

Field Hint: "customer_id" → "cust_id"

CORRECT INTERPRETATION:
- Treated as: orders.customer_id → customers.cust_id
- LLM looks for customer_id in one table and cust_id in another table
- Finds matches and generates join rules correctly
```

---

## The Fix

### 1. Schema Type Detection
```python
is_single_schema = len(schemas_info) == 1
```

### 2. Conditional Field Hint Formatting

**For Single-Schema**:
```
Table: orders
  → FIELD HINTS (suggested matches):
    - orders.customer_id → (other_table).cust_id
    - orders.product_code → (other_table).sku
```

**For Multi-Schema**:
```
Table: hana_material_master
  → FIELD HINTS (suggested matches):
    - MATERIAL → PLANNING_SKU
    - PRODUCT_TYPE → GPU_MODEL
```

### 3. Explicit LLM Instructions

**For Single-Schema**:
```
IMPORTANT FOR SINGLE-SCHEMA:
- Field hints specify which fields in different tables should be matched
- Example: If hint says "MATERIAL → PLANNING_SKU", find which table has MATERIAL and which has PLANNING_SKU
- Generate rules that JOIN these tables on these field mappings
- Use the SAME schema name for both source_schema and target_schema
```

**For Multi-Schema**:
```
IMPORTANT FOR MULTI-SCHEMA:
- Field hints specify which fields across different schemas should be matched
- Example: If hint says "MATERIAL → PLANNING_SKU", match MATERIAL in source schema with PLANNING_SKU in target schema
```

---

## Files Modified

### kg_builder/services/multi_schema_llm_service.py

**Change 1: Line 265 - `_build_inference_prompt()`**
- Added schema type detection
- Conditional field hint formatting for single vs multi-schema

**Change 2: Line 304 - Inference Prompt Context**
- Added schema context (intra-schema vs cross-schema)
- Updated task description based on schema type

**Change 3: Line 615 - `_build_reconciliation_rules_prompt()`**
- Added schema type detection
- Conditional field hint formatting for single vs multi-schema

**Change 4: Line 657 - Reconciliation Prompt Instructions**
- Added explicit instructions for single-schema field hints
- Added explicit instructions for multi-schema field hints

---

## How It Works Now

### Single-Schema Example

**Input**:
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

**LLM Processing**:
1. Detects: Single schema (len(schemas_info) == 1)
2. Reads: "orders.customer_id → (other_table).cust_id"
3. Searches: Which table has cust_id? → customers
4. Generates: orders.customer_id → customers.cust_id
5. Creates Rule: JOIN orders ON orders.customer_id = customers.cust_id

**Output**:
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

### Multi-Schema Example

**Input**:
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

**LLM Processing**:
1. Detects: Multi-schema (len(schemas_info) > 1)
2. Reads: "MATERIAL → PLANNING_SKU"
3. Searches: MATERIAL in hana schema, PLANNING_SKU in ops schema
4. Generates: hana.hana_material_master.MATERIAL → ops.brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU
5. Creates Rule: Match on MATERIAL = PLANNING_SKU

**Output**:
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

## Key Differences

| Aspect | Single-Schema | Multi-Schema |
|--------|---------------|--------------|
| Schema Count | 1 | 2+ |
| Field Hint Format | table.field → field | field → field |
| LLM Task | Find target table | Find target schema & table |
| Source Schema | Same as target | Different from target |
| Example | orders.id → customers.id | hana.id → ops.id |

---

## Testing Recommendations

### Test 1: Single-Schema with Multiple Tables
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

**Expected**: Rules with same schema name for source and target

### Test 2: Multi-Schema
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

**Expected**: Rules with different schema names for source and target

---

## Backward Compatibility

✅ **Fully backward compatible**
- Multi-schema field hints work exactly as before
- Single-schema field hints now work correctly
- No API changes
- No breaking changes

---

## Summary

**Issue**: Field hints were treated as cross-schema mappings even for single-schema
**Root Cause**: No distinction between single-schema and multi-schema in field hint processing
**Solution**: Added schema type detection and conditional field hint formatting
**Result**: Field hints now work correctly for both single-schema and multi-schema scenarios

---

## Next Steps

1. **Test** the fix with your single-schema field hints
2. **Verify** that rules are generated correctly
3. **Check** that source_schema and target_schema are the same for single-schema rules
4. **Confirm** that multi-schema rules still work as expected

---

## Documentation

- **FIELD_HINTS_SINGLE_SCHEMA_FIX.md** - Detailed explanation of the fix
- **FIELD_HINTS_SINGLE_SCHEMA_VERIFICATION.md** - This file


