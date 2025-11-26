"""
Database Connection Management Router
Provides endpoints for managing database connections and retrieving metadata using JDBC.
"""
import logging
import uuid
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from kg_builder.services.jdbc_connection_manager import get_jdbc_connection, ensure_jvm_initialized

logger = logging.getLogger(__name__)

router = APIRouter()

# Storage directory for database connections (persisted to disk)
DB_CONNECTIONS_DIR = Path("database_connections")
DB_CONNECTIONS_DIR.mkdir(exist_ok=True)
DB_CONNECTIONS_FILE = DB_CONNECTIONS_DIR / "connections.json"

# In-memory cache for database connections (loaded from disk on startup)
_connections: Dict[str, Dict[str, Any]] = {}

# Storage directory for schema configurations
SCHEMA_CONFIG_DIR = Path("schema_configurations")
SCHEMA_CONFIG_DIR.mkdir(exist_ok=True)

# Audit columns to exclude from column listing
# These are common audit/metadata columns that should not be used in schema wizard or data quality operations
AUDIT_COLUMNS = {
    # Timestamp audit columns
    "created_at", "created_date", "created_time", "creation_date", "creation_time",
    "updated_at", "updated_date", "updated_time", "update_date", "update_time",
    "modified_at", "modified_date", "modified_time", "modification_date", "modification_time",
    "deleted_at", "deleted_date", "deleted_time", "deletion_date", "deletion_time",
    # User audit columns
    "created_by", "creator", "created_user", "creation_user",
    "updated_by", "updater", "updated_user", "update_user", "modifier",
    "modified_by", "modified_user", "modification_user",
    "deleted_by", "deleter", "deleted_user", "deletion_user",
    # Other common audit columns
    "last_modified", "last_modified_by", "last_modified_date", "last_modified_time",
    "last_updated", "last_updated_by", "last_updated_date", "last_updated_time",
    "insert_date", "insert_time", "insert_user", "inserted_by",
    "change_date", "change_time", "change_user", "changed_by",
    # System metadata columns
    "row_version", "version", "timestamp", "rowversion",
    "audit_timestamp", "audit_user", "audit_date",
    # Soft delete columns
    "is_deleted", "deleted", "is_active", "active",
}


# ==================== Connection Persistence Functions ====================

def _load_connections_from_disk():
    """Load database connections from disk on startup."""
    global _connections
    try:
        if DB_CONNECTIONS_FILE.exists():
            with open(DB_CONNECTIONS_FILE, 'r') as f:
                _connections = json.load(f)
            logger.info(f"✅ Loaded {len(_connections)} database connection(s) from disk")
        else:
            logger.info("No existing connections file found. Starting with empty connections.")
    except Exception as e:
        logger.error(f"Failed to load connections from disk: {e}")
        _connections = {}


def _save_connections_to_disk():
    """Save database connections to disk."""
    try:
        with open(DB_CONNECTIONS_FILE, 'w') as f:
            json.dump(_connections, f, indent=2)
        logger.debug(f"💾 Saved {len(_connections)} connection(s) to disk")
    except Exception as e:
        logger.error(f"Failed to save connections to disk: {e}")


# Load connections on module import
_load_connections_from_disk()


class DatabaseConnectionRequest(BaseModel):
    """Request model for adding a database connection."""
    name: str = Field(..., description="Friendly name for the connection")
    type: str = Field(..., description="Database type: mysql, postgresql, sqlserver, oracle")
    host: str = Field(..., description="Database host")
    port: int = Field(..., description="Database port")
    database: str = Field(default="", description="Database name (optional for listing databases)")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    service_name: Optional[str] = Field(default=None, description="Oracle service name (if applicable)")


class DatabaseConnectionResponse(BaseModel):
    """Response model for database connection."""
    id: str
    name: str
    type: str
    host: str
    port: int
    database: str
    username: str
    status: str
    service_name: Optional[str] = None


class ColumnConfiguration(BaseModel):
    """Configuration for a column with aliases."""
    name: str
    aliases: List[str] = []


