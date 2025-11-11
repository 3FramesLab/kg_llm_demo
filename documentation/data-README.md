# Data Folder - SQL Scripts

This folder contains all SQL scripts for database setup, seed data, and fixes.

---

## 📋 Quick Start

**For new setup, use this file ONLY:**

### ⭐ **master_seed_data.sql**
**The comprehensive, all-in-one seed data script**
- Seeds all 10 tables with 1000 materials
- Includes realistic data (GPU & NBU products)
- Handles NULL values properly
- Includes verification queries
- **Execution time**: ~2-5 minutes
- **Documentation**: See `docs/MASTER_SEED_DATA_GUIDE.md`

```sql
-- How to run:
USE NewDQ;
GO
-- Then execute: master_seed_data.sql
```

---

## 📁 File Categories

### ✅ RECOMMENDED FILES

| File | Purpose | Status |
|------|---------|--------|
| **master_seed_data.sql** | **Main seed script - USE THIS** | ⭐ Current |

### 📦 LEGACY FILES (For Reference Only)

These files have been consolidated into `master_seed_data.sql`:

| File | Purpose | Status |
|------|---------|--------|
| seed_data_all_tables_1000_records.sql | Previous comprehensive seed | ⚠️ Legacy |
| seed_data_500_items_gpu_nbu.sql | GPU/NBU seed (500 items) | ⚠️ Legacy |
| seed_data_500_items_gpu_nbu_fixed.sql | Fixed version | ⚠️ Legacy |
| seed_data_rbp_sku_matching_500.sql | RBP/SKU matching data | ⚠️ Legacy |
| seed_data_ops_excel_gpu_with_nulls.sql | OPS GPU with NULLs | ⚠️ Legacy |
| seed_ops_excel_gpu_robust.sql | Robust OPS GPU seed | ⚠️ Legacy |

### 🔧 FIX SCRIPTS (Post-Processing)

Apply these **AFTER** seed data if needed:

| File | Purpose | When to Use |
|------|---------|-------------|
| fix_hana_material_master_planner.sql | Fixes long planner names | If OPS_PLANNER > 12 chars |
| fix_ops_excel_gpu_planner_truncation.sql | Fixes planner truncation | After OPS_EXCEL_GPU seed |
| update_ops_excel_gpu_null_planning_sku.sql | Adds NULL PLANNING_SKU | For testing NULL scenarios |
| fix_ibp_prdid_matching.sql | Fixes IBP PRDID matching | If IBP joins fail |

### 🏗️ TABLE CREATION SCRIPTS

| File | Purpose | Status |
|------|---------|--------|
| create_and_seed_nbu_tables.sql | Creates & seeds NBU tables | ⚠️ Legacy |
| create_and_seed_nbu_tables_fixed.sql | Fixed NBU table creation | ⚠️ Legacy |
| create_tables_and_seed_data.sql | Combined create & seed | ⚠️ Legacy |

### 🧪 TEST & VERIFICATION SCRIPTS

| File | Purpose |
|------|---------|
| check_actual_table_structure.sql | Verifies table structure |
| verify_nbu_tables.sql | Verifies NBU tables |
| generate_1000_test_records.sql | Test record generator |
| generate_1000_test_records_FIXED.sql | Fixed test generator |

### 🔄 RECONCILIATION SCRIPTS (Output from Recon API)

| File | Purpose |
|------|---------|
| reconciliation_execution_RECON_*.sql | Generated recon queries |
| reconciliation_queries_RECON_*_all.sql | All reconciliation queries |
| reconciliation_queries_RECON_*_matched.sql | Matched records only |

---

## 🚀 Usage Guide

### For Fresh Database Setup

1. **Create database schema** (if not exists)
   ```sql
   -- Use your schema DDL from schemas/dqschema.json
   ```

2. **Run master seed script**
   ```sql
   -- Execute: master_seed_data.sql
   -- This will:
   -- - Truncate all tables
   -- - Seed 1000 materials
   -- - Populate all 10 tables
   -- - Run verification
   ```

3. **Done!** Your database is ready for KPI execution

### For Existing Database

1. **Backup first!**
   ```sql
   BACKUP DATABASE NewDQ TO DISK = 'D:\backups\NewDQ_backup.bak';
   ```

2. **Run master seed script**
   - It will truncate existing data
   - Then populate with fresh seed data

### For Specific Issues

**Issue: Planner names too long**
```sql
-- Run: fix_hana_material_master_planner.sql
```

**Issue: Need more NULL PLANNING_SKU records**
```sql
-- Run: update_ops_excel_gpu_null_planning_sku.sql
```

---

## 📊 What Gets Created

