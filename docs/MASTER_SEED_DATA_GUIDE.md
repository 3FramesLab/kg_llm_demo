# Master Seed Data Script - Complete Guide

## Overview

The **master_seed_data.sql** script is a comprehensive, all-in-one seed data solution for the NewDQ database. It consolidates all previous seed data scripts into a single, well-structured, and maintainable SQL file.

---

## File Location

```
D:\learning\dq-poc\data\master_seed_data.sql
```

---

## What This Script Does

### Complete Database Population

1. **Truncates all 10 tables** for a clean start
2. **Seeds 1000 base materials** (500 GPU + 500 NBU)
3. **Populates all related tables** with matching data
4. **Includes realistic data** with proper NULL handling
5. **Generates ~9500 total records** across all tables

---

## Key Features

### ✅ Comprehensive Coverage
- All 10 tables in the schema
- 1000 base materials as foundation
- Multiple periods for time-series tables

### ✅ Realistic Data
- **GPU Products**: NVIDIA GeForce RTX 4090, AMD Radeon RX 7900 XTX, Tesla A100, H100
- **NBU Products**: ConnectX-7 SmartNIC, InfiniBand Switches, BlueField-3 DPU
- **Planner Names**: John Smith, Sarah Johnson, Michael Chen, Emily Rodriguez, David Kim, Lisa Wang, James Anderson, Maria Garcia

### ✅ Proper NULL Handling
- **GPU Materials (MAT00001 - MAT00500)**: Have values for OPS_PLANNER, OPS_STATUS, OPS_PLCCODE, ZTOPLVLNAME, ZMARKETCODE
- **NBU Materials (MAT00501 - MAT01000)**: NULL for these columns (realistic business scenario)
- **~10% of brz_lnd_OPS_EXCEL_GPU**: NULL PLANNING_SKU for testing edge cases

### ✅ Column Length Compliance
- All values respect schema constraints
- No truncation errors
- Planner names fit within NVARCHAR limits

### ✅ Progress Indicators
- Shows progress every 100 records
- Clear step-by-step output
- Verification queries at the end

---

## Execution Instructions

### Prerequisites

1. **SQL Server** must be running
2. **NewDQ database** must exist
3. **All 10 tables** must be created (use schema DDL)
4. **Sufficient permissions** to truncate and insert

### Method 1: SQL Server Management Studio (SSMS)

```sql
-- 1. Open SSMS
-- 2. Connect to your SQL Server instance
-- 3. Open the file: File > Open > File > master_seed_data.sql
-- 4. Ensure "NewDQ" is selected in the database dropdown
-- 5. Click Execute (F5)
```

### Method 2: Command Line (sqlcmd)

```bash
sqlcmd -S DESKTOP-41O1AL9\LOCALHOST -d NewDQ -U mithun -P mithun123 -i "D:\learning\dq-poc\data\master_seed_data.sql"
```

### Method 3: Azure Data Studio

```sql
-- 1. Open Azure Data Studio
-- 2. Connect to your SQL Server
-- 3. Open master_seed_data.sql
-- 4. Click Run
```

---

## Execution Time

**Approximate Duration**: 2-5 minutes

- Truncation: ~5 seconds
- hana_material_master: ~30 seconds
- All other tables: ~1-3 minutes
- Verification: ~5 seconds

---

## Data Structure

### Materials Distribution

| Range | Product Type | Count | Details |
|-------|--------------|-------|---------|
| MAT00001 - MAT00500 | GPU | 500 | Gaming & Data Center GPUs |
| MAT00501 - MAT01000 | NBU | 500 | Networking & InfiniBand |

### Record Counts

| Table | Records | Notes |
|-------|---------|-------|
| `hana_material_master` | 1,000 | Base material master |
| `brz_lnd_IBP_Product_Master` | 1,000 | IBP planning data |
| `brz_lnd_OPS_EXCEL_GPU` | 500 | GPU operations (~50 with NULL PLANNING_SKU) |
| `brz_lnd_OPS_EXCEL_NBU` | 500 | NBU operations |
| `brz_lnd_RBP_GPU` | 1,500 | Revenue planning (500 × 3 periods) |
| `brz_lnd_RBP_NBU` | 1,500 | Revenue planning (500 × 3 periods) |
| `brz_lnd_SAR_Excel_GPU` | 1,500 | SAR data (500 × 3 periods) |
| `brz_lnd_SAR_Excel_NBU` | 1,500 | SAR data (500 × 3 periods) |
| `brz_lnd_SKU_LIFNR_Excel` | 1,000 | Supplier data |
| `brz_lnd_GPU_SKU_IN_SKULIFNR` | 500 | GPU SKU lookup |
| **TOTAL** | **~9,500** | Across all tables |

