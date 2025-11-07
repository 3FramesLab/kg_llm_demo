# KPI Database Syntax Issue Fix ✅

## 🚨 **Error Encountered**

```
Msg 156, Level 15, State 1, Line 121
Incorrect syntax near the keyword 'AS'.
```

**Location**: Line 121 in `kpi_execution_results` table creation

---

## 🔍 **Root Cause Analysis**

### **Problematic Code** (Line 121):
```sql
-- INCORRECT SYNTAX
execution_date DATE AS (CAST(execution_timestamp AS DATE)) PERSISTED,
execution_hour TINYINT AS (DATEPART(HOUR, execution_timestamp)) PERSISTED,
```

### **Issue Explanation**:
- **Computed columns** cannot be defined inline during `CREATE TABLE` with this syntax
- **SQL Server** requires computed columns to be added **after** table creation
- **Parentheses** around the computed expression are optional but the syntax was malformed

---

## ✅ **Solution Applied**

### **Fixed Approach**:
1. **Create table** without computed columns first
2. **Add computed columns** using `ALTER TABLE` statements
3. **Use correct syntax** for computed column definitions

### **Corrected Code**:
```sql
-- STEP 1: Create table without computed columns
CREATE TABLE kpi_execution_results (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    kpi_id BIGINT NOT NULL,
    execution_timestamp DATETIME2 DEFAULT GETDATE(),
    -- ... other columns ...
    
    -- Remove computed columns from CREATE TABLE
    -- execution_date DATE AS (CAST(execution_timestamp AS DATE)) PERSISTED,  -- REMOVED
    -- execution_hour TINYINT AS (DATEPART(HOUR, execution_timestamp)) PERSISTED,  -- REMOVED
    
    CONSTRAINT FK_kpi_execution_results_kpi_id 
        FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id) ON DELETE CASCADE
);

-- STEP 2: Add computed columns after table creation
ALTER TABLE kpi_execution_results 
ADD execution_date AS CAST(execution_timestamp AS DATE) PERSISTED;

ALTER TABLE kpi_execution_results 
ADD execution_hour AS DATEPART(HOUR, execution_timestamp) PERSISTED;
```

---

## 📁 **Fixed Files Created**

### **New Fixed Script**: `scripts/create_kpi_database_separate_fixed.sql`

#### **Key Changes**:
1. ✅ **Separated computed column creation** from table creation
2. ✅ **Used ALTER TABLE** to add computed columns
3. ✅ **Removed parentheses** around computed expressions
4. ✅ **Added verification queries** to test computed columns
5. ✅ **Added test data** to validate functionality

#### **Verification Included**:
```sql
-- Test computed columns
SELECT 
    execution_date,
    execution_hour,
    COUNT(*) as executions_count
FROM kpi_execution_results
GROUP BY execution_date, execution_hour
ORDER BY execution_date DESC, execution_hour DESC;
```

---

## 🚀 **How to Use Fixed Script**

### **Method 1: SQL Server Management Studio (SSMS)**
1. **Open SSMS** and connect to your SQL Server
2. **Open new query window**
3. **Copy entire content** from `scripts/create_kpi_database_separate_fixed.sql`
4. **Execute the script** (F5)

### **Method 2: Command Line**
```bash
# Navigate to project directory
cd d:\learning\dq-poc

# Execute fixed script
sqlcmd -S localhost -E -i scripts/create_kpi_database_separate_fixed.sql
```

### **Method 3: PowerShell**
```powershell
# Navigate to project directory
cd "d:\learning\dq-poc"

# Execute fixed script
Invoke-Sqlcmd -ServerInstance "localhost" -InputFile "scripts/create_kpi_database_separate_fixed.sql"
```

---

## ✅ **Expected Output**

### **Success Messages**:
```
=== Creating Separate KPI Database (Fixed Version) ===
✓ Created KPI_Analytics database
Switched to KPI_Analytics database
Creating KPI tables with analytics optimization...
✓ Created kpi_definitions and kpi_execution_results tables
Adding computed columns for analytics optimization...
✓ Added computed columns for analytics optimization
Creating analytics-optimized indexes...
✓ Created analytics-optimized indexes
Creating analytics views...
✓ Created vw_kpi_latest_execution view
✓ Created vw_kpi_daily_summary view
Inserting sample KPI definitions...
✓ Inserted sample KPI definitions
Inserting test execution data...
✓ Inserted test execution data

=== KPI Analytics Database Verification ===
Database: KPI_Analytics
Tables: kpi_definitions, kpi_execution_results (with computed columns)
Views: vw_kpi_latest_execution, vw_kpi_daily_summary
Indexes: Analytics-optimized for time-series queries
Sample Data: 4 sample KPI definitions + 1 test execution
Computed Columns: execution_date, execution_hour (FIXED)
```

---

## 🔧 **Additional Troubleshooting**

### **If You Still Get Errors**:

#### **Error: File Path Not Found**
```sql
-- Update file paths in the script to match your SQL Server installation
-- Find your data directory:
SELECT 
    name,
    physical_name
FROM sys.master_files 
WHERE database_id = DB_ID('master');

-- Common paths:
-- SQL Server 2019: MSSQL15.MSSQLSERVER
-- SQL Server 2017: MSSQL14.MSSQLSERVER
-- SQL Server Express: MSSQL15.SQLEXPRESS
```

#### **Error: Permission Denied**
```sql
-- Run as administrator or use sysadmin account
-- Or create database manually first:
CREATE DATABASE [KPI_Analytics];
USE [KPI_Analytics];
-- Then run the rest of the script
```

#### **Error: Database Already Exists**
```sql
-- If you need to recreate:
USE master;
DROP DATABASE IF EXISTS KPI_Analytics;
-- Then run the fixed script
```

---

## 🎯 **Verification Steps**

### **Step 1: Check Database Creation**
```sql
SELECT name, create_date FROM sys.databases WHERE name = 'KPI_Analytics';
```

### **Step 2: Check Tables and Computed Columns**
```sql
USE KPI_Analytics;

-- Check tables
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES ORDER BY TABLE_NAME;

-- Check computed columns
SELECT 
    COLUMN_NAME, 
    DATA_TYPE, 
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'kpi_execution_results' 
    AND COLUMN_NAME IN ('execution_date', 'execution_hour');
```

### **Step 3: Test Computed Columns**
```sql
-- Insert test data and verify computed columns work
INSERT INTO kpi_execution_results (kpi_id, kg_name, select_schema, execution_timestamp)
VALUES (1, 'test', 'test', GETDATE());

-- Check computed columns
SELECT 
    execution_timestamp,
    execution_date,
    execution_hour
FROM kpi_execution_results 
WHERE kpi_id = 1;
```

The fixed script resolves the computed column syntax issue and provides a robust KPI Analytics database with proper error handling and verification steps.
