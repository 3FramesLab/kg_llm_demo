# Natural Language to Rules - Complete Workflow

## The Question

> "Why doesn't `/v1/kg/relationships/natural-language` automatically create reconciliation rulesets?"

## TL;DR

The API is designed in **3 levels** for flexibility:

1. **Level 1:** Parse only (preview) - `/kg/relationships/natural-language`
2. **Level 2:** Integrate to KG - `/kg/integrate-nl-relationships` ✅ **Use this!**
3. **Level 3:** Generate rules - `/reconciliation/generate`

To get from natural language to rules, use **Level 2 + Level 3** together.

---

## The 3 API Levels Explained

### Level 1: Parse Only (Preview)

```
POST /v1/kg/relationships/natural-language
```

**What it does:**
- ✅ Parses natural language text
- ✅ Returns relationship definitions as JSON
- ❌ Does NOT save to knowledge graph
- ❌ Does NOT generate reconciliation rules

**When to use:**
- Preview what relationships will be created
- Validate your natural language syntax
- Test different confidence thresholds
- See parsing results before committing

**Example:**
```bash
curl -X POST http://localhost:8000/v1/kg/relationships/natural-language \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "test_kg",
    "schemas": ["schema1", "schema2"],
    "definitions": ["Products are supplied by Vendors"],
    "use_llm": true,
    "min_confidence": 0.7
  }'
```

**Response:**
```json
{
  "success": true,
  "relationships": [...],
  "parsed_count": 1,
  "failed_count": 0
}
```

❌ **No KG update, no rules created**

---

### Level 2: Integrate to Knowledge Graph

```
POST /v1/kg/integrate-nl-relationships
```

**What it does:**
- ✅ Parses natural language text
- ✅ **Saves relationships to knowledge graph**
- ✅ Merges with auto-detected relationships
- ❌ Still does NOT generate reconciliation rules

**When to use:**
- Build up your knowledge graph with custom relationships
- Add domain-specific relationships not detected automatically
- Prepare the KG before generating rules

**Example:**
```bash
curl -X POST http://localhost:8000/v1/kg/integrate-nl-relationships \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "material_kg",
    "schemas": ["hana-material-schema", "ops-excel-schema"],
    "nl_definitions": [
      "hana_material_master.MATERIAL matches brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU",
      "Products are supplied by Vendors"
    ],
    "use_llm": true,
    "min_confidence": 0.75
  }'
```

**Response:**
```json
{
  "success": true,
  "kg_name": "material_kg",
  "total_relationships": 25,
  "nl_relationships_added": 2,
  "auto_detected_relationships": 23
}
```

✅ **KG updated**, ❌ **no rules yet**

---

### Level 3: Generate Reconciliation Rules

```
POST /v1/reconciliation/generate
```

**What it does:**
- ✅ Reads the knowledge graph (with all relationships)
- ✅ **Generates reconciliation rulesets**
- ✅ Saves rules to JSON file

**When to use:**
- After you've built up the KG with all relationships
- Ready to create executable reconciliation rules

**Example:**
```bash
curl -X POST http://localhost:8000/v1/reconciliation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "material_kg",
    "schema_names": ["hana-material-schema", "ops-excel-schema"],
    "use_llm_enhancement": true,
    "min_confidence": 0.75,
    "field_preferences": [...]
  }'
```

**Response:**
```json
{
  "success": true,
  "ruleset_id": "RECON_ABC123",
  "rules_count": 6,
  "rules": [...]
}
```

✅ **Rules created!**

---

## Complete Workflow: Natural Language → Rules

### Python Script (Recommended)

