# JDBC Database Connection Integration

## Overview
This document describes the JDBC-based database connection management system that allows users to connect to multiple database sources and retrieve metadata (databases, tables, columns) through the web interface.

## Backend Implementation

### New Router: `kg_builder/routers/database_router.py`
A new FastAPI router has been created to handle database connection management using JDBC.

#### Supported Database Types
- **MySQL** (Port 3306)
- **PostgreSQL** (Port 5432)
- **SQL Server** (Port 1433)
- **Oracle** (Port 1521)

#### API Endpoints

All endpoints are prefixed with `/v1/database/`

1. **POST /database/test-connection**
   - Test a database connection before adding it
   - Request: `DatabaseConnectionRequest`
   - Response: `{success: bool, message: string}`

2. **POST /database/connections**
   - Add a new database connection
   - Request: `DatabaseConnectionRequest`
   - Response: `{success: bool, connection: DatabaseConnectionResponse, message: string}`

3. **GET /database/connections**
   - List all saved database connections
   - Response: `{success: bool, connections: [DatabaseConnectionResponse], count: int}`

4. **DELETE /database/connections/{connection_id}**
   - Remove a database connection
   - Response: `{success: bool, message: string}`

5. **GET /database/connections/{connection_id}/databases**
   - Retrieve list of databases/schemas from a connection using JDBC
   - Response: `{success: bool, databases: [string], count: int}`

6. **GET /database/connections/{connection_id}/databases/{database_name}/tables**
   - List all tables in a specific database
   - Response: `{success: bool, tables: [string], count: int}`

7. **GET /database/connections/{connection_id}/databases/{database_name}/tables/{table_name}/columns**
   - Get column information for a specific table
   - Response: `{success: bool, columns: [ColumnInfo], count: int}`

#### Data Models

**DatabaseConnectionRequest**
```python
{
    "name": str,              # Friendly name for the connection
    "type": str,              # mysql, postgresql, sqlserver, oracle
    "host": str,              # Database host
    "port": int,              # Database port
    "database": str,          # Database name (optional for listing databases)
    "username": str,          # Database username
    "password": str,          # Database password
    "service_name": str       # Oracle service name (optional)
}
```

**DatabaseConnectionResponse**
```python
{
    "id": str,                # Unique connection ID (UUID)
    "name": str,              # Connection name
    "type": str,              # Database type
    "host": str,              # Host
    "port": int,              # Port
    "database": str,          # Database name
    "username": str,          # Username
    "status": str,            # "connected" or "disconnected"
    "service_name": str       # Oracle service name (optional)
}
```

### JDBC Connection Management

The router uses the centralized JDBC connection manager (`kg_builder/services/jdbc_connection_manager.py`) which:
- Initializes JVM with all JDBC drivers on startup
- Manages JDBC driver classpath
- Provides connection pooling capabilities

### Database-Specific Queries

**MySQL:**
- List databases: `SHOW DATABASES`
- List tables: `SHOW TABLES FROM database_name`
- Get columns: `DESCRIBE table_name`

**PostgreSQL:**
- List databases: `SELECT datname FROM pg_database WHERE datistemplate = false`
- List tables: Query `information_schema.tables`
- Get columns: Query `information_schema.columns`

**SQL Server:**
- List databases: `SELECT name FROM sys.databases WHERE database_id > 4`
- List tables: Query `INFORMATION_SCHEMA.TABLES`
- Get columns: Query `INFORMATION_SCHEMA.COLUMNS`

**Oracle:**
- List schemas: `SELECT username FROM all_users ORDER BY username`
- List tables: `SELECT table_name FROM all_tables WHERE owner = ?`
- Get columns: `SELECT * FROM all_tab_columns WHERE owner = ? AND table_name = ?`

## Frontend Integration

### Updated Components

**web-app/src/components/schema-wizard/DatabaseConnectionsStep.js**
- Added `service_name` field to form data
- Added conditional Oracle service name input field
- Integrated with backend API endpoints

**web-app/src/services/api.js**
- Already configured with correct `/v1` base URL
- All database connection API functions are properly defined

### UI Features

1. **Connection Management**
   - Add new database connections with test functionality
   - View all saved connections with status indicators
   - Remove connections
   - Refresh database list for each connection

2. **Oracle Support**
   - Conditional service name field appears only for Oracle connections
   - Supports both SID and Service Name connection methods

3. **Visual Feedback**
   - Connection status chips (Connected/Disconnected)
   - Database count display for each connection
   - Loading indicators during operations
   - Snackbar notifications for success/error messages

## Registration

The database router is registered in `kg_builder/main.py`:
```python
from kg_builder.routers.database_router import router as database_router
app.include_router(database_router, prefix="/v1", tags=["Database Connections"])
```

## Testing

To test the implementation:

1. Start the backend server
2. Navigate to the Schema Wizard in the web interface
3. Click "New Connection" to add a database
4. Fill in connection details and click "Test Connection"
5. If successful, click "Add Connection"
6. The connection will appear in the list with available databases count
7. Use the refresh button to reload databases from the connection

## Security Considerations

⚠️ **Important**: The current implementation stores database credentials in memory. For production use:
- Implement secure credential storage (encrypted database or secrets manager)
- Add authentication/authorization for API endpoints
- Use connection pooling with timeout management
- Implement rate limiting for connection attempts
- Add audit logging for connection operations

