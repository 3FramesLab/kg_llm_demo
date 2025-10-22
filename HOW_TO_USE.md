# How to Use DQ-POC: A Practical Guide with Examples

## Table of Contents
1. [Quick Start](#quick-start)
2. [Installation & Setup](#installation--setup)
3. [Basic Usage Examples](#basic-usage-examples)
4. [Advanced Workflows](#advanced-workflows)
5. [API Examples](#api-examples)
6. [Common Use Cases](#common-use-cases)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

Get started with DQ-POC in 3 simple steps:

```bash
# 1. Clone and navigate to the project
cd dq-poc

# 2. Set up environment
cp .env.example .env
# Edit .env with your OpenAI API key (optional but recommended)

# 3. Start with Docker (recommended)
docker-compose up -d

# OR start locally
python -m kg_builder.main
```

Access the interactive API documentation at: **http://localhost:8000/docs**

---

## Installation & Setup

### Prerequisites

- Python 3.9+
- Docker & Docker Compose (for containerized deployment)
- OpenAI API key (optional, for LLM-powered features)
- JDBC drivers (optional, for database validation/execution)

### Method 1: Docker Deployment (Recommended)

```bash
# 1. Start all services
docker-compose up -d

# 2. Wait for services to be ready (30-40 seconds)
docker-compose ps

# 3. Check health
curl http://localhost:8000/api/v1/health

# Expected response:
# {
#   "status": "healthy",
#   "falkordb_connected": true,
#   "graphiti_available": true,
#   "llm_enabled": true
# }
```

### Method 2: Local Development

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env file with your settings

# 4. Start the application
python -m kg_builder.main

# Server starts at http://localhost:8000
```

### Configuration

Edit `.env` file with your settings:

```env
# Essential Configuration
OPENAI_API_KEY=sk-your-key-here              # Required for LLM features
FALKORDB_HOST=localhost                       # Use 'falkordb' in Docker
FALKORDB_PORT=6379

# Optional: Database Connections (for rule validation/execution)
SOURCE_DB_TYPE=oracle
SOURCE_DB_HOST=localhost
SOURCE_DB_PORT=1521
SOURCE_DB_USERNAME=your_username
SOURCE_DB_PASSWORD=your_password

TARGET_DB_TYPE=oracle
TARGET_DB_HOST=localhost
TARGET_DB_PORT=1521
TARGET_DB_USERNAME=your_username
TARGET_DB_PASSWORD=your_password
```

---

## Basic Usage Examples

### Example 1: List Available Schemas

```bash
curl http://localhost:8000/api/v1/schemas
```

**Response:**
```json
{
  "schemas": [
    "orderMgmt-catalog",
    "qinspect-designcode"
  ],
  "count": 2
}
```

### Example 2: Generate a Simple Knowledge Graph

**Scenario:** Create a knowledge graph from a single schema.

```bash
curl -X POST http://localhost:8000/api/v1/kg/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_name": "orderMgmt-catalog",
    "kg_name": "orders_kg",
    "backends": ["graphiti"]
  }'
```

**Response:**
```json
{
  "kg_name": "orders_kg",
  "status": "created",
  "node_count": 25,
  "relationship_count": 18,
  "backends": ["graphiti"],
  "creation_time": "2024-10-22T10:30:00Z"
}
```

### Example 3: View Knowledge Graph Entities

```bash
curl http://localhost:8000/api/v1/kg/orders_kg/entities
```

**Response:**
```json
{
  "entities": [
    {
      "id": "table_catalog",
      "label": "catalog",
      "type": "table",
      "properties": {
        "column_count": 12,
        "has_primary_key": true
      }
    },
    {
      "id": "column_product_id",
      "label": "product_id",
      "type": "important_column",
      "source_table": "catalog"
    }
  ],
  "count": 25
}
```

### Example 4: View Knowledge Graph Relationships

```bash
curl http://localhost:8000/api/v1/kg/orders_kg/relationships
```

**Response:**
```json
{
  "relationships": [
    {
      "source_id": "column_product_id",
      "target_id": "table_catalog",
      "relationship_type": "BELONGS_TO",
      "properties": {
        "column_type": "NUMBER",
        "is_primary_key": true
      }
    },
    {
      "source_id": "table_orders",
      "target_id": "table_catalog",
      "relationship_type": "FOREIGN_KEY",
      "source_column": "product_id",
      "target_column": "product_id"
    }
  ],
  "count": 18
}
```

### Example 5: Export Knowledge Graph

```bash
# Export as JSON
curl http://localhost:8000/api/v1/kg/orders_kg/export > orders_kg.json

# View the exported graph
cat orders_kg.json
```

---

## Advanced Workflows

### Workflow 1: Multi-Schema Reconciliation with LLM

**Scenario:** You have two different database schemas (order management and quality inspection) and want to find matching rules between them.

#### Step 1: Generate Merged Knowledge Graph

```bash
curl -X POST http://localhost:8000/api/v1/kg/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_names": ["orderMgmt-catalog", "qinspect-designcode"],
    "kg_name": "unified_kg",
    "use_llm_enhancement": true,
    "backends": ["falkordb", "graphiti"]
  }'
```

**What happens:**
- System parses both schemas
- Extracts entities (tables, columns)
- LLM analyzes schemas for semantic relationships
- Creates merged knowledge graph
- Stores in both FalkorDB and Graphiti

**Response:**
```json
{
  "kg_name": "unified_kg",
  "status": "created",
  "node_count": 58,
  "relationship_count": 47,
  "llm_enhanced": true,
  "schemas_processed": 2,
  "backends": ["falkordb", "graphiti"]
}
```

#### Step 2: Generate Reconciliation Rules

```bash
curl -X POST http://localhost:8000/api/v1/reconciliation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_names": ["orderMgmt-catalog", "qinspect-designcode"],
    "kg_name": "unified_kg",
    "use_llm_enhancement": true,
    "min_confidence": 0.7
  }'
```

**What happens:**
- System queries the knowledge graph
- Identifies potential matching columns
- LLM enhances with semantic understanding
- Generates rules with confidence scores
- Filters rules below 0.7 confidence threshold

**Response:**
```json
{
  "ruleset_id": "RECON_20241022_103045",
  "rule_count": 12,
  "rules": [
    {
      "rule_id": "RULE_001",
      "rule_name": "catalog_product_to_designcode_item",
      "source_schema": "orderMgmt-catalog",
      "source_table": "catalog",
      "source_columns": ["product_id"],
      "target_schema": "qinspect-designcode",
      "target_table": "designcode",
      "target_columns": ["item_id"],
      "match_type": "semantic",
      "confidence_score": 0.85,
      "reasoning": "LLM matched product_id to item_id based on semantic similarity and context",
      "llm_generated": true
    },
    {
      "rule_id": "RULE_002",
      "rule_name": "catalog_vendor_to_vendor_master",
      "source_schema": "orderMgmt-catalog",
      "source_table": "catalog",
      "source_columns": ["vendor_uid"],
      "target_schema": "qinspect-designcode",
      "target_table": "vendor_master",
      "target_columns": ["vendor_id"],
      "match_type": "exact",
      "confidence_score": 0.92,
      "reasoning": "Direct foreign key relationship detected"
    }
  ],
  "created_at": "2024-10-22T10:30:45Z"
}
```

#### Step 3: Export Rules as SQL

```bash
curl http://localhost:8000/api/v1/reconciliation/rulesets/RECON_20241022_103045/export/sql
```

**Response:**
```sql
-- Reconciliation Ruleset: RECON_20241022_103045
-- Generated: 2024-10-22T10:30:45Z
-- Total Rules: 12

-- RULE_001: catalog_product_to_designcode_item
-- Match Type: semantic | Confidence: 0.85
-- Description: LLM matched product_id to item_id based on semantic similarity

-- Matched Records (exist in both systems)
SELECT
  s.product_id as source_product_id,
  t.item_id as target_item_id
FROM orderMgmt_catalog.catalog s
INNER JOIN qinspect_designcode.designcode t
  ON s.product_id = t.item_id;

-- Unmatched Source Records (only in source)
SELECT s.product_id
FROM orderMgmt_catalog.catalog s
LEFT JOIN qinspect_designcode.designcode t
  ON s.product_id = t.item_id
WHERE t.item_id IS NULL;

-- Unmatched Target Records (only in target)
SELECT t.item_id
FROM qinspect_designcode.designcode t
LEFT JOIN orderMgmt_catalog.catalog s
  ON s.product_id = t.item_id
WHERE s.product_id IS NULL;

-- ... (additional rules follow)
```

### Workflow 2: Adding Natural Language Relationships

**Scenario:** The auto-generated rules missed some important business relationships. You want to define them explicitly.

#### Step 1: Define Relationships in Natural Language

```bash
curl -X POST http://localhost:8000/api/v1/kg/relationships/natural-language \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "unified_kg",
    "schemas": ["orderMgmt-catalog", "qinspect-designcode"],
    "definitions": [
      "Products in catalog are inspected in quality inspection",
      "Vendors supply products to the catalog",
      "Inspection results reference design codes",
      "Orders contain products from the catalog"
    ],
    "use_llm": true,
    "min_confidence": 0.7
  }'
```

**What happens:**
- System parses each natural language definition
- LLM extracts entities and relationships
- Validates against actual schema structure
- Assigns confidence scores
- Returns parsed relationships

**Response:**
```json
{
  "parsed_count": 4,
  "valid_count": 3,
  "invalid_count": 1,
  "relationships": [
    {
      "definition": "Products in catalog are inspected in quality inspection",
      "parsed": {
        "source_entity": "catalog.product_id",
        "target_entity": "inspection.product_ref",
        "relationship_type": "INSPECTED_IN",
        "confidence": 0.88
      },
      "status": "valid"
    },
    {
      "definition": "Vendors supply products to the catalog",
      "parsed": {
        "source_entity": "vendor_master.vendor_id",
        "target_entity": "catalog.vendor_uid",
        "relationship_type": "SUPPLIES",
        "confidence": 0.92
      },
      "status": "valid"
    },
    {
      "definition": "Orders contain products from the catalog",
      "parsed": null,
      "status": "invalid",
      "error": "Entity 'Orders' not found in provided schemas"
    }
  ]
}
```

#### Step 2: Integrate NL Relationships into Knowledge Graph

```bash
curl -X POST http://localhost:8000/api/v1/kg/integrate-nl-relationships \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "unified_kg",
    "nl_relationships": [
      {
        "source_entity": "catalog.product_id",
        "target_entity": "inspection.product_ref",
        "relationship_type": "INSPECTED_IN",
        "confidence": 0.88
      },
      {
        "source_entity": "vendor_master.vendor_id",
        "target_entity": "catalog.vendor_uid",
        "relationship_type": "SUPPLIES",
        "confidence": 0.92
      }
    ],
    "backends": ["falkordb", "graphiti"]
  }'
```

#### Step 3: Regenerate Rules with Enhanced Knowledge Graph

```bash
# Now regenerate rules with the enhanced KG
curl -X POST http://localhost:8000/api/v1/reconciliation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_names": ["orderMgmt-catalog", "qinspect-designcode"],
    "kg_name": "unified_kg",
    "use_llm_enhancement": true,
    "min_confidence": 0.7
  }'
