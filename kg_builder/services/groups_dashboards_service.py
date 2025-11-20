"""
Service for managing Groups and Dashboards.
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import pyodbc
from kg_builder.config import get_groups_db_connection_string

logger = logging.getLogger(__name__)


class GroupsDashboardsService:
    """Service for managing groups and dashboards."""

    def __init__(self):
        """Initialize the service."""
        self.connection_string = get_groups_db_connection_string()

    def _get_connection(self):
        """Get database connection."""
        try:
            return pyodbc.connect(self.connection_string)
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    # ==================== Groups Operations ====================

    def create_group(self, code: str, name: str, description: Optional[str] = None,
                    color: Optional[str] = None, icon: Optional[str] = None,
                    is_active: bool = True, created_by: str = "system") -> Dict[str, Any]:
        """Create a new group."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO groups (code, name, description, color, icon, is_active, created_by, updated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (code, name, description, color, icon, is_active, created_by, created_by))

            conn.commit()
            group_id = cursor.lastrowid
            cursor.close()
            conn.close()

            return {"id": group_id, "code": code, "name": name, "success": True}
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
                FROM groups WHERE id = ?
            """, (group_id,))

            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                return {
                    "id": row[0],
                    "code": row[1],
                    "name": row[2],
                    "description": row[3],
                    "color": row[4],
                    "icon": row[5],
                    "is_active": row[6],
                    "created_at": row[7],
                    "updated_at": row[8]
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

            query = "SELECT id, code, name, description, color, icon, is_active, created_at, updated_at FROM groups"
            params = []

            if is_active is not None:
                query += " WHERE is_active = ?"
                params.append(is_active)

            query += " ORDER BY name"
            cursor.execute(query, params)

            groups = []
            for row in cursor.fetchall():
                groups.append({
                    "id": row[0],
                    "code": row[1],
                    "name": row[2],
                    "description": row[3],
                    "color": row[4],
                    "icon": row[5],
                    "is_active": row[6],
                    "created_at": row[7],
                    "updated_at": row[8]
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

            updates.append("updated_at = GETDATE()")
            params.append(group_id)

            query = f"UPDATE groups SET {', '.join(updates)} WHERE id = ?"
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

            cursor.execute("DELETE FROM groups WHERE id = ?", (group_id,))
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
            import json
            conn = self._get_connection()
            cursor = conn.cursor()

            layout_json = json.dumps(layout) if layout else None
            widgets_json = json.dumps(widgets) if widgets else None

            cursor.execute("""
                INSERT INTO dashboards (code, name, description, layout, widgets, is_active, created_by, updated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (code, name, description, layout_json, widgets_json, is_active, created_by, created_by))

            conn.commit()
            dashboard_id = cursor.lastrowid
            cursor.close()
            conn.close()

            return {"id": dashboard_id, "code": code, "name": name, "success": True}
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            raise

    def get_dashboard(self, dashboard_id: int) -> Optional[Dict[str, Any]]:
        """Get a dashboard by ID."""
        try:
            import json
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
                return {
                    "id": row[0],
                    "code": row[1],
                    "name": row[2],
                    "description": row[3],
                    "layout": json.loads(row[4]) if row[4] else None,
                    "widgets": json.loads(row[5]) if row[5] else None,
                    "is_active": row[6],
                    "created_at": row[7],
                    "updated_at": row[8]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting dashboard: {e}")
            raise

    def list_dashboards(self, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        """List dashboards (independent of groups)."""
        try:
            import json
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
            cursor.execute(query, params)

            dashboards = []
            for row in cursor.fetchall():
                dashboards.append({
                    "id": row[0],
                    "code": row[1],
                    "name": row[2],
                    "description": row[3],
                    "layout": json.loads(row[4]) if row[4] else None,
                    "widgets": json.loads(row[5]) if row[5] else None,
                    "is_active": row[6],
                    "created_at": row[7],
                    "updated_at": row[8]
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
            import json
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


def get_groups_dashboards_service() -> GroupsDashboardsService:
    """Get or create the service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = GroupsDashboardsService()
    return _service_instance

