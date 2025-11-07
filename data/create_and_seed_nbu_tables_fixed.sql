-- =====================================================
-- Create and Seed NBU Tables (FIXED VERSION)
-- Uses actual hana_material_master columns
-- =====================================================

SET NOCOUNT ON;
GO

PRINT '=== Creating and Seeding NBU Tables (Fixed Version) ===';

-- =====================================================
-- 1. Create brz_lnd_RBP_NBU table (same structure as brz_lnd_RBP_GPU)
-- =====================================================

PRINT 'Creating brz_lnd_RBP_NBU table...';

IF OBJECT_ID('brz_lnd_RBP_NBU', 'U') IS NOT NULL
    DROP TABLE brz_lnd_RBP_NBU;

CREATE TABLE brz_lnd_RBP_NBU (
    Product_Line NVARCHAR(14) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    Product_Line_Dec NVARCHAR(20) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    Product_Family NVARCHAR(14) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    Business_Unit NVARCHAR(13) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    Material NVARCHAR(18) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    Fiscal_Year_Period NVARCHAR(71) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    Overall_Result VARCHAR(255) COLLATE SQL_Latin1_General_CP850_BIN2 NULL
);

PRINT 'brz_lnd_RBP_NBU table created successfully';

-- =====================================================
-- 2. Create brz_lnd_OPS_EXCEL_NBU table (same structure as brz_lnd_OPS_EXCEL_GPU)
-- =====================================================

PRINT 'Creating brz_lnd_OPS_EXCEL_NBU table...';

IF OBJECT_ID('brz_lnd_OPS_EXCEL_NBU', 'U') IS NOT NULL
    DROP TABLE brz_lnd_OPS_EXCEL_NBU;

CREATE TABLE brz_lnd_OPS_EXCEL_NBU (
    PLANNING_SKU NVARCHAR(19) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    Product_Line NVARCHAR(12) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    Business_Unit NVARCHAR(13) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    Marketing_Code NVARCHAR(65) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    Planner NVARCHAR(12) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    Customer NVARCHAR(8) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    Active_Inactive NVARCHAR(16) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    Level_2_mapping_6 NVARCHAR(33) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    Level_2_usage NVARCHAR(14) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    CHIP_Family NVARCHAR(14) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    NBU_1 NVARCHAR(30) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    NBU_usage NVARCHAR(10) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    NBU_2 NVARCHAR(5) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    NBU_3 NVARCHAR(5) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    NBU_4 NVARCHAR(5) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    NBU_5 NVARCHAR(5) COLLATE SQL_Latin1_General_CP850_BIN2 NULL,
    ETL_BatchID INTEGER NULL,
    brz_LoadTime DATETIME NULL
);

PRINT 'brz_lnd_OPS_EXCEL_NBU table created successfully';

-- =====================================================
-- 3. Populate brz_lnd_RBP_NBU (250 NBU records)
-- =====================================================

PRINT '';
PRINT 'Populating brz_lnd_RBP_NBU with NBU records...';

INSERT INTO brz_lnd_RBP_NBU (
    Product_Line, Product_Line_Dec, Product_Family, Business_Unit, 
    Material, Fiscal_Year_Period, Overall_Result
)
SELECT
    -- NBU Product Lines (using actual Product Line from hana_material_master)
    CASE 
        WHEN [Product Line] = 'TEGRA' THEN 'TEGRA'
        WHEN [Product Line] = 'JETSO' THEN 'JETSON'
        WHEN [Product Line] = 'DRIVE' THEN 'DRIVE'
        WHEN [Product Line] = 'OMNIV' THEN 'OMNIVERSE'
        WHEN [Product Line] = 'MELLA' THEN 'MELLANOX'
        ELSE 'NBU_' + ISNULL([Product Line], 'GEN')
    END as Product_Line,

    -- NBU Product Line Descriptions
    CASE 
        WHEN [Product Line] = 'TEGRA' THEN 'Tegra Mobile SoC'
        WHEN [Product Line] = 'JETSO' THEN 'Jetson AI Computing'
        WHEN [Product Line] = 'DRIVE' THEN 'Drive Autonomous'
        WHEN [Product Line] = 'OMNIV' THEN 'Omniverse Platform'
        WHEN [Product Line] = 'MELLA' THEN 'Mellanox Networking'
        ELSE 'NBU Product Line'
    END as Product_Line_Dec,

    -- NBU Product Families
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 8)
        WHEN 0 THEN 'TEGRA_X1'
        WHEN 1 THEN 'TEGRA_X2'
        WHEN 2 THEN 'JETSON_NANO'
        WHEN 3 THEN 'JETSON_XAVIER'
        WHEN 4 THEN 'DRIVE_AGX'
        WHEN 5 THEN 'OMNIVERSE_RTX'
        WHEN 6 THEN 'MELLANOX_CX'
        ELSE 'DGX_A100'
    END as Product_Family,

    'NBU_BUSINESS' as Business_Unit,
    MATERIAL,
    
    -- Fiscal Year Period (2024.01 to 2024.12)
    '2024.' + RIGHT('00' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 12) + 1 AS VARCHAR), 2) as Fiscal_Year_Period,

    -- NBU Overall Results
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 6)
        WHEN 0 THEN 'Exceeds Target'
        WHEN 1 THEN 'Meets Target'
        WHEN 2 THEN 'Below Target'
        WHEN 3 THEN 'Under Development'
        WHEN 4 THEN 'In Production'
        ELSE 'Market Ready'
    END as Overall_Result