```

**Result:** New ruleset includes additional rules based on the NL relationships you defined!

### Workflow 3: Validate Rules Against Real Data

**Scenario:** Before executing rules, you want to verify they work correctly with actual database data.

#### Step 1: Select a Rule to Validate

```bash
# First, get the ruleset
curl http://localhost:8000/api/v1/reconciliation/rulesets/RECON_20241022_103045
```

#### Step 2: Validate Specific Rule

```bash
curl -X POST http://localhost:8000/api/v1/reconciliation/validate \
  -H "Content-Type: application/json" \
  -d '{
    "rule": {
      "rule_id": "RULE_001",
      "source_schema": "orderMgmt-catalog",
      "source_table": "catalog",
      "source_columns": ["product_id"],
      "target_schema": "qinspect-designcode",
      "target_table": "designcode",
      "target_columns": ["item_id"]
    },
    "sample_size": 100,
    "source_db_config": {
      "db_type": "oracle",
      "host": "source-db.company.com",
      "port": 1521,
      "database": "ORCL",
      "username": "user1",
      "password": "pass1",
      "service_name": "ORCL"
    },
    "target_db_config": {
      "db_type": "oracle",
      "host": "target-db.company.com",
      "port": 1521,
      "database": "ORCL",
      "username": "user2",
      "password": "pass2"
    }
  }'
