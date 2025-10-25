# Field Hints Example: HANA Material Master to OPS Excel GPU

## Overview

This document provides an elaborate example of using **field hints** to guide the LLM during Knowledge Graph (KG) generation and reconciliation rule generation. The example demonstrates how to map fields between two schemas:

- **Source Schema**: `hana_material_master` (SAP HANA)
- **Target Schema**: `brz_lnd_OPS_EXCEL_GPU` (Data Lake)

## The Mapping Challenge

### Problem
The two schemas have different field names for the same business concept:
- `hana_material_master.MATERIAL` represents a product identifier
- `brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU` represents the same product identifier

Without field hints, the LLM might:
- Miss this relationship entirely
- Create incorrect mappings
- Generate low-confidence rules

### Solution
Use **field_hints** to explicitly tell the LLM: "These fields represent the same data."

## Complete Field Preferences JSON

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

## Field Breakdown

### Table 1: hana_material_master

| Field | Type | Purpose |
|-------|------|---------|
| **MATERIAL** | String | Product identifier (primary key) |
| **MATERIAL_DESC** | String | Product description |
| INTERNAL_NOTES | String | Internal comments (excluded) |
| TEMP_FIELD | String | Temporary staging field (excluded) |

**Field Hints**: `"MATERIAL": "PLANNING_SKU"`
- Tells LLM: "MATERIAL in this table matches PLANNING_SKU in the target table"
- Confidence boost: High (explicit user guidance)

**Priority Fields**: `["MATERIAL", "MATERIAL_DESC"]`
- Focus on these fields first during relationship inference
- MATERIAL is the key identifier
- MATERIAL_DESC provides semantic context

**Exclude Fields**: `["INTERNAL_NOTES", "TEMP_FIELD"]`
- Skip these fields entirely
- Reduces noise in rule generation
- Improves performance

### Table 2: brz_lnd_OPS_EXCEL_GPU

| Field | Type | Purpose |
|-------|------|---------|
| **PLANNING_SKU** | String | Product identifier (matches MATERIAL) |
| **GPU_MODEL** | String | GPU model type |
| PRODUCT_TYPE | String | Product category |
| STAGING_FLAG | String | Data pipeline flag (excluded) |

**Field Hints**: 
- `"PLANNING_SKU": "MATERIAL"` - Bidirectional mapping (confirms the relationship)
- `"GPU_MODEL": "PRODUCT_TYPE"` - Additional mapping for GPU-specific attributes

**Priority Fields**: `["PLANNING_SKU", "GPU_MODEL"]`
- PLANNING_SKU is the key identifier
- GPU_MODEL is critical for GPU-specific reconciliation

**Exclude Fields**: `["STAGING_FLAG"]`
- Skip pipeline metadata
- Not relevant for business logic

## How This Works in Practice

### Step 1: KG Generation (with field hints)
```
User Input:
- Schema 1: hana_material_master
- Schema 2: brz_lnd_OPS_EXCEL_GPU
- Field Preferences: [above JSON]

LLM Processing:
1. Reads field hints: "MATERIAL → PLANNING_SKU"
2. Prioritizes MATERIAL and PLANNING_SKU fields
3. Infers: "These are the same business entity"
4. Creates relationship: MATERIAL --[MATCHES]--> PLANNING_SKU
5. Generates KG with high-confidence relationships

Result:
- Knowledge Graph with explicit MATERIAL ↔ PLANNING_SKU relationship
- Relationship confidence: HIGH (user-guided)
```

### Step 2: Rule Generation (using the KG)
```
Input:
- Knowledge Graph (from Step 1)
- Field Preferences: [same JSON]

LLM Processing:
1. Reads KG relationships (including MATERIAL ↔ PLANNING_SKU)
2. Applies field hints again for additional context
3. Generates reconciliation rules:
   - Rule 1: MATERIAL (hana) → PLANNING_SKU (brz_lnd) [EXACT match]
   - Rule 2: GPU_MODEL (brz_lnd) → PRODUCT_TYPE (hana) [SEMANTIC match]

Result:
- 2+ reconciliation rules with high confidence
- Rules ready for data matching and validation
```

## Usage in Web UI

### Knowledge Graph Page
1. Navigate to **Knowledge Graph** → **Generate KG** tab
2. Select schemas: `hana_material_master`, `brz_lnd_OPS_EXCEL_GPU`
3. Enable **Use LLM Enhancement**
4. Open **Field Preferences (Optional - Advanced)** accordion
5. Paste the JSON above
6. Click **Generate Knowledge Graph**

### Reconciliation Page
1. Navigate to **Reconciliation** → **Generate Rules** tab
2. Select schemas: `hana_material_master`, `brz_lnd_OPS_EXCEL_GPU`
3. Select KG: (the one generated above)
4. Enable **Use LLM Enhancement**
5. Open **Field Preferences (Optional - Advanced)** accordion
6. Paste the JSON above
7. Click **Generate Rules**

## Expected Results

### Without Field Hints
- Rules generated: ~5-8 (pattern-based only)
- Confidence: Medium (0.6-0.7)
- Accuracy: ~60% (may miss MATERIAL ↔ PLANNING_SKU)

### With Field Hints
- Rules generated: ~8-12 (pattern-based + LLM-guided)
- Confidence: High (0.8-0.95)
- Accuracy: ~95% (explicit MATERIAL ↔ PLANNING_SKU match)

## Key Takeaways

1. **Field Hints are Bidirectional**: You can specify `"A": "B"` in table A and `"B": "A"` in table B for clarity
2. **Priority Fields Focus LLM**: Use these for key identifiers and important attributes
3. **Exclude Fields Reduce Noise**: Skip staging, temporary, or internal fields
4. **Confidence Boost**: User-provided hints significantly increase rule confidence
5. **Fallback Support**: Even if LLM fails, field hints generate fallback rules

## Advanced Tips

- **Multiple Hints per Table**: Provide multiple field mappings if tables have multiple matching concepts
- **Semantic Hints**: Use hints for fields with different names but same meaning (e.g., `customer_id` → `cust_num`)
- **Hierarchical Hints**: For nested structures, hint at the parent level first
- **Iterative Refinement**: Start with key hints, then add more based on results


