-- =====================================================
-- Create Separate KPI Database in MS SQL Server
-- Dedicated database for KPI definitions and execution results
-- =====================================================

-- =====================================================
-- 1. Create KPI Database
-- =====================================================

PRINT '=== Creating Separate KPI Database ===';

-- Create the database
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'KPI_Analytics')
BEGIN
    CREATE DATABASE [KPI_Analytics]
    ON 
    ( NAME = 'KPI_Analytics_Data',
      FILENAME = 'C:\Program Files\Microsoft SQL Server\MSSQL15.MSSQLSERVER\MSSQL\DATA\KPI_Analytics.mdf',
      SIZE = 100MB,
      MAXSIZE = 10GB,
      FILEGROWTH = 10MB )
    LOG ON 
    ( NAME = 'KPI_Analytics_Log',
      FILENAME = 'C:\Program Files\Microsoft SQL Server\MSSQL15.MSSQLSERVER\MSSQL\DATA\KPI_Analytics.ldf',
      SIZE = 10MB,
      MAXSIZE = 1GB,
      FILEGROWTH = 10% );
    
    PRINT '✓ Created KPI_Analytics database';
END
ELSE
BEGIN
    PRINT '✓ KPI_Analytics database already exists';
END

-- Switch to KPI database
USE [KPI_Analytics];
GO

PRINT 'Switched to KPI_Analytics database';

-- =====================================================
-- 2. Create KPI Tables with Analytics Optimization
-- =====================================================

PRINT 'Creating KPI tables with analytics optimization...';

-- KPI Definitions Table
IF OBJECT_ID('kpi_definitions', 'U') IS NOT NULL
    DROP TABLE kpi_definitions;

CREATE TABLE kpi_definitions (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL UNIQUE,
    alias_name NVARCHAR(255) NULL,
    group_name NVARCHAR(255) NULL,
    description NVARCHAR(MAX) NULL,
    nl_definition NVARCHAR(MAX) NOT NULL,
    
    -- Metadata
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    created_by NVARCHAR(100) NULL,
    is_active BIT DEFAULT 1,
    
    -- Analytics specific fields
    execution_frequency NVARCHAR(50) DEFAULT 'on_demand', -- daily, hourly, on_demand
    target_sla_seconds INT DEFAULT 30,
    business_priority NVARCHAR(20) DEFAULT 'medium', -- high, medium, low
    data_retention_days INT DEFAULT 90
);

-- KPI Execution Results Table (Optimized for Analytics)
IF OBJECT_ID('kpi_execution_results', 'U') IS NOT NULL
    DROP TABLE kpi_execution_results;

CREATE TABLE kpi_execution_results (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    kpi_id BIGINT NOT NULL,
    
    -- Execution Context
    kg_name NVARCHAR(255) NOT NULL,
    select_schema NVARCHAR(255) NOT NULL,
    ruleset_name NVARCHAR(255) NULL,
    db_type NVARCHAR(50) DEFAULT 'sqlserver',
    limit_records INT DEFAULT 1000,
    use_llm BIT DEFAULT 1,
    excluded_fields NVARCHAR(MAX) NULL,
    
    -- SQL and Results
    generated_sql NVARCHAR(MAX) NULL,
    enhanced_sql NVARCHAR(MAX) NULL, -- SQL with ops_planner enhancement
    number_of_records INT DEFAULT 0,
    joined_columns NVARCHAR(MAX) NULL, -- JSON
    sql_query_type NVARCHAR(100) NULL,
    operation NVARCHAR(50) NULL,
    
    -- Execution Metrics
    execution_status NVARCHAR(50) DEFAULT 'pending',
    execution_timestamp DATETIME2 DEFAULT GETDATE(),
    execution_time_ms FLOAT NULL,
    confidence_score FLOAT NULL,
    error_message NVARCHAR(MAX) NULL,
    
    -- Data Storage (JSON format for flexibility)
    result_data NVARCHAR(MAX) NULL,
    evidence_data NVARCHAR(MAX) NULL,
    evidence_count INT DEFAULT 0,
    
    -- Table Metadata
    source_table NVARCHAR(255) NULL,
    target_table NVARCHAR(255) NULL,
    
    -- Session Information
    user_id NVARCHAR(100) NULL,
    session_id NVARCHAR(100) NULL,
    client_ip NVARCHAR(45) NULL,
    user_agent NVARCHAR(500) NULL,
    
    -- Analytics Fields
    execution_date DATE AS (CAST(execution_timestamp AS DATE)) PERSISTED,
    execution_hour TINYINT AS (DATEPART(HOUR, execution_timestamp)) PERSISTED,
    
    -- Foreign Key
    CONSTRAINT FK_kpi_execution_results_kpi_id 
        FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id) ON DELETE CASCADE
);

PRINT '✓ Created kpi_definitions and kpi_execution_results tables';

