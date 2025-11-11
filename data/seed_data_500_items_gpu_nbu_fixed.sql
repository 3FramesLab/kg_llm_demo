-- =====================================================
-- FIXED: Comprehensive Seed Data for 500 Items (GPU & NBU)
-- Based on newdqschemanov.json schema - SQL Server Compatible
-- =====================================================

-- Disable constraints for bulk insert
SET NOCOUNT ON;
GO

-- =====================================================
-- 1. HANA MATERIAL MASTER (Master Data - 500 records)
-- =====================================================

-- Clear existing data
TRUNCATE TABLE hana_material_master;

-- Generate 500 records using recursive CTE with MAXRECURSION
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
-- 2. BRZ_LND_RBP_GPU (Revenue Business Planning - GPU)
-- =====================================================

TRUNCATE TABLE brz_lnd_RBP_GPU;

INSERT INTO brz_lnd_RBP_GPU (
    Product_Line, Product_Line_Dec, Product_Family, Business_Unit, 
    Material, Fiscal_Year_Period, Overall_Result
)
SELECT 
    -- Product Line
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4)
        WHEN 0 THEN 'RTXGP'
        WHEN 1 THEN 'GTXGP' 
        WHEN 2 THEN 'QUADR'
        ELSE 'TESLA'
    END as Product_Line,
    
    -- Product Line Description
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4)
        WHEN 0 THEN 'RTX Graphics'
        WHEN 1 THEN 'GTX Graphics'
        WHEN 2 THEN 'Quadro Professional'
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
    
    -- Business Unit
    'GPU_BUSINESS' as Business_Unit,
    
    -- Material (matching hana_material_master)
    MATERIAL,
    
    -- Fiscal Year Period
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
WHERE [Product Type] = 'GPU';

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_RBP_GPU';

-- =====================================================
-- 3. BRZ_LND_OPS_EXCEL_GPU (Operations Excel - GPU)
-- =====================================================

TRUNCATE TABLE brz_lnd_OPS_EXCEL_GPU;

INSERT INTO brz_lnd_OPS_EXCEL_GPU (
    PLANNING_SKU, Product_Line, Business_Unit, Marketing_Code, Planner,
    Customer, Active_Inactive, Level_2_mapping_6, Level_2_usage, CHIP_Family,
    ETL_BatchID, brz_LoadTime
)
SELECT 
    -- Planning SKU (matches Material from hana_material_master)
    MATERIAL as PLANNING_SKU,
    
    -- Product Line
    [Product Line] as Product_Line,
    
    -- Business Unit  
    [Business Unit] as Business_Unit,
    
    -- Marketing Code
    'MKT_' + MATERIAL as Marketing_Code,
    
    -- Planner
    OPS_PLANNER as Planner,
    
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
    CASE OPS_STATUS
        WHEN 'ACTIVE' THEN 'Active'
        WHEN 'PHASE_OUT' THEN 'Inactive'
        ELSE 'Inactive'
    END as Active_Inactive,
    
    -- Level 2 Mapping
    'L2_MAP_' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS VARCHAR) as Level_2_mapping_6,
    
    -- Level 2 Usage
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4)
        WHEN 0 THEN 'Gaming'
        WHEN 1 THEN 'Professional'
        WHEN 2 THEN 'Data Center'
        ELSE 'AI/ML'
    END as Level_2_usage,
    
    -- Chip Family
    CASE [Product Line]
        WHEN 'RTXGP' THEN 'Ada Lovelace'
        WHEN 'GTXGP' THEN 'Turing'
        WHEN 'QUADR' THEN 'Ampere'
        ELSE 'Hopper'
    END as CHIP_Family,
    
    -- ETL Batch ID
    1001 as ETL_BatchID,
    
    -- Load Time
    GETDATE() as brz_LoadTime

FROM hana_material_master 
WHERE [Product Type] = 'GPU';

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_OPS_EXCEL_GPU';

-- =====================================================
-- 4. BRZ_LND_SKU_LIFNR_EXCEL (SKU Supplier Excel)
-- =====================================================

TRUNCATE TABLE brz_lnd_SKU_LIFNR_Excel;

