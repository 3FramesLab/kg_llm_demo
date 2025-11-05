-- =====================================================
-- CREATE TABLES AND SEED DATA - Complete Solution
-- Based on newdqschemanov.json schema
-- =====================================================

SET NOCOUNT ON;
GO

PRINT '=====================================================';
PRINT 'CREATING TABLES AND SEEDING DATA';
PRINT '=====================================================';

-- =====================================================
-- 1. CREATE hana_material_master TABLE
-- =====================================================

IF OBJECT_ID('hana_material_master', 'U') IS NOT NULL
    DROP TABLE hana_material_master;

CREATE TABLE hana_material_master (
    MATERIAL NVARCHAR(18) NULL,
    MATERIAL_GROUP NVARCHAR(9) NULL,
    MATERIAL_TYPE NVARCHAR(4) NULL,
    PLANT NVARCHAR(4) NULL,
    [Product Type] NVARCHAR(5) NULL,
    [Business Unit] NVARCHAR(5) NULL,
    [Product Line] NVARCHAR(5) NULL,
    OPS_MKTG_NM NVARCHAR(250) NULL,
    OPS_STATUS NVARCHAR(50) NULL,
    OPS_PLCCODE NVARCHAR(60) NULL,
    PRODGRP_CP NVARCHAR(60) NULL,
    IBP_FINANCE_MKT_NAME NVARCHAR(60) NULL,
    OPS_PLANNER NVARCHAR(250) NULL,
    OPS_PLANNER_LAT NVARCHAR(250) NULL,
    OPS_PLANNER_LAT_TEXT NVARCHAR(20) NULL,
    MAKE_BUY NVARCHAR(1) NULL,
    NBS_ITEM_GRP NVARCHAR(250) NULL,
    AN_PLC_CD NVARCHAR(60) NULL
);

PRINT 'Created hana_material_master table';

-- =====================================================
-- 2. CREATE brz_lnd_RBP_GPU TABLE
-- =====================================================

IF OBJECT_ID('brz_lnd_RBP_GPU', 'U') IS NOT NULL
    DROP TABLE brz_lnd_RBP_GPU;

CREATE TABLE brz_lnd_RBP_GPU (
    Product_Line NVARCHAR(14) NULL,
    Product_Line_Dec NVARCHAR(20) NULL,
    Product_Family NVARCHAR(14) NULL,
    Business_Unit NVARCHAR(13) NULL,
    Material NVARCHAR(18) NULL,
    Fiscal_Year_Period NVARCHAR(71) NULL,
    Overall_Result VARCHAR(255) NULL
);

PRINT 'Created brz_lnd_RBP_GPU table';

-- =====================================================
-- 3. CREATE brz_lnd_OPS_EXCEL_GPU TABLE (Essential columns only)
-- =====================================================

IF OBJECT_ID('brz_lnd_OPS_EXCEL_GPU', 'U') IS NOT NULL
    DROP TABLE brz_lnd_OPS_EXCEL_GPU;

CREATE TABLE brz_lnd_OPS_EXCEL_GPU (
    PLANNING_SKU NVARCHAR(19) NULL,
    Product_Line NVARCHAR(12) NULL,
    Business_Unit NVARCHAR(13) NULL,
    Marketing_Code NVARCHAR(65) NULL,
    Planner NVARCHAR(12) NULL,
    Customer NVARCHAR(8) NULL,
    Active_Inactive NVARCHAR(16) NULL,
    Level_2_mapping_6 NVARCHAR(33) NULL,
    Level_2_usage NVARCHAR(14) NULL,
    CHIP_Family NVARCHAR(14) NULL,
    ETL_BatchID INTEGER NULL,
    brz_LoadTime DATETIME NULL
);

PRINT 'Created brz_lnd_OPS_EXCEL_GPU table';

-- =====================================================
-- 4. CREATE brz_lnd_SKU_LIFNR_Excel TABLE
-- =====================================================

IF OBJECT_ID('brz_lnd_SKU_LIFNR_Excel', 'U') IS NOT NULL
    DROP TABLE brz_lnd_SKU_LIFNR_Excel;

