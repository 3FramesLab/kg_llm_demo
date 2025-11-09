-- ====================================================================
-- MASTER SEED DATA SCRIPT FOR NewDQ DATABASE
-- ====================================================================
-- Version: 2.0
-- Date: 2025-11-08
-- Database: NewDQ (MS SQL Server)
-- Tables: All 10 tables in the schema
-- Records: 1000 base materials (500 GPU + 500 NBU)
-- ====================================================================
--
-- WHAT THIS SCRIPT DOES:
-- 1. Truncates all tables to ensure clean start
-- 2. Seeds hana_material_master with 1000 materials
-- 3. Seeds all related tables with matching data
-- 4. Includes realistic data with proper NULL handling
-- 5. GPU materials: MAT00001 - MAT00500
-- 6. NBU materials: MAT00501 - MAT01000
--
-- KEY FEATURES:
-- - Material/PRDID/Planning_SKU Format: MAT00001, MAT00002, etc.
-- - GPU: Has values for OPS_PLANNER, OPS_STATUS, OPS_PLCCODE, ZTOPLVLNAME, ZMARKETCODE
-- - NBU: NULL for OPS_PLANNER, OPS_STATUS, OPS_PLCCODE, ZTOPLVLNAME, ZMARKETCODE
-- - ~10% of brz_lnd_OPS_EXCEL_GPU records have NULL PLANNING_SKU (realistic scenario)
-- - All column lengths comply with schema constraints
-- - Realistic product names and planners
--
-- EXECUTION TIME: ~2-5 minutes for all 1000+ records
-- ====================================================================

USE NewDQ;
GO

SET NOCOUNT ON;
GO

PRINT '';
PRINT '====================================================================';
PRINT ' MASTER SEED DATA SCRIPT - NewDQ DATABASE';
PRINT '====================================================================';
PRINT ' Starting: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '====================================================================';
PRINT '';

-- ====================================================================
-- STEP 1: TRUNCATE ALL TABLES (Clean Start)
-- ====================================================================
PRINT '>>> STEP 1: Truncating all tables...';
PRINT '';

BEGIN TRY
    TRUNCATE TABLE brz_lnd_SAR_Excel_NBU;
    PRINT '  ✓ brz_lnd_SAR_Excel_NBU truncated';

    TRUNCATE TABLE brz_lnd_SAR_Excel_GPU;
    PRINT '  ✓ brz_lnd_SAR_Excel_GPU truncated';

    TRUNCATE TABLE brz_lnd_GPU_SKU_IN_SKULIFNR;
    PRINT '  ✓ brz_lnd_GPU_SKU_IN_SKULIFNR truncated';

    TRUNCATE TABLE brz_lnd_RBP_NBU;
    PRINT '  ✓ brz_lnd_RBP_NBU truncated';

    TRUNCATE TABLE brz_lnd_RBP_GPU;
    PRINT '  ✓ brz_lnd_RBP_GPU truncated';

    TRUNCATE TABLE brz_lnd_OPS_EXCEL_NBU;
    PRINT '  ✓ brz_lnd_OPS_EXCEL_NBU truncated';

    TRUNCATE TABLE brz_lnd_OPS_EXCEL_GPU;
    PRINT '  ✓ brz_lnd_OPS_EXCEL_GPU truncated';

    TRUNCATE TABLE brz_lnd_SKU_LIFNR_Excel;
    PRINT '  ✓ brz_lnd_SKU_LIFNR_Excel truncated';

    TRUNCATE TABLE brz_lnd_IBP_Product_Master;
    PRINT '  ✓ brz_lnd_IBP_Product_Master truncated';

    TRUNCATE TABLE hana_material_master;
    PRINT '  ✓ hana_material_master truncated';

    PRINT '';
    PRINT '  ✅ All tables truncated successfully';
END TRY
BEGIN CATCH
    PRINT '  ❌ Error truncating tables: ' + ERROR_MESSAGE();
    PRINT '  Note: If foreign key constraints exist, you may need to disable them first';
END CATCH
GO

-- ====================================================================
-- STEP 2: SEED hana_material_master (Master Material Data)
-- ====================================================================
PRINT '';
PRINT '>>> STEP 2: Populating hana_material_master (1000 materials)...';
PRINT '';

