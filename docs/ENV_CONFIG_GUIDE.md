# Environment-Based Configuration Guide

## Overview

Database credentials can now be configured via **environment variables** instead of passing them in API request payloads. This provides:

✅ **Better Security** - No credentials in API requests/logs
✅ **Easier Setup** - Configure once, use everywhere
✅ **Environment Management** - Different configs for dev/staging/prod
✅ **No Code Changes** - Update configs without changing code

---

## Configuration Priority

The system uses this priority order (highest to lowest):

1. **Request Payload** - Database configs in API request body
2. **Environment Variables** - Database configs from `.env` file
3. **None** - SQL export mode (no database execution)

---

## Quick Setup

### 1. Copy Example File

```bash
cp .env.example .env
```

### 2. Configure Database Credentials

Edit `.env` and add your database credentials:

```bash
# Enable environment-based configs
USE_ENV_DB_CONFIGS=true

# Source database
SOURCE_DB_TYPE=oracle
SOURCE_DB_HOST=db-server-1.company.com
SOURCE_DB_PORT=1521
SOURCE_DB_DATABASE=ORCL
SOURCE_DB_USERNAME=schema1_user
SOURCE_DB_PASSWORD=your_secure_password
SOURCE_DB_SERVICE_NAME=PRODPDB

# Target database
TARGET_DB_TYPE=oracle
TARGET_DB_HOST=db-server-2.company.com
TARGET_DB_PORT=1521
TARGET_DB_DATABASE=ORCL
TARGET_DB_USERNAME=schema2_user
TARGET_DB_PASSWORD=your_secure_password
TARGET_DB_SERVICE_NAME=PRODPDB
```

### 3. Use the API

Now you can make API requests **without** database configs in the payload:

```bash
# Before (with payload configs)
curl -X POST http://localhost:8000/reconciliation/execute \
  -H "Content-Type: application/json" \
  -d '{
    "ruleset_id": "RECON_ABC123",
    "limit": 100,
    "source_db_config": {...},
    "target_db_config": {...}
  }'

# After (with environment configs)
curl -X POST http://localhost:8000/reconciliation/execute \
  -H "Content-Type: application/json" \
  -d '{
    "ruleset_id": "RECON_ABC123",
    "limit": 100
  }'
```

The system automatically uses database configs from environment variables! 🎉

---

## Configuration Options

### Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `USE_ENV_DB_CONFIGS` | Enable env-based configs | `true` | `true`, `false` |
| `SOURCE_DB_TYPE` | Source database type | `oracle` | `oracle`, `sqlserver`, `postgresql`, `mysql` |
| `SOURCE_DB_HOST` | Source database host | `localhost` | `db-server-1.company.com` |
| `SOURCE_DB_PORT` | Source database port | `1521` | `1521`, `1433`, `5432`, `3306` |
| `SOURCE_DB_DATABASE` | Source database name | `ORCL` | `ORCL`, `ProductionDB`, `mydb` |
| `SOURCE_DB_USERNAME` | Source database username | `` | `schema1_user` |
| `SOURCE_DB_PASSWORD` | Source database password | `` | `your_secure_password` |
| `SOURCE_DB_SERVICE_NAME` | Source service name (Oracle) | `` | `PRODPDB` |
| `TARGET_DB_TYPE` | Target database type | `oracle` | `oracle`, `sqlserver`, `postgresql`, `mysql` |
| `TARGET_DB_HOST` | Target database host | `localhost` | `db-server-2.company.com` |
| `TARGET_DB_PORT` | Target database port | `1521` | `1521`, `1433`, `5432`, `3306` |
| `TARGET_DB_DATABASE` | Target database name | `ORCL` | `ORCL`, `AnalyticsDB`, `analytics` |
| `TARGET_DB_USERNAME` | Target database username | `` | `schema2_user` |
| `TARGET_DB_PASSWORD` | Target database password | `` | `your_secure_password` |
| `TARGET_DB_SERVICE_NAME` | Target service name (Oracle) | `` | `PRODPDB` |

---

## Usage Examples

### Example 1: Environment Configs Only

**`.env` file:**
```bash
USE_ENV_DB_CONFIGS=true
SOURCE_DB_USERNAME=schema1_user
SOURCE_DB_PASSWORD=password1
TARGET_DB_USERNAME=schema2_user
TARGET_DB_PASSWORD=password2
```

