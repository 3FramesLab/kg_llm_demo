# Field Preferences Guide for Knowledge Graph Generation

## Overview

Field Preferences allow you to guide the LLM during Knowledge Graph and Reconciliation Rule generation by:
- **Prioritizing specific fields** for matching (e.g., material IDs, SKUs)
- **Providing hints** about field relationships across tables
- **Applying filters** to exclude inactive or deleted records
- **Excluding fields** that shouldn't be used for matching

This guide uses real examples from the **NewDQ database schema**.

---

## Table of Contents
1. [Schema Overview](#schema-overview)
2. [Basic Field Preferences](#basic-field-preferences)
3. [Advanced Examples with Filters](#advanced-examples-with-filters)
4. [Complete API Request Examples](#complete-api-request-examples)
5. [Best Practices](#best-practices)

---

## Schema Overview

### Tables in NewDQ Database

**1. hana_material_master** (Source - Material Master from HANA/SAP)
- **Key Fields**: `MATERIAL`, `MATERIAL_GROUP`, `MATERIAL_TYPE`, `PLANT`
- **Business Fields**: `Business Unit`, `Product Line`, `Product Type`
- **Status Fields**: `OPS_STATUS`, `MAKE_BUY`
- **Descriptive**: `OPS_MKTG_NM`, `OPS_PLANNER`

**2. brz_lnd_OPS_EXCEL_GPU** (Target - Operational Planning Excel Data)
- **Key Fields**: `PLANNING_SKU`, `Product_Line`, `Business_Unit`
- **Status Fields**: `Active_Inactive` ⚠️ (Critical for filtering!)
- **Business Fields**: `Marketing_Code`, `Planner`, `Customer`
- **Technical**: `GPU_1`, `Primary_Memory_1`, `CHIP_Family`

**3. brz_lnd_RBP_GPU** (Revenue/Business Planning)
- **Key Fields**: `Material`, `Product_Line`, `Business_Unit`
- **Time Fields**: `Fiscal_Year_Period`
- **Results**: `Overall_Result`

**4. brz_lnd_SKU_LIFNR_Excel** (SKU-Supplier Mapping)
- **Key Fields**: `Material`, `Supplier`, `Production_Version`
- **Planning**: `Reference_BOM`, `Planning_BOM`, `Lead_time`

---

## Basic Field Preferences

### Example 1: Simple Priority Fields

**Goal**: Match materials between HANA master and OPS Excel, prioritizing Material/SKU fields.

```json
{
  "field_preferences": [
    {
      "table_name": "hana_material_master",
      "priority_fields": ["MATERIAL", "MATERIAL_GROUP"],
      "exclude_fields": ["OPS_PLANNER_LAT", "OPS_PLANNER_LAT_TEXT"]
    },
    {
      "table_name": "brz_lnd_OPS_EXCEL_GPU",
      "priority_fields": ["PLANNING_SKU", "Product_Line"],
      "exclude_fields": ["NEXTVAL", "CURRVAL", "brz_LoadTime", "ETL_BatchID"]
    }
  ]
}
```

**What This Does**:
- LLM will **strongly prefer** matching `hana_material_master.MATERIAL` ↔ `brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU`
- Secondary matching on `MATERIAL_GROUP` ↔ `Product_Line`
- Ignores internal ETL columns and timestamp fields

---

### Example 2: Field Hints (Cross-Table Relationships)

**Goal**: Tell the LLM that certain fields have semantic relationships even if names differ.

```json
{
  "field_preferences": [
    {
      "table_name": "hana_material_master",
      "priority_fields": ["MATERIAL"],
      "field_hints": {
        "MATERIAL": "PLANNING_SKU",
        "Business Unit": "Business_Unit",
        "Product Line": "Product_Line",
        "OPS_MKTG_NM": "Marketing_Code"
      }
    },
    {
      "table_name": "brz_lnd_OPS_EXCEL_GPU",
      "priority_fields": ["PLANNING_SKU"],
      "field_hints": {
        "PLANNING_SKU": "MATERIAL",
        "Marketing_Code": "OPS_MKTG_NM",
        "Planner": "OPS_PLANNER"
      }
    }
  ]
}
```

**What This Does**:
- **Explicit hints**: `MATERIAL` should match with `PLANNING_SKU`
- Handles **space vs underscore** differences: `Business Unit` ↔ `Business_Unit`
- Maps marketing fields: `OPS_MKTG_NM` ↔ `Marketing_Code`

---

## Advanced Examples with Filters

### Example 3: Filter Inactive Records (CRITICAL for Production)

**Goal**: Only match **active** records, exclude inactive/deleted materials.

```json
{
  "field_preferences": [
    {
      "table_name": "hana_material_master",
      "priority_fields": ["MATERIAL", "PLANT"],
      "field_hints": {
        "MATERIAL": "PLANNING_SKU"
      },
      "filter_hints": {
        "OPS_STATUS": "Active"
      }
    },
    {
      "table_name": "brz_lnd_OPS_EXCEL_GPU",
      "priority_fields": ["PLANNING_SKU"],
      "field_hints": {
        "PLANNING_SKU": "MATERIAL"
      },
      "filter_hints": {
        "Active_Inactive": "Active"
      }
    }
  ]
}
```

**Generated SQL Filter**:
```sql
-- For hana_material_master
WHERE OPS_STATUS = 'Active'

-- For brz_lnd_OPS_EXCEL_GPU
WHERE Active_Inactive = 'Active'
```

**Result**: Only active materials will be included in reconciliation.

---

### Example 4: Multiple Filter Conditions

**Goal**: Match only specific product lines and active records.

```json
{
  "field_preferences": [
    {
      "table_name": "hana_material_master",
      "priority_fields": ["MATERIAL"],
      "filter_hints": {
        "OPS_STATUS": "Active",
        "Product Line": ["GC", "WS", "ML"],
        "MAKE_BUY": "M"
      }
    },
    {
      "table_name": "brz_lnd_OPS_EXCEL_GPU",
      "priority_fields": ["PLANNING_SKU"],
      "filter_hints": {
        "Active_Inactive": "Active",
        "Product_Line": ["GC", "WS", "ML"]
      }
    }
  ]
}
```

**Generated SQL Filter**:
```sql
-- For hana_material_master
WHERE OPS_STATUS = 'Active'
  AND "Product Line" IN ('GC', 'WS', 'ML')
  AND MAKE_BUY = 'M'

-- For brz_lnd_OPS_EXCEL_GPU
WHERE Active_Inactive = 'Active'
  AND Product_Line IN ('GC', 'WS', 'ML')
```

**Result**: Only **manufactured (MAKE_BUY='M')** materials in **specific product lines** that are **active**.

---

### Example 5: Null/Not Null Filters

**Goal**: Exclude records with missing critical fields.

```json
{
  "field_preferences": [
    {
      "table_name": "brz_lnd_OPS_EXCEL_GPU",
      "priority_fields": ["PLANNING_SKU", "Business_Unit"],
      "filter_hints": {
        "Active_Inactive": "Active",
        "PLANNING_SKU": "NOT NULL",
        "Business_Unit": "NOT NULL",
        "Do_Not_Use": null
      }
    }
  ]
}
```

**Generated SQL Filter**:
```sql
WHERE Active_Inactive = 'Active'
  AND PLANNING_SKU IS NOT NULL
  AND Business_Unit IS NOT NULL
  AND (Do_Not_Use IS NULL OR Do_Not_Use = '')
```

**Result**: Excludes records flagged with `Do_Not_Use` or missing critical identifiers.

---

### Example 6: Multi-Table Reconciliation (3+ Tables)

**Goal**: Reconcile Material Master → OPS Excel → RBP data.

```json
{
  "field_preferences": [
    {
      "table_name": "hana_material_master",
      "priority_fields": ["MATERIAL", "PLANT"],
      "field_hints": {
        "MATERIAL": "PLANNING_SKU",
        "Business Unit": "Business_Unit"
      },
      "filter_hints": {
        "OPS_STATUS": "Active"
      }
    },
    {
      "table_name": "brz_lnd_OPS_EXCEL_GPU",
      "priority_fields": ["PLANNING_SKU", "Business_Unit"],
      "field_hints": {
        "PLANNING_SKU": "Material",
        "Business_Unit": "Business_Unit"
      },
      "filter_hints": {
        "Active_Inactive": "Active"
      }
    },
    {
      "table_name": "brz_lnd_RBP_GPU",
      "priority_fields": ["Material", "Business_Unit"],
      "field_hints": {
        "Material": "PLANNING_SKU",
        "Business_Unit": "Business_Unit"
      }
    }
  ]
}
```

**Relationships Generated**:
1. `hana_material_master.MATERIAL` ↔ `brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU`
2. `brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU` ↔ `brz_lnd_RBP_GPU.Material`
3. Common join: `Business_Unit` across all tables

---

## Complete API Request Examples

### Example 7: Full KG Generation Request

**Scenario**: Create Knowledge Graph from material master and planning data, with filters.

```json
POST /api/v1/kg/generate
{
  "schema_names": ["newdqschema"],
  "kg_name": "material_planning_kg",
  "backends": ["falkordb"],
  "use_llm_enhancement": true,
  "field_preferences": [
    {
      "table_name": "hana_material_master",
      "priority_fields": ["MATERIAL", "MATERIAL_GROUP", "PLANT"],
      "exclude_fields": [
        "OPS_PLANNER_LAT",
        "OPS_PLANNER_LAT_TEXT",
        "AN_PLC_CD"
      ],
      "field_hints": {
        "MATERIAL": "PLANNING_SKU",
        "Business Unit": "Business_Unit",
        "Product Line": "Product_Line",
        "OPS_MKTG_NM": "Marketing_Code",
        "OPS_PLANNER": "Planner"
      },
      "filter_hints": {
        "OPS_STATUS": "Active",
        "Product Line": ["GC", "WS", "ML"]
      }
    },
    {
      "table_name": "brz_lnd_OPS_EXCEL_GPU",
      "priority_fields": ["PLANNING_SKU", "Product_Line", "Business_Unit"],
      "exclude_fields": [
        "NEXTVAL",
        "CURRVAL",
        "brz_LoadTime",
        "ETL_BatchID",
        "Check",
        "Do_Not_Use"
      ],
      "field_hints": {
        "PLANNING_SKU": "MATERIAL",
        "Marketing_Code": "OPS_MKTG_NM",
        "Planner": "OPS_PLANNER",
        "PLC_Code": "OPS_PLCCODE"
      },
      "filter_hints": {
        "Active_Inactive": "Active",
        "Product_Line": ["GC", "WS", "ML"],
        "Do_Not_Use": null
      }
    }
  ]
}
```

---

### Example 8: Full Reconciliation Rule Generation Request

**Scenario**: Generate reconciliation rules with filters.

```json
POST /api/v1/reconciliation/generate
{
  "schema_names": ["newdqschema"],
  "kg_name": "material_planning_kg",
  "use_llm_enhancement": true,
  "min_confidence": 0.8,
  "match_types": ["exact", "semantic"],
  "field_preferences": [
    {
      "table_name": "hana_material_master",
      "priority_fields": ["MATERIAL"],
      "field_hints": {
        "MATERIAL": "PLANNING_SKU"
      },
      "filter_hints": {
        "OPS_STATUS": "Active"
      }
    },
    {
      "table_name": "brz_lnd_OPS_EXCEL_GPU",
      "priority_fields": ["PLANNING_SKU"],
      "field_hints": {
        "PLANNING_SKU": "MATERIAL"
      },
      "filter_hints": {
        "Active_Inactive": "Active"
      }
    }
  ]
}
```

**Generated Rule Example**:
```json
{
  "rule_id": "RULE_001",
  "rule_name": "Match Materials by SKU",
  "source_table": "hana_material_master",
  "source_columns": ["MATERIAL"],
  "target_table": "brz_lnd_OPS_EXCEL_GPU",
  "target_columns": ["PLANNING_SKU"],
  "match_type": "exact",
  "filter_conditions": {
    "source": {"OPS_STATUS": "Active"},
    "target": {"Active_Inactive": "Active"}
  },
  "confidence_score": 0.95
}
```

---

## Best Practices

### 1. **Always Filter Inactive Records**

❌ **Bad** - No filtering:
```json
{
  "table_name": "brz_lnd_OPS_EXCEL_GPU",
  "priority_fields": ["PLANNING_SKU"]
}
```

✅ **Good** - Filter active records:
```json
{
  "table_name": "brz_lnd_OPS_EXCEL_GPU",
  "priority_fields": ["PLANNING_SKU"],
  "filter_hints": {
    "Active_Inactive": "Active"
  }
}
```

---

### 2. **Exclude ETL/Audit Columns**

❌ **Bad** - Include everything:
```json
{
  "table_name": "brz_lnd_OPS_EXCEL_GPU",
  "priority_fields": ["PLANNING_SKU", "NEXTVAL", "CURRVAL"]
}
```

✅ **Good** - Exclude technical columns:
```json
{
  "table_name": "brz_lnd_OPS_EXCEL_GPU",
  "priority_fields": ["PLANNING_SKU"],
  "exclude_fields": ["NEXTVAL", "CURRVAL", "brz_LoadTime", "ETL_BatchID"]
}
```

---

### 3. **Use Field Hints for Name Variations**

When column names differ but represent the same concept:

```json
{
  "field_hints": {
    "MATERIAL": "PLANNING_SKU",
    "Business Unit": "Business_Unit",
    "Product Line": "Product_Line",
    "OPS_MKTG_NM": "Marketing_Code"
  }
}
```

---

### 4. **Combine Multiple Filter Conditions**

For complex business logic:

```json
{
  "filter_hints": {
    "Active_Inactive": "Active",
    "Product_Line": ["GC", "WS", "ML"],
    "PLANNING_SKU": "NOT NULL",
    "Do_Not_Use": null
  }
}
```

---

### 5. **Priority Fields Drive Matching**

List most important fields first:

```json
{
  "priority_fields": [
    "MATERIAL",           // Primary key - highest priority
    "MATERIAL_GROUP",     // Secondary grouping
    "PLANT"               // Location context
  ]
}
```

---

## Filter Operators Reference

| Filter Value | SQL Generated | Use Case |
|--------------|---------------|----------|
| `"Active"` | `WHERE col = 'Active'` | Exact match |
| `["A", "B", "C"]` | `WHERE col IN ('A', 'B', 'C')` | Multiple values |
| `"NOT NULL"` | `WHERE col IS NOT NULL` | Exclude nulls |
| `null` | `WHERE col IS NULL OR col = ''` | Only nulls/empty |

---

## Real-World Scenarios

### Scenario 1: Material Master Reconciliation
```json
{
  "field_preferences": [
    {
      "table_name": "hana_material_master",
      "priority_fields": ["MATERIAL"],
      "filter_hints": {"OPS_STATUS": "Active"}
    },
    {
      "table_name": "brz_lnd_OPS_EXCEL_GPU",
      "priority_fields": ["PLANNING_SKU"],
      "filter_hints": {"Active_Inactive": "Active"}
    }
  ]
}
```

### Scenario 2: Product Line Specific Matching
```json
{
  "field_preferences": [
    {
      "table_name": "hana_material_master",
      "priority_fields": ["MATERIAL", "Product Line"],
      "filter_hints": {
        "OPS_STATUS": "Active",
        "Product Line": ["GC", "WS"]
      }
    },
    {
      "table_name": "brz_lnd_OPS_EXCEL_GPU",
      "priority_fields": ["PLANNING_SKU", "Product_Line"],
      "filter_hints": {
        "Active_Inactive": "Active",
        "Product_Line": ["GC", "WS"]
      }
    }
  ]
}
```

### Scenario 3: SKU-Supplier Mapping with Material Master
```json
{
  "field_preferences": [
    {
      "table_name": "hana_material_master",
      "priority_fields": ["MATERIAL"],
      "field_hints": {"MATERIAL": "Material"}
    },
    {
      "table_name": "brz_lnd_SKU_LIFNR_Excel",
      "priority_fields": ["Material", "Supplier"],
      "field_hints": {"Material": "MATERIAL"}
    }
  ]
}
```

---

## Summary

Field Preferences provide **fine-grained control** over:
1. **Which fields to prioritize** for matching
2. **How fields relate** across tables (field hints)
3. **Which records to include** (filter hints)
4. **Which fields to exclude** from consideration

**Key Benefits**:
- ✅ More accurate reconciliation rules
- ✅ Faster rule generation (focus on relevant fields)
- ✅ Exclude test/inactive/deleted data automatically
- ✅ Handle naming inconsistencies (spaces, underscores, abbreviations)

**Best Practice**: Always use `filter_hints` to exclude inactive records in production reconciliations!

---

## Additional Resources

- [KG Generation API Documentation](./KG_GENERATION_API.md)
- [Reconciliation Rules Guide](./RECONCILIATION_RULES.md)
- [KPI Management Guide](./KPI_MANAGEMENT_GUIDE.md)
