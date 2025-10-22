# Complete Setup Guide - Reconciliation with Environment Configs

## 🎯 Overview

This guide shows you how to set up and use the reconciliation system with **environment-based database configuration** for better security and usability.

---

## 📋 Prerequisites

- Python 3.8+
- Access to source and target databases
- JDBC drivers (for direct execution mode)

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt

# Optional: For direct database execution
pip install JayDeBeApi
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your database credentials
vim .env
```

**Example `.env` configuration:**
```bash
# Enable environment-based configs
USE_ENV_DB_CONFIGS=true

# Source database
SOURCE_DB_TYPE=oracle
SOURCE_DB_HOST=db-server-1.company.com
SOURCE_DB_PORT=1521
SOURCE_DB_DATABASE=ORCL
SOURCE_DB_USERNAME=your_username
SOURCE_DB_PASSWORD=your_secure_password

# Target database
TARGET_DB_TYPE=oracle
TARGET_DB_HOST=db-server-2.company.com
TARGET_DB_PORT=1521
TARGET_DB_DATABASE=ORCL
TARGET_DB_USERNAME=your_username
TARGET_DB_PASSWORD=your_secure_password
```

### Step 3: Add JDBC Drivers (Optional)

For direct execution mode, download and place JDBC drivers:

```bash
# Create jdbc_drivers directory
mkdir jdbc_drivers

# Download drivers (examples):
# - Oracle: ojdbc8.jar or ojdbc11.jar
# - SQL Server: mssql-jdbc-*.jar
# - PostgreSQL: postgresql-*.jar
# - MySQL: mysql-connector-*.jar

# Place JAR files in jdbc_drivers/
cp ~/Downloads/ojdbc8.jar jdbc_drivers/
```

### Step 4: Start the Server

```bash
python -m uvicorn kg_builder.main:app --reload
```

Server will start at: http://localhost:8000

### Step 5: Run the Demo

```bash
# In another terminal
python demo_reconciliation_execution.py
```

---

## 🎓 Usage Examples

### Example 1: Basic Reconciliation (SQL Export Mode)

**No database credentials needed!**

```python
import requests

# Generate rules
response = requests.post(
    "http://localhost:8000/reconciliation/generate",
    json={
        "schema_names": ["schema1", "schema2"],
        "kg_name": "my_kg",
        "use_llm_enhancement": True,
        "min_confidence": 0.7
    }
)

ruleset_id = response.json()['ruleset_id']

# Execute reconciliation (SQL export mode)
response = requests.post(
    "http://localhost:8000/reconciliation/execute",
    json={
        "ruleset_id": ruleset_id,
        "limit": 100
    }
)

# Get SQL queries
sql = response.json()['sql']

# Save to file
with open('reconciliation.sql', 'w') as f:
    f.write(sql)

print("✓ SQL queries saved to reconciliation.sql")
print("Run these queries in your database client!")
```

### Example 2: Direct Execution (With Environment Configs)

**Database credentials from `.env` file:**

```python
import requests

# Execute with environment configs (no credentials in request!)
response = requests.post(
    "http://localhost:8000/reconciliation/execute",
    json={
        "ruleset_id": "RECON_ABC123",
        "limit": 100
    }
)

result = response.json()
print(f"Matched: {result['matched_count']}")
print(f"Unmatched Source: {result['unmatched_source_count']}")
print(f"Unmatched Target: {result['unmatched_target_count']}")
```

### Example 3: Override Environment Configs

**Payload configs override environment configs:**

```python
import requests