-- GPU Materials (1-500): Have OPS_PLANNER, OPS_STATUS, OPS_PLCCODE
DECLARE @i INT = 1;
WHILE @i <= 500
BEGIN
    INSERT INTO hana_material_master (
        MATERIAL, MATERIAL_GROUP, MATERIAL_TYPE, PLANT, [Product Type],
        [Business Unit], [Product Line], OPS_MKTG_NM, OPS_STATUS, OPS_PLCCODE,
        PRODGRP_CP, IBP_FINANCE_MKT_NAME, OPS_PLANNER, OPS_PLANNER_LAT,
        OPS_PLANNER_LAT_TEXT, MAKE_BUY, NBS_ITEM_GRP, AN_PLC_CD
    ) VALUES (
        'MAT' + RIGHT('00000' + CAST(@i AS VARCHAR), 5),
        'MG' + CAST((@i % 10) + 1 AS VARCHAR),
        'FERT',
        'P001',
        'GPU',
        'BU0' + CAST((@i % 3) + 1 AS VARCHAR),
        'PL0' + CAST((@i % 5) + 1 AS VARCHAR),
        CASE (@i % 5)
            WHEN 0 THEN 'NVIDIA GeForce RTX 4090 Graphics Card'
            WHEN 1 THEN 'AMD Radeon RX 7900 XTX GPU Module'
            WHEN 2 THEN 'NVIDIA Tesla A100 AI Accelerator'
            WHEN 3 THEN 'AMD Instinct MI300X Compute GPU'
            ELSE 'NVIDIA H100 Tensor Core GPU'
        END,
        CASE (@i % 3)
            WHEN 0 THEN 'Active'
            WHEN 1 THEN 'Phase-In'
            ELSE 'Active'
        END,
        'PLC-' + CASE (@i % 4)
            WHEN 0 THEN 'GROWTH'
            WHEN 1 THEN 'MATURITY'
            WHEN 2 THEN 'INTRO'
            ELSE 'GROWTH'
        END,
        'PRODGRP-GPU-' + CAST((@i % 10) + 1 AS VARCHAR),
        'Finance Marketing GPU Unit ' + CAST((@i % 5) + 1 AS VARCHAR),
        CASE (@i % 8)
            WHEN 0 THEN 'John Smith'
            WHEN 1 THEN 'Sarah Johnson'
            WHEN 2 THEN 'Michael Chen'
            WHEN 3 THEN 'Emily Rodriguez'
            WHEN 4 THEN 'David Kim'
            WHEN 5 THEN 'Lisa Wang'
            WHEN 6 THEN 'James Anderson'
            ELSE 'Maria Garcia'
        END,
        CASE (@i % 8)
            WHEN 0 THEN 'Smith, John'
            WHEN 1 THEN 'Johnson, Sarah'
            WHEN 2 THEN 'Chen, Michael'
            WHEN 3 THEN 'Rodriguez, Emily'
            WHEN 4 THEN 'Kim, David'
            WHEN 5 THEN 'Wang, Lisa'
            WHEN 6 THEN 'Anderson, James'
            ELSE 'Garcia, Maria'
        END,
        CASE (@i % 8)
            WHEN 0 THEN 'JSMITH'
            WHEN 1 THEN 'SJOHNSON'
            WHEN 2 THEN 'MCHEN'
            WHEN 3 THEN 'ERODRIGUEZ'
            WHEN 4 THEN 'DKIM'
            WHEN 5 THEN 'LWANG'
            WHEN 6 THEN 'JANDERSON'
            ELSE 'MGARCIA'
        END,
        CASE (@i % 2) WHEN 0 THEN 'M' ELSE 'B' END,
        'GPU_' + CASE (@i % 3)
            WHEN 0 THEN 'Data Center'
            WHEN 1 THEN 'Gaming'
            ELSE 'Professional'
        END,
        'AN-PLC-' + CAST((@i % 5) + 1 AS VARCHAR)
    );

    -- Progress indicator every 100 records
    IF @i % 100 = 0
        PRINT '  Progress: ' + CAST(@i AS VARCHAR) + ' GPU materials inserted...';

    SET @i = @i + 1;
END;

PRINT '  ✓ 500 GPU materials inserted (MAT00001 - MAT00500)';

