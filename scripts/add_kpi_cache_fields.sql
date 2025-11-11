-- =====================================================
-- Add isAccept and isSQLCached fields to KPI definitions
-- =====================================================

USE [newdqschemanov];
GO

PRINT 'Adding isAccept and isSQLCached fields to kpi_definitions table...';

-- Check if isAccept column exists, if not add it
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_definitions' AND COLUMN_NAME = 'isAccept')
BEGIN
    ALTER TABLE kpi_definitions 
    ADD isAccept BIT DEFAULT 0;
    
    PRINT '✓ Added isAccept field (default: false)';
END
ELSE
BEGIN
    PRINT '⚠️ isAccept field already exists';
END

-- Check if isSQLCached column exists, if not add it
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_definitions' AND COLUMN_NAME = 'isSQLCached')
BEGIN
    ALTER TABLE kpi_definitions 
    ADD isSQLCached BIT DEFAULT 0;
    
    PRINT '✓ Added isSQLCached field (default: false)';
END
ELSE
BEGIN
    PRINT '⚠️ isSQLCached field already exists';
END

-- Also add cached_sql field to store the accepted SQL
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_definitions' AND COLUMN_NAME = 'cached_sql')
BEGIN
    ALTER TABLE kpi_definitions 
    ADD cached_sql NVARCHAR(MAX) NULL;
    
    PRINT '✓ Added cached_sql field for storing accepted SQL';
END
ELSE
BEGIN
    PRINT '⚠️ cached_sql field already exists';
END

-- Add index for performance on the new fields
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_kpi_definitions_cache_flags')
BEGIN
    CREATE INDEX IX_kpi_definitions_cache_flags 
    ON kpi_definitions (isAccept, isSQLCached);
    
    PRINT '✓ Added index on cache flags';
END

PRINT '';
PRINT '✅ KPI cache fields migration completed successfully!';
PRINT '';
PRINT 'New fields added:';
PRINT '  • isAccept (BIT): Indicates if generated SQL is accepted by user';
PRINT '  • isSQLCached (BIT): Indicates if cached SQL should be used instead of LLM generation';
PRINT '  • cached_sql (NVARCHAR(MAX)): Stores the accepted SQL query';
PRINT '';

-- Show updated table structure
PRINT 'Updated kpi_definitions table structure:';
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'kpi_definitions'
ORDER BY ORDINAL_POSITION;

GO