# Use different credentials for this specific request
response = requests.post(
    "http://localhost:8000/reconciliation/execute",
    json={
        "ruleset_id": "RECON_ABC123",
        "limit": 100,
        "source_db_config": {
            "db_type": "oracle",
            "host": "special-db.company.com",
            "port": 1521,
            "database": "ORCL",
            "username": "special_user",
            "password": "special_pass"
        },
        "target_db_config": {
            "db_type": "oracle",
            "host": "special-db2.company.com",
            "port": 1521,
            "database": "ORCL",
            "username": "special_user2",
            "password": "special_pass2"
        }
    }
)
```

---

## 🔧 Configuration Modes

### Mode 1: SQL Export Only (No Database Access)

**`.env` configuration:**
```bash
# Leave credentials empty or set USE_ENV_DB_CONFIGS=false
USE_ENV_DB_CONFIGS=false
```

**Usage:**
- System generates SQL queries
- No database execution
- Run queries manually in your database client

### Mode 2: Environment-Based Execution

**`.env` configuration:**
```bash
USE_ENV_DB_CONFIGS=true
SOURCE_DB_USERNAME=your_username
SOURCE_DB_PASSWORD=your_password
TARGET_DB_USERNAME=your_username
TARGET_DB_PASSWORD=your_password
```

**Usage:**
- System uses credentials from `.env`
- Automatic database execution
- No credentials in API requests

### Mode 3: Payload-Based Execution

**`.env` configuration:**
```bash
# Any setting - payload always takes priority
```

**Usage:**
- Provide credentials in each API request
- Overrides environment configs
- Good for ad-hoc testing

---

## 📊 Configuration Priority

```
1. Request Payload (highest priority)
   ↓
2. Environment Variables (.env file)
   ↓
3. None (SQL export mode - lowest priority)
```

---

## 🔒 Security Setup

### 1. Secure `.env` File

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore

# Set proper file permissions (Unix/Linux)
chmod 600 .env
```

### 2. Use Read-Only Database Users

**Oracle example:**
```sql
-- Create read-only user
CREATE USER reconciliation_ro IDENTIFIED BY secure_password;
GRANT CONNECT TO reconciliation_ro;
GRANT SELECT ON schema1.* TO reconciliation_ro;
GRANT SELECT ON schema2.* TO reconciliation_ro;

-- Verify no write permissions
SELECT * FROM DBA_TAB_PRIVS WHERE GRANTEE = 'RECONCILIATION_RO';
```

**PostgreSQL example:**
```sql
-- Create read-only user
CREATE USER reconciliation_ro WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE production_db TO reconciliation_ro;
GRANT USAGE ON SCHEMA schema1 TO reconciliation_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA schema1 TO reconciliation_ro;
```

### 3. Network Security

```bash
# Restrict database access to specific IPs
# Configure firewall or database whitelist
# Example: Only allow API server IP to connect to database
```

### 4. Credential Rotation

```bash
# Schedule regular password changes
# Example cron job for monthly rotation:
0 0 1 * * /path/to/rotate_credentials.sh
```

---

## 🧪 Testing Your Setup

### Test 1: Environment Variables Loaded

```python
import os
print("Source username:", os.getenv('SOURCE_DB_USERNAME'))
print("Target username:", os.getenv('TARGET_DB_USERNAME'))
print("Use env configs:", os.getenv('USE_ENV_DB_CONFIGS'))
```

### Test 2: API Health Check

```bash
curl http://localhost:8000/health
```

**Expected output:**
```json
{
  "status": "healthy",
  "falkordb_connected": true,
  "graphiti_available": true
}
```

### Test 3: SQL Export Mode

```bash
curl -X POST http://localhost:8000/reconciliation/execute \
  -H "Content-Type: application/json" \
  -d '{"ruleset_id":"RECON_ABC123","limit":10}'
```

**Expected:** SQL queries returned (no database execution)

### Test 4: Direct Execution Mode

```bash
# With credentials in .env
curl -X POST http://localhost:8000/reconciliation/execute \
  -H "Content-Type: application/json" \
  -d '{"ruleset_id":"RECON_ABC123","limit":10}'
```

**Expected:** Matched/unmatched records returned (database executed)

### Test 5: Check Logs

```bash
# Look for confirmation in logs:
tail -f logs/app.log | grep "database config"
```

**Expected log messages:**
- "Using database configurations from environment variables"
- "Direct Execution Mode: Executing ruleset..."

---

## 🐛 Troubleshooting

### Issue: Server won't start

**Check:**
```bash
# 1. Python version
python --version  # Should be 3.8+

# 2. Dependencies installed
pip list | grep fastapi

# 3. Port availability
netstat -ano | findstr :8000
```

### Issue: "Database connections not provided"