-- NBU Materials (501-1000): NULL for OPS_PLANNER, OPS_STATUS, OPS_PLCCODE
SET @i = 501;
WHILE @i <= 1000
BEGIN
    INSERT INTO hana_material_master (
        MATERIAL, MATERIAL_GROUP, MATERIAL_TYPE, PLANT, [Product Type],
        [Business Unit], [Product Line], OPS_MKTG_NM, OPS_STATUS, OPS_PLCCODE,
        PRODGRP_CP, IBP_FINANCE_MKT_NAME, OPS_PLANNER, OPS_PLANNER_LAT,
        OPS_PLANNER_LAT_TEXT, MAKE_BUY, NBS_ITEM_GRP, AN_PLC_CD
    ) VALUES (
        'MAT' + RIGHT('00000' + CAST(@i AS VARCHAR), 5),
        'MG' + CAST((@i % 10) + 1 AS VARCHAR),
        'FERT',
        'P001',
        'NBU',
        'BU0' + CAST((@i % 3) + 1 AS VARCHAR),
        'PL0' + CAST((@i % 5) + 1 AS VARCHAR),
        CASE (@i % 5)
            WHEN 0 THEN 'Mellanox ConnectX-7 SmartNIC Network Adapter'
            WHEN 1 THEN 'InfiniBand HDR 200Gb Switch Module'
            WHEN 2 THEN 'Ethernet 400G Network Interface Card'
            WHEN 3 THEN 'BlueField-3 DPU Data Processing Unit'
            ELSE 'Spectrum-4 Ethernet Switch ASIC'
        END,
        NULL, -- OPS_STATUS is NULL for NBU
        NULL, -- OPS_PLCCODE is NULL for NBU
        'PRODGRP-NBU-' + CAST((@i % 10) + 1 AS VARCHAR),
        'Finance Marketing NBU Unit ' + CAST((@i % 5) + 1 AS VARCHAR),
        NULL, -- OPS_PLANNER is NULL for NBU
        NULL, -- OPS_PLANNER_LAT is NULL for NBU
        NULL, -- OPS_PLANNER_LAT_TEXT is NULL for NBU
        CASE (@i % 2) WHEN 0 THEN 'M' ELSE 'B' END,
        'NBU_' + CASE (@i % 3)
            WHEN 0 THEN 'Networking'
            WHEN 1 THEN 'InfiniBand'
            ELSE 'Ethernet'
        END,
        'AN-PLC-' + CAST((@i % 5) + 1 AS VARCHAR)
    );

    -- Progress indicator every 100 records
    IF @i % 100 = 0
        PRINT '  Progress: ' + CAST(@i AS VARCHAR) + ' total materials inserted...';

    SET @i = @i + 1;
END;

PRINT '  ✓ 500 NBU materials inserted (MAT00501 - MAT01000)';
PRINT '';
PRINT '  ✅ hana_material_master: 1000 records inserted';
GO

-- ====================================================================
-- STEP 3: SEED brz_lnd_IBP_Product_Master (IBP Product Master Data)
-- ====================================================================
PRINT '';
PRINT '>>> STEP 3: Populating brz_lnd_IBP_Product_Master (1000 records)...';
PRINT '';

DECLARE @i INT = 1;
WHILE @i <= 500
BEGIN
    -- GPU Records
    INSERT INTO brz_lnd_IBP_Product_Master (
        field1, SCNID, PRDID, UOMID, PRODTYPE, ZBUSUNIT, ZPRDFAMILY,
        ZMARKTNAME, ZMARKETCODE, ZTOPLVLNAME, ZPLANNER, ZPLCCODE,
        ZACTIVEINACTIVE, PRODDESC, ZPRDUCTLINE, ZPRDLNEDESC,
        ZMAKEBUY, ZMATTYPE, ZITEMGRP, CREATEDBY, CREATEDDATE,
        LASTMODIFIEDBY, LASTMODIFIEDDATE
    ) VALUES (
        NULL,
        'SCN-GPU-001',
        'MAT' + RIGHT('00000' + CAST(@i AS VARCHAR), 5),
        'EA',
        'GPU',
        'BU0' + CAST((@i % 3) + 1 AS VARCHAR),
        'FAM-GPU-' + CAST((@i % 5) + 1 AS VARCHAR),
        CASE (@i % 5)
            WHEN 0 THEN 'GeForce RTX 4090'
            WHEN 1 THEN 'Radeon RX 7900 XTX'
            WHEN 2 THEN 'Tesla A100'
            WHEN 3 THEN 'Instinct MI300X'
            ELSE 'H100 Tensor Core'
        END,
        'MKT-' + CASE (@i % 4)
            WHEN 0 THEN 'Gaming High-End Desktop GPU'
            WHEN 1 THEN 'Data Center AI Accelerator'
            WHEN 2 THEN 'Professional Workstation GPU'
            ELSE 'Cloud Computing GPU Instance'
        END,
        'TopLevel-' + CASE (@i % 3)
            WHEN 0 THEN 'Consumer Graphics'
            WHEN 1 THEN 'Enterprise Compute'
            ELSE 'Professional Visualization'
        END,
        CASE (@i % 8)
            WHEN 0 THEN 'John Smith'
            WHEN 1 THEN 'Sarah Johnson'
            WHEN 2 THEN 'Michael Chen'
            WHEN 3 THEN 'Emily Rodriguez'
            WHEN 4 THEN 'David Kim'
            WHEN 5 THEN 'Lisa Wang'
            WHEN 6 THEN 'James Anderson'
            ELSE 'Maria Garcia'
        END,
        'PLC-' + CASE (@i % 4)
            WHEN 0 THEN 'GROWTH'
            WHEN 1 THEN 'MATURITY'
            WHEN 2 THEN 'INTRO'
            ELSE 'GROWTH'
        END,
        'Active',
        CASE (@i % 5)
            WHEN 0 THEN 'GeForce RTX 4090 Graphics Card 24GB GDDR6X'
            WHEN 1 THEN 'AMD Radeon RX 7900 XTX GPU 24GB'
            WHEN 2 THEN 'NVIDIA Tesla A100 PCIe 40GB HBM2'
            WHEN 3 THEN 'AMD Instinct MI300X 192GB HBM3'
            ELSE 'NVIDIA H100 SXM5 80GB HBM3'
        END,
        'PL0' + CAST((@i % 5) + 1 AS VARCHAR),
        'Product Line ' + CAST((@i % 5) + 1 AS VARCHAR),
        CASE (@i % 2) WHEN 0 THEN 'Make' ELSE 'Buy' END,
        'FERT',
        'GPU_ITEM_GRP_' + CAST((@i % 5) + 1 AS VARCHAR),
        'SYSTEM',
        '2024-01-15',
        'SYSTEM',
        '2025-11-08'
    );

    IF @i % 100 = 0
        PRINT '  Progress: ' + CAST(@i AS VARCHAR) + ' IBP records inserted...';

    SET @i = @i + 1;
