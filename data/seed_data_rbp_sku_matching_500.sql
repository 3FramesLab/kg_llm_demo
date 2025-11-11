-- =====================================================
-- RBP GPU & SKU LIFNR Excel Matching Seed Data (500 Records)
-- Ensures proper matching between brz_lnd_RBP_GPU and brz_lnd_SKU_LIFNR_Excel
-- =====================================================

SET NOCOUNT ON;
GO

PRINT '=== Starting RBP GPU & SKU LIFNR Excel Matching Data Generation ===';

-- =====================================================
-- 1. Clear existing data in target tables
-- =====================================================

PRINT 'Clearing existing data...';
TRUNCATE TABLE brz_lnd_RBP_GPU;
TRUNCATE TABLE brz_lnd_SKU_LIFNR_Excel;

-- =====================================================
-- 2. Populate brz_lnd_RBP_GPU (GPU materials only - 250 records)
-- =====================================================

PRINT 'Populating brz_lnd_RBP_GPU with 250 GPU records...';

INSERT INTO brz_lnd_RBP_GPU (
    Product_Line, Product_Line_Dec, Product_Family, Business_Unit, 
    Material, Fiscal_Year_Period, Overall_Result
)
SELECT
    -- Product Line
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5)
        WHEN 0 THEN 'GeForce RTX'
        WHEN 1 THEN 'GeForce GTX'
        WHEN 2 THEN 'Quadro RTX'
        WHEN 3 THEN 'Tesla V100'
        ELSE 'Tesla A100'
    END as Product_Line,

    -- Product Line Description
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5)
        WHEN 0 THEN 'GeForce RTX Gaming'
        WHEN 1 THEN 'GeForce GTX Gaming'
        WHEN 2 THEN 'Quadro Professional'
        WHEN 3 THEN 'Tesla Data Center'
        ELSE 'Tesla Compute'
    END as Product_Line_Dec,

    -- Product Family
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 6)
        WHEN 0 THEN 'RTX40_SERIES'
        WHEN 1 THEN 'RTX30_SERIES'
        WHEN 2 THEN 'GTX16_SERIES'
        WHEN 3 THEN 'QUADRO_RTX'
        WHEN 4 THEN 'TESLA_V100'
        ELSE 'TESLA_A100'
    END as Product_Family,

    'GPU_BUSINESS' as Business_Unit,
    MATERIAL,
    
    -- Fiscal Year Period (2024.01 to 2024.12)
    '2024.' + RIGHT('00' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 12) + 1 AS VARCHAR), 2) as Fiscal_Year_Period,

    -- Overall Result
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5)
        WHEN 0 THEN 'Exceeds Target'
        WHEN 1 THEN 'Meets Target'
        WHEN 2 THEN 'Below Target'
        WHEN 3 THEN 'Significantly Below'
        ELSE 'Under Review'
    END as Overall_Result

FROM hana_material_master
WHERE [Product Type] = 'GPU'
ORDER BY MATERIAL;

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_RBP_GPU';

-- =====================================================
-- 3. Populate brz_lnd_SKU_LIFNR_Excel (ALL materials - 500 records)
--    This ensures GPU materials from RBP_GPU have matching entries
-- =====================================================

PRINT 'Populating brz_lnd_SKU_LIFNR_Excel with 500 records (250 GPU + 250 NBU)...';