```python
import requests
import json

BASE_URL = "http://localhost:8000/v1"

def create_rules_from_natural_language():
    """
    Complete workflow: Natural Language → KG → Rules → SQL
    """

    # ========================================================================
    # STEP 1: Integrate Natural Language to Knowledge Graph
    # ========================================================================
    print("Step 1: Integrating relationships to KG...")

    integrate_response = requests.post(
        f"{BASE_URL}/kg/integrate-nl-relationships",
        json={
            "kg_name": "four_way_material_kg",
            "schemas": [
                "hana-material-schema",
                "ops-excel-schema",
                "rbp-gpu-schema",
                "sku-lifnr-schema"
            ],
            "nl_definitions": [
                "hana_material_master.MATERIAL matches brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU",
                "hana_material_master.MATERIAL matches brz_lnd_RBP_GPU.Material",
                "brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU matches brz_lnd_RBP_GPU.Material",
                "brz_lnd_RBP_GPU.Material matches brz_lnd_SKU_LIFNR_Excel.Material"
            ],
            "use_llm": True,
            "min_confidence": 0.75
        }
    )

    if integrate_response.status_code != 200:
        print(f"❌ KG integration failed: {integrate_response.text}")
        return None

    kg_data = integrate_response.json()
    print(f"✅ KG Integration complete!")
    print(f"   Total relationships: {kg_data['total_relationships']}")
    print(f"   NL relationships added: {kg_data['nl_relationships_added']}")

    # ========================================================================
    # STEP 2: Generate Reconciliation Rules from KG
    # ========================================================================
    print("\nStep 2: Generating reconciliation rules...")

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
            "min_confidence": 0.75,
            "field_preferences": [
                {
                    "table_name": "hana_material_master",
                    "priority_fields": ["MATERIAL"],
                    "field_hints": {
                        "MATERIAL": "PLANNING_SKU",
                        "MATERIAL": "Material"
                    }
                },
                {
                    "table_name": "brz_lnd_OPS_EXCEL_GPU",
                    "priority_fields": ["PLANNING_SKU", "Active_Inactive"],
                    "field_hints": {
                        "PLANNING_SKU": "MATERIAL",
                        "PLANNING_SKU": "Material"
                    },
                    "filter_hints": {
                        "Active_Inactive": "Active"
                    }
                },
                {
                    "table_name": "brz_lnd_RBP_GPU",
                    "priority_fields": ["Material"],
                    "field_hints": {
                        "Material": "PLANNING_SKU",
                        "Material": "MATERIAL"
                    }
                },
                {
                    "table_name": "brz_lnd_SKU_LIFNR_Excel",
                    "priority_fields": ["Material"],
                    "field_hints": {
                        "Material": "MATERIAL",
                        "Material": "PLANNING_SKU"
                    }
                }
            ]
        }
    )

    if rules_response.status_code != 200:
        print(f"❌ Rule generation failed: {rules_response.text}")
        return None

    rules_data = rules_response.json()
    print(f"✅ Rules generation complete!")
    print(f"   Ruleset ID: {rules_data['ruleset_id']}")
    print(f"   Rules count: {rules_data['rules_count']}")

    # ========================================================================
    # STEP 3: Export to SQL (Optional)
    # ========================================================================
    print("\nStep 3: Exporting to SQL...")

    ruleset_id = rules_data['ruleset_id']
    sql_response = requests.get(
        f"{BASE_URL}/reconciliation/rulesets/{ruleset_id}/export/sql"
    )

    if sql_response.status_code == 200:
        sql_data = sql_response.json()

        # Save to file
        filename = f"reconciliation_rules_{ruleset_id}.sql"
        with open(filename, 'w') as f:
            f.write(sql_data['sql'])

        print(f"✅ SQL export complete!")
        print(f"   Saved to: {filename}")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("🎉 COMPLETE WORKFLOW FINISHED!")
    print("=" * 80)
    print(f"\nRuleset ID: {rules_data['ruleset_id']}")
    print(f"Rules Created: {rules_data['rules_count']}")
    print(f"\nNext Steps:")
    print(f"  1. Review the SQL: reconciliation_rules_{ruleset_id}.sql")
    print(f"  2. Execute: POST /v1/reconciliation/execute")
    print(f"  3. View results: GET /v1/reconciliation/results")

    return rules_data

if __name__ == "__main__":
    create_rules_from_natural_language()
```

---

## Reusable Helper Function

Create a utility function to streamline the workflow:

```python
def natural_language_to_rules(
    kg_name: str,
    schemas: list[str],
    definitions: list[str],
    field_preferences: list[dict] = None,
    use_llm: bool = True,
    min_confidence: float = 0.75
) -> dict:
    """
    One-shot function: Natural Language → KG → Rules

    Args:
        kg_name: Name of the knowledge graph
        schemas: List of schema names
        definitions: Natural language definitions
        field_preferences: Optional field hints
        use_llm: Use LLM for parsing
        min_confidence: Minimum confidence threshold

    Returns:
        dict with ruleset_id, rules_count, and full response
    """
    import requests

    BASE_URL = "http://localhost:8000/v1"

    # Step 1: Integrate to KG
    kg_response = requests.post(
        f"{BASE_URL}/kg/integrate-nl-relationships",
        json={
            "kg_name": kg_name,
            "schemas": schemas,
            "nl_definitions": definitions,
            "use_llm": use_llm,
            "min_confidence": min_confidence
        }
    )

    if kg_response.status_code != 200:
        raise Exception(f"KG integration failed: {kg_response.text}")

    # Step 2: Generate rules
    rules_payload = {
        "kg_name": kg_name,
        "schema_names": schemas,
        "use_llm_enhancement": use_llm,
        "min_confidence": min_confidence
    }

    if field_preferences:
        rules_payload["field_preferences"] = field_preferences

    rules_response = requests.post(
        f"{BASE_URL}/reconciliation/generate",
        json=rules_payload
    )

    if rules_response.status_code != 200:
        raise Exception(f"Rule generation failed: {rules_response.text}")

    return rules_response.json()

# Usage
result = natural_language_to_rules(
    kg_name="material_reconciliation",
    schemas=["hana-material-schema", "ops-excel-schema"],
    definitions=[
        "hana_material_master.MATERIAL matches brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU"
    ],
    field_preferences=[
        {
            "table_name": "hana_material_master",
            "priority_fields": ["MATERIAL"],
            "field_hints": {"MATERIAL": "PLANNING_SKU"}
        }
    ]
)

print(f"Ruleset created: {result['ruleset_id']}")
```

---

## Why This Design?

The separation into 3 levels provides several benefits:

### 1. Flexibility
- Preview relationships before committing
- Validate syntax without side effects
- Test different confidence thresholds

### 2. Performance
- Rule generation is expensive (LLM calls)
- Don't regenerate rules every time relationships change
- Build up KG incrementally, generate rules once

### 3. Iteration
- Add relationships from multiple sources
- Combine auto-detected + custom relationships
- Refine KG before generating rules

### 4. Debugging
- See exactly what relationships are created
- Identify parsing errors early
- Validate before expensive operations

### 5. Reusability
- Same KG can generate different rulesets
- Different confidence thresholds
- Different field preferences

---

## Quick Reference

| Endpoint | Parses NL | Updates KG | Generates Rules |
|----------|-----------|------------|-----------------|
| `/kg/relationships/natural-language` | ✅ | ❌ | ❌ |
| `/kg/integrate-nl-relationships` | ✅ | ✅ | ❌ |
| `/reconciliation/generate` | ❌ | ❌ | ✅ |

**To get from NL to Rules:** Use endpoint 2 + endpoint 3

---

## Common Pitfalls

### ❌ Mistake 1: Using Level 1 expecting rules
```python
# This only parses, doesn't create rules!
response = requests.post("/v1/kg/relationships/natural-language", ...)
# ❌ No rules created
```

### ✅ Fix: Use Level 2 + Level 3
```python
# Step 1: Integrate
requests.post("/v1/kg/integrate-nl-relationships", ...)

# Step 2: Generate rules
requests.post("/v1/reconciliation/generate", ...)
# ✅ Rules created!
```

### ❌ Mistake 2: Generating rules before integrating
```python
# Generate rules from empty KG
requests.post("/v1/reconciliation/generate", ...)
# ❌ Few or no rules - KG is empty!
```

### ✅ Fix: Integrate first, then generate
```python
# Step 1: Build KG
requests.post("/v1/kg/integrate-nl-relationships", ...)

# Step 2: Generate from populated KG
requests.post("/v1/reconciliation/generate", ...)
# ✅ Rules based on all relationships
```

---

## Summary

**The Answer:** `/kg/relationships/natural-language` is designed for **preview only**.

**To create rules from natural language:**

1. Use `/kg/integrate-nl-relationships` to add relationships to KG
2. Use `/reconciliation/generate` to create rules from the KG
3. Optionally export SQL with `/reconciliation/rulesets/{id}/export/sql`

This design gives you flexibility, performance, and control over the entire workflow.

---

## Related Documentation

- [Natural Language Rules Examples](NATURAL_LANGUAGE_RULES_EXAMPLES.md)
- [Natural Language to SQL Workflow](NL_TO_SQL_WORKFLOW.md)
- [Reconciliation Execution Guide](RECONCILIATION_EXECUTION_GUIDE.md)
- [KPI Feature Guide](KPI_FEATURE_COMPLETE_GUIDE.md)
