# OPS Excel GPU NULL PLANNING_SKU Strategy ✅

## 🎯 Purpose

Adding NULL values to the `PLANNING_SKU` column in `brz_lnd_OPS_EXCEL_GPU` creates realistic test scenarios for:
- **NULL handling in joins**
- **Data quality testing**
- **Reconciliation edge cases**
- **LEFT JOIN vs INNER JOIN behavior**

---

## 📊 NULL Value Strategy

### **Target NULL Rate**: ~20-25% of records

### **Strategic NULL Scenarios**:

#### 1. **Systematic Pattern** (20% base rate)
```sql
-- Every 5th record has NULL PLANNING_SKU
WHEN ROW_NUMBER() OVER (ORDER BY MATERIAL) % 5 = 0 THEN NULL
```

#### 2. **Inactive Products** (Data quality issue)
```sql
-- Some inactive products missing planning data
WHEN OPS_STATUS = 'PHASE_OUT' AND ROW_NUMBER() % 3 = 0 THEN NULL
```

#### 3. **Specific Product Lines** (System integration gaps)
```sql
-- QUADR product line has some missing planning data
WHEN [Product Line] = 'QUADR' AND ROW_NUMBER() % 7 = 0 THEN NULL
```

#### 4. **Cascading NULLs** (Realistic data dependencies)
```sql
-- When PLANNING_SKU is NULL, related fields are also NULL
Marketing_Code = NULL
Level_2_mapping_6 = NULL
```

---

## 🔧 Implementation Options

### **Option 1: Update Existing Data**
**File**: `update_ops_excel_gpu_null_planning_sku.sql`
- Updates existing `brz_lnd_OPS_EXCEL_GPU` records
- Sets ~20% of records to have NULL PLANNING_SKU
- Preserves other data

### **Option 2: Fresh Data Generation**
**File**: `seed_data_ops_excel_gpu_with_nulls.sql`
- Regenerates entire `brz_lnd_OPS_EXCEL_GPU` table
- Includes NULL strategy from the start
- More comprehensive NULL scenarios

---

## 📈 Expected Results

### **Record Distribution**:
```sql
-- Total records: ~250 (GPU only)
-- NULL PLANNING_SKU: ~50-60 records (20-25%)
-- Non-NULL PLANNING_SKU: ~190-200 records (75-80%)
```

### **NULL Breakdown by Category**:
```sql
-- Active products: ~15% NULL rate
-- Inactive products: ~35% NULL rate  
-- QUADR product line: ~30% NULL rate
-- Other product lines: ~18% NULL rate
```

---

## 🔍 Testing Scenarios Enabled

### **1. JOIN Behavior Testing**
```sql
-- INNER JOIN (excludes NULLs)
SELECT COUNT(*) FROM brz_lnd_RBP_GPU r
INNER JOIN brz_lnd_OPS_EXCEL_GPU o ON r.Material = o.PLANNING_SKU;
-- Expected: ~190-200 matches

-- LEFT JOIN (includes NULLs)
SELECT COUNT(*) FROM brz_lnd_RBP_GPU r
LEFT JOIN brz_lnd_OPS_EXCEL_GPU o ON r.Material = o.PLANNING_SKU;
-- Expected: ~250 total records
```

### **2. Data Quality Queries**
```sql
-- Find records with missing planning data
SELECT * FROM brz_lnd_OPS_EXCEL_GPU 
WHERE PLANNING_SKU IS NULL;

-- Find orphaned RBP records (no matching planning data)
SELECT r.* FROM brz_lnd_RBP_GPU r
LEFT JOIN brz_lnd_OPS_EXCEL_GPU o ON r.Material = o.PLANNING_SKU
WHERE o.PLANNING_SKU IS NULL;
```

### **3. Reconciliation Testing**
```sql
-- Products in RBP but missing from OPS planning
SELECT 
    r.Material,
    r.Product_Line,
    'Missing from OPS Planning' as Issue
FROM brz_lnd_RBP_GPU r
LEFT JOIN brz_lnd_OPS_EXCEL_GPU o ON r.Material = o.PLANNING_SKU
WHERE o.PLANNING_SKU IS NULL;
```

### **4. NULL Handling Validation**
```sql
-- Test COALESCE and ISNULL functions
SELECT 
    COALESCE(PLANNING_SKU, 'MISSING') as Planning_SKU_Clean,
    ISNULL(Marketing_Code, 'NO_MARKETING') as Marketing_Code_Clean
FROM brz_lnd_OPS_EXCEL_GPU;
```

---

## 🎨 Business Scenarios

### **Realistic NULL Causes**:
1. **Data Migration Issues**: Some planning data not migrated
2. **System Integration Gaps**: QUADR products from different system
3. **Process Delays**: Inactive products lose planning assignments
4. **Data Entry Errors**: Manual processes miss planning SKU assignment

### **Testing Benefits**:
- ✅ **Robust join testing**: Both successful and failed matches
- ✅ **Error handling**: NULL value processing in queries
- ✅ **Data quality**: Identify missing critical data
- ✅ **Reconciliation**: Find data gaps between systems

---

## 🚀 Usage Instructions

### **Quick Update (Existing Data)**:
```sql
sqlcmd -S your_server -d your_database -i update_ops_excel_gpu_null_planning_sku.sql
```

### **Fresh Generation (Clean Start)**:
```sql
sqlcmd -S your_server -d your_database -i seed_data_ops_excel_gpu_with_nulls.sql
```

### **Verification**:
```sql
-- Check NULL distribution
SELECT 
    'NULL PLANNING_SKU' as Type,
    COUNT(*) as Count,
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM brz_lnd_OPS_EXCEL_GPU) AS DECIMAL(5,2)) as Percentage
FROM brz_lnd_OPS_EXCEL_GPU
WHERE PLANNING_SKU IS NULL;
```

---

## ✅ Expected Benefits

### **Query Testing**:
- ✅ **JOIN variations**: Test INNER vs LEFT JOIN behavior
- ✅ **NULL handling**: Validate COALESCE, ISNULL, IS NULL conditions
- ✅ **Data quality**: Identify and handle missing data scenarios

### **Reconciliation Testing**:
- ✅ **Gap analysis**: Find products missing planning data
- ✅ **Data completeness**: Measure planning data coverage
- ✅ **Business impact**: Assess effect of missing planning information

### **Real-world Preparation**:
- ✅ **Production readiness**: Handle NULL values gracefully
- ✅ **Error scenarios**: Test edge cases and data quality issues
- ✅ **Reporting accuracy**: Ensure correct counts and calculations with NULLs

This NULL value strategy creates comprehensive test scenarios that mirror real-world data quality challenges.
