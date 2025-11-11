-- =====================================================
-- Fix OPS_EXCEL_GPU Planner Column Truncation Issue
-- Ensures Planner values fit within NVARCHAR(12) limit
-- =====================================================

SET NOCOUNT ON;
GO

PRINT '=== Fixing OPS_EXCEL_GPU Planner Column Truncation ===';

-- =====================================================
-- 1. Check current state and identify truncation issues
-- =====================================================

PRINT 'Checking current hana_material_master OPS_PLANNER values...';

-- Show sample OPS_PLANNER values and their lengths
SELECT TOP 10
    MATERIAL,
    OPS_PLANNER,
    LEN(OPS_PLANNER) as Planner_Length,
    CASE 
        WHEN LEN(OPS_PLANNER) > 12 THEN 'WILL TRUNCATE'
        ELSE 'OK'
    END as Status
FROM hana_material_master
WHERE [Product Type] = 'GPU'
ORDER BY LEN(OPS_PLANNER) DESC;

-- Count how many records will have truncation issues
SELECT 
    'Records with Planner > 12 chars' as Description,
    COUNT(*) as Count
FROM hana_material_master
WHERE [Product Type] = 'GPU' AND LEN(OPS_PLANNER) > 12;

-- =====================================================
-- 2. Clear existing OPS_EXCEL_GPU data to avoid conflicts
-- =====================================================

PRINT 'Clearing existing brz_lnd_OPS_EXCEL_GPU data...';
TRUNCATE TABLE brz_lnd_OPS_EXCEL_GPU;

-- =====================================================
-- 3. Populate with truncation-safe data
-- =====================================================

PRINT 'Populating brz_lnd_OPS_EXCEL_GPU with truncation-safe Planner values...';

INSERT INTO brz_lnd_OPS_EXCEL_GPU (
    PLANNING_SKU, Product_Line, Business_Unit, Marketing_Code, Planner,
    Customer, Active_Inactive, Level_2_mapping_6, Level_2_usage, CHIP_Family,
    ETL_BatchID, brz_LoadTime
)
SELECT
    -- PLANNING_SKU with NULL strategy
    CASE 
        WHEN ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5 = 0 THEN NULL
        WHEN OPS_STATUS = 'PHASE_OUT' AND ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3 = 0 THEN NULL
        WHEN [Product Line] = 'QUADR' AND ROW_NUMBER() OVER (ORDER BY MATERIAL) % 7 = 0 THEN NULL
        ELSE MATERIAL
    END as PLANNING_SKU,

    [Product Line] as Product_Line,
    [Business Unit] as Business_Unit,
    
    -- Marketing Code
    CASE 
        WHEN ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5 = 0 THEN NULL
        WHEN OPS_STATUS = 'PHASE_OUT' AND ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3 = 0 THEN NULL
        WHEN [Product Line] = 'QUADR' AND ROW_NUMBER() OVER (ORDER BY MATERIAL) % 7 = 0 THEN NULL
        ELSE 'MKT_' + MATERIAL
    END as Marketing_Code,

    -- FIXED PLANNER: Ensure it fits in NVARCHAR(12)
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

    -- Active/Inactive status
    CASE OPS_STATUS
        WHEN 'ACTIVE' THEN 'Active'
        WHEN 'PHASE_OUT' THEN 'Inactive'
        ELSE 'Inactive'
    END as Active_Inactive,

    -- Level 2 mapping
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

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_OPS_EXCEL_GPU';

-- =====================================================
-- 4. Verification
-- =====================================================

PRINT '';
PRINT '=== VERIFICATION ===';

-- Check all Planner values fit within 12 characters
SELECT 
    'Max Planner Length' as Description,
    MAX(LEN(Planner)) as Max_Length
FROM brz_lnd_OPS_EXCEL_GPU;

-- Show sample of Planner values
SELECT TOP 10
    PLANNING_SKU,
    Planner,
    LEN(Planner) as Length,
    Customer,
    Active_Inactive
FROM brz_lnd_OPS_EXCEL_GPU
ORDER BY Planner;

-- Count NULL PLANNING_SKU records
SELECT 
    'Records with NULL PLANNING_SKU' as Description,
    COUNT(*) as Count
FROM brz_lnd_OPS_EXCEL_GPU
WHERE PLANNING_SKU IS NULL;

PRINT '';
PRINT '=== FIX COMPLETE ===';
PRINT 'Summary:';
PRINT '- Fixed Planner column truncation by using short codes (PLN_GPU_01, etc.)';
PRINT '- All Planner values now fit within NVARCHAR(12) limit';
PRINT '- Maintained NULL PLANNING_SKU strategy for testing';
PRINT '- Data ready for joins and reconciliation testing';
PRINT '';
