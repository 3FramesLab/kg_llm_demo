-- =====================================================
-- Test Data Generation for 1000 Records (500 GPU + 500 NBU)
-- Strictly following newdqschemanov.json schema
-- MS SQL Server T-SQL Syntax
-- =====================================================

SET NOCOUNT ON;
GO

PRINT '=====================================================';
PRINT 'GENERATING 1000 TEST RECORDS (500 GPU + 500 NBU)';
PRINT 'Following newdqschemanov.json schema exactly';
PRINT '=====================================================';

-- =====================================================
-- 1. HANA_MATERIAL_MASTER (1000 records)
-- =====================================================

TRUNCATE TABLE hana_material_master;

-- Generate 1000 records using recursive CTE
WITH Numbers AS (
    SELECT 1 as RowNum
    UNION ALL
    SELECT RowNum + 1
    FROM Numbers
    WHERE RowNum < 1000
),
MaterialData AS (
    SELECT 
        RowNum,
        CASE 
            WHEN RowNum <= 500 THEN N'GPU'
            ELSE N'NBU'
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
    -- MATERIAL (NVARCHAR(18))
    CASE 
        WHEN ProductType = N'GPU' THEN N'GPU-' + RIGHT(N'000' + CAST(RowNum AS NVARCHAR), 3)
        ELSE N'NBU-' + RIGHT(N'000' + CAST(RowNum - 500 AS NVARCHAR), 3)
    END,
    
    -- MATERIAL_GROUP (NVARCHAR(9))
    CASE ProductType 
        WHEN N'GPU' THEN N'GPUGRP' + CAST((RowNum % 5) + 1 AS NVARCHAR)
        ELSE N'NBUGRP' + CAST((RowNum % 3) + 1 AS NVARCHAR)
    END,
    
    -- MATERIAL_TYPE (NVARCHAR(4))
    CASE ProductType WHEN N'GPU' THEN N'FERT' ELSE N'HALB' END,
    
    -- PLANT (NVARCHAR(4))
    CASE (RowNum % 4)
        WHEN 0 THEN N'P001'
        WHEN 1 THEN N'P002' 
        WHEN 2 THEN N'P003'
        ELSE N'P004'
    END,
    
    -- Product Type (NVARCHAR(5))
    ProductType,
    
    -- Business Unit (NVARCHAR(5))
    CASE ProductType 
        WHEN N'GPU' THEN N'GPUBU'
        ELSE N'NBUBU'
    END,
    
    -- Product Line (NVARCHAR(5))
    CASE ProductType
        WHEN N'GPU' THEN 
            CASE (RowNum % 4)
                WHEN 0 THEN N'RTXGP'
                WHEN 1 THEN N'GTXGP'
                WHEN 2 THEN N'QUADR'
                ELSE N'TESLA'
            END
        ELSE 
            CASE (RowNum % 3)
                WHEN 0 THEN N'DRIVE'
                WHEN 1 THEN N'JETSO'
                ELSE N'ORIN'
            END
    END,
    
    -- OPS_MKTG_NM (NVARCHAR(250))
    CASE ProductType
        WHEN N'GPU' THEN N'GeForce RTX ' + CAST(4000 + (RowNum % 100) AS NVARCHAR) + N' Graphics Card'
        ELSE N'Jetson ' + CASE (RowNum % 3) WHEN 0 THEN N'Nano' WHEN 1 THEN N'Xavier' ELSE N'Orin' END + N' Developer Kit'
    END,
    
    -- OPS_STATUS (NVARCHAR(50)) - Appropriate status values
    CASE (RowNum % 10) 
        WHEN 0 THEN N'DISCONTINUED'
        WHEN 1 THEN N'PHASE_OUT'
        WHEN 2 THEN N'EOL_ANNOUNCED'
        WHEN 3 THEN N'ACTIVE'
        WHEN 4 THEN N'ACTIVE'
        WHEN 5 THEN N'ACTIVE'
        WHEN 6 THEN N'ACTIVE'
        WHEN 7 THEN N'NEW_PRODUCT'
        WHEN 8 THEN N'PILOT'
        ELSE N'ACTIVE'
    END,
    
    -- OPS_PLCCODE (NVARCHAR(60)) - Product Lifecycle Code
    CASE ProductType
        WHEN N'GPU' THEN N'PLC_GPU_' + CAST(RowNum AS NVARCHAR) + N'_' + 
            CASE (RowNum % 4) 
                WHEN 0 THEN N'GROWTH'
                WHEN 1 THEN N'MATURITY' 
                WHEN 2 THEN N'DECLINE'
                ELSE N'INTRODUCTION'
            END
        ELSE N'PLC_NBU_' + CAST(RowNum AS NVARCHAR) + N'_' +
            CASE (RowNum % 3)
                WHEN 0 THEN N'GROWTH'
                WHEN 1 THEN N'MATURITY'
                ELSE N'INTRODUCTION'
            END
    END,
    
    -- PRODGRP_CP (NVARCHAR(60))
    CASE ProductType
        WHEN N'GPU' THEN N'Graphics Processing Units - Consumer & Professional'
        ELSE N'Network Business Units - Edge Computing Solutions'
    END,
    
    -- IBP_FINANCE_MKT_NAME (NVARCHAR(60))
    CASE ProductType
        WHEN N'GPU' THEN N'GPU_Finance_' + CAST(RowNum AS NVARCHAR)
        ELSE N'NBU_Finance_' + CAST(RowNum AS NVARCHAR)
    END,
    
    -- OPS_PLANNER (NVARCHAR(250)) - Appropriate planner names
    CASE (RowNum % 15)
        WHEN 0 THEN N'John Smith - Senior Product Planner'
        WHEN 1 THEN N'Sarah Johnson - Lead Planning Analyst'
        WHEN 2 THEN N'Michael Chen - Product Planning Manager'
        WHEN 3 THEN N'Emily Davis - Strategic Planner'
        WHEN 4 THEN N'David Wilson - Operations Planner'
        WHEN 5 THEN N'Lisa Anderson - Demand Planner'
        WHEN 6 THEN N'Robert Taylor - Supply Chain Planner'
        WHEN 7 THEN N'Jennifer Brown - Product Line Planner'
        WHEN 8 THEN N'Christopher Lee - Planning Specialist'
        WHEN 9 THEN N'Amanda White - Capacity Planner'
        WHEN 10 THEN N'James Martinez - Production Planner'
        WHEN 11 THEN N'Michelle Garcia - Inventory Planner'
        WHEN 12 THEN N'Kevin Rodriguez - Forecast Planner'
        WHEN 13 THEN N'Rachel Thompson - Business Planner'
        ELSE N'Daniel Kim - Planning Coordinator'
    END,
    
    -- OPS_PLANNER_LAT (NVARCHAR(250))
    CASE (RowNum % 15)
        WHEN 0 THEN N'Juan Pérez - Planificador Senior de Productos'
        WHEN 1 THEN N'María González - Analista Líder de Planificación'
        WHEN 2 THEN N'Carlos Rodríguez - Gerente de Planificación'
        WHEN 3 THEN N'Ana Martínez - Planificadora Estratégica'
        WHEN 4 THEN N'Luis Hernández - Planificador de Operaciones'
        WHEN 5 THEN N'Carmen López - Planificadora de Demanda'
        WHEN 6 THEN N'Roberto Sánchez - Planificador de Cadena'
        WHEN 7 THEN N'Patricia Ramírez - Planificadora de Línea'
        WHEN 8 THEN N'Fernando Torres - Especialista en Planificación'
        WHEN 9 THEN N'Gabriela Flores - Planificadora de Capacidad'
        WHEN 10 THEN N'Alejandro Morales - Planificador de Producción'
        WHEN 11 THEN N'Mónica Jiménez - Planificadora de Inventario'
        WHEN 12 THEN N'Ricardo Vargas - Planificador de Pronósticos'
        WHEN 13 THEN N'Claudia Mendoza - Planificadora de Negocios'
        ELSE N'Andrés Castro - Coordinador de Planificación'
    END,
    
    -- OPS_PLANNER_LAT_TEXT (NVARCHAR(20))
    N'PLANNER_LAT_' + CAST((RowNum % 15) + 1 AS NVARCHAR),
    
    -- MAKE_BUY (NVARCHAR(1))
    CASE (RowNum % 3) 
        WHEN 0 THEN N'M'  -- Make
        WHEN 1 THEN N'B'  -- Buy
        ELSE N'C'         -- Contract
    END,
    
    -- NBS_ITEM_GRP (NVARCHAR(250))
    CASE ProductType
        WHEN N'GPU' THEN N'GPU Item Group - High Performance Computing Graphics'
        ELSE N'NBU Item Group - Network and Edge Computing Devices'
    END,
    
    -- AN_PLC_CD (NVARCHAR(60))
    N'AN_' + CASE ProductType WHEN N'GPU' THEN N'GPU' ELSE N'NBU' END + N'_' + 
    RIGHT(N'000' + CAST(RowNum AS NVARCHAR), 3) + N'_' +
    CASE (RowNum % 5)
        WHEN 0 THEN N'INTRO'
        WHEN 1 THEN N'GROWTH'
        WHEN 2 THEN N'MATURE'
        WHEN 3 THEN N'DECLINE'
        ELSE N'SUSTAIN'
    END

FROM MaterialData
OPTION (MAXRECURSION 1000);

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS NVARCHAR) + ' records into hana_material_master';

