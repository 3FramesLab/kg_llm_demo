# Knowledge Graph Relationship Pairs - Complete Guide

## 🎯 The Right Architecture

This guide explains the **v2 relationship-centric approach** for building Knowledge Graphs with explicit source→target relationships stored directly in the KG.

---

## Why Relationship Pairs at KG Level?

### The Problem with V1 (Field Hints at Rule Generation)

**Before (Wrong Approach):**
```
1. KG Creation with NL → Ambiguous relationships in KG
2. Rule Generation with field_preferences → Try to patch ambiguity
3. Generated Rules → Still missing relationships not in KG
```

❌ **Issue**: KG has incomplete/ambiguous relationships. Rule generation tries to compensate but can't add what's not in KG.

### The Solution: V2 (Explicit Pairs at KG Creation)

**After (Correct Approach):**
```
1. KG Creation with explicit relationship_pairs → Clear source→target in KG
2. Rule Generation → Reads clear KG relationships
3. Generated Rules → Complete and unambiguous
```

✅ **Benefit**: KG is the single source of truth with unambiguous relationships from the start!

---

## Architecture Overview

### Data Flow

```
┌─────────────────────────────────────────────┐
│  1. KG CREATION                             │
│  (/v1/kg/integrate-nl-relationships)        │
│                                             │
│  Input:                                     │
│  - Natural Language Definitions (V1)        │
│  - Explicit Relationship Pairs (V2) ✅      │
│                                             │
│  Output: Knowledge Graph with relationships │
└────────────────┬────────────────────────────┘
                 │
                 │ KG stored in FalkorDB
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  2. RULE GENERATION                         │
│  (/v1/reconciliation/generate)              │
│                                             │
│  Reads KG → Generates reconciliation rules  │
│                                             │
│  Output: Ruleset with SQL queries           │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  3. RULE EXECUTION                          │
│  (/v1/reconciliation/execute)               │
│                                             │
│  Executes SQL → Match/unmatch records       │
│                                             │
│  Output: Reconciliation results + KPIs      │
└─────────────────────────────────────────────┘
```

---

## RelationshipPair Model

### Full Specification

```python
class RelationshipPair(BaseModel):
    """Explicit relationship for KG creation."""
    # Required
    source_table: str          # Source table name
    source_column: str         # Source column name
    target_table: str          # Target table name
    target_column: str         # Target column name

    # Optional
    relationship_type: KGRelationshipType = "MATCHES"  # See enum below
    confidence: float = 0.95   # 0.0-1.0
    bidirectional: bool = False  # Create reverse too?
    metadata: Optional[Dict[str, Any]] = None  # Additional info
```

### Relationship Types

```python
class KGRelationshipType(str, Enum):
    MATCHES = "MATCHES"                      # Equal (e.g., product_id = item_id)
    REFERENCES = "REFERENCES"                # Foreign key reference
    FOREIGN_KEY = "FOREIGN_KEY"              # Explicit FK constraint
    CROSS_SCHEMA_REFERENCE = "CROSS_SCHEMA_REFERENCE"  # Across schemas
    SEMANTIC_REFERENCE = "SEMANTIC_REFERENCE"  # LLM-inferred
    CONTAINS = "CONTAINS"                    # One-to-many
    BELONGS_TO = "BELONGS_TO"                # Many-to-one
    RELATED_TO = "RELATED_TO"                # Generic
```

---

## API Usage

### Endpoint: POST /v1/kg/integrate-nl-relationships

Supports both V1 (natural language) and V2 (explicit pairs) approaches.

#### V2 Example (Recommended)

```bash
POST /v1/kg/integrate-nl-relationships
Content-Type: application/json

{
  "kg_name": "four_way_material_kg",
  "schemas": [
    "hana-material-schema",
    "ops-excel-schema",
    "rbp-gpu-schema",
    "sku-lifnr-schema"
  ],
  "relationship_pairs": [
    {
      "source_table": "hana_material_master",
      "source_column": "MATERIAL",
      "target_table": "brz_lnd_OPS_EXCEL_GPU",
      "target_column": "PLANNING_SKU",
      "relationship_type": "MATCHES",
      "confidence": 0.98,
      "bidirectional": true
    },
    {
      "source_table": "brz_lnd_OPS_EXCEL_GPU",
      "source_column": "PLANNING_SKU",
      "target_table": "brz_lnd_RBP_GPU",
      "target_column": "Material",
      "relationship_type": "MATCHES",
      "confidence": 0.95
    },
    {
      "source_table": "brz_lnd_RBP_GPU",
      "source_column": "Material",
      "target_table": "brz_lnd_SKU_LIFNR_Excel",
      "target_column": "Material",
      "relationship_type": "MATCHES"
    }
  ],
  "use_llm": true,
  "min_confidence": 0.75
}
```

