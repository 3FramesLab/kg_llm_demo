# NBU Tables Column Reference Fix ✅

## 🚨 Error Identified

**Error Messages**: Multiple "Invalid column name" errors
```
Msg 207, Level 16, State 1, Line 117
Invalid column name 'Product_Line_Dec'.
Msg 207, Level 16, State 1, Line 184
Invalid column name 'PLANNING_SKU'.
... (multiple similar errors)
```

**Root Cause**: 
- Script was referencing columns that don't exist in `hana_material_master`
- Assumed column names based on target table structure instead of source table structure

---

## 🔍 Actual hana_material_master Columns

### **Available Columns**:
```sql
MATERIAL                 NVARCHAR(18)   -- ✅ Available
MATERIAL_GROUP           NVARCHAR(9)    -- ✅ Available  
MATERIAL_TYPE            NVARCHAR(4)    -- ✅ Available
PLANT                    NVARCHAR(4)    -- ✅ Available
[Product Type]           NVARCHAR(5)    -- ✅ Available (with brackets)
[Business Unit]          NVARCHAR(5)    -- ✅ Available (with brackets)
[Product Line]           NVARCHAR(5)    -- ✅ Available (with brackets)
OPS_MKTG_NM             NVARCHAR(250)  -- ✅ Available
OPS_STATUS              NVARCHAR(50)   -- ✅ Available
OPS_PLCCODE             NVARCHAR(60)   -- ✅ Available
PRODGRP_CP              NVARCHAR(60)   -- ✅ Available
IBP_FINANCE_MKT_NAME    NVARCHAR(60)   -- ✅ Available
OPS_PLANNER             NVARCHAR(250)  -- ✅ Available
OPS_PLANNER_LAT         NVARCHAR(250)  -- ✅ Available
OPS_PLANNER_LAT_TEXT    NVARCHAR(20)   -- ✅ Available
MAKE_BUY                NVARCHAR(1)    -- ✅ Available
NBS_ITEM_GRP            NVARCHAR(250)  -- ✅ Available
AN_PLC_CD               NVARCHAR(60)   -- ✅ Available
```

### **Columns That DON'T Exist** (were causing errors):
```sql
Product_Line_Dec         -- ❌ Not in hana_material_master
PLANNING_SKU            -- ❌ Not in hana_material_master (target table column)
Marketing_Code          -- ❌ Not in hana_material_master (target table column)
Level_2_mapping_6       -- ❌ Not in hana_material_master (target table column)
Level_2_usage           -- ❌ Not in hana_material_master (target table column)
CHIP_Family             -- ❌ Not in hana_material_master (target table column)
NBU_1, NBU_usage, etc. -- ❌ Not in hana_material_master (target table columns)
```

---

## 🔧 Solution Applied

### **File Created**: `create_and_seed_nbu_tables_fixed.sql`

### **Key Fixes**:

#### **1. Use Actual Source Columns** ✅
```sql
-- BEFORE (Wrong - referencing non-existent columns)
SELECT Product_Line_Dec, PLANNING_SKU, Marketing_Code FROM hana_material_master

-- AFTER (Fixed - using actual columns)
SELECT [Product Line], MATERIAL, OPS_MKTG_NM FROM hana_material_master
```

#### **2. Generate Target Columns from Available Data** ✅
```sql
-- Product_Line_Dec (generated from Product Line)
CASE 
    WHEN [Product Line] = 'TEGRA' THEN 'Tegra Mobile SoC'
    WHEN [Product Line] = 'JETSO' THEN 'Jetson AI Computing'
    ELSE 'NBU Product Line'
END as Product_Line_Dec

-- PLANNING_SKU (use MATERIAL with NULL strategy)
CASE 
    WHEN ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5 = 0 THEN NULL
    ELSE MATERIAL
END as PLANNING_SKU
```

#### **3. Handle Column Name Brackets** ✅
```sql
-- Columns with spaces need brackets
[Product Type] = 'NBU'
[Business Unit]
[Product Line]
```

#### **4. Safe Planner Handling** ✅
```sql
-- Handle potential OPS_PLANNER truncation
CASE 
    WHEN LEN(OPS_PLANNER) <= 12 THEN OPS_PLANNER
    ELSE 'PLN_NBU_' + RIGHT('00' + CAST((ROW_NUMBER() OVER (ORDER BY MATERIAL) % 10) + 1 AS VARCHAR), 2)
END as Planner
```

#### **5. Safe Calculations** ✅
```sql
-- Prevent divide by zero errors
DECLARE @TotalNBU INT = (SELECT COUNT(*) FROM brz_lnd_OPS_EXCEL_NBU);
DECLARE @NullNBU INT = (SELECT COUNT(*) FROM brz_lnd_OPS_EXCEL_NBU WHERE PLANNING_SKU IS NULL);

SELECT 
    CASE 
        WHEN @TotalNBU = 0 THEN 0.00
        ELSE CAST(@NullNBU * 100.0 / @TotalNBU AS DECIMAL(5,2))
    END as Percentage;
```

---

## 🚀 Usage

### **Run Fixed Script**:
```sql
sqlcmd -S your_server -d your_database -i create_and_seed_nbu_tables_fixed.sql
```

### **Expected Success**:
- ✅ No "Invalid column name" errors
- ✅ NBU tables created successfully
- ✅ Data populated from actual hana_material_master columns
- ✅ 20% NULL PLANNING_SKU strategy maintained
- ✅ Safe calculations prevent divide by zero

---

## ✅ Key Learnings

### **Always Check Source Schema**:
- ✅ Verify actual column names before writing queries
- ✅ Don't assume column names based on target table structure
- ✅ Handle columns with spaces using brackets `[Column Name]`

### **Generate Missing Data**:
- ✅ Create target columns from available source data
- ✅ Use CASE statements to transform and generate values
- ✅ Maintain business logic while working with available columns

### **Safe Programming**:
- ✅ Use variables for calculations to prevent divide by zero
- ✅ Handle potential data truncation issues
- ✅ Test with actual schema before deployment

The fixed script now uses only actual columns from `hana_material_master` and generates the required target table data appropriately.
