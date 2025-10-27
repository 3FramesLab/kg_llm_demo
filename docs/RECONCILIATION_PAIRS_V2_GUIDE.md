# Reconciliation Pairs V2 - Complete Guide

## Summary

Version 2 introduces **relationship-centric** reconciliation pairs that explicitly define source→target table/column matching, replacing the ambiguous table-centric field_preferences approach from V1.

## Quick Comparison

| Feature | V1 (field_preferences) | V2 (reconciliation_pairs) |
|---------|------------------------|---------------------------|
| **Design** | Table-centric | Relationship-centric |
| **Clarity** | Ambiguous (which target table?) | Explicit source→target |
| **Filters** | Limited (filter_hints only) | Full control (source_filters + target_filters) |
| **Bidirectional** | Not supported | Supported |
| **Priority** | No control | Per-pair priority levels |
| **Match Type** | Auto-detected | Explicit (exact/fuzzy/semantic) |
| **KG Required** | Yes | Optional (when using explicit pairs) |

---

## The Problem with V1

### V1 Example (Ambiguous)

```json
{
  "field_preferences": [
    {
      "table_name": "hana_material_master",
      "field_hints": {
        "MATERIAL": "PLANNING_SKU"
      }
    },
    {
      "table_name": "brz_lnd_OPS_EXCEL_GPU",
      "field_hints": {
        "PLANNING_SKU": "Material"
      }
    },
    {
      "table_name": "brz_lnd_RBP_GPU",
      "field_hints": {
        "Material": "PLANNING_SKU"
      }
    }
  ]
}
```

### Issues

❌ **Ambiguity**: Does `MATERIAL: "PLANNING_SKU"` mean:
- Match hana_material_master.MATERIAL → brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU?
- Or some other table with PLANNING_SKU column?

❌ **Missing Relationships**: System cannot create rules between `brz_lnd_OPS_EXCEL_GPU` and `brz_lnd_RBP_GPU` because the KG doesn't have this relationship.

❌ **No Filter Control**: Cannot specify that only `Active_Inactive='Active'` records should be matched.

❌ **No Bidirectional**: Cannot specify that a relationship should work both ways.

---

## V2 Solution: Explicit Reconciliation Pairs

### V2 Example (Clear & Precise)

```json
{
  "reconciliation_pairs": [
    {
      "source_table": "hana_material_master",
      "source_columns": ["MATERIAL"],
      "target_table": "brz_lnd_OPS_EXCEL_GPU",
      "target_columns": ["PLANNING_SKU"],
      "match_type": "exact",
      "source_filters": null,
      "target_filters": {
        "Active_Inactive": "Active"
      },
      "bidirectional": true,
      "priority": "high"
    },
    {
      "source_table": "brz_lnd_OPS_EXCEL_GPU",
      "source_columns": ["PLANNING_SKU"],
      "target_table": "brz_lnd_RBP_GPU",
      "target_columns": ["Material"],
      "match_type": "exact",
      "bidirectional": false,
      "priority": "normal"
    },
    {
      "source_table": "brz_lnd_RBP_GPU",
      "source_columns": ["Material"],
      "target_table": "brz_lnd_SKU_LIFNR_Excel",
      "target_columns": ["Material"],
      "match_type": "exact",
      "bidirectional": false,
      "priority": "normal"
    }
  ],
  "auto_discover_additional": true
}
```

### Benefits

✅ **Explicit**: Each pair clearly states source→target relationship
✅ **Complete Control**: Filters, match types, transformations all specified per pair
✅ **No KG Required**: Pairs work independently of KG relationships
✅ **Bidirectional**: Can specify if relationship works both ways
✅ **Priority**: Control which rules take precedence

---

## ReconciliationPair Model

### Full Specification

```python
class ReconciliationPair(BaseModel):
    # Required Fields
    source_table: str                        # Source table name
    source_columns: List[str]                # Source columns to match
    target_table: str                        # Target table name
    target_columns: List[str]                # Target columns to match

    # Optional Configuration
    match_type: ReconciliationMatchType = "exact"    # exact | fuzzy | semantic
    source_filters: Optional[Dict[str, Any]] = None  # WHERE conditions for source
    target_filters: Optional[Dict[str, Any]] = None  # WHERE conditions for target
    transformation: Optional[str] = None             # SQL transformation (e.g., "UPPER(column)")
    bidirectional: bool = False                      # Create reverse rule too?
    priority: str = "normal"                         # low | normal | high
    confidence_override: Optional[float] = None      # Override default confidence score
```

### Match Types

```python
class ReconciliationMatchType(str, Enum):
    EXACT = "exact"          # Exact equality (=)
    FUZZY = "fuzzy"          # Fuzzy matching (Levenshtein distance, soundex)
    SEMANTIC = "semantic"    # LLM-based semantic matching
```

