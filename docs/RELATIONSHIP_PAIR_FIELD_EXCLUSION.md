# Relationship Pair Field Exclusion Guide

## 🎯 Overview

When creating Knowledge Graphs (KG) with relationship pairs, certain fields like `Product_Line`, `Business_Unit`, `[Product Type]`, and `[Business Unit]` should be excluded from the relationship definitions. This guide explains how the system automatically filters these fields.

---

## 📋 Excluded Fields

The following fields are automatically excluded from KG relationship creation:

### Product Line Variations
- `Product_Line`
- `product_line`
- `PRODUCT_LINE`
- `Product Line`

### Business Unit Variations
- `Business_Unit`
- `business_unit`
- `BUSINESS_UNIT`
- `Business Unit`
- `[Business Unit]`
- `BUSINESS_UNIT_CODE`

### Product Type Variations
- `[Product Type]`
- `Product Type`
- `product_type`
- `PRODUCT_TYPE`

---

## 🔧 How It Works

### 1. **Field Detection**

The system uses the `is_excluded_field()` function to check if a field should be excluded:

```python
from kg_builder.services.schema_parser import is_excluded_field

# Returns True for excluded fields
is_excluded_field("Product_Line")      # ✓ True
is_excluded_field("Business_Unit")     # ✓ True
is_excluded_field("[Product Type]")    # ✓ True

# Returns False for valid fields
is_excluded_field("MATERIAL")          # ✗ False
is_excluded_field("PLANNING_SKU")      # ✗ False
```

### 2. **Pair Filtering**

The `filter_relationship_pairs()` function automatically removes any relationship pairs that use excluded fields:

```python
from kg_builder.services.schema_parser import filter_relationship_pairs

pairs = [
    {
        "source_table": "hana_material_master",
        "source_column": "MATERIAL",
        "target_table": "brz_lnd_OPS_EXCEL_GPU",
        "target_column": "PLANNING_SKU"
    },
    {
        "source_table": "table1",
        "source_column": "Product_Line",  # ❌ EXCLUDED
        "target_table": "table2",
        "target_column": "PLANNING_SKU"
    }
]

filtered = filter_relationship_pairs(pairs)
# Result: Only 1 pair (the second one is filtered out)
```

### 3. **Automatic Integration**

The filtering is automatically applied in two places:

#### **KG Generation Endpoint**
```python
# POST /kg/generate
# Automatically filters relationship_pairs before processing
```

#### **KG Integration Endpoint**
```python
# POST /kg/integrate-nl-relationships
# Automatically filters relationship_pairs before processing
```

---

## 📊 Example: Your JSON

### Before (With Excluded Fields)
```json
[
  {
    "source_table": "hana_material_master",
    "source_column": "MATERIAL",
    "target_table": "brz_lnd_OPS_EXCEL_GPU",
    "target_column": "PLANNING_SKU",
    "bidirectional": true
  },
  {
    "source_table": "brz_lnd_OPS_EXCEL_GPU",
    "source_column": "PLANNING_SKU",
    "target_table": "brz_lnd_RBP_GPU",
    "target_column": "Material"
  },
  {
    "source_table": "brz_lnd_RBP_GPU",
    "source_column": "Material",
    "target_table": "brz_lnd_SKU_LIFNR_Excel",
    "target_column": "Material"
  }
]
```

### After Filtering
```json
[
  {
    "source_table": "hana_material_master",
    "source_column": "MATERIAL",
    "target_table": "brz_lnd_OPS_EXCEL_GPU",
    "target_column": "PLANNING_SKU",
    "bidirectional": true
  },
  {
    "source_table": "brz_lnd_OPS_EXCEL_GPU",
    "source_column": "PLANNING_SKU",
    "target_table": "brz_lnd_RBP_GPU",
    "target_column": "Material"
  },
  {
    "source_table": "brz_lnd_RBP_GPU",
    "source_column": "Material",
    "target_table": "brz_lnd_SKU_LIFNR_Excel",
    "target_column": "Material"
  }
]
```

**Result**: All 3 pairs are valid (no excluded fields) ✅

---

## 🚀 Usage Examples

### Example 1: Valid Pairs (All Kept)
```json
{
  "kg_name": "material_kg",
  "schemas": ["hana-schema", "ops-schema", "rbp-schema"],
  "relationship_pairs": [
    {
      "source_table": "hana_material_master",
      "source_column": "MATERIAL",
      "target_table": "brz_lnd_OPS_EXCEL_GPU",
      "target_column": "PLANNING_SKU"
    },
    {
      "source_table": "brz_lnd_OPS_EXCEL_GPU",
      "source_column": "PLANNING_SKU",
      "target_table": "brz_lnd_RBP_GPU",
      "target_column": "Material"
    }
  ]
}
```

