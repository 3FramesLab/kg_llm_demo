-- =====================================================
-- Check Actual Table Structure in Database
-- =====================================================

-- Check if tables exist and their column structures
PRINT '=====================================================';
PRINT 'CHECKING ACTUAL TABLE STRUCTURES IN DATABASE';
PRINT '=====================================================';

-- 1. Check if hana_material_master table exists
IF OBJECT_ID('hana_material_master', 'U') IS NOT NULL
BEGIN
    PRINT '';
    PRINT '1. hana_material_master - TABLE EXISTS';
    PRINT '   Columns:';
    
    SELECT 
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE,
        CHARACTER_MAXIMUM_LENGTH
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'hana_material_master'
    ORDER BY ORDINAL_POSITION;
END
ELSE
BEGIN
    PRINT '1. hana_material_master - TABLE DOES NOT EXIST!';
END

-- 2. Check brz_lnd_RBP_GPU
IF OBJECT_ID('brz_lnd_RBP_GPU', 'U') IS NOT NULL
BEGIN
    PRINT '';
    PRINT '2. brz_lnd_RBP_GPU - TABLE EXISTS';
    PRINT '   Column count:';
    SELECT COUNT(*) as ColumnCount FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'brz_lnd_RBP_GPU';
END
ELSE
BEGIN
    PRINT '2. brz_lnd_RBP_GPU - TABLE DOES NOT EXIST!';
END

-- 3. Check brz_lnd_OPS_EXCEL_GPU
IF OBJECT_ID('brz_lnd_OPS_EXCEL_GPU', 'U') IS NOT NULL
BEGIN
    PRINT '';
    PRINT '3. brz_lnd_OPS_EXCEL_GPU - TABLE EXISTS';
    PRINT '   Column count:';
    SELECT COUNT(*) as ColumnCount FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'brz_lnd_OPS_EXCEL_GPU';
END
ELSE
BEGIN
    PRINT '3. brz_lnd_OPS_EXCEL_GPU - TABLE DOES NOT EXIST!';
END

-- 4. Check brz_lnd_SKU_LIFNR_Excel
IF OBJECT_ID('brz_lnd_SKU_LIFNR_Excel', 'U') IS NOT NULL
BEGIN
    PRINT '';
    PRINT '4. brz_lnd_SKU_LIFNR_Excel - TABLE EXISTS';
    PRINT '   Column count:';
    SELECT COUNT(*) as ColumnCount FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'brz_lnd_SKU_LIFNR_Excel';
END
ELSE
BEGIN
    PRINT '4. brz_lnd_SKU_LIFNR_Excel - TABLE DOES NOT EXIST!';
END

-- 5. Check brz_lnd_IBP_Product_Master
IF OBJECT_ID('brz_lnd_IBP_Product_Master', 'U') IS NOT NULL
BEGIN
    PRINT '';
    PRINT '5. brz_lnd_IBP_Product_Master - TABLE EXISTS';
    PRINT '   Column count:';
    SELECT COUNT(*) as ColumnCount FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'brz_lnd_IBP_Product_Master';
END
ELSE
BEGIN
    PRINT '5. brz_lnd_IBP_Product_Master - TABLE DOES NOT EXIST!';
END

-- 6. Check brz_lnd_SAR_Excel_GPU
IF OBJECT_ID('brz_lnd_SAR_Excel_GPU', 'U') IS NOT NULL
BEGIN
    PRINT '';
    PRINT '6. brz_lnd_SAR_Excel_GPU - TABLE EXISTS';
    PRINT '   Column count:';
    SELECT COUNT(*) as ColumnCount FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'brz_lnd_SAR_Excel_GPU';
END
ELSE
BEGIN
    PRINT '6. brz_lnd_SAR_Excel_GPU - TABLE DOES NOT EXIST!';
END

-- 7. Check brz_lnd_GPU_SKU_IN_SKULIFNR
IF OBJECT_ID('brz_lnd_GPU_SKU_IN_SKULIFNR', 'U') IS NOT NULL
BEGIN
    PRINT '';
    PRINT '7. brz_lnd_GPU_SKU_IN_SKULIFNR - TABLE EXISTS';
    PRINT '   Column count:';
    SELECT COUNT(*) as ColumnCount FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'brz_lnd_GPU_SKU_IN_SKULIFNR';
END
ELSE
BEGIN
    PRINT '7. brz_lnd_GPU_SKU_IN_SKULIFNR - TABLE DOES NOT EXIST!';
END

-- 8. Check brz_lnd_SAR_Excel_NBU
IF OBJECT_ID('brz_lnd_SAR_Excel_NBU', 'U') IS NOT NULL
BEGIN
    PRINT '';
    PRINT '8. brz_lnd_SAR_Excel_NBU - TABLE EXISTS';
    PRINT '   Column count:';
    SELECT COUNT(*) as ColumnCount FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'brz_lnd_SAR_Excel_NBU';
END
ELSE
BEGIN
    PRINT '8. brz_lnd_SAR_Excel_NBU - TABLE DOES NOT EXIST!';
END

-- List all tables in the database
PRINT '';
PRINT '=====================================================';
PRINT 'ALL TABLES IN DATABASE:';
PRINT '=====================================================';

SELECT 
    TABLE_SCHEMA,
    TABLE_NAME,
    TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_SCHEMA, TABLE_NAME;

PRINT '';
PRINT '=====================================================';
PRINT 'DIAGNOSIS COMPLETE';
PRINT '=====================================================';