### Tables Populated (All 10)

1. **hana_material_master** - 1000 materials (500 GPU + 500 NBU)
2. **brz_lnd_IBP_Product_Master** - 1000 IBP records
3. **brz_lnd_OPS_EXCEL_GPU** - 500 GPU operations (~50 with NULL PLANNING_SKU)
4. **brz_lnd_OPS_EXCEL_NBU** - 500 NBU operations
5. **brz_lnd_RBP_GPU** - 1500 revenue planning (500 × 3 periods)
6. **brz_lnd_RBP_NBU** - 1500 revenue planning (500 × 3 periods)
7. **brz_lnd_SAR_Excel_GPU** - 1500 SAR records (500 × 3 periods)
8. **brz_lnd_SAR_Excel_NBU** - 1500 SAR records (500 × 3 periods)
9. **brz_lnd_SKU_LIFNR_Excel** - 1000 supplier records
10. **brz_lnd_GPU_SKU_IN_SKULIFNR** - 500 GPU SKU lookup

**Total: ~9,500 records**

### Material ID Format

- **GPU**: MAT00001 - MAT00500
- **NBU**: MAT00501 - MAT01000

### Key Data Points

**Planners** (for GPU only):
- John Smith (JSMITH)
- Sarah Johnson (SJOHNSON)
- Michael Chen (MCHEN)
- Emily Rodriguez (ERODRIGUEZ)
- David Kim (DKIM)
- Lisa Wang (LWANG)
- James Anderson (JANDERSON)
- Maria Garcia (MGARCIA)

**Product Types**:
- GPU: NVIDIA GeForce, AMD Radeon, Tesla A100, H100
- NBU: ConnectX-7, InfiniBand, BlueField-3, Spectrum-4

---

## ⚠️ Important Notes

### 1. Database Connection
Scripts assume:
- Database: **NewDQ**
- Server: **DESKTOP-41O1AL9\LOCALHOST**
- Update connection strings if different

### 2. Execution Order
For custom setup:
1. Schema/DDL (create tables)
2. master_seed_data.sql (populate data)
3. Fix scripts (if needed)

### 3. Foreign Keys
If you have foreign key constraints:
```sql
-- Disable before truncate
EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL';

-- Run seed script

-- Re-enable after
EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL';
```

### 4. Transaction Log
For large inserts, ensure sufficient transaction log space:
```sql
-- Check log usage
DBCC SQLPERF(LOGSPACE);

-- Increase if needed
ALTER DATABASE NewDQ MODIFY FILE (NAME = NewDQ_log, SIZE = 1GB);
```

---

## 🔍 Verification

### After Running Seed Script

```sql
-- 1. Check record counts
SELECT 'hana_material_master' AS TableName, COUNT(*) AS Records FROM hana_material_master
UNION ALL
SELECT 'brz_lnd_OPS_EXCEL_GPU', COUNT(*) FROM brz_lnd_OPS_EXCEL_GPU
UNION ALL
SELECT 'brz_lnd_RBP_GPU', COUNT(*) FROM brz_lnd_RBP_GPU;

-- 2. Check data quality
SELECT
    [Product Type],
    COUNT(*) as Total,
    COUNT(OPS_PLANNER) as With_Planner
FROM hana_material_master
GROUP BY [Product Type];

-- 3. Check NULL handling
SELECT
    COUNT(*) as Total,
    SUM(CASE WHEN PLANNING_SKU IS NULL THEN 1 ELSE 0 END) as Null_Count
FROM brz_lnd_OPS_EXCEL_GPU;
```

---

## 📚 Additional Resources

- **Master Seed Data Guide**: `docs/MASTER_SEED_DATA_GUIDE.md`
- **Schema Definition**: `schemas/dqschema.json`
- **Database Config**: `.env` (SOURCE_DB_* variables)

---

## 🆘 Troubleshooting

### Script fails with "Table not found"
- Ensure tables are created first
- Check database name (USE NewDQ)

### Truncate fails with FK error
- Disable foreign keys first (see Important Notes #3)

### Duplicate key errors
- Manually DELETE from tables first
- Then run seed script

### Slow execution
- Remove progress PRINT statements
- Increase batch size
- Check for indexes

---

## 📝 Maintenance

### To Update Seed Data

1. Edit `master_seed_data.sql`
2. Update version number in header
3. Test on dev environment
4. Document changes in docs/

### To Add New Materials

- Increase loop counters (WHILE @i <= 1000 → 2000)
- Maintain GPU/NBU split
- Update verification queries

---

**Last Updated**: 2025-11-08
**Current Version**: 2.0 (Master Seed Script)
