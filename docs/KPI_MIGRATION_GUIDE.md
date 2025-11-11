# KPI Migration Guide: SQLite to MS SQL Server ✅

## 🎯 **Purpose**

Migrate all existing KPI definitions and execution results from SQLite (`data/landing_kpi.db`) to MS SQL Server (`KPI_Analytics` database) to avoid manual re-entry.

---

## 🛠️ **Migration Script**

**File**: `scripts/migrate_kpis_sqlite_to_mssql.py`

### **Features**:
- ✅ **Migrates KPI definitions** (name, description, natural language definition, etc.)
- ✅ **Migrates execution history** (SQL queries, results, performance metrics)
- ✅ **Handles duplicates** (skips KPIs that already exist in MS SQL Server)
- ✅ **Preserves relationships** (execution results linked to correct KPIs)
- ✅ **Error handling** (continues migration even if some KPIs fail)
- ✅ **Detailed logging** (shows progress and results)

---

## 🚀 **How to Run Migration**

### **1. Test Migration (Dry Run)**
```bash
cd d:\learning\dq-poc
python scripts/migrate_kpis_sqlite_to_mssql.py --dry-run
```

**What it does**:
- Tests database connections
- Shows how many KPIs would be migrated
- Lists all KPIs that would be transferred
- **No actual migration** - safe to run

### **2. Migrate KPI Definitions Only**
```bash
python scripts/migrate_kpis_sqlite_to_mssql.py --skip-executions
```

**What it does**:
- Migrates only KPI definitions (name, description, etc.)
- Skips execution history (faster migration)
- Good for initial setup

### **3. Full Migration (Recommended)**
```bash
python scripts/migrate_kpis_sqlite_to_mssql.py
```

**What it does**:
- Migrates KPI definitions
- Migrates all execution history
- Preserves complete data lineage
- **This is what you want for complete migration**

### **4. Custom Options**
```bash
# Use different SQLite database
python scripts/migrate_kpis_sqlite_to_mssql.py --sqlite-path "path/to/your/kpi.db"

# Use different MS SQL Server
python scripts/migrate_kpis_sqlite_to_mssql.py --mssql-host "your-server" --mssql-database "YourDB"
```

---

## 📊 **Expected Output**

### **Successful Migration**:
```
================================================================================
🚀 STARTING KPI MIGRATION
================================================================================
INFO - KPI Migrator initialized
INFO - Source: SQLite (data/landing_kpi.db)
INFO - Target: MS SQL Server (your-server/KPI_Analytics)
INFO - Testing database connections...
INFO - ✓ SQLite connection successful - 15 KPIs found
INFO - ✓ MS SQL Server connection successful - 4 KPIs currently exist

INFO - Retrieved 15 KPIs from SQLite

📋 Migrating KPI 1/15: 'Product Match Rate'
INFO - ✓ Migrated KPI 'Product Match Rate' -> ID 5
INFO -   📊 Found 3 execution results
INFO - ✓ Migrated 3 execution results

📋 Migrating KPI 2/15: 'Missing Products in OPS'
INFO - KPI 'Missing Products in OPS' already exists with ID 2, skipping...
INFO -   📊 Found 1 execution results
INFO - ✓ Migrated 1 execution results

... (continues for all KPIs)

================================================================================
📊 MIGRATION SUMMARY
================================================================================
INFO - ✅ KPIs migrated: 11
INFO - ⏭️  KPIs skipped (already exist): 4
INFO - 📊 Execution results migrated: 47
INFO - ❌ Errors: 0
INFO - 🎯 Success rate: 100.0%
INFO - 🎉 MIGRATION COMPLETED SUCCESSFULLY!
```

---

## 🔍 **What Gets Migrated**

### **KPI Definitions**:
- ✅ **Name** - KPI name (e.g., "Product Match Rate")
- ✅ **Alias** - Short name (e.g., "PMR")
- ✅ **Group** - Category (e.g., "Data Quality")
- ✅ **Description** - What the KPI measures
- ✅ **Natural Language Definition** - Query in plain English
- ✅ **Metadata** - Created date, updated date, created by
- ✅ **Status** - Active/inactive flag

