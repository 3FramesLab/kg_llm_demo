-- Migration: Add group_id and dashboard_id to kpi_definitions table
-- Purpose: Associate KPIs with Groups and Dashboards from Master Page
-- Date: 2025-11-20

USE KPI_Analytics;
GO

-- Add group_id column (nullable, no foreign key since Groups are in different database)
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID('kpi_definitions') 
    AND name = 'group_id'
)
BEGIN
    ALTER TABLE kpi_definitions
    ADD group_id INT NULL;
    
    PRINT '✓ Added group_id column to kpi_definitions';
END
ELSE
BEGIN
    PRINT '✓ group_id column already exists in kpi_definitions';
END
GO

-- Add dashboard_id column (nullable, no foreign key since Dashboards are in different database)
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID('kpi_definitions') 
    AND name = 'dashboard_id'
)
BEGIN
    ALTER TABLE kpi_definitions
    ADD dashboard_id INT NULL;
    
    PRINT '✓ Added dashboard_id column to kpi_definitions';
END
ELSE
BEGIN
    PRINT '✓ dashboard_id column already exists in kpi_definitions';
END
GO

-- Create index on group_id for better query performance
IF NOT EXISTS (
    SELECT * FROM sys.indexes 
    WHERE name = 'IX_kpi_definitions_group_id' 
    AND object_id = OBJECT_ID('kpi_definitions')
)
BEGIN
    CREATE INDEX IX_kpi_definitions_group_id 
    ON kpi_definitions(group_id);
    
    PRINT '✓ Created index on group_id';
END
GO

-- Create index on dashboard_id for better query performance
IF NOT EXISTS (
    SELECT * FROM sys.indexes 
    WHERE name = 'IX_kpi_definitions_dashboard_id' 
    AND object_id = OBJECT_ID('kpi_definitions')
)
BEGIN
    CREATE INDEX IX_kpi_definitions_dashboard_id 
    ON kpi_definitions(dashboard_id);
    
    PRINT '✓ Created index on dashboard_id';
END
GO

PRINT '';
PRINT '========================================';
PRINT 'Migration completed successfully!';
PRINT 'KPI definitions can now be associated with Groups and Dashboards';
PRINT '========================================';
GO