END;

-- NBU Records (501-1000)
SET @i = 501;
WHILE @i <= 1000
BEGIN
    INSERT INTO brz_lnd_IBP_Product_Master (
        field1, SCNID, PRDID, UOMID, PRODTYPE, ZBUSUNIT, ZPRDFAMILY,
        ZMARKTNAME, ZMARKETCODE, ZTOPLVLNAME, ZPLANNER, ZPLCCODE,
        ZACTIVEINACTIVE, PRODDESC, ZPRDUCTLINE, ZPRDLNEDESC,
        ZMAKEBUY, ZMATTYPE, ZITEMGRP, CREATEDBY, CREATEDDATE,
        LASTMODIFIEDBY, LASTMODIFIEDDATE
    ) VALUES (
        NULL,
        'SCN-NBU-001',
        'MAT' + RIGHT('00000' + CAST(@i AS VARCHAR), 5),
        'EA',
        'NBU',
        'BU0' + CAST((@i % 3) + 1 AS VARCHAR),
        'FAM-NBU-' + CAST((@i % 5) + 1 AS VARCHAR),
        CASE (@i % 5)
            WHEN 0 THEN 'ConnectX-7 SmartNIC'
            WHEN 1 THEN 'InfiniBand HDR Switch'
            WHEN 2 THEN '400G Ethernet NIC'
            WHEN 3 THEN 'BlueField-3 DPU'
            ELSE 'Spectrum-4 Switch'
        END,
        NULL, -- ZMARKETCODE is NULL for NBU
        NULL, -- ZTOPLVLNAME is NULL for NBU
        NULL, -- ZPLANNER is NULL for NBU
        NULL, -- ZPLCCODE is NULL for NBU
        'Active',
        CASE (@i % 5)
            WHEN 0 THEN 'Mellanox ConnectX-7 200GbE SmartNIC PCIe Gen5'
            WHEN 1 THEN 'NVIDIA Quantum-2 InfiniBand Switch 64-Port'
            WHEN 2 THEN 'ConnectX-7 Ethernet 400Gb Network Adapter'
            WHEN 3 THEN 'NVIDIA BlueField-3 DPU 400G InfiniBand'
            ELSE 'Spectrum-4 Ethernet Switch 51.2Tbps'
        END,
        'PL0' + CAST((@i % 5) + 1 AS VARCHAR),
        'Product Line ' + CAST((@i % 5) + 1 AS VARCHAR),
        CASE (@i % 2) WHEN 0 THEN 'Make' ELSE 'Buy' END,
        'FERT',
        'NBU_ITEM_GRP_' + CAST((@i % 5) + 1 AS VARCHAR),
        'SYSTEM',
        '2024-01-15',
        'SYSTEM',
        '2025-11-08'
    );

    IF @i % 100 = 0
        PRINT '  Progress: ' + CAST(@i AS VARCHAR) + ' IBP records inserted...';

    SET @i = @i + 1;
END;

PRINT '  ✅ brz_lnd_IBP_Product_Master: 1000 records inserted';
GO

-- ====================================================================
-- STEP 4: SEED brz_lnd_OPS_EXCEL_GPU (GPU Operations Planning)
-- ====================================================================
PRINT '';
PRINT '>>> STEP 4: Populating brz_lnd_OPS_EXCEL_GPU (500 GPU records)...';
PRINT '  Note: ~10% will have NULL PLANNING_SKU for realistic testing';
PRINT '';