INSERT INTO brz_lnd_SKU_LIFNR_Excel (
    ETL_BatchID, brz_RowId, Material, Supplier, Production_Version,
    Reference_BOM, Planning_BOM, Prod_stor_location, Receiving_stor_loc_for_material,
    Lead_time, Additional_location, Storage_Location, MRP_Area, Product_Type,
    Tlane_Priority, Transform_Flag, Created_By, Created_On, Created_Time,
    Changed_By, Changed_Date, Changed_Time, Purchasing_group, Automated, brz_LoadTime
)
SELECT
    -- ETL Batch ID
    1001 as ETL_BatchID,

    -- BRZ Row ID
    ROW_NUMBER() OVER (ORDER BY MATERIAL) as brz_RowId,

    -- Material (matches hana_material_master)
    MATERIAL,

    -- Supplier
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

    -- Production Version
    'PV_' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS VARCHAR) as Production_Version,

    -- Reference BOM
    'REF_BOM_' + MATERIAL as Reference_BOM,

    -- Planning BOM
    'PLAN_BOM_' + MATERIAL as Planning_BOM,

    -- Production Storage Location
    'PROD_LOC_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) + 1 AS VARCHAR) as Prod_stor_location,

    -- Receiving Storage Location
    'REC_LOC_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) + 1 AS VARCHAR) as Receiving_stor_loc_for_material,

    -- Lead Time
    CASE [Product Type]
        WHEN 'GPU' THEN CAST(45 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 30) AS VARCHAR)
        ELSE CAST(30 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 20) AS VARCHAR)
    END as Lead_time,

    -- Additional Location
    'ADD_LOC_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4) + 1 AS VARCHAR) as Additional_location,

    -- Storage Location
    'STOR_LOC_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 6) + 1 AS VARCHAR) as Storage_Location,

    -- MRP Area
    'MRP_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) + 1 AS VARCHAR) as MRP_Area,

    -- Product Type
    [Product Type] as Product_Type,

    -- Tlane Priority
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3)
        WHEN 0 THEN 'HIGH'
        WHEN 1 THEN 'MEDIUM'
        ELSE 'LOW'
    END as Tlane_Priority,

    -- Transform Flag
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 2) WHEN 0 THEN 'Y' ELSE 'N' END as Transform_Flag,

    -- Created By
    'USER_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) + 1 AS VARCHAR) as Created_By,

    -- Created On
    FORMAT(DATEADD(day, -(ROW_NUMBER() OVER (ORDER BY MATERIAL) % 60), GETDATE()), 'yyyy-MM-dd') as Created_On,

    -- Created Time
    FORMAT(DATEADD(minute, ROW_NUMBER() OVER (ORDER BY MATERIAL) % 1440, '00:00:00'), 'HH:mm:ss') as Created_Time,

    -- Changed By
    'USER_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) + 1 AS VARCHAR) as Changed_By,

    -- Changed Date
    FORMAT(DATEADD(day, -(ROW_NUMBER() OVER (ORDER BY MATERIAL) % 30), GETDATE()), 'yyyy-MM-dd') as Changed_Date,

    -- Changed Time
    FORMAT(DATEADD(minute, ROW_NUMBER() OVER (ORDER BY MATERIAL) % 1440, '00:00:00'), 'HH:mm:ss') as Changed_Time,

    -- Purchasing Group
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5)
        WHEN 0 THEN 'PG001'
        WHEN 1 THEN 'PG002'
        WHEN 2 THEN 'PG003'
        WHEN 3 THEN 'PG004'
        ELSE 'PG005'
    END as Purchasing_group,

    -- Automated
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3)
        WHEN 0 THEN 'Yes'
        WHEN 1 THEN 'No'
        ELSE 'Partial'
    END as Automated,

    -- Load Time
    GETDATE() as brz_LoadTime

FROM hana_material_master;

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_SKU_LIFNR_Excel';

-- =====================================================
-- 5. BRZ_LND_IBP_PRODUCT_MASTER (IBP Product Master)
-- =====================================================

TRUNCATE TABLE brz_lnd_IBP_Product_Master;