### **Execution Results**:
- ✅ **SQL Queries** - Generated SQL and enhanced SQL
- ✅ **Results** - Number of records, result data (JSON)
- ✅ **Performance** - Execution time, confidence score
- ✅ **Context** - KG name, schema, parameters used
- ✅ **Status** - Success/failure, error messages
- ✅ **Metadata** - Execution timestamp, user info

---

## 🛡️ **Safety Features**

### **Duplicate Handling**:
- **Checks existing KPIs** by name before inserting
- **Skips duplicates** - won't create duplicate KPIs
- **Links executions** to existing KPIs if already present

### **Error Recovery**:
- **Continues on errors** - one failed KPI won't stop the whole migration
- **Detailed error logging** - shows exactly what failed and why
- **Transaction safety** - each KPI migration is atomic

### **Data Integrity**:
- **Preserves relationships** - execution results linked to correct KPIs
- **Maintains data types** - proper conversion between SQLite and MS SQL Server
- **Validates connections** - tests both databases before starting

---

## 🧪 **Testing the Migration**

### **1. Before Migration**:
```bash
# Check SQLite KPIs
python -c "
import sqlite3
conn = sqlite3.connect('data/landing_kpi.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM kpi_definitions')
print(f'SQLite KPIs: {cursor.fetchone()[0]}')
conn.close()
"

# Check MS SQL Server KPIs
python -c "
from kg_builder.services.landing_kpi_service_mssql import LandingKPIServiceMSSQL
service = LandingKPIServiceMSSQL()
kpis = service.get_all_kpis()
print(f'MS SQL Server KPIs: {len(kpis)}')
"
```

### **2. After Migration**:
```bash
# Verify migration worked
python -c "
from kg_builder.services.landing_kpi_service_mssql import LandingKPIServiceMSSQL
service = LandingKPIServiceMSSQL()
kpis = service.get_all_kpis()
print(f'MS SQL Server KPIs after migration: {len(kpis)}')
for kpi in kpis[:5]:  # Show first 5
    print(f'  - {kpi[\"name\"]} ({kpi[\"group_name\"]})')
"
```

---

## 🚨 **Troubleshooting**

### **Connection Issues**:
```bash
# Test SQLite connection
python -c "import sqlite3; print('SQLite OK' if sqlite3.connect('data/landing_kpi.db') else 'SQLite FAIL')"

# Test MS SQL Server connection
python -c "
from kg_builder.services.landing_kpi_service_mssql import LandingKPIServiceMSSQL
try:
    service = LandingKPIServiceMSSQL()
    service.get_all_kpis()
    print('MS SQL Server OK')
except Exception as e:
    print(f'MS SQL Server FAIL: {e}')
"
```

### **Common Issues**:
1. **SQLite file not found** - Check path: `data/landing_kpi.db`
2. **MS SQL Server connection failed** - Check server is running and accessible
3. **Permission denied** - Ensure database user has INSERT permissions
4. **Duplicate key errors** - Normal, script handles this automatically

---

## 🎉 **After Migration**

### **Verify Everything Works**:
1. **Open Landing KPI page** - `http://localhost:3000/landing-kpi`
2. **Check KPI list loads** - Should show all migrated KPIs
3. **Test KPI execution** - Execute a KPI to verify it works
4. **Check enhanced features** - Verify ops_planner appears in SQL

### **Clean Up (Optional)**:
```bash
# Backup SQLite database
cp data/landing_kpi.db data/landing_kpi_backup.db

# You can now use the new MS SQL Server API exclusively
```

---

## 🎯 **Migration Complete**

After running the migration script, you'll have:

- ✅ **All KPIs** transferred to MS SQL Server
- ✅ **All execution history** preserved
- ✅ **Enhanced features** available (ops_planner, always-visible SQL)
- ✅ **Better performance** with MS SQL Server backend
- ✅ **No manual re-entry** required

**Status**: 🚀 **Ready to migrate your KPIs!**