---

## Complete API Example

### Request

```bash
POST /v1/reconciliation/generate
Content-Type: application/json

{
  "kg_name": "four_way_material_kg",
  "schema_names": [
    "hana-material-schema",
    "ops-excel-schema",
    "rbp-gpu-schema",
    "sku-lifnr-schema"
  ],
  "use_llm_enhancement": true,
  "min_confidence": 0.75,
  "reconciliation_pairs": [
    {
      "source_table": "hana_material_master",
      "source_columns": ["MATERIAL"],
      "target_table": "brz_lnd_OPS_EXCEL_GPU",
      "target_columns": ["PLANNING_SKU"],
      "match_type": "exact",
      "target_filters": {
        "Active_Inactive": "Active"
      },
      "bidirectional": true,
      "priority": "high",
      "confidence_override": 0.98
    },
    {
      "source_table": "brz_lnd_OPS_EXCEL_GPU",
      "source_columns": ["PLANNING_SKU"],
      "target_table": "brz_lnd_RBP_GPU",
      "target_columns": ["Material"],
      "match_type": "exact",
      "source_filters": {
        "Active_Inactive": "Active"
      },
      "bidirectional": false
    },
    {
      "source_table": "brz_lnd_RBP_GPU",
      "source_columns": ["Material"],
      "target_table": "brz_lnd_SKU_LIFNR_Excel",
      "target_columns": ["Material"],
      "match_type": "exact"
    }
  ],
  "auto_discover_additional": true
}
```

### Response

```json
{
  "success": true,
  "ruleset_id": "RECON_ABC12345",
  "rules_count": 8,
  "generation_time_ms": 1250.5,
  "message": "Generated 8 reconciliation rules (4 explicit, 4 auto-discovered)",
  "rules": [
    {
      "rule_id": "RULE_A1B2C3D4",
      "rule_name": "Explicit_hana_material_master_to_brz_lnd_OPS_EXCEL_GPU",
      "source_schema": "hana_db",
      "source_table": "hana_material_master",
      "source_columns": ["MATERIAL"],
      "target_schema": "ops_excel_db",
      "target_table": "brz_lnd_OPS_EXCEL_GPU",
      "target_columns": ["PLANNING_SKU"],
      "match_type": "exact",
      "filter_conditions": {
        "target.Active_Inactive": "Active"
      },
      "confidence_score": 0.98,
      "reasoning": "Explicit user-defined reconciliation pair (priority: high)",
      "validation_status": "VALID",
      "llm_generated": false,
      "metadata": {
        "source": "explicit_pair_v2",
        "priority": "high",
        "bidirectional": true
      }
    },
    {
      "rule_id": "RULE_E5F6G7H8",
      "rule_name": "Reverse_brz_lnd_OPS_EXCEL_GPU_to_hana_material_master",
      "source_schema": "ops_excel_db",
      "source_table": "brz_lnd_OPS_EXCEL_GPU",
      "source_columns": ["PLANNING_SKU"],
      "target_schema": "hana_db",
      "target_table": "hana_material_master",
      "target_columns": ["MATERIAL"],
      "match_type": "exact",
      "filter_conditions": {
        "source.Active_Inactive": "Active"
      },
      "confidence_score": 0.98,
      "reasoning": "Explicit user-defined reconciliation pair (priority: high)",
      "validation_status": "VALID",
      "llm_generated": false,
      "metadata": {
        "source": "explicit_pair_v2_reverse",
        "priority": "high"
      }
    }
  ]
}
```

---

## Using the Web UI

### Step 1: Navigate to Reconciliation Page

1. Go to **Reconciliation Rule Generation** page
2. Select your schemas and knowledge graph
3. Click **Advanced Options** accordion

### Step 2: Select V2 Mode

- Choose **V2: Reconciliation Pairs (Explicit source→target) - Recommended**

### Step 3: Define Pairs

Enter your reconciliation pairs in JSON format:

```json
[
  {
    "source_table": "products",
    "source_columns": ["product_id"],
    "target_table": "inventory",
    "target_columns": ["item_id"],
    "match_type": "exact",
    "bidirectional": true
  }
]
```

### Step 4: Configure Auto-Discovery

- ✅ **Enable** "Auto-discover additional rules from Knowledge Graph" to supplement explicit pairs with KG-discovered rules
- ❌ **Disable** to use ONLY your explicit pairs (no KG discovery)

### Step 5: Generate Rules

Click **Generate Rules** and view the results showing:
- Number of explicit rules created
- Number of auto-discovered rules (if enabled)
- Total rule count

---

## Advanced Features

### 1. Multi-Column Matching

Match on multiple columns simultaneously:

```json
{
  "source_table": "orders",
  "source_columns": ["customer_id", "order_date"],
  "target_table": "invoices",
  "target_columns": ["client_id", "invoice_date"],
  "match_type": "exact"
}
```

