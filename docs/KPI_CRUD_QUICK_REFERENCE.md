# KPI CRUD - Quick Reference Card

**Last Updated**: 2025-10-27  
**Status**: Backend Complete ✅

---

## 🚀 Quick Start (30 seconds)

```bash
# 1. Initialize database
python scripts/init_landing_kpi_db.py

# 2. Start server
python -m uvicorn kg_builder.main:app --reload

# 3. Open Swagger UI
# http://localhost:8000/docs
```

---

## 📍 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/v1/landing-kpi/kpis` | Create KPI |
| GET | `/v1/landing-kpi/kpis` | List KPIs |
| GET | `/v1/landing-kpi/kpis/{id}` | Get KPI |
| PUT | `/v1/landing-kpi/kpis/{id}` | Update KPI |
| DELETE | `/v1/landing-kpi/kpis/{id}` | Delete KPI |
| POST | `/v1/landing-kpi/kpis/{id}/execute` | Execute KPI |
| GET | `/v1/landing-kpi/kpis/{id}/executions` | Get history |
| GET | `/v1/landing-kpi/executions/{id}` | Get result |
| GET | `/v1/landing-kpi/executions/{id}/drilldown` | Get drill-down |

---

## 💾 Database

**Location**: `data/landing_kpi.db`

**Tables**:
- `kpi_definitions` - Master KPI config
- `kpi_execution_results` - Execution history

**Indexes**:
- `idx_kpi_name` - KPI name lookup
- `idx_kpi_active` - Active status filter
- `idx_execution_kpi_id` - Execution lookup
- `idx_execution_timestamp` - Time-based queries
- `idx_execution_status` - Status filter

---

## 🔧 Service Layer

**File**: `kg_builder/services/landing_kpi_service.py`

**Class**: `LandingKPIService`

**Key Methods**:
```python
# CRUD
create_kpi(kpi_data)
get_kpi(kpi_id)
list_kpis(filters)
update_kpi(kpi_id, kpi_data)
delete_kpi(kpi_id)

# Execution
execute_kpi(kpi_id, params)
update_execution_result(exec_id, data)
get_execution_result(exec_id)
get_execution_results(kpi_id, filters)

# Drill-down
get_drilldown_data(exec_id, page, page_size)
```

---

## 📦 Pydantic Models

**File**: `kg_builder/models.py`

**Models**:
- `KPICreateRequest` - Create request
- `KPIUpdateRequest` - Update request
- `KPIDefinition` - KPI response
- `KPIListResponse` - List response
- `KPIExecutionRequest` - Execute request
- `KPIExecutionResult` - Execution response
- `KPIExecutionResponse` - Single execution
- `KPIExecutionListResponse` - List executions
- `DrilldownRequest` - Pagination request
- `DrilldownResponse` - Drill-down response

---

## 🧪 Common Curl Commands

### Create KPI
```bash
curl -X POST http://localhost:8000/v1/landing-kpi/kpis \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Product Match Rate",
    "alias_name": "PMR",
    "group_name": "Data Quality",
    "description": "Products matched between systems",
    "nl_definition": "Show products in RBP not in OPS"
  }'
```

### List KPIs
```bash
curl http://localhost:8000/v1/landing-kpi/kpis
```

### Get KPI
```bash
curl http://localhost:8000/v1/landing-kpi/kpis/1
```

### Update KPI
```bash
curl -X PUT http://localhost:8000/v1/landing-kpi/kpis/1 \
  -H "Content-Type: application/json" \
  -d '{"description": "Updated description"}'
```

### Delete KPI
```bash
curl -X DELETE http://localhost:8000/v1/landing-kpi/kpis/1
```

### Execute KPI
```bash
curl -X POST http://localhost:8000/v1/landing-kpi/kpis/1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "KG_098",
    "select_schema": "newdqschema",
    "db_type": "mysql",
    "limit_records": 1000,
    "use_llm": true
  }'
```

### Get Execution History
```bash
curl http://localhost:8000/v1/landing-kpi/kpis/1/executions
```

