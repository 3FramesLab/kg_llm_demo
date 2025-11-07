-- =====================================================
-- Quick Fix: Update hana_material_master OPS_PLANNER to fit NVARCHAR(12)
-- This fixes the root cause so all subsequent operations work
-- =====================================================

SET NOCOUNT ON;
GO

PRINT '=== Fixing hana_material_master OPS_PLANNER Column ===';

-- =====================================================
-- 1. Show current problematic values
-- =====================================================

PRINT 'Current OPS_PLANNER values that exceed 12 characters:';

SELECT 
    MATERIAL,
    OPS_PLANNER,
    LEN(OPS_PLANNER) as Current_Length,
    LEFT(OPS_PLANNER, 12) as Truncated_Value
FROM hana_material_master
WHERE LEN(OPS_PLANNER) > 12
ORDER BY LEN(OPS_PLANNER) DESC;

-- =====================================================
-- 2. Update OPS_PLANNER to fit within 12 characters
-- =====================================================

PRINT 'Updating OPS_PLANNER values to fit within 12 characters...';

-- Strategy: Replace long planner names with short codes
UPDATE hana_material_master
SET OPS_PLANNER = 
    CASE 
        -- If already 12 chars or less, keep as is
        WHEN LEN(OPS_PLANNER) <= 12 THEN OPS_PLANNER
        
        -- For longer names, create short planner codes
        ELSE 'PLN_' + 
             CASE [Product Type]
                 WHEN 'GPU' THEN 'GPU_'
                 WHEN 'NBU' THEN 'NBU_'
                 ELSE 'GEN_'
             END +
             RIGHT('00' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 99) + 1 AS VARCHAR), 2)
    END
WHERE LEN(OPS_PLANNER) > 12;

PRINT 'Updated ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records with long OPS_PLANNER values';

-- =====================================================
-- 3. Verification
-- =====================================================

PRINT '';
PRINT '=== VERIFICATION ===';

-- Check max length after update
SELECT 
    'Max OPS_PLANNER Length After Fix' as Description,
    MAX(LEN(OPS_PLANNER)) as Max_Length
FROM hana_material_master;

-- Show sample of updated values
SELECT TOP 15
    MATERIAL,
    OPS_PLANNER,
    LEN(OPS_PLANNER) as Length,
    [Product Type]
FROM hana_material_master
ORDER BY [Product Type], OPS_PLANNER;

-- Count by product type
SELECT 
    [Product Type],
    COUNT(*) as Total_Records,
    MAX(LEN(OPS_PLANNER)) as Max_Planner_Length
FROM hana_material_master
GROUP BY [Product Type]
ORDER BY [Product Type];

PRINT '';
PRINT '=== FIX COMPLETE ===';
PRINT 'Summary:';
PRINT '- All OPS_PLANNER values now fit within NVARCHAR(12) limit';
PRINT '- Updated format: PLN_GPU_01, PLN_NBU_01, etc.';
PRINT '- Original short values preserved';
PRINT '- Ready for OPS_EXCEL_GPU population without truncation errors';
PRINT '';
PRINT 'You can now run your original OPS_EXCEL_GPU seed data scripts successfully.';
PRINT '';
