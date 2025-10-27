# KPI CRUD API Testing Guide

**Date**: 2025-10-27  
**API Prefix**: `/v1/landing-kpi/`  
**Base URL**: `http://localhost:8000`

---

## 🚀 Quick Start

### 1. Start the Server
```bash
python -m uvicorn kg_builder.main:app --reload
```

### 2. Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📝 API Endpoints Reference

### 1. Create KPI
**Endpoint**: `POST /v1/landing-kpi/kpis`

**Request**:
```json
{
  "name": "Product Match Rate",
  "alias_name": "PMR",
  "group_name": "Data Quality",
  "description": "Percentage of products matched between systems",
  "nl_definition": "Show me all products in RBP that are not in OPS",
  "created_by": "admin"
}
```

**Response** (201):
```json
{
  "success": true,
  "message": "KPI 'Product Match Rate' created successfully",
  "kpi": {
    "id": 1,
    "name": "Product Match Rate",
    "alias_name": "PMR",
    "group_name": "Data Quality",
    "description": "Percentage of products matched between systems",
    "nl_definition": "Show me all products in RBP that are not in OPS",
    "created_at": "2025-10-27T21:00:00",
    "updated_at": "2025-10-27T21:00:00",
    "created_by": "admin",
    "is_active": true
  }
}
```

---

### 2. List KPIs
**Endpoint**: `GET /v1/landing-kpi/kpis`

**Query Parameters**:
- `group_name` (optional) - Filter by group
- `is_active` (optional) - Filter by active status (default: true)
- `search` (optional) - Search in name and description

**Examples**:
```bash
# Get all active KPIs
curl http://localhost:8000/v1/landing-kpi/kpis

# Filter by group
curl "http://localhost:8000/v1/landing-kpi/kpis?group_name=Data%20Quality"

# Search
curl "http://localhost:8000/v1/landing-kpi/kpis?search=Product"

# Get all (including inactive)
curl "http://localhost:8000/v1/landing-kpi/kpis?is_active=false"
```

**Response**:
```json
{
  "success": true,
  "total": 1,
  "kpis": [
    {
      "id": 1,
      "name": "Product Match Rate",
      "alias_name": "PMR",
      "group_name": "Data Quality",
      "description": "Percentage of products matched between systems",
      "nl_definition": "Show me all products in RBP that are not in OPS",
      "created_at": "2025-10-27T21:00:00",
      "updated_at": "2025-10-27T21:00:00",
      "created_by": "admin",
      "is_active": true
    }
  ]
}
```

---

### 3. Get KPI
**Endpoint**: `GET /v1/landing-kpi/kpis/{kpi_id}`

**Example**:
```bash
curl http://localhost:8000/v1/landing-kpi/kpis/1
```

**Response**:
```json
{
  "success": true,
  "kpi": {
    "id": 1,
    "name": "Product Match Rate",
    ...
  }
}
```

---

### 4. Update KPI
**Endpoint**: `PUT /v1/landing-kpi/kpis/{kpi_id}`

**Request** (partial update):
```json
{
  "description": "Updated description",
  "alias_name": "PMR_V2"
}
```

**Example**:
```bash
curl -X PUT http://localhost:8000/v1/landing-kpi/kpis/1 \
  -H "Content-Type: application/json" \
  -d '{"description": "Updated description"}'
```

**Response**:
```json
{
  "success": true,
  "message": "KPI ID 1 updated successfully",
  "kpi": {
    "id": 1,
    "description": "Updated description",
    ...
  }
}
```

---

### 5. Delete KPI
**Endpoint**: `DELETE /v1/landing-kpi/kpis/{kpi_id}`

**Example**:
```bash
curl -X DELETE http://localhost:8000/v1/landing-kpi/kpis/1
```

**Response**:
```json
{
  "success": true,
  "message": "KPI ID 1 deleted successfully"
}
```

---

### 6. Execute KPI
**Endpoint**: `POST /v1/landing-kpi/kpis/{kpi_id}/execute`

**Request**:
```json
{
  "kg_name": "KG_098",
  "select_schema": "newdqschema",
  "ruleset_name": "default",
  "db_type": "mysql",
  "limit_records": 1000,
  "use_llm": true,
  "excluded_fields": ["internal_id", "temp_field"]
}
```

