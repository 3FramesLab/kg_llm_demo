-- ====================================================================
-- Seed Data Script for All 10 Tables
-- 1000 Records Total: 500 GPU + 500 NBU
-- Material/PRDID/Planning_SKU Format: MAT00001, MAT00002, etc.
-- GPU: Has values for ops_planner, ops_status, ops_plccode, ztoplvlname, zmarketcode
-- NBU: NULL for ops_planner, ops_status, ops_plccode, ztoplvlname, zmarketcode
-- MS SQL Server Compatible
-- ====================================================================

USE NewDQ;
GO

-- ====================================================================
-- TRUNCATE ALL TABLES
-- ====================================================================
PRINT 'Truncating all tables...';

TRUNCATE TABLE brz_lnd_SAR_Excel_NBU;
TRUNCATE TABLE brz_lnd_SAR_Excel_GPU;
TRUNCATE TABLE brz_lnd_GPU_SKU_IN_SKULIFNR;
TRUNCATE TABLE brz_lnd_RBP_NBU;
TRUNCATE TABLE brz_lnd_RBP_GPU;
TRUNCATE TABLE brz_lnd_OPS_EXCEL_NBU;
TRUNCATE TABLE brz_lnd_OPS_EXCEL_GPU;
TRUNCATE TABLE brz_lnd_SKU_LIFNR_Excel;
TRUNCATE TABLE brz_lnd_IBP_Product_Master;
TRUNCATE TABLE hana_material_master;

PRINT 'All tables truncated successfully.';
GO

-- ====================================================================
-- TABLE 1: hana_material_master
-- All 1000 materials (500 GPU + 500 NBU)
-- ====================================================================
PRINT 'Inserting data into hana_material_master...';

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
            WHEN 2 THEN 'INTRODUCTION'
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
    SET @i = @i + 1;
END;

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
    SET @i = @i + 1;
END;

PRINT 'hana_material_master: 1000 records inserted (500 GPU + 500 NBU)';
GO

-- ====================================================================
-- TABLE 2: brz_lnd_IBP_Product_Master
-- All 1000 materials with comprehensive IBP data
-- ====================================================================
PRINT 'Inserting data into brz_lnd_IBP_Product_Master...';

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
            WHEN 2 THEN 'INTRODUCTION'
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
        '2025-11-06'
    );
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
        '2025-11-06'
    );
    SET @i = @i + 1;
END;

PRINT 'brz_lnd_IBP_Product_Master: 1000 records inserted';
GO

-- ====================================================================
-- TABLE 3: brz_lnd_OPS_EXCEL_GPU
-- 500 GPU materials only
-- NOTE: ~10% of records will have NULL PLANNING_SKU (every 10th record)
-- ====================================================================
PRINT 'Inserting data into brz_lnd_OPS_EXCEL_GPU...';

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
    SET @i = @i + 1;
END;

PRINT 'brz_lnd_OPS_EXCEL_GPU: 500 GPU records inserted (~50 with NULL PLANNING_SKU)';
GO

-- ====================================================================
-- TABLE 4: brz_lnd_OPS_EXCEL_NBU
-- 500 NBU materials only
-- ====================================================================
PRINT 'Inserting data into brz_lnd_OPS_EXCEL_NBU...';

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
    SET @i = @i + 1;
    SET @j = @j + 1;
END;

PRINT 'brz_lnd_OPS_EXCEL_NBU: 500 NBU records inserted';
GO

-- ====================================================================
-- TABLE 5: brz_lnd_RBP_GPU
-- 500 GPU materials with fiscal periods
-- ====================================================================
PRINT 'Inserting data into brz_lnd_RBP_GPU...';

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
    SET @i = @i + 1;
END;

PRINT 'brz_lnd_RBP_GPU: 1500 records inserted (500 materials x 3 periods)';
GO

-- ====================================================================
-- TABLE 6: brz_lnd_RBP_NBU
-- 500 NBU materials with fiscal periods
-- ====================================================================
PRINT 'Inserting data into brz_lnd_RBP_NBU...';

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
    SET @i = @i + 1;
END;

PRINT 'brz_lnd_RBP_NBU: 1500 records inserted (500 materials x 3 periods)';
GO

-- ====================================================================
-- TABLE 7: brz_lnd_SAR_Excel_GPU
-- 500 GPU materials with SAR data
-- ====================================================================
PRINT 'Inserting data into brz_lnd_SAR_Excel_GPU...';

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
    SET @i = @i + 1;
END;

PRINT 'brz_lnd_SAR_Excel_GPU: 1500 records inserted (500 materials x 3 periods)';
GO

-- ====================================================================
-- TABLE 8: brz_lnd_SAR_Excel_NBU
-- 500 NBU materials with SAR data
-- ====================================================================
PRINT 'Inserting data into brz_lnd_SAR_Excel_NBU...';

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
    SET @i = @i + 1;
END;

PRINT 'brz_lnd_SAR_Excel_NBU: 1500 records inserted (500 materials x 3 periods)';
GO

-- ====================================================================
-- TABLE 9: brz_lnd_SKU_LIFNR_Excel
-- All 1000 materials with supplier data
-- ====================================================================
PRINT 'Inserting data into brz_lnd_SKU_LIFNR_Excel...';

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
    SET @i = @i + 1;
END;

PRINT 'brz_lnd_SKU_LIFNR_Excel: 1000 records inserted';
GO

-- ====================================================================
-- TABLE 10: brz_lnd_GPU_SKU_IN_SKULIFNR
-- 500 GPU materials lookup
-- ====================================================================
PRINT 'Inserting data into brz_lnd_GPU_SKU_IN_SKULIFNR...';

DECLARE @i INT = 1;
WHILE @i <= 500
BEGIN
    INSERT INTO brz_lnd_GPU_SKU_IN_SKULIFNR (
        PLANNING_SKU, Prd_Type
    ) VALUES (
        'MAT' + RIGHT('00000' + CAST(@i AS VARCHAR), 5),
        'GPU'
    );
    SET @i = @i + 1;
END;

PRINT 'brz_lnd_GPU_SKU_IN_SKULIFNR: 500 GPU records inserted';
GO

-- ====================================================================
-- SUMMARY
-- ====================================================================
PRINT '';
PRINT '====================================================================';
PRINT 'SEED DATA INSERTION COMPLETED SUCCESSFULLY';
PRINT '====================================================================';
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
PRINT '====================================================================';
GO

-- Verify record counts
PRINT 'Verifying record counts...';
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
PRINT 'Verifying NULL PLANNING_SKU records in brz_lnd_OPS_EXCEL_GPU...';
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