**API Request:**
```python
import requests

# No database configs in payload!
response = requests.post(
    "http://localhost:8000/reconciliation/execute",
    json={
        "ruleset_id": "RECON_ABC123",
        "limit": 100
    }
)

result = response.json()
print(f"Matched: {result['matched_count']}")
```

### Example 2: Payload Configs Override Environment

**`.env` file:**
```bash
USE_ENV_DB_CONFIGS=true
SOURCE_DB_USERNAME=default_user
SOURCE_DB_PASSWORD=default_pass
```

**API Request:**
```python
# Payload configs take priority over environment
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
        "target_db_config": {...}
    }
)
```

Environment configs are **ignored** when payload configs are provided.

### Example 3: Disable Environment Configs

**`.env` file:**
```bash
# Disable environment-based configs
USE_ENV_DB_CONFIGS=false
```

Now the system will **only** use:
1. Payload configs (if provided)
2. SQL export mode (if no payload configs)

Environment credentials are ignored.

### Example 4: Different Databases

**`.env` file:**
```bash
# Source: Oracle database
SOURCE_DB_TYPE=oracle
SOURCE_DB_HOST=oracle-prod.company.com
SOURCE_DB_PORT=1521
SOURCE_DB_DATABASE=ORCL
SOURCE_DB_USERNAME=oracle_user
SOURCE_DB_PASSWORD=oracle_pass
SOURCE_DB_SERVICE_NAME=PRODPDB

# Target: PostgreSQL database
TARGET_DB_TYPE=postgresql
TARGET_DB_HOST=postgres-analytics.company.com
TARGET_DB_PORT=5432
TARGET_DB_DATABASE=analytics_db
TARGET_DB_USERNAME=postgres_user
TARGET_DB_PASSWORD=postgres_pass
```

The system handles **cross-database reconciliation** automatically!

---

## Database Type Examples

### Oracle

```bash
SOURCE_DB_TYPE=oracle
SOURCE_DB_HOST=oracle-server.company.com
SOURCE_DB_PORT=1521
SOURCE_DB_DATABASE=ORCL
SOURCE_DB_USERNAME=schema_user
SOURCE_DB_PASSWORD=password
SOURCE_DB_SERVICE_NAME=ORCLPDB  # Optional: use service name instead of SID
```

### SQL Server

```bash
SOURCE_DB_TYPE=sqlserver
SOURCE_DB_HOST=sqlserver.company.com
SOURCE_DB_PORT=1433
SOURCE_DB_DATABASE=ProductionDB
SOURCE_DB_USERNAME=sa
SOURCE_DB_PASSWORD=password
```

### PostgreSQL

```bash
SOURCE_DB_TYPE=postgresql
SOURCE_DB_HOST=postgres.company.com
SOURCE_DB_PORT=5432
SOURCE_DB_DATABASE=production_db
SOURCE_DB_USERNAME=postgres
SOURCE_DB_PASSWORD=password
```

### MySQL

```bash
SOURCE_DB_TYPE=mysql
SOURCE_DB_HOST=mysql.company.com
SOURCE_DB_PORT=3306
SOURCE_DB_DATABASE=production_db
SOURCE_DB_USERNAME=root
SOURCE_DB_PASSWORD=password
```

---

## Environment Management

### Development Environment

**`.env.development`:**
```bash
USE_ENV_DB_CONFIGS=true

SOURCE_DB_HOST=dev-db.company.com
SOURCE_DB_USERNAME=dev_user
SOURCE_DB_PASSWORD=dev_password

TARGET_DB_HOST=dev-db.company.com
TARGET_DB_USERNAME=dev_user2
TARGET_DB_PASSWORD=dev_password2
```

### Staging Environment

**`.env.staging`:**
```bash
USE_ENV_DB_CONFIGS=true

SOURCE_DB_HOST=staging-db.company.com
SOURCE_DB_USERNAME=staging_user
SOURCE_DB_PASSWORD=staging_password

TARGET_DB_HOST=staging-db.company.com
TARGET_DB_USERNAME=staging_user2
TARGET_DB_PASSWORD=staging_password2
```

### Production Environment

**`.env.production`:**
```bash
USE_ENV_DB_CONFIGS=true

SOURCE_DB_HOST=prod-db.company.com
SOURCE_DB_USERNAME=prod_readonly_user
SOURCE_DB_PASSWORD=secure_prod_password

TARGET_DB_HOST=prod-db2.company.com
TARGET_DB_USERNAME=prod_readonly_user2
TARGET_DB_PASSWORD=secure_prod_password2
```