class TableConfiguration(BaseModel):
    """Configuration for a table with selected columns and aliases."""
    connectionId: str
    connectionName: str
    databaseName: str
    tableName: str
    tableAliases: List[str] = []
    primaryAlias: Optional[str] = Field(
        None,
        description="The primary/canonical alias selected by the user from the tableAliases list"
    )
    columns: List[ColumnConfiguration] = []


class SchemaConfigurationRequest(BaseModel):
    """Request model for saving schema configuration."""
    schemaName: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the schema configuration"
    )
    tables: List[TableConfiguration]


def _is_audit_column(column_name: str) -> bool:
    """
    Check if a column is an audit column that should be excluded.

    Args:
        column_name: Name of the column to check

    Returns:
        bool: True if the column is an audit column, False otherwise
    """
    return column_name.lower() in AUDIT_COLUMNS


def _get_driver_class(db_type: str) -> str:
    """Get JDBC driver class for database type."""
    drivers = {
        "mysql": "com.mysql.cj.jdbc.Driver",
        "postgresql": "org.postgresql.Driver",
        "sqlserver": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
        "oracle": "oracle.jdbc.OracleDriver"
    }
    driver = drivers.get(db_type.lower())
    if not driver:
        raise ValueError(f"Unsupported database type: {db_type}")
    return driver


def _build_jdbc_url(db_type: str, host: str, port: int, database: str, service_name: Optional[str] = None) -> str:
    """Build JDBC URL for database connection."""
    db_type = db_type.lower()

    if db_type == "mysql":
        # For MySQL, if database is empty, connect to default (no database specified)
        db_part = f"/{database}" if database else ""
        return f"jdbc:mysql://{host}:{port}{db_part}?useSSL=false&allowPublicKeyRetrieval=true"
    elif db_type == "postgresql":
        # For PostgreSQL, if database is empty, connect to 'postgres' default database
        db_name = database if database else "postgres"
        return f"jdbc:postgresql://{host}:{port}/{db_name}"
    elif db_type == "sqlserver":
        # For SQL Server, if database is empty, connect to master
        db_name = database if database else "master"
        return f"jdbc:sqlserver://{host}:{port};databaseName={db_name};trustServerCertificate=true"
    elif db_type == "oracle":
        if service_name:
            return f"jdbc:oracle:thin:@//{host}:{port}/{service_name}"
        else:
            return f"jdbc:oracle:thin:@{host}:{port}:{database}"
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


@router.post("/database/test-connection")
async def test_database_connection(request: DatabaseConnectionRequest):
    """Test a database connection."""
    try:
        # Ensure JVM is initialized
        if not ensure_jvm_initialized():
            raise HTTPException(status_code=500, detail="Failed to initialize JDBC drivers")

        driver_class = _get_driver_class(request.type)
        jdbc_url = _build_jdbc_url(request.type, request.host, request.port, request.database, request.service_name)

        logger.info(f"Testing connection to {request.type} at {request.host}:{request.port}")
        logger.info(f"JDBC URL: {jdbc_url}")
        logger.info(f"Driver class: {driver_class}")

        # Try to connect
        conn = get_jdbc_connection(driver_class, jdbc_url, request.username, request.password)

        if conn:
            conn.close()
            return {
                "success": True,
                "message": f"Successfully connected to {request.type} database at {request.host}:{request.port}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to establish connection")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Connection test failed: {e}", exc_info=True)
        error_msg = str(e)

        # Provide helpful error messages
        if "Communications link failure" in error_msg or "Connection refused" in error_msg:
            # Special handling for SQL Server TCP/IP issues
            if request.type == "sqlserver" and "Connection refused" in error_msg:
                raise HTTPException(
                    status_code=500,
                    detail=f"Cannot connect to SQL Server at {request.host}:{request.port}. "
                           f"SQL Server may not be configured to accept TCP/IP connections on this port. "
                           f"Please enable TCP/IP protocol in SQL Server Configuration Manager and ensure port {request.port} is configured. "
                           f"See SQL_SERVER_TCP_IP_SETUP.md for detailed instructions."
                )
            else:
                raise HTTPException(status_code=500, detail=f"Cannot connect to {request.host}:{request.port}. Check if database is running and port is correct.")
        elif "Access denied" in error_msg or "authentication failed" in error_msg or "Login failed" in error_msg:
            raise HTTPException(status_code=500, detail=f"Authentication failed. Check username and password. For SQL Server, use 'sa' or a valid SQL Server login (not 'root').")
        elif "Unknown database" in error_msg or "Cannot open database" in error_msg:
            raise HTTPException(status_code=500, detail=f"Database '{request.database}' does not exist or you don't have permission to access it.")
        else:
            raise HTTPException(status_code=500, detail=f"Connection failed: {error_msg}")