CREATE TABLE brz_lnd_SKU_LIFNR_Excel (
    ETL_BatchID INTEGER NOT NULL,
    brz_RowId INTEGER NOT NULL,
    Material VARCHAR(255) NULL,
    Supplier VARCHAR(255) NULL,
    Production_Version VARCHAR(255) NULL,
    Reference_BOM VARCHAR(255) NULL,
    Planning_BOM VARCHAR(255) NULL,
    Prod_stor_location VARCHAR(255) NULL,
    Receiving_stor_loc_for_material VARCHAR(255) NULL,
    Lead_time VARCHAR(255) NULL,
    Additional_location VARCHAR(255) NULL,
    Storage_Location VARCHAR(255) NULL,
    MRP_Area VARCHAR(255) NULL,
    Product_Type VARCHAR(255) NULL,
    Tlane_Priority VARCHAR(255) NULL,
    Transform_Flag VARCHAR(255) NULL,
    Created_By VARCHAR(255) NULL,
    Created_On VARCHAR(255) NULL,
    Created_Time VARCHAR(255) NULL,
    Changed_By VARCHAR(255) NULL,
    Changed_Date VARCHAR(255) NULL,
    Changed_Time VARCHAR(255) NULL,
    Purchasing_group VARCHAR(255) NULL,
    Automated VARCHAR(255) NULL,
    brz_LoadTime DATETIME NULL
);

PRINT 'Created brz_lnd_SKU_LIFNR_Excel table';

-- =====================================================
-- 5. CREATE brz_lnd_IBP_Product_Master TABLE (Essential columns only)
-- =====================================================

IF OBJECT_ID('brz_lnd_IBP_Product_Master', 'U') IS NOT NULL
    DROP TABLE brz_lnd_IBP_Product_Master;

CREATE TABLE brz_lnd_IBP_Product_Master (
    field1 NVARCHAR(5) NULL,
    SCNID NVARCHAR(12) NULL,
    PRDID NVARCHAR(31) NULL,
    UOMID NVARCHAR(9) NULL,
    ZBASEMATERIAL NVARCHAR(34) NULL,
    ZBOM1TXT NVARCHAR(40) NULL,
    ZBOM1 NVARCHAR(18) NULL,
    ZBOM1QTYPER NVARCHAR(12) NULL,
    ZBOM2 NVARCHAR(18) NULL,
    ZBOM2QTYPER NVARCHAR(12) NULL,
    ZBOM3 NVARCHAR(18) NULL,
    ZBOM3QTYPER NVARCHAR(12) NULL,
    ZBOM4 NVARCHAR(18) NULL,
    ZBOM4QTYPER NVARCHAR(12) NULL
);

PRINT 'Created brz_lnd_IBP_Product_Master table';

-- =====================================================
-- 6. CREATE brz_lnd_SAR_Excel_GPU TABLE
-- =====================================================

IF OBJECT_ID('brz_lnd_SAR_Excel_GPU', 'U') IS NOT NULL
    DROP TABLE brz_lnd_SAR_Excel_GPU;

CREATE TABLE brz_lnd_SAR_Excel_GPU (
    Fiscal_Year_Period NVARCHAR(27) NULL,
    Overall_Result VARCHAR(255) NULL,
    Material NVARCHAR(18) NULL
);

PRINT 'Created brz_lnd_SAR_Excel_GPU table';

-- =====================================================
-- 7. CREATE brz_lnd_GPU_SKU_IN_SKULIFNR TABLE
-- =====================================================

IF OBJECT_ID('brz_lnd_GPU_SKU_IN_SKULIFNR', 'U') IS NOT NULL
    DROP TABLE brz_lnd_GPU_SKU_IN_SKULIFNR;

CREATE TABLE brz_lnd_GPU_SKU_IN_SKULIFNR (
    PLANNING_SKU NVARCHAR(19) NULL,
    Prd_Type NVARCHAR(5) NULL
);

PRINT 'Created brz_lnd_GPU_SKU_IN_SKULIFNR table';

-- =====================================================
-- 8. CREATE brz_lnd_SAR_Excel_NBU TABLE
-- =====================================================

IF OBJECT_ID('brz_lnd_SAR_Excel_NBU', 'U') IS NOT NULL
    DROP TABLE brz_lnd_SAR_Excel_NBU;

CREATE TABLE brz_lnd_SAR_Excel_NBU (
    Fiscal_Year_Period NVARCHAR(27) NULL,
    Overall_Result VARCHAR(255) NULL,
    Material NVARCHAR(18) NULL
);

PRINT 'Created brz_lnd_SAR_Excel_NBU table';

