"""
Service for managing Groups and Dashboards using JDBC connections.
This version uses JDBC (jaydebeapi) instead of ODBC/pymysql for database connectivity.
"""
import logging
from typing import List, Optional, Dict, Any
import json

try:
    import jaydebeapi  # noqa: F401
    JAYDEBEAPI_AVAILABLE = True
except ImportError:
    JAYDEBEAPI_AVAILABLE = False
    logging.warning("JayDeBeApi not installed. Database execution will not be available.")

from kg_builder.config import (
    GROUPS_DB_TYPE, GROUPS_DB_HOST, GROUPS_DB_PORT, GROUPS_DB_DATABASE,
    GROUPS_DB_USERNAME, GROUPS_DB_PASSWORD
)
from kg_builder.services.jdbc_connection_manager import get_jdbc_connection

logger = logging.getLogger(__name__)


class GroupsDashboardsServiceJDBC:
    """Service for managing groups and dashboards using JDBC."""

    def __init__(self):
        """Initialize the service."""
        self.host = GROUPS_DB_HOST
        self.port = GROUPS_DB_PORT
        self.database = GROUPS_DB_DATABASE
        self.username = GROUPS_DB_USERNAME
        self.password = GROUPS_DB_PASSWORD
        self.db_type = GROUPS_DB_TYPE.lower()
        
        logger.info(f"Groups/Dashboards Service initialized for {self.db_type} at {self.host}:{self.port}/{self.database}")

    def _get_connection(self):
        """Get JDBC database connection."""
        if not JAYDEBEAPI_AVAILABLE:
            raise Exception("jaydebeapi is not available - cannot connect to database")

        try:
            # Build JDBC URL based on database type
            if self.db_type in ['sqlserver', 'mssql']:
                # Handle named SQL Server instances (contains backslash)
                if '\\' in self.host:
                    # Named instance - use instance name, not port
                    jdbc_url = f"jdbc:sqlserver://{self.host};databaseName={self.database};encrypt=true;trustServerCertificate=true"
                else:
                    # Default instance or IP - include port
                    jdbc_url = f"jdbc:sqlserver://{self.host}:{self.port};databaseName={self.database};encrypt=true;trustServerCertificate=true"
                driver_class = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
            elif self.db_type == "mysql":
                jdbc_url = f"jdbc:mysql://{self.host}:{self.port}/{self.database}?connectTimeout=60000&socketTimeout=120000&autoReconnect=true"
                driver_class = "com.mysql.cj.jdbc.Driver"
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            logger.debug(f"JDBC URL: {jdbc_url}")
            logger.debug(f"Driver class: {driver_class}")
            
            # Use centralized JDBC connection manager
            conn = get_jdbc_connection(driver_class, jdbc_url, self.username, self.password)

            if not conn:
                raise Exception("Failed to get JDBC connection from connection manager")

            # Disable autocommit to allow manual transaction control
            conn.jconn.setAutoCommit(False)

            return conn
            
        except Exception as e:
            logger.error(f"Failed to connect to {self.db_type} database: {e}")
            raise

    def _convert_java_types(self, value):
        """Convert Java types to Python types."""
        from kg_builder.utils.java_type_converter import convert_java_types
        return convert_java_types(value)

    def _convert_row_to_dict(self, row, columns):
        """Convert a database row to a dictionary with proper type conversion."""
        result = {}
        for i, col_name in enumerate(columns):
            result[col_name] = self._convert_java_types(row[i])
        return result

    # ==================== Groups Operations ====================

    def create_group(self, code: str, name: str, description: Optional[str] = None,
                    color: Optional[str] = None, icon: Optional[str] = None,
                    is_active: bool = True, created_by: str = "system") -> Dict[str, Any]:
        """Create a new group."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO `groups` (code, name, description, color, icon, is_active, created_by, updated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (code, name, description, color, icon, is_active, created_by, created_by))

            conn.commit()

            # Get the last inserted ID
            if self.db_type == 'mysql':
                cursor.execute("SELECT LAST_INSERT_ID()")
            else:  # SQL Server
                cursor.execute("SELECT SCOPE_IDENTITY()")

            group_id = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            return {"id": int(group_id), "code": code, "name": name, "success": True}
        except Exception as e:
            logger.error(f"Error creating group: {e}")
            raise

    def get_group(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Get a group by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, code, name, description, color, icon, is_active, created_at, updated_at
                FROM `groups` WHERE id = ?
            """, (group_id,))

            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                return {
                    "id": self._convert_java_types(row[0]),
                    "code": self._convert_java_types(row[1]),
                    "name": self._convert_java_types(row[2]),
                    "description": self._convert_java_types(row[3]),
                    "color": self._convert_java_types(row[4]),
                    "icon": self._convert_java_types(row[5]),
                    "is_active": self._convert_java_types(row[6]),
                    "created_at": self._convert_java_types(row[7]),
                    "updated_at": self._convert_java_types(row[8])
                }
            return None
        except Exception as e:
            logger.error(f"Error getting group: {e}")
            raise

    def list_groups(self, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        """List all groups."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = "SELECT id, code, name, description, color, icon, is_active, created_at, updated_at FROM `groups`"
            params = []

            if is_active is not None:
                query += " WHERE is_active = ?"
                params.append(is_active)

            query += " ORDER BY name"
            cursor.execute(query, params if params else None)

            groups = []
            for row in cursor.fetchall():
                groups.append({
                    "id": self._convert_java_types(row[0]),
                    "code": self._convert_java_types(row[1]),
                    "name": self._convert_java_types(row[2]),
                    "description": self._convert_java_types(row[3]),
                    "color": self._convert_java_types(row[4]),
                    "icon": self._convert_java_types(row[5]),
                    "is_active": self._convert_java_types(row[6]),
                    "created_at": self._convert_java_types(row[7]),
                    "updated_at": self._convert_java_types(row[8])
                })

            cursor.close()
            conn.close()
            return groups
        except Exception as e:
            logger.error(f"Error listing groups: {e}")
            raise

    def update_group(self, group_id: int, **kwargs) -> Dict[str, Any]:
        """Update a group."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            updates = []
            params = []

            for key, value in kwargs.items():
                if key in ["code", "name", "description", "color", "icon", "is_active"]:
                    updates.append(f"{key} = ?")
                    params.append(value)

            if not updates:
                return {"success": False, "error": "No fields to update"}

            # Use appropriate timestamp function based on database type
            if self.db_type == 'mysql':
                updates.append("updated_at = NOW()")
            else:
                updates.append("updated_at = GETDATE()")
            params.append(group_id)

            query = f"UPDATE `groups` SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            cursor.close()
            conn.close()

            return {"success": True, "id": group_id}
        except Exception as e:
            logger.error(f"Error updating group: {e}")
            raise

    def delete_group(self, group_id: int) -> Dict[str, Any]:
        """Delete a group."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM `groups` WHERE id = ?", (group_id,))
            conn.commit()
            cursor.close()
            conn.close()

            return {"success": True, "id": group_id}
        except Exception as e:
            logger.error(f"Error deleting group: {e}")
            raise

    # ==================== Dashboards Operations ====================

    def create_dashboard(self, code: str, name: str, description: Optional[str] = None,
                        layout: Optional[Dict[str, Any]] = None,
                        widgets: Optional[List[Dict[str, Any]]] = None,
                        is_active: bool = True, created_by: str = "system") -> Dict[str, Any]:
        """Create a new dashboard (independent of groups)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            layout_json = json.dumps(layout) if layout else None
            widgets_json = json.dumps(widgets) if widgets else None

            cursor.execute("""
                INSERT INTO dashboards (code, name, description, layout, widgets, is_active, created_by, updated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (code, name, description, layout_json, widgets_json, is_active, created_by, created_by))

            conn.commit()

            # Get the last inserted ID
            if self.db_type == 'mysql':
                cursor.execute("SELECT LAST_INSERT_ID()")
            else:  # SQL Server
                cursor.execute("SELECT SCOPE_IDENTITY()")

            dashboard_id = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            return {"id": int(dashboard_id), "code": code, "name": name, "success": True}
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            raise

    def get_dashboard(self, dashboard_id: int) -> Optional[Dict[str, Any]]:
        """Get a dashboard by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, code, name, description, layout, widgets, is_active, created_at, updated_at
                FROM dashboards
                WHERE id = ?
            """, (dashboard_id,))

            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                layout_str = self._convert_java_types(row[4])
                widgets_str = self._convert_java_types(row[5])

                return {
                    "id": self._convert_java_types(row[0]),
                    "code": self._convert_java_types(row[1]),
                    "name": self._convert_java_types(row[2]),
                    "description": self._convert_java_types(row[3]),
                    "layout": json.loads(layout_str) if layout_str else None,
                    "widgets": json.loads(widgets_str) if widgets_str else None,
                    "is_active": self._convert_java_types(row[6]),
                    "created_at": self._convert_java_types(row[7]),
                    "updated_at": self._convert_java_types(row[8])
                }
            return None
        except Exception as e:
            logger.error(f"Error getting dashboard: {e}")
            raise

    def list_dashboards(self, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        """List dashboards (independent of groups)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = """
                SELECT id, code, name, description, layout, widgets, is_active, created_at, updated_at
                FROM dashboards
                WHERE 1=1
            """
            params = []

            if is_active is not None:
                query += " AND is_active = ?"
                params.append(is_active)

            query += " ORDER BY created_at DESC"
            cursor.execute(query, params if params else None)

            dashboards = []
            for row in cursor.fetchall():
                layout_str = self._convert_java_types(row[4])
                widgets_str = self._convert_java_types(row[5])

                dashboards.append({
                    "id": self._convert_java_types(row[0]),
                    "code": self._convert_java_types(row[1]),
                    "name": self._convert_java_types(row[2]),
                    "description": self._convert_java_types(row[3]),
                    "layout": json.loads(layout_str) if layout_str else None,
                    "widgets": json.loads(widgets_str) if widgets_str else None,
                    "is_active": self._convert_java_types(row[6]),
                    "created_at": self._convert_java_types(row[7]),
                    "updated_at": self._convert_java_types(row[8])
                })

            cursor.close()
            conn.close()
            return dashboards
        except Exception as e:
            logger.error(f"Error listing dashboards: {e}")
            raise

    def update_dashboard(self, dashboard_id: int, **kwargs) -> Dict[str, Any]:
        """Update a dashboard."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            updates = []
            params = []

            for key, value in kwargs.items():
                if key in ["code", "name", "description", "is_active"]:
                    updates.append(f"{key} = ?")
                    params.append(value)
                elif key in ["layout", "widgets"]:
                    updates.append(f"{key} = ?")
                    params.append(json.dumps(value) if value else None)

            if not updates:
                return {"success": False, "error": "No fields to update"}

            # Use appropriate timestamp function based on database type
            if self.db_type == 'mysql':
                updates.append("updated_at = NOW()")
            else:
                updates.append("updated_at = GETDATE()")
            params.append(dashboard_id)

            query = f"UPDATE dashboards SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            cursor.close()
            conn.close()

            return {"success": True, "id": dashboard_id}
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
            raise

    def delete_dashboard(self, dashboard_id: int) -> Dict[str, Any]:
        """Delete a dashboard."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM dashboards WHERE id = ?", (dashboard_id,))
            conn.commit()
            cursor.close()
            conn.close()

            return {"success": True, "id": dashboard_id}
        except Exception as e:
            logger.error(f"Error deleting dashboard: {e}")
            raise


# Singleton instance
_service_instance = None


def get_groups_dashboards_service() -> GroupsDashboardsServiceJDBC:
    """Get or create the service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = GroupsDashboardsServiceJDBC()
    return _service_instance