FROM hana_material_master
WHERE [Product Type] = 'NBU'
ORDER BY MATERIAL;

DECLARE @RBP_NBU_Count INT = @@ROWCOUNT;
PRINT 'Inserted ' + CAST(@RBP_NBU_Count AS VARCHAR) + ' records into brz_lnd_RBP_NBU';

-- =====================================================
-- 4. Populate brz_lnd_OPS_EXCEL_NBU (NBU records with NULL strategy)
-- =====================================================

PRINT '';
PRINT 'Populating brz_lnd_OPS_EXCEL_NBU with NBU records...';

INSERT INTO brz_lnd_OPS_EXCEL_NBU (
    PLANNING_SKU, Product_Line, Business_Unit, Marketing_Code, Planner,
    Customer, Active_Inactive, Level_2_mapping_6, Level_2_usage, CHIP_Family,
    NBU_1, NBU_usage, NBU_2, NBU_3, NBU_4, NBU_5,
    ETL_BatchID, brz_LoadTime
)
SELECT
    -- NULL PLANNING_SKU Strategy (20% NULL rate for testing)
    CASE
        WHEN ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5 = 0 THEN NULL
        WHEN OPS_STATUS = 'PHASE_OUT' AND ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3 = 0 THEN NULL
        ELSE MATERIAL
    END as PLANNING_SKU,

    -- NBU Product Lines (using actual Product Line from hana_material_master, shortened to fit NVARCHAR(12))
    CASE
        WHEN [Product Line] = 'TEGRA' THEN 'TEGRA'
        WHEN [Product Line] = 'JETSO' THEN 'JETSON'
        WHEN [Product Line] = 'DRIVE' THEN 'DRIVE'
        WHEN [Product Line] = 'OMNIV' THEN 'OMNIVERSE'
        WHEN [Product Line] = 'MELLA' THEN 'MELLANOX'
        ELSE LEFT('NBU_' + ISNULL([Product Line], 'GEN'), 12)
    END as Product_Line,

    -- Business Unit (using actual Business Unit from hana_material_master)
    ISNULL([Business Unit], 'NBU') as Business_Unit,

    -- Marketing Code (NULL when PLANNING_SKU is NULL)
    CASE
        WHEN ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5 = 0 THEN NULL
        WHEN OPS_STATUS = 'PHASE_OUT' AND ROW_NUMBER() OVER (ORDER BY MATERIAL) % 3 = 0 THEN NULL
        ELSE 'MKT_' + MATERIAL
    END as Marketing_Code,

    -- NBU Planner (fits in NVARCHAR(12), using truncated OPS_PLANNER or generated code)
    CASE
        WHEN LEN(OPS_PLANNER) <= 12 THEN OPS_PLANNER
        ELSE 'PLN_NBU_' + RIGHT('00' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 10) + 1 AS VARCHAR), 2)
    END as Planner,

    -- NBU Customers (different from GPU customers)
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 10)
        WHEN 0 THEN 'TESLA'
        WHEN 1 THEN 'MERCEDES'
        WHEN 2 THEN 'BMW'
        WHEN 3 THEN 'AUDI'
        WHEN 4 THEN 'VOLVO'
        WHEN 5 THEN 'FORD'
        WHEN 6 THEN 'GM'
        WHEN 7 THEN 'TOYOTA'
        WHEN 8 THEN 'HONDA'
        ELSE 'HYUNDAI'
    END as Customer,

    -- Active/Inactive status (using actual OPS_STATUS)
    CASE
        WHEN OPS_STATUS = 'ACTIVE' THEN 'Active'
        WHEN OPS_STATUS = 'PHASE_OUT' THEN 'Inactive'
        ELSE 'Active'
    END as Active_Inactive,

    -- Level 2 mapping (NULL when PLANNING_SKU is NULL)
    CASE
        WHEN ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5 = 0 THEN NULL
        ELSE 'L2_NBU_' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS VARCHAR)
    END as Level_2_mapping_6,

    -- NBU Level 2 usage
    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5)
        WHEN 0 THEN 'Automotive'
        WHEN 1 THEN 'Robotics'
        WHEN 2 THEN 'IoT'
        WHEN 3 THEN 'Edge AI'
        ELSE 'Embedded'
    END as Level_2_usage,

    -- NBU CHIP Family
    CASE
        WHEN [Product Line] = 'TEGRA' THEN 'Parker'
        WHEN [Product Line] = 'JETSO' THEN 'Xavier'
        WHEN [Product Line] = 'DRIVE' THEN 'Orin'
        WHEN [Product Line] = 'OMNIV' THEN 'Ada'
        WHEN [Product Line] = 'MELLA' THEN 'ConnectX'
        ELSE 'Grace'
    END as CHIP_Family,

    -- NBU specific columns
    'NBU_SPEC_' + CAST(ROW_NUMBER() OVER (ORDER BY MATERIAL) AS VARCHAR) as NBU_1,

    CASE (ROW_NUMBER() OVER (ORDER BY MATERIAL) % 4)
        WHEN 0 THEN 'AUTO'
        WHEN 1 THEN 'ROBOT'
        WHEN 2 THEN 'IOT'
        ELSE 'EDGE'
    END as NBU_usage,

    -- NBU_2 through NBU_5 (sample values)
    'N2_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 100) AS VARCHAR) as NBU_2,
    'N3_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 100) AS VARCHAR) as NBU_3,
    'N4_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 100) AS VARCHAR) as NBU_4,
    'N5_' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 100) AS VARCHAR) as NBU_5,

    1002 as ETL_BatchID,
    GETDATE() as brz_LoadTime

