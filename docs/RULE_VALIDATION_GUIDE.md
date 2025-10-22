# Rule Validation Guide

## Overview

The Rule Validation feature validates reconciliation rules against **actual database data** using JDBC connections. This ensures that generated rules will work correctly before using them in production.

---

## What Gets Validated?

When you validate a rule, the system performs these checks:

| Check | Description | Result |
|-------|-------------|--------|
| **Table Existence** | Verifies source/target tables exist | `exists: true/false` |
| **Column Existence** | Verifies all columns in the rule exist | `exists: true/false` |
| **Type Compatibility** | Checks if column data types are compatible | `types_compatible: true/false` |
| **Sample Matching** | Tests rule on sample data (e.g., 100 records) | `sample_match_rate: 0.0-1.0` |
| **Cardinality** | Detects relationship type | `cardinality: "1:1", "1:N", "N:1", "N:M"` |
| **Performance** | Estimates query execution time | `estimated_performance_ms: float` |

---

## Prerequisites

### 1. Install JayDeBeApi

```bash
pip install JayDeBeApi
```

### 2. Download JDBC Drivers

Create a directory for JDBC drivers:

```bash
mkdir jdbc_drivers
```

Download the appropriate driver for your database:

| Database | Driver JAR | Download Link |
|----------|------------|---------------|
| **Oracle** | `ojdbc8.jar` or `ojdbc11.jar` | [Oracle JDBC Downloads](https://www.oracle.com/database/technologies/appdev/jdbc-downloads.html) |
| **SQL Server** | `mssql-jdbc-*.jar` | [Microsoft JDBC Downloads](https://docs.microsoft.com/en-us/sql/connect/jdbc/download-microsoft-jdbc-driver-for-sql-server) |
| **PostgreSQL** | `postgresql-*.jar` | [PostgreSQL JDBC](https://jdbc.postgresql.org/download.html) |
| **MySQL** | `mysql-connector-java-*.jar` | [MySQL Connector/J](https://dev.mysql.com/downloads/connector/j/) |

Place the JAR files in the `jdbc_drivers/` directory:

```
jdbc_drivers/
├── ojdbc8.jar
├── mssql-jdbc-9.4.0.jre11.jar
├── postgresql-42.3.1.jar
└── mysql-connector-java-8.0.28.jar
```

### 3. Configure Environment

Update `.env` file:

```bash
# JDBC Settings
JDBC_DRIVERS_PATH=jdbc_drivers
```

---

## Usage

### Basic Validation (No Database Connection)

Validates rule structure only, without connecting to actual databases:

```python
import requests

BASE_URL = "http://localhost:8000"

rule = {
    "rule_id": "RULE_001",
    "rule_name": "Vendor_Match",
    "source_schema": "orderMgmt",
    "source_table": "catalog",
    "source_columns": ["vendor_uid"],
    "target_schema": "vendorDB",
    "target_table": "suppliers",
    "target_columns": ["supplier_id"],
    "match_type": "exact",
    "transformation": None,
    "confidence_score": 0.95,
    "reasoning": "Vendor UID matching",
    "validation_status": "UNCERTAIN",
    "llm_generated": False,
    "created_at": "2025-10-22T10:00:00",
    "metadata": {}
}

request_data = {
    "rule": rule,
    "sample_size": 100
    # No database configs provided - basic validation only
}

response = requests.post(
    f"{BASE_URL}/reconciliation/validate",
    json=request_data
)

print(response.json())
```

**Expected Output:**

```json
{
  "success": true,
  "validation": {
    "rule_id": "RULE_001",
    "valid": true,
    "exists": true,
    "types_compatible": true,
    "sample_match_rate": null,
    "cardinality": null,
    "estimated_performance_ms": null,
    "issues": [],
    "warnings": [
      "Database connections not provided - skipping data validation",
      "Provide 'source_db_config' and 'target_db_config' for full validation"
    ]
  }
}
```

---

### Full Validation (With Database Connections)

Validates against actual database data:

```python
import requests

BASE_URL = "http://localhost:8000"

# Your rule to validate
rule = {
    "rule_id": "RULE_002",
    "rule_name": "Order_Customer_Match",
    "source_schema": "SALES_SCHEMA",
    "source_table": "ORDERS",
    "source_columns": ["CUSTOMER_ID"],
    "target_schema": "CRM_SCHEMA",
    "target_table": "CUSTOMERS",
    "target_columns": ["CUST_ID"],
    "match_type": "exact",
    "transformation": None,
    "confidence_score": 0.92,
    "reasoning": "Customer ID matching between sales and CRM",
    "validation_status": "UNCERTAIN",
    "llm_generated": True,
    "created_at": "2025-10-22T10:00:00",
    "metadata": {}
}

# Source database configuration
source_db_config = {
    "db_type": "oracle",
    "host": "db-server-1.company.com",
    "port": 1521,
    "database": "PROD_DB",
    "username": "sales_user",
    "password": "your_password_here",
    "service_name": "PRODPDB"
}

# Target database configuration
target_db_config = {
    "db_type": "oracle",
    "host": "db-server-2.company.com",
    "port": 1521,
    "database": "PROD_DB",
    "username": "crm_user",
    "password": "your_password_here",
    "service_name": "PRODPDB"
}

request_data = {
    "rule": rule,
    "sample_size": 100,
    "source_db_config": source_db_config,
    "target_db_config": target_db_config
}

response = requests.post(
    f"{BASE_URL}/reconciliation/validate",
    json=request_data
)

result = response.json()
print(result)
```

**Expected Output:**

```json
{
  "success": true,
  "validation": {
    "rule_id": "RULE_002",
    "valid": true,
    "exists": true,
    "types_compatible": true,
    "sample_match_rate": 0.87,
    "cardinality": "N:1",
    "estimated_performance_ms": 45.3,
    "issues": [],
    "warnings": [
      "Low match rate detected: 87.00%"
    ]
  }
}
```

---

## Database Configuration Examples

### Oracle

```python
db_config = {
    "db_type": "oracle",
    "host": "oracle-server.example.com",
    "port": 1521,
    "database": "ORCL",
    "username": "schema_user",
    "password": "password",
    "service_name": "ORCLPDB"  # Optional: use service_name instead of database
}
```

### SQL Server

```python
db_config = {
    "db_type": "sqlserver",
    "host": "sqlserver.example.com",
    "port": 1433,
    "database": "MyDatabase",
    "username": "sa",
    "password": "password"
}
```

### PostgreSQL

```python
db_config = {
    "db_type": "postgresql",
    "host": "postgres.example.com",
    "port": 5432,
    "database": "mydb",
    "username": "postgres",
    "password": "password"
}
```

### MySQL

```python
db_config = {
    "db_type": "mysql",
    "host": "mysql.example.com",
    "port": 3306,
    "database": "mydb",
    "username": "root",
    "password": "password"
}
```

---

## Understanding Validation Results

### Valid Rule Example

```json
{
  "rule_id": "RULE_003",
  "valid": true,
  "exists": true,
  "types_compatible": true,
  "sample_match_rate": 0.95,
  "cardinality": "1:1",
  "estimated_performance_ms": 23.5,
  "issues": [],
  "warnings": []
}
```

✅ **Interpretation:**
- Rule is valid and ready for production
- 95% of sample records matched successfully
- 1:1 relationship detected (unique on both sides)
- Expected to execute in ~23.5ms

---

### Invalid Rule Example

```json
{
  "rule_id": "RULE_004",
  "valid": false,
  "exists": false,
  "types_compatible": false,
  "sample_match_rate": null,
  "cardinality": null,
  "estimated_performance_ms": null,
  "issues": [
    "Source table not found: SCHEMA1.MISSING_TABLE",
    "Target column not found: user_id in SCHEMA2.USERS",
    "Type mismatch: order_id (type 2) vs order_num (type 12)"
  ],
  "warnings": []
}
```

❌ **Interpretation:**
- Rule is invalid - DO NOT use in production
- Multiple issues detected:
  - Source table doesn't exist
  - Target column missing
  - Incompatible data types

---

### Low Match Rate Example

```json
{
  "rule_id": "RULE_005",
  "valid": true,
  "exists": true,
  "types_compatible": true,
  "sample_match_rate": 0.35,
  "cardinality": "N:M",
  "estimated_performance_ms": 156.7,
  "issues": [],
  "warnings": [
    "Low match rate detected: 35.00%"
  ]
}
```

⚠️ **Interpretation:**
- Rule is structurally valid but has low match rate (35%)
- Many-to-many relationship detected
- May need rule refinement or transformation
- Review and test thoroughly before production use

---

## Match Rate Guidelines

| Match Rate | Interpretation | Recommendation |
|------------|----------------|----------------|
| **90-100%** | Excellent | Use in production |
| **70-89%** | Good | Review edge cases, then use |
| **50-69%** | Fair | Investigate mismatches, may need transformation |
| **30-49%** | Poor | Rule likely incorrect, needs revision |
| **0-29%** | Very Poor | Rule is wrong, do not use |

---

## Cardinality Types

| Cardinality | Meaning | Example |
|-------------|---------|---------|
| **1:1** | One-to-one | Each order has one invoice |
| **1:N** | One-to-many | One customer has many orders |
| **N:1** | Many-to-one | Many orders belong to one customer |
| **N:M** | Many-to-many | Products and suppliers (complex) |

---

## End-to-End Workflow

### Step 1: Generate Rules

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

### Step 2: Validate Each Rule

For each generated rule, validate it:

```bash
curl -X POST http://localhost:8000/reconciliation/validate \
  -H "Content-Type: application/json" \
  -d '{
    "rule": {...},
    "sample_size": 100,
    "source_db_config": {...},
    "target_db_config": {...}
  }'
```

### Step 3: Filter Rules

Keep only rules with:
- `valid: true`
- `sample_match_rate >= 0.7`
- No critical issues

### Step 4: Use Validated Rules

Use validated rules for:
- ETL pipelines
- Data integration
- Master data management
- Reconciliation reports

---

## Running the Test Suite

```bash
# Start the API server
python -m uvicorn kg_builder.main:app --reload

# In another terminal, run the test script
python test_rule_validation.py
```

The test script demonstrates:
1. ✅ Basic validation without DB connection
2. ✅ Full validation with DB connection (requires config)
3. ✅ Validating generated rules end-to-end
4. ✅ Database configuration examples

---

## Troubleshooting

### Issue: "JDBC driver not found"

**Solution:**
1. Download the correct JDBC driver JAR
2. Place it in `jdbc_drivers/` directory
3. Verify path in `.env`: `JDBC_DRIVERS_PATH=jdbc_drivers`

### Issue: "Failed to connect to database"

**Solution:**
1. Verify database credentials are correct
2. Check network connectivity to database server
3. Ensure database is running and accepting connections
4. Verify firewall rules allow connection

### Issue: "Source table not found"

**Solution:**
1. Verify schema name is correct (case-sensitive)
2. Verify table name is correct (case-sensitive)
3. Ensure user has SELECT permissions on the table

### Issue: "Type mismatch"

**Solution:**
1. Check if column data types are truly incompatible
2. Consider adding a transformation to the rule
3. Review the match_type (exact vs fuzzy vs transformation)

---

## API Reference

### POST /reconciliation/validate

Validate a reconciliation rule.

**Request Body:**

```json
{
  "rule": {
    "rule_id": "string",
    "rule_name": "string",
    "source_schema": "string",
    "source_table": "string",
    "source_columns": ["string"],
    "target_schema": "string",
    "target_table": "string",
    "target_columns": ["string"],
    "match_type": "exact|fuzzy|composite|transformation|semantic",
    "transformation": "string|null",
    "confidence_score": 0.0-1.0,
    "reasoning": "string",
    "validation_status": "VALID|LIKELY|UNCERTAIN",
    "llm_generated": true|false,
    "created_at": "ISO-8601 datetime",
    "metadata": {}
  },
  "sample_size": 100,
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
  }
}
```

**Response:**

```json
{
  "success": true|false,
  "validation": {
    "rule_id": "string",
    "valid": true|false,
    "exists": true|false,
    "types_compatible": true|false,
    "sample_match_rate": 0.0-1.0 | null,
    "cardinality": "1:1|1:N|N:1|N:M" | null,
    "estimated_performance_ms": float | null,
    "issues": ["string"],
    "warnings": ["string"]
  }
}
```

---

## Security Considerations

⚠️ **IMPORTANT:**

1. **Never commit database passwords to version control**
   - Use environment variables
   - Use secret management systems

2. **Use read-only database users for validation**
   - Grant only SELECT permissions
   - Limit to specific schemas/tables

3. **Secure API endpoint**
   - Use HTTPS in production
   - Implement authentication/authorization
   - Rate limit validation requests

4. **Limit sample sizes**
   - Default: 100 records
   - Don't validate with full datasets
   - Use appropriate sample_size for large tables

---

## Next Steps

1. ✅ Set up JDBC drivers
2. ✅ Configure database connections
3. ✅ Run test_rule_validation.py
4. ✅ Validate your generated rules
5. ✅ Use validated rules in production

For more information, see:
- [Reconciliation Usage Guide](RECONCILIATION_USAGE_GUIDE.md)
- [Reconciliation Rules Approach](RECONCILIATION_RULES_APPROACH.md)

---

**Questions?** Check the API documentation at http://localhost:8000/docs