Generated SQL:
```sql
SELECT *
FROM orders o
INNER JOIN invoices i
  ON o.customer_id = i.client_id
  AND o.order_date = i.invoice_date
```

### 2. Complex Filters

Apply complex WHERE conditions:

```json
{
  "source_table": "products",
  "source_columns": ["sku"],
  "target_table": "catalog",
  "target_columns": ["product_code"],
  "source_filters": {
    "status": "active",
    "category": "electronics"
  },
  "target_filters": {
    "is_available": true,
    "stock_quantity": ">0"
  }
}
```

Generated SQL:
```sql
SELECT *
FROM products p
INNER JOIN catalog c ON p.sku = c.product_code
WHERE p.status = 'active'
  AND p.category = 'electronics'
  AND c.is_available = 1
  AND c.stock_quantity > 0
```

### 3. Transformations

Apply SQL transformations:

```json
{
  "source_table": "customers",
  "source_columns": ["email"],
  "target_table": "users",
  "target_columns": ["email_address"],
  "transformation": "LOWER(TRIM(email))",
  "match_type": "exact"
}
```

Generated SQL:
```sql
SELECT *
FROM customers c
INNER JOIN users u
  ON LOWER(TRIM(c.email)) = LOWER(TRIM(u.email_address))
```

### 4. Confidence Override

Control confidence scores:

```json
{
  "source_table": "legacy_products",
  "source_columns": ["old_id"],
  "target_table": "new_products",
  "target_columns": ["new_id"],
  "confidence_override": 0.65,
  "match_type": "fuzzy"
}
```

**Use Case**: Legacy migrations where fuzzy matching is needed but you want to explicitly set a lower confidence threshold.

---

## Migration Guide: V1 → V2

### Step 1: Identify Your V1 Field Preferences

**V1 (Before)**:
```json
{
  "field_preferences": [
    {
      "table_name": "products",
      "field_hints": {
        "product_id": "item_id"
      },
      "priority_fields": ["product_id", "product_name"],
      "filter_hints": {
        "status": "active"
      }
    },
    {
      "table_name": "inventory",
      "field_hints": {
        "item_id": "product_id"
      }
    }
  ]
}
```

### Step 2: Convert to V2 Reconciliation Pairs

**V2 (After)**:
```json
{
  "reconciliation_pairs": [
    {
      "source_table": "products",
      "source_columns": ["product_id"],
      "target_table": "inventory",
      "target_columns": ["item_id"],
      "match_type": "exact",
      "source_filters": {
        "status": "active"
      },
      "bidirectional": true
    }
  ]
}
```

### Key Changes

1. **Explicit Direction**: `field_hints` becomes explicit `source_table → target_table`
2. **Filter Promotion**: `filter_hints` becomes `source_filters` and `target_filters`
3. **Bidirectional**: Add `bidirectional: true` if relationship works both ways
4. **Priority Fields**: No longer needed (explicit pairs are already prioritized)

---

## Use Cases & Best Practices

### Use Case 1: Multi-Table Material Reconciliation

**Scenario**: Match materials across HANA, OPS Excel, RBP GPU, and SKU LIFNR tables.

**Solution**:
```json
{
  "reconciliation_pairs": [
    {
      "source_table": "hana_material_master",
      "source_columns": ["MATERIAL"],
      "target_table": "brz_lnd_OPS_EXCEL_GPU",
      "target_columns": ["PLANNING_SKU"],
      "target_filters": {"Active_Inactive": "Active"},
      "bidirectional": true,
      "priority": "high"
    },
    {
      "source_table": "brz_lnd_OPS_EXCEL_GPU",
      "source_columns": ["PLANNING_SKU"],
      "target_table": "brz_lnd_RBP_GPU",
      "target_columns": ["Material"],
      "source_filters": {"Active_Inactive": "Active"}
    },
    {
      "source_table": "brz_lnd_RBP_GPU",
      "source_columns": ["Material"],
      "target_table": "brz_lnd_SKU_LIFNR_Excel",
      "target_columns": ["Material"]
    }
  ],
  "auto_discover_additional": true
}
```

**Benefit**: Creates 4+ explicit rules (with bidirectional) + auto-discovered supplementary rules.

### Use Case 2: Legacy System Migration

**Scenario**: Migrate from old customer database to new CRM, fuzzy matching on names.

**Solution**:
```json
{
  "reconciliation_pairs": [
    {
      "source_table": "legacy_customers",
      "source_columns": ["customer_name"],
      "target_table": "crm_contacts",
      "target_columns": ["full_name"],
      "match_type": "fuzzy",
      "confidence_override": 0.70,
      "transformation": "UPPER(TRIM(customer_name))"
    }
  ],
  "auto_discover_additional": false
}
```

