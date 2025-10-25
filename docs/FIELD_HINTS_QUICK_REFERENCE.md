# Field Hints Quick Reference Guide

## What are Field Hints?

**Field Hints** are user-provided suggestions that tell the LLM which fields in different tables represent the same business data.

```
Format: "source_field": "target_field"
Example: "MATERIAL": "PLANNING_SKU"
Meaning: "MATERIAL in this table matches PLANNING_SKU in another table"
```

## JSON Structure

```json
[
  {
    "table_name": "table_1",
    "field_hints": {
      "field_a": "field_b",
      "field_c": "field_d"
    },
    "priority_fields": ["field_a", "field_c"],
    "exclude_fields": ["temp_field", "internal_field"]
  },
  {
    "table_name": "table_2",
    "field_hints": {
      "field_b": "field_a",
      "field_d": "field_c"
    },
    "priority_fields": ["field_b", "field_d"],
    "exclude_fields": ["staging_flag"]
  }
]
```

## Three Components

### 1. Field Hints (Required for hints)
```json
"field_hints": {
  "source_column": "target_column",
  "another_source": "another_target"
}
```
- Maps fields that represent the same data
- Can be bidirectional (specify in both tables)
- Example: `"MATERIAL": "PLANNING_SKU"`

### 2. Priority Fields (Optional)
```json
"priority_fields": ["MATERIAL", "MATERIAL_DESC", "PRODUCT_ID"]
```
- Fields to focus on during LLM inference
- Use for key identifiers and important attributes
- Improves relationship discovery
- Reduces processing time

### 3. Exclude Fields (Optional)
```json
"exclude_fields": ["INTERNAL_NOTES", "TEMP_FIELD", "STAGING_FLAG"]
```
- Fields to skip entirely
- Use for temporary, internal, or metadata fields
- Reduces noise in rule generation
- Improves performance

## Real-World Example

### Scenario
Match SAP HANA material data with data lake GPU specifications:

```json
[
  {
    "table_name": "hana_material_master",
    "field_hints": {
      "MATERIAL": "PLANNING_SKU"
    },
    "priority_fields": ["MATERIAL", "MATERIAL_DESC"],
    "exclude_fields": ["INTERNAL_NOTES", "TEMP_FIELD"]
  },
  {
    "table_name": "brz_lnd_OPS_EXCEL_GPU",
    "field_hints": {
      "PLANNING_SKU": "MATERIAL",
      "GPU_MODEL": "PRODUCT_TYPE"
    },
    "priority_fields": ["PLANNING_SKU", "GPU_MODEL"],
    "exclude_fields": ["STAGING_FLAG"]
  }
]
```

### What This Does
1. **Tells LLM**: "MATERIAL and PLANNING_SKU are the same thing"
2. **Prioritizes**: Focus on MATERIAL, MATERIAL_DESC, PLANNING_SKU, GPU_MODEL
3. **Excludes**: Skip internal notes, temp fields, staging flags
4. **Result**: High-confidence rules for material matching

## Usage Steps

### In Knowledge Graph Page
1. Go to **Generate KG** tab
2. Select your schemas
3. Enable **Use LLM Enhancement**
4. Click **Field Preferences (Optional - Advanced)**
5. Paste your JSON
6. Click **Generate Knowledge Graph**

### In Reconciliation Page
1. Go to **Generate Rules** tab
2. Select your schemas and KG
3. Enable **Use LLM Enhancement**
4. Click **Field Preferences (Optional - Advanced)**
5. Paste your JSON
6. Click **Generate Rules**

## Common Patterns

### Pattern 1: Simple Field Mapping
```json
{
  "table_name": "orders",
  "field_hints": {
    "order_id": "order_number",
    "customer_id": "cust_id"
  }
}
```

### Pattern 2: Multi-Table Reconciliation
```json
[
  {
    "table_name": "source_table",
    "field_hints": { "id": "identifier", "code": "product_code" },
    "priority_fields": ["id", "code"]
  },
  {
    "table_name": "target_table",
    "field_hints": { "identifier": "id", "product_code": "code" },
    "priority_fields": ["identifier", "product_code"]
  }
]
```

### Pattern 3: Exclude Sensitive Data
```json
{
  "table_name": "customer_data",
  "field_hints": { "customer_id": "cust_num" },
  "exclude_fields": ["ssn", "credit_card", "password", "internal_notes"]
}
```

### Pattern 4: Focus on Key Fields
```json
{
  "table_name": "products",
  "field_hints": { "sku": "product_code" },
  "priority_fields": ["sku", "product_code", "product_name", "category"],
  "exclude_fields": ["temp_staging", "debug_info"]
}
```

## Tips & Best Practices

✅ **DO**
- Use field hints for fields with different names but same meaning
- Specify bidirectional hints in both tables for clarity
- Prioritize key identifiers (IDs, codes, SKUs)
- Exclude temporary, staging, or internal fields
- Start with critical hints, add more iteratively

❌ **DON'T**
- Use hints for fields that are already identical
- Hint at fields that don't exist in the table
- Exclude fields you need for matching
- Create circular hints (A→B→A)
- Provide hints for unrelated fields

## Expected Impact

| Metric | Without Hints | With Hints |
|--------|---------------|-----------|
| Rules Generated | 5-8 | 8-12 |
| Confidence Score | 0.6-0.7 | 0.8-0.95 |
| Accuracy | ~60% | ~95% |
| Processing Time | Normal | Slightly faster |
| Fallback Rules | None | Generated |

## Troubleshooting

### Issue: "Invalid JSON in field preferences"
- Check JSON syntax (use a JSON validator)
- Ensure all strings are quoted
- Verify no trailing commas

### Issue: No rules generated
- Verify table names match exactly (case-sensitive)
- Check field names exist in the tables
- Ensure LLM is enabled
- Try without hints first to see if it's a schema issue

### Issue: Low confidence scores
- Add more priority_fields
- Verify field_hints are correct
- Check if fields actually represent the same data
- Review the generated KG relationships

## See Also
- [Field Hints Example](FIELD_HINTS_EXAMPLE.md) - Detailed HANA to OPS Excel GPU example
- [Field Suggestions Documentation](FIELD_SUGGESTIONS_DOCUMENTATION_INDEX.md) - Full feature documentation


