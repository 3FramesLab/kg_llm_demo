# Quick Start: KPI Feature (Fixed) 🚀

## ✅ What Was Fixed

All KPI API routes were returning **404 Not Found** due to double `/v1` prefix.

**Fixed:** Removed `/v1` from all KPI route decorators in `kg_builder/routes.py`

---

## 🚀 Getting Started

### 1. Start Backend Server
```bash
python -m uvicorn kg_builder.main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 2. Start Frontend Server
```bash
cd web-app
npm start
```

Expected output:
```
Compiled successfully!
You can now view web-app in the browser.
```

### 3. Open Web App
Navigate to: `http://localhost:3000`

---

## 📋 KPI Features Available

### 1. KPI Management
**URL:** `http://localhost:3000/kpi-management`

**Features:**
- ✅ Create new KPIs
- ✅ View all KPIs
- ✅ Filter by ruleset
- ✅ Edit KPI configurations
- ✅ Delete KPIs

### 2. KPI Results
**URL:** `http://localhost:3000/kpi-results`

**Features:**
- ✅ View KPI execution results
- ✅ Drill-down into evidence data
- ✅ Analyze detailed records
- ✅ Filter by KPI

---

## 🔗 API Endpoints (Now Working!)

### Create KPI
```bash
POST /v1/reconciliation/kpi/create
```

### List KPIs
```bash
GET /v1/reconciliation/kpi/list
GET /v1/reconciliation/kpi/list?ruleset_id=my_ruleset
```

### Get KPI Details
```bash
GET /v1/reconciliation/kpi/{kpi_id}
```

### Get KPI Evidence (Drill-Down)
```bash
POST /v1/reconciliation/kpi/{kpi_id}/evidence
```

### Execute KPI
```bash
POST /v1/reconciliation/kpi/{kpi_id}/execute
```

### Batch Execute KPIs
```bash
POST /v1/reconciliation/kpi/execute/batch
```

### List KPI Results
```bash
GET /v1/reconciliation/kpi/results
GET /v1/reconciliation/kpi/results?kpi_id=my_kpi&limit=50
```

### Get KPI Result
```bash
GET /v1/reconciliation/kpi/results/{result_id}
```

---

## 🧪 Test the Fix

### Test 1: Check Backend Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "falkordb_connected": true,
  "graphiti_available": true
}
```

### Test 2: List KPIs
```bash
curl http://localhost:8000/v1/reconciliation/kpi/list
```

Expected response:
```json
{
  "success": true,
  "count": 0,
  "kpis": []
}
```

### Test 3: Create KPI
```bash
curl -X POST http://localhost:8000/v1/reconciliation/kpi/create \
  -H "Content-Type: application/json" \
  -d '{
    "kpi_name": "Material Match Rate",
    "kpi_description": "Percentage of materials matched",
    "kpi_type": "match_rate",
    "ruleset_id": "material_ruleset",
    "warning_threshold": 80,
    "critical_threshold": 70,
    "comparison_operator": "less_than",
    "enabled": true
  }'
```

---

## 📊 KPI Types Available

1. **match_rate** - Percentage of matched records
2. **unmatched_source_count** - Count of unmatched source records
3. **unmatched_target_count** - Count of unmatched target records
4. **inactive_record_count** - Count of inactive records
5. **match_percentage** - Match percentage (0-100)
6. **data_quality_score** - Overall data quality score

---

## 🔍 Troubleshooting

### Issue: Still Getting 404 Errors

**Solution:**
1. Stop backend server (Ctrl+C)
2. Clear Python cache: `find . -type d -name __pycache__ -exec rm -r {} +`
3. Restart backend: `python -m uvicorn kg_builder.main:app --reload`

### Issue: Frontend Can't Connect to Backend

**Solution:**
1. Check backend is running on port 8000
2. Check CORS is enabled in main.py
3. Check frontend is calling correct URL: `http://localhost:8000/v1/...`

### Issue: KPI Pages Show Blank

**Solution:**
1. Open DevTools (F12)
2. Check Console tab for errors
3. Check Network tab for API responses
4. Verify backend is returning JSON (not HTML)

---

## 📚 Documentation

- **API Route Fix**: `docs/API_ROUTE_404_FIX.md`
- **KPI Feature Guide**: `docs/KPI_FEATURE_COMPLETE_GUIDE.md`
- **Error Fix Summary**: `docs/KPI_ERROR_FIX_AND_MONGODB_REMOVAL.md`

---

## ✨ Summary

✅ **All 404 errors fixed**
✅ **KPI routes working**
✅ **Frontend can load KPI pages**
✅ **API endpoints accessible**
✅ **Ready for production**

Enjoy using the KPI feature! 🎉