```

**What happens:**
- System connects to both databases via JDBC
- Verifies tables and columns exist
- Samples 100 records from each table
- Tests the matching logic
- Calculates match rate and identifies issues

**Response:**
```json
{
  "rule_id": "RULE_001",
  "validation_status": "VALID",
  "table_exists_source": true,
  "table_exists_target": true,
  "columns_exist_source": true,
  "columns_exist_target": true,
  "data_type_compatible": true,
  "sample_match_rate": 0.73,
  "samples_tested": 100,
  "matches_found": 73,
  "estimated_performance": "good",
  "issues": [],
  "warnings": [
    "27% of source records had no match in target database"
  ],
  "recommendations": [
    "Consider adding data quality checks for unmatched records",
    "Review transformation logic if match rate is lower than expected"
  ]
}
```

### Workflow 4: Execute Reconciliation

**Scenario A: SQL Export Mode** (No database access from API)

```bash
curl -X POST http://localhost:8000/api/v1/reconciliation/execute \
  -H "Content-Type: application/json" \
  -d '{
    "ruleset_id": "RECON_20241022_103045",
    "limit": 1000,
    "export_sql": true
  }'
```

**Response:**
```json
{
  "mode": "sql_export",
  "ruleset_id": "RECON_20241022_103045",
  "sql_queries": {
    "RULE_001": {
      "matched_query": "SELECT s.product_id, t.item_id FROM ...",
      "unmatched_source_query": "SELECT s.product_id FROM ... WHERE t.item_id IS NULL",
      "unmatched_target_query": "SELECT t.item_id FROM ... WHERE s.product_id IS NULL"
    }
  },
  "instructions": "Execute these SQL queries manually in your database client"
}
```

**Scenario B: Direct Execution Mode** (With database credentials)

```bash
curl -X POST http://localhost:8000/api/v1/reconciliation/execute \
  -H "Content-Type: application/json" \
  -d '{
    "ruleset_id": "RECON_20241022_103045",
    "limit": 1000,
    "source_db_config": {
      "db_type": "oracle",
      "host": "source-db.company.com",
      "port": 1521,
      "database": "ORCL",
      "username": "user1",
      "password": "pass1"
    },
    "target_db_config": {
      "db_type": "oracle",
      "host": "target-db.company.com",
      "port": 1521,
      "database": "ORCL",
      "username": "user2",
      "password": "pass2"
    }
  }'