### Get Execution Result
```bash
curl http://localhost:8000/v1/landing-kpi/executions/1
```

### Get Drill-down Data
```bash
curl "http://localhost:8000/v1/landing-kpi/executions/1/drilldown?page=1&page_size=50"
```

---

## 📊 Request/Response Examples

### Create KPI Request
```json
{
  "name": "Product Match Rate",
  "alias_name": "PMR",
  "group_name": "Data Quality",
  "description": "Percentage of products matched",
  "nl_definition": "Show products in RBP not in OPS",
  "created_by": "admin"
}
```

### Create KPI Response
```json
{
  "success": true,
  "message": "KPI 'Product Match Rate' created successfully",
  "kpi": {
    "id": 1,
    "name": "Product Match Rate",
    "alias_name": "PMR",
    "group_name": "Data Quality",
    "description": "Percentage of products matched",
    "nl_definition": "Show products in RBP not in OPS",
    "created_at": "2025-10-27T21:00:00",
    "updated_at": "2025-10-27T21:00:00",
    "created_by": "admin",
    "is_active": true
  }
}
```

### Execute KPI Request
```json
{
  "kg_name": "KG_098",
  "select_schema": "newdqschema",
  "ruleset_name": "default",
  "db_type": "mysql",
  "limit_records": 1000,
  "use_llm": true,
  "excluded_fields": ["internal_id"]
}
```

### Drill-down Response
```json
{
  "success": true,
  "execution_id": 1,
  "page": 1,
  "page_size": 50,
  "total": 150,
  "total_pages": 3,
  "data": [
    {
      "product_id": "P001",
      "product_name": "Product A",
      "status": "matched"
    }
  ]
}
```

---

## 🔍 Query Parameters

### List KPIs
- `group_name` - Filter by group
- `is_active` - Filter by status (default: true)
- `search` - Search in name/description

### Get Executions
- `status` - Filter by status (pending, success, failed)

### Get Drill-down
- `page` - Page number (default: 1)
- `page_size` - Records per page (default: 50)

---

## 🛠️ Files Overview

| File | Purpose | Lines |
|------|---------|-------|
| `scripts/init_landing_kpi_db.py` | DB initialization | 150+ |
| `kg_builder/services/landing_kpi_service.py` | Service layer | 300+ |
| `kg_builder/models.py` | Pydantic models | 130+ |
| `kg_builder/routes.py` | API endpoints | 200+ |

---

## 📚 Documentation

- **KPI_CRUD_BACKEND_IMPLEMENTATION_SUMMARY.md** - Complete overview
- **KPI_CRUD_API_TESTING_GUIDE.md** - Detailed API reference
- **KPI_CRUD_IMPLEMENTATION_PHASE_1_COMPLETE.md** - Phase details
- **KPI_CRUD_IMPLEMENTATION_IMPROVEMENTS.md** - Enhancement suggestions

---

## ✅ Status

| Component | Status |
|-----------|--------|
| Database | ✅ Ready |
| Service Layer | ✅ Ready |
| API Endpoints | ✅ Ready |
| Pydantic Models | ✅ Ready |
| Frontend | ⏳ Pending |
| Testing | ⏳ Pending |

---

## 🚀 Next Steps

1. **Frontend Development** (Phase 5)
   - React components
   - KPI management UI
   - Execution history view
   - Drill-down table

2. **Testing** (Phase 6)
   - Unit tests
   - Integration tests
   - E2E tests

3. **Integration** (Phase 7)
   - Connect to NL Query engine
   - Implement execution logic
   - Add result processing

---

## 📞 Support

For detailed information, see:
- **API Testing**: `KPI_CRUD_API_TESTING_GUIDE.md`
- **Implementation**: `KPI_CRUD_IMPLEMENTATION_PHASE_1_COMPLETE.md`
- **Improvements**: `KPI_CRUD_IMPLEMENTATION_IMPROVEMENTS.md`

---

**Last Updated**: 2025-10-27  
**Backend Status**: ✅ COMPLETE

---

