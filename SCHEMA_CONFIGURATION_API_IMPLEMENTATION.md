# Schema Configuration API Implementation

## Overview
This document describes the implementation of the schema configuration API endpoints that allow users to save and retrieve database schema configurations through the Schema Wizard.

## Implementation Summary

### Frontend Changes
**File**: `web-app/src/services/api.js`

Added new API function to retrieve schema configurations:
```javascript
export const getSchemaConfigurations = () => api.get('/database/schema-configuration');
```

**Location**: Line 178, immediately after the existing `saveSchemaConfiguration` function

### Backend Changes
**File**: `kg_builder/routers/database_router.py`

Added new GET endpoint to retrieve all saved schema configurations:
```python
@router.get("/database/schema-configuration")
async def get_schema_configurations():
    """Retrieve all saved schema configurations."""
```

**Location**: Lines 621-681, immediately after the existing POST endpoint

## API Endpoints

### 1. Save Schema Configuration (Existing)
**Endpoint**: `POST /v1/database/schema-configuration`

**Description**: Saves a new schema configuration from the Schema Wizard

**Request Body**:
```json
{
  "tables": [
    {
      "connectionId": "uuid-string",
      "connectionName": "Connection Name",
      "databaseName": "database_name",
      "tableName": "table_name",
      "tableAliases": ["alias1", "alias2"],
      "columns": [
        {
          "name": "column_name",
          "aliases": ["col_alias1", "col_alias2"]
        }
      ]
    }
  ]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Schema configuration saved successfully",
  "config_id": "schema_config_20251118_212935_da1e9ea2",
  "summary": {
    "total_tables": 2,
    "total_columns": 6,
    "databases": ["NewDQ"],
    "connections": ["SQL Server"]
  },
  "file_path": "schema_configurations/schema_config_20251118_212935_da1e9ea2.json"
}
```

### 2. Get Schema Configurations (NEW)
**Endpoint**: `GET /v1/database/schema-configuration`

**Description**: Retrieves all saved schema configurations

**Request**: No parameters required

**Response**:
```json
{
  "success": true,
  "configurations": [
    {
      "id": "schema_config_20251118_212935_da1e9ea2",
      "created_at": "2025-11-18T21:29:35.253652",
      "tables": [...],
      "summary": {
        "total_tables": 2,
        "total_columns": 6,
        "databases": ["NewDQ"],
        "connections": ["SQL Server"]
      }
    }
  ],
  "count": 1,
  "message": "Successfully retrieved 1 schema configuration(s)"
}
```

## Data Storage

### Storage Location
Schema configurations are stored as JSON files in the `schema_configurations/` directory.

### File Naming Convention
`schema_config_YYYYMMDD_HHMMSS_<8-char-uuid>.json`

Example: `schema_config_20251118_212935_da1e9ea2.json`

### Data Structure
Each configuration file contains:
- **id**: Unique identifier for the configuration
- **created_at**: ISO 8601 timestamp of creation
- **tables**: Array of table configurations with columns and aliases
- **summary**: Aggregated statistics (total tables, columns, databases, connections)

## Features

### GET Endpoint Features
1. **Automatic Directory Creation**: Creates the storage directory if it doesn't exist
2. **Error Handling**: Gracefully handles corrupted JSON files and continues processing
3. **Sorting**: Returns configurations sorted by creation date (newest first)
4. **Comprehensive Logging**: Logs all operations for debugging and monitoring
5. **Empty State Handling**: Returns appropriate response when no configurations exist

### Error Handling
- **404 Errors**: Not applicable (returns empty array if no configurations)
- **500 Errors**: Returned for file system errors or JSON parsing failures
- **Logging**: All errors are logged with full stack traces for debugging

## Usage Examples

### Frontend Usage
```javascript
import { getSchemaConfigurations, saveSchemaConfiguration } from '../services/api';

// Retrieve all configurations
const response = await getSchemaConfigurations();
const configurations = response.data.configurations;

// Save a new configuration
const newConfig = {
  tables: [...]
};
const saveResponse = await saveSchemaConfiguration(newConfig);
```

### Backend Testing
Use the provided test script:
```bash
python test_schema_configuration_api.py
```

## Testing

### Test Script
**File**: `test_schema_configuration_api.py`

The test script includes:
1. **Test 1**: Retrieve existing configurations
2. **Test 2**: Save a new configuration
3. **Test 3**: Verify the new configuration was saved

### Running Tests
```bash
# Ensure the backend server is running
python -m uvicorn kg_builder.main:app --reload

# In another terminal, run the test
python test_schema_configuration_api.py
```

## Integration Points

### Router Registration
The database router is already registered in `kg_builder/main.py`:
```python
from kg_builder.routers.database_router import router as database_router
app.include_router(database_router, prefix="/v1", tags=["Database Connections"])
```

### API Documentation
The endpoint is automatically documented in:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Future Enhancements

Potential improvements for future iterations:
1. Add filtering/search capabilities (by database, connection, date range)
2. Add pagination for large numbers of configurations
3. Add individual configuration retrieval by ID
4. Add update/delete endpoints for configuration management
5. Add database storage instead of file-based storage
6. Add configuration validation and schema versioning
7. Add export/import functionality for configurations

## Status
✅ **Implementation Complete**
- Frontend API function created
- Backend GET endpoint implemented
- Test script provided
- Documentation complete
- Ready for integration and testing

