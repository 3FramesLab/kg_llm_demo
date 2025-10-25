# Reconciliation Execution UI - Quick Reference

## Screen Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Reconciliation Execution                                        │
│ Execute reconciliation rules and view results                   │
│                                                                 │
│ [SQL Export Mode] [Direct Execution Mode] [Results]            │
│                                                                 │
│ ┌──────────────────────────┐  ┌──────────────────────────┐    │
│ │ Direct Execution Mode    │  │ Request Payload          │    │
│ │                          │  │ {                        │    │
│ │ Ruleset: [Select ▼]      │  │   "ruleset_id": "...",   │    │
│ │ Limit: [1000]            │  │   "limit": 1000,         │    │
│ │                          │  │   "include_matched": ... │    │
│ │ Execution Options        │  │ }                        │    │
│ │ ☑ Include Matched        │  │                          │    │
│ │ ☑ Include Unmatched      │  │ Response Placeholder     │    │
│ │ ☑ Store in MongoDB       │  │ {                        │    │
│ │                          │  │   "success": true,       │    │
│ │ ▼ Source DB Config       │  │   "matched_count": ...   │    │
│ │   DB Type: [Oracle ▼]    │  │ }                        │    │
│ │   Host: [localhost]      │  │                          │    │
│ │   Port: [1521]           │  │                          │    │
│ │   Database: [ORCL]       │  │                          │    │
│ │   Username: []           │  │                          │    │
│ │   Password: [••••]       │  │                          │    │
│ │   Service Name: []       │  │                          │    │
│ │                          │  │                          │    │
│ │ ▼ Target DB Config       │  │                          │    │
│ │   (Same as Source)       │  │                          │    │
│ │                          │  │                          │    │
│ │ [Execute Reconciliation] │  │                          │    │
│ └──────────────────────────┘  └──────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## How to Use

### Step 1: Select Ruleset
1. Click "Ruleset" dropdown
2. Choose a ruleset from the list
3. Shows rule count for each ruleset

### Step 2: Configure Execution Options
1. **Include Matched Records** - Check to include matched records
2. **Include Unmatched Records** - Check to include unmatched records
3. **Store Results in MongoDB** - Check to persist results

### Step 3: Configure Source Database
1. Select **Database Type** (Oracle, SQL Server, PostgreSQL, MySQL)
2. Enter **Host** (e.g., localhost, 192.168.1.100)
3. Enter **Port** (e.g., 1521 for Oracle)
4. Enter **Database** name (e.g., ORCL)
5. Enter **Username**
6. Enter **Password**
7. If Oracle: Enter **Service Name** (e.g., ORCLPDB)

### Step 4: Configure Target Database
1. Repeat Step 3 for target database
2. Can use different database type than source

### Step 5: Execute
1. Click **Execute Reconciliation** button
2. Wait for execution to complete
3. View results in **Results** tab

---

## Database Type Configuration

### Oracle
```
Database Type: Oracle
Host: localhost
Port: 1521
Database: ORCL
Username: scott
Password: tiger
Service Name: ORCLPDB (optional)
```

### SQL Server
```
Database Type: SQL Server
Host: localhost
Port: 1433
Database: master
Username: sa
Password: password
Service Name: (not used)
```

### PostgreSQL
```
Database Type: PostgreSQL
Host: localhost
Port: 5432
Database: postgres
Username: postgres
Password: password
Service Name: (not used)
```

### MySQL
```
Database Type: MySQL
Host: localhost
Port: 3306
Database: mysql
Username: root
Password: password
Service Name: (not used)
```

---

## Execution Options Explained

| Option | Default | Purpose |
|--------|---------|---------|
| **Include Matched Records** | ✅ | Include records found in both source and target |
| **Include Unmatched Records** | ✅ | Include records found in only source or only target |
| **Store Results in MongoDB** | ✅ | Automatically save results to MongoDB for later retrieval |

### When to Uncheck

- **Uncheck "Include Matched"** - Only want to see discrepancies
- **Uncheck "Include Unmatched"** - Only want to see successful matches
- **Uncheck "Store in MongoDB"** - Don't need to persist results (faster execution)

---

## Request Payload Example

```json
{
  "ruleset_id": "RECON_ABC123",
  "limit": 1000,
  "include_matched": true,
  "include_unmatched": true,
  "store_in_mongodb": true,
  "source_db_config": {
    "db_type": "oracle",
    "host": "source-db.example.com",
    "port": 1521,
    "database": "ORCL",
    "username": "source_user",
    "password": "source_pass",
    "service_name": "ORCLPDB"
  },
  "target_db_config": {
    "db_type": "oracle",
    "host": "target-db.example.com",
    "port": 1521,
    "database": "ORCL",
    "username": "target_user",
    "password": "target_pass",
    "service_name": "ORCLPDB"
  }
}
```

---

## Response Example

```json
{
  "success": true,
  "mode": "direct_execution",
  "ruleset_id": "RECON_ABC123",
  "matched_count": 1247,
  "unmatched_source_count": 53,
  "unmatched_target_count": 28,
  "execution_time_ms": 2500,
  "mongodb_document_id": "507f1f77bcf86cd799439011",
  "storage_location": "mongodb",
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

## Results Tab

After execution, click **Results** tab to see:

1. **Execution Summary**
   - Mode (sql_export or direct_execution)
   - Matched count
   - Unmatched source count
   - Unmatched target count
   - Match rate percentage

2. **Results Table** (for direct execution)
   - Rule ID
   - Matched records count
   - Unmatched source count
   - Unmatched target count
   - Match rate percentage

3. **SQL Queries** (for SQL export mode)
   - Matched query
   - Unmatched source query
   - Unmatched target query

---

## Troubleshooting

### Connection Failed
- Verify host and port are correct
- Check username and password
- Ensure database is running and accessible
- For Oracle: Verify service name is correct

### No Results
- Check if ruleset has rules
- Verify limit is not too low
- Check if include_matched/include_unmatched are enabled
- Review error message in alert

### MongoDB Storage Failed
- Verify MongoDB is running
- Check MongoDB connection configuration
- Results will still be returned even if storage fails

---

## Tips & Tricks

1. **Test Connection** - Use SQL Export mode first to verify queries
2. **Start Small** - Use limit=100 for initial testing
3. **Check Both** - Enable both matched and unmatched for full picture
4. **Save Results** - Enable MongoDB storage for historical tracking
5. **Different DBs** - Source and target can be different database types


