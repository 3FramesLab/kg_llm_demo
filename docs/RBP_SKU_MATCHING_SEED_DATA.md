# RBP GPU & SKU LIFNR Excel Matching Seed Data ✅

## 🎯 Problem Identified

**Issue**: `brz_lnd_RBP_GPU` and `brz_lnd_SKU_LIFNR_Excel` tables had insufficient matching entries for proper joins and reconciliation queries.

**Root Cause**: 
- `brz_lnd_RBP_GPU` contained only **GPU materials** (250 records)
- `brz_lnd_SKU_LIFNR_Excel` contained **ALL materials** (500 records: GPU + NBU)
- But the data generation wasn't ensuring proper overlap for testing joins

---

## 🔧 Solution Implemented

### **File Created**: `seed_data_rbp_sku_matching_500.sql`

### **Strategy**: Ensure Perfect Material Matching
1. ✅ **RBP_GPU**: 250 GPU materials (GPU-001 to GPU-250)
2. ✅ **SKU_LIFNR_Excel**: 500 materials (250 GPU + 250 NBU)
3. ✅ **Perfect Overlap**: All 250 GPU materials in RBP_GPU have matching entries in SKU_LIFNR_Excel

---

## 📊 Data Structure

### **brz_lnd_RBP_GPU** (250 GPU Records)
```sql
Material: GPU-001, GPU-002, ..., GPU-250
Product_Line: GeForce RTX, GeForce GTX, Quadro RTX, Tesla V100, Tesla A100
Business_Unit: GPU_BUSINESS
Fiscal_Year_Period: 2024.01 to 2024.12
Overall_Result: Exceeds Target, Meets Target, Below Target, etc.
```

### **brz_lnd_SKU_LIFNR_Excel** (500 Records)
```sql
Material: GPU-001 to GPU-250, NBU-001 to NBU-250
Supplier: TSMC_001, SAMSUNG_002, GLOBALFOUNDRIES_003, etc.
Product_Type: GPU (250 records), NBU (250 records)
Lead_time: GPU (45-75 days), NBU (30-50 days)
Production_Version: PV_1, PV_2, ..., PV_500
```

---

## 🔗 Matching Relationships

### **Perfect GPU Matching** ✅
```sql
-- All these will return matching records
SELECT r.*, s.*
FROM brz_lnd_RBP_GPU r
INNER JOIN brz_lnd_SKU_LIFNR_Excel s ON r.Material = s.Material
-- Result: 250 matching records
```

### **Additional NBU Coverage** ✅
```sql
-- NBU materials in SKU_LIFNR_Excel (not in RBP_GPU)
SELECT s.*
FROM brz_lnd_SKU_LIFNR_Excel s
LEFT JOIN brz_lnd_RBP_GPU r ON s.Material = r.Material
WHERE r.Material IS NULL AND s.Product_Type = 'NBU'
-- Result: 250 NBU-only records
```

---

## 🎨 Business Logic Features

### **Realistic Supplier Data**
- **GPU Suppliers**: TSMC, Samsung, GlobalFoundries, Intel, ASML
- **Lead Times**: GPU (45-75 days), NBU (30-50 days)
- **Production Versions**: Unique for each material

### **Comprehensive Coverage**
- **Storage Locations**: 5 production, 3 receiving, 6 storage locations
- **MRP Areas**: 3 different MRP areas
- **Purchasing Groups**: 5 specialized groups
- **Priority Levels**: HIGH, MEDIUM, LOW

### **Time-Based Data**
- **Created Dates**: Last 60 days
- **Changed Dates**: Last 30 days
- **Fiscal Periods**: 2024.01 to 2024.12

---

## 🚀 Usage Instructions

### **1. Run the Seed Data Script**
```sql
-- Execute the seed data script
sqlcmd -S your_server -d your_database -i seed_data_rbp_sku_matching_500.sql
```

### **2. Verify Matching**
```sql
-- Check matching GPU records
SELECT COUNT(*) as Matching_GPU_Records
FROM brz_lnd_RBP_GPU r
INNER JOIN brz_lnd_SKU_LIFNR_Excel s ON r.Material = s.Material
WHERE s.Product_Type = 'GPU';
-- Expected: 250
```

### **3. Test Reconciliation Queries**
```sql
-- Find GPU materials in RBP but not in SKU_LIFNR (should be 0)
SELECT r.Material
FROM brz_lnd_RBP_GPU r
LEFT JOIN brz_lnd_SKU_LIFNR_Excel s ON r.Material = s.Material
WHERE s.Material IS NULL;
-- Expected: 0 records

-- Find GPU materials in SKU_LIFNR but not in RBP (should be 0)
SELECT s.Material
FROM brz_lnd_SKU_LIFNR_Excel s
LEFT JOIN brz_lnd_RBP_GPU r ON s.Material = r.Material
WHERE r.Material IS NULL AND s.Product_Type = 'GPU';
-- Expected: 0 records
```

---

## ✅ Expected Results

### **Record Counts**:
- ✅ `brz_lnd_RBP_GPU`: **250 records** (GPU only)
- ✅ `brz_lnd_SKU_LIFNR_Excel`: **500 records** (250 GPU + 250 NBU)

### **Join Success**:
- ✅ **100% GPU matching**: All RBP_GPU materials have SKU_LIFNR_Excel entries
- ✅ **Perfect reconciliation**: No orphaned GPU records in either table
- ✅ **Additional coverage**: 250 NBU materials for comprehensive testing

### **Query Testing**:
- ✅ **Inner joins**: Return 250 matching GPU records
- ✅ **Left joins**: Identify NBU-only records (250)
- ✅ **Reconciliation**: Perfect material coverage for GPU products

---

## 🎯 Benefits

### **Testing Capabilities**:
- ✅ **Join testing**: Perfect material matching for GPU products
- ✅ **Reconciliation testing**: Comprehensive coverage scenarios
- ✅ **Performance testing**: 500 records provide adequate test volume

### **Business Scenarios**:
- ✅ **GPU supply chain**: Complete supplier and lead time data
- ✅ **Mixed product types**: Both GPU and NBU for comprehensive testing
- ✅ **Realistic data**: Business-appropriate suppliers, locations, and timelines

This seed data ensures robust testing of joins and reconciliation queries between RBP_GPU and SKU_LIFNR_Excel tables.
