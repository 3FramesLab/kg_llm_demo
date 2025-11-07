# NBU Tables Creation and Seed Data ✅

## 🎯 Purpose

Created NBU counterparts to the existing GPU tables to support comprehensive testing of both product types:
- **`brz_lnd_RBP_NBU`** - NBU Revenue Planning data (mirrors `brz_lnd_RBP_GPU`)
- **`brz_lnd_OPS_EXCEL_NBU`** - NBU Operations Excel data (mirrors `brz_lnd_OPS_EXCEL_GPU`)

---

## 📊 Table Structures

### **brz_lnd_RBP_NBU** (250 NBU Records)
**Structure**: Identical to `brz_lnd_RBP_GPU`
```sql
Product_Line         NVARCHAR(14)   -- TEGRA, JETSON, DRIVE, OMNIVERSE, MELLANOX, DGX
Product_Line_Dec     NVARCHAR(20)   -- Descriptive names
Product_Family       NVARCHAR(14)   -- TEGRA_X1, JETSON_NANO, DRIVE_AGX, etc.
Business_Unit        NVARCHAR(13)   -- NBU_BUSINESS
Material             NVARCHAR(18)   -- NBU-001 to NBU-250
Fiscal_Year_Period   NVARCHAR(71)   -- 2024.01 to 2024.12
Overall_Result       VARCHAR(255)   -- Exceeds Target, Meets Target, etc.
```

### **brz_lnd_OPS_EXCEL_NBU** (250 NBU Records)
**Structure**: Similar to `brz_lnd_OPS_EXCEL_GPU` but with NBU-specific columns
```sql
PLANNING_SKU         NVARCHAR(19)   -- NBU materials (20% NULL for testing)
Product_Line         NVARCHAR(12)   -- TEGRA, JETSON, DRIVE, etc.
Business_Unit        NVARCHAR(13)   -- NBU business units
Marketing_Code       NVARCHAR(65)   -- MKT_NBU-xxx codes
Planner              NVARCHAR(12)   -- PLN_NBU_01 to PLN_NBU_10
Customer             NVARCHAR(8)    -- TESLA, MERCEDES, BMW, etc.
Active_Inactive      NVARCHAR(16)   -- Active/Inactive status
Level_2_mapping_6    NVARCHAR(33)   -- L2_NBU_xxx mappings
Level_2_usage        NVARCHAR(14)   -- Automotive, Robotics, IoT, Edge AI
CHIP_Family          NVARCHAR(14)   -- Parker, Xavier, Orin, Ada, ConnectX
NBU_1 to NBU_50      NVARCHAR(5)    -- NBU-specific columns (vs GPU_1 to GPU_50)
ETL_BatchID          INTEGER        -- 1002 (vs 1001 for GPU)
brz_LoadTime         DATETIME       -- Current timestamp
```

---

## 🎨 NBU-Specific Data Characteristics

### **NBU Product Lines**:
- **TEGRA**: Mobile SoC platforms
- **JETSON**: AI computing modules
- **DRIVE**: Autonomous vehicle platforms
- **OMNIVERSE**: Collaboration platforms
- **MELLANOX**: Networking solutions
- **DGX**: AI systems

### **NBU Product Families**:
- **TEGRA_X1, TEGRA_X2**: Mobile processors
- **JETSON_NANO, JETSON_XAVIER**: AI edge computing
- **DRIVE_AGX**: Autonomous driving
- **OMNIVERSE_RTX**: Real-time collaboration
- **MELLANOX_CX**: ConnectX networking
- **DGX_A100**: AI training systems

### **NBU Customers** (Automotive/Industrial):
- **Automotive**: TESLA, MERCEDES, BMW, AUDI, VOLVO
- **Traditional**: FORD, GM, TOYOTA, HONDA, HYUNDAI

### **NBU Use Cases**:
- **Automotive**: Self-driving cars, infotainment
- **Robotics**: Industrial automation, service robots
- **IoT**: Smart devices, edge computing
- **Edge AI**: Real-time inference, embedded AI
- **Embedded**: Custom applications, specialized hardware

---

## 🔗 Relationships and Joins