-- =====================================================
-- 2. BRZ_LND_RBP_GPU (GPU records only - 500 records)
-- =====================================================

TRUNCATE TABLE brz_lnd_RBP_GPU;

INSERT INTO brz_lnd_RBP_GPU (
    Product_Line, Product_Line_Dec, Product_Family, Business_Unit, 
    Material, Fiscal_Year_Period, Overall_Result
)
SELECT 
    -- Product_Line (NVARCHAR(14))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4)
        WHEN 0 THEN N'RTXGP'
        WHEN 1 THEN N'GTXGP' 
        WHEN 2 THEN N'QUADR'
        ELSE N'TESLA'
    END,
    
    -- Product_Line_Dec (NVARCHAR(20))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4)
        WHEN 0 THEN N'RTX Graphics'
        WHEN 1 THEN N'GTX Graphics'
        WHEN 2 THEN N'Quadro Pro'
        ELSE N'Tesla Compute'
    END,
    
    -- Product_Family (NVARCHAR(14))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 8)
        WHEN 0 THEN N'RTX40_SERIES'
        WHEN 1 THEN N'RTX30_SERIES'
        WHEN 2 THEN N'GTX16_SERIES'
        WHEN 3 THEN N'QUADRO_RTX'
        WHEN 4 THEN N'TESLA_V100'
        WHEN 5 THEN N'TESLA_A100'
        WHEN 6 THEN N'RTX_ADA'
        ELSE N'HOPPER_H100'
    END,
    
    -- Business_Unit (NVARCHAR(13))
    N'GPU_BUSINESS',
    
    -- Material (NVARCHAR(18)) - matches hana_material_master
    MATERIAL,
    
    -- Fiscal_Year_Period (NVARCHAR(71))
    N'FY2024.Q' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4) + 1 AS NVARCHAR) + 
    N'.M' + RIGHT(N'00' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 12) + 1 AS NVARCHAR), 2),
    
    -- Overall_Result (VARCHAR(255))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 6)
        WHEN 0 THEN 'Exceeds Target - Strong Performance'
        WHEN 1 THEN 'Meets Target - On Track'
        WHEN 2 THEN 'Below Target - Needs Attention'
        WHEN 3 THEN 'Significantly Below - Action Required'
        WHEN 4 THEN 'Under Review - Pending Analysis'
        ELSE 'Above Target - Excellent Results'
    END