@router.post("/database/connections")
async def add_database_connection(request: DatabaseConnectionRequest):
    """Add a new database connection."""
    try:
        # Ensure JVM is initialized
        if not ensure_jvm_initialized():
            raise HTTPException(status_code=500, detail="Failed to initialize JDBC drivers")

        # Test the connection first
        driver_class = _get_driver_class(request.type)
        jdbc_url = _build_jdbc_url(request.type, request.host, request.port, request.database, request.service_name)

        logger.info(f"Adding connection '{request.name}' - {request.type} at {request.host}:{request.port}")
        logger.info(f"JDBC URL: {jdbc_url}")

        conn = get_jdbc_connection(driver_class, jdbc_url, request.username, request.password)

        if not conn:
            raise HTTPException(status_code=500, detail="Failed to establish connection")

        conn.close()
        logger.info(f"Connection test successful for '{request.name}'")

        # Generate unique ID
        connection_id = str(uuid.uuid4())

        # Store connection info
        _connections[connection_id] = {
            "id": connection_id,
            "name": request.name,
            "type": request.type,
            "host": request.host,
            "port": request.port,
            "database": request.database,
            "username": request.username,
            "password": request.password,
            "service_name": request.service_name,
            "status": "connected"
        }

        # Persist to disk
        _save_connections_to_disk()

        connection_response = DatabaseConnectionResponse(**_connections[connection_id])

        logger.info(f"Connection '{request.name}' added successfully with ID: {connection_id}")

        return {
            "success": True,
            "connection": connection_response,
            "message": "Connection added successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add connection: {e}", exc_info=True)
        error_msg = str(e)

        # Provide helpful error messages
        if "Communications link failure" in error_msg or "Connection refused" in error_msg:
            # Special handling for SQL Server TCP/IP issues
            if request.type == "sqlserver" and "Connection refused" in error_msg:
                raise HTTPException(
                    status_code=500,
                    detail=f"Cannot connect to SQL Server at {request.host}:{request.port}. "
                           f"SQL Server may not be configured to accept TCP/IP connections on this port. "
                           f"Please enable TCP/IP protocol in SQL Server Configuration Manager and ensure port {request.port} is configured. "
                           f"See SQL_SERVER_TCP_IP_SETUP.md for detailed instructions."
                )
            else:
                raise HTTPException(status_code=500, detail=f"Cannot connect to {request.host}:{request.port}. Check if database is running and port is correct.")
        elif "Access denied" in error_msg or "authentication failed" in error_msg or "Login failed" in error_msg:
            raise HTTPException(status_code=500, detail=f"Authentication failed. Check username and password. For SQL Server, use 'sa' or a valid SQL Server login (not 'root').")
        elif "Unknown database" in error_msg or "Cannot open database" in error_msg:
            raise HTTPException(status_code=500, detail=f"Database '{request.database}' does not exist or you don't have permission to access it.")
        else:
            raise HTTPException(status_code=500, detail=f"Failed to add connection: {error_msg}")


@router.get("/database/connections")
async def list_database_connections():
    """List all database connections."""
    try:
        connections = [
            DatabaseConnectionResponse(
                id=conn["id"],
                name=conn["name"],
                type=conn["type"],
                host=conn["host"],
                port=conn["port"],
                database=conn["database"],
                username=conn["username"],
                status=conn["status"],
                service_name=conn.get("service_name")
            )
            for conn in _connections.values()
        ]

        return {
            "success": True,
            "connections": connections,
            "count": len(connections)
        }

    except Exception as e:
        logger.error(f"Failed to list connections: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list connections: {str(e)}")