#### Response

```json
{
  "success": true,
  "kg_name": "four_way_material_kg",
  "nodes_count": 120,
  "relationships_count": 250,
  "nl_relationships_added": 0,
  "explicit_pairs_added": 4,
  "total_relationships": 250,
  "statistics": {
    "nl_defined": 0,
    "explicit_pairs": 4,
    "auto_detected": 246
  },
  "processing_time_ms": 1250.5
}
```

**Note**: With `bidirectional: true` on the first pair, it creates 4 relationships (3 explicit + 1 reverse).

---

## Complete Workflow Example

### Step 1: Create KG with Explicit Pairs

```python
import requests

BASE_URL = "http://localhost:8000/v1"

# Define explicit relationship pairs
pairs = [
    {
        "source_table": "hana_material_master",
        "source_column": "MATERIAL",
        "target_table": "brz_lnd_OPS_EXCEL_GPU",
        "target_column": "PLANNING_SKU",
        "relationship_type": "MATCHES",
        "confidence": 0.98,
        "bidirectional": True,
        "metadata": {
            "notes": "Primary material matching field",
            "source": "user_defined"
        }
    },
    {
        "source_table": "brz_lnd_OPS_EXCEL_GPU",
        "source_column": "PLANNING_SKU",
        "target_table": "brz_lnd_RBP_GPU",
        "target_column": "Material",
        "relationship_type": "MATCHES",
        "confidence": 0.95
    },
    {
        "source_table": "brz_lnd_RBP_GPU",
        "source_column": "Material",
        "target_table": "brz_lnd_SKU_LIFNR_Excel",
        "target_column": "Material",
        "relationship_type": "MATCHES"
    }
]

# Create KG with explicit pairs
kg_response = requests.post(
    f"{BASE_URL}/kg/integrate-nl-relationships",
    json={
        "kg_name": "four_way_material_kg",
        "schemas": [
            "hana-material-schema",
            "ops-excel-schema",
            "rbp-gpu-schema",
            "sku-lifnr-schema"
        ],
        "relationship_pairs": pairs,
        "use_llm": True,
        "min_confidence": 0.75
    }
)

print(f"KG created with {kg_response.json()['explicit_pairs_added']} explicit pairs")
```

### Step 2: Generate Rules from KG

```python
# Generate reconciliation rules
rules_response = requests.post(
    f"{BASE_URL}/reconciliation/generate",
    json={
        "kg_name": "four_way_material_kg",
        "schema_names": [
            "hana-material-schema",
            "ops-excel-schema",
            "rbp-gpu-schema",
            "sku-lifnr-schema"
        ],
        "use_llm_enhancement": True,
        "min_confidence": 0.75
    }
)

ruleset = rules_response.json()
print(f"Ruleset ID: {ruleset['ruleset_id']}")
print(f"Rules count: {ruleset['rules_count']}")
```

### Step 3: Execute Rules

```python
# Execute reconciliation
exec_response = requests.post(
    f"{BASE_URL}/reconciliation/execute",
    json={
        "ruleset_id": ruleset['ruleset_id'],
        "source_db_config": {...},
        "target_db_config": {...}
    }
)

results = exec_response.json()
print(f"Matched: {results['matched_count']}")
print(f"Unmatched: {results['unmatched_source']}")
```

---

## Web UI Usage

### Step 1: Navigate to Natural Language Page

1. Open the web app
2. Go to **Natural Language to Reconciliation Rules** page

### Step 2: Select V2 Mode

- Select **Explicit Pairs (V2 - Recommended)**

### Step 3: Enter Relationship Pairs

Enter JSON array of relationship pairs:

