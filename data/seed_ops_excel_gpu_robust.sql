-- =====================================================
-- Robust OPS_EXCEL_GPU Seed Data Generation
-- Fixes: Planner truncation + Divide by zero + NULL PLANNING_SKU
-- =====================================================

SET NOCOUNT ON;
GO

PRINT '=== Starting Robust OPS_EXCEL_GPU Data Generation ===';

-- =====================================================
-- 1. Clear existing data
-- =====================================================

PRINT 'Clearing existing brz_lnd_OPS_EXCEL_GPU data...';
TRUNCATE TABLE brz_lnd_OPS_EXCEL_GPU;

-- =====================================================
-- 2. Populate with all fixes applied
-- =====================================================

PRINT 'Populating brz_lnd_OPS_EXCEL_GPU with robust data...';

INSERT INTO brz_lnd_OPS_EXCEL_GPU (
    PLANNING_SKU, Product_Line, Business_Unit, Marketing_Code, Planner,
    Customer, Active_Inactive, Level_2_mapping_6, Level_2_usage, CHIP_Family,
    ETL_BatchID, brz_LoadTime
)
SELECT
    -- NULL PLANNING_SKU Strategy (20% NULL rate)
    CASE 
        WHEN ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5 = 0 THEN NULL
        ELSE MATERIAL
    END as PLANNING_SKU,

    [Product Line] as Product_Line,
    [Business Unit] as Business_Unit,
    
    -- Marketing Code (NULL when PLANNING_SKU is NULL)
    CASE 
        WHEN ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5 = 0 THEN NULL
        ELSE 'MKT_' + MATERIAL
    END as Marketing_Code,

    -- ROBUST PLANNER (fits in NVARCHAR(12), no truncation)
    'PLN_GPU_' + RIGHT('00' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 10) + 1 AS VARCHAR), 2) as Planner,

    -- Customer
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 8)
        WHEN 0 THEN 'ASUS'
        WHEN 1 THEN 'MSI'
        WHEN 2 THEN 'EVGA'
        WHEN 3 THEN 'GIGABYTE'
        WHEN 4 THEN 'ZOTAC'
        WHEN 5 THEN 'PNY'
        WHEN 6 THEN 'PALIT'
        ELSE 'INNO3D'
    END as Customer,

    -- Active/Inactive
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4)
        WHEN 0 THEN 'Inactive'
        ELSE 'Active'
    END as Active_Inactive,

    -- Level 2 mapping (NULL when PLANNING_SKU is NULL)
    CASE 
        WHEN ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5 = 0 THEN NULL
        ELSE 'L2_MAP_' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS VARCHAR)
    END as Level_2_mapping_6,

    -- Level 2 usage
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4)
        WHEN 0 THEN 'Gaming'
        WHEN 1 THEN 'Professional'
        WHEN 2 THEN 'Data Center'
        ELSE 'AI/ML'
    END as Level_2_usage,

    -- CHIP Family
    CASE [Product Line]
        WHEN 'RTXGP' THEN 'Ada Lovelace'
        WHEN 'GTXGP' THEN 'Turing'
        WHEN 'QUADR' THEN 'Ampere'
        ELSE 'Hopper'
    END as CHIP_Family,

    1001 as ETL_BatchID,
    GETDATE() as brz_LoadTime

FROM hana_material_master
WHERE [Product Type] = 'GPU'
ORDER BY MATERIAL;

DECLARE @RowCount INT = @@ROWCOUNT;
PRINT 'Inserted ' + CAST(@RowCount AS VARCHAR) + ' records into brz_lnd_OPS_EXCEL_GPU';

-- =====================================================
-- 3. Safe Verification (no divide by zero)
-- =====================================================

PRINT '';
PRINT '=== VERIFICATION (Divide by Zero Safe) ===';

-- Total records
DECLARE @TotalRecords INT = (SELECT COUNT(*) FROM brz_lnd_OPS_EXCEL_GPU);
DECLARE @NullRecords INT = (SELECT COUNT(*) FROM brz_lnd_OPS_EXCEL_GPU WHERE PLANNING_SKU IS NULL);

SELECT 'Total Records' as Description, @TotalRecords as Count;
SELECT 'Records with NULL PLANNING_SKU' as Description, @NullRecords as Count;
SELECT 'Records with PLANNING_SKU' as Description, (@TotalRecords - @NullRecords) as Count;

-- Safe percentage calculation
SELECT 
    'Percentage of NULL PLANNING_SKU' as Description,
    CASE 
        WHEN @TotalRecords = 0 THEN 0.00
        ELSE CAST(@NullRecords * 100.0 / @TotalRecords AS DECIMAL(5,2))
    END as Percentage;

-- Check planner length (should be <= 12)
SELECT 
    'Max Planner Length' as Description,
    ISNULL(MAX(LEN(Planner)), 0) as Max_Length
FROM brz_lnd_OPS_EXCEL_GPU;

-- Sample data
SELECT TOP 10
    PLANNING_SKU,
    Planner,
    LEN(Planner) as Planner_Length,
    Customer,
    Active_Inactive
FROM brz_lnd_OPS_EXCEL_GPU
ORDER BY Planner;

PRINT '';
PRINT '=== ROBUST DATA GENERATION COMPLETE ===';
PRINT 'Summary:';
PRINT '- Fixed planner truncation: All planners fit in NVARCHAR(12)';
PRINT '- Fixed divide by zero: Safe percentage calculations';
PRINT '- Maintained NULL PLANNING_SKU strategy: ~20% NULL rate';
PRINT '- Ready for joins and reconciliation testing';
PRINT '';
