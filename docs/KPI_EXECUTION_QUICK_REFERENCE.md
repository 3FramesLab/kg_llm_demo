# KPI Execution Quick Reference 🚀

## TL;DR

**KPIs are executed manually on-demand via API calls. There is NO automatic scheduling yet.**

---

## 🎯 How to Execute KPIs

### Option 1: Execute Single KPI
```bash
curl -X POST http://localhost:8000/v1/reconciliation/kpi/KPI_001/execute \
  -H "Content-Type: application/json" \
  -d '{"ruleset_id": "RECON_9240A5F7"}'
```

### Option 2: Execute Multiple KPIs (Batch)
```bash
curl -X POST http://localhost:8000/v1/reconciliation/kpi/execute/batch \
  -H "Content-Type: application/json" \
  -d '{
    "kpi_ids": ["KPI_001", "KPI_002", "KPI_003"],
    "ruleset_id": "RECON_9240A5F7"
  }'
```

### Option 3: Execute via Python
```python
from kg_builder.services.kpi_file_service import KPIFileService

service = KPIFileService()
result = service.execute_kpi("KPI_001", "RECON_9240A5F7")
print(f"Value: {result['calculated_value']}, Status: {result['status']}")
```

---

## 📊 What Happens During Execution

1. **Load KPI Definition** - Get KPI configuration
2. **Execute Query** - Query reconciliation data based on KPI type
3. **Calculate Value** - Apply formula to get KPI value
4. **Determine Status** - Compare against thresholds (OK/WARNING/CRITICAL)
5. **Save Result** - Store result to file with timestamp
6. **Return Result** - Send result back to caller

---

## 📁 Where Results Are Stored

```
data/kpi/results/
├── KPI_001_20251026125945.json    # Individual result
├── KPI_001_20251026130000.json    # Another execution
└── index.json                      # Index of all results
```

---

## 🔍 View KPI Results

### List All Results
```bash
curl http://localhost:8000/v1/reconciliation/kpi/results
```

### List Results for Specific KPI
```bash
curl http://localhost:8000/v1/reconciliation/kpi/results?kpi_id=KPI_001
```

### Get Specific Result
```bash
curl http://localhost:8000/v1/reconciliation/kpi/results/RES_ABC123
```

---

## 📋 KPI Types

| Type | Formula | Example |
|------|---------|---------|
| `match_rate` | (matched / total) × 100 | 95% |
| `match_percentage` | Same as match_rate | 95% |
| `unmatched_source_count` | total - matched | 50 |
| `unmatched_target_count` | total - matched | 50 |
| `inactive_record_count` | Count of inactive | 10 |
| `data_quality_score` | Avg confidence | 0.92 |

---

## 🎯 Status Determination

```
Value: 75%
Thresholds:
  - Warning: 80%
  - Critical: 70%
  - Operator: less_than

Result: WARNING (75% < 80%)
```

---

## 📊 Response Format

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
    "metrics": {
      "matched_count": 955,
      "total_source_count": 1000
    },
    "thresholds": {
      "warning_threshold": 80,
      "critical_threshold": 70,
      "comparison_operator": "less_than"
    }
  },
  "result_id": "RES_ABC123"
}
```

---

## 🔄 Execution Flow

```
1. Create KPI
   ↓
2. Execute KPI (manual)
   ↓
3. Backend calculates value
   ↓
4. Result saved to file
   ↓
5. View results
```

---

## ⚙️ API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/v1/reconciliation/kpi/{kpi_id}/execute` | Execute single KPI |
| POST | `/v1/reconciliation/kpi/execute/batch` | Execute multiple KPIs |
| GET | `/v1/reconciliation/kpi/results` | List all results |
| GET | `/v1/reconciliation/kpi/results/{result_id}` | Get specific result |
| DELETE | `/v1/reconciliation/kpi/results/{result_id}` | Delete result |

---

## 🚀 Common Workflows

### Workflow 1: Create and Execute KPI
```bash
# 1. Create KPI
curl -X POST http://localhost:8000/v1/reconciliation/kpi/create \
  -H "Content-Type: application/json" \
  -d '{
    "kpi_name": "Match Rate",
    "kpi_type": "match_rate",
    "ruleset_id": "RECON_9240A5F7",
    "thresholds": {
      "warning_threshold": 80,
      "critical_threshold": 70,
      "comparison_operator": "less_than"
    }
  }'

# 2. Execute KPI
curl -X POST http://localhost:8000/v1/reconciliation/kpi/KPI_001/execute \
  -H "Content-Type: application/json" \
  -d '{"ruleset_id": "RECON_9240A5F7"}'

# 3. View results
curl http://localhost:8000/v1/reconciliation/kpi/results
```

### Workflow 2: Batch Execute Multiple KPIs
```bash
curl -X POST http://localhost:8000/v1/reconciliation/kpi/execute/batch \
  -H "Content-Type: application/json" \
  -d '{
    "kpi_ids": ["KPI_001", "KPI_002", "KPI_003"],
    "ruleset_id": "RECON_9240A5F7"
  }'
```

---

## 📌 Important Notes

1. **Manual Execution** - KPIs are NOT automatically executed
2. **On-Demand** - Execute whenever you need results
3. **File-Based** - Results stored as JSON files
4. **Timestamped** - Each execution creates new result file
5. **Indexed** - Results indexed for quick lookup
6. **Stateless** - No database required

---

## 🔮 Future: Automatic Execution

Currently planned but not implemented:
- ✅ Scheduled execution (hourly, daily, etc.)
- ✅ Event-based triggers (on reconciliation complete)
- ✅ Alerts (email, Slack)
- ✅ Dashboards
- ✅ Web UI execute button

---

## 📚 Related Documentation

- **WHEN_KPI_GETS_EXECUTED.md** - Detailed explanation
- **KPI_FEATURE_COMPLETE_GUIDE.md** - Complete guide
- **KPI_QUICK_START.md** - Quick start guide

---

## 💡 Tips

1. **Always provide ruleset_id** - Needed to query reconciliation data
2. **Check thresholds** - Set appropriate warning/critical levels
3. **Monitor results** - Check status after execution
4. **Keep history** - Results are timestamped for tracking
5. **Batch execute** - Execute multiple KPIs at once for efficiency

---

## ❓ FAQ

**Q: When do KPIs execute automatically?**
A: They don't. You must manually call the execute endpoint.

**Q: Can I schedule KPI execution?**
A: Not yet. This is a planned feature.

**Q: Where are results stored?**
A: In `data/kpi/results/` as JSON files.

**Q: How do I view results?**
A: Use the `/v1/reconciliation/kpi/results` endpoint.

**Q: Can I delete results?**
A: Yes, use DELETE `/v1/reconciliation/kpi/results/{result_id}`.

---

That's it! KPIs are simple: create them, execute them manually, view results. 🎉