```json
[
  {
    "source_table": "products",
    "source_column": "product_id",
    "target_table": "inventory",
    "target_column": "item_id",
    "relationship_type": "MATCHES",
    "confidence": 0.95,
    "bidirectional": true
  }
]
```

### Step 4: Generate

Click **Integrate & Generate Rules** and see:
- Explicit pairs added to KG
- Rules generated from KG
- Ruleset ID for execution

---

## Comparison: V1 vs V2

### V1 Example (Natural Language - Ambiguous)

```json
{
  "nl_definitions": [
    "hana_material_master.MATERIAL matches brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU",
    "Products are supplied by Vendors"
  ]
}
```

**Issues:**
- ❌ Parser may misinterpret
- ❌ Ambiguous table references
- ❌ No control over confidence
- ❌ Can't specify bidirectional

### V2 Example (Explicit Pairs - Clear)

```json
{
  "relationship_pairs": [
    {
      "source_table": "hana_material_master",
      "source_column": "MATERIAL",
      "target_table": "brz_lnd_OPS_EXCEL_GPU",
      "target_column": "PLANNING_SKU",
      "relationship_type": "MATCHES",
      "confidence": 0.98,
      "bidirectional": true
    }
  ]
}
```

**Benefits:**
- ✅ Explicit source→target
- ✅ Column-level precision
- ✅ Controlled confidence
- ✅ Bidirectional support
- ✅ No parsing ambiguity

---

## Advanced Features

### 1. Bidirectional Relationships

Create relationships that work both ways:

```json
{
  "source_table": "customers",
  "source_column": "customer_id",
  "target_table": "orders",
  "target_column": "customer_id",
  "relationship_type": "REFERENCES",
  "bidirectional": true
}
```

**Result**: Creates two relationships:
1. customers.customer_id → orders.customer_id (REFERENCES)
2. orders.customer_id → customers.customer_id (REFERENCES - reverse)

### 2. Relationship Types

Use semantic relationship types:

```json
{
  "source_table": "orders",
  "source_column": "order_id",
  "target_table": "order_items",
  "target_column": "order_id",
  "relationship_type": "CONTAINS"
}
```

### 3. Custom Metadata

Add custom metadata to relationships:

```json
{
  "source_table": "products",
  "source_column": "sku",
  "target_table": "catalog",
  "target_column": "product_code",
  "relationship_type": "MATCHES",
  "metadata": {
    "business_owner": "Product Team",
    "validated_date": "2025-10-27",
    "notes": "Primary product identifier across systems"
  }
}
```

### 4. Combining V1 and V2

Use both natural language AND explicit pairs:

```json
{
  "kg_name": "unified_kg",
  "schemas": ["schema1", "schema2"],
  "nl_definitions": [
    "Products are supplied by Vendors"
  ],
  "relationship_pairs": [
    {
      "source_table": "products",
      "source_column": "vendor_id",
      "target_table": "vendors",
      "target_column": "id",
      "relationship_type": "FOREIGN_KEY"
    }
  ]
}
```

---

## Migration Guide: NL → Explicit Pairs

### Before (Natural Language)

```json
{
  "nl_definitions": [
    "hana_material_master.MATERIAL matches PLANNING_SKU"
  ]
}
```

**Problem**: Which table has PLANNING_SKU? Ambiguous!

### After (Explicit Pairs)

```json
{
  "relationship_pairs": [
    {
      "source_table": "hana_material_master",
      "source_column": "MATERIAL",
      "target_table": "brz_lnd_OPS_EXCEL_GPU",
      "target_column": "PLANNING_SKU",
      "relationship_type": "MATCHES"
    }
  ]
}
```

**Solution**: Explicit table and column names. No ambiguity!

---

## Use Cases

### Use Case 1: Four-Way Material Reconciliation

**Scenario**: Match materials across 4 different systems.

**Solution**:
```json
{
  "relationship_pairs": [
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
}
```

**Result**: Complete relationship chain with no missing links!

### Use Case 2: Cross-System Customer Matching

**Scenario**: Match customers across CRM, ERP, and billing systems.

**Solution**:
```json
{
  "relationship_pairs": [
    {
      "source_table": "crm_customers",
      "source_column": "customer_id",
      "target_table": "erp_clients",
      "target_column": "client_code",
      "relationship_type": "MATCHES",
      "confidence": 0.90
    },
    {
      "source_table": "erp_clients",
      "source_column": "client_code",
      "target_table": "billing_accounts",
      "target_column": "account_number",
      "relationship_type": "MATCHES",
      "confidence": 0.85
    }
  ]
}
```