@router.delete("/database/connections/{connection_id}")
async def remove_database_connection(connection_id: str):
    """Remove a database connection."""
    try:
        if connection_id not in _connections:
            raise HTTPException(status_code=404, detail=f"Connection {connection_id} not found")

        del _connections[connection_id]

        # Persist to disk
        _save_connections_to_disk()

        return {
            "success": True,
            "message": f"Connection {connection_id} removed"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove connection: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to remove connection: {str(e)}")


@router.get("/database/connections/{connection_id}/databases")
async def list_databases_from_connection(connection_id: str):
    """List all databases from a connection using JDBC."""
    try:
        if connection_id not in _connections:
            raise HTTPException(status_code=404, detail=f"Connection {connection_id} not found")

        conn_info = _connections[connection_id]

        # Excel connections don't have databases - return empty list
        if conn_info["type"] == "excel":
            return {
                "success": True,
                "databases": [],
                "count": 0,
                "message": "Excel files do not have databases"
            }

        driver_class = _get_driver_class(conn_info["type"])

        # For listing databases, connect without specifying a database
        jdbc_url = _build_jdbc_url(
            conn_info["type"],
            conn_info["host"],
            conn_info["port"],
            "",  # Empty database name
            conn_info.get("service_name")
        )

        logger.info(f"Retrieving databases from {conn_info['type']} at {conn_info['host']}")

        conn = get_jdbc_connection(driver_class, jdbc_url, conn_info["username"], conn_info["password"])

        if not conn:
            raise HTTPException(status_code=500, detail="Failed to establish connection")

        try:
            cursor = conn.cursor()
            databases = []

            db_type = conn_info["type"].lower()

            if db_type == "mysql":
                cursor.execute("SHOW DATABASES")
                databases = [str(row[0]) for row in cursor.fetchall()]

            elif db_type == "postgresql":
                cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
                databases = [str(row[0]) for row in cursor.fetchall()]

            elif db_type == "sqlserver":
                cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4")  # Exclude system databases
                databases = [str(row[0]) for row in cursor.fetchall()]

            elif db_type == "oracle":
                # Oracle doesn't have multiple databases, but has schemas/users
                cursor.execute("SELECT username FROM all_users ORDER BY username")
                databases = [str(row[0]) for row in cursor.fetchall()]

            cursor.close()
            conn.close()

            return {
                "success": True,
                "databases": databases,
                "count": len(databases)
            }

        except Exception as e:
            conn.close()
            raise e

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list databases: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list databases: {str(e)}")


@router.get("/database/connections/{connection_id}/databases/{database_name}/tables")
async def list_tables_from_database(connection_id: str, database_name: str):
    """List all tables from a specific database using JDBC or Excel sheets."""
    try:
        if connection_id not in _connections:
            raise HTTPException(status_code=404, detail=f"Connection {connection_id} not found")

        conn_info = _connections[connection_id]

        # Handle Excel connections - read sheet names from the Excel file
        if conn_info["type"] == "excel":
            try:
                import pandas as pd
                file_path = conn_info.get("file_path")

                if not file_path or not Path(file_path).exists():
                    raise HTTPException(status_code=404, detail=f"Excel file not found: {file_path}")

                logger.info(f"Reading sheet names from Excel file: {file_path}")

                # Read Excel file and get sheet names
                excel_file = pd.ExcelFile(file_path)
                sheet_names = excel_file.sheet_names

                logger.info(f"Found {len(sheet_names)} sheets in Excel file: {sheet_names}")

                return {
                    "success": True,
                    "tables": sheet_names,
                    "count": len(sheet_names),
                    "message": "Excel sheets listed as tables"
                }

            except ImportError:
                raise HTTPException(
                    status_code=500,
                    detail="pandas library is required to read Excel files. Please install it: pip install pandas openpyxl"
                )
            except Exception as e:
                logger.error(f"Failed to read Excel file: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to read Excel file: {str(e)}")

        # Handle regular database connections
        driver_class = _get_driver_class(conn_info["type"])

        # Connect to the specific database
        jdbc_url = _build_jdbc_url(
            conn_info["type"],
            conn_info["host"],
            conn_info["port"],
            database_name,
            conn_info.get("service_name")
        )

        logger.info(f"Retrieving tables from {database_name} on {conn_info['type']}")

        conn = get_jdbc_connection(driver_class, jdbc_url, conn_info["username"], conn_info["password"])

        if not conn:
            raise HTTPException(status_code=500, detail="Failed to establish connection")

        try:
            cursor = conn.cursor()
            tables = []

            db_type = conn_info["type"].lower()

            if db_type == "mysql":
                cursor.execute(f"SHOW TABLES FROM `{database_name}`")
                tables = [str(row[0]) for row in cursor.fetchall()]

            elif db_type == "postgresql":
                cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """)
                tables = [str(row[0]) for row in cursor.fetchall()]

            elif db_type == "sqlserver":
                cursor.execute("""
                    SELECT TABLE_NAME
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG = ?
                    ORDER BY TABLE_NAME
                """, (database_name,))
                tables = [str(row[0]) for row in cursor.fetchall()]

            elif db_type == "oracle":
                # For Oracle, database_name is actually the schema/user
                cursor.execute("""
                    SELECT table_name
                    FROM all_tables
                    WHERE owner = ?
                    ORDER BY table_name
                """, (database_name.upper(),))
                tables = [str(row[0]) for row in cursor.fetchall()]

            cursor.close()
            conn.close()

            return {
                "success": True,
                "tables": tables,
                "count": len(tables)
            }

        except Exception as e:
            conn.close()
            raise e

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list tables: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list tables: {str(e)}")


@router.get("/database/connections/{connection_id}/databases/{database_name}/tables/{table_name}/columns")
async def get_table_columns(connection_id: str, database_name: str, table_name: str):
    """
    Get column information for a specific table using JDBC.

    This endpoint automatically filters out audit columns (created_at, updated_at, created_by, etc.)
    to return only columns relevant for schema wizard and data quality operations.

    Returns:
        - columns: List of non-audit columns
        - count: Number of non-audit columns
        - total_columns: Total number of columns (including audit columns)
        - excluded_audit_columns: Number of audit columns that were filtered out
    """
    try:
        if connection_id not in _connections:
            raise HTTPException(status_code=404, detail=f"Connection {connection_id} not found")

        conn_info = _connections[connection_id]
        driver_class = _get_driver_class(conn_info["type"])

        # Connect to the specific database
        jdbc_url = _build_jdbc_url(
            conn_info["type"],
            conn_info["host"],
            conn_info["port"],
            database_name,
            conn_info.get("service_name")
        )

        logger.info(f"Retrieving columns from {database_name}.{table_name} on {conn_info['type']}")

        conn = get_jdbc_connection(driver_class, jdbc_url, conn_info["username"], conn_info["password"])

        if not conn:
            raise HTTPException(status_code=500, detail="Failed to establish connection")

        try:
            cursor = conn.cursor()
            columns = []

            db_type = conn_info["type"].lower()

            if db_type == "mysql":
                cursor.execute(f"DESCRIBE `{database_name}`.`{table_name}`")
                for row in cursor.fetchall():
                    columns.append({
                        "name": str(row[0]),
                        "type": str(row[1]),
                        "nullable": str(row[2]) == "YES",
                        "key": str(row[3]) if row[3] else "",
                        "default": str(row[4]) if row[4] else None
                    })

            elif db_type == "postgresql":
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = ?
                    ORDER BY ordinal_position
                """, (table_name,))
                for row in cursor.fetchall():
                    columns.append({
                        "name": str(row[0]),
                        "type": str(row[1]),
                        "nullable": str(row[2]) == "YES",
                        "default": str(row[3]) if row[3] else None
                    })

            elif db_type == "sqlserver":
                cursor.execute("""
                    SELECT
                        c.COLUMN_NAME,
                        c.DATA_TYPE,
                        c.IS_NULLABLE,
                        c.COLUMN_DEFAULT
                    FROM INFORMATION_SCHEMA.COLUMNS c
                    WHERE c.TABLE_NAME = ? AND c.TABLE_CATALOG = ?
                    ORDER BY c.ORDINAL_POSITION
                """, (table_name, database_name))
                for row in cursor.fetchall():
                    columns.append({
                        "name": str(row[0]),
                        "type": str(row[1]),
                        "nullable": str(row[2]) == "YES",
                        "default": str(row[3]) if row[3] else None
                    })

            elif db_type == "oracle":
                cursor.execute("""
                    SELECT
                        column_name,
                        data_type,
                        nullable,
                        data_default
                    FROM all_tab_columns
                    WHERE owner = ? AND table_name = ?
                    ORDER BY column_id
                """, (database_name.upper(), table_name.upper()))
                for row in cursor.fetchall():
                    columns.append({
                        "name": str(row[0]),
                        "type": str(row[1]),
                        "nullable": str(row[2]) == "Y",
                        "default": str(row[3]) if row[3] else None
                    })

            cursor.close()
            conn.close()

            # Filter out audit columns
            total_columns = len(columns)
            filtered_columns = [col for col in columns if not _is_audit_column(col["name"])]
            excluded_count = total_columns - len(filtered_columns)

            if excluded_count > 0:
                logger.info(f"Filtered out {excluded_count} audit columns from {database_name}.{table_name}")

            return {
                "success": True,
                "columns": filtered_columns,
                "count": len(filtered_columns),
                "total_columns": total_columns,
                "excluded_audit_columns": excluded_count
            }

        except Exception as e:
            conn.close()
            raise e

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get table columns: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get table columns: {str(e)}")


