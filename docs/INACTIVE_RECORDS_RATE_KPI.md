# Inactive Records Rate (IRR) KPI - Complete Guide

## 🎯 Overview

The **Inactive Records Rate (IRR)** is a new KPI that tracks the percentage of inactive records in the source database. This helps identify data quality issues and stale records that may impact reconciliation accuracy.

**Formula:**
```
IRR = (Inactive Records / Total Source Records) × 100
```

Where:
- **Inactive Records** = Records where `is_active = 0` or `is_active IS NULL`
- **Total Source Records** = Total number of records in the source table

---

## 📊 Status Levels

| Status | IRR Range | Interpretation | Action |
|--------|-----------|-----------------|--------|
| **EXCELLENT** | 0-5% | Very few inactive records | Continue current practices |
| **GOOD** | 5-10% | Acceptable level | Monitor regularly |
| **WARNING** | 10-20% | Moderate level | Review and archive inactive records |
| **CRITICAL** | >20% | High level | Urgent action required |

---

## 🔍 How It Works

### 1. Data Collection
```sql
SELECT COUNT(*) as inactive_count
FROM `ordermgmt`.`catalog`
WHERE `is_active` = 0 OR `is_active` IS NULL
```

### 2. Calculation
```python
inactive_rate = (inactive_count / total_source_count) * 100
```

### 3. Status Determination
```python
if inactive_rate <= 5:
    status = "EXCELLENT"
elif inactive_rate <= 10:
    status = "GOOD"
elif inactive_rate <= 20:
    status = "WARNING"
else:
    status = "CRITICAL"
```

---

## 📋 MongoDB Document Structure

### Collection Name
```
kpi_inactive_records_rate
```

### Document Example
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439014"),
  "kpi_type": "INACTIVE_RECORDS_RATE",
  "ruleset_id": "RECON_ABC123",
  "ruleset_name": "Reconciliation_Test",
  "execution_id": "EXEC_20251024_080446",
  "timestamp": ISODate("2025-10-24T08:04:46.000Z"),
  "period": "execution",
  "metrics": {
    "total_records": 100,
    "active_records": 95,
    "inactive_records": 5,
    "inactive_rate": 5.0,
    "inactive_percentage": 5.0,
    "active_percentage": 95.0
  },
  "breakdown_by_status": [],
  "thresholds": {
    "excellent": 5,
    "good": 10,
    "warning": 20,
    "critical": 100,
    "current_status": "EXCELLENT"
  },
  "data_quality_assessment": {
    "status": "EXCELLENT",
    "interpretation": "Only 5.00% of records are inactive - excellent data quality",
    "recommendation": "Continue current data maintenance practices"
  },
  "data_lineage": {
    "source_kg": "kg_20251024_005324",
    "source_schemas": ["orderMgmt-catalog", "qinspect-designcode"],
    "generated_from_kg": "kg_20251024_005324"
  },
  "created_at": ISODate("2025-10-24T08:04:46.000Z"),
  "updated_at": ISODate("2025-10-24T08:04:46.000Z")
}
```

---

## 🔧 Implementation Details

### Files Modified

#### 1. `kg_builder/services/kpi_service.py`
- Added `calculate_irr()` method
- Added `_interpret_irr_status()` helper method
- Added `_get_irr_recommendation()` helper method
- Updated `_get_collection_name()` to include IRR mapping
- Added IRR collection index creation

#### 2. `kg_builder/services/reconciliation_executor.py`
- Added `_count_inactive_records()` method
- Updated `execute_ruleset()` to count inactive records
- Added `inactive_count` to response data

#### 3. `kg_builder/models.py`
- Added `inactive_count` field to `RuleExecutionResponse`

#### 4. `test_e2e_reconciliation_simple.py`
- Updated `calculate_kpis()` to calculate and store IRR
- Updated summary output to display IRR

---

## 📈 Example Output

### Console Output
```
📊 KPI Results:
  - RCR: 0.00%
  - DQCS: 0.750
  - REI: 0.00
  - IRR: 5.00% (Inactive Records Rate)
  - Calculation Method: Python In-Memory