FROM hana_material_master 
WHERE [Product Type] = N'GPU';

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS NVARCHAR) + ' records into brz_lnd_RBP_GPU';

-- =====================================================
-- 3. BRZ_LND_SKU_LIFNR_EXCEL (1000 records - all materials)
-- =====================================================

TRUNCATE TABLE brz_lnd_SKU_LIFNR_Excel;

INSERT INTO brz_lnd_SKU_LIFNR_Excel (
    ETL_BatchID, Material, Supplier, Production_Version,
    Reference_BOM, Planning_BOM, Prod_stor_location, Receiving_stor_loc_for_material,
    Lead_time, Additional_location, Storage_Location, MRP_Area, Product_Type,
    Tlane_Priority, Transform_Flag, Created_By, Created_On, Created_Time,
    Changed_By, Changed_Date, Changed_Time, Purchasing_group, Automated, brz_LoadTime
)
SELECT
    -- ETL_BatchID (INTEGER)
    1001,

    -- Material (VARCHAR(255))
    MATERIAL,

    -- Supplier (VARCHAR(255))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 12)
        WHEN 0 THEN 'TSMC_Taiwan_Semiconductor'
        WHEN 1 THEN 'Samsung_Foundry_Korea'
        WHEN 2 THEN 'SK_Hynix_Memory_Solutions'
        WHEN 3 THEN 'Micron_Technology_USA'
        WHEN 4 THEN 'ASE_Group_Assembly'
        WHEN 5 THEN 'Amkor_Technology_Services'
        WHEN 6 THEN 'JCET_Group_China'
        WHEN 7 THEN 'ChipMOS_Technologies'
        WHEN 8 THEN 'Powertech_Technology'
        WHEN 9 THEN 'Advanced_Semiconductor_Eng'
        WHEN 10 THEN 'GlobalFoundries_Malta'
        ELSE 'Intel_Foundry_Services'
    END,

    -- Production_Version (VARCHAR(255))
    'PV_' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS VARCHAR) + '_' +
    CASE [Product Type] WHEN N'GPU' THEN 'GPU_PROD' ELSE 'NBU_PROD' END,

    -- Reference_BOM (VARCHAR(255))
    'REF_BOM_' + MATERIAL + '_V1.0',

    -- Planning_BOM (VARCHAR(255))
    'PLAN_BOM_' + MATERIAL + '_ACTIVE',

    -- Prod_stor_location (VARCHAR(255))
    'PROD_LOC_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 8) + 1 AS VARCHAR) + '_' +
    CASE [Product Type] WHEN N'GPU' THEN 'GPU_FAB' ELSE 'NBU_FAB' END,

    -- Receiving_stor_loc_for_material (VARCHAR(255))
    'REC_LOC_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) + 1 AS VARCHAR) + '_WAREHOUSE',

    -- Lead_time (VARCHAR(255))
    CASE [Product Type]
        WHEN N'GPU' THEN CAST(60 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 40) AS VARCHAR) + ' days'
        ELSE CAST(45 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 30) AS VARCHAR) + ' days'
    END,

    -- Additional_location (VARCHAR(255))
    'ADD_LOC_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 6) + 1 AS VARCHAR) + '_BACKUP',

    -- Storage_Location (VARCHAR(255))
    'STOR_LOC_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 10) + 1 AS VARCHAR) + '_MAIN',

    -- MRP_Area (VARCHAR(255))
    'MRP_' + CASE [Product Type] WHEN N'GPU' THEN 'GPU_AREA_' ELSE 'NBU_AREA_' END +
    CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4) + 1 AS VARCHAR),

    -- Product_Type (VARCHAR(255))
    [Product Type],

    -- Tlane_Priority (VARCHAR(255))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5)
        WHEN 0 THEN 'CRITICAL'
        WHEN 1 THEN 'HIGH'
        WHEN 2 THEN 'MEDIUM'
        WHEN 3 THEN 'LOW'
        ELSE 'STANDARD'
    END,

    -- Transform_Flag (VARCHAR(255))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3)
        WHEN 0 THEN 'Y'
        WHEN 1 THEN 'N'
        ELSE 'P'
    END,

    -- Created_By (VARCHAR(255))
    'SYSTEM_USER_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 8) + 1 AS VARCHAR),

    -- Created_On (VARCHAR(255))
    FORMAT(DATEADD(day, -(ROW_NUMBER() OVER (ORDER BY MATERIAL) % 90), GETDATE()), 'yyyy-MM-dd'),

    -- Created_Time (VARCHAR(255))
    FORMAT(DATEADD(minute, ROW_NUMBER() OVER (ORDER BY MATERIAL) % 1440, '00:00:00'), 'HH:mm:ss'),

    -- Changed_By (VARCHAR(255))
    'SYSTEM_USER_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 8) + 1 AS VARCHAR),

    -- Changed_Date (VARCHAR(255))
    FORMAT(DATEADD(day, -(ROW_NUMBER() OVER (ORDER BY MATERIAL) % 30), GETDATE()), 'yyyy-MM-dd'),

    -- Changed_Time (VARCHAR(255))
    FORMAT(DATEADD(minute, ROW_NUMBER() OVER (ORDER BY MATERIAL) % 1440, '08:00:00'), 'HH:mm:ss'),

    -- Purchasing_group (VARCHAR(255))
    'PG_' + CASE [Product Type] WHEN N'GPU' THEN 'GPU_' ELSE 'NBU_' END +
    CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 6) + 1 AS VARCHAR),

    -- Automated (VARCHAR(255))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4)
        WHEN 0 THEN 'FULLY_AUTOMATED'
        WHEN 1 THEN 'SEMI_AUTOMATED'
        WHEN 2 THEN 'MANUAL'
        ELSE 'HYBRID'
    END,

    -- brz_LoadTime (DATETIME)
    GETDATE()

FROM hana_material_master;

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS NVARCHAR) + ' records into brz_lnd_SKU_LIFNR_Excel';

-- =====================================================
-- 4. BRZ_LND_IBP_PRODUCT_MASTER (1000 records - all materials)
-- =====================================================

