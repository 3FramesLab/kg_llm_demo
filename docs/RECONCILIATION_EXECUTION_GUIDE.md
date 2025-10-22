# Reconciliation Execution Guide

## Overview

This guide explains how to execute reconciliation rules to find matched and unmatched records between different data sources. The system supports **two execution modes**:

1. **SQL Export Mode** - Generate SQL queries to run manually
2. **Direct Execution Mode** - Automatically execute queries via JDBC

---

## Execution Modes Comparison

| Feature | SQL Export Mode | Direct Execution Mode |
|---------|----------------|----------------------|
| **Database Connection** | Not required | Required (JDBC) |
| **Prerequisites** | None | JayDeBeApi + JDBC drivers |
| **Use Case** | Review queries, manual execution | Automated execution |
| **Security** | No credentials needed | Requires DB credentials |
| **Flexibility** | Can customize SQL | Fixed SQL generation |
| **Best For** | Testing, auditing, custom workflows | Production automation |

---

## SQL Export Mode

### What It Does

- Generates SQL queries for matched and unmatched records
- Returns queries as text (no database execution)
- Allows you to review, customize, and run queries manually

### Usage

```bash
curl -X POST http://localhost:8000/reconciliation/execute \
  -H "Content-Type: application/json" \
  -d '{
    "ruleset_id": "RECON_ABC123",
    "limit": 100
  }'
```

**Note:** No `source_db_config` or `target_db_config` provided = SQL Export Mode

### Response

```json
{
  "success": true,
  "mode": "sql_export",
  "message": "SQL queries generated. Execute these queries manually in your database.",
  "sql": "-- Full SQL queries here",
  "matched_count": 0,
  "unmatched_source_count": 0,
  "unmatched_target_count": 0,
  "instructions": [
    "Copy the SQL queries from the 'sql' field",
    "Run them in your database client (SQL Developer, DBeaver, etc.)",
    "Review the matched and unmatched records",
    "For automated execution, provide source_db_config and target_db_config"
  ]
}
```

### Example Workflow

1. **Generate SQL queries**
```python
import requests

response = requests.post(
    "http://localhost:8000/reconciliation/execute",
    json={"ruleset_id": "RECON_ABC123", "limit": 100}
)

result = response.json()
sql = result['sql']
```

2. **Save to file**
```python
with open('reconciliation_queries.sql', 'w') as f:
    f.write(sql)
```

3. **Run in your database client**
   - Open SQL Developer, DBeaver, or similar
   - Connect to your database
   - Execute the queries
   - Review results

---

## Direct Execution Mode

### What It Does

- Connects to actual databases via JDBC
- Executes SQL queries automatically
- Returns matched and unmatched records as JSON

### Prerequisites

1. **Install JayDeBeApi**
```bash
pip install JayDeBeApi
```

2. **Download JDBC Drivers**

Create `jdbc_drivers/` directory and add:

| Database | Driver JAR | Download |
|----------|-----------|----------|
| Oracle | `ojdbc8.jar` or `ojdbc11.jar` | [Oracle JDBC Downloads](https://www.oracle.com/database/technologies/appdev/jdbc-downloads.html) |
| SQL Server | `mssql-jdbc-*.jar` | [Microsoft JDBC](https://docs.microsoft.com/en-us/sql/connect/jdbc/download-microsoft-jdbc-driver-for-sql-server) |
| PostgreSQL | `postgresql-*.jar` | [PostgreSQL JDBC](https://jdbc.postgresql.org/download.html) |
| MySQL | `mysql-connector-*.jar` | [MySQL Connector/J](https://dev.mysql.com/downloads/connector/j/) |

3. **Configure environment**

Update `.env`:
```bash
JDBC_DRIVERS_PATH=jdbc_drivers
```

### Usage

```bash
curl -X POST http://localhost:8000/reconciliation/execute \
  -H "Content-Type: application/json" \
  -d '{
    "ruleset_id": "RECON_ABC123",
    "limit": 100,
    "source_db_config": {
      "db_type": "oracle",
      "host": "localhost",
      "port": 1521,
      "database": "ORCL",
      "username": "user1",
      "password": "pass1"
    },
    "target_db_config": {
      "db_type": "oracle",
      "host": "localhost",
      "port": 1521,
      "database": "ORCL",
      "username": "user2",
      "password": "pass2"
    },
    "include_matched": true,
    "include_unmatched": true
  }'
```

### Response

```json
{
  "success": true,
  "matched_count": 87,
  "unmatched_source_count": 13,
  "unmatched_target_count": 5,
  "matched_records": [
    {
      "source_record": {...},
      "target_record": {...},
      "match_confidence": 0.95,
      "rule_used": "RULE_001",
      "rule_name": "Vendor_Match"
    }
  ],
  "unmatched_source": [
    {...}
  ],
  "unmatched_target": [
    {...}
  ],
  "execution_time_ms": 1234.56
}
```

---

## Generated SQL Queries

### Query Types

The system generates 4 types of SQL queries:

#### 1. Matched Records Query

Finds records that exist in both source and target:

```sql
-- MATCHED RECORDS: Records that exist in both source and target
SELECT
    'RULE_001' AS rule_id,
    'Vendor_Match' AS rule_name,
    0.95 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt.catalog s
INNER JOIN vendorDB.suppliers t
    ON s.vendor_uid = t.supplier_id;
```

#### 2. Unmatched Source Query

Finds records in source but NOT in target:

```sql
-- UNMATCHED SOURCE: Records in source but NOT in target
SELECT
    'RULE_001' AS rule_id,
    'Vendor_Match' AS rule_name,
    s.*
FROM orderMgmt.catalog s
WHERE NOT EXISTS (
    SELECT 1
    FROM vendorDB.suppliers t
    WHERE s.vendor_uid = t.supplier_id
);
```

#### 3. Unmatched Target Query

Finds records in target but NOT in source:

```sql
-- UNMATCHED TARGET: Records in target but NOT in source
SELECT
    'RULE_001' AS rule_id,
    'Vendor_Match' AS rule_name,
    t.*
FROM vendorDB.suppliers t
WHERE NOT EXISTS (
    SELECT 1
    FROM orderMgmt.catalog s
    WHERE s.vendor_uid = t.supplier_id
);
```

#### 4. Summary Statistics Query

Provides counts and statistics:

```sql
-- SUMMARY STATISTICS
SELECT
    'Vendor_Match' AS rule_name,
    (SELECT COUNT(*) FROM orderMgmt.catalog) AS total_source,
    (SELECT COUNT(*) FROM vendorDB.suppliers) AS total_target,
    (SELECT COUNT(*)
     FROM orderMgmt.catalog s
     INNER JOIN vendorDB.suppliers t
         ON s.vendor_uid = t.supplier_id) AS matched_count,
    (SELECT COUNT(*)
     FROM orderMgmt.catalog s
     WHERE NOT EXISTS (
         SELECT 1 FROM vendorDB.suppliers t
         WHERE s.vendor_uid = t.supplier_id)) AS unmatched_source_count,
    (SELECT COUNT(*)
     FROM vendorDB.suppliers t
     WHERE NOT EXISTS (
         SELECT 1 FROM orderMgmt.catalog s
         WHERE s.vendor_uid = t.supplier_id)) AS unmatched_target_count
FROM DUAL;
```

---

## Export SQL API

### Endpoint

`GET /reconciliation/rulesets/{ruleset_id}/export/sql`

### Parameters

| Parameter | Type | Description | Options |
|-----------|------|-------------|---------|
| `ruleset_id` | string | ID of ruleset to export | Required |
| `query_type` | string | Type of queries to generate | `all`, `matched`, `unmatched_source`, `unmatched_target` |

### Examples

**Export all query types:**
```bash
curl "http://localhost:8000/reconciliation/rulesets/RECON_ABC123/export/sql?query_type=all"
```

**Export only matched records query:**
```bash
curl "http://localhost:8000/reconciliation/rulesets/RECON_ABC123/export/sql?query_type=matched"
```

**Export only unmatched source query:**
```bash
curl "http://localhost:8000/reconciliation/rulesets/RECON_ABC123/export/sql?query_type=unmatched_source"
```

---

## Complete Workflow

### Step 1: Generate Reconciliation Rules

```bash
curl -X POST http://localhost:8000/reconciliation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_names": ["schema1", "schema2"],
    "kg_name": "my_kg",
    "use_llm_enhancement": true,
    "min_confidence": 0.7
  }'
```

**Response:**
```json
{
  "success": true,
  "ruleset_id": "RECON_ABC123",
  "rules_count": 5,
  "rules": [...]
}
```

Save the `ruleset_id` for execution.

### Step 2: Export SQL Queries

```bash
curl "http://localhost:8000/reconciliation/rulesets/RECON_ABC123/export/sql?query_type=all" \
  > reconciliation_queries.sql
```

### Step 3: Review SQL Queries

Open `reconciliation_queries.sql` and review:
- JOIN conditions are correct
- Table and column names match your database
- No security concerns

### Step 4: Execute (Choose Mode)

**Option A: SQL Export Mode (Manual)**
```bash
# Generate SQL
curl -X POST http://localhost:8000/reconciliation/execute \
  -H "Content-Type: application/json" \
  -d '{"ruleset_id": "RECON_ABC123", "limit": 100}' \
  | jq -r '.sql' > queries.sql

# Run in database client
sqlplus user/pass@db @queries.sql
```

**Option B: Direct Execution Mode (Automated)**
```bash
curl -X POST http://localhost:8000/reconciliation/execute \
  -H "Content-Type: application/json" \
  -d '{
    "ruleset_id": "RECON_ABC123",
    "limit": 100,
    "source_db_config": {...},
    "target_db_config": {...}
  }'
```

---

## Python Examples

### Example 1: SQL Export Mode

```python
import requests

BASE_URL = "http://localhost:8000"

# Execute in SQL export mode
response = requests.post(
    f"{BASE_URL}/reconciliation/execute",
    json={
        "ruleset_id": "RECON_ABC123",
        "limit": 100
    }
)

result = response.json()

# Save SQL to file
with open('reconciliation_queries.sql', 'w') as f:
    f.write(result['sql'])

print(f"✓ SQL queries saved to reconciliation_queries.sql")
print(f"  Mode: {result['mode']}")
print(f"  Message: {result['message']}")
```

### Example 2: Direct Execution Mode

```python
import requests

BASE_URL = "http://localhost:8000"

# Database configurations
source_db = {
    "db_type": "oracle",
    "host": "db-server-1.company.com",
    "port": 1521,
    "database": "PROD",
    "username": "schema1_user",
    "password": "password1",
    "service_name": "PRODPDB"
}

target_db = {
    "db_type": "oracle",
    "host": "db-server-2.company.com",
    "port": 1521,
    "database": "PROD",
    "username": "schema2_user",
    "password": "password2",
    "service_name": "PRODPDB"
}

# Execute reconciliation
response = requests.post(
    f"{BASE_URL}/reconciliation/execute",
    json={
        "ruleset_id": "RECON_ABC123",
        "limit": 100,
        "source_db_config": source_db,
        "target_db_config": target_db,
        "include_matched": True,
        "include_unmatched": True
    }
)

result = response.json()

print(f"✓ Reconciliation executed successfully!")
print(f"  Matched: {result['matched_count']}")
print(f"  Unmatched Source: {result['unmatched_source_count']}")
print(f"  Unmatched Target: {result['unmatched_target_count']}")
print(f"  Execution Time: {result['execution_time_ms']:.2f} ms")

# Process matched records
for match in result['matched_records']:
    print(f"\nMatched by rule: {match['rule_name']}")
    print(f"  Confidence: {match['match_confidence']}")
    print(f"  Source: {match['source_record']}")
    print(f"  Target: {match['target_record']}")
```

### Example 3: Export Specific Query Types

```python
import requests

BASE_URL = "http://localhost:8000"
RULESET_ID = "RECON_ABC123"

# Export different query types
query_types = ["all", "matched", "unmatched_source", "unmatched_target"]

for query_type in query_types:
    response = requests.get(
        f"{BASE_URL}/reconciliation/rulesets/{RULESET_ID}/export/sql",
        params={"query_type": query_type}
    )

    result = response.json()
    sql = result['sql']

    # Save to file
    filename = f"reconciliation_{query_type}.sql"
    with open(filename, 'w') as f:
        f.write(sql)

    print(f"✓ {query_type} queries saved to {filename}")
```

---

## Running the Demo

```bash
# Start the API server
python -m uvicorn kg_builder.main:app --reload

# In another terminal, run the demo
python demo_reconciliation_execution.py
```

The demo will:
1. List available schemas
2. Generate a knowledge graph
3. Generate reconciliation rules
4. Export SQL queries in multiple formats
5. Execute in SQL export mode
6. Show how to use direct execution mode

---

## Troubleshooting

### Issue: "JayDeBeApi is not installed"

**Solution:**
```bash
pip install JayDeBeApi
```

### Issue: "JDBC driver not found"

**Solution:**
1. Download the appropriate JDBC driver JAR
2. Place it in `jdbc_drivers/` directory
3. Verify path in `.env`: `JDBC_DRIVERS_PATH=jdbc_drivers`

### Issue: "Failed to connect to database"

**Solution:**
1. Verify database credentials
2. Check network connectivity
3. Ensure database is running
4. Verify firewall rules

### Issue: "Table not found"

**Solution:**
1. Verify schema and table names (case-sensitive)
2. Ensure user has SELECT permissions
3. Check if tables are in the correct schema

### Issue: SQL syntax errors

**Solution:**
1. Export SQL and review manually
2. Database-specific syntax may differ (ROWNUM vs LIMIT)
3. Customize SQL as needed for your database

---

## Best Practices

### Security

1. **Never commit database credentials**
   - Use environment variables
   - Use secret management systems

2. **Use read-only database users**
   - Grant only SELECT permissions
   - Limit to specific schemas/tables

3. **Secure the API endpoint**
   - Use HTTPS in production
   - Implement authentication/authorization
   - Rate limit requests

### Performance

1. **Use appropriate limits**
   - Start with small limits (100-1000 records)
   - Increase gradually based on performance

2. **Add indexes**
   - Index columns used in JOIN conditions
   - Monitor query performance

3. **Batch processing**
   - For large datasets, process in batches
   - Use pagination

### Monitoring

1. **Track execution metrics**
   - Execution time
   - Match rates
   - Error rates

2. **Log results**
   - Save matched/unmatched records
   - Track changes over time

3. **Validate results**
   - Spot-check matched records
   - Investigate low match rates

---

## API Reference

### POST /reconciliation/execute

Execute reconciliation rules.

**Request Body:**
```json
{
  "ruleset_id": "string (required)",
  "limit": 100,
  "source_db_config": {
    "db_type": "oracle|sqlserver|postgresql|mysql",
    "host": "string",
    "port": integer,
    "database": "string",
    "username": "string",
    "password": "string",
    "service_name": "string (optional, Oracle only)"
  },
  "target_db_config": {
    "db_type": "oracle|sqlserver|postgresql|mysql",
    "host": "string",
    "port": integer,
    "database": "string",
    "username": "string",
    "password": "string",
    "service_name": "string (optional, Oracle only)"
  },
  "include_matched": true,
  "include_unmatched": true
}
```

**Response (SQL Export Mode):**
```json
{
  "success": true,
  "mode": "sql_export",
  "message": "string",
  "sql": "string",
  "instructions": ["string"]
}
```

**Response (Direct Execution Mode):**
```json
{
  "success": true,
  "matched_count": integer,
  "unmatched_source_count": integer,
  "unmatched_target_count": integer,
  "matched_records": [...],
  "unmatched_source": [...],
  "unmatched_target": [...],
  "execution_time_ms": float
}
```

### GET /reconciliation/rulesets/{ruleset_id}/export/sql

Export ruleset as SQL queries.

**Query Parameters:**
- `query_type`: `all`, `matched`, `unmatched_source`, `unmatched_target`

**Response:**
```json
{
  "success": true,
  "ruleset_id": "string",
  "query_type": "string",
  "sql": "string"
}
```

---

## Next Steps

1. ✅ Review generated SQL queries
2. ✅ Test with small datasets first
3. ✅ Validate match results
4. ✅ Set up monitoring and logging
5. ✅ Integrate into your data pipelines

For more information, see:
- [Rule Validation Guide](RULE_VALIDATION_GUIDE.md)
- [Reconciliation Usage Guide](RECONCILIATION_USAGE_GUIDE.md)
- [Reconciliation Rules Approach](RECONCILIATION_RULES_APPROACH.md)

---

**Questions?** Check the API documentation at http://localhost:8000/docs
