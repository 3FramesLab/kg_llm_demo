# KPI (Key Performance Indicator) Feature - Complete Guide ✅

## 🎯 Overview

The KPI feature enables users to create, calculate, and monitor Key Performance Indicators based on reconciliation results. KPIs are stored as JSON files (no MongoDB dependency) with full drill-down capability to view evidence records.

---

## ✨ Features

✅ **KPI Creation** - Create custom KPIs via web app or API
✅ **Multiple KPI Types** - Match rate, unmatched counts, data quality score, etc.
✅ **Threshold Configuration** - Set warning and critical thresholds
✅ **File-Based Storage** - JSON files in `kpi_results/` and `kpi_evidence/` folders
✅ **Evidence Drill-Down** - View detailed records that contributed to KPI calculation
✅ **Status Tracking** - Pass, Warning, or Critical status based on thresholds
✅ **Pagination Support** - Retrieve evidence records with limit/offset
✅ **Comprehensive Logging** - All KPI operations logged for debugging

---

## 📊 KPI Types

| Type | Description | Formula | Example |
|------|-------------|---------|---------|
| **match_rate** | Percentage of matched records | (matched / total) * 100 | 85% |
| **match_percentage** | Same as match_rate | (matched / total) * 100 | 85% |
| **unmatched_source_count** | Count of unmatched source records | unmatched_source | 150 |
| **unmatched_target_count** | Count of unmatched target records | unmatched_target | 200 |
| **inactive_record_count** | Count of inactive records | inactive_count | 50 |
| **data_quality_score** | Overall data quality | ((matched + (total - unmatched_source)) / total) * 100 | 90% |

---

## 🗂️ File Structure

### KPI Configuration Files
```
kpi_configs/
├── kpi_config_KPI_ABC123.json
├── kpi_config_KPI_DEF456.json
└── ...
```

### KPI Result Files
```
kpi_results/
├── kpi_result_KPI_ABC123_20251026_143022.json
├── kpi_result_KPI_ABC123_20251026_150145.json
└── ...
```

### KPI Evidence Files
```
kpi_evidence/
├── kpi_evidence_KPI_ABC123_20251026_143022.json
├── kpi_evidence_KPI_ABC123_20251026_150145.json
└── ...
```

---

## 📝 Data Models

### KPI Configuration
```json
{
  "kpi_id": "KPI_ABC123",
  "kpi_name": "Material Match Rate",
  "kpi_description": "Percentage of materials matched between source and target",
  "kpi_type": "match_rate",
  "ruleset_id": "RECON_ABC123",
  "thresholds": {
    "warning_threshold": 80.0,
    "critical_threshold": 70.0,
    "comparison_operator": "less_than"
  },
  "enabled": true,
  "created_at": "2025-10-26T14:30:22.123456",
  "updated_at": "2025-10-26T14:30:22.123456"
}
```

### KPI Result
```json
{
  "kpi_id": "KPI_ABC123",
  "kpi_name": "Material Match Rate",
  "kpi_type": "match_rate",
  "ruleset_id": "RECON_ABC123",
  "calculated_value": 85.5,
  "thresholds": {
    "warning_threshold": 80.0,
    "critical_threshold": 70.0,
    "comparison_operator": "less_than"
  },
  "status": "pass",
  "execution_timestamp": "2025-10-26T14:30:22.123456",
  "evidence_count": 1000,
  "evidence_file_path": "kpi_evidence/kpi_evidence_KPI_ABC123_20251026_143022.json",
  "calculation_details": {
    "matched_count": 855,
    "total_source_count": 1000,
    "formula": "(matched_count / total_source_count) * 100"
  }
}
```

### Evidence Record
```json
{
  "record_id": "MAT_001",
  "record_data": {
    "material_id": "MAT_001",
    "name": "Steel Plate",
    "category": "Raw Material",
    "quantity": 100,
    "unit": "kg"
  },
  "match_status": "matched",
  "rule_name": "Material_Name_Match"
}
```

---

## 🚀 API Endpoints

### 1. Create KPI
```
POST /v1/reconciliation/kpi/create
```

**Request:**
```json
{
  "kpi_name": "Material Match Rate",
  "kpi_description": "Percentage of materials matched",
  "kpi_type": "match_rate",
  "ruleset_id": "RECON_ABC123",
  "thresholds": {
    "warning_threshold": 80.0,
    "critical_threshold": 70.0,
    "comparison_operator": "less_than"
  },
  "enabled": true
}
```

**Response:**
```json
{
  "success": true,
  "result_file_path": "kpi_configs/kpi_config_KPI_ABC123.json"
}
```

### 2. List KPIs
```
GET /v1/reconciliation/kpi/list?ruleset_id=RECON_ABC123
```

**Response:**
```json
{
  "success": true,
  "count": 2,
  "kpis": [
    { "kpi_id": "KPI_ABC123", "kpi_name": "Material Match Rate", ... },
    { "kpi_id": "KPI_DEF456", "kpi_name": "Data Quality Score", ... }
  ]
}
```

### 3. Get KPI
```
GET /v1/reconciliation/kpi/{kpi_id}
```

**Response:**
```json
{
  "success": true,
  "kpi": { "kpi_id": "KPI_ABC123", ... }
}
```

### 4. Get Evidence (Drill-Down)
```
POST /v1/reconciliation/kpi/{kpi_id}/evidence
```

**Request:**
```json
{
  "kpi_id": "KPI_ABC123",
  "match_status": "unmatched_source",
  "limit": 100,
  "offset": 0
}
```