@router.post("/database/schema-configuration")
async def save_schema_configuration(request: SchemaConfigurationRequest):
    """
    Save schema configuration from the Schema Wizard.

    This endpoint saves the user's selections including:
    - Schema name provided by the user
    - Selected tables from databases
    - Selected columns for each table
    - User-defined aliases for tables
    - User-defined aliases for columns

    The configuration is saved as a JSON file that can be used later
    for knowledge graph generation or other data quality operations.
    """
    try:
        # Generate a unique configuration ID
        config_id = f"schema_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        # Prepare the configuration data
        config_data = {
            "id": config_id,
            "schemaName": request.schemaName.strip(),
            "created_at": datetime.now().isoformat(),
            "tables": [table.model_dump() for table in request.tables],
            "summary": {
                "total_tables": len(request.tables),
                "total_columns": sum(len(table.columns) for table in request.tables),
                "databases": list(set(table.databaseName for table in request.tables)),
                "connections": list(set(table.connectionName for table in request.tables)),
            }
        }

        # Save to file
        config_file = SCHEMA_CONFIG_DIR / f"{config_id}.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Schema configuration saved: {config_id}")
        logger.info(f"  Schema Name: {config_data['schemaName']}")
        logger.info(f"  Tables: {config_data['summary']['total_tables']}")
        logger.info(f"  Columns: {config_data['summary']['total_columns']}")
        logger.info(f"  Databases: {', '.join(config_data['summary']['databases'])}")

        return {
            "success": True,
            "message": "Schema configuration saved successfully",
            "config_id": config_id,
            "schemaName": config_data['schemaName'],
            "summary": config_data['summary'],
            "file_path": str(config_file)
        }

    except Exception as e:
        logger.error(f"Failed to save schema configuration: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save schema configuration: {str(e)}"
        )


