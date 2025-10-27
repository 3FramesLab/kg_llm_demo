# Natural Language to SQL Generation Workflow

## Overview

The natural language rules creation is a **3-step process**. SQL is generated in **Step 3**, not immediately after parsing natural language.

```
Natural Language → Relationships → Reconciliation Rules → SQL Queries
     (Step 1)          (Step 2)            (Step 3)
     No SQL            No SQL           ✅ SQL HERE!
```

---

## Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STEP 1: Parse Natural Language                  │
│                                                                           │
│  Input: "Products are supplied by Vendors"                              │
│  ↓                                                                        │
│  POST /v1/kg/relationships/natural-language                              │
│  ↓                                                                        │
│  Output: Relationship Definitions (JSON)                                 │
│  {                                                                        │
│    "relationships": [{                                                   │
│      "source_entity": "Products",                                        │
│      "target_entity": "Vendors",                                         │
│      "relationship_type": "SUPPLIED_BY"                                  │
│    }]                                                                    │
│  }                                                                        │
│                                                                           │
│  ❌ No SQL generated yet                                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 2: Generate Reconciliation Rules                 │
│                                                                           │
│  Input: Knowledge Graph with Relationships                               │
│  ↓                                                                        │
│  POST /v1/reconciliation/generate                                        │
│  ↓                                                                        │
│  Output: Reconciliation Rules (JSON file)                                │
│  {                                                                        │
│    "ruleset_id": "RECON_ABC123",                                        │
│    "rules": [{                                                           │
│      "rule_id": "RULE_001",                                             │
│      "source_table": "products",                                         │
│      "target_table": "vendors",                                          │
│      "source_columns": ["product_id"],                                   │
│      "target_columns": ["vendor_product_id"],                            │
│      "match_type": "EXACT"                                               │
│    }]                                                                    │
│  }                                                                        │
│                                                                           │
│  Saved to: data/reconciliation_rules/RECON_ABC123.json                  │
│  ❌ Still no SQL                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         STEP 3: Export to SQL                            │
│                                                                           │
│  Input: Ruleset ID from Step 2                                           │
│  ↓                                                                        │
│  GET /v1/reconciliation/rulesets/{ruleset_id}/export/sql                │
│  ↓                                                                        │
│  Process:                                                                 │
│  1. Load ruleset from JSON                                               │
│  2. Load schema files to get column names                                │
│  3. Generate SQL with specific columns (not SELECT *)                    │
│  ↓                                                                        │
│  Output: SQL Queries (Text)                                              │
│                                                                           │
│  SELECT                                                                   │
│      'RULE_001' AS rule_id,                                              │
│      'Product_Vendor_Match' AS rule_name,                                │
│      0.95 AS confidence_score,                                           │
│      s.product_id,                                                       │
│      s.product_name,                                                     │
│      s.category,                                                         │
│      t.vendor_product_id,                                                │
│      t.vendor_name                                                       │
│  FROM orderMgmt.products s                                               │
│  INNER JOIN vendorDB.vendors t                                           │
│      ON s.product_id = t.vendor_product_id;                              │
│                                                                           │
│  ✅ SQL GENERATED HERE!                                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Code Example

### Complete Python Script