PRINT '';
PRINT '=====================================================';
PRINT 'ALL TABLES CREATED SUCCESSFULLY!';
PRINT 'Now proceeding with data insertion...';
PRINT '=====================================================';

-- =====================================================
-- DATA INSERTION STARTS HERE
-- =====================================================

-- Generate 500 records using recursive CTE
WITH Numbers AS (
    SELECT 1 as RowNum
    UNION ALL
    SELECT RowNum + 1
    FROM Numbers
    WHERE RowNum < 500
),
MaterialData AS (
    SELECT 
        RowNum,
        CASE 
            WHEN RowNum <= 250 THEN 'GPU'
            ELSE 'NBU'
        END as ProductType
    FROM Numbers
)
INSERT INTO hana_material_master (
    MATERIAL, MATERIAL_GROUP, MATERIAL_TYPE, PLANT, [Product Type], 
    [Business Unit], [Product Line], OPS_MKTG_NM, OPS_STATUS, OPS_PLCCODE,
    PRODGRP_CP, IBP_FINANCE_MKT_NAME, OPS_PLANNER, OPS_PLANNER_LAT,
    OPS_PLANNER_LAT_TEXT, MAKE_BUY, NBS_ITEM_GRP, AN_PLC_CD
)
SELECT 
    -- Material ID: GPU-001 to GPU-250, NBU-001 to NBU-250
    CASE 
        WHEN ProductType = 'GPU' THEN 'GPU-' + RIGHT('000' + CAST(RowNum AS VARCHAR), 3)
        ELSE 'NBU-' + RIGHT('000' + CAST(RowNum - 250 AS VARCHAR), 3)
    END as MATERIAL,
    
    -- Material Group
    CASE ProductType 
        WHEN 'GPU' THEN 'GPUGRP' + CAST((RowNum % 5) + 1 AS VARCHAR)
        ELSE 'NBUGRP' + CAST((RowNum % 3) + 1 AS VARCHAR)
    END as MATERIAL_GROUP,
    
    -- Material Type
    CASE ProductType WHEN 'GPU' THEN 'FERT' ELSE 'HALB' END as MATERIAL_TYPE,
    
    -- Plant
    CASE (RowNum % 4)
        WHEN 0 THEN 'P001'
        WHEN 1 THEN 'P002' 
        WHEN 2 THEN 'P003'
        ELSE 'P004'
    END as PLANT,
    
    ProductType as [Product Type],
    
    -- Business Unit
    CASE ProductType 
        WHEN 'GPU' THEN 'GPUBU'
        ELSE 'NBUBU'
    END as [Business Unit],
    
    -- Product Line
    CASE ProductType
        WHEN 'GPU' THEN 
            CASE (RowNum % 4)
                WHEN 0 THEN 'RTXGP'
                WHEN 1 THEN 'GTXGP'
                WHEN 2 THEN 'QUADR'
                ELSE 'TESLA'
            END
        ELSE 
            CASE (RowNum % 3)
                WHEN 0 THEN 'DRIVE'
                WHEN 1 THEN 'JETSO'
                ELSE 'ORIN'
            END
    END as [Product Line],
    
    -- Marketing Name
    CASE ProductType
        WHEN 'GPU' THEN 'GeForce RTX ' + CAST(4000 + (RowNum % 100) AS VARCHAR)
        ELSE 'Jetson ' + CASE (RowNum % 3) WHEN 0 THEN 'Nano' WHEN 1 THEN 'Xavier' ELSE 'Orin' END
    END as OPS_MKTG_NM,
    
    -- Status
    CASE (RowNum % 10) 
        WHEN 0 THEN 'DISCONTINUED'
        WHEN 1 THEN 'PHASE_OUT'
        ELSE 'ACTIVE'
    END as OPS_STATUS,
    
    -- PLC Code
    'PLC' + RIGHT('000' + CAST(RowNum AS VARCHAR), 3) as OPS_PLCCODE,
    
    -- Product Group
    CASE ProductType
        WHEN 'GPU' THEN 'Graphics Processing Units'
        ELSE 'Network Business Units'
    END as PRODGRP_CP,
    
    -- Finance Marketing Name
    CASE ProductType
        WHEN 'GPU' THEN 'GPU_FIN_' + CAST(RowNum AS VARCHAR)
        ELSE 'NBU_FIN_' + CAST(RowNum AS VARCHAR)
    END as IBP_FINANCE_MKT_NAME,
    
    -- Planner
    'PLANNER_' + CAST((RowNum % 10) + 1 AS VARCHAR) as OPS_PLANNER,
    
    -- Planner LAT
    'PLANNER_LAT_' + CAST((RowNum % 10) + 1 AS VARCHAR) as OPS_PLANNER_LAT,
    
    -- OPS Planner LAT Text
    'LAT_' + CAST((RowNum % 10) + 1 AS VARCHAR) as OPS_PLANNER_LAT_TEXT,
    
    -- Make Buy
    CASE (RowNum % 2) WHEN 0 THEN 'M' ELSE 'B' END as MAKE_BUY,
    
    -- NBS Item Group
    CASE ProductType
        WHEN 'GPU' THEN 'GPU_ITEM_GROUP'
        ELSE 'NBU_ITEM_GROUP'
    END as NBS_ITEM_GRP,
    
    -- AN PLC Code
    'AN_' + RIGHT('000' + CAST(RowNum AS VARCHAR), 3) as AN_PLC_CD