DECLARE @i INT = 1;
WHILE @i <= 500
BEGIN
    INSERT INTO brz_lnd_OPS_EXCEL_GPU (
        PLANNING_SKU, Product_Line, Business_Unit, Marketing_Code, Planner,
        Customer, Active_Inactive, PLC_Code, Top_Level, BU,
        Marketing_Name_Ops, L1_Mapping, L2_Mapping, L3_Mapping,
        brz_LoadTime, ETL_BatchID, NEXTVAL, CURRVAL
    ) VALUES (
        -- Set PLANNING_SKU to NULL for every 10th record (~10% NULL values)
        CASE WHEN (@i % 10) = 0 THEN NULL ELSE 'MAT' + RIGHT('00000' + CAST(@i AS VARCHAR), 5) END,
        'PL0' + CAST((@i % 5) + 1 AS VARCHAR),
        'BU0' + CAST((@i % 3) + 1 AS VARCHAR),
        'MKT-GPU-' + CAST((@i % 10) + 1 AS VARCHAR),
        CASE (@i % 8)
            WHEN 0 THEN 'JSMITH'
            WHEN 1 THEN 'SJOHNSON'
            WHEN 2 THEN 'MCHEN'
            WHEN 3 THEN 'ERODRIGUEZ'
            WHEN 4 THEN 'DKIM'
            WHEN 5 THEN 'LWANG'
            WHEN 6 THEN 'JANDERSON'
            ELSE 'MGARCIA'
        END,
        'CUST' + CAST((@i % 20) + 1 AS VARCHAR),
        CASE (@i % 3) WHEN 0 THEN 'Active' WHEN 1 THEN 'Phase-In' ELSE 'Active' END,
        'PLC-' + CASE (@i % 4) WHEN 0 THEN 'GROWTH' WHEN 1 THEN 'MATURITY' WHEN 2 THEN 'INTRO' ELSE 'GROWTH' END,
        'TL-GPU-' + CAST((@i % 5) + 1 AS VARCHAR),
        'GPU',
        'GPU Marketing Name ' + CAST(@i AS VARCHAR),
        'L1-MAP-' + CAST(@i AS VARCHAR),
        'L2-MAP-' + CAST(@i AS VARCHAR),
        'L3-MAP-' + CAST(@i AS VARCHAR),
        GETDATE(),
        1000 + @i,
        @i,
        @i
    );

    IF @i % 100 = 0
        PRINT '  Progress: ' + CAST(@i AS VARCHAR) + ' OPS_EXCEL_GPU records inserted...';

    SET @i = @i + 1;
END;

PRINT '  ✅ brz_lnd_OPS_EXCEL_GPU: 500 GPU records inserted (~50 with NULL PLANNING_SKU)';
GO

-- ====================================================================
-- STEP 5: SEED brz_lnd_OPS_EXCEL_NBU (NBU Operations Planning)
-- ====================================================================
PRINT '';
PRINT '>>> STEP 5: Populating brz_lnd_OPS_EXCEL_NBU (500 NBU records)...';
PRINT '';

DECLARE @i INT = 501;
DECLARE @j INT = 1;
WHILE @i <= 1000
BEGIN
    INSERT INTO brz_lnd_OPS_EXCEL_NBU (
        MATERIAL_PN, MELLANOX_PN, PRODUCT_FAMILY, ITEM_GROUP, PLANNER,
        CUSTOMER, ACTIVE_INACTIVE, PLC_CODE, PRODUCT_TYPE, TECHNOLOGY,
        FORECASTING_MARKETING_CODE, FORECASTING_BU, L1_MAPPING, L2_MAPPING, L3_MAPPING,
        brz_LoadTime, ETL_BatchID
    ) VALUES (
        'MAT' + RIGHT('00000' + CAST(@i AS VARCHAR), 5),
        'MLX-' + RIGHT('00000' + CAST(@j AS VARCHAR), 5),
        CASE (@i % 3) WHEN 0 THEN 'ConnectX' WHEN 1 THEN 'BlueField' ELSE 'Spectrum' END,
        'NBU_' + CASE (@i % 3) WHEN 0 THEN 'NIC' WHEN 1 THEN 'DPU' ELSE 'Switch' END,
        NULL, -- PLANNER is NULL for NBU
        'CUST' + CAST((@i % 20) + 1 AS VARCHAR),
        'Active',
        NULL, -- PLC_CODE is NULL for NBU
        CASE (@i % 4)
            WHEN 0 THEN 'Network Adapter'
            WHEN 1 THEN 'Switch'
            WHEN 2 THEN 'Cable'
            ELSE 'Transceiver'
        END,
        CASE (@i % 3) WHEN 0 THEN 'InfiniBand' WHEN 1 THEN 'Ethernet' ELSE 'Fiber' END,
        'MKT-NBU-' + CAST((@j % 10) + 1 AS VARCHAR),
        'NBU',
        'NBU-L1-' + CAST(@j AS VARCHAR),
        'NBU-L2-' + CAST(@j AS VARCHAR),
        'NBU-L3-' + CAST(@j AS VARCHAR),
        GETDATE(),
        1500 + @j
    );

    IF @i % 100 = 0
        PRINT '  Progress: ' + CAST(@i AS VARCHAR) + ' OPS_EXCEL_NBU records inserted...';

    SET @i = @i + 1;
    SET @j = @j + 1;
