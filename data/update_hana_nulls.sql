-- =====================================================
-- Update hana_material_master to have NULL values
-- for OPS_PLANNER, OPS_STATUS, OPS_PLCCODE in some records
-- =====================================================

SET NOCOUNT ON;

PRINT '=====================================================';
PRINT 'UPDATING hana_material_master with NULL values';
PRINT 'Setting some records to have NULL OPS fields';
PRINT '=====================================================';

-- Update approximately 20% of records to have NULL OPS_PLANNER
UPDATE hana_material_master 
SET OPS_PLANNER = NULL
WHERE (
    -- Use a pattern to select ~20% of records
    CAST(RIGHT(MATERIAL, 3) AS INT) % 5 = 0
);

PRINT 'Set OPS_PLANNER to NULL for ' + CAST(@@ROWCOUNT AS NVARCHAR) + ' records (~20%)';

-- Update approximately 15% of records to have NULL OPS_STATUS  
UPDATE hana_material_master 
SET OPS_STATUS = NULL
WHERE (
    -- Use a different pattern to select ~15% of records
    CAST(RIGHT(MATERIAL, 3) AS INT) % 7 = 0
);

PRINT 'Set OPS_STATUS to NULL for ' + CAST(@@ROWCOUNT AS NVARCHAR) + ' records (~15%)';

-- Update approximately 25% of records to have NULL OPS_PLCCODE
UPDATE hana_material_master 
SET OPS_PLCCODE = NULL
WHERE (
    -- Use another pattern to select ~25% of records
    CAST(RIGHT(MATERIAL, 3) AS INT) % 4 = 0
);

PRINT 'Set OPS_PLCCODE to NULL for ' + CAST(@@ROWCOUNT AS NVARCHAR) + ' records (~25%)';

-- =====================================================
-- VALIDATION: Check NULL distribution
-- =====================================================

PRINT '';
PRINT 'NULL VALUE DISTRIBUTION ANALYSIS:';
PRINT '=====================================================';

-- Count NULL values for each column
SELECT 
    'OPS_PLANNER' as ColumnName,
    COUNT(*) as TotalRecords,
    SUM(CASE WHEN OPS_PLANNER IS NULL THEN 1 ELSE 0 END) as NullCount,
    SUM(CASE WHEN OPS_PLANNER IS NOT NULL THEN 1 ELSE 0 END) as NotNullCount,
    CAST(SUM(CASE WHEN OPS_PLANNER IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(5,1)) as NullPercentage
FROM hana_material_master

UNION ALL

SELECT 
    'OPS_STATUS' as ColumnName,
    COUNT(*) as TotalRecords,
    SUM(CASE WHEN OPS_STATUS IS NULL THEN 1 ELSE 0 END) as NullCount,
    SUM(CASE WHEN OPS_STATUS IS NOT NULL THEN 1 ELSE 0 END) as NotNullCount,
    CAST(SUM(CASE WHEN OPS_STATUS IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(5,1)) as NullPercentage
FROM hana_material_master

UNION ALL

SELECT 
    'OPS_PLCCODE' as ColumnName,
    COUNT(*) as TotalRecords,
    SUM(CASE WHEN OPS_PLCCODE IS NULL THEN 1 ELSE 0 END) as NullCount,
    SUM(CASE WHEN OPS_PLCCODE IS NOT NULL THEN 1 ELSE 0 END) as NotNullCount,
    CAST(SUM(CASE WHEN OPS_PLCCODE IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(5,1)) as NullPercentage
FROM hana_material_master;

PRINT '';
PRINT 'SAMPLE RECORDS WITH NULL VALUES:';

-- Show sample records with NULL values
SELECT TOP 10
    MATERIAL,
    [Product Type],
    OPS_PLANNER,
    OPS_STATUS, 
    OPS_PLCCODE,
    CASE 
        WHEN OPS_PLANNER IS NULL AND OPS_STATUS IS NULL AND OPS_PLCCODE IS NULL THEN 'ALL_NULL'
        WHEN OPS_PLANNER IS NULL OR OPS_STATUS IS NULL OR OPS_PLCCODE IS NULL THEN 'PARTIAL_NULL'
        ELSE 'NO_NULL'
    END as NullStatus
FROM hana_material_master
WHERE OPS_PLANNER IS NULL OR OPS_STATUS IS NULL OR OPS_PLCCODE IS NULL
ORDER BY MATERIAL;

PRINT '';
PRINT 'RECORDS WITH ALL THREE FIELDS NULL:';

-- Count records where all three fields are NULL
SELECT 
    COUNT(*) as RecordsWithAllThreeNull,
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM hana_material_master) AS DECIMAL(5,1)) as PercentageAllNull
FROM hana_material_master
WHERE OPS_PLANNER IS NULL AND OPS_STATUS IS NULL AND OPS_PLCCODE IS NULL;

PRINT '';
PRINT 'BREAKDOWN BY PRODUCT TYPE:';

-- Show NULL distribution by Product Type
SELECT 
    [Product Type],
    COUNT(*) as TotalRecords,
    SUM(CASE WHEN OPS_PLANNER IS NULL THEN 1 ELSE 0 END) as NullPlanner,
    SUM(CASE WHEN OPS_STATUS IS NULL THEN 1 ELSE 0 END) as NullStatus,
    SUM(CASE WHEN OPS_PLCCODE IS NULL THEN 1 ELSE 0 END) as NullPlcCode
FROM hana_material_master
GROUP BY [Product Type]
ORDER BY [Product Type];

PRINT '';
PRINT '=====================================================';
PRINT 'NULL VALUE UPDATE COMPLETED SUCCESSFULLY!';
PRINT 'OPS_PLANNER: ~20% NULL';
PRINT 'OPS_STATUS: ~15% NULL'; 
PRINT 'OPS_PLCCODE: ~25% NULL';
PRINT '=====================================================';

SET NOCOUNT OFF;
