# IRR KPI - Quick Start Guide

## 🎯 What is IRR?

**Inactive Records Rate (IRR)** is a new KPI that measures the percentage of inactive records in your source database.

```
IRR = (Inactive Records / Total Records) × 100
```

**Why it matters:**
- Identifies stale/obsolete data
- Impacts reconciliation accuracy
- Indicates data quality issues
- Helps plan data maintenance

---

## 📊 Status Levels

```
IRR 0-5%    → EXCELLENT ✅ (Keep doing what you're doing)
IRR 5-10%   → GOOD ✅ (Monitor regularly)
IRR 10-20%  → WARNING ⚠️ (Review and archive inactive records)
IRR >20%    → CRITICAL 🔴 (Urgent action required)
```

---

## 🚀 How It Works

### Step 1: Execution
```
When you run reconciliation, the system:
1. Counts total records in source
2. Counts inactive records (is_active = 0 or NULL)
3. Calculates IRR percentage
4. Determines status
```

### Step 2: Calculation
```python
inactive_count = 50
total_count = 1000
irr = (50 / 1000) * 100  # = 5.0%
status = "EXCELLENT"      # Because 5% is in 0-5% range
```

### Step 3: Storage
```
Stored in MongoDB:
Collection: kpi_inactive_records_rate
Document includes:
- IRR percentage
- Status (EXCELLENT, GOOD, WARNING, CRITICAL)
- Interpretation
- Recommendation
```

---

## 📈 Example Output

### Console Output
```
📊 KPI Results:
  - RCR: 0.00%
  - DQCS: 0.750
  - REI: 0.00
  - IRR: 5.00% (Inactive Records Rate)
```

### Detailed Log
```
[OK] IRR: 5.00% - MongoDB ID: 507f1f77bcf86cd799439014
     Status: EXCELLENT
     Interpretation: Only 5.00% of records are inactive - excellent data quality
     Recommendation: Continue current data maintenance practices
```

---

## 🔍 MongoDB Query Examples

### Get Latest IRR
```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['reconciliation']
irr_collection = db['kpi_inactive_records_rate']

# Get latest IRR for a ruleset
latest = irr_collection.find_one(
    {"ruleset_id": "RECON_ABC123"},
    sort=[("timestamp", -1)]
)

print(f"IRR: {latest['metrics']['inactive_rate']}%")
print(f"Status: {latest['data_quality_assessment']['status']}")
```

### Get IRR Trend (Last 7 Days)
```python
from datetime import datetime, timedelta

seven_days_ago = datetime.utcnow() - timedelta(days=7)

trend = irr_collection.find({
    "ruleset_id": "RECON_ABC123",
    "timestamp": {"$gte": seven_days_ago}
}).sort("timestamp", 1)

for doc in trend:
    print(f"{doc['timestamp']}: {doc['metrics']['inactive_rate']}%")
```

### Find All Critical IRR Records
```python
critical = irr_collection.find({
    "data_quality_assessment.status": "CRITICAL"
})

for doc in critical:
    print(f"Ruleset: {doc['ruleset_name']}")
    print(f"IRR: {doc['metrics']['inactive_rate']}%")
    print(f"Action: {doc['data_quality_assessment']['recommendation']}")
```

---

## 📋 MongoDB Document Structure

```json
{
  "_id": ObjectId("..."),
  "kpi_type": "INACTIVE_RECORDS_RATE",
  "ruleset_id": "RECON_ABC123",
  "ruleset_name": "Reconciliation_Test",
  "execution_id": "EXEC_20251024_080446",
  "timestamp": ISODate("2025-10-24T08:04:46.000Z"),
  
  "metrics": {
    "total_records": 1000,
    "active_records": 950,
    "inactive_records": 50,
    "inactive_rate": 5.0,
    "inactive_percentage": 5.0,
    "active_percentage": 95.0
  },
  
  "data_quality_assessment": {
    "status": "EXCELLENT",
    "interpretation": "Only 5.00% of records are inactive - excellent data quality",
    "recommendation": "Continue current data maintenance practices"
  },
  
  "thresholds": {
    "excellent": 5,
    "good": 10,
    "warning": 20,
    "critical": 100,
    "current_status": "EXCELLENT"
  }
}
```

---

## 🔧 Python API Usage

### Calculate IRR
```python
from kg_builder.services.kpi_service import KPIService

kpi_service = KPIService()

# Calculate IRR
irr_doc = kpi_service.calculate_irr(
    total_source_count=1000,
    inactive_count=50,
    ruleset_id="RECON_ABC123",
    ruleset_name="Test Reconciliation",
    execution_id="EXEC_20251024_080446",
    source_kg="kg_20251024_005324",
    source_schemas=["orderMgmt-catalog", "qinspect-designcode"]
)

# Store in MongoDB
irr_id = kpi_service.store_kpi("INACTIVE_RECORDS_RATE", irr_doc)
print(f"Stored IRR with ID: {irr_id}")
```

### Retrieve Latest IRR
```python
# Get latest IRR for a ruleset
latest_irr = kpi_service.get_latest_kpi(
    "INACTIVE_RECORDS_RATE",
    "RECON_ABC123"
)

print(f"IRR: {latest_irr['metrics']['inactive_rate']}%")
print(f"Status: {latest_irr['data_quality_assessment']['status']}")
```

---

## 💡 Use Cases

### 1. Data Quality Monitoring
```
Track IRR over time to identify trends:
Week 1: 3% (EXCELLENT)
Week 2: 5% (EXCELLENT)
Week 3: 12% (WARNING) ← Alert!
```

### 2. Reconciliation Planning
```
Understand active vs inactive records:
Total: 1000
Active: 850 (85%)
Inactive: 150 (15%)
→ Reconciliation covers 85% of data
```

### 3. SLA Compliance
```
Define SLA: IRR must be < 10%
Current: 8% ✅ PASS
```

### 4. Data Maintenance
```
IRR > 20% → Schedule data cleanup
IRR > 30% → Urgent action required
```

---

## 🎯 Best Practices

✅ **Do:**
- Monitor IRR daily/weekly
- Set up alerts for IRR > 15%
- Archive inactive records regularly
- Document reasons for inactive records
- Track IRR trends

❌ **Don't:**
- Ignore high IRR values
- Delete inactive records without backup
- Assume all inactive = stale
- Skip IRR monitoring

---

## 📚 Related Documentation

- `INACTIVE_RECORDS_RATE_KPI.md` - Complete IRR guide
- `IRR_KPI_IMPLEMENTATION_SUMMARY.md` - Technical details
- `MONGODB_DATA_STRUCTURE.md` - MongoDB collections
- `test_e2e_reconciliation_simple.py` - Test implementation

---

## 🔗 Files Modified

1. `kg_builder/services/kpi_service.py` - Added IRR calculation
2. `kg_builder/services/reconciliation_executor.py` - Added inactive count
3. `kg_builder/models.py` - Added inactive_count field
4. `test_e2e_reconciliation_simple.py` - Added IRR to test

---

## ✨ Key Features

✅ Automatic detection during execution
✅ Clear status levels (EXCELLENT, GOOD, WARNING, CRITICAL)
✅ Actionable recommendations
✅ MongoDB persistence
✅ Database agnostic (MySQL, Oracle, PostgreSQL, SQL Server)
✅ Graceful error handling
✅ Detailed logging

---

**Version**: 1.0  
**Date**: 2025-10-24  
**Status**: ✅ Complete & Tested