FROM MaterialData
OPTION (MAXRECURSION 500);

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into hana_material_master';

-- =====================================================
-- INSERT DATA INTO REMAINING TABLES
-- =====================================================

-- 2. BRZ_LND_RBP_GPU (GPU only)
INSERT INTO brz_lnd_RBP_GPU (
    Product_Line, Product_Line_Dec, Product_Family, Business_Unit,
    Material, Fiscal_Year_Period, Overall_Result
)
SELECT
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4)
        WHEN 0 THEN 'RTXGP'
        WHEN 1 THEN 'GTXGP'
        WHEN 2 THEN 'QUADR'
        ELSE 'TESLA'
    END as Product_Line,

    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4)
        WHEN 0 THEN 'RTX Graphics'
        WHEN 1 THEN 'GTX Graphics'
        WHEN 2 THEN 'Quadro Professional'
        ELSE 'Tesla Compute'
    END as Product_Line_Dec,

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
    '2024.' + RIGHT('00' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 12) + 1 AS VARCHAR), 2) as Fiscal_Year_Period,

    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5)
        WHEN 0 THEN 'Exceeds Target'
        WHEN 1 THEN 'Meets Target'
        WHEN 2 THEN 'Below Target'
        WHEN 3 THEN 'Significantly Below'
        ELSE 'Under Review'
    END as Overall_Result

FROM hana_material_master
WHERE [Product Type] = 'GPU';

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_RBP_GPU';

-- 3. BRZ_LND_OPS_EXCEL_GPU (GPU only)
INSERT INTO brz_lnd_OPS_EXCEL_GPU (
    PLANNING_SKU, Product_Line, Business_Unit, Marketing_Code, Planner,
    Customer, Active_Inactive, Level_2_mapping_6, Level_2_usage, CHIP_Family,
    ETL_BatchID, brz_LoadTime
)
SELECT
    MATERIAL as PLANNING_SKU,
    [Product Line] as Product_Line,
    [Business Unit] as Business_Unit,
    'MKT_' + MATERIAL as Marketing_Code,
    OPS_PLANNER as Planner,

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

    CASE OPS_STATUS
        WHEN 'ACTIVE' THEN 'Active'
        WHEN 'PHASE_OUT' THEN 'Inactive'
        ELSE 'Inactive'
    END as Active_Inactive,

    'L2_MAP_' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS VARCHAR) as Level_2_mapping_6,

    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4)
        WHEN 0 THEN 'Gaming'
        WHEN 1 THEN 'Professional'
        WHEN 2 THEN 'Data Center'
        ELSE 'AI/ML'
    END as Level_2_usage,

    CASE [Product Line]
        WHEN 'RTXGP' THEN 'Ada Lovelace'
        WHEN 'GTXGP' THEN 'Turing'
        WHEN 'QUADR' THEN 'Ampere'
        ELSE 'Hopper'
    END as CHIP_Family,

    1001 as ETL_BatchID,
    GETDATE() as brz_LoadTime

FROM hana_material_master
WHERE [Product Type] = 'GPU';

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_OPS_EXCEL_GPU';