INSERT INTO brz_lnd_IBP_Product_Master (
    field1, SCNID, PRDID, UOMID, ZBASEMATERIAL, ZBOM1TXT, ZBOM1,
    ZBOM1QTYPER, ZBOM2, ZBOM2QTYPER, ZBOM3, ZBOM3QTYPER, ZBOM4, ZBOM4QTYPER
)
SELECT
    -- Field1
    CASE [Product Type] WHEN 'GPU' THEN 'GPU' ELSE 'NBU' END as field1,

    -- Scenario ID
    'SCN' + RIGHT('000' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS VARCHAR), 3) as SCNID,

    -- Product ID (hierarchical above material)
    'PRD_' + MATERIAL as PRDID,

    -- Unit of Measure ID
    CASE [Product Type]
        WHEN 'GPU' THEN 'EA'
        ELSE 'PC'
    END as UOMID,

    -- Base Material (matches hana_material_master.MATERIAL)
    MATERIAL as ZBASEMATERIAL,

    -- BOM Component 1 Text
    CASE [Product Type]
        WHEN 'GPU' THEN 'GPU Die'
        ELSE 'Processing Unit'
    END as ZBOM1TXT,

    -- BOM Component 1
    'BOM1_' + MATERIAL as ZBOM1,

    -- BOM Component 1 Quantity
    '1.000' as ZBOM1QTYPER,

    -- BOM Component 2
    'BOM2_' + MATERIAL as ZBOM2,

    -- BOM Component 2 Quantity
    CASE [Product Type]
        WHEN 'GPU' THEN CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 8) + 1 AS VARCHAR) + '.000'
        ELSE '2.000'
    END as ZBOM2QTYPER,

    -- BOM Component 3
    'BOM3_' + MATERIAL as ZBOM3,

    -- BOM Component 3 Quantity
    '1.000' as ZBOM3QTYPER,

    -- BOM Component 4
    'BOM4_' + MATERIAL as ZBOM4,

    -- BOM Component 4 Quantity
    '1.000' as ZBOM4QTYPER

FROM hana_material_master;

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_IBP_Product_Master';

-- =====================================================
-- 6. BRZ_LND_SAR_EXCEL_GPU (SAR Excel - GPU)
-- =====================================================

TRUNCATE TABLE brz_lnd_SAR_Excel_GPU;

INSERT INTO brz_lnd_SAR_Excel_GPU (
    Fiscal_Year_Period, Overall_Result, Material
)
SELECT
    -- Fiscal Year Period
    '2024.' + RIGHT('00' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 12) + 1 AS VARCHAR), 2) as Fiscal_Year_Period,

    -- Overall Result
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 6)
        WHEN 0 THEN 'Excellent Performance'
        WHEN 1 THEN 'Good Performance'
        WHEN 2 THEN 'Average Performance'
        WHEN 3 THEN 'Below Average'
        WHEN 4 THEN 'Poor Performance'
        ELSE 'Under Investigation'
    END as Overall_Result,

    -- Material (matches hana_material_master)
    MATERIAL

FROM hana_material_master
WHERE [Product Type] = 'GPU';

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_SAR_Excel_GPU';

-- =====================================================
-- 7. BRZ_LND_GPU_SKU_IN_SKULIFNR (GPU SKU in SKU LIFNR)
-- =====================================================

TRUNCATE TABLE brz_lnd_GPU_SKU_IN_SKULIFNR;

INSERT INTO brz_lnd_GPU_SKU_IN_SKULIFNR (
    PLANNING_SKU, Prd_Type
)
SELECT
    -- Planning SKU (same as Material for GPU products)
    MATERIAL as PLANNING_SKU,

    -- Product Type
    [Product Type] as Prd_Type

FROM hana_material_master
WHERE [Product Type] = 'GPU';

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_GPU_SKU_IN_SKULIFNR';

-- =====================================================
-- 8. BRZ_LND_SAR_EXCEL_NBU (SAR Excel - NBU)
-- =====================================================

TRUNCATE TABLE brz_lnd_SAR_Excel_NBU;

INSERT INTO brz_lnd_SAR_Excel_NBU (
    Fiscal_Year_Period, Overall_Result, Material
)
SELECT
    -- Fiscal Year Period
    '2024.' + RIGHT('00' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 12) + 1 AS VARCHAR), 2) as Fiscal_Year_Period,

    -- Overall Result
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 6)
        WHEN 0 THEN 'Outstanding Results'
        WHEN 1 THEN 'Strong Performance'
        WHEN 2 THEN 'Satisfactory'
        WHEN 3 THEN 'Needs Improvement'
        WHEN 4 THEN 'Critical Issues'
        ELSE 'Action Required'
    END as Overall_Result,

    -- Material (matches hana_material_master)
    MATERIAL

FROM hana_material_master
WHERE [Product Type] = 'NBU';

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records into brz_lnd_SAR_Excel_NBU';

-- =====================================================
-- DATA VALIDATION QUERIES
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
PRINT 'SEED DATA GENERATION COMPLETED SUCCESSFULLY!';
PRINT '500 items created (250 GPU + 250 NBU)';
PRINT 'All tables populated with consistent relationships';
PRINT '=====================================================';

-- Re-enable constraints
SET NOCOUNT OFF;
GO