INSERT INTO brz_lnd_SKU_LIFNR_Excel (
    ETL_BatchID, brz_RowId, Material, Supplier, Production_Version,
    Reference_BOM, Planning_BOM, Prod_stor_location, Receiving_stor_loc_for_material,
    Lead_time, Additional_location, Storage_Location, MRP_Area, Product_Type,
    Tlane_Priority, Transform_Flag, Created_By, Created_On, Created_Time,
    Changed_By, Changed_Date, Changed_Time, Purchasing_group, Automated, brz_LoadTime
)
SELECT
    1001 as ETL_BatchID,
    ROW_NUMBER() OVER (ORDER BY MATERIAL) as brz_RowId,
    MATERIAL,

    -- Supplier (10 different suppliers)
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 10)
        WHEN 0 THEN 'TSMC_001'
        WHEN 1 THEN 'SAMSUNG_002'
        WHEN 2 THEN 'GLOBALFOUNDRIES_003'
        WHEN 3 THEN 'INTEL_004'
        WHEN 4 THEN 'ASML_005'
        WHEN 5 THEN 'APPLIED_MATERIALS_006'
        WHEN 6 THEN 'LAM_RESEARCH_007'
        WHEN 7 THEN 'KLA_CORP_008'
        WHEN 8 THEN 'TOKYO_ELECTRON_009'
        ELSE 'AMAT_010'
    END as Supplier,

    'PV_' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS VARCHAR) as Production_Version,
    'REF_BOM_' + MATERIAL as Reference_BOM,
    'PLAN_BOM_' + MATERIAL as Planning_BOM,
    
    -- Production Storage Location
    'PROD_LOC_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) + 1 AS VARCHAR) as Prod_stor_location,
    
    -- Receiving Storage Location
    'REC_LOC_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) + 1 AS VARCHAR) as Receiving_stor_loc_for_material,

    -- Lead Time (GPU: 45-75 days, NBU: 30-50 days)
    CASE [Product Type]
        WHEN 'GPU' THEN CAST(45 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 30) AS VARCHAR)
        ELSE CAST(30 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 20) AS VARCHAR)
    END as Lead_time,

    'ADD_LOC_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4) + 1 AS VARCHAR) as Additional_location,
    'STOR_LOC_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 6) + 1 AS VARCHAR) as Storage_Location,
    'MRP_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) + 1 AS VARCHAR) as MRP_Area,
    [Product Type] as Product_Type,

    -- T-lane Priority
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3)
        WHEN 0 THEN 'HIGH'
        WHEN 1 THEN 'MEDIUM'
        ELSE 'LOW'
    END as Tlane_Priority,

    -- Transform Flag
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 2) WHEN 0 THEN 'Y' ELSE 'N' END as Transform_Flag,
    
    -- Created By
    'USER_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) + 1 AS VARCHAR) as Created_By,
    
    -- Created On (last 60 days)
    FORMAT(DATEADD(day, -(ROW_NUMBER() OVER (ORDER BY MATERIAL) % 60), GETDATE()), 'yyyy-MM-dd') as Created_On,
    
    -- Created Time
    FORMAT(DATEADD(minute, ROW_NUMBER() OVER (ORDER BY MATERIAL) % 1440, '00:00:00'), 'HH:mm:ss') as Created_Time,
    
    -- Changed By
    'USER_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) + 1 AS VARCHAR) as Changed_By,
    
    -- Changed Date (last 30 days)
    FORMAT(DATEADD(day, -(ROW_NUMBER() OVER (ORDER BY MATERIAL) % 30), GETDATE()), 'yyyy-MM-dd') as Changed_Date,
    
    -- Changed Time
    FORMAT(DATEADD(minute, ROW_NUMBER() OVER (ORDER BY MATERIAL) % 1440, '00:00:00'), 'HH:mm:ss') as Changed_Time,

    -- Purchasing Group
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5)
        WHEN 0 THEN 'PG_GPU_001'
        WHEN 1 THEN 'PG_GPU_002'
        WHEN 2 THEN 'PG_NBU_003'
        WHEN 3 THEN 'PG_NBU_004'
        ELSE 'PG_MIXED_005'
    END as Purchasing_group,

    -- Automated
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3)
        WHEN 0 THEN 'Yes'
        WHEN 1 THEN 'No'
        ELSE 'Partial'
    END as Automated,

    GETDATE() as brz_LoadTime

FROM hana_material_master
ORDER BY MATERIAL;

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_SKU_LIFNR_Excel';

-- =====================================================
-- 4. Verification - Show matching records
-- =====================================================

PRINT '';
PRINT '=== VERIFICATION RESULTS ===';

-- Count records in each table
SELECT 'brz_lnd_RBP_GPU' as Table_Name, COUNT(*) as Record_Count FROM brz_lnd_RBP_GPU
UNION ALL
SELECT 'brz_lnd_SKU_LIFNR_Excel' as Table_Name, COUNT(*) as Record_Count FROM brz_lnd_SKU_LIFNR_Excel;

-- Show matching GPU materials between the tables
PRINT '';
PRINT 'GPU Materials that match between RBP_GPU and SKU_LIFNR_Excel:';

SELECT
    r.Material as RBP_Material,
    s.Material as SKU_Material,
    r.Product_Line,
    s.Supplier,
    s.Lead_time
FROM brz_lnd_RBP_GPU r
INNER JOIN brz_lnd_SKU_LIFNR_Excel s ON r.Material = s.Material
WHERE s.Product_Type = 'GPU'
ORDER BY r.Material;

-- Show count of matching records
SELECT
    'Matching GPU Records' as Description,
    COUNT(*) as Count
FROM brz_lnd_RBP_GPU r
INNER JOIN brz_lnd_SKU_LIFNR_Excel s ON r.Material = s.Material
WHERE s.Product_Type = 'GPU';

-- Show sample of non-matching records (NBU in SKU_LIFNR_Excel but not in RBP_GPU)
PRINT '';
PRINT 'Sample NBU Materials in SKU_LIFNR_Excel (not in RBP_GPU):';

SELECT TOP 10
    s.Material,
    s.Product_Type,
    s.Supplier,
    s.Lead_time
FROM brz_lnd_SKU_LIFNR_Excel s
LEFT JOIN brz_lnd_RBP_GPU r ON s.Material = r.Material
WHERE r.Material IS NULL
AND s.Product_Type = 'NBU'
ORDER BY s.Material;

PRINT '';
PRINT '=== DATA GENERATION COMPLETE ===';
PRINT 'Summary:';
PRINT '- brz_lnd_RBP_GPU: 250 GPU records';
PRINT '- brz_lnd_SKU_LIFNR_Excel: 500 records (250 GPU + 250 NBU)';
PRINT '- All 250 GPU materials in RBP_GPU have matching entries in SKU_LIFNR_Excel';
PRINT '- Additional 250 NBU materials in SKU_LIFNR_Excel for comprehensive coverage';
PRINT '';