-- 4. BRZ_LND_SKU_LIFNR_Excel (All materials)
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

    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 10)
        WHEN 0 THEN 'SUP001'
        WHEN 1 THEN 'SUP002'
        WHEN 2 THEN 'SUP003'
        WHEN 3 THEN 'SUP004'
        WHEN 4 THEN 'SUP005'
        WHEN 5 THEN 'SUP006'
        WHEN 6 THEN 'SUP007'
        WHEN 7 THEN 'SUP008'
        WHEN 8 THEN 'SUP009'
        ELSE 'SUP010'
    END as Supplier,

    'PV_' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS VARCHAR) as Production_Version,
    'REF_BOM_' + MATERIAL as Reference_BOM,
    'PLAN_BOM_' + MATERIAL as Planning_BOM,
    'PROD_LOC_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) + 1 AS VARCHAR) as Prod_stor_location,
    'REC_LOC_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) + 1 AS VARCHAR) as Receiving_stor_loc_for_material,

    CASE [Product Type]
        WHEN 'GPU' THEN CAST(45 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 30) AS VARCHAR)
        ELSE CAST(30 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 20) AS VARCHAR)
    END as Lead_time,

    'ADD_LOC_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4) + 1 AS VARCHAR) as Additional_location,
    'STOR_LOC_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 6) + 1 AS VARCHAR) as Storage_Location,
    'MRP_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) + 1 AS VARCHAR) as MRP_Area,
    [Product Type] as Product_Type,

    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3)
        WHEN 0 THEN 'HIGH'
        WHEN 1 THEN 'MEDIUM'
        ELSE 'LOW'
    END as Tlane_Priority,

    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 2) WHEN 0 THEN 'Y' ELSE 'N' END as Transform_Flag,
    'USER_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) + 1 AS VARCHAR) as Created_By,
    FORMAT(DATEADD(day, -(ROW_NUMBER() OVER (ORDER BY MATERIAL) % 60), GETDATE()), 'yyyy-MM-dd') as Created_On,
    FORMAT(DATEADD(minute, ROW_NUMBER() OVER (ORDER BY MATERIAL) % 1440, '00:00:00'), 'HH:mm:ss') as Created_Time,
    'USER_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) + 1 AS VARCHAR) as Changed_By,
    FORMAT(DATEADD(day, -(ROW_NUMBER() OVER (ORDER BY MATERIAL) % 30), GETDATE()), 'yyyy-MM-dd') as Changed_Date,
    FORMAT(DATEADD(minute, ROW_NUMBER() OVER (ORDER BY MATERIAL) % 1440, '00:00:00'), 'HH:mm:ss') as Changed_Time,

    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5)
        WHEN 0 THEN 'PG001'
        WHEN 1 THEN 'PG002'
        WHEN 2 THEN 'PG003'
        WHEN 3 THEN 'PG004'
        ELSE 'PG005'
    END as Purchasing_group,

    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3)
        WHEN 0 THEN 'Yes'
        WHEN 1 THEN 'No'
        ELSE 'Partial'
    END as Automated,

    GETDATE() as brz_LoadTime

FROM hana_material_master;

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_SKU_LIFNR_Excel';

-- 5. BRZ_LND_IBP_Product_Master (All materials)
INSERT INTO brz_lnd_IBP_Product_Master (
    field1, SCNID, PRDID, UOMID, ZBASEMATERIAL, ZBOM1TXT, ZBOM1,
    ZBOM1QTYPER, ZBOM2, ZBOM2QTYPER, ZBOM3, ZBOM3QTYPER, ZBOM4, ZBOM4QTYPER
)
SELECT
    CASE [Product Type] WHEN 'GPU' THEN 'GPU' ELSE 'NBU' END as field1,
    'SCN' + RIGHT('000' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS VARCHAR), 3) as SCNID,
    'PRD_' + MATERIAL as PRDID,
    CASE [Product Type] WHEN 'GPU' THEN 'EA' ELSE 'PC' END as UOMID,
    MATERIAL as ZBASEMATERIAL,
    CASE [Product Type] WHEN 'GPU' THEN 'GPU Die' ELSE 'Processing Unit' END as ZBOM1TXT,
    'BOM1_' + MATERIAL as ZBOM1,
    '1.000' as ZBOM1QTYPER,
    'BOM2_' + MATERIAL as ZBOM2,
    CASE [Product Type]
        WHEN 'GPU' THEN CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 8) + 1 AS VARCHAR) + '.000'
        ELSE '2.000'
    END as ZBOM2QTYPER,
    'BOM3_' + MATERIAL as ZBOM3,
    '1.000' as ZBOM3QTYPER,
    'BOM4_' + MATERIAL as ZBOM4,
    '1.000' as ZBOM4QTYPER

