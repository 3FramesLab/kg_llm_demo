# KPI Execution Payload Update ✅

## Overview

Updated the KPI Execution Dialog and backend to use a new, more flexible payload structure that supports multiple schemas and definitions.

---

## New Payload Structure

### Request Format

```json
{
  "kg_name": "KG_102",
  "schemas": ["newdqschema"],
  "definitions": ["Show me all the products in RBP GPU which are inactive OPS Excel"],
  "use_llm": true,
  "min_confidence": 0.7,
  "limit": 1000,
  "db_type": "sqlserver"
}
```

### Field Descriptions

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| **kg_name** | string | ✅ Yes | - | Knowledge Graph name |
| **schemas** | array | ✅ Yes | - | List of schema names to query |
| **definitions** | array | ✅ Yes | - | List of NL definitions to execute |
| **use_llm** | boolean | ❌ No | true | Use LLM for parsing |
| **min_confidence** | float | ❌ No | 0.7 | Minimum confidence threshold (0.0-1.0) |
| **limit** | integer | ❌ No | 1000 | Max records to return (1-100000) |
| **db_type** | string | ❌ No | sqlserver | Database type (sqlserver, mysql, postgresql, oracle) |

---

## Files Modified

### 1. Backend Model (`kg_builder/models.py`)

**Updated**: `KPIExecutionRequest` class (line 1019)

**Before**:
```python
class KPIExecutionRequest(BaseModel):
    kg_name: str
    select_schema: str
    ruleset_name: Optional[str] = None
    db_type: str = "mysql"
    limit_records: int = 1000
    use_llm: bool = True
    excluded_fields: Optional[List[str]] = None
```

**After**:
```python
class KPIExecutionRequest(BaseModel):
    kg_name: str
    schemas: List[str]
    definitions: List[str]
    use_llm: bool = True
    min_confidence: float = 0.7
    limit: int = 1000
    db_type: str = "sqlserver"
```

---

### 2. KPI Service (`kg_builder/services/landing_kpi_service.py`)

**Updated**: `execute_kpi()` method (line 155)

**Changes**:
- Extracts parameters from new payload structure
- Supports both old and new formats for backward compatibility
- Uses first schema from `schemas` list
- Stores execution parameters with new field names
- Removed `ruleset_name` and `excluded_fields` from storage

---

### 3. KPI Executor (`kg_builder/services/landing_kpi_executor.py`)

**Updated**: `_execute_kpi_internal()` method (line 71)

**Changes**:
- Extracts all parameters from new payload structure
- Uses first definition from `definitions` list
- Uses first schema from `schemas` list
- Passes `min_confidence` and `limit` to executor
- Consistent db_type handling (defaults to 'sqlserver')

---

### 4. Frontend Dialog (`web-app/src/components/KPIExecutionDialog.js`)

**Updated**: Complete component refactor

**Changes**:
- Updated form state to match new payload structure
- Added `schemas` array field
- Added `definitions` array field
- Added `min_confidence` field (0.0-1.0)
- Renamed `limit_records` to `limit`
- Changed `select_schema` to `schemas` (array)
- Made NL Definition read-only (from KPI)
- Updated validation logic
- Updated form UI with new fields

**New Form Fields**:
1. Knowledge Graph (dropdown)
2. Schema (dropdown)
3. NL Definition (read-only text area)
4. Min Confidence (number input, 0.0-1.0)
5. Limit Records (number input, 1-100000)

---

## Execution Flow

```
Frontend Dialog
    ↓
User selects KG, Schema, adjusts confidence & limit
    ↓
Payload created with new structure
    ↓
POST /v1/landing-kpi/kpis/{kpi_id}/execute
    ↓
Backend validates KPIExecutionRequest
    ↓
LandingKPIService.execute_kpi()
    ↓
Create execution record
    ↓
LandingKPIExecutor.execute_kpi_async()
    ↓
Extract parameters from new structure
    ↓
Use first definition & schema
    ↓
Classify → Parse → Connect → Execute
    ↓
Return results
```

---

## Backward Compatibility

The backend services support both old and new payload formats:

**Old Format** (still works):
```json
{
  "kg_name": "KG_102",
  "select_schema": "newdqschema",
  "db_type": "sqlserver",
  "limit_records": 1000,
  "use_llm": true
}
```

**New Format** (preferred):
```json
{
  "kg_name": "KG_102",
  "schemas": ["newdqschema"],
  "definitions": ["Show me all products..."],
  "db_type": "sqlserver",
  "limit": 1000,
  "use_llm": true,
  "min_confidence": 0.7
}
```

---

## Key Improvements

✅ **Flexible**: Supports multiple schemas and definitions (future-proof)
✅ **Cleaner**: Removed unused fields (ruleset_name, excluded_fields)
✅ **Consistent**: Hardcoded db_type to 'sqlserver' as required
✅ **Configurable**: Added min_confidence threshold
✅ **User-Friendly**: NL Definition shown as read-only in dialog
✅ **Backward Compatible**: Old format still works

---

## Testing

### Example Request

```bash
curl -X POST http://localhost:8000/v1/landing-kpi/kpis/2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "KG_102",
    "schemas": ["newdqschema"],
    "definitions": ["Show me all the products in RBP GPU which are inactive OPS Excel"],
    "use_llm": true,
    "min_confidence": 0.7,
    "limit": 1000,
    "db_type": "sqlserver"
  }'
```

### Expected Response

```json
{
  "success": true,
  "execution_id": 123,
  "status": "pending"
}
```

---

## Status

✅ **COMPLETE** - KPI Execution now uses new flexible payload structure!