**Load different environments:**
```bash
# Development
cp .env.development .env

# Staging
cp .env.staging .env

# Production
cp .env.production .env
```

---

## Security Best Practices

### 1. Never Commit `.env` to Version Control

**.gitignore:**
```
.env
.env.development
.env.staging
.env.production
.env.local
```

✅ **DO** commit: `.env.example`
❌ **DO NOT** commit: `.env`

### 2. Use Read-Only Database Users

```sql
-- Oracle example
CREATE USER reconciliation_readonly IDENTIFIED BY secure_password;
GRANT CONNECT TO reconciliation_readonly;
GRANT SELECT ON schema1.* TO reconciliation_readonly;

-- Revoke write permissions
REVOKE INSERT, UPDATE, DELETE, DROP ON schema1.* FROM reconciliation_readonly;
```

### 3. Use Strong Passwords

✅ **Good passwords:**
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- Generated by password manager
- Example: `K9#mP2$xR7@qL5!w`

❌ **Bad passwords:**
- `password123`
- `admin`
- `company_name`

### 4. Rotate Credentials Regularly

Schedule regular password rotations:
- Development: Every 90 days
- Staging: Every 60 days
- Production: Every 30-45 days

### 5. Use Secrets Management Systems

For production environments, consider:
- **AWS Secrets Manager**
- **Azure Key Vault**
- **HashiCorp Vault**
- **Google Secret Manager**

Example with AWS Secrets Manager:
```python
import boto3
import json
import os

def load_db_credentials():
    """Load database credentials from AWS Secrets Manager."""
    client = boto3.client('secretsmanager')

    # Get source DB credentials
    source_secret = client.get_secret_value(SecretId='reconciliation/source-db')
    source_creds = json.loads(source_secret['SecretString'])

    # Set environment variables
    os.environ['SOURCE_DB_USERNAME'] = source_creds['username']
    os.environ['SOURCE_DB_PASSWORD'] = source_creds['password']

    # Get target DB credentials
    target_secret = client.get_secret_value(SecretId='reconciliation/target-db')
    target_creds = json.loads(target_secret['SecretString'])

    os.environ['TARGET_DB_USERNAME'] = target_creds['username']
    os.environ['TARGET_DB_PASSWORD'] = target_creds['password']

# Load credentials before starting the app
load_db_credentials()
```

### 6. Limit Network Access

Configure firewall rules to restrict database access:
```bash
# Only allow specific IP addresses
# iptables example
iptables -A INPUT -p tcp --dport 1521 -s 10.0.1.100 -j ACCEPT
iptables -A INPUT -p tcp --dport 1521 -j DROP
```

### 7. Enable Database Audit Logging

Monitor database access:
```sql
-- Oracle example
AUDIT SELECT ON schema1.sensitive_table BY ACCESS;
AUDIT INSERT, UPDATE, DELETE ON schema1.* BY ACCESS;
```

---

## Verification

### Check Configuration

**1. Verify environment variables are loaded:**
```python
import os
print("SOURCE_DB_USERNAME:", os.getenv('SOURCE_DB_USERNAME'))
print("TARGET_DB_USERNAME:", os.getenv('TARGET_DB_USERNAME'))
print("USE_ENV_DB_CONFIGS:", os.getenv('USE_ENV_DB_CONFIGS'))
```

**2. Test API with environment configs:**
```bash
curl -X POST http://localhost:8000/reconciliation/execute \
  -H "Content-Type: application/json" \
  -d '{"ruleset_id":"RECON_ABC123","limit":10}'
```

**3. Check logs:**
```
INFO: Attempting to use database configs from environment variables
INFO: Using database configurations from environment variables
```

---

## Troubleshooting

### Issue: "Database connections not provided"

**Cause:** Environment credentials are not configured or `USE_ENV_DB_CONFIGS=false`

**Solution:**
```bash
# 1. Check .env file exists
ls .env

# 2. Check credentials are set
cat .env | grep DB_USERNAME

# 3. Ensure USE_ENV_DB_CONFIGS=true
echo "USE_ENV_DB_CONFIGS=true" >> .env

# 4. Restart server
python -m uvicorn kg_builder.main:app --reload
```