FROM hana_material_master;

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_IBP_Product_Master';

-- 6. BRZ_LND_SAR_Excel_GPU (GPU only)
INSERT INTO brz_lnd_SAR_Excel_GPU (
    Fiscal_Year_Period, Overall_Result, Material
)
SELECT
    '2024.' + RIGHT('00' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 12) + 1 AS VARCHAR), 2) as Fiscal_Year_Period,
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 6)
        WHEN 0 THEN 'Excellent Performance'
        WHEN 1 THEN 'Good Performance'
        WHEN 2 THEN 'Average Performance'
        WHEN 3 THEN 'Below Average'
        WHEN 4 THEN 'Poor Performance'
        ELSE 'Under Investigation'
    END as Overall_Result,
    MATERIAL

FROM hana_material_master
WHERE [Product Type] = 'GPU';

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_SAR_Excel_GPU';

-- 7. BRZ_LND_GPU_SKU_IN_SKULIFNR (GPU only)
INSERT INTO brz_lnd_GPU_SKU_IN_SKULIFNR (
    PLANNING_SKU, Prd_Type
)
SELECT
    MATERIAL as PLANNING_SKU,
    [Product Type] as Prd_Type

FROM hana_material_master
WHERE [Product Type] = 'GPU';

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_GPU_SKU_IN_SKULIFNR';

-- 8. BRZ_LND_SAR_Excel_NBU (NBU only)
INSERT INTO brz_lnd_SAR_Excel_NBU (
    Fiscal_Year_Period, Overall_Result, Material
)
SELECT
    '2024.' + RIGHT('00' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 12) + 1 AS VARCHAR), 2) as Fiscal_Year_Period,
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 6)
        WHEN 0 THEN 'Outstanding Results'
        WHEN 1 THEN 'Strong Performance'
        WHEN 2 THEN 'Satisfactory'
        WHEN 3 THEN 'Needs Improvement'
        WHEN 4 THEN 'Critical Issues'
        ELSE 'Action Required'
    END as Overall_Result,
    MATERIAL

FROM hana_material_master
WHERE [Product Type] = 'NBU';

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_SAR_Excel_NBU';

-- =====================================================
-- FINAL VALIDATION
-- =====================================================

PRINT '';
PRINT '=====================================================';
PRINT 'DATA VALIDATION SUMMARY';
PRINT '=====================================================';

-- Count by table
SELECT 'hana_material_master' as TableName, COUNT(*) as RecordCount FROM hana_material_master
UNION ALL
SELECT 'brz_lnd_RBP_GPU', COUNT(*) FROM brz_lnd_RBP_GPU
UNION ALL
SELECT 'brz_lnd_OPS_EXCEL_GPU', COUNT(*) FROM brz_lnd_OPS_EXCEL_GPU
UNION ALL
SELECT 'brz_lnd_SKU_LIFNR_Excel', COUNT(*) FROM brz_lnd_SKU_LIFNR_Excel
UNION ALL
SELECT 'brz_lnd_IBP_Product_Master', COUNT(*) FROM brz_lnd_IBP_Product_Master
UNION ALL
SELECT 'brz_lnd_SAR_Excel_GPU', COUNT(*) FROM brz_lnd_SAR_Excel_GPU
UNION ALL
SELECT 'brz_lnd_GPU_SKU_IN_SKULIFNR', COUNT(*) FROM brz_lnd_GPU_SKU_IN_SKULIFNR
UNION ALL
SELECT 'brz_lnd_SAR_Excel_NBU', COUNT(*) FROM brz_lnd_SAR_Excel_NBU;

PRINT '';
PRINT 'Product Type Distribution:';

-- Count by Product Type
SELECT
    [Product Type],
    COUNT(*) as Count
FROM hana_material_master
GROUP BY [Product Type];

PRINT '';
PRINT 'Sample Material IDs:';

-- Sample records
SELECT TOP 10
    MATERIAL,
    [Product Type],
    [Business Unit],
    [Product Line],
    OPS_MKTG_NM
FROM hana_material_master
ORDER BY MATERIAL;

PRINT '';
PRINT '=====================================================';
PRINT 'COMPLETE SUCCESS!';
PRINT 'Created 8 tables and inserted 500 items (250 GPU + 250 NBU)';
PRINT 'All tables populated with consistent relationships';
PRINT '=====================================================';

SET NOCOUNT OFF;
GO
