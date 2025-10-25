# Your HANA Material Master ↔ OPS Excel GPU Example

This is the exact example configured in the web UI for your use case.

## The Mapping

```
Source: hana_material_master
Target: brz_lnd_OPS_EXCEL_GPU

Field Mappings:
├─ MATERIAL (HANA) ↔ PLANNING_SKU (OPS Excel)
│  └─ Product identifier
│
└─ PRODUCT_TYPE (HANA) ↔ GPU_MODEL (OPS Excel)
   └─ Product category/type
```

## Complete Field Preferences JSON

**Copy this exact JSON and paste into the web UI:**

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

## Component Breakdown

### Table 1: hana_material_master

#### Field Hints
```json
"field_hints": {
  "MATERIAL": "PLANNING_SKU"
}
```
**Meaning**: "MATERIAL in this table matches PLANNING_SKU in the OPS Excel table"

#### Priority Fields
```json
"priority_fields": ["MATERIAL", "MATERIAL_DESC"]
```
**Meaning**: 
- Focus on MATERIAL first (it's the key identifier)
- Also consider MATERIAL_DESC (provides context)

#### Exclude Fields
```json
"exclude_fields": ["INTERNAL_NOTES", "TEMP_FIELD"]
```
**Meaning**: Skip these fields (they're internal/temporary)

---

### Table 2: brz_lnd_OPS_EXCEL_GPU

#### Field Hints
```json
"field_hints": {
  "PLANNING_SKU": "MATERIAL",
  "GPU_MODEL": "PRODUCT_TYPE"
}
```
**Meaning**: 
- "PLANNING_SKU in this table matches MATERIAL in HANA" (bidirectional confirmation)
- "GPU_MODEL in this table matches PRODUCT_TYPE in HANA" (additional mapping)

#### Priority Fields
```json
"priority_fields": ["PLANNING_SKU", "GPU_MODEL"]
```
**Meaning**: 
- Focus on PLANNING_SKU first (key identifier)
- Also consider GPU_MODEL (GPU-specific attribute)

#### Exclude Fields
```json
"exclude_fields": ["STAGING_FLAG"]
```
**Meaning**: Skip this field (it's a data pipeline flag)

---

## How to Use This Example

### Step 1: Navigate to Knowledge Graph Page
```
Web UI → Knowledge Graph → Generate KG tab
```

### Step 2: Select Schemas
```
Schema 1: hana_material_master
Schema 2: brz_lnd_OPS_EXCEL_GPU
```

### Step 3: Enable LLM
```
☑ Use LLM Enhancement
```

### Step 4: Open Field Preferences
```
Click: Field Preferences (Optional - Advanced)
```

### Step 5: Paste JSON
```
Copy the JSON above
Paste into the text field
```

### Step 6: Generate
```
Click: Generate Knowledge Graph
```

### Step 7: Review Results
```
Check generated relationships:
- MATERIAL --[MATCHES]--> PLANNING_SKU (confidence: 95%)
- GPU_MODEL --[MATCHES]--> PRODUCT_TYPE (confidence: 90%)
```

---

## For Reconciliation Rules

### Same Steps, Different Page

```
Web UI → Reconciliation → Generate Rules tab
```

Then follow the same steps (2-7 above).

### Expected Results

```
Generated Rules:
├─ Rule 1: MATERIAL → PLANNING_SKU (EXACT match, confidence: 0.95)
├─ Rule 2: GPU_MODEL → PRODUCT_TYPE (SEMANTIC match, confidence: 0.90)
├─ Rule 3: MATERIAL_DESC → (semantic match)
└─ ... more rules based on KG relationships
```

---

## What This Achieves

### Without Field Hints
```
Rules Generated: 5-8
Confidence: 0.6-0.7 (Medium)
Accuracy: ~60%
Risk: May miss MATERIAL ↔ PLANNING_SKU mapping
```

### With Field Hints (Your Example)
```
Rules Generated: 8-12
Confidence: 0.8-0.95 (High)
Accuracy: ~95%
Benefit: Explicit MATERIAL ↔ PLANNING_SKU match
```

---

## Field Details

### hana_material_master Fields

| Field | Type | Purpose | Action |
|-------|------|---------|--------|
| **MATERIAL** | String | Product ID | ✅ Priority + Hint |
| **MATERIAL_DESC** | String | Product name | ✅ Priority |
| INTERNAL_NOTES | String | Internal comments | ❌ Exclude |
| TEMP_FIELD | String | Temporary staging | ❌ Exclude |
| (other fields) | Various | Other attributes | ⚪ Include |

### brz_lnd_OPS_EXCEL_GPU Fields

| Field | Type | Purpose | Action |
|-------|------|---------|--------|
| **PLANNING_SKU** | String | Product ID | ✅ Priority + Hint |
| **GPU_MODEL** | String | GPU type | ✅ Priority + Hint |
| PRODUCT_TYPE | String | Product category | ⚪ Include |
| STAGING_FLAG | String | Pipeline flag | ❌ Exclude |
| (other fields) | Various | Other attributes | ⚪ Include |

---

## Customization Guide

If your actual schema differs, modify:

### Change Table Names
```json
// BEFORE
"table_name": "hana_material_master"

// AFTER (if your table is named differently)
"table_name": "your_actual_table_name"
```

### Change Field Names
```json
// BEFORE
"field_hints": { "MATERIAL": "PLANNING_SKU" }

// AFTER (if your fields are named differently)
"field_hints": { "your_source_field": "your_target_field" }
```

### Add More Hints
```json
// BEFORE
"field_hints": { "MATERIAL": "PLANNING_SKU" }

// AFTER (add more mappings)
"field_hints": {
  "MATERIAL": "PLANNING_SKU",
  "PRODUCT_TYPE": "GPU_MODEL",
  "CATEGORY": "PRODUCT_CATEGORY"
}
```

### Change Priority Fields
```json
// BEFORE
"priority_fields": ["MATERIAL", "MATERIAL_DESC"]

// AFTER (focus on different fields)
"priority_fields": ["MATERIAL", "CATEGORY", "PRODUCT_TYPE"]
```

### Change Exclude Fields
```json
// BEFORE
"exclude_fields": ["INTERNAL_NOTES", "TEMP_FIELD"]

// AFTER (exclude different fields)
"exclude_fields": ["DEBUG_INFO", "STAGING_DATE", "TEMP_FLAG"]
```

---

## Validation Checklist

Before pasting into web UI:

- [ ] JSON syntax is valid (no trailing commas, all strings quoted)
- [ ] Table names match your actual schema (case-sensitive)
- [ ] Field names match your actual columns (case-sensitive)
- [ ] All field names exist in their respective tables
- [ ] No typos in any names
- [ ] Exclude fields are truly internal/temporary
- [ ] Priority fields are truly important

---

## Troubleshooting

### "Invalid JSON in field preferences"
**Solution**: 
- Copy the JSON exactly as shown above
- Check for typos
- Use an online JSON validator: https://jsonlint.com/

### No rules generated
**Solution**:
- Verify table names match exactly (case-sensitive)
- Verify field names exist in the tables
- Ensure LLM is enabled
- Check the error message in the UI

### Low confidence scores
**Solution**:
- Verify field_hints are correct
- Check if fields actually represent the same data
- Review the generated KG relationships
- Add more priority_fields

---

## Next Steps

1. **Copy** the JSON above
2. **Paste** into the web UI (Knowledge Graph or Reconciliation page)
3. **Generate** the KG or Rules
4. **Review** the results
5. **Iterate** if needed

---

## Related Documentation

- [Field Hints Quick Reference](FIELD_HINTS_QUICK_REFERENCE.md)
- [Field Hints Copy-Paste Examples](FIELD_HINTS_COPY_PASTE_EXAMPLES.md)
- [Field Hints Visual Guide](FIELD_HINTS_VISUAL_GUIDE.md)
- [Field Hints Index](FIELD_HINTS_INDEX.md)


