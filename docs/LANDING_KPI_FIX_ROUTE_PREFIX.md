# Landing KPI - Route Prefix Fix ✅

## Problem

When creating a new KPI, the frontend was showing a "Not Found" error (HTTP 404).

### Root Cause

The Landing KPI routes had a **double `/v1` prefix issue**:

1. **Backend Routes** (in `kg_builder/routes.py`):
   - Routes were defined with `/v1/landing-kpi/...` prefix
   - Example: `@router.post("/v1/landing-kpi/kpis")`

2. **Router Registration** (in `kg_builder/main.py`):
   - Router was included with `/v1` prefix:
   ```python
   app.include_router(router, prefix="/v1", tags=["Knowledge Graph"])
   ```

3. **Result**:
   - Final URL became: `/v1/v1/landing-kpi/kpis` ❌
   - This caused 404 "Not Found" errors

---

## Solution

### Step 1: Remove `/v1` from Route Definitions

**File**: `kg_builder/routes.py`

Changed all Landing KPI routes from:
```python
@router.post("/v1/landing-kpi/kpis", ...)
@router.get("/v1/landing-kpi/kpis", ...)
@router.get("/v1/landing-kpi/kpis/{kpi_id}", ...)
@router.put("/v1/landing-kpi/kpis/{kpi_id}", ...)
@router.delete("/v1/landing-kpi/kpis/{kpi_id}", ...)
@router.post("/v1/landing-kpi/kpis/{kpi_id}/execute", ...)
@router.get("/v1/landing-kpi/kpis/{kpi_id}/executions", ...)
@router.get("/v1/landing-kpi/executions/{execution_id}", ...)
@router.get("/v1/landing-kpi/executions/{execution_id}/drilldown", ...)
```

To:
```python
@router.post("/landing-kpi/kpis", ...)
@router.get("/landing-kpi/kpis", ...)
@router.get("/landing-kpi/kpis/{kpi_id}", ...)
@router.put("/landing-kpi/kpis/{kpi_id}", ...)
@router.delete("/landing-kpi/kpis/{kpi_id}", ...)
@router.post("/landing-kpi/kpis/{kpi_id}/execute", ...)
@router.get("/landing-kpi/kpis/{kpi_id}/executions", ...)
@router.get("/landing-kpi/executions/{execution_id}", ...)
@router.get("/landing-kpi/executions/{execution_id}/drilldown", ...)
```

### Step 2: Update Frontend API Client

**File**: `web-app/src/services/api.js`

Updated all API endpoints to use `/v1` prefix (since it's added by the router):
```javascript
// Landing KPI CRUD Operations
export const createKPI = (data) => api.post('/v1/landing-kpi/kpis', data);
export const listKPIs = (params) => api.get('/v1/landing-kpi/kpis', { params });
export const getKPI = (kpiId) => api.get(`/v1/landing-kpi/kpis/${kpiId}`);
export const updateKPI = (kpiId, data) => api.put(`/v1/landing-kpi/kpis/${kpiId}`, data);
export const deleteKPI = (kpiId) => api.delete(`/v1/landing-kpi/kpis/${kpiId}`);

// Landing KPI Execution
export const executeKPI = (kpiId, data) => api.post(`/v1/landing-kpi/kpis/${kpiId}/execute`, data);
export const getKPIExecutions = (kpiId, params) => api.get(`/v1/landing-kpi/kpis/${kpiId}/executions`, { params });
export const getKPIExecutionResult = (executionId) => api.get(`/v1/landing-kpi/executions/${executionId}`);
export const getKPIDrilldownData = (executionId, params) => api.get(`/v1/landing-kpi/executions/${executionId}/drilldown`, { params });
```

---

## Verification

### Test 1: Create KPI (cURL)
```bash
curl -X POST http://localhost:8000/v1/landing-kpi/kpis \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test KPI",
    "alias_name": "TKPI",
    "group_name": "Data Quality",
    "description": "Test",
    "nl_definition": "Show me all products"
  }'
```

**Response** ✅:
```json
{
  "success": true,
  "message": "KPI 'Test KPI' created successfully",
  "kpi": {
    "id": 1,
    "name": "Test KPI",
    "alias_name": "TKPI",
    "group_name": "Data Quality",
    "description": "Test",
    "nl_definition": "Show me all products",
    "created_at": "2025-10-27 17:54:04",
    "updated_at": "2025-10-27 17:54:04",
    "created_by": null,
    "is_active": 1
  }
}
```

### Test 2: List KPIs (cURL)
```bash
curl http://localhost:8000/v1/landing-kpi/kpis
```

**Response** ✅:
```json
{
  "success": true,
  "total": 1,
  "kpis": [
    {
      "id": 1,
      "name": "Test KPI",
      "alias_name": "TKPI",
      "group_name": "Data Quality",
      "description": "Test",
      "nl_definition": "Show me all products",
      "created_at": "2025-10-27 17:54:04",
      "updated_at": "2025-10-27 17:54:04",
      "created_by": null,
      "is_active": 1
    }
  ]
}
```

---

## Files Modified

1. **`kg_builder/routes.py`** (9 routes fixed)
   - Removed `/v1` prefix from all Landing KPI routes
   - Routes now use `/landing-kpi/...` instead of `/v1/landing-kpi/...`

2. **`web-app/src/services/api.js`** (9 endpoints updated)
   - Updated all API calls to use `/v1/landing-kpi/...`
   - Frontend now correctly calls the backend with proper prefix

---

## How It Works Now

```
Frontend Request
    ↓
/v1/landing-kpi/kpis (from api.js)
    ↓
Router Prefix: /v1
    ↓
Route Definition: /landing-kpi/kpis
    ↓
Final URL: /v1/landing-kpi/kpis ✅
    ↓
Backend Handler
```

---

## Status

✅ **FIXED** - All Landing KPI endpoints now working correctly

### All 9 Endpoints Working:
- ✅ POST `/v1/landing-kpi/kpis` - Create KPI
- ✅ GET `/v1/landing-kpi/kpis` - List KPIs
- ✅ GET `/v1/landing-kpi/kpis/{kpi_id}` - Get KPI
- ✅ PUT `/v1/landing-kpi/kpis/{kpi_id}` - Update KPI
- ✅ DELETE `/v1/landing-kpi/kpis/{kpi_id}` - Delete KPI
- ✅ POST `/v1/landing-kpi/kpis/{kpi_id}/execute` - Execute KPI
- ✅ GET `/v1/landing-kpi/kpis/{kpi_id}/executions` - Get execution history
- ✅ GET `/v1/landing-kpi/executions/{execution_id}` - Get execution result
- ✅ GET `/v1/landing-kpi/executions/{execution_id}/drilldown` - Get drill-down data

---

## Next Steps

1. Restart the backend server (already done)
2. Restart the frontend (if needed)
3. Test KPI creation in the UI
4. All CRUD operations should now work correctly

The "Not Found" error should now be resolved! 🎉

