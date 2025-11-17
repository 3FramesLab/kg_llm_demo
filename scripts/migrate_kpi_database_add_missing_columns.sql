-- ============================================================================
-- KPI Database Migration Script - Add Missing Columns
-- Adds missing columns to existing KPI_Analytics database
-- Version: 1.1
-- Date: 2024-11-10
-- ============================================================================

USE KPI_Analytics;
GO

PRINT 'Starting KPI Database Migration - Adding Missing Columns';
PRINT '============================================================================';

-- ============================================================================
-- 1. ADD MISSING COLUMNS TO kpi_execution_results TABLE
-- ============================================================================

-- Check if select_schema column exists, if not add it
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_execution_results' 
               AND COLUMN_NAME = 'select_schema')
BEGIN
    ALTER TABLE kpi_execution_results 
    ADD select_schema VARCHAR(255) NOT NULL DEFAULT 'default';
    
    PRINT '✅ Added select_schema column to kpi_execution_results';
END
ELSE
BEGIN
    PRINT '⚠️ Column select_schema already exists in kpi_execution_results';
END

-- Check if kg_name column exists, if not add it
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_execution_results' 
               AND COLUMN_NAME = 'kg_name')
BEGIN
    ALTER TABLE kpi_execution_results 
    ADD kg_name VARCHAR(255);
    
    PRINT '✅ Added kg_name column to kpi_execution_results';
END
ELSE
BEGIN
    PRINT '⚠️ Column kg_name already exists in kpi_execution_results';
END

-- Check if db_type column exists, if not add it
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_execution_results' 
               AND COLUMN_NAME = 'db_type')
BEGIN
    ALTER TABLE kpi_execution_results 
    ADD db_type VARCHAR(50) DEFAULT 'sqlserver';
    
    PRINT '✅ Added db_type column to kpi_execution_results';
END
ELSE
BEGIN
    PRINT '⚠️ Column db_type already exists in kpi_execution_results';
END

-- Check if schemas column exists, if not add it
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_execution_results' 
               AND COLUMN_NAME = 'schemas')
BEGIN
    ALTER TABLE kpi_execution_results 
    ADD schemas TEXT;
    
    PRINT '✅ Added schemas column to kpi_execution_results';
END
ELSE
BEGIN
    PRINT '⚠️ Column schemas already exists in kpi_execution_results';
END

-- Check if definitions column exists, if not add it
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_execution_results' 
               AND COLUMN_NAME = 'definitions')
BEGIN
    ALTER TABLE kpi_execution_results 
    ADD definitions TEXT;
    
    PRINT '✅ Added definitions column to kpi_execution_results';
END
ELSE
BEGIN
    PRINT '⚠️ Column definitions already exists in kpi_execution_results';
END

-- Check if use_llm column exists, if not add it
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_execution_results' 
               AND COLUMN_NAME = 'use_llm')
BEGIN
    ALTER TABLE kpi_execution_results 
    ADD use_llm BIT DEFAULT 1;
    
    PRINT '✅ Added use_llm column to kpi_execution_results';
END
ELSE
BEGIN
    PRINT '⚠️ Column use_llm already exists in kpi_execution_results';
END

-- Check if min_confidence column exists, if not add it
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_execution_results' 
               AND COLUMN_NAME = 'min_confidence')
BEGIN
    ALTER TABLE kpi_execution_results 
    ADD min_confidence DECIMAL(5,4) DEFAULT 0.7;
    
    PRINT '✅ Added min_confidence column to kpi_execution_results';
END
ELSE
BEGIN
    PRINT '⚠️ Column min_confidence already exists in kpi_execution_results';
END

-- Check if limit_records column exists, if not add it
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_execution_results' 
               AND COLUMN_NAME = 'limit_records')
BEGIN
    ALTER TABLE kpi_execution_results 
    ADD limit_records INTEGER DEFAULT 1000;
    
    PRINT '✅ Added limit_records column to kpi_execution_results';
END
ELSE
BEGIN
    PRINT '⚠️ Column limit_records already exists in kpi_execution_results';
END

-- ============================================================================
-- 2. UPDATE EXISTING NULL VALUES
-- ============================================================================

-- Update any existing NULL values in select_schema column
UPDATE kpi_execution_results 
SET select_schema = 'default' 
WHERE select_schema IS NULL;

PRINT '✅ Updated NULL values in select_schema column';

-- ============================================================================
-- 3. ADD INDEXES FOR NEW COLUMNS
-- ============================================================================

-- Add index for select_schema if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_execution_select_schema')
BEGIN
    CREATE INDEX idx_execution_select_schema ON kpi_execution_results(select_schema);
    PRINT '✅ Added index for select_schema column';
END

-- Add index for kg_name if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_execution_kg_name')
BEGIN
    CREATE INDEX idx_execution_kg_name ON kpi_execution_results(kg_name);
    PRINT '✅ Added index for kg_name column';
END

-- Add index for db_type if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_execution_db_type')
BEGIN
    CREATE INDEX idx_execution_db_type ON kpi_execution_results(db_type);
    PRINT '✅ Added index for db_type column';
END

-- ============================================================================
-- 4. VERIFICATION
-- ============================================================================

PRINT '';
PRINT 'Migration Verification:';
PRINT '============================================================================';

-- Show all columns in kpi_execution_results table
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'kpi_execution_results'
ORDER BY ORDINAL_POSITION;

PRINT '';
PRINT '✅ KPI Database Migration Completed Successfully!';
PRINT 'All missing columns have been added to the kpi_execution_results table.';
PRINT '============================================================================';
