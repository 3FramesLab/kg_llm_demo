-- Migration: Add code field to groups and dashboards tables
-- Date: 2025-11-20
-- Description: Add unique code field to both groups and dashboards tables for user-provided identifiers

-- Add code field to groups table
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'groups') AND name = 'code')
BEGIN
    ALTER TABLE groups ADD code NVARCHAR(100) NULL;
END
GO

-- Add unique constraint on code field for groups (after adding the column)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID(N'groups') AND name = 'UQ_groups_code')
BEGIN
    ALTER TABLE groups ADD CONSTRAINT UQ_groups_code UNIQUE (code);
END
GO

-- Add code field to dashboards table
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'dashboards') AND name = 'code')
BEGIN
    ALTER TABLE dashboards ADD code NVARCHAR(100) NULL;
END
GO

-- Add unique constraint on code field for dashboards within the same group
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID(N'dashboards') AND name = 'UQ_dashboards_group_code')
BEGIN
    ALTER TABLE dashboards ADD CONSTRAINT UQ_dashboards_group_code UNIQUE (group_id, code);
END
GO

-- Create indexes for better query performance on code fields
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID(N'groups') AND name = 'idx_groups_code')
BEGIN
    CREATE INDEX idx_groups_code ON groups(code);
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID(N'dashboards') AND name = 'idx_dashboards_code')
BEGIN
    CREATE INDEX idx_dashboards_code ON dashboards(code);
END
GO

PRINT 'Migration completed: Added code field to groups and dashboards tables';