**Example**:
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

**Response**:
```json
{
  "success": true,
  "message": "KPI execution started",
  "execution_result": {
    "id": 1,
    "kpi_id": 1,
    "kg_name": "KG_098",
    "select_schema": "newdqschema",
    "execution_status": "pending",
    "execution_timestamp": "2025-10-27T21:05:00",
    ...
  }
}
```

---

### 7. Get Execution History
**Endpoint**: `GET /v1/landing-kpi/kpis/{kpi_id}/executions`

**Query Parameters**:
- `status` (optional) - Filter by status (pending, success, failed)

**Example**:
```bash
# Get all executions
curl http://localhost:8000/v1/landing-kpi/kpis/1/executions

# Get only successful executions
curl "http://localhost:8000/v1/landing-kpi/kpis/1/executions?status=success"
```

**Response**:
```json
{
  "success": true,
  "total": 1,
  "executions": [
    {
      "id": 1,
      "kpi_id": 1,
      "execution_status": "pending",
      ...
    }
  ]
}
```

---

### 8. Get Execution Result
**Endpoint**: `GET /v1/landing-kpi/executions/{execution_id}`

**Example**:
```bash
curl http://localhost:8000/v1/landing-kpi/executions/1
```

**Response**:
```json
{
  "success": true,
  "execution": {
    "id": 1,
    "kpi_id": 1,
    "generated_sql": "SELECT * FROM ...",
    "number_of_records": 150,
    "execution_status": "success",
    "execution_time_ms": 245.5,
    "confidence_score": 0.95,
    ...
  }
}
```

---

### 9. Get Drill-down Data
**Endpoint**: `GET /v1/landing-kpi/executions/{execution_id}/drilldown`

**Query Parameters**:
- `page` (optional, default: 1) - Page number
- `page_size` (optional, default: 50) - Records per page

**Example**:
```bash
# Get first page
curl http://localhost:8000/v1/landing-kpi/executions/1/drilldown

# Get page 2 with 100 records per page
curl "http://localhost:8000/v1/landing-kpi/executions/1/drilldown?page=2&page_size=100"
```

**Response**:
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
    },
    ...
  ]
}
```

---

## 🧪 Complete Test Workflow

```bash
# 1. Create a KPI
KPI_ID=$(curl -s -X POST http://localhost:8000/v1/landing-kpi/kpis \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test KPI",
    "nl_definition": "Show all products"
  }' | jq -r '.kpi.id')

echo "Created KPI: $KPI_ID"

# 2. List KPIs
curl http://localhost:8000/v1/landing-kpi/kpis | jq

# 3. Get specific KPI
curl http://localhost:8000/v1/landing-kpi/kpis/$KPI_ID | jq

# 4. Update KPI
curl -X PUT http://localhost:8000/v1/landing-kpi/kpis/$KPI_ID \
  -H "Content-Type: application/json" \
  -d '{"description": "Updated"}' | jq

# 5. Execute KPI
EXEC_ID=$(curl -s -X POST http://localhost:8000/v1/landing-kpi/kpis/$KPI_ID/execute \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "KG_098",
    "select_schema": "newdqschema"
  }' | jq -r '.execution_result.id')

echo "Created Execution: $EXEC_ID"

# 6. Get execution history
curl http://localhost:8000/v1/landing-kpi/kpis/$KPI_ID/executions | jq

# 7. Get execution result
curl http://localhost:8000/v1/landing-kpi/executions/$EXEC_ID | jq

# 8. Get drill-down data
curl http://localhost:8000/v1/landing-kpi/executions/$EXEC_ID/drilldown | jq
```

---

## 🔍 Error Handling

### Common Errors

**400 Bad Request** - Invalid input
```json
{
  "detail": "KPI name 'Product Match Rate' already exists"
}
```

**404 Not Found** - Resource not found
```json
{
  "detail": "KPI ID 999 not found"
}
```

**500 Internal Server Error** - Server error
```json
{
  "detail": "Database connection error"
}
```

---

## 📊 Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Server Error |

---

**End of Document**

