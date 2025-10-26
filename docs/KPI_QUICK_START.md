# KPI Feature - Quick Start Guide ✅

## 🚀 Getting Started in 5 Minutes

### Step 1: Create a KPI via Web App

1. Navigate to **KPI Management** page
2. Click **Create KPI** button
3. Fill in the form:
   - **KPI Name:** "Material Match Rate"
   - **Description:** "Percentage of materials matched"
   - **Type:** "Match Rate (%)"
   - **Ruleset:** Select your ruleset
   - **Warning Threshold:** 80
   - **Critical Threshold:** 70
   - **Operator:** "Less Than"
4. Click **Create**

### Step 2: View KPI Results

1. Navigate to **KPI Results** page
2. See all your KPIs displayed as cards
3. Click **View Evidence** to drill down into records

### Step 3: Drill Down into Evidence

1. In the evidence dialog, filter by status (optional)
2. Adjust limit for pagination
3. Click **Refresh** to load evidence records
4. View detailed record data in the table

---

## 📊 KPI Types Quick Reference

| Type | Use Case | Example |
|------|----------|---------|
| **Match Rate** | % of matched records | 85% match rate |
| **Unmatched Source** | Count of unmatched source records | 150 unmatched |
| **Unmatched Target** | Count of unmatched target records | 200 unmatched |
| **Inactive Count** | Count of inactive records | 50 inactive |
| **Data Quality Score** | Overall data quality | 90% quality |

---

## 🔧 API Quick Reference

### Create KPI
```bash
curl -X POST http://localhost:8000/v1/reconciliation/kpi/create \
  -H "Content-Type: application/json" \
  -d '{
    "kpi_name": "Material Match Rate",
    "kpi_type": "match_rate",
    "ruleset_id": "RECON_ABC123",
    "thresholds": {
      "warning_threshold": 80,
      "critical_threshold": 70,
      "comparison_operator": "less_than"
    }
  }'
```

### List KPIs
```bash
curl http://localhost:8000/v1/reconciliation/kpi/list
```

### Get KPI
```bash
curl http://localhost:8000/v1/reconciliation/kpi/KPI_ABC123
```

### Get Evidence
```bash
curl -X POST http://localhost:8000/v1/reconciliation/kpi/KPI_ABC123/evidence \
  -H "Content-Type: application/json" \
  -d '{
    "kpi_id": "KPI_ABC123",
    "match_status": "unmatched_source",
    "limit": 100,
    "offset": 0
  }'
```

---

## 📁 File Locations

| Type | Location | Example |
|------|----------|---------|
| **Config** | `kpi_configs/` | `kpi_config_KPI_ABC123.json` |
| **Results** | `kpi_results/` | `kpi_result_KPI_ABC123_20251026_143022.json` |
| **Evidence** | `kpi_evidence/` | `kpi_evidence_KPI_ABC123_20251026_143022.json` |

---

## 🎯 Threshold Configuration

### Less Than (Default)
```
Value < Critical → CRITICAL
Value < Warning → WARNING
Value >= Warning → PASS
```

**Example:** Match rate < 70% = CRITICAL, < 80% = WARNING

### Greater Than
```
Value > Critical → CRITICAL
Value > Warning → WARNING
Value <= Warning → PASS
```

**Example:** Unmatched count > 200 = CRITICAL, > 100 = WARNING

---

## 📊 Status Meanings

| Status | Meaning | Action |
|--------|---------|--------|
| **PASS** | KPI within acceptable range | No action needed |
| **WARNING** | KPI approaching threshold | Review and monitor |
| **CRITICAL** | KPI exceeded critical threshold | Investigate immediately |

---

## 🔍 Evidence Drill-Down

### Match Status Filters
- **matched** - Records found in both source and target
- **unmatched_source** - Records only in source
- **unmatched_target** - Records only in target
- **inactive** - Inactive records (is_active = 0 or NULL)

### Evidence Record Fields
- **record_id** - Primary key of the record
- **record_data** - Full record from master table
- **match_status** - Status of the record
- **rule_name** - Rule that matched/failed

---

## 💡 Common Use Cases

### Use Case 1: Monitor Match Quality
```
KPI Type: Match Rate
Threshold: Warning at 80%, Critical at 70%
Action: Alert when match rate drops below 80%
```

### Use Case 2: Track Unmatched Records
```
KPI Type: Unmatched Source Count
Threshold: Warning at 100, Critical at 200
Action: Alert when unmatched count exceeds 100
```