```python
import requests
import json

BASE_URL = "http://localhost:8000/v1"

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

# ============================================================================
# STEP 1: Parse Natural Language
# ============================================================================
print_section("STEP 1: Parse Natural Language → Create Relationships")

nl_payload = {
    "kg_name": "supply_chain_kg",
    "schemas": ["orderMgmt-catalog", "vendorDB-suppliers"],
    "definitions": [
        "Products are supplied by Vendors",
        "Orders contain Products with quantity",
        "Vendors have Locations"
    ],
    "use_llm": True,
    "min_confidence": 0.7
}

print("📤 Sending natural language definitions...")
nl_response = requests.post(
    f"{BASE_URL}/kg/relationships/natural-language",
    json=nl_payload
)

if nl_response.status_code == 200:
    nl_data = nl_response.json()
    print(f"✅ Success!")
    print(f"   Relationships parsed: {nl_data['parsed_count']}")
    print(f"   Processing time: {nl_data['processing_time_ms']:.2f}ms")

    print("\n📋 Parsed Relationships:")
    for rel in nl_data['relationships']:
        print(f"   - {rel['source_entity']}.{rel['source_column']} "
              f"→ {rel['target_entity']}.{rel['target_column']} "
              f"({rel['relationship_type']})")

    print("\n⚠️  Note: No SQL generated yet - only relationship definitions")
else:
    print(f"❌ Error: {nl_response.status_code}")
    print(nl_response.text)
    exit(1)

input("\nPress Enter to continue to Step 2...")

# ============================================================================
# STEP 2: Generate Reconciliation Rules
# ============================================================================
print_section("STEP 2: Generate Reconciliation Rules from Knowledge Graph")

rules_payload = {
    "kg_name": "supply_chain_kg",
    "schema_names": ["orderMgmt-catalog", "vendorDB-suppliers"],
    "use_llm_enhancement": True,
    "min_confidence": 0.7
}

print("📤 Generating reconciliation rules...")
rules_response = requests.post(
    f"{BASE_URL}/reconciliation/generate",
    json=rules_payload
)

if rules_response.status_code == 200:
    rules_data = rules_response.json()
    ruleset_id = rules_data['ruleset_id']

    print(f"✅ Success!")
    print(f"   Ruleset ID: {ruleset_id}")
    print(f"   Rules generated: {rules_data['rules_count']}")
    print(f"   Generation time: {rules_data['generation_time_ms']:.2f}ms")

    print("\n📋 Generated Rules:")
    for rule in rules_data['rules'][:3]:  # Show first 3
        print(f"   - {rule['rule_name']}")
        print(f"     {rule['source_schema']}.{rule['source_table']} "
              f"→ {rule['target_schema']}.{rule['target_table']}")
        print(f"     Match: {', '.join(rule['source_columns'])} "
              f"→ {', '.join(rule['target_columns'])}")
        print(f"     Confidence: {rule['confidence_score']:.2%}")

    if rules_data['rules_count'] > 3:
        print(f"   ... and {rules_data['rules_count'] - 3} more rules")

    print("\n⚠️  Note: Rules saved to JSON, but still no SQL generated")
    print(f"   Rules saved at: data/reconciliation_rules/{ruleset_id}.json")
else:
    print(f"❌ Error: {rules_response.status_code}")
    print(rules_response.text)
    exit(1)

input("\nPress Enter to continue to Step 3 (SQL Generation)...")

# ============================================================================
# STEP 3: Export to SQL
# ============================================================================
print_section("STEP 3: Export Reconciliation Rules to SQL")

print(f"📤 Generating SQL for ruleset: {ruleset_id}...")
sql_response = requests.get(
    f"{BASE_URL}/reconciliation/rulesets/{ruleset_id}/export/sql",
    params={"query_type": "all"}
)

if sql_response.status_code == 200:
    sql_data = sql_response.json()
    sql_queries = sql_data['sql']

    print("✅ Success! SQL Generated!")
    print(f"   Query type: {sql_data['query_type']}")
    print(f"   Ruleset: {sql_data['ruleset_id']}")

    # Count SQL statements
    matched_count = sql_queries.count("-- MATCHED RECORDS")
    unmatched_src = sql_queries.count("-- UNMATCHED SOURCE")
    unmatched_tgt = sql_queries.count("-- UNMATCHED TARGET")

    print(f"\n📊 SQL Statistics:")
    print(f"   Matched queries: {matched_count}")
    print(f"   Unmatched source queries: {unmatched_src}")
    print(f"   Unmatched target queries: {unmatched_tgt}")

    # Save to file
    output_file = f"generated_sql_{ruleset_id}.sql"
    with open(output_file, 'w') as f:
        f.write(sql_queries)

    print(f"\n💾 SQL saved to: {output_file}")

    print("\n" + "="*80)
    print("GENERATED SQL (First 50 lines):")
    print("="*80)
    lines = sql_queries.split('\n')
    for line in lines[:50]:
        print(line)

    if len(lines) > 50:
        print(f"\n... and {len(lines) - 50} more lines")

    print("\n" + "="*80)
    print("✅ SQL GENERATION COMPLETE!")
    print("="*80)

else:
    print(f"❌ Error: {sql_response.status_code}")
    print(sql_response.text)
    exit(1)

print("\n" + "="*80)
print("WORKFLOW COMPLETE!")
print("="*80)
print("\n📝 Summary:")
print("   Step 1: Natural Language → Relationships ✅")
print("   Step 2: Relationships → Reconciliation Rules ✅")
print("   Step 3: Rules → SQL Queries ✅")
print("\n🎉 You can now:")
print(f"   1. Review the SQL in: {output_file}")
print("   2. Run the SQL in your database")
print("   3. Or execute via API: POST /v1/reconciliation/execute")
```

