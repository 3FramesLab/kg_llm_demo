-- Quick KPI Cache Fields Migration
-- Run this in SQL Server Management Studio or any SQL client

USE [newdqschemanov];
GO

PRINT 'Adding KPI cache fields...';

-- Add isAccept field
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_definitions' AND COLUMN_NAME = 'isAccept')
BEGIN
    ALTER TABLE kpi_definitions ADD isAccept BIT DEFAULT 0;
    PRINT '✓ Added isAccept field';
END
ELSE
BEGIN
    PRINT '⚠️ isAccept field already exists';
END

-- Add isSQLCached field  
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_definitions' AND COLUMN_NAME = 'isSQLCached')
BEGIN
    ALTER TABLE kpi_definitions ADD isSQLCached BIT DEFAULT 0;
    PRINT '✓ Added isSQLCached field';
END
ELSE
BEGIN
    PRINT '⚠️ isSQLCached field already exists';
END

-- Add cached_sql field
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'kpi_definitions' AND COLUMN_NAME = 'cached_sql')
BEGIN
    ALTER TABLE kpi_definitions ADD cached_sql NVARCHAR(MAX) NULL;
    PRINT '✓ Added cached_sql field';
END
ELSE
BEGIN
    PRINT '⚠️ cached_sql field already exists';
END

PRINT '✅ Migration completed!';
PRINT 'You can now use the KPI cache features.';

-- Show updated table structure
PRINT '';
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