TRUNCATE TABLE brz_lnd_IBP_Product_Master;

INSERT INTO brz_lnd_IBP_Product_Master (
    field1, SCNID, PRDID, UOMID, ZBASEMATERIAL, ZBOM1TXT, ZBOM1,
    ZBOM1QTYPER, ZBOM2, ZBOM2QTYPER, ZBOM3, ZBOM3QTYPER, ZBOM4, ZBOM4QTYPER,
    ZBUILDPACKOUT, ZBUSUNIT, ZPRDFAMILY, ZMATGRP, ZCODERELEVANT, ZCONSTRAINTHORIZON,
    ZCOOLINGTYPE, ZCRITICALPRODUCT, ZXPLANTSTATUS, ZDEMANDGROUP, ZDEVICECAT,
    ZDIEBIN, ZDIERBPINDICATOR, ZDIEREVLVL, ZDIRECTPOST, ZDRIVERSKU,
    ZDTKDESC, ZFAB, ZFABTECH, ZGPU1, ZGPU1QTYPER, ZGPU2, ZGPU2QTYPER,
    ZMAKEBUY, ZMATTYPE, ZITEMGRP, ZMARKTNAME, ZITMPRIORITYTIER, ZITEMTECH,
    ZJFFMKTNAME, ZRBPITGP, ZKITPRODUCT, ZLIFECYCLESTATE, PRODGROUP, PRODTYPE,
    ZPRIMARYMEMORY1, ZMEMORY1QTYPER, ZMEMORY2, ZMEMORY2QTYPER, ZMOQ2, ZMOQ1,
    ZRBPNOTES3, ZOLDMAT, ZACTIVEINACTIVE, ZOPSPCB, ZPLANNER, ZPLCCODE,
    PRODDESC, ZPRODUCTFLAG1, ZPRDGROUP, PRODUCTHIERARCHY, ZPRDUCTLINE, ZPRDLNEDESC,
    PRODUCTDEL, ZRBPNOTES1, ZPROFITCENTER, ZPROGCODE, ZRBPPLANNER, ZMARKETCODE,
    ZRBPNOTES2, SHELFLIFEACTIVE, ZSNPPLNR, ZSORTPRIORITYINT, ZSUBFMLY,
    ZSYSTEMDIRECTBUILD, ZTKLEADTIME, ZTKMANUFACTURER, ZTKMANUFACTPARTNUM, ZTKUNITCOST,
    ZTOPLVLNAME, ZVIRTUALKIT, LASTMODIFIEDBY, LASTMODIFIEDDATE, CREATEDBY, CREATEDDATE
)
SELECT
    -- field1 (NVARCHAR(5))
    CASE [Product Type] WHEN N'GPU' THEN N'GPU' ELSE N'NBU' END,

    -- SCNID (NVARCHAR(12))
    N'SCN' + RIGHT(N'000000' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR), 6),

    -- PRDID (NVARCHAR(31))
    N'PRD_' + MATERIAL,

    -- UOMID (NVARCHAR(9))
    CASE [Product Type] WHEN N'GPU' THEN N'EA' ELSE N'PC' END,

    -- ZBASEMATERIAL (NVARCHAR(34))
    MATERIAL,

    -- ZBOM1TXT (NVARCHAR(40))
    CASE [Product Type] WHEN N'GPU' THEN N'GPU Die Silicon Wafer' ELSE N'Processing Unit Core' END,

    -- ZBOM1 (NVARCHAR(18)) - Max 18 chars
    N'BOM1_' + RIGHT(MATERIAL, 11),  -- 'BOM1_' (5) + 11 chars = 16 total

    -- ZBOM1QTYPER (NVARCHAR(12))
    N'1.000',

    -- ZBOM2 (NVARCHAR(18)) - Max 18 chars
    N'BOM2_' + RIGHT(MATERIAL, 11),  -- 'BOM2_' (5) + 11 chars = 16 total

    -- ZBOM2QTYPER (NVARCHAR(12))
    N'2.000',

    -- ZBOM3 (NVARCHAR(9)) - Max 9 chars
    N'BOM3_' + RIGHT(MATERIAL, 2),   -- 'BOM3_' (5) + 2 chars = 7 total

    -- ZBOM3QTYPER (NVARCHAR(12))
    N'1.000',

    -- ZBOM4 (NVARCHAR(18)) - Max 18 chars
    N'BOM4_' + RIGHT(MATERIAL, 11),  -- 'BOM4_' (5) + 11 chars = 16 total

    -- ZBOM4QTYPER (NVARCHAR(12))
    N'1.000',

    -- ZBUILDPACKOUT (NVARCHAR(14))
    CASE [Product Type] WHEN N'GPU' THEN N'GPU_BUILD_OUT' ELSE N'NBU_BUILD_OUT' END,

    -- ZBUSUNIT (NVARCHAR(9))
    CASE [Product Type] WHEN N'GPU' THEN N'GPUBU' ELSE N'NBUBU' END,

    -- ZPRDFAMILY (NVARCHAR(19))
    CASE [Product Type] WHEN N'GPU' THEN N'GPU_FAMILY_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4) + 1 AS NVARCHAR) ELSE N'NBU_FAMILY_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) + 1 AS NVARCHAR) END,

    -- ZMATGRP (NVARCHAR(18))
    CASE [Product Type] WHEN N'GPU' THEN N'GPU_MAT_GRP' ELSE N'NBU_MAT_GRP' END,

    -- ZCODERELEVANT (NVARCHAR(13))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 2) WHEN 0 THEN N'YES' ELSE N'NO' END,

    -- ZCONSTRAINTHORIZON (NVARCHAR(18))
    N'HORIZON_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 12) + 1 AS NVARCHAR),

    -- ZCOOLINGTYPE (NVARCHAR(12))
    CASE [Product Type] WHEN N'GPU' THEN CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) WHEN 0 THEN N'AIR_COOLING' WHEN 1 THEN N'LIQUID_COOL' ELSE N'HYBRID_COOL' END ELSE N'PASSIVE_COOL' END,

    -- ZCRITICALPRODUCT (NVARCHAR(16))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) WHEN 0 THEN N'CRITICAL' WHEN 1 THEN N'HIGH_PRIORITY' ELSE N'STANDARD' END,

    -- ZXPLANTSTATUS (NVARCHAR(27))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4) WHEN 0 THEN N'ACTIVE_PRODUCTION' WHEN 1 THEN N'RAMP_UP' WHEN 2 THEN N'PHASE_OUT' ELSE N'MAINTENANCE' END,

    -- ZDEMANDGROUP (NVARCHAR(25))
    CASE [Product Type] WHEN N'GPU' THEN N'GPU_DEMAND_GROUP_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) + 1 AS NVARCHAR) ELSE N'NBU_DEMAND_GROUP_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 2) + 1 AS NVARCHAR) END,

    -- ZDEVICECAT (NVARCHAR(15))
    CASE [Product Type] WHEN N'GPU' THEN N'GRAPHICS_CARD' ELSE N'EDGE_DEVICE' END,

    -- ZDIEBIN (NVARCHAR(7))
    N'BIN_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 10) + 1 AS NVARCHAR),

    -- ZDIERBPINDICATOR (NVARCHAR(17))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 2) WHEN 0 THEN N'RBP_ACTIVE' ELSE N'RBP_INACTIVE' END,

    -- ZDIEREVLVL (NVARCHAR(18))
    N'REV_' + CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) WHEN 0 THEN N'A0' WHEN 1 THEN N'A1' WHEN 2 THEN N'B0' WHEN 3 THEN N'B1' ELSE N'C0' END,

    -- ZDIRECTPOST (NVARCHAR(19))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 2) WHEN 0 THEN N'DIRECT_POST_YES' ELSE N'DIRECT_POST_NO' END,

    -- ZDRIVERSKU (NVARCHAR(10))
    N'DRV_' + RIGHT(N'000' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR), 3),

    -- ZDTKDESC (NVARCHAR(40))
    CASE [Product Type] WHEN N'GPU' THEN N'GPU Desktop Graphics Card Description' ELSE N'NBU Edge Computing Device Description' END,

    -- ZFAB (NVARCHAR(4))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4) WHEN 0 THEN N'FAB1' WHEN 1 THEN N'FAB2' WHEN 2 THEN N'FAB3' ELSE N'FAB4' END,

    -- ZFABTECH (NVARCHAR(8))
    CASE [Product Type] WHEN N'GPU' THEN CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) WHEN 0 THEN N'5NM' WHEN 1 THEN N'7NM' ELSE N'4NM' END ELSE CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 2) WHEN 0 THEN N'7NM' ELSE N'5NM' END END,

    -- ZGPU1 (NVARCHAR(18)) - Max 18 chars
    CASE [Product Type] WHEN N'GPU' THEN N'GPU1_' + RIGHT(MATERIAL, 11) ELSE NULL END,  -- 'GPU1_' (5) + 11 = 16

    -- ZGPU1QTYPER (NVARCHAR(13))
    CASE [Product Type] WHEN N'GPU' THEN N'1.000' ELSE NULL END,

    -- ZGPU2 (NVARCHAR(18)) - Max 18 chars
    CASE [Product Type] WHEN N'GPU' THEN N'GPU2_' + RIGHT(MATERIAL, 11) ELSE NULL END,  -- 'GPU2_' (5) + 11 = 16

    -- ZGPU2QTYPER (NVARCHAR(13))
    CASE [Product Type] WHEN N'GPU' THEN N'0.000' ELSE NULL END,

    -- ZMAKEBUY (NVARCHAR(1))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) WHEN 0 THEN N'M' WHEN 1 THEN N'B' ELSE N'C' END,

    -- ZMATTYPE (NVARCHAR(4))
    CASE [Product Type] WHEN N'GPU' THEN N'FERT' ELSE N'HALB' END,

    -- ZITEMGRP (NVARCHAR(250))
    CASE [Product Type] WHEN N'GPU' THEN N'GPU Item Group - High Performance Computing Graphics Solutions' ELSE N'NBU Item Group - Network and Edge Computing Device Solutions' END,

    -- ZMARKTNAME (NVARCHAR(60))
    CASE [Product Type] WHEN N'GPU' THEN N'GPU Marketing Name ' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR) ELSE N'NBU Marketing Name ' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR) END,

    -- ZITMPRIORITYTIER (NVARCHAR(16))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4) WHEN 0 THEN N'TIER_1_CRITICAL' WHEN 1 THEN N'TIER_2_HIGH' WHEN 2 THEN N'TIER_3_MEDIUM' ELSE N'TIER_4_LOW' END,

    -- ZITEMTECH (NVARCHAR(11))
    CASE [Product Type] WHEN N'GPU' THEN N'GPU_TECH' ELSE N'NBU_TECH' END,

    -- ZJFFMKTNAME (NVARCHAR(60))
    CASE [Product Type] WHEN N'GPU' THEN N'JFF GPU Market Name ' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR) ELSE N'JFF NBU Market Name ' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR) END,

    -- ZRBPITGP (NVARCHAR(60))
    CASE [Product Type] WHEN N'GPU' THEN N'RBP GPU Item Group ' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR) ELSE N'RBP NBU Item Group ' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR) END,

    -- ZKITPRODUCT (NVARCHAR(12))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) WHEN 0 THEN N'KIT_PRODUCT' WHEN 1 THEN N'SINGLE_ITEM' ELSE N'BUNDLE' END,

    -- ZLIFECYCLESTATE (NVARCHAR(16))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) WHEN 0 THEN N'INTRODUCTION' WHEN 1 THEN N'GROWTH' WHEN 2 THEN N'MATURITY' WHEN 3 THEN N'DECLINE' ELSE N'SUSTAIN' END,

    -- PRODGROUP (NVARCHAR(60))
    CASE [Product Type] WHEN N'GPU' THEN N'Graphics Processing Units - Consumer & Professional' ELSE N'Network Business Units - Edge Computing Solutions' END,

    -- PRODTYPE (NVARCHAR(5))
    [Product Type],

    -- ZPRIMARYMEMORY1 (NVARCHAR(15)) - Max 15 chars
    CASE [Product Type] WHEN N'GPU' THEN N'MEM1_' + RIGHT(MATERIAL, 8) ELSE NULL END,  -- 'MEM1_' (5) + 8 = 13

    -- ZMEMORY1QTYPER (NVARCHAR(12))
    CASE [Product Type] WHEN N'GPU' THEN CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 8) + 1 AS NVARCHAR) + N'.000' ELSE NULL END,

    -- ZMEMORY2 (NVARCHAR(12)) - Max 12 chars
    CASE [Product Type] WHEN N'GPU' THEN N'MEM2_' + RIGHT(MATERIAL, 5) ELSE NULL END,  -- 'MEM2_' (5) + 5 = 10

    -- ZMEMORY2QTYPER (NVARCHAR(16))
    CASE [Product Type] WHEN N'GPU' THEN N'0.000' ELSE NULL END,

    -- ZMOQ2 (NVARCHAR(12))
    CAST(100 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 900) AS NVARCHAR),

    -- ZMOQ1 (NVARCHAR(12))
    CAST(50 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 450) AS NVARCHAR),

    -- ZRBPNOTES3 (NVARCHAR(250))
    N'RBP Notes 3: Additional planning notes for ' + MATERIAL,

    -- ZOLDMAT (NVARCHAR(18))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 10) WHEN 0 THEN N'OLD_' + MATERIAL ELSE NULL END,

    -- ZACTIVEINACTIVE (NVARCHAR(16))
    CASE OPS_STATUS WHEN N'ACTIVE' THEN N'ACTIVE' WHEN N'NEW_PRODUCT' THEN N'ACTIVE' ELSE N'INACTIVE' END,

    -- ZOPSPCB (NVARCHAR(7)) - Max 7 chars
    N'PCB' + RIGHT(MATERIAL, 3),  -- 'PCB' (3) + 3 chars = 6 total

    -- ZPLANNER (NVARCHAR(250))
    OPS_PLANNER,

    -- ZPLCCODE (NVARCHAR(60))
    OPS_PLCCODE,

    -- PRODDESC (NVARCHAR(250))
    CASE [Product Type] WHEN N'GPU' THEN N'High Performance Graphics Processing Unit for Gaming, Professional, and AI Applications' ELSE N'Advanced Network Processing Unit for Edge Computing, IoT, and Autonomous Systems' END,

    -- ZPRODUCTFLAG1 (NVARCHAR(13))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) WHEN 0 THEN N'FLAG_PREMIUM' WHEN 1 THEN N'FLAG_STANDARD' ELSE N'FLAG_VALUE' END,

    -- ZPRDGROUP (NVARCHAR(60))
    PRODGRP_CP,

    -- PRODUCTHIERARCHY (NVARCHAR(31))
    N'HIER_' + CASE [Product Type] WHEN N'GPU' THEN N'GPU' ELSE N'NBU' END + N'_' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR),

    -- ZPRDUCTLINE (NVARCHAR(5))
    [Product Line],

    -- ZPRDLNEDESC (NVARCHAR(20))
    CASE [Product Line] WHEN N'RTXGP' THEN N'RTX Graphics' WHEN N'GTXGP' THEN N'GTX Graphics' WHEN N'QUADR' THEN N'Quadro Professional' WHEN N'TESLA' THEN N'Tesla Compute' WHEN N'DRIVE' THEN N'DRIVE Automotive' WHEN N'JETSO' THEN N'Jetson Edge AI' ELSE N'Orin Computing' END,

    -- PRODUCTDEL (NVARCHAR(1))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 20) WHEN 0 THEN N'X' ELSE NULL END,

    -- ZRBPNOTES1 (NVARCHAR(250))
    N'RBP Notes 1: Revenue business planning notes for ' + MATERIAL,

    -- ZPROFITCENTER (NVARCHAR(10))
    CASE [Product Type] WHEN N'GPU' THEN N'PC_GPU_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) + 1 AS NVARCHAR) ELSE N'PC_NBU_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) + 1 AS NVARCHAR) END,

    -- ZPROGCODE (NVARCHAR(60))
    N'PROG_' + CASE [Product Type] WHEN N'GPU' THEN N'GPU' ELSE N'NBU' END + N'_' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR),

    -- ZRBPPLANNER (NVARCHAR(250))
    N'RBP Planner: ' + LEFT(OPS_PLANNER, 230),

    -- ZMARKETCODE (NVARCHAR(43))
    CASE [Product Type]
        WHEN N'GPU' THEN
            CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 6)
                WHEN 0 THEN N'MKT_GPU_GAMING_CONSUMER_NA_HIGH_END'
                WHEN 1 THEN N'MKT_GPU_PROFESSIONAL_WORKSTATION_EMEA'
                WHEN 2 THEN N'MKT_GPU_DATACENTER_AI_APAC_ENTERPRISE'
                WHEN 3 THEN N'MKT_GPU_AUTOMOTIVE_EMBEDDED_GLOBAL'
                WHEN 4 THEN N'MKT_GPU_CRYPTO_MINING_LATAM_VOLUME'
                ELSE N'MKT_GPU_EDGE_COMPUTING_MEA_SPECIALTY'
            END
        ELSE
            CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4)
                WHEN 0 THEN N'MKT_NBU_EDGE_AI_ROBOTICS_GLOBAL_PREMIUM'
                WHEN 1 THEN N'MKT_NBU_AUTOMOTIVE_AUTONOMOUS_NA_TIER1'
                WHEN 2 THEN N'MKT_NBU_INDUSTRIAL_IOT_EMEA_STANDARD'
                ELSE N'MKT_NBU_HEALTHCARE_MEDICAL_APAC_CRITICAL'
            END
    END,

    -- ZRBPNOTES2 (NVARCHAR(250))
    N'RBP Notes 2: Secondary planning notes for ' + MATERIAL,

    -- SHELFLIFEACTIVE (NVARCHAR(15))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 2) WHEN 0 THEN N'ACTIVE' ELSE N'INACTIVE' END,

    -- ZSNPPLNR (NVARCHAR(250))
    N'SNP Planner: ' + LEFT(OPS_PLANNER, 230),

    -- ZSORTPRIORITYINT (NVARCHAR(16))
    CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 1000) + 1 AS NVARCHAR),

    -- ZSUBFMLY (NVARCHAR(19))
    CASE [Product Type] WHEN N'GPU' THEN N'GPU_SUBFAMILY_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) + 1 AS NVARCHAR) ELSE N'NBU_SUBFAMILY_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) + 1 AS NVARCHAR) END,

    -- ZSYSTEMDIRECTBUILD (NVARCHAR(18))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 2) WHEN 0 THEN N'DIRECT_BUILD_YES' ELSE N'DIRECT_BUILD_NO' END,

    -- ZTKLEADTIME (NVARCHAR(12))
    CAST(30 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 60) AS NVARCHAR),

    -- ZTKMANUFACTURER (NVARCHAR(250))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) WHEN 0 THEN N'TSMC Taiwan Semiconductor Manufacturing Company' WHEN 1 THEN N'Samsung Foundry Korea Advanced Manufacturing' WHEN 2 THEN N'GlobalFoundries Malta Semiconductor Fabrication' WHEN 3 THEN N'Intel Foundry Services Advanced Process Technology' ELSE N'SK Hynix Memory Solutions Manufacturing' END,

    -- ZTKMANUFACTPARTNUM (NVARCHAR(250))
    N'MPN_' + MATERIAL + N'_' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR),

    -- ZTKUNITCOST (NVARCHAR(12))
    CASE [Product Type] WHEN N'GPU' THEN CAST(200 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 800) AS NVARCHAR) + N'.00' ELSE CAST(100 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 400) AS NVARCHAR) + N'.00' END,

    -- ZTOPLVLNAME (NVARCHAR(41))
    CASE [Product Type]
        WHEN N'GPU' THEN
            CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5)
                WHEN 0 THEN N'NVIDIA GeForce RTX Gaming Graphics'
                WHEN 1 THEN N'NVIDIA Quadro Professional Workstation'
                WHEN 2 THEN N'NVIDIA Tesla Data Center Accelerator'
                WHEN 3 THEN N'NVIDIA DRIVE Automotive Computing'
                ELSE N'NVIDIA Omniverse Enterprise Platform'
            END
        ELSE
            CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4)
                WHEN 0 THEN N'NVIDIA Jetson Edge AI Computing Platform'
                WHEN 1 THEN N'NVIDIA DRIVE AGX Autonomous Vehicle'
                WHEN 2 THEN N'NVIDIA Clara Healthcare AI Platform'
                ELSE N'NVIDIA Metropolis Smart City Solutions'
            END
    END,

    -- ZVIRTUALKIT (NVARCHAR(12))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) WHEN 0 THEN N'VIRTUAL_KIT' WHEN 1 THEN N'PHYSICAL_KIT' ELSE N'HYBRID_KIT' END,

    -- LASTMODIFIEDBY (NVARCHAR(250))
    N'SYSTEM_USER_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 10) + 1 AS NVARCHAR),

    -- LASTMODIFIEDDATE (NVARCHAR(255))
    FORMAT(DATEADD(day, -(ROW_NUMBER() OVER (ORDER BY MATERIAL) % 30), GETDATE()), 'yyyy-MM-dd'),

    -- CREATEDBY (NVARCHAR(250))
    N'SYSTEM_USER_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 10) + 1 AS NVARCHAR),

    -- CREATEDDATE (NVARCHAR(255))
    FORMAT(DATEADD(day, -(ROW_NUMBER() OVER (ORDER BY MATERIAL) % 90), GETDATE()), 'yyyy-MM-dd')