FROM hana_material_master
WHERE [Product Type] = 'NBU'
ORDER BY MATERIAL;

DECLARE @OPS_NBU_Count INT = @@ROWCOUNT;
PRINT 'Inserted ' + CAST(@OPS_NBU_Count AS VARCHAR) + ' records into brz_lnd_OPS_EXCEL_NBU';

-- =====================================================
-- 5. Safe Verification (no divide by zero)
-- =====================================================

PRINT '';
PRINT '=== NBU TABLES VERIFICATION (FIXED VERSION) ===';

-- Record counts
SELECT 'brz_lnd_RBP_NBU' as Table_Name, COUNT(*) as Record_Count FROM brz_lnd_RBP_NBU
UNION ALL
SELECT 'brz_lnd_OPS_EXCEL_NBU' as Table_Name, COUNT(*) as Record_Count FROM brz_lnd_OPS_EXCEL_NBU;

-- Safe NULL analysis
DECLARE @TotalNBU INT = (SELECT COUNT(*) FROM brz_lnd_OPS_EXCEL_NBU);
DECLARE @NullNBU INT = (SELECT COUNT(*) FROM brz_lnd_OPS_EXCEL_NBU WHERE PLANNING_SKU IS NULL);

SELECT 'Total NBU OPS Records' as Description, @TotalNBU as Count;
SELECT 'NBU Records with NULL PLANNING_SKU' as Description, @NullNBU as Count;
SELECT 'NBU Records with PLANNING_SKU' as Description, (@TotalNBU - @NullNBU) as Count;

-- Safe percentage calculation
SELECT
    'NBU Percentage of NULL PLANNING_SKU' as Description,
    CASE
        WHEN @TotalNBU = 0 THEN 0.00
        ELSE CAST(@NullNBU * 100.0 / @TotalNBU AS DECIMAL(5,2))
    END as Percentage;

-- Sample NBU data
PRINT '';
PRINT 'Sample NBU RBP data:';
SELECT TOP 10
    Product_Line,
    Product_Family,
    Material,
    Business_Unit,
    Overall_Result
FROM brz_lnd_RBP_NBU
ORDER BY Product_Line, Material;

PRINT '';
PRINT 'Sample NBU OPS EXCEL data:';
SELECT TOP 10
    PLANNING_SKU,
    Product_Line,
    Customer,
    Level_2_usage,
    CHIP_Family,
    Planner
FROM brz_lnd_OPS_EXCEL_NBU
ORDER BY Product_Line, Customer;

-- Safe join testing
DECLARE @JoinCount INT = (
    SELECT COUNT(*)
    FROM brz_lnd_RBP_NBU r
    INNER JOIN brz_lnd_OPS_EXCEL_NBU o ON r.Material = o.PLANNING_SKU
    WHERE o.PLANNING_SKU IS NOT NULL
);

SELECT 'NBU Materials matching between RBP and OPS' as Description, @JoinCount as Count;

PRINT '';
PRINT '=== NBU TABLES CREATION COMPLETE (FIXED) ===';
PRINT 'Summary:';
PRINT '- Fixed column references to use actual hana_material_master columns';
PRINT '- Created NBU tables with proper NBU-specific data';
PRINT '- Maintained 20% NULL PLANNING_SKU strategy for testing';
PRINT '- All divide by zero issues resolved with safe calculations';
PRINT '- Ready for NBU-specific joins and reconciliation testing';
PRINT '';
