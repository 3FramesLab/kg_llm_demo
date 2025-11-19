# Schema Configuration API - Quick Reference

## 🎯 What Was Implemented

### Frontend (JavaScript)
**File**: `web-app/src/services/api.js` (Line 178)
```javascript
export const getSchemaConfigurations = () => api.get('/database/schema-configuration');
```

### Backend (Python)
**File**: `kg_builder/routers/database_router.py` (Lines 621-681)
```python
@router.get("/database/schema-configuration")
async def get_schema_configurations():
    # Returns all saved schema configurations
```

## 🚀 Quick Start

### 1. Start the Backend Server
```bash
python -m uvicorn kg_builder.main:app --reload
```

### 2. Test the API
```bash
python test_schema_configuration_api.py
```

### 3. Use in Frontend
```javascript
import { getSchemaConfigurations } from '../services/api';

// Fetch all configurations
const response = await getSchemaConfigurations();
console.log(response.data.configurations);
```

## 📡 API Endpoints

### GET - Retrieve All Configurations
```
GET /v1/database/schema-configuration
```

**Response**:
```json
{
  "success": true,
  "configurations": [...],
  "count": 5,
  "message": "Successfully retrieved 5 schema configuration(s)"
}
```

### POST - Save New Configuration (Existing)
```
POST /v1/database/schema-configuration
```

**Request Body**:
```json
{
  "tables": [
    {
      "connectionId": "uuid",
      "connectionName": "My DB",
      "databaseName": "mydb",
      "tableName": "users",
      "tableAliases": ["user"],
      "columns": [
        {
          "name": "id",
          "aliases": ["user_id"]
        }
      ]
    }
  ]
}
```

## 📂 File Storage

**Location**: `schema_configurations/`

**Format**: `schema_config_YYYYMMDD_HHMMSS_<uuid>.json`

**Example**: `schema_config_20251118_212935_da1e9ea2.json`

## 🧪 Testing

### Manual Testing with cURL
```bash
# Get all configurations
curl http://localhost:8000/v1/database/schema-configuration

# Save a new configuration
curl -X POST http://localhost:8000/v1/database/schema-configuration \
  -H "Content-Type: application/json" \
  -d '{"tables": [...]}'
```

### Automated Testing
```bash
python test_schema_configuration_api.py
```

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## ✅ Features

- ✅ Retrieve all saved schema configurations
- ✅ Sorted by creation date (newest first)
- ✅ Includes full configuration data and summaries
- ✅ Proper error handling and logging
- ✅ Consistent response format
- ✅ Automatic directory creation
- ✅ Graceful handling of corrupted files

## 🔍 Response Structure

Each configuration includes:
- `id`: Unique identifier
- `created_at`: ISO 8601 timestamp
- `tables`: Array of table configurations
- `summary`: Statistics (tables, columns, databases, connections)

## 💡 Usage Tips

1. **Check for existing configurations before creating new ones**
2. **Use the summary field for quick overview**
3. **Sort by created_at for chronological order**
4. **Handle empty state (count: 0) gracefully**
5. **Log errors for debugging**

## 🐛 Troubleshooting

### No configurations returned
- Check if `schema_configurations/` directory exists
- Verify JSON files are valid
- Check server logs for errors

### 500 Error
- Check file permissions
- Verify JSON file format
- Review server logs

### Connection refused
- Ensure backend server is running
- Check port 8000 is not in use
- Verify API_BASE_URL in frontend

## 📝 Files Modified/Created

### Modified
1. `web-app/src/services/api.js` - Added GET function
2. `kg_builder/routers/database_router.py` - Added GET endpoint

### Created
1. `test_schema_configuration_api.py` - Test script
2. `SCHEMA_CONFIGURATION_API_IMPLEMENTATION.md` - Full documentation
3. `SCHEMA_CONFIG_QUICK_REFERENCE.md` - This file

## 🎉 Status

**✅ COMPLETE AND READY FOR USE**

All endpoints are implemented, tested, and documented.

