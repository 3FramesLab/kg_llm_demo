# 📊 Comprehensive KPI Database Setup Guide

## 🎯 Overview

This script creates a complete KPI Analytics database with all necessary tables, views, triggers, and stored procedures for a full-featured KPI management system.

## 🗄️ Database Structure

### **Core Tables:**
1. **`kpi_definitions`** - KPI metadata and configuration
2. **`kpi_execution_results`** - Execution history and results
3. **`kpi_schedules`** - Scheduling configuration
4. **`kpi_schedule_executions`** - Schedule execution tracking
5. **`kpi_alerts`** - Alert configuration
6. **`kpi_alert_history`** - Alert firing history
7. **`kpi_audit_log`** - Change tracking and audit trail
8. **`kpi_configuration`** - System configuration

### **Views:**
- **`vw_kpi_dashboard`** - Dashboard summary data
- **`vw_kpi_performance`** - Performance analytics

### **Stored Procedures:**
- **`sp_cleanup_old_executions`** - Cleanup old execution data
- **`sp_get_kpi_health_status`** - Health status reporting

## 🚀 Installation Instructions

### **Step 1: Run the Script**
```bash
# Using sqlcmd (Windows/Linux)
sqlcmd -S your_server_name -d master -i create_comprehensive_kpi_database.sql

# Using SQL Server Management Studio
# 1. Open SSMS
# 2. Connect to your SQL Server instance
# 3. Open the script file
# 4. Execute (F5)
```

### **Step 2: Verify Installation**
```sql
USE KPI_Analytics;

-- Check all tables were created
SELECT TABLE_NAME, 
       (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = t.TABLE_NAME) as COLUMN_COUNT
FROM INFORMATION_SCHEMA.TABLES t
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

-- Verify sample data
SELECT COUNT(*) as KPI_COUNT FROM kpi_definitions;
SELECT COUNT(*) as CONFIG_COUNT FROM kpi_configuration;
```

### **Step 3: Configure Application**
Update your application configuration:

```python
# Environment variables
KPI_DB_HOST=your_sql_server
KPI_DB_PORT=1433
KPI_DB_DATABASE=KPI_Analytics
KPI_DB_USERNAME=your_username
KPI_DB_PASSWORD=your_password
```

## 📋 Key Features

### **✅ Complete KPI Lifecycle Management**
- KPI definition and metadata storage
- Execution tracking with detailed metrics
- Performance monitoring and analytics
- Automated scheduling with cron expressions
- Alert configuration and notification history

### **✅ Advanced Features**
- **SQL Caching**: Store and reuse generated SQL
- **Audit Logging**: Track all changes automatically
- **Performance Metrics**: Detailed execution analytics
- **Health Monitoring**: Built-in health status checks
- **Data Retention**: Configurable cleanup procedures

### **✅ Enterprise Ready**
- **Scalable Design**: Optimized indexes and constraints
- **Data Integrity**: Foreign key relationships and validation
- **Security**: Audit trails and user tracking
- **Maintenance**: Automated cleanup procedures
- **Monitoring**: Performance views and health checks

## 🔧 Configuration Options

The system includes default configuration values that can be customized:

| Configuration Key | Default | Description |
|------------------|---------|-------------|
| `default_execution_timeout` | 300 | Execution timeout (seconds) |
| `max_concurrent_executions` | 10 | Max concurrent executions |
| `cleanup_retention_days` | 90 | Data retention period |
| `default_confidence_threshold` | 0.7 | LLM confidence threshold |
| `enable_sql_caching` | true | Enable SQL caching |

## 📊 Sample Usage

### **Create a KPI:**
```sql
INSERT INTO kpi_definitions (
    name, group_name, description, nl_definition,
    created_by, business_priority, warning_threshold, critical_threshold
) VALUES (
    'Customer Satisfaction Rate',
    'Customer Experience',
    'Percentage of satisfied customers based on survey responses',
    'Calculate the percentage of customers with satisfaction score >= 4',
    'admin',
    'high',
    80.0,
    70.0
);
```

### **Schedule a KPI:**
```sql
INSERT INTO kpi_schedules (
    kpi_id, schedule_name, cron_expression, 
    execution_params, created_by
) VALUES (
    1,
    'Daily Customer Satisfaction Check',
    '0 9 * * *',  -- Daily at 9 AM
    '{"limit": 1000, "use_llm": true}',
    'admin'
);
```

### **Monitor Performance:**
```sql
-- Get KPI dashboard data
SELECT * FROM vw_kpi_dashboard;

-- Get performance metrics
SELECT * FROM vw_kpi_performance WHERE kpi_name LIKE '%Customer%';

-- Check health status
EXEC sp_get_kpi_health_status;
```

## 🛠️ Maintenance

### **Regular Cleanup:**
```sql
-- Clean up old execution results (keep last 90 days)
EXEC sp_cleanup_old_executions @retention_days = 90;
```

### **Monitor Database Size:**
```sql
-- Check table sizes
SELECT 
    t.NAME AS TableName,
    s.Name AS SchemaName,
    p.rows AS RowCounts,
    CAST(ROUND(((SUM(a.total_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS TotalSpaceMB
FROM sys.tables t
INNER JOIN sys.indexes i ON t.OBJECT_ID = i.object_id
INNER JOIN sys.partitions p ON i.object_id = p.OBJECT_ID AND i.index_id = p.index_id
INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
GROUP BY t.Name, s.Name, p.Rows
ORDER BY TotalSpaceMB DESC;
```

## 🎉 Success!

Your comprehensive KPI Analytics database is now ready for use with full scheduling, alerting, and monitoring capabilities!