**Fix:**
```bash
# 1. Check .env exists
ls -la .env

# 2. Check credentials are set
cat .env | grep DB_USERNAME

# 3. Ensure USE_ENV_DB_CONFIGS=true
grep USE_ENV_DB_CONFIGS .env

# 4. Restart server
```

### Issue: "Failed to connect to database"

**Fix:**
```bash
# 1. Test connectivity
ping db-server.company.com
telnet db-server.company.com 1521

# 2. Verify credentials work
sqlplus username/password@host:port/service

# 3. Check firewall rules
# 4. Verify database is running
```

### Issue: "JDBC driver not found"

**Fix:**
```bash
# 1. Check driver exists
ls jdbc_drivers/

# 2. Download correct driver
# Oracle: https://www.oracle.com/database/technologies/appdev/jdbc-downloads.html
# SQL Server: https://docs.microsoft.com/en-us/sql/connect/jdbc/

# 3. Place in jdbc_drivers/
# 4. Verify in .env: JDBC_DRIVERS_PATH=jdbc_drivers
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[README_RECONCILIATION.md](README_RECONCILIATION.md)** | Main documentation |
| **[RECONCILIATION_QUICKSTART.md](RECONCILIATION_QUICKSTART.md)** | Quick reference |
| **[ENV_CONFIG_GUIDE.md](docs/ENV_CONFIG_GUIDE.md)** | Environment configuration |
| **[RECONCILIATION_EXECUTION_GUIDE.md](docs/RECONCILIATION_EXECUTION_GUIDE.md)** | Execution guide |
| **[ENV_CONFIG_IMPLEMENTATION.md](ENV_CONFIG_IMPLEMENTATION.md)** | Implementation details |
| **[.env.example](.env.example)** | Configuration template |

---

## 🎯 Next Steps

### For Development

1. ✅ Configure `.env` with dev database credentials
2. ✅ Run demo script to verify setup
3. ✅ Review generated SQL queries
4. ✅ Test with your schemas

### For Staging

1. ✅ Create `.env.staging` with staging credentials
2. ✅ Test full reconciliation workflow
3. ✅ Validate results against known data
4. ✅ Document any issues

### For Production

1. ✅ Use read-only database users
2. ✅ Set up secrets management (AWS Secrets Manager, etc.)
3. ✅ Configure monitoring and alerting
4. ✅ Set up credential rotation
5. ✅ Enable audit logging

---

## 💡 Best Practices

### Development
- ✅ Use environment configs for regular work
- ✅ Use payload configs for ad-hoc testing
- ✅ Keep `.env` in `.gitignore`
- ✅ Use SQL export mode to review queries first

### Production
- ✅ Always use environment configs
- ✅ Never use payload configs (security risk)
- ✅ Use secrets management system
- ✅ Enable database audit logging
- ✅ Monitor execution metrics
- ✅ Set up alerts for failures

---

## ✅ Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created from `.env.example`
- [ ] Database credentials configured in `.env`
- [ ] JDBC drivers downloaded (if using direct execution)
- [ ] Server starts successfully
- [ ] Health check passes
- [ ] Demo script runs successfully
- [ ] SQL queries generated
- [ ] Database execution works (if configured)
- [ ] `.env` added to `.gitignore`
- [ ] Documentation reviewed

---

## 🎉 You're Ready!

Your reconciliation system is now set up with environment-based configuration!

### Quick Commands

```bash
# Start server
python -m uvicorn kg_builder.main:app --reload

# Run demo
python demo_reconciliation_execution.py

# Check health
curl http://localhost:8000/health

# Execute reconciliation
curl -X POST http://localhost:8000/reconciliation/execute \
  -d '{"ruleset_id":"RECON_ABC123","limit":100}'
```

### What You Can Do Now

✅ Generate reconciliation rules from knowledge graphs
✅ Export rules as SQL queries
✅ Execute reconciliation (SQL export or direct execution)
✅ Find matched records between data sources
✅ Identify unmatched records
✅ Get summary statistics

**Happy Reconciling!** 🚀

---

**Need help?** Check the [Documentation](#-documentation) or API docs at http://localhost:8000/docs
