# Field Exclusion - Quick Reference

## 🎯 What Gets Excluded?

These fields are **automatically excluded** from relationship pairs during KG creation:

### Product Line
```
Product_Line, product_line, PRODUCT_LINE, Product Line
```

### Business Unit
```
Business_Unit, business_unit, BUSINESS_UNIT, Business Unit, [Business Unit], BUSINESS_UNIT_CODE, business unit
```

### Product Type
```
[Product Type], Product Type, product_type, PRODUCT_TYPE
```

---

## ✅ What Stays?

These fields are **kept** in relationship pairs:

```
MATERIAL, PLANNING_SKU, Material, SKU, ID, Code, Reference, etc.
```

---

## 📊 Example

### ❌ This Pair Gets Filtered Out
```json
{
  "source_table": "table1",
  "source_column": "Product_Line",  ← EXCLUDED
  "target_table": "table2",
  "target_column": "PLANNING_SKU"
}
```

### ✅ This Pair Stays
```json
{
  "source_table": "hana_material_master",
  "source_column": "MATERIAL",      ← VALID
  "target_table": "brz_lnd_OPS_EXCEL_GPU",
  "target_column": "PLANNING_SKU"   ← VALID
}
```

---

## 🚀 How to Use

### 1. Prepare Your Pairs
```json
{
  "relationship_pairs": [
    {
      "source_table": "hana_material_master",
      "source_column": "MATERIAL",
      "target_table": "brz_lnd_OPS_EXCEL_GPU",
      "target_column": "PLANNING_SKU"
    }
  ]
}
```

### 2. Send to API
```bash
POST /kg/generate
POST /kg/integrate-nl-relationships
```

### 3. System Automatically Filters
- Checks each pair
- Removes pairs with excluded fields
- Logs what was filtered
- Processes remaining pairs

### 4. Check Logs
```
INFO: Filtered pairs: 5 → 3
INFO: Added 3 explicit relationship pairs to KG
```

---

## 🔍 Testing

Run tests:
```bash
python -m pytest tests/test_relationship_pair_filtering.py -v
```

Expected: **15/15 PASSED** ✅

---

## 📝 Excluded Fields List

| Category | Fields |
|----------|--------|
| **Product Line** | Product_Line, product_line, PRODUCT_LINE, Product Line |
| **Business Unit** | Business_Unit, business_unit, BUSINESS_UNIT, Business Unit, [Business Unit], BUSINESS_UNIT_CODE, business unit |
| **Product Type** | [Product Type], Product Type, product_type, PRODUCT_TYPE |

**Total**: 15 field variations

---

## 💡 Tips

1. **Use valid column names** like MATERIAL, PLANNING_SKU, Material, SKU
2. **Avoid excluded fields** in source_column and target_column
3. **Check logs** to see what was filtered
4. **All other fields** are automatically kept

---

## 🎯 Common Scenarios

### Scenario 1: All Valid Pairs
```json
[
  {"source_column": "MATERIAL", "target_column": "PLANNING_SKU"},
  {"source_column": "PLANNING_SKU", "target_column": "Material"}
]
```
**Result**: All pairs processed ✅

### Scenario 2: Mixed Valid and Invalid
```json
[
  {"source_column": "MATERIAL", "target_column": "PLANNING_SKU"},
  {"source_column": "Product_Line", "target_column": "Product_Line"}
]
```
**Result**: 1 pair processed, 1 filtered ✅

### Scenario 3: All Invalid Pairs
```json
[
  {"source_column": "Business_Unit", "target_column": "Business_Unit"},
  {"source_column": "[Product Type]", "target_column": "[Product Type]"}
]
```
**Result**: 0 pairs processed ✅

---

## 🔧 Implementation

**Files**:
- `kg_builder/services/schema_parser.py` - Filtering logic
- `kg_builder/routes.py` - API integration
- `tests/test_relationship_pair_filtering.py` - Tests

**Functions**:
- `is_excluded_field(field_name)` - Check if field is excluded
- `filter_relationship_pairs(pairs)` - Filter pairs

---

## ✨ Features

- ✅ Automatic filtering
- ✅ Case-insensitive
- ✅ Comprehensive coverage
- ✅ Transparent logging
- ✅ Non-breaking
- ✅ Well-tested

---

## 📞 Need to Add More Fields?

Edit `EXCLUDED_FIELDS` in:
```
kg_builder/services/schema_parser.py (lines 19-26)
```

Add your fields:
```python
EXCLUDED_FIELDS = {
    # ... existing ...
    "YourField", "your_field", "YOUR_FIELD",
}
```

---

**Status**: ✅ **READY TO USE**

Relationship pairs with excluded fields are automatically filtered during KG creation!