### Use Case 3: Inventory Hierarchy

**Scenario**: Define product hierarchy (categories contain products).

**Solution**:
```json
{
  "relationship_pairs": [
    {
      "source_table": "categories",
      "source_column": "category_id",
      "target_table": "products",
      "target_column": "category_id",
      "relationship_type": "CONTAINS",
      "bidirectional": false
    }
  ]
}
```

**Note**: Reverse would be `products BELONGS_TO categories` (automatic if bidirectional: true).

---

## Troubleshooting

### Issue 1: "Source table 'X' not found in any schema"

**Cause**: Table name doesn't match schema definition (case-sensitive).

**Solution**: List schemas and verify table names:
```bash
GET /v1/schemas/{schema_name}
```

### Issue 2: "Source column 'Y' not found in table 'X'"

**Cause**: Column name doesn't exist or is misspelled.

**Solution**: Check schema for exact column names (case-sensitive).

### Issue 3: No rules generated from KG

**Cause**: Relationships in KG but not recognized by rule generator.

**Solution**:
1. Check relationship types are standard (MATCHES, REFERENCES, etc.)
2. Verify confidence scores meet min_confidence threshold
3. Ensure tables/columns are valid in schemas

---

## Best Practices

### 1. Use Explicit Pairs for Critical Relationships

✅ **Do**: Define business-critical relationships as explicit pairs
```json
{
  "source_table": "orders",
  "source_column": "order_id",
  "target_table": "invoices",
  "target_column": "order_reference",
  "relationship_type": "REFERENCES",
  "confidence": 1.0
}
```

❌ **Don't**: Rely on natural language for critical relationships
```json
{
  "nl_definitions": ["Orders reference Invoices"]
}
```

### 2. Use Bidirectional Sparingly

✅ **Do**: Use bidirectional for symmetric relationships
```json
{
  "relationship_type": "MATCHES",
  "bidirectional": true
}
```

❌ **Don't**: Use bidirectional for hierarchical relationships
```json
{
  "relationship_type": "CONTAINS",  // One-way only!
  "bidirectional": false
}
```

### 3. Set Appropriate Confidence Scores

- **1.0**: Known foreign keys, exact matches
- **0.9-0.95**: Business-validated relationships
- **0.75-0.85**: Inferred but likely relationships
- **< 0.75**: Uncertain relationships (may be filtered out)

---

## FAQ

### Q: Can I use both NL definitions and explicit pairs?

**A**: Yes! You can combine them:
```json
{
  "nl_definitions": ["Products are supplied by Vendors"],
  "relationship_pairs": [{...}]
}
```

### Q: What happens to auto-detected relationships?

**A**: They're preserved! Explicit pairs are added to auto-detected relationships, creating a complete KG.

### Q: Can I update existing relationships?

**A**: Yes, re-run the integration endpoint with updated pairs. The merge_strategy controls how duplicates are handled.

### Q: Do explicit pairs require LLM?

**A**: No! Explicit pairs work without LLM. Set `use_llm: false` for faster processing.

---

## Related Documentation

- [Reconciliation Pairs V2 (Rule Generation Level)](RECONCILIATION_PAIRS_V2_GUIDE.md)
- [Natural Language to Rules Workflow](NL_TO_RULES_COMPLETE_WORKFLOW.md)
- [Natural Language Examples](NATURAL_LANGUAGE_RULES_EXAMPLES.md)

---

## Changelog

### 2025-10-27 - V2 KG-Level Relationship Pairs

**Added**:
- ✅ RelationshipPair model for KG creation
- ✅ KGRelationshipType enum with semantic types
- ✅ kg_relationship_service for processing pairs
- ✅ Updated /v1/kg/integrate-nl-relationships endpoint
- ✅ Web UI support in Natural Language page
- ✅ Bidirectional relationship support

**Maintained**:
- ✅ V1 natural language definitions (backward compatible)
- ✅ Auto-discovery from schema analysis
- ✅ All existing KG operations

---

**Version**: 2.0 (KG Level)
**Date**: 2025-10-27
**Status**: ✅ Complete and Tested
