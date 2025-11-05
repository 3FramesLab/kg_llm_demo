-- =====================================================
-- FIXED: Test Data Generation for 1000 Records (500 GPU + 500 NBU)
-- ALL COLUMN LENGTHS VERIFIED AGAINST SCHEMA
-- MS SQL Server T-SQL Syntax
-- =====================================================

SET NOCOUNT ON;
GO

PRINT '=====================================================';
PRINT 'GENERATING 1000 TEST RECORDS (500 GPU + 500 NBU)';
PRINT 'ALL COLUMN LENGTHS VERIFIED AGAINST SCHEMA';
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
    
    -- OPS_STATUS (NVARCHAR(50))
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
    
    -- OPS_PLCCODE (NVARCHAR(60))
    CASE ProductType
        WHEN N'GPU' THEN N'PLC_GPU_' + CAST(RowNum AS NVARCHAR) + N'_' + 
            CASE (RowNum % 4) 
                WHEN 0 THEN N'GROWTH'
                WHEN 1 THEN N'MATURITY' 
                WHEN 2 THEN N'DECLINE'
                ELSE N'INTRO'
            END
        ELSE N'PLC_NBU_' + CAST(RowNum AS NVARCHAR) + N'_' +
            CASE (RowNum % 3)
                WHEN 0 THEN N'GROWTH'
                WHEN 1 THEN N'MATURITY'
                ELSE N'INTRO'
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
    
    -- OPS_PLANNER (NVARCHAR(250))
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
        WHEN 0 THEN N'M'
        WHEN 1 THEN N'B'
        ELSE N'C'
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
-- 2. BRZ_LND_IBP_PRODUCT_MASTER (1000 records) - ALL LENGTHS FIXED
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
    -- field1 (NVARCHAR(5)) - Max 5 chars
    CASE [Product Type] WHEN N'GPU' THEN N'GPU' ELSE N'NBU' END,

    -- SCNID (NVARCHAR(12)) - Max 12 chars
    N'SCN' + RIGHT(N'000000' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR), 6),

    -- PRDID (NVARCHAR(31)) - Max 31 chars
    N'PRD_' + MATERIAL,

    -- UOMID (NVARCHAR(9)) - Max 9 chars
    CASE [Product Type] WHEN N'GPU' THEN N'EA' ELSE N'PC' END,

    -- ZBASEMATERIAL (NVARCHAR(34)) - Max 34 chars
    MATERIAL,

    -- ZBOM1TXT (NVARCHAR(40)) - Max 40 chars
    CASE [Product Type] WHEN N'GPU' THEN N'GPU Die Silicon Wafer' ELSE N'Processing Unit Core' END,

    -- ZBOM1 (NVARCHAR(18)) - Max 18 chars
    N'B1_' + RIGHT(MATERIAL, 13),

    -- ZBOM1QTYPER (NVARCHAR(12)) - Max 12 chars
    N'1.000',

    -- ZBOM2 (NVARCHAR(18)) - Max 18 chars
    N'B2_' + RIGHT(MATERIAL, 13),

    -- ZBOM2QTYPER (NVARCHAR(12)) - Max 12 chars
    N'2.000',

    -- ZBOM3 (NVARCHAR(9)) - Max 9 chars
    N'B3_' + RIGHT(MATERIAL, 4),

    -- ZBOM3QTYPER (NVARCHAR(12)) - Max 12 chars
    N'1.000',

    -- ZBOM4 (NVARCHAR(18)) - Max 18 chars
    N'B4_' + RIGHT(MATERIAL, 13),

    -- ZBOM4QTYPER (NVARCHAR(12)) - Max 12 chars
    N'1.000',

    -- ZBUILDPACKOUT (NVARCHAR(16)) - Max 16 chars
    CASE [Product Type] WHEN N'GPU' THEN N'GPU_BUILD' ELSE N'NBU_BUILD' END,

    -- ZBUSUNIT (NVARCHAR(13)) - Max 13 chars
    CASE [Product Type] WHEN N'GPU' THEN N'GPUBU' ELSE N'NBUBU' END,

    -- ZPRDFAMILY (NVARCHAR(19)) - Max 19 chars
    CASE [Product Type] WHEN N'GPU' THEN N'GPU_FAM_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4) + 1 AS NVARCHAR) ELSE N'NBU_FAM_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) + 1 AS NVARCHAR) END,

    -- ZMATGRP (NVARCHAR(18)) - Max 18 chars
    CASE [Product Type] WHEN N'GPU' THEN N'GPU_MAT_GRP' ELSE N'NBU_MAT_GRP' END,

    -- ZCODERELEVANT (NVARCHAR(13)) - Max 13 chars
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 2) WHEN 0 THEN N'YES' ELSE N'NO' END,

    -- ZCONSTRAINTHORIZON (NVARCHAR(18)) - Max 18 chars
    N'HORIZON_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 12) + 1 AS NVARCHAR),

    -- ZCOOLINGTYPE (NVARCHAR(12)) - Max 12 chars
    CASE [Product Type] WHEN N'GPU' THEN CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) WHEN 0 THEN N'AIR' WHEN 1 THEN N'LIQUID' ELSE N'HYBRID' END ELSE N'PASSIVE' END,

    -- ZCRITICALPRODUCT (NVARCHAR(16)) - Max 16 chars
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) WHEN 0 THEN N'CRITICAL' WHEN 1 THEN N'HIGH_PRIORITY' ELSE N'STANDARD' END,

    -- ZXPLANTSTATUS (NVARCHAR(27)) - Max 27 chars
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4) WHEN 0 THEN N'ACTIVE_PRODUCTION' WHEN 1 THEN N'RAMP_UP' WHEN 2 THEN N'PHASE_OUT' ELSE N'MAINTENANCE' END,

    -- ZDEMANDGROUP (NVARCHAR(25)) - Max 25 chars
    CASE [Product Type] WHEN N'GPU' THEN N'GPU_DEMAND_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) + 1 AS NVARCHAR) ELSE N'NBU_DEMAND_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 2) + 1 AS NVARCHAR) END,

    -- ZDEVICECAT (NVARCHAR(15)) - Max 15 chars
    CASE [Product Type] WHEN N'GPU' THEN N'GRAPHICS_CARD' ELSE N'EDGE_DEVICE' END,

    -- ZDIEBIN (NVARCHAR(7)) - Max 7 chars
    N'BIN' + RIGHT(MATERIAL, 3),

    -- ZDIERBPINDICATOR (NVARCHAR(17)) - Max 17 chars
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 2) WHEN 0 THEN N'RBP_ACTIVE' ELSE N'RBP_INACTIVE' END,

    -- ZDIEREVLVL (NVARCHAR(18)) - Max 18 chars
    N'REV_' + CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) WHEN 0 THEN N'A0' WHEN 1 THEN N'A1' WHEN 2 THEN N'B0' WHEN 3 THEN N'B1' ELSE N'C0' END,

    -- ZDIRECTPOST (NVARCHAR(19)) - Max 19 chars
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 2) WHEN 0 THEN N'DIRECT_POST_YES' ELSE N'DIRECT_POST_NO' END,

    -- ZDRIVERSKU (NVARCHAR(10)) - Max 10 chars
    N'DRV' + RIGHT(MATERIAL, 6),

    -- ZDTKDESC (NVARCHAR(18)) - Max 18 chars *** THIS WAS THE ISSUE ***
    CASE [Product Type] WHEN N'GPU' THEN N'GPU Desktop Card' ELSE N'NBU Edge Device' END,

    -- ZFAB (NVARCHAR(4)) - Max 4 chars
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4) WHEN 0 THEN N'FAB1' WHEN 1 THEN N'FAB2' WHEN 2 THEN N'FAB3' ELSE N'FAB4' END,

    -- ZFABTECH (NVARCHAR(14)) - Max 14 chars
    CASE [Product Type] WHEN N'GPU' THEN CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) WHEN 0 THEN N'5NM' WHEN 1 THEN N'7NM' ELSE N'4NM' END ELSE CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 2) WHEN 0 THEN N'7NM' ELSE N'5NM' END END,

    -- ZGPU1 (NVARCHAR(18)) - Max 18 chars
    CASE [Product Type] WHEN N'GPU' THEN N'G1_' + RIGHT(MATERIAL, 14) ELSE NULL END,

    -- ZGPU1QTYPER (NVARCHAR(13)) - Max 13 chars
    CASE [Product Type] WHEN N'GPU' THEN N'1.000' ELSE NULL END,

    -- ZGPU2 (NVARCHAR(18)) - Max 18 chars
    CASE [Product Type] WHEN N'GPU' THEN N'G2_' + RIGHT(MATERIAL, 14) ELSE NULL END,

    -- ZGPU2QTYPER (NVARCHAR(13)) - Max 13 chars
    CASE [Product Type] WHEN N'GPU' THEN N'0.000' ELSE NULL END,

    -- ZMAKEBUY (NVARCHAR(20)) - Max 20 chars
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) WHEN 0 THEN N'M' WHEN 1 THEN N'B' ELSE N'C' END,

    -- ZMATTYPE (NVARCHAR(26)) - Max 26 chars
    CASE [Product Type] WHEN N'GPU' THEN N'FERT' ELSE N'HALB' END,

    -- ZITEMGRP (NVARCHAR(40)) - Max 40 chars
    CASE [Product Type] WHEN N'GPU' THEN N'GPU Item Group - Graphics Solutions' ELSE N'NBU Item Group - Edge Computing' END,

    -- ZMARKTNAME (NVARCHAR(40)) - Max 40 chars
    CASE [Product Type] WHEN N'GPU' THEN N'GPU Mkt ' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR) ELSE N'NBU Mkt ' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR) END,

    -- ZITMPRIORITYTIER (NVARCHAR(18)) - Max 18 chars
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4) WHEN 0 THEN N'TIER_1_CRITICAL' WHEN 1 THEN N'TIER_2_HIGH' WHEN 2 THEN N'TIER_3_MEDIUM' ELSE N'TIER_4_LOW' END,

    -- ZITEMTECH (NVARCHAR(22)) - Max 22 chars
    CASE [Product Type] WHEN N'GPU' THEN N'GPU_TECH' ELSE N'NBU_TECH' END,

    -- ZJFFMKTNAME (NVARCHAR(38)) - Max 38 chars
    CASE [Product Type] WHEN N'GPU' THEN N'JFF GPU Mkt ' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR) ELSE N'JFF NBU Mkt ' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR) END,

    -- ZRBPITGP (NVARCHAR(38)) - Max 38 chars
    CASE [Product Type] WHEN N'GPU' THEN N'RBP GPU Grp ' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR) ELSE N'RBP NBU Grp ' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR) END,

    -- ZKITPRODUCT (NVARCHAR(11)) - Max 11 chars
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) WHEN 0 THEN N'KIT_PRODUCT' WHEN 1 THEN N'SINGLE_ITEM' ELSE N'BUNDLE' END,

    -- ZLIFECYCLESTATE (NVARCHAR(15)) - Max 15 chars
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) WHEN 0 THEN N'INTRODUCTION' WHEN 1 THEN N'GROWTH' WHEN 2 THEN N'MATURITY' WHEN 3 THEN N'DECLINE' ELSE N'SUSTAIN' END,

    -- PRODGROUP (NVARCHAR(14)) - Max 14 chars
    CASE [Product Type] WHEN N'GPU' THEN N'Graphics' ELSE N'Network' END,

    -- PRODTYPE (NVARCHAR(13)) - Max 13 chars
    [Product Type],

    -- ZPRIMARYMEMORY1 (NVARCHAR(15)) - Max 15 chars
    CASE [Product Type] WHEN N'GPU' THEN N'MEM1_' + RIGHT(MATERIAL, 8) ELSE NULL END,

    -- ZMEMORY1QTYPER (NVARCHAR(16)) - Max 16 chars
    CASE [Product Type] WHEN N'GPU' THEN CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 8) + 1 AS NVARCHAR) + N'.000' ELSE NULL END,

    -- ZMEMORY2 (NVARCHAR(12)) - Max 12 chars
    CASE [Product Type] WHEN N'GPU' THEN N'MEM2_' + RIGHT(MATERIAL, 5) ELSE NULL END,

    -- ZMEMORY2QTYPER (NVARCHAR(16)) - Max 16 chars
    CASE [Product Type] WHEN N'GPU' THEN N'0.000' ELSE NULL END,

    -- ZMOQ2 (NVARCHAR(15)) - Max 15 chars
    CAST(100 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 900) AS NVARCHAR),

    -- ZMOQ1 (NVARCHAR(5)) - Max 5 chars
    CAST(50 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 49) AS NVARCHAR),

    -- ZRBPNOTES3 (NVARCHAR(34)) - Max 34 chars
    N'RBP Notes 3: ' + RIGHT(MATERIAL, 18),

    -- ZOLDMAT (NVARCHAR(12)) - Max 12 chars
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 10) WHEN 0 THEN N'OLD_' + RIGHT(MATERIAL, 7) ELSE NULL END,

    -- ZACTIVEINACTIVE (NVARCHAR(19)) - Max 19 chars
    CASE OPS_STATUS WHEN N'ACTIVE' THEN N'ACTIVE' WHEN N'NEW_PRODUCT' THEN N'ACTIVE' ELSE N'INACTIVE' END,

    -- ZOPSPCB (NVARCHAR(7)) - Max 7 chars
    N'PCB' + RIGHT(MATERIAL, 3),

    -- ZPLANNER (NVARCHAR(21)) - Max 21 chars
    LEFT(OPS_PLANNER, 21),

    -- ZPLCCODE (NVARCHAR(21)) - Max 21 chars
    LEFT(OPS_PLCCODE, 21),

    -- PRODDESC (NVARCHAR(40)) - Max 40 chars
    CASE [Product Type] WHEN N'GPU' THEN N'High Performance Graphics Unit' ELSE N'Advanced Network Processing Unit' END,

    -- ZPRODUCTFLAG1 (NVARCHAR(13)) - Max 13 chars
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) WHEN 0 THEN N'FLAG_PREMIUM' WHEN 1 THEN N'FLAG_STANDARD' ELSE N'FLAG_VALUE' END,

    -- ZPRDGROUP (NVARCHAR(13)) - Max 13 chars
    LEFT(PRODGRP_CP, 13),

    -- PRODUCTHIERARCHY (NVARCHAR(18)) - Max 18 chars
    N'HIER_' + CASE [Product Type] WHEN N'GPU' THEN N'GPU' ELSE N'NBU' END + N'_' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR),

    -- ZPRDUCTLINE (NVARCHAR(12)) - Max 12 chars
    [Product Line],

    -- ZPRDLNEDESC (NVARCHAR(24)) - Max 24 chars
    CASE [Product Line] WHEN N'RTXGP' THEN N'RTX Graphics' WHEN N'GTXGP' THEN N'GTX Graphics' WHEN N'QUADR' THEN N'Quadro Professional' WHEN N'TESLA' THEN N'Tesla Compute' WHEN N'DRIVE' THEN N'DRIVE Automotive' WHEN N'JETSO' THEN N'Jetson Edge AI' ELSE N'Orin Computing' END,

    -- PRODUCTDEL (NVARCHAR(27)) - Max 27 chars
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 20) WHEN 0 THEN N'X' ELSE NULL END,

    -- ZRBPNOTES1 (NVARCHAR(15)) - Max 15 chars
    N'RBP1: ' + RIGHT(MATERIAL, 7),

    -- ZPROFITCENTER (NVARCHAR(13)) - Max 13 chars
    CASE [Product Type] WHEN N'GPU' THEN N'PC_GPU_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) + 1 AS NVARCHAR) ELSE N'PC_NBU_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) + 1 AS NVARCHAR) END,

    -- ZPROGCODE (NVARCHAR(20)) - Max 20 chars
    N'PROG_' + CASE [Product Type] WHEN N'GPU' THEN N'GPU' ELSE N'NBU' END + N'_' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR),

    -- ZRBPPLANNER (NVARCHAR(19)) - Max 19 chars
    N'RBP: ' + LEFT(OPS_PLANNER, 13),

    -- ZMARKETCODE (NVARCHAR(43)) - Max 43 chars
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

    -- ZRBPNOTES2 (NVARCHAR(26)) - Max 26 chars
    N'RBP2: ' + RIGHT(MATERIAL, 18),

    -- SHELFLIFEACTIVE (NVARCHAR(26)) - Max 26 chars
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 2) WHEN 0 THEN N'ACTIVE' ELSE N'INACTIVE' END,

    -- ZSNPPLNR (NVARCHAR(11)) - Max 11 chars
    N'SNP: ' + LEFT(OPS_PLANNER, 5),

    -- ZSORTPRIORITYINT (NVARCHAR(21)) - Max 21 chars
    CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 1000) + 1 AS NVARCHAR),

    -- ZSUBFMLY (NVARCHAR(17)) - Max 17 chars
    CASE [Product Type] WHEN N'GPU' THEN N'GPU_SUB_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) + 1 AS NVARCHAR) ELSE N'NBU_SUB_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) + 1 AS NVARCHAR) END,

    -- ZSYSTEMDIRECTBUILD (NVARCHAR(20)) - Max 20 chars
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 2) WHEN 0 THEN N'DIRECT_BUILD_YES' ELSE N'DIRECT_BUILD_NO' END,

    -- ZTKLEADTIME (NVARCHAR(12)) - Max 12 chars
    CAST(30 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 60) AS NVARCHAR),

    -- ZTKMANUFACTURER (NVARCHAR(30)) - Max 30 chars
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5) WHEN 0 THEN N'TSMC Taiwan Semiconductor' WHEN 1 THEN N'Samsung Foundry Korea' WHEN 2 THEN N'GlobalFoundries Malta' WHEN 3 THEN N'Intel Foundry Services' ELSE N'SK Hynix Memory Solutions' END,

    -- ZTKMANUFACTPARTNUM (NVARCHAR(30)) - Max 30 chars
    N'MPN_' + MATERIAL + N'_' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS NVARCHAR),

    -- ZTKUNITCOST (NVARCHAR(12)) - Max 12 chars
    CASE [Product Type] WHEN N'GPU' THEN CAST(200 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 800) AS NVARCHAR) + N'.00' ELSE CAST(100 + (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 400) AS NVARCHAR) + N'.00' END,

    -- ZTOPLVLNAME (NVARCHAR(41)) - Max 41 chars
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

    -- ZVIRTUALKIT (NVARCHAR(40)) - Max 40 chars
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3) WHEN 0 THEN N'VIRTUAL_KIT' WHEN 1 THEN N'PHYSICAL_KIT' ELSE N'HYBRID_KIT' END,

    -- LASTMODIFIEDBY (NVARCHAR(14)) - Max 14 chars
    N'SYS_USER_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 10) + 1 AS NVARCHAR),

    -- LASTMODIFIEDDATE (NVARCHAR(16)) - Max 16 chars
    FORMAT(DATEADD(day, -(ROW_NUMBER() OVER (ORDER BY MATERIAL) % 30), GETDATE()), 'yyyy-MM-dd'),

    -- CREATEDBY (NVARCHAR(12)) - Max 12 chars
    N'SYS_USR_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 10) + 1 AS NVARCHAR),

    -- CREATEDDATE (NVARCHAR(14)) - Max 14 chars
    FORMAT(DATEADD(day, -(ROW_NUMBER() OVER (ORDER BY MATERIAL) % 90), GETDATE()), 'yyyy-MM-dd')

FROM hana_material_master;

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS NVARCHAR) + ' records into brz_lnd_IBP_Product_Master';
