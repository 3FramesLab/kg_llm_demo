-- =====================================================
-- Create KPI Tables in MS SQL Server
-- Migrates kpi_execution_results from SQLite to MS SQL Server
-- =====================================================

USE [NewDQ];
GO

PRINT '=== Creating KPI Tables in MS SQL Server ===';

-- =====================================================
-- 1. Create kpi_definitions table
-- =====================================================

PRINT 'Creating kpi_definitions table...';

IF OBJECT_ID('kpi_definitions', 'U') IS NOT NULL
    DROP TABLE kpi_definitions;

CREATE TABLE kpi_definitions (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL UNIQUE,
    alias_name NVARCHAR(255) NULL,
    group_name NVARCHAR(255) NULL,
    description NVARCHAR(MAX) NULL,
    nl_definition NVARCHAR(MAX) NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    created_by NVARCHAR(100) NULL,
    is_active BIT DEFAULT 1
);

-- Create indexes for performance
CREATE INDEX idx_kpi_name ON kpi_definitions(name);
CREATE INDEX idx_kpi_active ON kpi_definitions(is_active);
CREATE INDEX idx_kpi_group ON kpi_definitions(group_name);

PRINT '✓ Created kpi_definitions table with indexes';

-- =====================================================
-- 2. Create kpi_execution_results table
-- =====================================================

PRINT 'Creating kpi_execution_results table...';

IF OBJECT_ID('kpi_execution_results', 'U') IS NOT NULL
    DROP TABLE kpi_execution_results;

CREATE TABLE kpi_execution_results (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    kpi_id BIGINT NOT NULL,
    
    -- Execution Parameters
    kg_name NVARCHAR(255) NOT NULL,
    select_schema NVARCHAR(255) NOT NULL,
    ruleset_name NVARCHAR(255) NULL,
    db_type NVARCHAR(50) DEFAULT 'sqlserver',
    limit_records INT DEFAULT 1000,
    use_llm BIT DEFAULT 1,
    excluded_fields NVARCHAR(MAX) NULL, -- JSON array
    
    -- Execution Results
    generated_sql NVARCHAR(MAX) NULL,
    number_of_records INT DEFAULT 0,
    joined_columns NVARCHAR(MAX) NULL, -- JSON array of join column pairs
    sql_query_type NVARCHAR(100) NULL, -- COMPARISON_QUERY, DATA_QUERY, etc.
    operation NVARCHAR(50) NULL, -- NOT_IN, IN, EQUALS, AGGREGATE, etc.
    
    -- Metadata
    execution_status NVARCHAR(50) DEFAULT 'pending',
    execution_timestamp DATETIME2 DEFAULT GETDATE(),
    execution_time_ms FLOAT NULL,
    confidence_score FLOAT NULL,
    error_message NVARCHAR(MAX) NULL,
    
    -- Result Data (JSON format)
    result_data NVARCHAR(MAX) NULL,
    
    -- Table Information
    source_table NVARCHAR(255) NULL,
    target_table NVARCHAR(255) NULL,
    
    -- Evidence Data (JSON format) - NEW: Store evidence data directly
    evidence_data NVARCHAR(MAX) NULL,
    evidence_count INT DEFAULT 0,
    
    -- Additional Metadata
    user_id NVARCHAR(100) NULL,
    session_id NVARCHAR(100) NULL,
    
    -- Foreign Key
    CONSTRAINT FK_kpi_execution_results_kpi_id 
        FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX idx_execution_kpi_id ON kpi_execution_results(kpi_id);
CREATE INDEX idx_execution_timestamp ON kpi_execution_results(execution_timestamp);
CREATE INDEX idx_execution_status ON kpi_execution_results(execution_status);
CREATE INDEX idx_execution_kg_name ON kpi_execution_results(kg_name);
CREATE INDEX idx_execution_schema ON kpi_execution_results(select_schema);

PRINT '✓ Created kpi_execution_results table with indexes and foreign key';

-- =====================================================
-- 3. Create views for easy access
-- =====================================================

PRINT 'Creating helper views...';

-- View for latest execution per KPI
CREATE VIEW vw_kpi_latest_execution AS
SELECT 
    k.id as kpi_id,
    k.name as kpi_name,
    k.alias_name,
    k.group_name,
    k.description,
    k.is_active,
    e.id as execution_id,
    e.execution_timestamp,
    e.execution_status,
    e.generated_sql,
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

PRINT '✓ Created vw_kpi_latest_execution view';

-- View for execution summary
CREATE VIEW vw_kpi_execution_summary AS
SELECT 
    k.id as kpi_id,
    k.name as kpi_name,
    k.alias_name,
    k.group_name,
    COUNT(e.id) as total_executions,
    MAX(e.execution_timestamp) as last_execution,
    AVG(e.execution_time_ms) as avg_execution_time_ms,
    SUM(CASE WHEN e.execution_status = 'success' THEN 1 ELSE 0 END) as successful_executions,
    SUM(CASE WHEN e.execution_status = 'error' THEN 1 ELSE 0 END) as failed_executions
FROM kpi_definitions k
LEFT JOIN kpi_execution_results e ON k.id = e.kpi_id
WHERE k.is_active = 1
GROUP BY k.id, k.name, k.alias_name, k.group_name;

PRINT '✓ Created vw_kpi_execution_summary view';

-- =====================================================
-- 4. Insert sample data for testing
-- =====================================================

PRINT 'Inserting sample KPI definitions...';

INSERT INTO kpi_definitions (name, alias_name, group_name, description, nl_definition, created_by)
VALUES 
    ('Product Match Rate', 'PMR', 'Data Quality', 'Percentage of products that match between RBP and OPS', 'Show me the match rate between RBP GPU and OPS Excel GPU', 'system'),
    ('Missing Products in OPS', 'Missing OPS', 'Data Quality', 'Products in RBP but missing in OPS', 'Show me products in RBP GPU that are missing in OPS Excel GPU', 'system'),
    ('Orphaned OPS Products', 'Orphaned OPS', 'Data Quality', 'Products in OPS but not in RBP', 'Show me products in OPS Excel GPU that are not in RBP GPU', 'system');

PRINT '✓ Inserted sample KPI definitions';

PRINT '';
PRINT '=== MS SQL Server KPI Tables Creation Complete ===';
PRINT 'Tables Created:';
PRINT '- kpi_definitions (with indexes)';
PRINT '- kpi_execution_results (with indexes and foreign key)';
PRINT 'Views Created:';
PRINT '- vw_kpi_latest_execution';
PRINT '- vw_kpi_execution_summary';
PRINT 'Sample Data: 3 sample KPI definitions inserted';
PRINT '';