**Response:**
```json
{
  "success": true,
  "kpi_id": "KPI_ABC123",
  "kpi_name": "Material Match Rate",
  "total_evidence_count": 150,
  "returned_count": 100,
  "evidence_records": [
    {
      "record_id": "MAT_001",
      "record_data": { ... },
      "match_status": "unmatched_source",
      "rule_name": "Material_Name_Match"
    }
  ]
}
```

---

## 🎨 Web App Pages

### KPI Management Page
**Location:** `web-app/src/pages/KPIManagement.js`

**Features:**
- Create new KPIs with form validation
- List all KPIs with filtering by ruleset
- Edit and delete KPIs
- View KPI configuration details

### KPI Results Page
**Location:** `web-app/src/pages/KPIResults.js`

**Features:**
- View all KPI results
- Display KPI status (pass/warning/critical)
- Drill-down into evidence records
- Filter evidence by match status
- Pagination support for large datasets
- Export evidence data

---

## 🔧 Backend Implementation

### KPI Executor Service
**Location:** `kg_builder/services/kpi_executor.py`

**Key Methods:**
- `create_kpi()` - Create new KPI configuration
- `calculate_kpi()` - Calculate KPI value based on reconciliation results
- `store_kpi_result()` - Store KPI result and evidence to files
- `load_kpi_config()` - Load KPI configuration from file
- `list_kpi_configs()` - List all KPI configurations

### Data Models
**Location:** `kg_builder/models.py`

**Models:**
- `KPIType` - Enum of KPI types
- `KPIThresholds` - Threshold configuration
- `KPICreateRequest` - Request to create KPI
- `KPIConfiguration` - Stored KPI configuration
- `KPIResult` - KPI calculation result
- `KPIEvidenceRecord` - Evidence record for drill-down
- `KPIEvidenceDrillDownRequest` - Request for evidence
- `KPIEvidenceDrillDownResponse` - Response with evidence

### API Routes
**Location:** `kg_builder/routes.py`

**Endpoints:**
- `POST /v1/reconciliation/kpi/create` - Create KPI
- `GET /v1/reconciliation/kpi/list` - List KPIs
- `GET /v1/reconciliation/kpi/{kpi_id}` - Get KPI
- `POST /v1/reconciliation/kpi/{kpi_id}/evidence` - Get evidence

---

## 📊 Threshold Configuration

### Comparison Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| **less_than** | Value < threshold | Match rate < 80% = warning |
| **greater_than** | Value > threshold | Unmatched count > 100 = warning |
| **equal_to** | Value = threshold | Inactive count = 50 = warning |

### Status Determination

```
if operator == "less_than":
  if value < critical_threshold → "critical"
  elif value < warning_threshold → "warning"
  else → "pass"

if operator == "greater_than":
  if value > critical_threshold → "critical"
  elif value > warning_threshold → "warning"
  else → "pass"
```

---

## 💾 File-Based Storage

### Directory Structure
```
project_root/
├── kpi_configs/          # KPI configurations
├── kpi_results/          # KPI calculation results
├── kpi_evidence/         # Evidence records for drill-down
└── ...
```

### Automatic Directory Creation
Directories are automatically created on first use by `KPIExecutor._ensure_directories()`

### File Naming Convention
- **Config:** `kpi_config_{kpi_id}.json`
- **Result:** `kpi_result_{kpi_id}_{timestamp}.json`
- **Evidence:** `kpi_evidence_{kpi_id}_{timestamp}.json`

---

## 🧪 Usage Examples

### Example 1: Create a Match Rate KPI
```python
from kg_builder.services.kpi_executor import get_kpi_executor
from kg_builder.models import KPICreateRequest, KPIThresholds

executor = get_kpi_executor()

request = KPICreateRequest(
    kpi_name="Material Match Rate",
    kpi_description="Percentage of materials matched",
    kpi_type="match_rate",
    ruleset_id="RECON_ABC123",
    thresholds=KPIThresholds(
        warning_threshold=80.0,
        critical_threshold=70.0,
        comparison_operator="less_than"
    ),
    enabled=True
)

config, config_file = executor.create_kpi(request)
print(f"Created KPI: {config.kpi_id}")
```

### Example 2: Calculate KPI
```python
kpi_config = executor.load_kpi_config("KPI_ABC123")

result = executor.calculate_kpi(
    kpi_config=kpi_config,
    matched_count=850,
    unmatched_source_count=100,
    unmatched_target_count=50,
    total_source_count=1000,
    inactive_count=10
)

print(f"KPI Value: {result.calculated_value}")
print(f"Status: {result.status}")
```

### Example 3: Store KPI Result with Evidence
```python
evidence_records = [
    KPIEvidenceRecord(
        record_id="MAT_001",
        record_data={"material_id": "MAT_001", "name": "Steel"},
        match_status="matched",
        rule_name="Material_Name_Match"
    ),
    # ... more records
]

result_file, evidence_file = executor.store_kpi_result(
    kpi_result=result,
    evidence_records=evidence_records
)

print(f"Result stored: {result_file}")
print(f"Evidence stored: {evidence_file}")
```

---

## 📚 Related Documentation

- **Reconciliation Execution**: `RECONCILIATION_EXECUTION_GUIDE.md`
- **File-Based Storage**: `RECONCILIATION_FILE_BASED_STORAGE.md`
- **SQL Query Logging**: `SQL_QUERY_LOGGING_GUIDE.md`

---

## 🎉 Summary

✅ **KPI Creation** - Create custom KPIs via web app or API
✅ **Multiple Types** - 6 different KPI types supported
✅ **File-Based Storage** - No MongoDB dependency
✅ **Evidence Drill-Down** - View detailed records
✅ **Threshold Alerts** - Pass/Warning/Critical status
✅ **Production Ready** - Fully tested and documented

The KPI feature is now ready for production use!


