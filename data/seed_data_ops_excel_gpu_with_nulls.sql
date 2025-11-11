-- =====================================================
-- Enhanced OPS_EXCEL_GPU Seed Data with NULL PLANNING_SKU values
-- Creates realistic test scenarios for NULL handling from the start
-- =====================================================

SET NOCOUNT ON;
GO

PRINT '=== Starting Enhanced OPS_EXCEL_GPU Data Generation ===';

-- =====================================================
-- 1. Clear existing data
-- =====================================================

PRINT 'Clearing existing brz_lnd_OPS_EXCEL_GPU data...';
TRUNCATE TABLE brz_lnd_OPS_EXCEL_GPU;

-- =====================================================
-- 2. Populate brz_lnd_OPS_EXCEL_GPU with strategic NULL values
-- =====================================================

PRINT 'Populating brz_lnd_OPS_EXCEL_GPU with NULL PLANNING_SKU scenarios...';

INSERT INTO brz_lnd_OPS_EXCEL_GPU (
    PLANNING_SKU, Product_Line, Business_Unit, Marketing_Code, Planner,
    Customer, Active_Inactive, Level_2_mapping_6, Level_2_usage, CHIP_Family,
    ETL_BatchID, brz_LoadTime
)
SELECT
    -- STRATEGIC NULL PLANNING_SKU: Set to NULL for specific scenarios
    CASE 
        -- Scenario 1: Every 5th record (20% NULL rate)
        WHEN ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5 = 0 THEN NULL
        
        -- Scenario 2: Some inactive products have missing planning data
        WHEN OPS_STATUS = 'PHASE_OUT' AND ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3 = 0 THEN NULL
        
        -- Scenario 3: Specific product lines might have data quality issues
        WHEN [Product Line] = 'QUADR' AND ROW_NUMBER() OVER (ORDER BY MATERIAL) % 7 = 0 THEN NULL
        
        -- Default: Use MATERIAL as PLANNING_SKU
        ELSE MATERIAL
    END as PLANNING_SKU,

    [Product Line] as Product_Line,
    [Business Unit] as Business_Unit,
    
    -- Marketing Code: NULL when PLANNING_SKU is NULL (cascading data quality issue)
    CASE 
        WHEN ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5 = 0 THEN NULL
        WHEN OPS_STATUS = 'PHASE_OUT' AND ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3 = 0 THEN NULL
        WHEN [Product Line] = 'QUADR' AND ROW_NUMBER() OVER (ORDER BY MATERIAL) % 7 = 0 THEN NULL
        ELSE 'MKT_' + MATERIAL
    END as Marketing_Code,

    -- FIXED PLANNER: Ensure it fits in NVARCHAR(12) limit
    CASE
        WHEN LEN(OPS_PLANNER) <= 12 THEN OPS_PLANNER
        ELSE
            -- Create short planner codes that fit in 12 characters
            CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 10)
                WHEN 0 THEN 'PLN_GPU_01'
                WHEN 1 THEN 'PLN_GPU_02'
                WHEN 2 THEN 'PLN_GPU_03'
                WHEN 3 THEN 'PLN_GPU_04'
                WHEN 4 THEN 'PLN_GPU_05'
                WHEN 5 THEN 'PLN_GPU_06'
                WHEN 6 THEN 'PLN_GPU_07'
                WHEN 7 THEN 'PLN_GPU_08'
                WHEN 8 THEN 'PLN_GPU_09'
                ELSE 'PLN_GPU_10'
            END
    END as Planner,

    -- Customer assignment
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

    -- Active/Inactive status
    CASE OPS_STATUS
        WHEN 'ACTIVE' THEN 'Active'
        WHEN 'PHASE_OUT' THEN 'Inactive'
        ELSE 'Inactive'
    END as Active_Inactive,

    -- Level 2 mapping
    CASE 
        WHEN ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5 = 0 THEN NULL  -- NULL when PLANNING_SKU is NULL
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

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_OPS_EXCEL_GPU';

-- =====================================================
-- 3. Verification and Analysis
-- =====================================================

PRINT '';
PRINT '=== DATA QUALITY ANALYSIS ===';

-- Count total records
SELECT 
    'Total Records' as Description,
    COUNT(*) as Count
FROM brz_lnd_OPS_EXCEL_GPU;

-- Count NULL PLANNING_SKU records
SELECT 
    'Records with NULL PLANNING_SKU' as Description,
    COUNT(*) as Count
FROM brz_lnd_OPS_EXCEL_GPU
WHERE PLANNING_SKU IS NULL;

-- Count non-NULL PLANNING_SKU records
SELECT 
    'Records with PLANNING_SKU' as Description,
    COUNT(*) as Count
FROM brz_lnd_OPS_EXCEL_GPU
WHERE PLANNING_SKU IS NOT NULL;

-- Calculate NULL percentage (with divide by zero protection)
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
-- 4. Show NULL scenarios breakdown
-- =====================================================

PRINT '';
PRINT 'NULL PLANNING_SKU scenarios breakdown:';

-- By Active/Inactive status
SELECT 
    Active_Inactive,
    COUNT(*) as Total_Records,
    SUM(CASE WHEN PLANNING_SKU IS NULL THEN 1 ELSE 0 END) as NULL_PLANNING_SKU,
    CASE
        WHEN COUNT(*) = 0 THEN 0.00
        ELSE CAST(
            SUM(CASE WHEN PLANNING_SKU IS NULL THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0)
            AS DECIMAL(5,2)
        )
    END as NULL_Percentage
FROM brz_lnd_OPS_EXCEL_GPU
GROUP BY Active_Inactive
ORDER BY Active_Inactive;

-- By Product Line
SELECT 
    Product_Line,
    COUNT(*) as Total_Records,
    SUM(CASE WHEN PLANNING_SKU IS NULL THEN 1 ELSE 0 END) as NULL_PLANNING_SKU,
    CASE
        WHEN COUNT(*) = 0 THEN 0.00
        ELSE CAST(
            SUM(CASE WHEN PLANNING_SKU IS NULL THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0)
            AS DECIMAL(5,2)
        )
    END as NULL_Percentage
FROM brz_lnd_OPS_EXCEL_GPU
GROUP BY Product_Line
ORDER BY Product_Line;

-- =====================================================
-- 5. Sample records with NULL PLANNING_SKU
-- =====================================================

PRINT '';
PRINT 'Sample records with NULL PLANNING_SKU:';

SELECT TOP 15
    PLANNING_SKU,
    Product_Line,
    Customer,
    Active_Inactive,
    Level_2_usage,
    Marketing_Code,
    Level_2_mapping_6
FROM brz_lnd_OPS_EXCEL_GPU
WHERE PLANNING_SKU IS NULL
ORDER BY Product_Line, Active_Inactive;

PRINT '';
PRINT '=== DATA GENERATION COMPLETE ===';
PRINT 'Summary:';
PRINT '- Created realistic NULL PLANNING_SKU scenarios (~20-25% NULL rate)';
PRINT '- NULL values concentrated in: Inactive products, QUADR product line, every 5th record';
PRINT '- Cascading NULLs: Marketing_Code and Level_2_mapping_6 also NULL when PLANNING_SKU is NULL';
PRINT '- This enables testing of NULL handling in joins and data quality scenarios';
PRINT '';