-- =====================================================
-- 3. Create Analytics-Optimized Indexes
-- =====================================================

PRINT 'Creating analytics-optimized indexes...';

-- KPI Definitions Indexes
CREATE INDEX idx_kpi_name ON kpi_definitions(name);
CREATE INDEX idx_kpi_active ON kpi_definitions(is_active);
CREATE INDEX idx_kpi_group ON kpi_definitions(group_name);
CREATE INDEX idx_kpi_priority ON kpi_definitions(business_priority);

-- KPI Execution Results Indexes (Time-series optimized)
CREATE INDEX idx_execution_kpi_id ON kpi_execution_results(kpi_id);
CREATE INDEX idx_execution_timestamp ON kpi_execution_results(execution_timestamp DESC);
CREATE INDEX idx_execution_date ON kpi_execution_results(execution_date DESC);
CREATE INDEX idx_execution_status ON kpi_execution_results(execution_status);
CREATE INDEX idx_execution_kg_schema ON kpi_execution_results(kg_name, select_schema);

-- Composite indexes for common queries
CREATE INDEX idx_kpi_execution_composite ON kpi_execution_results(kpi_id, execution_timestamp DESC);
CREATE INDEX idx_execution_date_status ON kpi_execution_results(execution_date, execution_status);
CREATE INDEX idx_execution_user_date ON kpi_execution_results(user_id, execution_date DESC);

PRINT '✓ Created analytics-optimized indexes';

-- =====================================================
-- 4. Create Analytics Views
-- =====================================================

PRINT 'Creating analytics views...';

-- Latest execution per KPI
CREATE VIEW vw_kpi_latest_execution AS
SELECT 
    k.id as kpi_id,
    k.name as kpi_name,
    k.alias_name,
    k.group_name,
    k.business_priority,
    k.is_active,
    e.id as execution_id,
    e.execution_timestamp,
    e.execution_status,
    e.generated_sql,
    e.enhanced_sql,
    e.number_of_records,
    e.execution_time_ms,
    e.confidence_score,
    e.error_message,
    e.evidence_count
FROM kpi_definitions k
LEFT JOIN kpi_execution_results e ON k.id = e.kpi_id
    AND e.execution_timestamp = (
        SELECT MAX(execution_timestamp) 
        FROM kpi_execution_results 
        WHERE kpi_id = k.id
    )
WHERE k.is_active = 1;

-- Daily execution summary
CREATE VIEW vw_kpi_daily_summary AS
SELECT 
    k.name as kpi_name,
    k.alias_name,
    k.group_name,
    e.execution_date,
    COUNT(e.id) as total_executions,
    SUM(CASE WHEN e.execution_status = 'success' THEN 1 ELSE 0 END) as successful_executions,
    SUM(CASE WHEN e.execution_status = 'error' THEN 1 ELSE 0 END) as failed_executions,
    AVG(e.execution_time_ms) as avg_execution_time_ms,
    AVG(e.number_of_records) as avg_record_count,
    AVG(e.confidence_score) as avg_confidence_score
FROM kpi_definitions k
JOIN kpi_execution_results e ON k.id = e.kpi_id
WHERE k.is_active = 1
GROUP BY k.name, k.alias_name, k.group_name, e.execution_date;

PRINT '✓ Created analytics views';

-- =====================================================
-- 5. Insert Sample Data
-- =====================================================

PRINT 'Inserting sample KPI definitions...';

INSERT INTO kpi_definitions (name, alias_name, group_name, description, nl_definition, created_by, business_priority, target_sla_seconds)
VALUES 
    ('Product Match Rate', 'PMR', 'Data Quality', 'Percentage of products that match between RBP and OPS', 'Show me the match rate between RBP GPU and OPS Excel GPU', 'system', 'high', 15),
    ('Missing Products in OPS', 'Missing OPS', 'Data Quality', 'Products in RBP but missing in OPS', 'Show me products in RBP GPU that are missing in OPS Excel GPU', 'system', 'high', 20),
    ('Orphaned OPS Products', 'Orphaned OPS', 'Data Quality', 'Products in OPS but not in RBP', 'Show me products in OPS Excel GPU that are not in RBP GPU', 'system', 'medium', 25),
    ('NBU Product Coverage', 'NBU Coverage', 'Data Quality', 'NBU product coverage between systems', 'Show me NBU products coverage between RBP and OPS', 'system', 'medium', 30);

PRINT '✓ Inserted sample KPI definitions';

PRINT '';
PRINT '=== KPI Analytics Database Creation Complete ===';
PRINT 'Database: KPI_Analytics';
PRINT 'Tables: kpi_definitions, kpi_execution_results';
PRINT 'Views: vw_kpi_latest_execution, vw_kpi_daily_summary';
PRINT 'Indexes: Analytics-optimized for time-series queries';
PRINT 'Sample Data: 4 sample KPI definitions';
PRINT '';