```

**Response:**
```json
{
  "mode": "direct_execution",
  "ruleset_id": "RECON_20241022_103045",
  "execution_time": "2024-10-22T10:45:00Z",
  "results": {
    "RULE_001": {
      "matched_count": 1247,
      "unmatched_source_count": 53,
      "unmatched_target_count": 28,
      "matched_records": [
        {"source_product_id": "P001", "target_item_id": "P001"},
        {"source_product_id": "P002", "target_item_id": "P002"}
      ],
      "unmatched_source_records": [
        {"source_product_id": "P999"},
        {"source_product_id": "P888"}
      ],
      "unmatched_target_records": [
        {"target_item_id": "I777"}
      ]
    },
    "RULE_002": {
      "matched_count": 342,
      "unmatched_source_count": 12,
      "unmatched_target_count": 5
    }
  },
  "summary": {
    "total_rules_executed": 12,
    "total_matched": 8934,
    "total_unmatched_source": 412,
    "total_unmatched_target": 287,
    "overall_match_rate": 0.78
  }
}
```

---

## API Examples

### Python Examples

#### Example 1: Generate KG and Rules

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Step 1: Generate Knowledge Graph
response = requests.post(
    f"{BASE_URL}/kg/generate",
    json={
        "schema_names": ["orderMgmt-catalog", "qinspect-designcode"],
        "kg_name": "my_reconciliation_kg",
        "use_llm_enhancement": True,
        "backends": ["falkordb", "graphiti"]
    }
)
kg_result = response.json()
print(f"KG Created: {kg_result['kg_name']}")
print(f"Nodes: {kg_result['node_count']}, Relationships: {kg_result['relationship_count']}")

# Step 2: Generate Reconciliation Rules
response = requests.post(
    f"{BASE_URL}/reconciliation/generate",
    json={
        "schema_names": ["orderMgmt-catalog", "qinspect-designcode"],
        "kg_name": "my_reconciliation_kg",
        "use_llm_enhancement": True,
        "min_confidence": 0.7
    }
)
rules_result = response.json()
ruleset_id = rules_result['ruleset_id']
print(f"\nRuleset Created: {ruleset_id}")
print(f"Total Rules: {rules_result['rule_count']}")

# Step 3: Export SQL
response = requests.get(
    f"{BASE_URL}/reconciliation/rulesets/{ruleset_id}/export/sql"
)
sql_queries = response.text
with open("reconciliation_queries.sql", "w") as f:
    f.write(sql_queries)
print("\nSQL queries exported to reconciliation_queries.sql")
```

