# Seed Data Documentation - 500 Items (GPU & NBU)

## 🎯 Overview

This seed data script generates **500 comprehensive test records** across all 8 tables in the `newdqschemanov.json` schema, with **250 GPU products** and **250 NBU products**.

## 📊 Data Distribution

### Product Types
- **GPU (Graphics Processing Unit)**: 250 items
  - Material IDs: `GPU-001` to `GPU-250`
  - Business Unit: `GPUBU`
  - Product Lines: `RTXGP`, `GTXGP`, `QUADR`, `TESLA`

- **NBU (Network Business Unit)**: 250 items
  - Material IDs: `NBU-001` to `NBU-250`
  - Business Unit: `NBUBU`
  - Product Lines: `DRIVE`, `JETSO`, `ORIN`

## 🗂️ Table Structure & Relationships

### 1. **hana_material_master** (Master Data - 500 records)
**Purpose**: Central material master data
**Key Fields**:
- `MATERIAL`: Primary identifier (GPU-001 to GPU-250, NBU-001 to NBU-250)
- `Product Type`: GPU or NBU
- `Business Unit`: GPUBU or NBUBU
- `Product Line`: Various product families
- `OPS_MKTG_NM`: Marketing names (GeForce RTX series, Jetson series)
- `OPS_STATUS`: ACTIVE, PHASE_OUT, DISCONTINUED

### 2. **brz_lnd_RBP_GPU** (Revenue Business Planning - 250 GPU records)
**Purpose**: GPU revenue and business planning data
**Key Fields**:
- `Material`: References `hana_material_master.MATERIAL`
- `Product_Line`: RTX Graphics, GTX Graphics, Quadro Professional, Tesla Compute
- `Product_Family`: RTX40_SERIES, RTX30_SERIES, GTX16_SERIES, etc.
- `Business_Unit`: GPU_BUSINESS
- `Overall_Result`: Performance indicators

### 3. **brz_lnd_OPS_EXCEL_GPU** (Operations Excel - 250 GPU records)
**Purpose**: GPU operational planning data
**Key Fields**:
- `PLANNING_SKU`: Matches `hana_material_master.MATERIAL`
- `Customer`: ASUS, MSI, EVGA, GIGABYTE, etc.
- `Active_Inactive`: Based on material status
- `CHIP_Family`: Ada Lovelace, Turing, Ampere, Hopper
- `Level_2_usage`: Gaming, Professional, Data Center, AI/ML

### 4. **brz_lnd_SKU_LIFNR_Excel** (SKU Supplier - 500 records)
**Purpose**: Supplier and procurement data for all materials
**Key Fields**:
- `Material`: References `hana_material_master.MATERIAL`
- `Supplier`: SUP001-SUP010 (TSMC, Samsung, SK Hynix, etc.)
- `Lead_Time_Days`: 45-75 days for GPU, 30-50 days for NBU
- `Unit_Cost`: $150-650 for GPU, $80-280 for NBU
- `Purchasing_group`: PG001-PG005

### 5. **brz_lnd_IBP_Product_Master** (IBP Product Master - 500 records)
**Purpose**: Integrated Business Planning product hierarchy
**Key Fields**:
- `PRDID`: Product ID (PRD_GPU-001, PRD_NBU-001, etc.)
- `ZBASEMATERIAL`: References `hana_material_master.MATERIAL`
- `ZBOM1-ZBOM5`: Bill of Materials components
- `ZBOM1TXT-ZBOM5TXT`: BOM component descriptions

### 6. **brz_lnd_SAR_Excel_GPU** (SAR Excel GPU - 250 GPU records)
**Purpose**: GPU performance analysis data
**Key Fields**:
- `Material`: References `hana_material_master.MATERIAL` (GPU only)
- `Fiscal_Year_Period`: 2024.01 to 2024.12
- `Overall_Result`: Performance ratings

### 7. **brz_lnd_GPU_SKU_IN_SKULIFNR** (GPU SKU Mapping - 250 GPU records)
**Purpose**: GPU SKU to supplier mapping
**Key Fields**:
- `PLANNING_SKU`: Matches GPU materials
- `Material`: References `hana_material_master.MATERIAL`