### Use Case 3: Monitor Data Quality
```
KPI Type: Data Quality Score
Threshold: Warning at 85%, Critical at 75%
Action: Alert when quality drops below 85%
```

---

## 🐛 Troubleshooting

### KPI Not Appearing
- Check if KPI is enabled
- Verify ruleset ID is correct
- Check `kpi_configs/` directory

### Evidence Not Loading
- Verify KPI has been calculated
- Check `kpi_evidence/` directory
- Try refreshing the page

### Wrong Status
- Verify threshold values
- Check comparison operator
- Review calculation formula

---

## 📚 Full Documentation

For detailed information, see:
- **Complete Guide:** `KPI_FEATURE_COMPLETE_GUIDE.md`
- **API Reference:** `KPI_FEATURE_COMPLETE_GUIDE.md#-api-endpoints`
- **Data Models:** `KPI_FEATURE_COMPLETE_GUIDE.md#-data-models`

---

## ✅ Checklist

- [ ] Created at least one KPI
- [ ] Viewed KPI results
- [ ] Drilled down into evidence records
- [ ] Tested threshold alerts
- [ ] Reviewed evidence data

You're ready to use KPIs! 🎉

# Calculate RCR
rcr = kpi_service.calculate_rcr(
    matched_count=1247,
    total_source_count=1300,
    ruleset_id="RECON_23B2B063",
    ruleset_name="Reconciliation_Test_New_321",
    execution_id="EXEC_001",
    source_kg="Test_New_321",
    source_schemas=["schema1", "schema2"]
)

# Store RCR
rcr_id = kpi_service.store_kpi("RECONCILIATION_COVERAGE_RATE", rcr)
print(f"RCR stored: {rcr_id}")

# Close connection
kpi_service.close()
```

### Calculate All Three KPIs
```python
from kg_builder.services.kpi_service import KPIService

kpi_service = KPIService()
kpi_service._ensure_indexes()

# Sample data
matched_records = [
    {"match_confidence": 0.95},
    {"match_confidence": 0.85},
    {"match_confidence": 0.75},
]

# Calculate RCR
rcr = kpi_service.calculate_rcr(
    matched_count=1247,
    total_source_count=1300,
    ruleset_id="RECON_23B2B063",
    ruleset_name="Reconciliation_Test_New_321",
    execution_id="EXEC_001",
    source_kg="Test_New_321",
    source_schemas=["schema1", "schema2"]
)
rcr_id = kpi_service.store_kpi("RECONCILIATION_COVERAGE_RATE", rcr)

# Calculate DQCS
dqcs = kpi_service.calculate_dqcs(
    matched_records=matched_records,
    ruleset_id="RECON_23B2B063",
    ruleset_name="Reconciliation_Test_New_321",
    execution_id="EXEC_001",
    source_kg="Test_New_321"
)
dqcs_id = kpi_service.store_kpi("DATA_QUALITY_CONFIDENCE_SCORE", dqcs)

# Calculate REI
rei = kpi_service.calculate_rei(
    matched_count=1247,
    total_source_count=1300,
    active_rules=18,
    total_rules=22,
    execution_time_ms=2500,
    ruleset_id="RECON_23B2B063",
    ruleset_name="Reconciliation_Test_New_321",
    execution_id="EXEC_001",
    source_kg="Test_New_321"
)
rei_id = kpi_service.store_kpi("RECONCILIATION_EFFICIENCY_INDEX", rei)

print(f"RCR: {rcr['metrics']['coverage_rate']}%")
print(f"DQCS: {dqcs['metrics']['overall_confidence_score']}")
print(f"REI: {rei['metrics']['efficiency_index']}")

kpi_service.close()
```

---

## 🌐 Using KPI API Endpoints

### Calculate KPIs via API
```bash
curl -X POST http://localhost:8000/kpi/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "execution_id": "EXEC_001",
    "ruleset_id": "RECON_23B2B063",
    "ruleset_name": "Reconciliation_Test_New_321",
    "source_kg": "Test_New_321",
    "source_schemas": ["schema1", "schema2"],
    "matched_count": 1247,
    "total_source_count": 1300,
    "matched_records": [
      {"match_confidence": 0.95},
      {"match_confidence": 0.85}
    ],
    "active_rules": 18,
    "total_rules": 22,
    "execution_time_ms": 2500
  }'
