-- ============================================================================
-- RECREATE kpi_execution_results table with correct structure
-- This script backs up existing data and recreates the table
-- ============================================================================

USE KPI_Analytics;
GO

PRINT '🔄 RECREATING kpi_execution_results table with correct structure';
PRINT '============================================================================';

-- Step 1: Check if table exists and backup data
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'kpi_execution_results')
BEGIN
    PRINT '📋 Backing up existing data...';
    
    -- Create backup table
    SELECT * 
    INTO kpi_execution_results_backup
    FROM kpi_execution_results;
    
    DECLARE @backup_count INT;
    SELECT @backup_count = COUNT(*) FROM kpi_execution_results_backup;
    PRINT '✅ Backed up ' + CAST(@backup_count AS VARCHAR) + ' records to kpi_execution_results_backup';
    
    -- Drop the existing table
    DROP TABLE kpi_execution_results;
    PRINT '✅ Dropped existing table';
END
ELSE
BEGIN
    PRINT '⚠️ Table does not exist - creating new table';
END

-- Step 2: Create the table with correct structure
PRINT '';
PRINT '🔧 Creating kpi_execution_results table with correct structure...';

CREATE TABLE kpi_execution_results (
    -- Primary identification
    id INTEGER PRIMARY KEY IDENTITY(1,1),
    kpi_id INTEGER NOT NULL,
    
    -- Execution metadata
    execution_timestamp DATETIME2 DEFAULT GETDATE(),
    execution_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    execution_type VARCHAR(50) DEFAULT 'manual',
    
    -- REQUIRED: Schema and database context (these were missing!)
    select_schema VARCHAR(255) NOT NULL DEFAULT 'newdqschemanov',
    kg_name VARCHAR(255),
    db_type VARCHAR(50) DEFAULT 'sqlserver',
    schemas TEXT, -- JSON array of schemas
    definitions TEXT, -- JSON array of definitions
    
    -- Execution parameters
    execution_params TEXT,
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    
    -- Additional execution settings
    use_llm BIT DEFAULT 1,
    min_confidence DECIMAL(5,4) DEFAULT 0.7,
    limit_records INTEGER DEFAULT 1000,
    
    -- SQL and query information
    generated_sql TEXT,
    final_sql TEXT,
    sql_generation_time_ms DECIMAL(10,2),
    query_execution_time_ms DECIMAL(10,2),
    
    -- Results and metrics
    number_of_records INTEGER DEFAULT 0,
    result_data TEXT,
    calculated_value DECIMAL(15,6),
    
    -- Performance metrics
    total_execution_time_ms DECIMAL(10,2),
    memory_usage_mb DECIMAL(10,2),
    cpu_usage_percent DECIMAL(5,2),
    
    -- Status and error handling
    confidence_score DECIMAL(5,4),
    error_message TEXT,
    error_type VARCHAR(100),
    retry_count INTEGER DEFAULT 0,
    
    -- Data lineage and traceability
    source_tables VARCHAR(1000),
    join_columns VARCHAR(500),
    filters_applied VARCHAR(1000),
    
    -- Caching and optimization
    used_cached_sql BIT DEFAULT 0,
    cache_hit BIT DEFAULT 0,
    
    -- Legacy fields for compatibility
    joined_columns TEXT,
    sql_query_type VARCHAR(100),
    operation VARCHAR(100),
    evidence_data TEXT,
    evidence_count INTEGER DEFAULT 0,
    source_table VARCHAR(255),
    target_table VARCHAR(255),
    client_ip VARCHAR(45),
    user_agent VARCHAR(500),
    
    -- Foreign key constraint
    CONSTRAINT fk_execution_kpi FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id) ON DELETE CASCADE,
    
    -- Check constraints
    CONSTRAINT chk_execution_status CHECK (execution_status IN ('pending', 'running', 'success', 'failed', 'timeout', 'cancelled')),
    CONSTRAINT chk_execution_type CHECK (execution_type IN ('manual', 'scheduled', 'api', 'batch', 'test'))
);

PRINT '✅ Created kpi_execution_results table with correct structure';

-- Step 3: Create indexes for performance
PRINT '';
PRINT '🔧 Creating indexes...';

CREATE INDEX idx_execution_kpi_id ON kpi_execution_results(kpi_id);
CREATE INDEX idx_execution_timestamp ON kpi_execution_results(execution_timestamp);
CREATE INDEX idx_execution_status ON kpi_execution_results(execution_status);
CREATE INDEX idx_execution_user ON kpi_execution_results(user_id);
CREATE INDEX idx_execution_type ON kpi_execution_results(execution_type);
CREATE INDEX idx_execution_select_schema ON kpi_execution_results(select_schema);
CREATE INDEX idx_execution_kg_name ON kpi_execution_results(kg_name);
CREATE INDEX idx_execution_db_type ON kpi_execution_results(db_type);

PRINT '✅ Created performance indexes';

-- Step 4: Restore data if backup exists
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'kpi_execution_results_backup')
BEGIN
    PRINT '';
    PRINT '🔄 Restoring data from backup...';
    
    -- Insert data back with proper column mapping
    INSERT INTO kpi_execution_results (
        kpi_id, execution_timestamp, execution_status, 
        select_schema, kg_name, db_type, limit_records, use_llm,
        generated_sql, number_of_records, confidence_score, error_message,
        result_data, evidence_data, evidence_count, source_table, target_table,
        user_id, session_id, total_execution_time_ms
    )
    SELECT 
        kpi_id, 
        ISNULL(execution_timestamp, GETDATE()),
        ISNULL(execution_status, 'success'),
        ISNULL(select_schema, 'newdqschemanov'),
        kg_name,
        ISNULL(db_type, 'sqlserver'),
        ISNULL(limit_records, 1000),
        ISNULL(use_llm, 1),
        generated_sql,
        ISNULL(number_of_records, 0),
        confidence_score,
        error_message,
        result_data,
        evidence_data,
        ISNULL(evidence_count, 0),
        source_table,
        target_table,
        user_id,
        session_id,
        execution_time_ms
    FROM kpi_execution_results_backup;
    
    DECLARE @restored_count INT;
    SELECT @restored_count = COUNT(*) FROM kpi_execution_results;
    PRINT '✅ Restored ' + CAST(@restored_count AS VARCHAR) + ' records';
    
    -- Drop backup table
    DROP TABLE kpi_execution_results_backup;
    PRINT '✅ Cleaned up backup table';
END

-- Step 5: Verify the fix
PRINT '';
PRINT '🔍 VERIFICATION: Testing the fix...';

BEGIN TRY
    -- Test insert
    INSERT INTO kpi_execution_results (kpi_id, execution_status)
    VALUES (999999, 'test');
    
    -- Delete test record
    DELETE FROM kpi_execution_results WHERE kpi_id = 999999 AND execution_status = 'test';
    
    PRINT '✅ SUCCESS: Table is working correctly!';
    
END TRY
BEGIN CATCH
    PRINT '❌ ERROR: ' + ERROR_MESSAGE();
END CATCH

PRINT '';
PRINT '============================================================================';
PRINT '🎉 TABLE RECREATION COMPLETED!';
PRINT 'The select_schema error should now be completely resolved.';
PRINT '============================================================================';
