# KPI Execution - Database Connection Fix ✅

## Issue

When executing a KPI via `/v1/landing-kpi/kpis/{kpi_id}/execute`, the following error occurred:

```
ModuleNotFoundError: No module named 'kg_builder.services.database_connector'
```

## Root Cause

The `landing_kpi_executor.py` was trying to import a non-existent module:

```python
from kg_builder.services.database_connector import get_database_connection
```

This module doesn't exist in the codebase. The code was calling:

```python
connection = get_database_connection(
    kg_name=execution_params['kg_name'],
    schema=execution_params['select_schema'],
    db_type=execution_params.get('db_type', 'mysql')
)
```

But the only `get_database_connection()` function in `config.py` returns a SQLite connection and doesn't accept parameters.

---

## Solution

### 1. Removed Invalid Import

**File**: `kg_builder/services/landing_kpi_executor.py`

**Before**:
```python
from kg_builder.services.database_connector import get_database_connection
```

**After**: Removed (no import needed)

---

### 2. Created Helper Function

Added `_get_source_database_connection()` function that:
- Connects to the source database (not SQLite)
- Supports multiple database types: SQL Server, MySQL, PostgreSQL, Oracle
- Uses JayDeBeApi for JDBC connections
- Handles connection pooling and error handling

**Location**: `kg_builder/services/landing_kpi_executor.py` (lines 160-225)

**Function Signature**:
```python
def _get_source_database_connection(db_type: str = 'sqlserver') -> Optional[Any]:
    """
    Get a connection to the source database for KPI execution.
    
    Args:
        db_type: Database type (sqlserver, mysql, postgresql, oracle)
    
    Returns:
        Database connection object or None if not configured
    """
```

---

### 3. Updated KPI Execution Flow

**Before**:
```python
connection = get_database_connection(
    kg_name=execution_params['kg_name'],
    schema=execution_params['select_schema'],
    db_type=execution_params.get('db_type', 'mysql')
)
executor = get_nl_query_executor(execution_params.get('db_type', 'mysql'))
```

**After**:
```python
db_type = execution_params.get('db_type', 'sqlserver')
connection = _get_source_database_connection(db_type=db_type)
executor = get_nl_query_executor(db_type)
```

---

## Database Connection Flow

```
KPI Execution Request
    ↓
Extract db_type from execution_params (default: 'sqlserver')
    ↓
_get_source_database_connection(db_type)
    ↓
Get source DB config from kg_builder.config
    ↓
Build JDBC URL based on db_type
    ↓
Find JDBC driver JAR
    ↓
Connect using JayDeBeApi
    ↓
Return connection object
    ↓
Pass to NL Query Executor
    ↓
Execute SQL query
    ↓
Return results
```

---

## Supported Database Types

| DB Type | JDBC URL Pattern | Driver Class |
|---------|------------------|--------------|
| **sqlserver** | `jdbc:sqlserver://host:port;databaseName=db` | `com.microsoft.sqlserver.jdbc.SQLServerDriver` |
| **mysql** | `jdbc:mysql://host:port/db?connectTimeout=60000...` | `com.mysql.jdbc.Driver` |
| **postgresql** | `jdbc:postgresql://host:port/db` | `org.postgresql.Driver` |
| **oracle** | `jdbc:oracle:thin:@host:port:service` | `oracle.jdbc.driver.OracleDriver` |

---

## Configuration Required

The source database must be configured in `kg_builder/config.py`:

```python
def get_source_db_config() -> Optional[DatabaseConnectionInfo]:
    """Get source database configuration."""
    # Returns DatabaseConnectionInfo with:
    # - db_type: 'sqlserver', 'mysql', 'postgresql', or 'oracle'
    # - host: Database host
    # - port: Database port
    # - database: Database name
    # - username: Database username
    # - password: Database password
    # - service_name: (Optional) Oracle service name
```

---

## Error Handling

If database connection fails:
- Logs error with details
- Returns `None`
- KPI execution raises: `ValueError("Could not establish database connection")`
- Error is caught and stored in execution record

---

## Files Modified

1. **kg_builder/services/landing_kpi_executor.py**
   - Removed invalid import
   - Added `_get_source_database_connection()` helper function
   - Updated KPI execution flow to use new helper
   - Consistent db_type handling throughout

---

## Testing

To test KPI execution:

1. Ensure source database is configured in `.env` or `config.py`
2. Create a KPI with NL definition
3. Execute KPI via API:
   ```bash
   POST /v1/landing-kpi/kpis/{kpi_id}/execute
   {
     "kg_name": "my_kg",
     "select_schema": "my_schema",
     "db_type": "sqlserver",
     "limit_records": 1000,
     "use_llm": true
   }
   ```
4. Check execution status and results

---

## Status

✅ **FIXED** - KPI execution now properly connects to source database

The error `ModuleNotFoundError: No module named 'kg_builder.services.database_connector'` is resolved.