```

### Get Latest RCR
```bash
curl http://localhost:8000/kpi/rcr/RECON_23B2B063
```

### Get Latest DQCS
```bash
curl http://localhost:8000/kpi/dqcs/RECON_23B2B063
```

### Get Latest REI
```bash
curl http://localhost:8000/kpi/rei/RECON_23B2B063
```

---

## 📊 Understanding KPI Values

### RCR (Reconciliation Coverage Rate)
```
Value Range: 0-100%
Status Levels:
- ✅ HEALTHY: ≥90%
- ⚠️  WARNING: 80-90%
- ❌ CRITICAL: <80%

Example: 95.92% means 95.92% of source records were matched
```

### DQCS (Data Quality Confidence Score)
```
Value Range: 0-1.0
Status Levels:
- ✅ GOOD: ≥0.80
- ⚠️  ACCEPTABLE: 0.70-0.80
- ❌ POOR: <0.70

Example: 0.862 means average confidence is 86.2%
```

### REI (Reconciliation Efficiency Index)
```
Value Range: 0-100+
Status Levels:
- ✅ EXCELLENT: ≥50
- ✅ GOOD: 40-50
- ⚠️  ACCEPTABLE: 30-40
- ⚠️  WARNING: 20-30
- ❌ CRITICAL: <20

Example: 40.8 means acceptable efficiency
```

---

## 🔍 Monitoring KPIs

### Check Latest KPIs
```python
from kg_builder.services.kpi_service import KPIService

kpi_service = KPIService()

# Get latest values
rcr = kpi_service.get_latest_kpi("RECONCILIATION_COVERAGE_RATE", "RECON_23B2B063")
dqcs = kpi_service.get_latest_kpi("DATA_QUALITY_CONFIDENCE_SCORE", "RECON_23B2B063")
rei = kpi_service.get_latest_kpi("RECONCILIATION_EFFICIENCY_INDEX", "RECON_23B2B063")

# Display results
if rcr:
    print(f"RCR: {rcr['metrics']['coverage_rate']}% - {rcr['thresholds']['status']}")
if dqcs:
    print(f"DQCS: {dqcs['metrics']['overall_confidence_score']} - {dqcs['thresholds']['current_status']}")
if rei:
    print(f"REI: {rei['metrics']['efficiency_index']} - {rei['efficiency_assessment']['status']}")

kpi_service.close()
```

---

## 🐛 Troubleshooting

### MongoDB Connection Error
```
Error: No connection could be made because the target machine actively refused it

Solution:
1. Ensure MongoDB is running: docker ps | grep mongodb
2. If not running: docker run -d -p 27017:27017 --name mongodb mongo:latest
3. Check connection string in config.py
```

### Import Error
```
Error: ModuleNotFoundError: No module named 'pymongo'

Solution:
pip install pymongo
```

### Test Failures
```
If tests fail:
1. Check MongoDB is running
2. Check connection string is correct
3. Review error messages in logs
4. Check MongoDB is accessible at localhost:27017
```

---

## 📚 Documentation

- **Detailed Specs**: `docs/KPI_DESIGN_AND_ANALYSIS.md`
- **Implementation Guide**: `docs/KPI_IMPLEMENTATION_GUIDE.md`
- **Executive Summary**: `docs/KPI_EXECUTIVE_SUMMARY.md`
- **Implementation Status**: `docs/KPI_IMPLEMENTATION_COMPLETE.md`

---

## ✅ Checklist

- [ ] MongoDB installed and running
- [ ] pymongo installed (`pip install pymongo`)
- [ ] Unit tests passing (`python test_kpi_calculations.py`)
- [ ] Integration tests passing (`python test_kpi_service.py`)
- [ ] API endpoints accessible
- [ ] KPI values being calculated correctly
- [ ] KPI data being stored in MongoDB
- [ ] Monitoring dashboard setup (optional)

---

## 🎯 Next Steps

1. **Integrate with Reconciliation**: Auto-calculate KPIs after execution
2. **Setup Monitoring**: Create dashboard to visualize KPIs
3. **Configure Alerts**: Setup alerts for threshold violations
4. **Analyze Trends**: Monitor KPI trends over time
5. **Optimize Rules**: Use KPI insights to improve rules

---

**Quick Start Version**: 1.0
**Last Updated**: 2025-10-23
**Status**: Ready to Use

