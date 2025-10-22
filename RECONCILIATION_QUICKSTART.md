# Reconciliation Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### 1. Start the Server
```bash
python -m uvicorn kg_builder.main:app --reload
```

### 2. Run the Demo
```bash
python demo_reconciliation_execution.py
```

That's it! The demo will:
- ✅ Generate a knowledge graph
- ✅ Create reconciliation rules
- ✅ Export SQL queries
- ✅ Show execution examples

---

## 📋 Complete Workflow

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

**Save the `ruleset_id` from the response!**

### Step 2: Export SQL Queries
```bash
curl "http://localhost:8000/reconciliation/rulesets/RECON_ABC123/export/sql?query_type=all" \
  > reconciliation_queries.sql
```

### Step 3: Execute Reconciliation

**Option A: SQL Export Mode (Easy)**
```bash
curl -X POST http://localhost:8000/reconciliation/execute \
  -H "Content-Type: application/json" \
  -d '{
    "ruleset_id": "RECON_ABC123",
    "limit": 100
  }' | jq -r '.sql' > queries.sql
```

Then run `queries.sql` in your database client!

**Option B: Direct Execution (Automated)**
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
    }
  }'
```

---

## 🎯 What Gets Generated?

The system generates **4 types of SQL queries**:

### 1. ✅ Matched Records
```sql
-- Records that exist in BOTH source and target
SELECT s.*, t.*
FROM schema1.table1 s
INNER JOIN schema2.table2 t ON s.id = t.id;
```

### 2. ⚠️ Unmatched Source
```sql
-- Records ONLY in source (missing in target)
SELECT s.*
FROM schema1.table1 s
WHERE NOT EXISTS (
    SELECT 1 FROM schema2.table2 t WHERE s.id = t.id
);
```

### 3. ⚠️ Unmatched Target
```sql
-- Records ONLY in target (missing in source)
SELECT t.*
FROM schema2.table2 t
WHERE NOT EXISTS (
    SELECT 1 FROM schema1.table1 s WHERE s.id = t.id
);
```

### 4. 📊 Summary Statistics
```sql
-- Counts and match rates
SELECT
    'Rule_Name' AS rule_name,
    (SELECT COUNT(*) FROM schema1.table1) AS total_source,
    (SELECT COUNT(*) FROM schema2.table2) AS total_target,
    -- ... matched/unmatched counts
FROM DUAL;
```

---

## 🔧 Configuration

### For SQL Export Mode
**No configuration needed!** Just provide the `ruleset_id`.

### For Direct Execution Mode
1. Install JayDeBeApi:
```bash
pip install JayDeBeApi
```

2. Add JDBC drivers to `jdbc_drivers/` directory:
   - Oracle: `ojdbc8.jar` or `ojdbc11.jar`
   - SQL Server: `mssql-jdbc-*.jar`
   - PostgreSQL: `postgresql-*.jar`
   - MySQL: `mysql-connector-*.jar`

3. Update `.env`:
```bash
JDBC_DRIVERS_PATH=jdbc_drivers
```

---

## 📚 Documentation

- **[Complete Execution Guide](docs/RECONCILIATION_EXECUTION_GUIDE.md)** - Detailed documentation
- **[Rule Validation Guide](docs/RULE_VALIDATION_GUIDE.md)** - Validate rules before execution
- **[Demo Script](demo_reconciliation_execution.py)** - Complete working example

---

## 🐛 Troubleshooting

### Server won't start?
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Or use a different port
python -m uvicorn kg_builder.main:app --port 8001
```

### No schemas found?
Place JSON schema files in the `schemas/` directory.

### JDBC connection fails?
1. Check database credentials
2. Verify JDBC driver is in `jdbc_drivers/`
3. Ensure database is running and accessible

---

## 🎓 Examples

### Python Example
```python
import requests

# Generate and execute
response = requests.post(
    "http://localhost:8000/reconciliation/execute",
    json={"ruleset_id": "RECON_ABC123", "limit": 100}
)

# Get SQL queries
sql = response.json()['sql']

# Save to file
with open('queries.sql', 'w') as f:
    f.write(sql)

print("✓ SQL queries saved to queries.sql")
```

### cURL Example
```bash
# Generate rules
RULESET_ID=$(curl -s -X POST http://localhost:8000/reconciliation/generate \
  -H "Content-Type: application/json" \
  -d '{"schema_names":["schema1","schema2"],"kg_name":"test"}' \
  | jq -r '.ruleset_id')

echo "Ruleset ID: $RULESET_ID"

# Export SQL
curl "http://localhost:8000/reconciliation/rulesets/$RULESET_ID/export/sql" \
  | jq -r '.sql' > reconciliation.sql

echo "✓ SQL saved to reconciliation.sql"
```

---

## ⚡ Quick Commands

```bash
# 1. Start server
python -m uvicorn kg_builder.main:app --reload

# 2. Run demo (in another terminal)
python demo_reconciliation_execution.py

# 3. List all rulesets
curl http://localhost:8000/reconciliation/rulesets

# 4. Export SQL for a ruleset
curl "http://localhost:8000/reconciliation/rulesets/RECON_ABC123/export/sql?query_type=all"

# 5. Execute in SQL export mode
curl -X POST http://localhost:8000/reconciliation/execute \
  -H "Content-Type: application/json" \
  -d '{"ruleset_id":"RECON_ABC123","limit":100}'
```

---

## 🎉 Success Indicators

You'll know it's working when:
- ✅ Server starts without errors
- ✅ Demo completes successfully
- ✅ SQL files are generated in the project directory
- ✅ SQL queries are valid and can run in your database
- ✅ Matched/unmatched records are identified correctly

---

## 🆘 Need Help?

1. Check the full documentation: [RECONCILIATION_EXECUTION_GUIDE.md](docs/RECONCILIATION_EXECUTION_GUIDE.md)
2. Review the demo script: [demo_reconciliation_execution.py](demo_reconciliation_execution.py)
3. Check API docs: http://localhost:8000/docs
4. Review test examples: [test_rule_validation.py](test_rule_validation.py)

---

## 🚀 Next Steps

1. ✅ Run the demo script
2. ✅ Review generated SQL files
3. ✅ Test queries in your database
4. ✅ Validate results match expectations
5. ✅ Integrate into your data pipeline

**Happy Reconciling!** 🎯
