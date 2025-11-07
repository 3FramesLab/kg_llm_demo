-- =====================================================
-- Update brz_lnd_OPS_EXCEL_GPU to have NULL PLANNING_SKU values
-- Creates realistic test scenarios for NULL handling in joins
-- =====================================================

SET NOCOUNT ON;
GO

PRINT '=== Starting OPS_EXCEL_GPU PLANNING_SKU NULL Update ===';

-- =====================================================
-- 1. Show current state before update
-- =====================================================

PRINT 'Current state of brz_lnd_OPS_EXCEL_GPU:';

SELECT 
    'Total Records' as Description,
    COUNT(*) as Count
FROM brz_lnd_OPS_EXCEL_GPU;

SELECT 
    'Records with PLANNING_SKU' as Description,
    COUNT(*) as Count
FROM brz_lnd_OPS_EXCEL_GPU
WHERE PLANNING_SKU IS NOT NULL;

SELECT 
    'Records with NULL PLANNING_SKU' as Description,
    COUNT(*) as Count
FROM brz_lnd_OPS_EXCEL_GPU
WHERE PLANNING_SKU IS NULL;

-- =====================================================
-- 2. Update strategy: Set ~20% of records to have NULL PLANNING_SKU
--    This creates realistic scenarios for testing NULL handling
-- =====================================================

PRINT '';
PRINT 'Updating PLANNING_SKU to NULL for selected records...';

-- Strategy: Set PLANNING_SKU to NULL for records where:
-- 1. ROW_NUMBER() % 5 = 0 (every 5th record - 20%)
-- 2. Focus on specific business scenarios that might have missing planning data

UPDATE brz_lnd_OPS_EXCEL_GPU
SET PLANNING_SKU = NULL
WHERE ETL_BatchID IN (
    SELECT ETL_BatchID
    FROM (
        SELECT 
            ETL_BatchID,
            ROW_NUMBER() OVER (ORDER BY PLANNING_SKU) as RowNum
        FROM brz_lnd_OPS_EXCEL_GPU
    ) ranked
    WHERE ranked.RowNum % 5 = 0  -- Every 5th record
);

PRINT 'Updated records where ROW_NUMBER % 5 = 0 (every 5th record)';

-- =====================================================
-- 3. Additional strategic NULL updates for specific scenarios
-- =====================================================

-- Set PLANNING_SKU to NULL for some "Inactive" products (realistic scenario)
UPDATE TOP (10) brz_lnd_OPS_EXCEL_GPU
SET PLANNING_SKU = NULL
WHERE Active_Inactive = 'Inactive'
AND PLANNING_SKU IS NOT NULL;

PRINT 'Updated additional 10 Inactive products to have NULL PLANNING_SKU';

-- Set PLANNING_SKU to NULL for some specific customers (data quality issues)
UPDATE TOP (5) brz_lnd_OPS_EXCEL_GPU
SET PLANNING_SKU = NULL
WHERE Customer IN ('PALIT', 'INNO3D')
AND PLANNING_SKU IS NOT NULL;

PRINT 'Updated 5 records for specific customers to have NULL PLANNING_SKU';

-- =====================================================
-- 4. Show updated state after changes
-- =====================================================

PRINT '';
PRINT '=== UPDATED STATE ===';

SELECT 
    'Total Records' as Description,
    COUNT(*) as Count
FROM brz_lnd_OPS_EXCEL_GPU;

SELECT 
    'Records with PLANNING_SKU' as Description,
    COUNT(*) as Count
FROM brz_lnd_OPS_EXCEL_GPU
WHERE PLANNING_SKU IS NOT NULL;

SELECT 
    'Records with NULL PLANNING_SKU' as Description,
    COUNT(*) as Count
FROM brz_lnd_OPS_EXCEL_GPU
WHERE PLANNING_SKU IS NULL;

-- Show percentage of NULL records (with divide by zero protection)
SELECT
    'Percentage of NULL PLANNING_SKU' as Description,
    CASE
        WHEN (SELECT COUNT(*) FROM brz_lnd_OPS_EXCEL_GPU) = 0 THEN 0.00
        ELSE CAST(
            (SELECT COUNT(*) FROM brz_lnd_OPS_EXCEL_GPU WHERE PLANNING_SKU IS NULL) * 100.0 /
            NULLIF((SELECT COUNT(*) FROM brz_lnd_OPS_EXCEL_GPU), 0)
        AS DECIMAL(5,2))
    END as Percentage;

-- =====================================================
-- 5. Show sample records with NULL PLANNING_SKU
-- =====================================================

PRINT '';
PRINT 'Sample records with NULL PLANNING_SKU:';

SELECT TOP 10
    PLANNING_SKU,
    Product_Line,
    Customer,
    Active_Inactive,
    Level_2_usage,
    CHIP_Family
FROM brz_lnd_OPS_EXCEL_GPU
WHERE PLANNING_SKU IS NULL
ORDER BY Customer, Active_Inactive;

-- =====================================================
-- 6. Show impact on joins (for testing purposes)
-- =====================================================

PRINT '';
PRINT '=== JOIN IMPACT ANALYSIS ===';

-- Show how this affects joins with RBP_GPU
SELECT 
    'RBP_GPU records that will match OPS_EXCEL_GPU' as Description,
    COUNT(*) as Count
FROM brz_lnd_RBP_GPU r
INNER JOIN brz_lnd_OPS_EXCEL_GPU o ON r.Material = o.PLANNING_SKU
WHERE o.PLANNING_SKU IS NOT NULL;

-- Show RBP_GPU records that won't match due to NULL PLANNING_SKU
SELECT 
    'RBP_GPU records that might not match due to NULL PLANNING_SKU' as Description,
    COUNT(*) as Count
FROM brz_lnd_RBP_GPU r
WHERE r.Material IN (
    SELECT PLANNING_SKU 
    FROM brz_lnd_OPS_EXCEL_GPU 
    WHERE PLANNING_SKU IS NULL
);

PRINT '';
PRINT '=== UPDATE COMPLETE ===';
PRINT 'Summary:';
PRINT '- Added NULL PLANNING_SKU values to ~20-25% of records';
PRINT '- Focused on realistic scenarios: Inactive products, specific customers';
PRINT '- This will test NULL handling in joins and reconciliation queries';
PRINT '- Use LEFT JOIN to include records with NULL PLANNING_SKU';
PRINT '- Use WHERE PLANNING_SKU IS NULL to find records with missing planning data';
PRINT '';