```

### Detailed Logging
```
[OK] IRR: 5.00% - MongoDB ID: 507f1f77bcf86cd799439014
     Status: EXCELLENT
     Interpretation: Only 5.00% of records are inactive - excellent data quality
```

---

## 🎯 Use Cases

### 1. Data Quality Monitoring
Track inactive records over time to identify data quality trends:
```
Week 1: IRR = 3% (EXCELLENT)
Week 2: IRR = 5% (EXCELLENT)
Week 3: IRR = 12% (WARNING) ← Alert!
```

### 2. Reconciliation Accuracy
Understand how many records are excluded from reconciliation:
```
Total Records: 1000
Inactive Records: 150 (15%)
Active Records: 850 (85%)
Reconciliation Coverage: 85% of total
```

### 3. Data Maintenance Planning
Identify when data cleanup is needed:
```
IRR > 20% → Schedule data archival
IRR > 30% → Urgent data cleanup required
```

### 4. SLA Monitoring
Define SLAs based on inactive record rates:
```
SLA: IRR must be < 10%
Current: IRR = 8% ✅ PASS
```

---

## 🔍 Query Examples

### Get Latest IRR for a Ruleset
```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['reconciliation']
collection = db['kpi_inactive_records_rate']

# Get latest IRR
latest_irr = collection.find_one(
    {"ruleset_id": "RECON_ABC123"},
    sort=[("timestamp", -1)]
)

print(f"IRR: {latest_irr['metrics']['inactive_rate']}%")
print(f"Status: {latest_irr['data_quality_assessment']['status']}")
```

### Get IRR Trend Over Time
```python
# Get last 7 days of IRR data
from datetime import datetime, timedelta

seven_days_ago = datetime.utcnow() - timedelta(days=7)

irr_trend = collection.find({
    "ruleset_id": "RECON_ABC123",
    "timestamp": {"$gte": seven_days_ago}
}).sort("timestamp", 1)

for doc in irr_trend:
    print(f"{doc['timestamp']}: {doc['metrics']['inactive_rate']}%")
```

### Get All Critical IRR Records
```python
# Find all executions with critical IRR
critical_irr = collection.find({
    "data_quality_assessment.status": "CRITICAL"
})

for doc in critical_irr:
    print(f"Ruleset: {doc['ruleset_name']}")
    print(f"IRR: {doc['metrics']['inactive_rate']}%")
    print(f"Recommendation: {doc['data_quality_assessment']['recommendation']}")
```

---

## 📊 Metrics Breakdown

### Metrics Object
```json
{
  "total_records": 1000,           // Total records in source
  "active_records": 850,           // Records with is_active = 1
  "inactive_records": 150,         // Records with is_active = 0 or NULL
  "inactive_rate": 15.0,           // Percentage (0-100)
  "inactive_percentage": 15.0,     // Same as inactive_rate
  "active_percentage": 85.0        // 100 - inactive_percentage
}
```

---

## 🚀 Integration with Other KPIs

### RCR (Reconciliation Coverage Rate)
```
RCR considers only active records:
RCR = (Matched Active Records / Total Active Records) × 100
```

### DQCS (Data Quality Confidence Score)
```
DQCS is calculated from matched records:
High IRR → Fewer records to match → Lower DQCS
```

### REI (Reconciliation Efficiency Index)
```
REI considers active records for efficiency:
High IRR → Lower efficiency (more inactive records to skip)
```

---

## 💡 Best Practices

✅ **Do:**
- Monitor IRR regularly (daily/weekly)
- Set up alerts for IRR > 15%
- Archive inactive records periodically
- Document reasons for inactive records
- Track IRR trends over time

❌ **Don't:**
- Ignore high IRR values
- Delete inactive records without backup
- Assume all inactive records are stale
- Skip IRR monitoring

---

## 🔗 Related Documentation

- `MONGODB_DATA_STRUCTURE.md` - MongoDB collections overview
- `KPI_EXECUTION_FLOW.md` - KPI calculation workflow
- `test_e2e_reconciliation_simple.py` - Test implementation

---

**Version**: 1.0  
**Date**: 2025-10-24  
**Status**: ✅ Complete