FROM hana_material_master;

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS NVARCHAR) + ' records into brz_lnd_IBP_Product_Master';

-- =====================================================
-- 5. BRZ_LND_OPS_EXCEL_GPU (GPU records only - 500 records)
-- =====================================================

TRUNCATE TABLE brz_lnd_OPS_EXCEL_GPU;

INSERT INTO brz_lnd_OPS_EXCEL_GPU (
    PLANNING_SKU, Product_Line, Business_Unit, Marketing_Code, Planner,
    Customer, Active_Inactive, Level_2_mapping_6, Level_2_usage, CHIP_Family,
    ETL_BatchID, brz_LoadTime
)
SELECT
    -- PLANNING_SKU (NVARCHAR(19)) - matches Material from hana_material_master
    MATERIAL,

    -- Product_Line (NVARCHAR(12))
    [Product Line],

    -- Business_Unit (NVARCHAR(13))
    [Business Unit],

    -- Marketing_Code (NVARCHAR(65))
    N'MKT_' + MATERIAL + N'_' +
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4)
        WHEN 0 THEN N'PREMIUM'
        WHEN 1 THEN N'MAINSTREAM'
        WHEN 2 THEN N'VALUE'
        ELSE N'ENTERPRISE'
    END,

    -- Planner (NVARCHAR(12))
    LEFT(OPS_PLANNER, 12),

    -- Customer (NVARCHAR(8))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 10)
        WHEN 0 THEN N'ASUS'
        WHEN 1 THEN N'MSI'
        WHEN 2 THEN N'EVGA'
        WHEN 3 THEN N'GIGABYTE'
        WHEN 4 THEN N'ZOTAC'
        WHEN 5 THEN N'PNY'
        WHEN 6 THEN N'PALIT'
        WHEN 7 THEN N'INNO3D'
        WHEN 8 THEN N'GALAX'
        ELSE N'GAINWARD'
    END,

    -- Active_Inactive (NVARCHAR(16))
    CASE OPS_STATUS
        WHEN N'ACTIVE' THEN N'Active'
        WHEN N'NEW_PRODUCT' THEN N'Active'
        WHEN N'PILOT' THEN N'Active'
        WHEN N'PHASE_OUT' THEN N'Inactive'
        WHEN N'DISCONTINUED' THEN N'Inactive'
        WHEN N'EOL_ANNOUNCED' THEN N'Inactive'
        ELSE N'Active'
    END,

    -- Level_2_mapping_6 (NVARCHAR(33))
    N'L2_MAP_' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR) + N'_GPU',

    -- Level_2_usage (NVARCHAR(14))
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 6)
        WHEN 0 THEN N'Gaming'
        WHEN 1 THEN N'Professional'
        WHEN 2 THEN N'Data Center'
        WHEN 3 THEN N'AI/ML'
        WHEN 4 THEN N'Crypto Mining'
        ELSE N'Workstation'
    END,

    -- CHIP_Family (NVARCHAR(14))
    CASE [Product Line]
        WHEN N'RTXGP' THEN N'Ada Lovelace'
        WHEN N'GTXGP' THEN N'Turing'
        WHEN N'QUADR' THEN N'Ampere'
        ELSE N'Hopper'
    END,

    -- ETL_BatchID (INTEGER)
    1001,

    -- brz_LoadTime (DATETIME)
    GETDATE()