---

## Sample Data

### GPU Material Example (MAT00001)

```sql
-- hana_material_master
MATERIAL: MAT00001
MATERIAL_TYPE: FERT
Product Type: GPU
OPS_PLANNER: John Smith
OPS_STATUS: Active
OPS_PLCCODE: PLC-GROWTH
OPS_MKTG_NM: NVIDIA GeForce RTX 4090 Graphics Card

-- brz_lnd_OPS_EXCEL_GPU
PLANNING_SKU: MAT00001
Planner: JSMITH
Active_Inactive: Active
Product_Line: PL01
Business_Unit: BU01

-- brz_lnd_RBP_GPU
Material: MAT00001
Fiscal_Year_Period: 2025.001, 2025.002, 2025.003
Overall_Result: 1001100, 1001200, 1001300
```

### NBU Material Example (MAT00501)

```sql
-- hana_material_master
MATERIAL: MAT00501
MATERIAL_TYPE: FERT
Product Type: NBU
OPS_PLANNER: NULL  ← Note: NULL for NBU
OPS_STATUS: NULL
OPS_PLCCODE: NULL
OPS_MKTG_NM: Mellanox ConnectX-7 SmartNIC Network Adapter

-- brz_lnd_OPS_EXCEL_NBU
MATERIAL_PN: MAT00501
PLANNER: NULL  ← Note: NULL for NBU
PLC_CODE: NULL
PRODUCT_FAMILY: ConnectX
ITEM_GROUP: NBU_NIC

-- brz_lnd_RBP_NBU
Material: MAT00501
Fiscal_Year_Period: 2025.001, 2025.002, 2025.003
Overall_Result: 801400, 801480, 801560
```

---

## Verification

### After Execution

The script automatically runs verification queries. Expected output:

```
TableName                         RecordCount
--------------------------------  -----------
hana_material_master              1000
brz_lnd_IBP_Product_Master        1000
brz_lnd_OPS_EXCEL_GPU             500
brz_lnd_OPS_EXCEL_NBU             500
brz_lnd_RBP_GPU                   1500
brz_lnd_RBP_NBU                   1500
brz_lnd_SAR_Excel_GPU             1500
brz_lnd_SAR_Excel_NBU             1500
brz_lnd_SKU_LIFNR_Excel           1000
brz_lnd_GPU_SKU_IN_SKULIFNR       500
```

### Manual Verification Queries

```sql
-- Check GPU vs NBU distribution
SELECT
    [Product Type],
    COUNT(*) as Total,
    COUNT(OPS_PLANNER) as With_Planner,
    COUNT(*) - COUNT(OPS_PLANNER) as Without_Planner
FROM hana_material_master
GROUP BY [Product Type];

-- Expected:
-- GPU: 500 total, 500 with planner, 0 without
-- NBU: 500 total, 0 with planner, 500 without

-- Check NULL PLANNING_SKU in OPS_EXCEL_GPU
SELECT
    COUNT(*) as Total_Records,
    SUM(CASE WHEN PLANNING_SKU IS NULL THEN 1 ELSE 0 END) as Null_Count,
    SUM(CASE WHEN PLANNING_SKU IS NOT NULL THEN 1 ELSE 0 END) as Not_Null_Count
FROM brz_lnd_OPS_EXCEL_GPU;

-- Expected: 500 total, ~50 null, ~450 not null

-- Check unique planners
SELECT DISTINCT OPS_PLANNER
FROM hana_material_master
WHERE OPS_PLANNER IS NOT NULL
ORDER BY OPS_PLANNER;

-- Expected: 8 unique planners
```

---

## Troubleshooting

### Issue: Truncate fails with foreign key error

**Solution**: Disable foreign key constraints temporarily

```sql
-- Disable constraints
EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL';

-- Run the seed script
-- (execute master_seed_data.sql)

-- Re-enable constraints
EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL';
```

### Issue: Script timeout

**Solution**: Increase command timeout in SSMS

```
Tools > Options > Query Execution > SQL Server > Advanced
Set "Execution time-out" to 0 (unlimited)
```

### Issue: Slow execution

**Reasons**:
- Large number of inserts
- Indexes on tables
- Transaction log growing

**Solutions**:
- Drop indexes before seeding, recreate after
- Run in batches (comment out some tables)
- Increase transaction log size

### Issue: Duplicate key errors

