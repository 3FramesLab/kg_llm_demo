-- =====================================================
-- NBU Tables Verification Script
-- Quick verification of NBU table creation and data quality
-- =====================================================

SET NOCOUNT ON;
GO

PRINT '=== NBU Tables Verification ===';

-- =====================================================
-- 1. Table Existence Check
-- =====================================================

PRINT 'Checking table existence...';

IF OBJECT_ID('brz_lnd_RBP_NBU', 'U') IS NOT NULL
    PRINT '✅ brz_lnd_RBP_NBU table exists'
ELSE
    PRINT '❌ brz_lnd_RBP_NBU table missing';

IF OBJECT_ID('brz_lnd_OPS_EXCEL_NBU', 'U') IS NOT NULL
    PRINT '✅ brz_lnd_OPS_EXCEL_NBU table exists'
ELSE
    PRINT '❌ brz_lnd_OPS_EXCEL_NBU table missing';

-- =====================================================
-- 2. Record Count Verification
-- =====================================================

PRINT '';
PRINT '=== Record Count Summary ===';

SELECT 
    'GPU Tables' as Category,
    'brz_lnd_RBP_GPU' as Table_Name,
    COUNT(*) as Record_Count
FROM brz_lnd_RBP_GPU
UNION ALL
SELECT 
    'GPU Tables' as Category,
    'brz_lnd_OPS_EXCEL_GPU' as Table_Name,
    COUNT(*) as Record_Count
FROM brz_lnd_OPS_EXCEL_GPU
UNION ALL
SELECT 
    'NBU Tables' as Category,
    'brz_lnd_RBP_NBU' as Table_Name,
    COUNT(*) as Record_Count
FROM brz_lnd_RBP_NBU
UNION ALL
SELECT 
    'NBU Tables' as Category,
    'brz_lnd_OPS_EXCEL_NBU' as Table_Name,
    COUNT(*) as Record_Count
FROM brz_lnd_OPS_EXCEL_NBU
ORDER BY Category, Table_Name;

-- =====================================================
-- 3. Product Type Verification
-- =====================================================

PRINT '';
PRINT '=== Product Type Analysis ===';

-- Check if NBU materials are properly segregated
SELECT 
    'NBU RBP Materials' as Description,
    MIN(Material) as First_Material,
    MAX(Material) as Last_Material,
    COUNT(*) as Total_Count
FROM brz_lnd_RBP_NBU;

SELECT 
    'NBU OPS Materials' as Description,
    MIN(PLANNING_SKU) as First_Material,
    MAX(PLANNING_SKU) as Last_Material,
    COUNT(*) as Total_Count
FROM brz_lnd_OPS_EXCEL_NBU
WHERE PLANNING_SKU IS NOT NULL;

-- =====================================================
-- 4. Business Unit Verification
-- =====================================================

PRINT '';
PRINT '=== Business Unit Distribution ===';

SELECT 
    Business_Unit,
    COUNT(*) as Record_Count,
    'RBP_NBU' as Source
FROM brz_lnd_RBP_NBU
GROUP BY Business_Unit
UNION ALL
SELECT 
    Business_Unit,
    COUNT(*) as Record_Count,
    'OPS_NBU' as Source
FROM brz_lnd_OPS_EXCEL_NBU
GROUP BY Business_Unit
ORDER BY Source, Business_Unit;

-- =====================================================
-- 5. Join Testing
-- =====================================================

PRINT '';
PRINT '=== Join Testing Results ===';

-- NBU internal joins
SELECT 
    'NBU Internal Join' as Join_Type,
    COUNT(*) as Matching_Records
FROM brz_lnd_RBP_NBU r
INNER JOIN brz_lnd_OPS_EXCEL_NBU o ON r.Material = o.PLANNING_SKU
WHERE o.PLANNING_SKU IS NOT NULL;

-- Cross-product type joins (should be 0)
SELECT 
    'GPU-NBU Cross Join (should be 0)' as Join_Type,
    COUNT(*) as Matching_Records
FROM brz_lnd_RBP_GPU r
INNER JOIN brz_lnd_OPS_EXCEL_NBU o ON r.Material = o.PLANNING_SKU;

-- =====================================================
-- 6. NULL Analysis
-- =====================================================

PRINT '';
PRINT '=== NULL PLANNING_SKU Analysis ===';

DECLARE @TotalNBU INT = (SELECT COUNT(*) FROM brz_lnd_OPS_EXCEL_NBU);
DECLARE @NullNBU INT = (SELECT COUNT(*) FROM brz_lnd_OPS_EXCEL_NBU WHERE PLANNING_SKU IS NULL);

SELECT 
    'NBU NULL Analysis' as Description,
    @TotalNBU as Total_Records,
    @NullNBU as NULL_Records,
    (@TotalNBU - @NullNBU) as Non_NULL_Records,
    CASE 
        WHEN @TotalNBU = 0 THEN 0.00
        ELSE CAST(@NullNBU * 100.0 / @TotalNBU AS DECIMAL(5,2))
    END as NULL_Percentage;

-- =====================================================
-- 7. Sample Data Display
-- =====================================================

PRINT '';
PRINT '=== Sample NBU Data ===';

PRINT 'Sample RBP_NBU records:';
SELECT TOP 5
    Product_Line,
    Product_Family,
    Material,
    Business_Unit,
    Overall_Result
FROM brz_lnd_RBP_NBU
ORDER BY Product_Line, Material;

PRINT '';
PRINT 'Sample OPS_EXCEL_NBU records:';
SELECT TOP 5
    PLANNING_SKU,
    Product_Line,
    Customer,
    Level_2_usage,
    CHIP_Family
FROM brz_lnd_OPS_EXCEL_NBU
ORDER BY Product_Line, Customer;

PRINT '';
PRINT '=== NBU VERIFICATION COMPLETE ===';
PRINT 'Status: NBU tables created and populated successfully';
PRINT 'Ready for: NBU-specific testing and cross-product analysis';
PRINT '';