@router.get("/database/schema-configuration")
async def get_schema_configurations():
    """
    Retrieve all saved schema configurations.

    This endpoint returns a list of all schema configurations that have been
    saved through the Schema Wizard, including their metadata, schema names, and summaries.

    Returns:
        JSON response with:
        - success: Boolean indicating success
        - configurations: List of configuration objects with metadata including:
            - id: Unique configuration identifier
            - schemaName: User-provided name for the schema
            - created_at: Timestamp when configuration was created
            - tables: List of configured tables
            - summary: Summary statistics (total_tables, total_columns, databases, connections)
        - count: Total number of configurations
    """
    try:
        configurations = []

        # Check if directory exists
        if not SCHEMA_CONFIG_DIR.exists():
            logger.warning(f"Schema configuration directory does not exist: {SCHEMA_CONFIG_DIR}")
            return {
                "success": True,
                "configurations": [],
                "count": 0,
                "message": "No schema configurations found"
            }

        # Read all JSON files from the schema configurations directory
        for config_file in SCHEMA_CONFIG_DIR.glob("*.json"):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    configurations.append(config_data)
            except json.JSONDecodeError as je:
                logger.error(f"Failed to parse configuration file {config_file}: {je}")
                continue
            except Exception as file_error:
                logger.error(f"Error reading configuration file {config_file}: {file_error}")
                continue

        # Sort configurations by created_at timestamp (newest first)
        configurations.sort(
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )

        logger.info(f"Retrieved {len(configurations)} schema configurations")

        return {
            "success": True,
            "configurations": configurations,
            "count": len(configurations),
            "message": f"Successfully retrieved {len(configurations)} schema configuration(s)"
        }

    except Exception as e:
        logger.error(f"Failed to retrieve schema configurations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve schema configurations: {str(e)}"
        )

