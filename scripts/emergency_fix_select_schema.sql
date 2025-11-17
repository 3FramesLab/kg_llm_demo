-- ============================================================================
-- EMERGENCY FIX: Resolve select_schema NULL constraint error
-- This script handles all possible scenarios for the missing column
-- ============================================================================

USE KPI_Analytics;
GO

PRINT '🚨 EMERGENCY FIX: Resolving select_schema NULL constraint error';
PRINT '============================================================================';

-- Step 1: Check if table exists
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'kpi_execution_results')
BEGIN
    PRINT '❌ ERROR: Table kpi_execution_results does not exist!';
    PRINT 'Please run the comprehensive database creation script first.';
    PRINT '============================================================================';
    RETURN;
END

PRINT '✅ Table kpi_execution_results exists';

-- Step 2: Check current table structure
PRINT '';
PRINT '📋 Current table structure:';
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'kpi_execution_results'
ORDER BY ORDINAL_POSITION;

-- Step 3: Check if select_schema column exists
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_execution_results' 
               AND COLUMN_NAME = 'select_schema')
BEGIN
    PRINT '';
    PRINT '🔧 SCENARIO 1: select_schema column does not exist - Adding it now';
    
    ALTER TABLE kpi_execution_results 
    ADD select_schema VARCHAR(255) NOT NULL DEFAULT 'newdqschemanov';
    
    PRINT '✅ SUCCESS: Added select_schema column with default value';
    
    -- Add index for performance
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_execution_select_schema')
    BEGIN
        CREATE INDEX idx_execution_select_schema ON kpi_execution_results(select_schema);
        PRINT '✅ SUCCESS: Added index for select_schema column';
    END
END
ELSE
BEGIN
    PRINT '';
    PRINT '🔧 SCENARIO 2: select_schema column exists - Checking configuration';
    
    -- Check if column allows NULL
    DECLARE @is_nullable VARCHAR(3);
    SELECT @is_nullable = IS_NULLABLE 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'kpi_execution_results' 
    AND COLUMN_NAME = 'select_schema';
    
    IF @is_nullable = 'YES'
    BEGIN
        PRINT '⚠️ Column allows NULL - Converting to NOT NULL';
        
        -- First, update any existing NULL values
        UPDATE kpi_execution_results 
        SET select_schema = 'newdqschemanov' 
        WHERE select_schema IS NULL;
        
        PRINT '✅ Updated existing NULL values';
        
        -- Then alter column to NOT NULL
        ALTER TABLE kpi_execution_results 
        ALTER COLUMN select_schema VARCHAR(255) NOT NULL;
        
        PRINT '✅ SUCCESS: Column now requires NOT NULL';
    END
    ELSE
    BEGIN
        PRINT '✅ Column already configured as NOT NULL';
    END
END

-- Step 4: Add other commonly missing columns
PRINT '';
PRINT '🔧 Adding other commonly missing columns...';

-- Add kg_name if missing
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_execution_results' 
               AND COLUMN_NAME = 'kg_name')
BEGIN
    ALTER TABLE kpi_execution_results ADD kg_name VARCHAR(255);
    PRINT '✅ Added kg_name column';
END

-- Add db_type if missing
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_execution_results' 
               AND COLUMN_NAME = 'db_type')
BEGIN
    ALTER TABLE kpi_execution_results ADD db_type VARCHAR(50) DEFAULT 'sqlserver';
    PRINT '✅ Added db_type column';
END

-- Add limit_records if missing
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_execution_results' 
               AND COLUMN_NAME = 'limit_records')
BEGIN
    ALTER TABLE kpi_execution_results ADD limit_records INTEGER DEFAULT 1000;
    PRINT '✅ Added limit_records column';
END

-- Add use_llm if missing
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_execution_results' 
               AND COLUMN_NAME = 'use_llm')
BEGIN
    ALTER TABLE kpi_execution_results ADD use_llm BIT DEFAULT 1;
    PRINT '✅ Added use_llm column';
END

-- Step 5: Verify the fix
PRINT '';
PRINT '🔍 VERIFICATION: Final table structure';
PRINT '============================================================================';

SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'kpi_execution_results'
AND COLUMN_NAME IN ('select_schema', 'kg_name', 'db_type', 'limit_records', 'use_llm')
ORDER BY COLUMN_NAME;

-- Step 6: Test insert to verify fix
PRINT '';
PRINT '🧪 TESTING: Attempting test insert to verify fix';

BEGIN TRY
    -- Test insert with minimal required fields
    INSERT INTO kpi_execution_results (kpi_id, execution_status)
    VALUES (999999, 'test');
    
    -- If successful, delete the test record
    DELETE FROM kpi_execution_results WHERE kpi_id = 999999 AND execution_status = 'test';
    
    PRINT '✅ SUCCESS: Test insert completed successfully!';
    PRINT '✅ The select_schema error should now be resolved.';
    
END TRY
BEGIN CATCH
    PRINT '❌ ERROR: Test insert failed:';
    PRINT ERROR_MESSAGE();
    PRINT '';
    PRINT 'Please check the table structure and try again.';
END CATCH

PRINT '';
PRINT '============================================================================';
PRINT '🎉 EMERGENCY FIX COMPLETED!';
PRINT 'You can now retry your KPI execution.';
PRINT '============================================================================';