### 8. **brz_lnd_SAR_Excel_NBU** (SAR Excel NBU - 250 NBU records)
**Purpose**: NBU performance analysis data
**Key Fields**:
- `Material`: References `hana_material_master.MATERIAL` (NBU only)
- `Fiscal_Year_Period`: 2024.01 to 2024.12
- `Overall_Result`: Performance ratings

## 🔗 Key Relationships

### **Primary Relationships**:
1. **`hana_material_master.MATERIAL`** ↔ **All other tables' Material fields**
   - Central hub for all material references
   - Enables cross-table joins and reconciliation

2. **`brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU`** ↔ **`hana_material_master.MATERIAL`**
   - Planning SKU references material master

3. **`brz_lnd_IBP_Product_Master.ZBASEMATERIAL`** ↔ **`hana_material_master.MATERIAL`**
   - Product hierarchy to material mapping

### **Business Logic Relationships**:
- **GPU products** appear in: RBP_GPU, OPS_EXCEL_GPU, SAR_Excel_GPU, GPU_SKU_IN_SKULIFNR
- **NBU products** appear in: SAR_Excel_NBU
- **All products** appear in: hana_material_master, SKU_LIFNR_Excel, IBP_Product_Master

## 🎲 Data Patterns & Variations

### **Realistic Variations**:
- **Status Distribution**: 80% Active, 10% Phase Out, 10% Discontinued
- **Multiple Plants**: P001, P002, P003, P004
- **Diverse Suppliers**: 10 different suppliers with realistic names
- **Cost Variations**: GPU ($150-650), NBU ($80-280)
- **Lead Time Variations**: GPU (45-75 days), NBU (30-50 days)
- **Performance Ratings**: 6 different performance levels

### **Consistent Relationships**:
- All material IDs are consistently referenced across tables
- Product types are maintained across all related tables
- Business units align with product types
- Fiscal periods span full year (2024.01-2024.12)

## 🚀 Usage Instructions

### **1. Execute the Script**:
```sql
-- Run in SQL Server Management Studio or similar tool
-- Make sure you have the target database selected
-- Script includes transaction safety and validation
```

### **2. Validation Queries**:
The script includes built-in validation queries that show:
- Record counts per table
- Product type distribution
- Sample data preview
- Relationship integrity checks

### **3. Testing Scenarios**:
Perfect for testing:
- **Knowledge Graph Generation**: Rich relationships between tables
- **Reconciliation Rules**: Multiple matching patterns
- **Cross-Schema Analysis**: GPU vs NBU business patterns
- **LLM Relationship Detection**: Semantic and structural relationships

## 📈 Business Scenarios Supported

### **GPU Business Scenarios**:
- Graphics card product planning and forecasting
- Customer allocation (ASUS, MSI, EVGA, etc.)
- Performance tracking across product families
- Supply chain management with semiconductor suppliers

### **NBU Business Scenarios**:
- Network processing unit development
- Edge computing and IoT applications
- Automotive and embedded systems (Drive, Jetson, Orin)
- Performance analysis and optimization

### **Cross-Business Scenarios**:
- Unified material master management
- Shared supplier relationships
- Integrated business planning
- Comparative performance analysis

## 🎯 Perfect for Testing

This seed data is specifically designed to test:
- ✅ **Relationship Detection**: Multiple relationship types
- ✅ **Data Reconciliation**: Consistent material references
- ✅ **LLM Analysis**: Rich semantic patterns
- ✅ **Cross-Table Joins**: Complex multi-table scenarios
- ✅ **Business Intelligence**: Realistic business patterns
- ✅ **Performance Testing**: 500 records with realistic complexity

## 🔧 Customization Options

### **Scale Up**:
- Modify the CTE to generate more records
- Adjust the ROW_NUMBER() ranges for larger datasets

### **Add Variations**:
- Extend product lines and families
- Add more suppliers and customers
- Include additional fiscal periods
- Expand BOM components

### **Business Rules**:
- Modify status distributions
- Adjust cost ranges
- Change lead time patterns
- Update performance criteria

This seed data provides a comprehensive, realistic foundation for testing all aspects of your knowledge graph and reconciliation system!