FROM hana_material_master
WHERE [Product Type] = N'GPU';

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS NVARCHAR) + ' records into brz_lnd_OPS_EXCEL_GPU';

-- =====================================================
-- 6. Remaining Tables (SAR_Excel_GPU, SAR_Excel_NBU, GPU_SKU_IN_SKULIFNR)
-- =====================================================

-- BRZ_LND_SAR_EXCEL_GPU (GPU only - 500 records)
TRUNCATE TABLE brz_lnd_SAR_Excel_GPU;

INSERT INTO brz_lnd_SAR_Excel_GPU (
    Fiscal_Year_Period, Overall_Result, Material
)
SELECT
    N'FY2024.Q' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4) + 1 AS NVARCHAR) +
    N'.M' + RIGHT(N'00' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 12) + 1 AS NVARCHAR), 2),

    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 8)
        WHEN 0 THEN 'Excellent Performance - Above Target'
        WHEN 1 THEN 'Good Performance - Meets Expectations'
        WHEN 2 THEN 'Average Performance - On Track'
        WHEN 3 THEN 'Below Average - Needs Improvement'
        WHEN 4 THEN 'Poor Performance - Action Required'
        WHEN 5 THEN 'Under Investigation - Pending Review'
        WHEN 6 THEN 'Outstanding Results - Exceeds Target'
        ELSE 'Satisfactory - Within Range'
    END,

    MATERIAL