END;

PRINT '  ✅ brz_lnd_OPS_EXCEL_NBU: 500 NBU records inserted';
GO

-- ====================================================================
-- STEP 6: SEED brz_lnd_RBP_GPU (Revenue Planning - GPU)
-- ====================================================================
PRINT '';
PRINT '>>> STEP 6: Populating brz_lnd_RBP_GPU (500 materials x 3 periods)...';
PRINT '';

DECLARE @i INT = 1;
DECLARE @period INT;
WHILE @i <= 500
BEGIN
    -- Insert 3 periods per material for revenue planning
    SET @period = 1;
    WHILE @period <= 3
    BEGIN
        INSERT INTO brz_lnd_RBP_GPU (
            Product_Line, Product_Line_Dec, Product_Family, Business_Unit,
            Material, Fiscal_Year_Period, Overall_Result
        ) VALUES (
            'PL0' + CAST((@i % 5) + 1 AS VARCHAR),
            'Product Line ' + CAST((@i % 5) + 1 AS VARCHAR),
            'FAM-GPU-' + CAST((@i % 5) + 1 AS VARCHAR),
            'BU0' + CAST((@i % 3) + 1 AS VARCHAR),
            'MAT' + RIGHT('00000' + CAST(@i AS VARCHAR), 5),
            '2025.00' + CAST(@period AS VARCHAR),
            CAST((1000000 + (@i * 1000) + (@period * 100)) AS VARCHAR)
        );
        SET @period = @period + 1;
    END;

    IF @i % 100 = 0
        PRINT '  Progress: ' + CAST(@i * 3 AS VARCHAR) + ' RBP_GPU records inserted...';

    SET @i = @i + 1;
END;

PRINT '  ✅ brz_lnd_RBP_GPU: 1500 records inserted (500 materials x 3 periods)';
GO

-- ====================================================================
-- STEP 7: SEED brz_lnd_RBP_NBU (Revenue Planning - NBU)
-- ====================================================================
PRINT '';
PRINT '>>> STEP 7: Populating brz_lnd_RBP_NBU (500 materials x 3 periods)...';
PRINT '';

DECLARE @i INT = 501;
DECLARE @period INT;
WHILE @i <= 1000
BEGIN
    -- Insert 3 periods per material for revenue planning
    SET @period = 1;
    WHILE @period <= 3
    BEGIN
        INSERT INTO brz_lnd_RBP_NBU (
            Product_Line, Product_Line_Desc, Product_Family, Business_Unit,
            Material, Fiscal_Year_Period, Overall_Result
        ) VALUES (
            'PL0' + CAST((@i % 5) + 1 AS VARCHAR),
            'NBU Line ' + CAST((@i % 5) + 1 AS VARCHAR),
            'FAM-NBU-' + CAST((@i % 5) + 1 AS VARCHAR),
            'BU0' + CAST((@i % 3) + 1 AS VARCHAR),
            'MAT' + RIGHT('00000' + CAST(@i AS VARCHAR), 5),
            '2025.00' + CAST(@period AS VARCHAR),
            CAST((800000 + (@i * 800) + (@period * 80)) AS VARCHAR)
        );
        SET @period = @period + 1;
    END;

    IF @i % 100 = 0
        PRINT '  Progress: ' + CAST((@i - 500) * 3 AS VARCHAR) + ' RBP_NBU records inserted...';

    SET @i = @i + 1;
END;

PRINT '  ✅ brz_lnd_RBP_NBU: 1500 records inserted (500 materials x 3 periods)';
GO

-- ====================================================================
-- STEP 8: SEED brz_lnd_SAR_Excel_GPU (SAR - GPU)
-- ====================================================================
PRINT '';
PRINT '>>> STEP 8: Populating brz_lnd_SAR_Excel_GPU (500 materials x 3 periods)...';
PRINT '';

DECLARE @i INT = 1;
DECLARE @period INT;
WHILE @i <= 500
BEGIN
    -- Insert 3 periods per material
    SET @period = 1;
    WHILE @period <= 3
    BEGIN
        INSERT INTO brz_lnd_SAR_Excel_GPU (
            Fiscal_Year_Period, Overall_Result, Material
        ) VALUES (
            '2025.00' + CAST(@period AS VARCHAR),
            CAST((500000 + (@i * 500) + (@period * 50)) AS VARCHAR),
            'MAT' + RIGHT('00000' + CAST(@i AS VARCHAR), 5)
        );
        SET @period = @period + 1;
    END;

    IF @i % 100 = 0
        PRINT '  Progress: ' + CAST(@i * 3 AS VARCHAR) + ' SAR_GPU records inserted...';

    SET @i = @i + 1;
