-- ============================================================================
-- QUICK FIX: Add select_schema column to kpi_execution_results
-- This script immediately fixes the NULL constraint error
-- ============================================================================

USE KPI_Analytics;
GO

PRINT 'Quick Fix: Adding select_schema column to resolve NULL constraint error';
PRINT '============================================================================';

-- Add the missing select_schema column with NOT NULL constraint and default value
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_execution_results' 
               AND COLUMN_NAME = 'select_schema')
BEGIN
    -- Add the column with default value
    ALTER TABLE kpi_execution_results 
    ADD select_schema VARCHAR(255) NOT NULL DEFAULT 'newdqschemanov';
    
    PRINT '✅ SUCCESS: Added select_schema column with default value "newdqschemanov"';
    
    -- Add index for performance
    CREATE INDEX idx_execution_select_schema ON kpi_execution_results(select_schema);
    PRINT '✅ SUCCESS: Added index for select_schema column';
END
ELSE
BEGIN
    PRINT '⚠️ WARNING: Column select_schema already exists';
    
    -- Check if it allows NULL and fix if needed
    IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_execution_results' 
               AND COLUMN_NAME = 'select_schema' 
               AND IS_NULLABLE = 'YES')
    BEGIN
        -- First update any NULL values
        UPDATE kpi_execution_results 
        SET select_schema = 'newdqschemanov' 
        WHERE select_schema IS NULL;
        
        -- Then alter column to NOT NULL
        ALTER TABLE kpi_execution_results 
        ALTER COLUMN select_schema VARCHAR(255) NOT NULL;
        
        PRINT '✅ SUCCESS: Updated select_schema column to NOT NULL with default values';
    END
    ELSE
    BEGIN
        PRINT '✅ INFO: Column select_schema already exists and is properly configured';
    END
END

-- Verify the fix
PRINT '';
PRINT 'Verification:';
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'kpi_execution_results' 
AND COLUMN_NAME = 'select_schema';

PRINT '';
PRINT '✅ QUICK FIX COMPLETED!';
PRINT 'The select_schema column error should now be resolved.';
PRINT 'You can now retry your KPI execution.';
PRINT '============================================================================';
