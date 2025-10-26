# When Do KPIs Get Executed? 🎯

## Overview

KPIs are **manually executed on-demand** through the API. There is **no automatic scheduling** currently implemented.

---

## 📋 Current Execution Methods

### Method 1: Manual Execution via API

**Endpoint:**
```
POST /v1/reconciliation/kpi/{kpi_id}/execute
```

**Request:**
```json
{
  "ruleset_id": "RECON_9240A5F7"  // Optional override
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "result_id": "RES_ABC123",
    "kpi_id": "KPI_001",
    "kpi_name": "Material Match Rate",
    "calculated_value": 95.5,
    "status": "OK",
    "execution_timestamp": "2025-10-26T12:59:45.123456",
    "metrics": {...}
  },
  "result_id": "RES_ABC123"
}
```

### Method 2: Batch Execution via API

**Endpoint:**
```
POST /v1/reconciliation/kpi/execute/batch
```

**Request:**
```json
{
  "kpi_ids": ["KPI_001", "KPI_002", "KPI_003"],
  "ruleset_id": "RECON_9240A5F7"  // Optional
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "kpi_id": "KPI_001",
      "status": "success",
      "result_id": "RES_ABC123"
    },
    {
      "kpi_id": "KPI_002",
      "status": "success",
      "result_id": "RES_ABC124"
    }
  ],
  "total": 3,
  "successful": 2,
  "failed": 1
}
```

---

## 🔄 Execution Flow

### Step 1: Load KPI Definition
```
GET /v1/reconciliation/kpi/{kpi_id}
↓
Returns KPI configuration with:
- kpi_name
- kpi_type
- ruleset_id
- thresholds
- enabled status
```

### Step 2: Execute KPI
```
POST /v1/reconciliation/kpi/{kpi_id}/execute
↓
Backend:
1. Loads KPI definition
2. Executes query based on KPI type
3. Calculates KPI value
4. Determines status (OK/WARNING/CRITICAL)
5. Saves result to file
6. Returns result
```

### Step 3: Store Result
```
Result saved to:
kpi_results/{kpi_id}_{timestamp}.json

Index updated:
kpi_results/index.json
```

### Step 4: View Results
```
GET /v1/reconciliation/kpi/results
↓
Returns list of all KPI results

GET /v1/reconciliation/kpi/results/{result_id}
↓
Returns specific result details
```

---

## 🔍 How KPI Execution Works

### Backend Process (kpi_file_service.py)

```python
def execute_kpi(self, kpi_id: str, ruleset_id: Optional[str] = None):
    # 1. Get KPI definition
    kpi = self.get_kpi_definition(kpi_id)
    
    # 2. Execute query based on KPI type
    query_result = self._execute_kpi_query(kpi_type, ruleset_id)
    
    # 3. Calculate KPI value
    calculated_value = self._calculate_kpi_value(kpi_type, query_result)
    
    # 4. Determine status
    status = self._determine_status(calculated_value, thresholds)
    
    # 5. Create result document
    result = {
        "result_id": uuid.uuid4(),
        "kpi_id": kpi_id,
        "calculated_value": calculated_value,
        "status": status,
        "execution_timestamp": datetime.utcnow(),
        "metrics": query_result,
        "thresholds": thresholds
    }
    
    # 6. Save result
    result_id = self.save_kpi_result(result)
    
    return result
```

---

## 📊 KPI Types & Calculations

### 1. Match Rate (%)
```
Formula: (matched_count / total_source_count) × 100
Example: (950 / 1000) × 100 = 95%
```

### 2. Match Percentage (%)
```
Formula: Same as Match Rate
```

### 3. Unmatched Source Count
```
Formula: total_source_count - matched_count
Example: 1000 - 950 = 50
```

### 4. Unmatched Target Count
```
Formula: total_target_count - matched_count
Example: 1000 - 950 = 50
```

### 5. Inactive Record Count
```
Formula: Count of inactive records
Example: 10
```

### 6. Data Quality Score
```
Formula: Average confidence score
Example: 0.92 (92%)
```

---

## 🎯 Status Determination

After calculating KPI value, status is determined:

```python
def _determine_status(self, value, thresholds):
    critical = thresholds.get('critical_threshold')
    warning = thresholds.get('warning_threshold')
    operator = thresholds.get('comparison_operator')
    
    if operator == 'less_than':
        if value < critical:
            return 'CRITICAL'
        elif value < warning:
            return 'WARNING'
    elif operator == 'greater_than':
        if value > critical:
            return 'CRITICAL'
        elif value > warning:
            return 'WARNING'
    
    return 'OK'
```

