-- Migration: Add dashboard_name column to kpi_definitions table
-- Database: KPI_Analytics
-- Purpose: Store dashboard name alongside dashboard_id for display and reporting

USE KPI_Analytics;
GO

-- Add dashboard_name column
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID('kpi_definitions') 
    AND name = 'dashboard_name'
)
BEGIN
    ALTER TABLE kpi_definitions
    ADD dashboard_name VARCHAR(255) NULL;
    
    PRINT '✓ Added dashboard_name column to kpi_definitions table';
END
ELSE
BEGIN
    PRINT '⚠ dashboard_name column already exists in kpi_definitions table';
END
GO

-- Create index for better query performance
IF NOT EXISTS (
    SELECT * FROM sys.indexes 
    WHERE name = 'idx_kpi_definitions_dashboard_name' 
    AND object_id = OBJECT_ID('kpi_definitions')
)
BEGIN
    CREATE INDEX idx_kpi_definitions_dashboard_name 
    ON kpi_definitions(dashboard_name);
    
    PRINT '✓ Created index on dashboard_name column';
END
ELSE
BEGIN
    PRINT '⚠ Index on dashboard_name already exists';
END
GO

PRINT '✅ Migration completed successfully';
GO