**Cause**: Tables not truncated properly

**Solution**:
```sql
-- Manually delete all data
DELETE FROM brz_lnd_SAR_Excel_NBU;
DELETE FROM brz_lnd_SAR_Excel_GPU;
DELETE FROM brz_lnd_GPU_SKU_IN_SKULIFNR;
DELETE FROM brz_lnd_RBP_NBU;
DELETE FROM brz_lnd_RBP_GPU;
DELETE FROM brz_lnd_OPS_EXCEL_NBU;
DELETE FROM brz_lnd_OPS_EXCEL_GPU;
DELETE FROM brz_lnd_SKU_LIFNR_Excel;
DELETE FROM brz_lnd_IBP_Product_Master;
DELETE FROM hana_material_master;

-- Then run the seed script
```

---

## Testing KPI Queries

### After seeding, test common KPI queries:

```sql
-- 1. Products in RBP but not in OPS (GPU)
SELECT DISTINCT r.Material
FROM brz_lnd_RBP_GPU r
LEFT JOIN brz_lnd_OPS_EXCEL_GPU o ON r.Material = o.PLANNING_SKU
WHERE o.PLANNING_SKU IS NULL;

-- Expected: ~50 results (those with NULL PLANNING_SKU)

-- 2. Get OPS_PLANNER for materials
SELECT DISTINCT
    s.Material,
    h.OPS_PLANNER
FROM brz_lnd_SKU_LIFNR_Excel s
LEFT JOIN hana_material_master h ON s.Material = h.MATERIAL
WHERE s.Product_Type = 'GPU'
ORDER BY h.OPS_PLANNER;

-- Expected: 500 GPU materials with 8 different planners

-- 3. Materials with missing data
SELECT
    m.MATERIAL,
    m.[Product Type],
    m.OPS_PLANNER,
    i.PRDID as IBP_Exists,
    o.PLANNING_SKU as OPS_Exists
FROM hana_material_master m
LEFT JOIN brz_lnd_IBP_Product_Master i ON m.MATERIAL = i.PRDID
LEFT JOIN brz_lnd_OPS_EXCEL_GPU o ON m.MATERIAL = o.PLANNING_SKU
WHERE m.[Product Type] = 'GPU'
ORDER BY m.MATERIAL;
```

---

## Comparison with Previous Scripts

| Feature | Old Scripts | Master Script |
|---------|-------------|---------------|
| Number of files | 9 separate files | 1 consolidated file |
| Truncate steps | Inconsistent | ✅ All tables |
| NULL handling | Manual fixes needed | ✅ Built-in |
| Progress indicators | ❌ None | ✅ Every 100 records |
| Documentation | Scattered | ✅ Comprehensive |
| Verification | Manual | ✅ Automatic |
| Column compliance | Required fixes | ✅ Pre-validated |
| Realistic data | Basic | ✅ Production-like |

---

## Maintenance

### To Modify Data

**Change record counts**:
```sql
-- Line 122: WHILE @i <= 500  -- Change 500 to desired GPU count
-- Line 175: WHILE @i <= 1000 -- Change 1000 to total (GPU + NBU)
```

**Add new planner names**:
```sql
-- Lines 147-154: Add new CASE branches
CASE (@i % 10)
    WHEN 0 THEN 'John Smith'
    WHEN 1 THEN 'Sarah Johnson'
    -- ... add more
    WHEN 9 THEN 'Your New Planner'
END
```

**Change product names**:
```sql
-- Lines 138-143: Modify product descriptions
CASE (@i % 5)
    WHEN 0 THEN 'Your New Product Name'
    -- ...
END
```

---

## Best Practices

1. **Always backup** before running seed scripts
2. **Test on dev environment** first
3. **Review verification** output after execution
4. **Keep the script in version control**
5. **Document any customizations**

---

## Related Files

- **Schema DDL**: `schemas/dqschema.json`
- **KPI Definitions**: Stored in `KPI_Analytics` database
- **API Configuration**: `.env` file (SOURCE_DB settings)

---

## Change Log

### Version 2.0 (2025-11-08)
- Consolidated all seed scripts into one master script
- Added comprehensive documentation
- Added progress indicators
- Added automatic verification
- Improved realistic data

### Version 1.0
- Original `seed_data_all_tables_1000_records.sql`
- Basic seed data for 10 tables

---

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review execution logs
3. Verify database permissions
4. Check SQL Server error logs

---

**✅ Ready to Use!**

Simply execute `master_seed_data.sql` and your NewDQ database will be fully populated with realistic test data.