END;

PRINT '  ✅ brz_lnd_SAR_Excel_GPU: 1500 records inserted (500 materials x 3 periods)';
GO

-- ====================================================================
-- STEP 9: SEED brz_lnd_SAR_Excel_NBU (SAR - NBU)
-- ====================================================================
PRINT '';
PRINT '>>> STEP 9: Populating brz_lnd_SAR_Excel_NBU (500 materials x 3 periods)...';
PRINT '';

DECLARE @i INT = 501;
DECLARE @period INT;
WHILE @i <= 1000
BEGIN
    -- Insert 3 periods per material
    SET @period = 1;
    WHILE @period <= 3
    BEGIN
        INSERT INTO brz_lnd_SAR_Excel_NBU (
            Fiscal_Year_Period, Overall_Result, Material
        ) VALUES (
            '2025.00' + CAST(@period AS VARCHAR),
            CAST((400000 + (@i * 400) + (@period * 40)) AS VARCHAR),
            'MAT' + RIGHT('00000' + CAST(@i AS VARCHAR), 5)
        );
        SET @period = @period + 1;
    END;

    IF @i % 100 = 0
        PRINT '  Progress: ' + CAST((@i - 500) * 3 AS VARCHAR) + ' SAR_NBU records inserted...';

    SET @i = @i + 1;
END;

PRINT '  ✅ brz_lnd_SAR_Excel_NBU: 1500 records inserted (500 materials x 3 periods)';
GO

-- ====================================================================
-- STEP 10: SEED brz_lnd_SKU_LIFNR_Excel (SKU Supplier Data)
-- ====================================================================
PRINT '';
PRINT '>>> STEP 10: Populating brz_lnd_SKU_LIFNR_Excel (1000 records)...';
PRINT '';

DECLARE @i INT = 1;
WHILE @i <= 1000
BEGIN
    INSERT INTO brz_lnd_SKU_LIFNR_Excel (
        ETL_BatchID, brz_RowId, Material, Supplier, Production_Version,
        Reference_BOM, Planning_BOM, Prod_stor_location,
        Receiving_stor_loc_for_material, Lead_time, Storage_Location,
        MRP_Area, Product_Type, Created_By, Created_On, Created_Time,
        brz_LoadTime
    ) VALUES (
        2000 + @i,
        @i,
        'MAT' + RIGHT('00000' + CAST(@i AS VARCHAR), 5),
        'SUPP' + RIGHT('0000' + CAST((@i % 50) + 1 AS VARCHAR), 4),
        'V001',
        'BOM-REF-' + CAST(@i AS VARCHAR),
        'BOM-PLN-' + CAST(@i AS VARCHAR),
        'SL01',
        'SL02',
        CAST((10 + (@i % 20)) AS VARCHAR),
        'WH01',
        'MRP-' + CAST((@i % 5) + 1 AS VARCHAR),
        CASE WHEN @i <= 500 THEN 'GPU' ELSE 'NBU' END,
        'ADMIN',
        '2024-01-15',
        '10:30:00',
        GETDATE()
    );

    IF @i % 100 = 0
        PRINT '  Progress: ' + CAST(@i AS VARCHAR) + ' SKU_LIFNR records inserted...';

    SET @i = @i + 1;
END;

PRINT '  ✅ brz_lnd_SKU_LIFNR_Excel: 1000 records inserted';
GO

-- ====================================================================
-- STEP 11: SEED brz_lnd_GPU_SKU_IN_SKULIFNR (GPU SKU Lookup)
-- ====================================================================
PRINT '';
PRINT '>>> STEP 11: Populating brz_lnd_GPU_SKU_IN_SKULIFNR (500 GPU records)...';
PRINT '';

DECLARE @i INT = 1;
WHILE @i <= 500
BEGIN
    INSERT INTO brz_lnd_GPU_SKU_IN_SKULIFNR (
        PLANNING_SKU, Prd_Type
    ) VALUES (
        'MAT' + RIGHT('00000' + CAST(@i AS VARCHAR), 5),
        'GPU'
    );

    IF @i % 100 = 0
        PRINT '  Progress: ' + CAST(@i AS VARCHAR) + ' GPU_SKU records inserted...';

    SET @i = @i + 1;
END;

PRINT '  ✅ brz_lnd_GPU_SKU_IN_SKULIFNR: 500 GPU records inserted';
GO