FROM hana_material_master
WHERE [Product Type] = N'GPU';

-- BRZ_LND_SAR_EXCEL_NBU (NBU only - 500 records)
TRUNCATE TABLE brz_lnd_SAR_Excel_NBU;

INSERT INTO brz_lnd_SAR_Excel_NBU (
    Fiscal_Year_Period, Overall_Result, Material
)
SELECT
    N'FY2024.Q' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4) + 1 AS NVARCHAR) +
    N'.M' + RIGHT(N'00' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 12) + 1 AS NVARCHAR), 2),

    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 8)
        WHEN 0 THEN 'Outstanding Results - Market Leader'
        WHEN 1 THEN 'Strong Performance - Growth Trajectory'
        WHEN 2 THEN 'Satisfactory - Stable Performance'
        WHEN 3 THEN 'Needs Improvement - Below Forecast'
        WHEN 4 THEN 'Critical Issues - Immediate Action'
        WHEN 5 THEN 'Action Required - Performance Gap'
        WHEN 6 THEN 'Exceptional - Breakthrough Results'
        ELSE 'Good - Meeting Objectives'
    END,

    MATERIAL

FROM hana_material_master
WHERE [Product Type] = N'NBU';

-- BRZ_LND_GPU_SKU_IN_SKULIFNR (GPU only - 500 records)
TRUNCATE TABLE brz_lnd_GPU_SKU_IN_SKULIFNR;