#### Example 2: Add Natural Language Relationships

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Define business relationships in plain English
nl_definitions = [
    "Products in catalog are inspected in quality inspection",
    "Vendors supply products to the catalog",
    "Inspection results reference design codes from designcode table"
]

response = requests.post(
    f"{BASE_URL}/kg/relationships/natural-language",
    json={
        "kg_name": "my_reconciliation_kg",
        "schemas": ["orderMgmt-catalog", "qinspect-designcode"],
        "definitions": nl_definitions,
        "use_llm": True,
        "min_confidence": 0.7
    }
)

result = response.json()
print(f"Parsed {result['parsed_count']} relationships")
print(f"Valid: {result['valid_count']}, Invalid: {result['invalid_count']}")

for rel in result['relationships']:
    if rel['status'] == 'valid':
        print(f"\n✓ {rel['definition']}")
        print(f"  Confidence: {rel['parsed']['confidence']}")
    else:
        print(f"\n✗ {rel['definition']}")
        print(f"  Error: {rel['error']}")
```

#### Example 3: Execute Reconciliation with Results

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Execute reconciliation
response = requests.post(
    f"{BASE_URL}/reconciliation/execute",
    json={
        "ruleset_id": "RECON_20241022_103045",
        "limit": 1000,
        "source_db_config": {
            "db_type": "oracle",
            "host": "source-db.company.com",
            "port": 1521,
            "database": "ORCL",
            "username": "user1",
            "password": "pass1"
        },
        "target_db_config": {
            "db_type": "oracle",
            "host": "target-db.company.com",
            "port": 1521,
            "database": "ORCL",
            "username": "user2",
            "password": "pass2"
        }
    }
)

result = response.json()

# Analyze results
print(f"Reconciliation Summary")
print(f"=" * 50)
print(f"Total Matched: {result['summary']['total_matched']}")
print(f"Unmatched Source: {result['summary']['total_unmatched_source']}")
print(f"Unmatched Target: {result['summary']['total_unmatched_target']}")
print(f"Match Rate: {result['summary']['overall_match_rate'] * 100:.2f}%")

# Save detailed results
with open("reconciliation_results.json", "w") as f:
    json.dump(result, f, indent=2)
print("\nDetailed results saved to reconciliation_results.json")
```

