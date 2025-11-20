-- Migration: Remove group dependency from dashboards table
-- This makes dashboards completely independent from groups

-- Step 1: Drop foreign key constraint
IF EXISTS (
    SELECT * FROM sys.foreign_keys 
    WHERE name = 'FK__dashboards__group_id' 
    OR parent_object_id = OBJECT_ID('dashboards')
    AND referenced_object_id = OBJECT_ID('groups')
)
BEGIN
    DECLARE @ConstraintName NVARCHAR(200);
    SELECT @ConstraintName = name 
    FROM sys.foreign_keys 
    WHERE parent_object_id = OBJECT_ID('dashboards')
    AND referenced_object_id = OBJECT_ID('groups');
    
    IF @ConstraintName IS NOT NULL
    BEGIN
        DECLARE @SQL NVARCHAR(MAX) = 'ALTER TABLE dashboards DROP CONSTRAINT ' + @ConstraintName;
        EXEC sp_executesql @SQL;
        PRINT 'Dropped foreign key constraint: ' + @ConstraintName;
    END
END
GO

-- Step 2: Drop unique constraint on (group_id, name)
IF EXISTS (
    SELECT * FROM sys.indexes 
    WHERE name = 'UQ__dashboards__group_name' 
    OR (object_id = OBJECT_ID('dashboards') AND is_unique_constraint = 1)
)
BEGIN
    DECLARE @UniqueConstraintName NVARCHAR(200);
    SELECT TOP 1 @UniqueConstraintName = name 
    FROM sys.indexes 
    WHERE object_id = OBJECT_ID('dashboards') 
    AND is_unique_constraint = 1
    AND name LIKE '%group%';
    
    IF @UniqueConstraintName IS NOT NULL
    BEGIN
        DECLARE @DropUniqueSQL NVARCHAR(MAX) = 'ALTER TABLE dashboards DROP CONSTRAINT ' + @UniqueConstraintName;
        EXEC sp_executesql @DropUniqueSQL;
        PRINT 'Dropped unique constraint: ' + @UniqueConstraintName;
    END
END
GO

-- Step 3: Make group_id nullable
IF EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dashboards') AND name = 'group_id' AND is_nullable = 0)
BEGIN
    ALTER TABLE dashboards ALTER COLUMN group_id INT NULL;
    PRINT 'Made group_id column nullable';
END
GO

-- Step 4: Drop index on group_id (since it's no longer a foreign key)
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_dashboards_group_id' AND object_id = OBJECT_ID('dashboards'))
BEGIN
    DROP INDEX idx_dashboards_group_id ON dashboards;
    PRINT 'Dropped index: idx_dashboards_group_id';
END
GO

IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_dashboards_group_active' AND object_id = OBJECT_ID('dashboards'))
BEGIN
    DROP INDEX idx_dashboards_group_active ON dashboards;
    PRINT 'Dropped index: idx_dashboards_group_active';
END
GO

-- Step 5: Add unique constraint on code only (dashboards are now independent)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'UQ_dashboards_code' AND object_id = OBJECT_ID('dashboards'))
BEGIN
    ALTER TABLE dashboards ADD CONSTRAINT UQ_dashboards_code UNIQUE (code);
    PRINT 'Added unique constraint on code';
END
GO

-- Step 6: Create index on code for better query performance
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_dashboards_code' AND object_id = OBJECT_ID('dashboards'))
BEGIN
    CREATE INDEX idx_dashboards_code ON dashboards(code);
    PRINT 'Created index on code';
END
GO

PRINT 'Migration completed: Dashboards are now independent from Groups';