-- ====================================================================
-- COMPLETION SUMMARY
-- ====================================================================
PRINT '';
PRINT '====================================================================';
PRINT ' SEED DATA INSERTION COMPLETED SUCCESSFULLY';
PRINT '====================================================================';
PRINT ' Completed: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '====================================================================';
PRINT '';
PRINT 'Table                              | Records Inserted';
PRINT '----------------------------------------------------------------';
PRINT 'hana_material_master               | 1000 (500 GPU + 500 NBU)';
PRINT 'brz_lnd_IBP_Product_Master         | 1000 (500 GPU + 500 NBU)';
PRINT 'brz_lnd_OPS_EXCEL_GPU              | 500  (GPU only, ~50 NULL PLANNING_SKU)';
PRINT 'brz_lnd_OPS_EXCEL_NBU              | 500  (NBU only)';
PRINT 'brz_lnd_RBP_GPU                    | 1500 (500 materials x 3 periods)';
PRINT 'brz_lnd_RBP_NBU                    | 1500 (500 materials x 3 periods)';
PRINT 'brz_lnd_SAR_Excel_GPU              | 1500 (500 materials x 3 periods)';
PRINT 'brz_lnd_SAR_Excel_NBU              | 1500 (500 materials x 3 periods)';
PRINT 'brz_lnd_SKU_LIFNR_Excel            | 1000 (All materials)';
PRINT 'brz_lnd_GPU_SKU_IN_SKULIFNR        | 500  (GPU only)';
PRINT '====================================================================';
PRINT 'Total Base Materials: 1000';
PRINT 'Total Records Across All Tables: ~9500';
PRINT '';
PRINT 'GPU Materials: MAT00001 - MAT00500';
PRINT '  - Have values for: OPS_PLANNER, OPS_STATUS, OPS_PLCCODE,';
PRINT '                     ZTOPLVLNAME, ZMARKETCODE';
PRINT '';
PRINT 'NBU Materials: MAT00501 - MAT01000';
PRINT '  - NULL for: OPS_PLANNER, OPS_STATUS, OPS_PLCCODE,';
PRINT '              ZTOPLVLNAME, ZMARKETCODE';
PRINT '';
PRINT 'Special Notes:';
PRINT '  - brz_lnd_OPS_EXCEL_GPU: ~10% records have NULL PLANNING_SKU';
PRINT '    (every 10th record: MAT00010, MAT00020, ... MAT00500)';
PRINT '  - All column lengths comply with schema constraints';
PRINT '  - Realistic product names and planner data';
PRINT '====================================================================';
GO

-- ====================================================================
-- VERIFICATION QUERIES
-- ====================================================================
PRINT '';
PRINT '>>> VERIFICATION: Record Counts...';
PRINT '';

SELECT 'hana_material_master' AS TableName, COUNT(*) AS RecordCount FROM hana_material_master
UNION ALL
SELECT 'brz_lnd_IBP_Product_Master', COUNT(*) FROM brz_lnd_IBP_Product_Master
UNION ALL
SELECT 'brz_lnd_OPS_EXCEL_GPU', COUNT(*) FROM brz_lnd_OPS_EXCEL_GPU
UNION ALL
SELECT 'brz_lnd_OPS_EXCEL_NBU', COUNT(*) FROM brz_lnd_OPS_EXCEL_NBU
UNION ALL
SELECT 'brz_lnd_RBP_GPU', COUNT(*) FROM brz_lnd_RBP_GPU
UNION ALL
SELECT 'brz_lnd_RBP_NBU', COUNT(*) FROM brz_lnd_RBP_NBU
UNION ALL
SELECT 'brz_lnd_SAR_Excel_GPU', COUNT(*) FROM brz_lnd_SAR_Excel_GPU
UNION ALL
SELECT 'brz_lnd_SAR_Excel_NBU', COUNT(*) FROM brz_lnd_SAR_Excel_NBU
UNION ALL
SELECT 'brz_lnd_SKU_LIFNR_Excel', COUNT(*) FROM brz_lnd_SKU_LIFNR_Excel
UNION ALL
SELECT 'brz_lnd_GPU_SKU_IN_SKULIFNR', COUNT(*) FROM brz_lnd_GPU_SKU_IN_SKULIFNR;
GO

-- Verify NULL PLANNING_SKU in brz_lnd_OPS_EXCEL_GPU
PRINT '';
PRINT '>>> VERIFICATION: NULL PLANNING_SKU Analysis...';
PRINT '';

SELECT
    'Total Records' AS Category,
    COUNT(*) AS Count
FROM brz_lnd_OPS_EXCEL_GPU
UNION ALL
SELECT
    'Records with NULL PLANNING_SKU',
    COUNT(*)
FROM brz_lnd_OPS_EXCEL_GPU
WHERE PLANNING_SKU IS NULL
UNION ALL
SELECT
    'Records with Valid PLANNING_SKU',
    COUNT(*)
FROM brz_lnd_OPS_EXCEL_GPU
WHERE PLANNING_SKU IS NOT NULL;
GO

PRINT '';
PRINT '====================================================================';
PRINT ' ✅ MASTER SEED DATA SCRIPT COMPLETED SUCCESSFULLY!';
PRINT '====================================================================';
PRINT '';