**Result**: 2 pairs processed ✅

### Example 2: Mixed Valid and Invalid Pairs
```json
{
  "kg_name": "material_kg",
  "schemas": ["hana-schema", "ops-schema"],
  "relationship_pairs": [
    {
      "source_table": "hana_material_master",
      "source_column": "MATERIAL",
      "target_table": "brz_lnd_OPS_EXCEL_GPU",
      "target_column": "PLANNING_SKU"
    },
    {
      "source_table": "table1",
      "source_column": "Product_Line",
      "target_table": "table2",
      "target_column": "Product_Line"
    }
  ]
}
```

**Result**: 1 pair processed (second pair filtered out) ✅

### Example 3: All Invalid Pairs
```json
{
  "kg_name": "material_kg",
  "schemas": ["hana-schema", "ops-schema"],
  "relationship_pairs": [
    {
      "source_table": "table1",
      "source_column": "Business_Unit",
      "target_table": "table2",
      "target_column": "Business_Unit"
    },
    {
      "source_table": "table3",
      "source_column": "[Product Type]",
      "target_table": "table4",
      "target_column": "[Product Type]"
    }
  ]
}
```

**Result**: 0 pairs processed (all filtered out) ✅

---

## 📝 API Response

When you submit relationship pairs, the API logs show the filtering:

```
INFO: Adding 3 explicit relationship pairs to KG
INFO: Filtered pairs: 3 → 3
INFO: Added 3 explicit relationship pairs to KG
```

Or if some pairs are excluded:

```
INFO: Adding 5 explicit relationship pairs to KG
INFO: Excluding relationship pair: Product_Line -> PLANNING_SKU (excluded field)
INFO: Excluding relationship pair: Business_Unit -> Business_Unit (excluded field)
INFO: Filtered pairs: 5 → 3
INFO: Added 3 explicit relationship pairs to KG
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
python -m pytest tests/test_relationship_pair_filtering.py -v -s
```

**Expected Output**:
```
15 passed ✅
```

### Test Coverage

- ✅ Field detection (all variations)
- ✅ Pair filtering (source and target columns)
- ✅ Mixed valid/invalid pairs
- ✅ Pair structure preservation
- ✅ Real-world scenarios
- ✅ Excluded fields list validation

---

## 🔍 Implementation Details

### Files Modified

1. **`kg_builder/services/schema_parser.py`**
   - Added `EXCLUDED_FIELDS` set (15 field variations)
   - Added `is_excluded_field()` function
   - Added `filter_relationship_pairs()` function

2. **`kg_builder/routes.py`**
   - Updated `/kg/generate` endpoint to filter pairs
   - Updated `/kg/integrate-nl-relationships` endpoint to filter pairs

3. **`tests/test_relationship_pair_filtering.py`** (NEW)
   - 15 comprehensive tests
   - All tests passing ✅

---

## 📊 Excluded Fields List

```python
EXCLUDED_FIELDS = {
    "Product_Line", "product_line", "PRODUCT_LINE",
    "Business_Unit", "business_unit", "BUSINESS_UNIT",
    "[Product Type]", "Product Type", "product_type", "PRODUCT_TYPE",
    "[Business Unit]", "business unit", "BUSINESS_UNIT_CODE",
    "Product Line", "Business Unit",
}
```

---

## ✨ Benefits

1. **Automatic Filtering**: No manual intervention needed
2. **Case-Insensitive**: Handles all case variations
3. **Comprehensive**: Covers all field name variations
4. **Transparent**: Logs show what was filtered
5. **Non-Breaking**: Invalid pairs are silently excluded
6. **Well-Tested**: 15 tests covering all scenarios

---

## 🎯 Next Steps

1. **Use the API** with your relationship pairs
2. **Check logs** to see filtering in action
3. **Verify results** in the generated KG
4. **Add more fields** to `EXCLUDED_FIELDS` if needed

---

## 📞 Support

For questions or to add more excluded fields, update the `EXCLUDED_FIELDS` set in:
```
kg_builder/services/schema_parser.py (line 19-26)
```

---

**Status**: ✅ **COMPLETE AND TESTED**

All relationship pairs with excluded fields are automatically filtered during KG creation!