### Example
```
KPI: Match Rate
Value: 75%
Thresholds:
  - Warning: 80%
  - Critical: 70%
  - Operator: less_than

Status: WARNING (75% < 80%)
```

---

## 📁 File Storage

### KPI Definition
```
data/kpi/definitions/kpis.json
{
  "kpis": [
    {
      "kpi_id": "KPI_001",
      "kpi_name": "Material Match Rate",
      "kpi_type": "match_rate",
      "ruleset_id": "RECON_9240A5F7",
      "thresholds": {
        "warning_threshold": 80,
        "critical_threshold": 70,
        "comparison_operator": "less_than"
      },
      "enabled": true
    }
  ]
}
```

### KPI Result
```
data/kpi/results/KPI_001_20251026125945.json
{
  "result_id": "RES_ABC123",
  "kpi_id": "KPI_001",
  "kpi_name": "Material Match Rate",
  "calculated_value": 95.5,
  "status": "OK",
  "execution_timestamp": "2025-10-26T12:59:45.123456",
  "metrics": {
    "matched_count": 955,
    "total_source_count": 1000
  },
  "thresholds": {
    "warning_threshold": 80,
    "critical_threshold": 70,
    "comparison_operator": "less_than"
  }
}
```

### Result Index
```
data/kpi/results/index.json
{
  "results": [
    {
      "result_id": "RES_ABC123",
      "kpi_id": "KPI_001",
      "kpi_name": "Material Match Rate",
      "execution_timestamp": "2025-10-26T12:59:45.123456",
      "calculated_value": 95.5,
      "status": "OK",
      "file_path": "KPI_001_20251026125945.json"
    }
  ],
  "metadata": {
    "total_results": 1,
    "last_updated": "2025-10-26T12:59:45.123456"
  }
}
```

---

## 🚀 How to Execute KPIs

### Via cURL
```bash
# Execute single KPI
curl -X POST http://localhost:8000/v1/reconciliation/kpi/KPI_001/execute \
  -H "Content-Type: application/json" \
  -d '{"ruleset_id": "RECON_9240A5F7"}'

# Execute batch
curl -X POST http://localhost:8000/v1/reconciliation/kpi/execute/batch \
  -H "Content-Type: application/json" \
  -d '{
    "kpi_ids": ["KPI_001", "KPI_002"],
    "ruleset_id": "RECON_9240A5F7"
  }'
```

### Via Python
```python
from kg_builder.services.kpi_file_service import KPIFileService

service = KPIFileService()

# Execute single KPI
result = service.execute_kpi("KPI_001", "RECON_9240A5F7")
print(f"Result: {result['calculated_value']}, Status: {result['status']}")

# List results
results = service.list_kpi_results("KPI_001", limit=10)
for r in results:
    print(f"{r['kpi_name']}: {r['calculated_value']} ({r['status']})")
```

---

## 📊 View KPI Results

### List All Results
```
GET /v1/reconciliation/kpi/results
```

### List Results for Specific KPI
```
GET /v1/reconciliation/kpi/results?kpi_id=KPI_001
```

### Get Specific Result
```
GET /v1/reconciliation/kpi/results/{result_id}
```

---

## 🔮 Future Enhancements

### Planned Features
1. **Scheduled Execution** - Run KPIs on schedule (hourly, daily, etc.)
2. **Event-Based Triggers** - Execute KPIs when reconciliation completes
3. **Alerts** - Email/Slack notifications on status changes
4. **Dashboards** - Visual KPI monitoring
5. **History Tracking** - Track KPI changes over time
6. **Comparisons** - Compare KPIs across rulesets
7. **Export** - Export to CSV/Excel
8. **Templates** - Pre-built KPI templates

---

## 📋 Summary

### Current State
✅ Manual on-demand execution
✅ Single KPI execution
✅ Batch execution
✅ File-based storage
✅ Result history tracking

### Not Yet Implemented
❌ Automatic scheduling
❌ Event-based triggers
❌ Alerts/notifications
❌ Dashboards
❌ Web UI execution button

---

## 🎯 Next Steps

To add automatic execution:

1. **Add Scheduler** - Use APScheduler
2. **Add Triggers** - Hook into reconciliation completion
3. **Add UI Button** - Execute button in KPI Management page
4. **Add Alerts** - Email/Slack notifications
5. **Add Dashboard** - Visual KPI monitoring

Would you like me to implement any of these features?