### Issue: "Partial database configuration found"

**Cause:** Only source OR target credentials are configured (need both)

**Solution:**
```bash
# Ensure BOTH source and target credentials are set
SOURCE_DB_USERNAME=user1
SOURCE_DB_PASSWORD=pass1
TARGET_DB_USERNAME=user2
TARGET_DB_PASSWORD=pass2
```

### Issue: "Failed to connect to database"

**Cause:** Invalid credentials or network issues

**Solution:**
```bash
# 1. Verify credentials work manually
sqlplus username/password@host:port/service

# 2. Check network connectivity
ping db-server.company.com
telnet db-server.company.com 1521

# 3. Verify firewall rules allow connection
# 4. Check database is running and accessible
```

### Issue: Payload configs not working

**Cause:** Environment configs might be overriding

**Solution:**
```bash
# Payload configs ALWAYS take priority
# If they're not working, check for:
# 1. Syntax errors in payload
# 2. Missing required fields
# 3. Server logs for errors
```

---

## Comparison: Payload vs Environment

| Aspect | Payload Configs | Environment Configs |
|--------|----------------|---------------------|
| **Security** | ❌ Credentials in requests | ✅ No credentials exposed |
| **Logging** | ❌ May appear in logs | ✅ Not in logs |
| **Setup** | ❌ Per-request config | ✅ One-time setup |
| **Flexibility** | ✅ Different per request | ❌ Fixed per environment |
| **Testing** | ✅ Easy to test different DBs | ❌ Requires env changes |
| **Production** | ❌ Not recommended | ✅ Recommended |
| **Development** | ✅ Good for ad-hoc testing | ✅ Good for regular use |

**Recommendation:**
- **Development:** Use payload configs for ad-hoc testing
- **Production:** Use environment configs for regular operations

---

## Migration Guide

### From Payload Configs to Environment Configs

**Before:**
```python
# Every request includes credentials
response = requests.post(
    "http://localhost:8000/reconciliation/execute",
    json={
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
    }
)
```

**After:**

1. **Create `.env` file:**
```bash
USE_ENV_DB_CONFIGS=true
SOURCE_DB_TYPE=oracle
SOURCE_DB_HOST=localhost
SOURCE_DB_PORT=1521
SOURCE_DB_DATABASE=ORCL
SOURCE_DB_USERNAME=user1
SOURCE_DB_PASSWORD=pass1
TARGET_DB_TYPE=oracle
TARGET_DB_HOST=localhost
TARGET_DB_PORT=1521
TARGET_DB_DATABASE=ORCL
TARGET_DB_USERNAME=user2
TARGET_DB_PASSWORD=pass2
```

2. **Simplify API requests:**
```python
# No credentials in request!
response = requests.post(
    "http://localhost:8000/reconciliation/execute",
    json={
        "ruleset_id": "RECON_ABC123",
        "limit": 100
    }
)
```

3. **Benefits:**
   - ✅ Cleaner code
   - ✅ No credentials in source control
   - ✅ Easier environment management
   - ✅ Better security

---

## API Behavior

### Reconciliation Execution (`/reconciliation/execute`)

**With environment configs:**
```bash
curl -X POST http://localhost:8000/reconciliation/execute \
  -d '{"ruleset_id":"RECON_ABC123","limit":100}'

# Response: Direct execution with DB connections
{
  "success": true,
  "matched_count": 87,
  "unmatched_source_count": 13,
  "unmatched_target_count": 5,
  "execution_time_ms": 1234.56
}
```

**Without configs:**
```bash
# Response: SQL export mode
{
  "success": true,
  "mode": "sql_export",
  "sql": "-- SQL queries here",
  "instructions": [...]
}
```

### Rule Validation (`/reconciliation/validate`)

Same behavior - uses environment configs if available, otherwise returns basic validation.

---

## Summary

✅ **Configure database credentials in `.env` file**
✅ **No credentials in API requests**
✅ **Better security and environment management**
✅ **Payload configs still work as overrides**
✅ **Backward compatible with existing code**

For more information, see:
- [Reconciliation Execution Guide](RECONCILIATION_EXECUTION_GUIDE.md)
- [Quick Start](../RECONCILIATION_QUICKSTART.md)
- [.env.example](../.env.example)

---

**Questions?** Check the API documentation at http://localhost:8000/docs