### **NBU Table Relationships**:
```sql
-- NBU RBP to NBU OPS join
brz_lnd_RBP_NBU.Material ↔ brz_lnd_OPS_EXCEL_NBU.PLANNING_SKU

-- Cross-product type analysis
brz_lnd_RBP_GPU.Material vs brz_lnd_RBP_NBU.Material
brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU vs brz_lnd_OPS_EXCEL_NBU.PLANNING_SKU
```

### **Join Testing Scenarios**:
```sql
-- NBU-only joins
SELECT COUNT(*) FROM brz_lnd_RBP_NBU r
INNER JOIN brz_lnd_OPS_EXCEL_NBU o ON r.Material = o.PLANNING_SKU;

-- Cross-product type comparison
SELECT 'GPU' as Product_Type, COUNT(*) as Count FROM brz_lnd_RBP_GPU
UNION ALL
SELECT 'NBU' as Product_Type, COUNT(*) as Count FROM brz_lnd_RBP_NBU;

-- Mixed product analysis
SELECT r.Material, r.Product_Line, 'GPU' as Type FROM brz_lnd_RBP_GPU r
UNION ALL
SELECT r.Material, r.Product_Line, 'NBU' as Type FROM brz_lnd_RBP_NBU r
ORDER BY Material;
```

---

## 🔍 Testing Capabilities

### **NULL Handling Testing**:
- ✅ **20% NULL PLANNING_SKU** in NBU OPS table
- ✅ **Cascading NULLs** in Marketing_Code and Level_2_mapping_6
- ✅ **JOIN behavior** testing (INNER vs LEFT JOIN)

### **Product Type Segregation**:
- ✅ **GPU vs NBU** comparison queries
- ✅ **Business unit** analysis (GPU_BUSINESS vs NBU_BUSINESS)
- ✅ **Customer base** differences (Gaming vs Automotive)

### **Data Quality Scenarios**:
- ✅ **Missing planning data** (NULL PLANNING_SKU)
- ✅ **Inactive products** (Phase-out scenarios)
- ✅ **Cross-reference validation** (RBP vs OPS consistency)

---

## 🚀 Usage Instructions

### **Create and Populate NBU Tables**:
```sql
sqlcmd -S your_server -d your_database -i create_and_seed_nbu_tables.sql
```

### **Verification Queries**:
```sql
-- Check record counts
SELECT 'RBP_NBU' as Table_Name, COUNT(*) FROM brz_lnd_RBP_NBU
UNION ALL
SELECT 'OPS_NBU' as Table_Name, COUNT(*) FROM brz_lnd_OPS_EXCEL_NBU;

-- Test NBU joins
SELECT COUNT(*) as NBU_Matching_Records
FROM brz_lnd_RBP_NBU r
INNER JOIN brz_lnd_OPS_EXCEL_NBU o ON r.Material = o.PLANNING_SKU
WHERE o.PLANNING_SKU IS NOT NULL;

-- Compare GPU vs NBU
SELECT 
    'GPU_RBP' as Source, COUNT(*) as Count FROM brz_lnd_RBP_GPU
UNION ALL
SELECT 
    'NBU_RBP' as Source, COUNT(*) as Count FROM brz_lnd_RBP_NBU
UNION ALL
SELECT 
    'GPU_OPS' as Source, COUNT(*) as Count FROM brz_lnd_OPS_EXCEL_GPU
UNION ALL
SELECT 
    'NBU_OPS' as Source, COUNT(*) as Count FROM brz_lnd_OPS_EXCEL_NBU;
```

---

## ✅ Expected Results

### **Record Counts**:
- **brz_lnd_RBP_NBU**: 250 records (NBU materials)
- **brz_lnd_OPS_EXCEL_NBU**: 250 records (NBU materials)
- **Total NBU records**: 500 across both tables

### **Data Distribution**:
- **Product Lines**: 6 NBU product lines (TEGRA, JETSON, DRIVE, etc.)
- **Customers**: 10 automotive/industrial customers
- **NULL Rate**: ~20% NULL PLANNING_SKU for testing
- **Business Unit**: All records have NBU_BUSINESS

### **Join Success**:
- **NBU Internal Joins**: ~200 matching records (80% due to NULL strategy)
- **Cross-Product Analysis**: GPU vs NBU comparison capabilities
- **Comprehensive Testing**: Both product types available for reconciliation

The NBU tables provide comprehensive test coverage for multi-product-type scenarios while maintaining the same data quality testing capabilities as the GPU tables.