### JavaScript/Node.js Examples

#### Example: Complete Workflow

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api/v1';

async function runReconciliation() {
  try {
    // Step 1: Generate KG
    console.log('Generating Knowledge Graph...');
    const kgResponse = await axios.post(`${BASE_URL}/kg/generate`, {
      schema_names: ['orderMgmt-catalog', 'qinspect-designcode'],
      kg_name: 'unified_kg',
      use_llm_enhancement: true,
      backends: ['falkordb', 'graphiti']
    });
    console.log(`✓ KG Created: ${kgResponse.data.kg_name}`);
    console.log(`  Nodes: ${kgResponse.data.node_count}, Relationships: ${kgResponse.data.relationship_count}`);

    // Step 2: Generate Rules
    console.log('\nGenerating Reconciliation Rules...');
    const rulesResponse = await axios.post(`${BASE_URL}/reconciliation/generate`, {
      schema_names: ['orderMgmt-catalog', 'qinspect-designcode'],
      kg_name: 'unified_kg',
      use_llm_enhancement: true,
      min_confidence: 0.7
    });
    const rulesetId = rulesResponse.data.ruleset_id;
    console.log(`✓ Ruleset Created: ${rulesetId}`);
    console.log(`  Total Rules: ${rulesResponse.data.rule_count}`);

    // Step 3: Export SQL
    console.log('\nExporting SQL Queries...');
    const sqlResponse = await axios.get(
      `${BASE_URL}/reconciliation/rulesets/${rulesetId}/export/sql`
    );
    require('fs').writeFileSync('queries.sql', sqlResponse.data);
    console.log('✓ SQL exported to queries.sql');

  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

runReconciliation();
```

---

## Common Use Cases

### Use Case 1: Data Migration Validation

**Problem:** You're migrating data from an old system to a new one and need to verify completeness.

**Solution:**
1. Export schemas from both systems as JSON
2. Place in `schemas/` folder
3. Generate merged KG with LLM enhancement
4. Generate reconciliation rules
5. Execute rules to find:
   - Records successfully migrated (matched)
   - Records missing in target (unmatched source)
   - Extra records in target (unmatched target)

### Use Case 2: System Integration Testing

**Problem:** Two systems need to integrate, but use different database schemas.

**Solution:**
1. Create KG from both schemas
2. Define integration points using natural language
3. Generate reconciliation rules
4. Validate rules against test data
5. Use rules to identify data synchronization issues

### Use Case 3: Data Quality Auditing

**Problem:** Need to audit data consistency across multiple databases.

**Solution:**
1. Generate KG from all database schemas
2. Use LLM to identify semantic relationships
3. Generate comprehensive reconciliation rules
4. Execute rules periodically
5. Monitor unmatched records as data quality metrics

### Use Case 4: Master Data Management (MDM)

**Problem:** Multiple systems maintain customer/product data independently.

**Solution:**
1. Create unified KG from all system schemas
2. Define master data relationships in natural language
3. Generate rules to identify duplicates and inconsistencies
4. Execute rules to build master data registry

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Schema file not found"

**Error:**
```json
{
  "error": "Schema file not found: myschema"
}
```

**Solution:**
- Ensure JSON file exists in `schemas/` directory
- Use schema name WITHOUT `.json` extension
- Check file permissions

```bash
# Verify schema exists
ls schemas/
# Should show: orderMgmt-catalog.json

# Use in API without extension
curl http://localhost:8000/api/v1/schemas
```

#### Issue 2: "FalkorDB connection failed"

**Error:**
```json
{
  "error": "Failed to connect to FalkorDB"
}
```

**Solution:**
- Check if FalkorDB container is running: `docker-compose ps`
- Verify `FALKORDB_HOST` in `.env` (use `falkordb` for Docker, `localhost` for local)
- System automatically falls back to Graphiti/file storage

```bash
# Restart FalkorDB
docker-compose restart falkordb

# Check logs
docker-compose logs falkordb
```

#### Issue 3: "OpenAI API key not configured"

**Error:**
```json
{
  "llm_enabled": false,
  "warning": "OpenAI API key not configured"
}
```

**Solution:**
- Add `OPENAI_API_KEY` to `.env` file
- Restart the application
- LLM features will remain disabled but basic functionality works

```bash
# Edit .env
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# Restart
docker-compose restart app
# OR
python -m kg_builder.main
```

#### Issue 4: Low Confidence Rules

**Problem:** Generated rules have low confidence scores.

**Solutions:**
1. **Add Natural Language Relationships:**
   ```bash
   # Define explicit business relationships
   curl -X POST http://localhost:8000/api/v1/kg/relationships/natural-language \
     -d '{
       "definitions": ["Products are supplied by Vendors"],
       ...
     }'
   ```

2. **Lower Confidence Threshold:**
   ```bash
   # Accept rules with lower confidence
   curl -X POST http://localhost:8000/api/v1/reconciliation/generate \
     -d '{
       "min_confidence": 0.5  # Default is 0.7
     }'
   ```

3. **Improve Schema Metadata:**
   - Use meaningful table/column names
   - Add descriptions in JSON schema
   - Define explicit foreign keys

#### Issue 5: Database Connection Timeout

**Error:**
```json
{
  "error": "Database connection timeout"
}
```

**Solution:**
- Verify database is accessible from your network
- Check firewall rules
- Test connection manually:

```bash
# Test Oracle connection
sqlplus username/password@host:port/service_name