---

## Alternative Workflows

### Option A: Skip SQL Export, Execute Directly

```python
# Steps 1-2 are the same...

# Step 3: Execute directly (SQL generated internally)
execute_response = requests.post(
    f"{BASE_URL}/reconciliation/execute",
    json={
        "ruleset_id": ruleset_id,
        "limit": 100,
        "source_db_config": {
            "db_type": "sqlserver",
            "host": "localhost",
            "port": 1433,
            "database": "SourceDB",
            "username": "user",
            "password": "pass"
        },
        "target_db_config": {
            "db_type": "sqlserver",
            "host": "localhost",
            "port": 1433,
            "database": "TargetDB",
            "username": "user",
            "password": "pass"
        }
    }
)

# SQL is generated and executed, results returned
results = execute_response.json()
print(f"Matched: {results['matched_count']}")
print(f"Unmatched Source: {results['unmatched_source_count']}")
```

### Option B: Generate SQL Multiple Times

```python
# Generate different SQL variations from same ruleset
sql_matched = requests.get(
    f"{BASE_URL}/reconciliation/rulesets/{ruleset_id}/export/sql",
    params={"query_type": "matched"}
).json()['sql']

sql_unmatched_source = requests.get(
    f"{BASE_URL}/reconciliation/rulesets/{ruleset_id}/export/sql",
    params={"query_type": "unmatched_source"}
).json()['sql']

sql_all = requests.get(
    f"{BASE_URL}/reconciliation/rulesets/{ruleset_id}/export/sql",
    params={"query_type": "all"}
).json()['sql']
```

---

## Key Takeaways

1. ✅ **Natural Language API** → Parses text, creates relationships (No SQL)
2. ✅ **Reconciliation Generate** → Creates rules from relationships (No SQL)
3. ✅ **Export SQL Endpoint** → **This is where SQL is generated!**
4. ✅ **SQL uses specific columns** from schema (not `SELECT *`)
5. ✅ **Rules are reusable** - Generate SQL multiple times with different options

---

## When is SQL Generated?

| Action | SQL Generated? | Why? |
|--------|----------------|------|
| Parse natural language | ❌ No | Only creates relationship metadata |
| Generate rules | ❌ No | Only creates rule definitions in JSON |
| **Export to SQL** | ✅ **Yes** | Reads rules + schemas → generates SQL |
| Execute rules | ✅ Yes (internal) | Generates and runs SQL, returns results |

---

## File Locations

After completing all 3 steps, you'll have:

```
dq-poc/
├── data/
│   └── reconciliation_rules/
│       └── RECON_ABC123.json           ← Step 2 creates this
├── generated_sql_RECON_ABC123.sql      ← Step 3 creates this
└── logs/
    └── sql_queries_RECON_ABC123.log    ← If SQL logging enabled
```

---

## Next Steps

After SQL is generated:

1. **Review the SQL** - Check the queries before running
2. **Run in Database** - Execute in SQL Developer, DBeaver, etc.
3. **Or Execute via API** - Let the system run it for you
4. **Create KPIs** - Monitor reconciliation quality over time

For more information:
- [Natural Language Examples](NATURAL_LANGUAGE_RULES_EXAMPLES.md)
- [Reconciliation Execution Guide](RECONCILIATION_EXECUTION_GUIDE.md)
- [KPI Feature Guide](KPI_FEATURE_COMPLETE_GUIDE.md)