INSERT INTO brz_lnd_GPU_SKU_IN_SKULIFNR (
    PLANNING_SKU, Prd_Type
)
SELECT
    MATERIAL,
    [Product Type]

FROM hana_material_master
WHERE [Product Type] = N'GPU';

PRINT 'Inserted records into remaining tables';

-- =====================================================
-- FINAL VALIDATION AND SUMMARY
-- =====================================================

PRINT '';
PRINT '=====================================================';
PRINT 'DATA GENERATION COMPLETED SUCCESSFULLY!';
PRINT '1000 records created (500 GPU + 500 NBU)';
PRINT '=====================================================';

-- Validation queries
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

-- Product Type Distribution
SELECT
    [Product Type],
    COUNT(*) as Count
FROM hana_material_master
GROUP BY [Product Type];

-- Sample records with key fields
SELECT TOP 10
    MATERIAL,
    [Product Type],
    OPS_PLANNER,
    OPS_STATUS,
    OPS_PLCCODE
FROM hana_material_master
ORDER BY MATERIAL;

PRINT '';
PRINT 'Key Data Validation:';
PRINT '- OPS_PLANNER: Realistic planner names with roles';
PRINT '- OPS_STATUS: Appropriate status values (ACTIVE, DISCONTINUED, etc.)';
PRINT '- OPS_PLCCODE: Product lifecycle codes with stages';
PRINT '- ZMARKETCODE: Market segmentation codes';
PRINT '- ZTOPLVLNAME: Top-level product family names';
PRINT '- Product Types: GPU and NBU as requested';
PRINT '- Record Count: Exactly 1000 records total';

SET NOCOUNT OFF;
GO