**Benefit**: Controlled fuzzy matching with transformation, no auto-discovery interference.

### Use Case 3: Data Quality Checks

**Scenario**: Find orphaned records (products without vendors).

**Solution**:
```json
{
  "reconciliation_pairs": [
    {
      "source_table": "products",
      "source_columns": ["vendor_id"],
      "target_table": "vendors",
      "target_columns": ["id"],
      "match_type": "exact"
    }
  ]
}
```

Then run execution and analyze unmatched records.

---

## Troubleshooting

### Issue 1: "Could not find schema for tables"

**Error**:
```
Could not find schema for tables: my_table or other_table
```

**Solution**: Ensure table names match exactly (case-sensitive) with schema definitions.

```bash
# List schemas to verify table names
GET /v1/schemas
```

### Issue 2: "Invalid columns in pair"

**Error**:
```
Invalid columns in pair: products.product_id → inventory.item_id
```

**Solution**: Verify column names exist in their respective tables.

```bash
# Get schema details
GET /v1/schemas/{schema_name}
```

### Issue 3: No Rules Generated

**Scenario**: Sent explicit pairs but got 0 rules.

**Checklist**:
1. Verify `min_confidence` is not too high (try 0.5)
2. Check JSON syntax is valid
3. Ensure table/column names are correct (case-sensitive)
4. Verify schemas are loaded into the system

---

## API Reference

### POST /v1/reconciliation/generate

Generate reconciliation rules using v2 reconciliation pairs.

**Request Body**:
```typescript
{
  kg_name: string                              // Knowledge graph name
  schema_names: string[]                        // List of schemas
  use_llm_enhancement: boolean                  // Enable LLM rules
  min_confidence: number                        // Minimum confidence (0.0-1.0)

  // V2 (Recommended)
  reconciliation_pairs?: ReconciliationPair[]   // Explicit pairs
  table_hints?: TableHint[]                     // Optional discovery hints
  auto_discover_additional?: boolean            // Auto-discover from KG (default: true)

  // V1 (Legacy - Backward compatible)
  field_preferences?: FieldPreference[]         // Table-centric hints
}
```

**Response**:
```typescript
{
  success: boolean
  ruleset_id: string
  rules_count: number
  rules: ReconciliationRule[]
  generation_time_ms: number
  message: string  // "Generated N rules (X explicit, Y auto-discovered)"
}
```

---

## Python SDK Example

```python
import requests

BASE_URL = "http://localhost:8000/v1"

# Define explicit reconciliation pairs
pairs = [
    {
        "source_table": "products",
        "source_columns": ["product_id"],
        "target_table": "inventory",
        "target_columns": ["item_id"],
        "match_type": "exact",
        "source_filters": {"status": "active"},
        "bidirectional": True
    },
    {
        "source_table": "inventory",
        "source_columns": ["item_id"],
        "target_table": "warehouse",
        "target_columns": ["stock_id"],
        "match_type": "exact"
    }
]

# Generate rules
response = requests.post(
    f"{BASE_URL}/reconciliation/generate",
    json={
        "kg_name": "product_kg",
        "schema_names": ["products-schema", "inventory-schema", "warehouse-schema"],
        "use_llm_enhancement": True,
        "min_confidence": 0.75,
        "reconciliation_pairs": pairs,
        "auto_discover_additional": True
    }
)

result = response.json()
print(f"Ruleset ID: {result['ruleset_id']}")
print(f"Rules: {result['rules_count']}")
print(f"Message: {result['message']}")

# Export to SQL
sql_response = requests.get(
    f"{BASE_URL}/reconciliation/rulesets/{result['ruleset_id']}/export/sql"
)

with open(f"{result['ruleset_id']}.sql", 'w') as f:
    f.write(sql_response.json()['sql'])
```

---

## Related Documentation

- [Natural Language to Rules Workflow](NL_TO_RULES_COMPLETE_WORKFLOW.md)
- [Reconciliation Execution Guide](RECONCILIATION_EXECUTION_GUIDE.md)
- [KPI Feature Guide](KPI_FEATURE_COMPLETE_GUIDE.md)

---

## Changelog

### 2025-10-27 - V2 Release

**Added**:
- ✅ ReconciliationPair model with explicit source→target
- ✅ TableHint model for optional auto-discovery
- ✅ Support for source_filters and target_filters
- ✅ Bidirectional rule creation
- ✅ Per-pair priority and confidence override
- ✅ Web UI toggle for v1/v2 modes

**Maintained**:
- ✅ V1 field_preferences (backward compatible)
- ✅ All existing API endpoints
- ✅ Auto-discovery from Knowledge Graph

---

## Feedback

For issues or feature requests, please report at:
https://github.com/anthropics/claude-code/issues

---

**Version**: 2.0
**Date**: 2025-10-27
**Status**: ✅ Complete and Tested