# Test with telnet
telnet database-host 1521
```

- Update `.env` with correct credentials
- For Docker: ensure network connectivity to external databases

#### Issue 6: JDBC Driver Not Found

**Error:**
```json
{
  "error": "JDBC driver not found for oracle"
}
```

**Solution:**
1. Download JDBC drivers
2. Place in `jdbc_drivers/` directory:
   ```
   jdbc_drivers/
   ├── ojdbc8.jar          # Oracle
   ├── mssql-jdbc.jar      # SQL Server
   ├── postgresql.jar      # PostgreSQL
   └── mysql-connector.jar # MySQL
   ```
3. Restart application

---

## Additional Resources

### Quick Start Script

Run the interactive quick start script:

```bash
python quick_start.py
```

This script guides you through:
- Selecting schemas
- Generating knowledge graphs
- Creating reconciliation rules
- Exporting results

### Demo Script

Run a complete reconciliation demo:

```bash
python demo_reconciliation_execution.py
```

### API Documentation

Interactive API documentation is available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Project Documentation

See the `docs/` folder for comprehensive documentation:
- `START_HERE.md` - Quick Docker setup
- `QUICKSTART.md` - Basic usage guide
- `API_EXAMPLES.md` - Detailed API examples
- `RECONCILIATION_USAGE_GUIDE.md` - Complete reconciliation guide
- `LLM_INTEGRATION.md` - LLM features guide

---

## Summary

DQ-POC provides a powerful, automated approach to data quality assessment and reconciliation. Key capabilities:

1. **Automated Rule Generation** - No manual mapping required
2. **LLM Intelligence** - Semantic understanding of data relationships
3. **Natural Language Interface** - Define relationships in plain English
4. **Multi-Database Support** - Works with Oracle, SQL Server, PostgreSQL, MySQL
5. **Flexible Execution** - SQL export or direct database execution
6. **Validation** - Test rules before execution

**Typical Workflow:**
```
Schemas → KG Generation → Rule Generation → Validation → Execution → Results
```

**Getting Help:**
- GitHub Issues: https://github.com/anthropics/claude-code/issues
- Documentation: `docs/` folder
- API Docs: http://localhost:8000/docs

**Happy Reconciling!**
