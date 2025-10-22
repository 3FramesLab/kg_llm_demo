# Reconciliation Rule Generation - Usage Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Workflow](#step-by-step-workflow)
4. [API Examples](#api-examples)
5. [Understanding the Output](#understanding-the-output)
6. [Advanced Usage](#advanced-usage)

---

## Quick Start

**5-Minute Setup:**

```bash
# 1. Start the API server
python -m uvicorn kg_builder.main:app --reload

# 2. In a new terminal, run the demo
python test_reconciliation_demo.py
```

The demo will automatically:
- Check available schemas
- Generate a knowledge graph
- Create reconciliation rules
- Display and export results

---

## Prerequisites

### 1. Ensure FalkorDB is Running

```bash
# Check if FalkorDB (Redis) is running
redis-cli ping
# Should return: PONG

# If not running, start it:
# Windows: Start Redis service
# Linux/Mac: redis-server
```

### 2. Set OpenAI API Key (for LLM features)

Edit `.env` file:
```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

### 3. Prepare Schema Files

Place your JSON schema files in the `schemas/` directory. Example schemas:
- `schemas/orderMgmt-catalog.json`
- `schemas/vendorDB-suppliers.json`

---

## Step-by-Step Workflow

### Step 1: Start the API Server

```bash
cd D:\learning\dq-poc
python -m uvicorn kg_builder.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 2: Verify Server is Running

Open your browser and go to:
- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Or use curl:
```bash
curl http://localhost:8000/health
```

### Step 3: List Available Schemas

```bash
curl http://localhost:8000/schemas
```

**Expected Response:**
```json
{
  "success": true,
  "schemas": [
    "orderMgmt-catalog",
    "vendorDB-suppliers",
    "qinspect-designcode"
  ],
  "count": 3
}
```

### Step 4: Generate a Knowledge Graph

First, create a unified knowledge graph from your schemas:

```bash
curl -X POST http://localhost:8000/kg/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_names": ["orderMgmt-catalog", "vendorDB-suppliers"],
    "kg_name": "my_unified_kg",
    "backends": ["falkordb"],
    "use_llm_enhancement": true
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "schemas_processed": ["orderMgmt-catalog", "vendorDB-suppliers"],
  "message": "Knowledge graph 'my_unified_kg' generated successfully from 2 schema(s)",
  "kg_name": "my_unified_kg",
  "nodes_count": 45,
  "relationships_count": 38,
  "backends_used": ["falkordb"],
  "generation_time_ms": 2456.7
}
```

### Step 5: Generate Reconciliation Rules

Now generate reconciliation rules from the knowledge graph:

```bash
curl -X POST http://localhost:8000/reconciliation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_names": ["orderMgmt-catalog", "vendorDB-suppliers"],
    "kg_name": "my_unified_kg",
    "use_llm_enhancement": true,
    "min_confidence": 0.7,
    "match_types": ["exact", "semantic"]
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "ruleset_id": "RECON_A1B2C3D4",
  "rules_count": 5,
  "generation_time_ms": 3245.8,
  "message": "Generated 5 reconciliation rules",
  "rules": [
    {
      "rule_id": "RULE_XYZ123",
      "rule_name": "Vendor_UID_Match",
      "source_schema": "orderMgmt-catalog",
      "source_table": "catalog",
      "source_columns": ["vendor_uid"],
      "target_schema": "vendorDB-suppliers",
      "target_table": "suppliers",
      "target_columns": ["supplier_id"],
      "match_type": "exact",
      "transformation": null,
      "confidence_score": 0.95,
      "reasoning": "Both fields represent unique vendor identifiers",
      "validation_status": "VALID",
      "llm_generated": true,
      "created_at": "2025-10-21T10:30:00",
      "metadata": {}
    }
  ]
}
```

### Step 6: View Generated Rules

```bash
# List all rulesets
curl http://localhost:8000/reconciliation/rulesets

# Get specific ruleset details
curl http://localhost:8000/reconciliation/rulesets/RECON_A1B2C3D4
```

### Step 7: Export Rules to SQL

```bash
curl http://localhost:8000/reconciliation/rulesets/RECON_A1B2C3D4/export/sql
```

**Expected Output:**
```sql
-- Reconciliation Rules: Reconciliation_my_unified_kg
-- Generated from KG: my_unified_kg
-- Schemas: orderMgmt-catalog, vendorDB-suppliers
-- Total Rules: 5

-- Rule 1: Vendor_UID_Match
-- Match Type: exact
-- Confidence: 0.95
-- Reasoning: Both fields represent unique vendor identifiers

SELECT s.vendor_uid, t.supplier_id
FROM orderMgmt-catalog.catalog s
JOIN vendorDB-suppliers.suppliers t
    ON s.vendor_uid = t.supplier_id;
```

---

## API Examples

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Generate Knowledge Graph
kg_response = requests.post(
    f"{BASE_URL}/kg/generate",
    json={
        "schema_names": ["orderMgmt-catalog", "vendorDB-suppliers"],
        "kg_name": "my_kg",
        "backends": ["falkordb"],
        "use_llm_enhancement": True
    }
)
print(kg_response.json())

# 2. Generate Reconciliation Rules
rules_response = requests.post(
    f"{BASE_URL}/reconciliation/generate",
    json={
        "schema_names": ["orderMgmt-catalog", "vendorDB-suppliers"],
        "kg_name": "my_kg",
        "use_llm_enhancement": True,
        "min_confidence": 0.7
    }
)
result = rules_response.json()
ruleset_id = result['ruleset_id']
print(f"Generated {result['rules_count']} rules")

# 3. View the Rules
for rule in result['rules']:
    print(f"\n{rule['rule_name']}:")
    print(f"  Confidence: {rule['confidence_score']}")
    print(f"  {rule['source_schema']}.{rule['source_table']} -> "
          f"{rule['target_schema']}.{rule['target_table']}")
    print(f"  Reasoning: {rule['reasoning']}")
```

### Using JavaScript/Node.js

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

async function generateRules() {
  // Generate KG
  const kgResponse = await axios.post(`${BASE_URL}/kg/generate`, {
    schema_names: ['orderMgmt-catalog', 'vendorDB-suppliers'],
    kg_name: 'my_kg',
    backends: ['falkordb'],
    use_llm_enhancement: true
  });

  console.log('KG Created:', kgResponse.data.kg_name);

  // Generate Rules
  const rulesResponse = await axios.post(`${BASE_URL}/reconciliation/generate`, {
    schema_names: ['orderMgmt-catalog', 'vendorDB-suppliers'],
    kg_name: 'my_kg',
    use_llm_enhancement: true,
    min_confidence: 0.7
  });

  const result = rulesResponse.data;
  console.log(`Generated ${result.rules_count} rules`);

  // Display rules
  result.rules.forEach(rule => {
    console.log(`\n${rule.rule_name}:`);
    console.log(`  Confidence: ${rule.confidence_score}`);
    console.log(`  Match: ${rule.source_table} -> ${rule.target_table}`);
  });
}

generateRules();
```

---

## Understanding the Output

### Rule Structure

Each generated rule contains:

| Field | Description | Example |
|-------|-------------|---------|
| `rule_id` | Unique identifier | `"RULE_A1B2C3"` |
| `rule_name` | Descriptive name | `"Vendor_UID_Match"` |
| `source_schema` | Source schema name | `"orderMgmt-catalog"` |
| `source_table` | Source table | `"catalog"` |
| `source_columns` | Source columns to match | `["vendor_uid"]` |
| `target_schema` | Target schema name | `"vendorDB-suppliers"` |
| `target_table` | Target table | `"suppliers"` |
| `target_columns` | Target columns to match | `["supplier_id"]` |
| `match_type` | Type of match | `"exact"`, `"fuzzy"`, `"semantic"` |
| `transformation` | SQL/Python transform | `"UPPER(TRIM(code))"` or `null` |
| `confidence_score` | Confidence (0.0-1.0) | `0.95` |
| `reasoning` | Why this rule exists | `"Both are vendor UIDs"` |
| `validation_status` | Validation status | `"VALID"`, `"LIKELY"`, `"UNCERTAIN"` |
| `llm_generated` | Generated by LLM? | `true` or `false` |

### Match Types

1. **EXACT**: Direct column-to-column match
   ```sql
   WHERE table1.id = table2.id
   ```

2. **FUZZY**: String similarity matching
   ```sql
   WHERE LEVENSHTEIN(table1.name, table2.name) < 3
   ```

3. **COMPOSITE**: Multiple columns together
   ```sql
   WHERE table1.first = table2.fname AND table1.last = table2.lname
   ```

4. **TRANSFORMATION**: Apply function before match
   ```sql
   WHERE UPPER(TRIM(table1.code)) = table2.code
   ```

5. **SEMANTIC**: LLM-inferred relationship
   - Complex business logic
   - Non-obvious connections

### Confidence Scores

| Score Range | Meaning | Action |
|-------------|---------|--------|
| 0.90 - 1.00 | Very High | Use directly in production |
| 0.80 - 0.89 | High | Review and approve |
| 0.70 - 0.79 | Medium | Test thoroughly before use |
| 0.60 - 0.69 | Low | Manual validation required |
| < 0.60 | Very Low | Filtered out by default |

---

## Advanced Usage

### Filter Rulesets by Schema

```bash
curl "http://localhost:8000/reconciliation/rulesets?schema_name=orderMgmt-catalog"
```

### Filter Rulesets by Knowledge Graph

```bash
curl "http://localhost:8000/reconciliation/rulesets?kg_name=my_unified_kg"
```

### Custom Confidence Threshold

Generate rules with higher confidence:

```bash
curl -X POST http://localhost:8000/reconciliation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_names": ["schema1", "schema2"],
    "kg_name": "my_kg",
    "use_llm_enhancement": true,
    "min_confidence": 0.85
  }'
```

### Disable LLM Enhancement (Pattern-Only)

For faster generation without LLM calls:

```bash
curl -X POST http://localhost:8000/reconciliation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_names": ["schema1", "schema2"],
    "kg_name": "my_kg",
    "use_llm_enhancement": false,
    "min_confidence": 0.7
  }'
```

### Delete a Ruleset

```bash
curl -X DELETE http://localhost:8000/reconciliation/rulesets/RECON_A1B2C3D4
```

---

## Using the Demo Script

The demo script provides a complete end-to-end workflow:

```bash
python test_reconciliation_demo.py
```

**What it does:**
1. ✅ Checks API health
2. ✅ Lists available schemas
3. ✅ Generates a knowledge graph from multiple schemas
4. ✅ Generates reconciliation rules
5. ✅ Displays all generated rules with details
6. ✅ Lists all saved rulesets
7. ✅ Shows detailed ruleset information
8. ✅ Exports rules to SQL format

**Expected Output:**
```
================================================================================
  RECONCILIATION RULE GENERATION DEMO
================================================================================

================================================================================
  1. Health Check
================================================================================

Status Code: 200
{'falkordb_connected': True,
 'graphiti_available': True,
 'status': 'healthy',
 'timestamp': '2025-10-21T10:30:00'}

================================================================================
  2. List Available Schemas
================================================================================

Status Code: 200
{'count': 3,
 'schemas': ['orderMgmt-catalog', 'vendorDB-suppliers', 'qinspect-designcode'],
 'success': True}

...

Generated 5 rules:

Rule 1: Vendor_UID_Match
  Match Type: exact
  Confidence: 0.95
  Source: orderMgmt-catalog.catalog (vendor_uid)
  Target: vendorDB-suppliers.suppliers (supplier_id)
  Reasoning: Both fields represent unique vendor identifiers
  LLM Generated: True
```

---

## Troubleshooting

### Issue: "FalkorDB not connected"

**Solution:**
```bash
# Start Redis/FalkorDB
redis-server

# Or check if it's running
redis-cli ping
```

### Issue: "LLM service not enabled"

**Solution:**
Set your OpenAI API key in `.env`:
```bash
OPENAI_API_KEY=sk-your-key-here
```

### Issue: "No schemas found"

**Solution:**
Add JSON schema files to the `schemas/` directory:
```bash
ls schemas/
# Should show: orderMgmt-catalog.json, vendorDB-suppliers.json, etc.
```

### Issue: "Schema not found"

**Solution:**
Check the exact schema filename (without .json extension):
```bash
# Wrong: "orderMgmt-catalog.json"
# Correct: "orderMgmt-catalog"
```

### Issue: Connection refused on port 8000

**Solution:**
```bash
# Check if server is running
curl http://localhost:8000/health

# If not, start it:
python -m uvicorn kg_builder.main:app --reload
```

---

## Next Steps

1. **Integrate with your ETL pipeline**: Use the generated rules in your data integration workflows
2. **Validate rules**: Test rules against sample data
3. **Execute reconciliation**: Implement the execution logic to match actual records
4. **Monitor and refine**: Track rule effectiveness and adjust confidence thresholds

---

## API Reference

Complete API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

All reconciliation endpoints:
- `POST /reconciliation/generate` - Generate rules
- `GET /reconciliation/rulesets` - List rulesets
- `GET /reconciliation/rulesets/{id}` - Get ruleset
- `DELETE /reconciliation/rulesets/{id}` - Delete ruleset
- `GET /reconciliation/rulesets/{id}/export/sql` - Export to SQL
- `POST /reconciliation/validate` - Validate rule
- `POST /reconciliation/execute` - Execute rules

---

**Questions?** Check the logs or API documentation for more details.