@router.post("/upload-excel")
async def upload_excel_file(file: UploadFile = File(...), name: str = Form(None)):
    """
    Upload an Excel file (.xlsx or .xls) and create a connection entry.

    This endpoint accepts Excel files, validates them, saves them to disk,
    and creates a connection entry that appears in the connections list.

    Args:
        file: Excel file uploaded via multipart/form-data
        name: Optional connection name (defaults to filename if not provided)

    Returns:
        JSON response with success status, message, and connection details

    Raises:
        HTTPException: If file validation fails or processing errors occur
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Check file extension
        file_extension = file.filename.lower().split('.')[-1]
        valid_extensions = ['xlsx', 'xls']

        if file_extension not in valid_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Only Excel files (.xlsx, .xls) are supported. Got: .{file_extension}"
            )

        # Validate MIME type
        valid_mime_types = [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
            'application/vnd.ms-excel',  # .xls
            'application/octet-stream'  # Sometimes browsers send this for Excel files
        ]

        if file.content_type not in valid_mime_types:
            logger.warning(f"Unexpected MIME type: {file.content_type} for file: {file.filename}")
            # Don't reject based on MIME type alone, as browsers can be inconsistent

        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of 10MB. File size: {file_size / (1024 * 1024):.2f}MB"
            )

        if file_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        # Create uploads directory if it doesn't exist
        uploads_dir = Path("uploads/excel")
        uploads_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4().hex[:8]
        safe_filename = f"excel_{timestamp}_{unique_id}.{file_extension}"
        file_path = uploads_dir / safe_filename

        # Save file to disk
        with open(file_path, 'wb') as f:
            f.write(file_content)

        logger.info(f"Excel file uploaded successfully: {file.filename} -> {safe_filename}")
        logger.info(f"File size: {file_size / 1024:.2f} KB")
        logger.info(f"Saved to: {file_path}")

        # Create connection entry
        connection_id = str(uuid.uuid4())
        connection_name = name if name and name.strip() else file.filename

        # Store connection info (similar to database connections)
        _connections[connection_id] = {
            "id": connection_id,
            "name": connection_name,
            "type": "excel",
            "host": "local",
            "port": 0,
            "database": safe_filename,  # Store the saved filename
            "username": "",
            "password": "",
            "service_name": None,
            "status": "connected",
            "file_path": str(file_path),
            "original_filename": file.filename,
            "file_size_kb": round(file_size / 1024, 2),
            "uploaded_at": timestamp
        }

        # Persist to disk
        _save_connections_to_disk()

        logger.info(f"Excel connection '{connection_name}' created with ID: {connection_id}")

        # Create response matching DatabaseConnectionResponse format
        connection_response = {
            "id": connection_id,
            "name": connection_name,
            "type": "excel",
            "host": "local",
            "port": 0,
            "database": safe_filename,
            "username": "",
            "status": "connected",
            "service_name": None
        }

        return {
            "success": True,
            "message": f"Excel file '{file.filename}' uploaded successfully and connection created",
            "connection": connection_response,
            "file_name": file.filename,
            "saved_as": safe_filename,
            "file_size_kb": round(file_size / 1024, 2),
            "file_path": str(file_path),
            "timestamp": timestamp
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload Excel file: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload Excel file: {str(e)}"
        )


