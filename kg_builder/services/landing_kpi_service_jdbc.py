"""
Landing KPI Service using JDBC (Working Alternative to pyodbc)
Uses the existing JDBC infrastructure that's already working in the system.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import glob
import os
import json

try:
    import jaydebeapi
    JAYDEBEAPI_AVAILABLE = True
except ImportError:
    JAYDEBEAPI_AVAILABLE = False
    logging.warning("JayDeBeApi not installed. Database execution will not be available.")

from kg_builder.config import (
    KPI_DB_HOST, KPI_DB_PORT, KPI_DB_DATABASE,
    KPI_DB_USERNAME, KPI_DB_PASSWORD, KPI_DB_TYPE,
    JDBC_DRIVERS_PATH
)

logger = logging.getLogger(__name__)


class LandingKPIServiceJDBC:
    """Landing KPI Service using JDBC connections (like the rest of the system)."""

    @staticmethod
    def _to_bool(value):
        """Convert database value to boolean safely."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)

    @staticmethod
    def _convert_java_types(value):
        """Convert Java types to Python types for JSON serialization."""
        from kg_builder.utils.java_type_converter import convert_java_types
        return convert_java_types(value)

    def _convert_response(self, data):
        """Convert all Java objects in response data to Python objects."""
        from kg_builder.utils.java_type_converter import convert_java_dict, convert_java_list

        if isinstance(data, dict):
            return convert_java_dict(data)
        elif isinstance(data, list):
            return convert_java_list(data)
        else:
            return self._convert_java_types(data)

    def __init__(self, database: str = None):
        """Initialize with JDBC connection to KPI database."""
        self.host = KPI_DB_HOST
        self.port = KPI_DB_PORT
        self.database = database or KPI_DB_DATABASE  # Use KPI-specific database
        self.username = KPI_DB_USERNAME
        self.password = KPI_DB_PASSWORD
        self.db_type = KPI_DB_TYPE

        logger.info(f"KPI Service initialized for {self.db_type} at {self.host}:{self.port}/{self.database}")
    
    def _get_connection(self):
        """Get JDBC database connection (same as other services use)."""
        if not JAYDEBEAPI_AVAILABLE:
            raise Exception("jaydebeapi is not available - cannot connect to database")

        try:
            # Build JDBC URL
            if self.db_type.lower() in ['sqlserver', 'mssql']:
                jdbc_url = f"jdbc:sqlserver://{self.host}:{self.port};databaseName={self.database};encrypt=true;trustServerCertificate=true"
                driver_class = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
                jar_pattern = "mssql-jdbc*.jar"
            elif self.db_type.lower() == "mysql":
                jdbc_url = f"jdbc:mysql://{self.host}:{self.port}/{self.database}?connectTimeout=60000&socketTimeout=120000&autoReconnect=true"
                driver_class = "com.mysql.cj.jdbc.Driver"
                jar_pattern = "mysql-connector-j*.jar"
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            # Find JDBC driver
            jdbc_dir = JDBC_DRIVERS_PATH
            pattern = os.path.join(jdbc_dir, jar_pattern)
            jars = glob.glob(pattern)
            
            if not jars:
                raise Exception(f"No JDBC driver found for {self.db_type} at {pattern}")
            
            driver_jar = jars[0]
            logger.debug(f"Using JDBC driver: {driver_jar}")
            
            # Use centralized JDBC connection manager
            from kg_builder.services.jdbc_connection_manager import get_jdbc_connection
            conn = get_jdbc_connection(driver_class, jdbc_url, self.username, self.password)

            if not conn:
                raise Exception("Failed to get JDBC connection from connection manager")

            # Disable autocommit to allow manual transaction control
            conn.jconn.setAutoCommit(False)

            return conn
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def get_all_kpis(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """Get all KPIs using JDBC connection."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            where_clause = "" if include_inactive else "WHERE k.is_active = 1"
            
            # Try to include cache fields, but handle gracefully if they don't exist
            try:
                # First check if cache fields exist (MySQL syntax for KPI Analytics DB)
                cursor.execute("SELECT isAccept FROM kpi_definitions LIMIT 1")
                cache_fields_exist = True
            except Exception:
                cache_fields_exist = False
                logger.info("Cache fields not yet available in database")

            if cache_fields_exist:
                query = f"""
                    SELECT
                        k.id, k.name, k.alias_name, k.group_name, k.description, k.nl_definition,
                        k.created_at, k.updated_at, k.created_by, k.is_active,
                        k.isAccept, k.isSQLCached, k.cached_sql,
                        e.id as latest_execution_id,
                        e.execution_timestamp as latest_execution,
                        e.execution_status as latest_status,
                        e.number_of_records as latest_record_count,
                        e.generated_sql as latest_sql,
                        e.error_message as latest_error
                    FROM kpi_definitions k
                    LEFT JOIN kpi_execution_results e ON k.id = e.kpi_id
                        AND e.execution_timestamp = (
                            SELECT MAX(execution_timestamp)
                            FROM kpi_execution_results
                            WHERE kpi_id = k.id
                        )
                    {where_clause}
                    ORDER BY k.group_name, k.name
                """
            else:
                query = f"""
                    SELECT
                        k.id, k.name, k.alias_name, k.group_name, k.description, k.nl_definition,
                        k.created_at, k.updated_at, k.created_by, k.is_active,
                        e.id as latest_execution_id,
                        e.execution_timestamp as latest_execution,
                        e.execution_status as latest_status,
                        e.number_of_records as latest_record_count,
                        e.generated_sql as latest_sql,
                        e.error_message as latest_error
                    FROM kpi_definitions k
                    LEFT JOIN kpi_execution_results e ON k.id = e.kpi_id
                        AND e.execution_timestamp = (
                            SELECT MAX(execution_timestamp)
                            FROM kpi_execution_results
                            WHERE kpi_id = k.id
                        )
                    {where_clause}
                    ORDER BY k.group_name, k.name
                """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            kpis = []
            for row in rows:
                if cache_fields_exist:
                    # Include cache fields
                    kpi = {
                        'id': self._convert_java_types(row[0]),
                        'name': self._convert_java_types(row[1]),
                        'alias_name': self._convert_java_types(row[2]),
                        'group_name': self._convert_java_types(row[3]),
                        'description': self._convert_java_types(row[4]),
                        'nl_definition': self._convert_java_types(row[5]),
                        'created_at': str(self._convert_java_types(row[6])) if row[6] else None,
                        'updated_at': str(self._convert_java_types(row[7])) if row[7] else None,
                        'created_by': self._convert_java_types(row[8]),
                        'is_active': bool(self._convert_java_types(row[9])),
                        'isAccept': self._to_bool(self._convert_java_types(row[10])),
                        'isSQLCached': self._to_bool(self._convert_java_types(row[11])),
                        'cached_sql': self._convert_java_types(row[12]),
                        'latest_execution': {
                            'id': self._convert_java_types(row[13]),
                            'timestamp': str(self._convert_java_types(row[14])) if row[14] else None,
                            'status': self._convert_java_types(row[15]),
                            'record_count': self._convert_java_types(row[16]),
                            'generated_sql': self._convert_java_types(row[17]),
                            'error_message': self._convert_java_types(row[18])
                        } if row[13] else None
                    }
                else:
                    # Without cache fields (backward compatibility)
                    kpi = {
                        'id': self._convert_java_types(row[0]),
                        'name': self._convert_java_types(row[1]),
                        'alias_name': self._convert_java_types(row[2]),
                        'group_name': self._convert_java_types(row[3]),
                        'description': self._convert_java_types(row[4]),
                        'nl_definition': self._convert_java_types(row[5]),
                        'created_at': str(self._convert_java_types(row[6])) if row[6] else None,
                        'updated_at': str(self._convert_java_types(row[7])) if row[7] else None,
                        'created_by': self._convert_java_types(row[8]),
                        'is_active': bool(self._convert_java_types(row[9])),
                        'isAccept': False,  # Default values
                        'isSQLCached': False,
                        'cached_sql': None,
                        'latest_execution': {
                            'id': self._convert_java_types(row[10]),
                            'timestamp': str(self._convert_java_types(row[11])) if row[11] else None,
                            'status': self._convert_java_types(row[12]),
                            'record_count': self._convert_java_types(row[13]),
                            'generated_sql': self._convert_java_types(row[14]),
                            'error_message': self._convert_java_types(row[15])
                        } if row[10] else None
                    }
                kpis.append(kpi)
            
            logger.info(f"Retrieved {len(kpis)} KPIs via JDBC")
            return self._convert_response(kpis)
            
        finally:
            cursor.close()
            conn.close()

    def delete_kpi(self, kpi_id: int) -> bool:
        """Delete a KPI by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # First check if KPI exists
            cursor.execute("SELECT id FROM kpi_definitions WHERE id = ?", (kpi_id,))
            if not cursor.fetchone():
                logger.warning(f"KPI with ID {kpi_id} not found for deletion")
                return False

            # Delete execution results first (foreign key constraint)
            cursor.execute("DELETE FROM kpi_execution_results WHERE kpi_id = ?", (kpi_id,))
            deleted_executions = cursor.rowcount

            # Delete the KPI definition
            cursor.execute("DELETE FROM kpi_definitions WHERE id = ?", (kpi_id,))
            deleted_kpi = cursor.rowcount

            # Commit the transaction
            conn.commit()

            logger.info(f"✓ Deleted KPI {kpi_id} and {deleted_executions} execution records")
            return deleted_kpi > 0

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to delete KPI {kpi_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def test_connection(self) -> bool:
        """Test if JDBC connection works."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result[0] == 1
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data grouped by KPI groups."""
        kpis = self.get_all_kpis(include_inactive=False)
        
        # Group KPIs by group_name
        groups = {}
        for kpi in kpis:
            group_name = kpi.get('group_name') or 'Ungrouped'
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(kpi)
        
        # Convert to list format
        groups_list = [
            {
                'group_name': group_name,
                'kpis': kpis_in_group
            }
            for group_name, kpis_in_group in sorted(groups.items())
        ]
        
        return {'groups': groups_list}
    
    def create_kpi(self, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new KPI definition."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO kpi_definitions
                (name, alias_name, group_name, description, nl_definition, created_by,
                 is_active, isAccept, isSQLCached, cached_sql)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                kpi_data.get('name'),
                kpi_data.get('alias_name'),
                kpi_data.get('group_name'),
                kpi_data.get('description'),
                kpi_data.get('nl_definition'),
                kpi_data.get('created_by'),
                kpi_data.get('is_active', True),  # Default to active
                kpi_data.get('isAccept', False),
                kpi_data.get('isSQLCached', False),
                kpi_data.get('cached_sql')
            ))

            conn.commit()
            logger.info(f"✓ Created KPI: {kpi_data.get('name')}")

            # Get the created KPI (since JDBC doesn't return the ID easily, we'll find it by name)
            created_kpis = self.get_all_kpis()
            for kpi in created_kpis:
                if kpi['name'] == kpi_data.get('name'):
                    return kpi

            # Fallback - return the data with a placeholder ID
            return {
                'id': 0,
                'success': True,
                'message': 'KPI created successfully',
                **kpi_data
            }

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to create KPI: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def update_kpi(self, kpi_id: int, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update KPI definition using JDBC connection."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Build dynamic update query
            updates = []
            params = []

            # Handle the fields that can be updated (including new cache fields)
            for key in ['name', 'alias_name', 'group_name', 'description', 'nl_definition', 'is_active', 'isAccept', 'isSQLCached', 'cached_sql']:
                if key in kpi_data and kpi_data[key] is not None:
                    updates.append(f"{key} = ?")
                    params.append(kpi_data[key])

            if not updates:
                # No updates to make, just return the current KPI
                return self.get_kpi(kpi_id)

            # Add updated_at timestamp (MySQL syntax for KPI Analytics DB)
            updates.append("updated_at = NOW()")
            params.append(kpi_id)

            # Execute update query
            query = f"UPDATE kpi_definitions SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)

            if cursor.rowcount == 0:
                raise ValueError(f"KPI with ID {kpi_id} not found")

            conn.commit()
            logger.info(f"✓ Updated KPI ID: {kpi_id}")

            # Return the updated KPI
            return self.get_kpi(kpi_id)

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to update KPI {kpi_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def update_cache_flags(self, kpi_id: int, cache_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update KPI cache flags (isAccept, isSQLCached, cached_sql)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            updates = []
            params = []

            # Check if cache fields exist in the database first
            try:
                cursor.execute("SELECT isAccept, isSQLCached, cached_sql FROM kpi_definitions WHERE id = ? LIMIT 1", (kpi_id,))
                cache_fields_exist = True
            except Exception:
                logger.warning("Cache fields don't exist in database yet. Please run the migration script.")
                cache_fields_exist = False

            if not cache_fields_exist:
                # Fallback to regular update without cache fields
                logger.info(f"Cache fields not available, skipping cache update for KPI {kpi_id}")
                return self.get_kpi(kpi_id)

            if 'isAccept' in cache_data:
                updates.append("isAccept = ?")
                params.append(cache_data['isAccept'])
                logger.info(f"   Setting isAccept = {cache_data['isAccept']}")

            if 'isSQLCached' in cache_data:
                updates.append("isSQLCached = ?")
                params.append(cache_data['isSQLCached'])
                logger.info(f"   Setting isSQLCached = {cache_data['isSQLCached']}")

            if 'cached_sql' in cache_data:
                sql_value = cache_data['cached_sql']
                updates.append("cached_sql = ?")
                params.append(sql_value)
                logger.info(f"   Setting cached_sql = {sql_value[:100] if sql_value else 'NULL'}...")
                logger.info(f"   cached_sql length: {len(sql_value) if sql_value else 0}")

            if not updates:
                return self.get_kpi(kpi_id)

            # Add updated_at timestamp (MySQL syntax for KPI Analytics DB)
            updates.append("updated_at = NOW()")
            params.append(kpi_id)

            query = f"UPDATE kpi_definitions SET {', '.join(updates)} WHERE id = ?"
            logger.info(f"🔄 Executing SQL: {query}")
            logger.info(f"🔄 With params: {[str(p)[:100] if isinstance(p, str) else p for p in params]}")

            cursor.execute(query, params)

            if cursor.rowcount == 0:
                raise ValueError(f"KPI with ID {kpi_id} not found")

            conn.commit()
            logger.info(f"✓ Updated cache flags for KPI ID: {kpi_id}, rows affected: {cursor.rowcount}")

            # Get and return updated KPI
            updated_kpi = self.get_kpi(kpi_id)
            logger.info(f"✓ Returning updated KPI with cached_sql length: {len(updated_kpi.get('cached_sql', ''))}")
            return updated_kpi

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to update cache flags for KPI {kpi_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def clear_cache_flags(self, kpi_id: int) -> Dict[str, Any]:
        """Clear both isAccept and isSQLCached flags for a KPI."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Check if cache fields exist in the database first
            try:
                cursor.execute("SELECT isAccept, isSQLCached, cached_sql FROM kpi_definitions WHERE id = ? LIMIT 1", (kpi_id,))
                cache_fields_exist = True
            except Exception:
                logger.warning("Cache fields don't exist in database yet. Please run the migration script.")
                cache_fields_exist = False

            if not cache_fields_exist:
                logger.info(f"Cache fields not available, skipping cache clear for KPI {kpi_id}")
                return self.get_kpi(kpi_id)

            # Clear cache flags (MySQL syntax for KPI Analytics DB)
            cursor.execute("""
                UPDATE kpi_definitions
                SET isAccept = 0, isSQLCached = 0, cached_sql = NULL, updated_at = NOW()
                WHERE id = ?
            """, (kpi_id,))

            if cursor.rowcount == 0:
                raise ValueError(f"KPI with ID {kpi_id} not found")

            conn.commit()
            logger.info(f"✓ Cleared cache flags for KPI ID: {kpi_id}")
            return self.get_kpi(kpi_id)

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to clear cache flags for KPI {kpi_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_kpi(self, kpi_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific KPI by ID with cache fields."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Check if cache fields exist
            try:
                cursor.execute("SELECT isAccept FROM kpi_definitions LIMIT 1")
                cache_fields_exist = True
            except Exception:
                cache_fields_exist = False
                logger.info("Cache fields not yet available in database")

            if cache_fields_exist:
                query = """
                    SELECT
                        k.id, k.name, k.alias_name, k.group_name, k.description, k.nl_definition,
                        k.created_at, k.updated_at, k.created_by, k.is_active,
                        k.isAccept, k.isSQLCached, k.cached_sql,
                        e.id as latest_execution_id,
                        e.execution_timestamp as latest_execution,
                        e.execution_status as latest_status,
                        e.number_of_records as latest_record_count,
                        e.generated_sql as latest_sql,
                        e.error_message as latest_error
                    FROM kpi_definitions k
                    LEFT JOIN kpi_execution_results e ON k.id = e.kpi_id
                        AND e.execution_timestamp = (
                            SELECT MAX(execution_timestamp)
                            FROM kpi_execution_results
                            WHERE kpi_id = k.id
                        )
                    WHERE k.id = ?
                """
            else:
                query = """
                    SELECT
                        k.id, k.name, k.alias_name, k.group_name, k.description, k.nl_definition,
                        k.created_at, k.updated_at, k.created_by, k.is_active,
                        e.id as latest_execution_id,
                        e.execution_timestamp as latest_execution,
                        e.execution_status as latest_status,
                        e.number_of_records as latest_record_count,
                        e.generated_sql as latest_sql,
                        e.error_message as latest_error
                    FROM kpi_definitions k
                    LEFT JOIN kpi_execution_results e ON k.id = e.kpi_id
                        AND e.execution_timestamp = (
                            SELECT MAX(execution_timestamp)
                            FROM kpi_execution_results
                            WHERE kpi_id = k.id
                        )
                    WHERE k.id = ?
                """

            cursor.execute(query, (kpi_id,))
            row = cursor.fetchone()

            if not row:
                return None

            if cache_fields_exist:
                # Include cache fields
                kpi = {
                    'id': row[0],
                    'name': row[1],
                    'alias_name': row[2],
                    'group_name': row[3],
                    'description': row[4],
                    'nl_definition': row[5],
                    'created_at': str(row[6]) if row[6] else None,
                    'updated_at': str(row[7]) if row[7] else None,
                    'created_by': row[8],
                    'is_active': bool(row[9]),
                    'isAccept': self._to_bool(row[10]),
                    'isSQLCached': self._to_bool(row[11]),
                    'cached_sql': row[12],
                    'latest_execution': {
                        'id': row[13],
                        'timestamp': str(row[14]) if row[14] else None,
                        'status': row[15],
                        'record_count': row[16],
                        'generated_sql': row[17],
                        'error_message': row[18]
                    } if row[13] else None
                }
            else:
                # Without cache fields (backward compatibility)
                kpi = {
                    'id': row[0],
                    'name': row[1],
                    'alias_name': row[2],
                    'group_name': row[3],
                    'description': row[4],
                    'nl_definition': row[5],
                    'created_at': str(row[6]) if row[6] else None,
                    'updated_at': str(row[7]) if row[7] else None,
                    'created_by': row[8],
                    'is_active': bool(row[9]),
                    'isAccept': False,  # Default values
                    'isSQLCached': False,
                    'cached_sql': None,
                    'latest_execution': {
                        'id': row[10],
                        'timestamp': str(row[11]) if row[11] else None,
                        'status': row[12],
                        'record_count': row[13],
                        'generated_sql': row[14],
                        'error_message': row[15]
                    } if row[10] else None
                }

            # Debug logging
            logger.info(f"🔍 get_kpi({kpi_id}) returning:")
            logger.info(f"   isAccept: {kpi.get('isAccept')} (type: {type(kpi.get('isAccept'))})")
            logger.info(f"   isSQLCached: {kpi.get('isSQLCached')} (type: {type(kpi.get('isSQLCached'))})")
            logger.info(f"   cached_sql: {bool(kpi.get('cached_sql'))}")

            return kpi

        finally:
            cursor.close()
            conn.close()
    
    def create_execution_record(self, kpi_id: int, execution_params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new execution record for a KPI without executing it."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Validate kg_name first
            kg_name = execution_params.get('kg_name')
            if not kg_name or kg_name.strip() == '' or kg_name.lower() == 'default':
                raise ValueError(
                    "kg_name is required and cannot be empty or 'default'. "
                    "Please provide a valid Knowledge Graph name (e.g., 'New_KG_101', 'KG_102')."
                )

            # Get select_schema - prioritize direct select_schema over schemas array
            select_schema = execution_params.get('select_schema')
            schemas = execution_params.get('schemas', [])

            # If select_schema is provided directly, use it
            if select_schema and select_schema.strip():
                logger.info(f"✅ Using direct select_schema: '{select_schema}'")
            # Otherwise, fall back to schemas array
            elif schemas and len(schemas) > 0:
                select_schema = schemas[0]
                logger.info(f"📋 Converted from schemas array: '{select_schema}' (from {schemas})")
            # Final fallback
            else:
                select_schema = 'newdqnov7'  # Use the schema from the request example
                logger.warning(f"⚠️ Using fallback schema: '{select_schema}'")

            # Convert limit to limit_records if needed
            limit_records = execution_params.get('limit_records') or execution_params.get('limit', 1000)

            logger.info(f"🔧 Creating execution record with parameters:")
            logger.info(f"   kpi_id: {kpi_id}")
            logger.info(f"   kg_name: {kg_name}")
            logger.info(f"   select_schema: {select_schema} (converted from schemas: {schemas})")
            logger.info(f"   db_type: {execution_params.get('db_type', 'sqlserver')}")
            logger.info(f"   limit_records: {limit_records}")
            logger.info(f"   use_llm: {execution_params.get('use_llm', True)}")

            cursor.execute("""
                INSERT INTO kpi_execution_results
                (kpi_id, kg_name, select_schema, db_type, limit_records, use_llm,
                 execution_status, user_id, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                kpi_id,
                kg_name,
                select_schema,  # Use the converted value
                execution_params.get('db_type', 'sqlserver'),
                limit_records,  # Use the converted value
                execution_params.get('use_llm', True),
                'pending',
                execution_params.get('user_id'),
                execution_params.get('session_id')
            ))

            # Get the inserted ID (MySQL syntax for KPI Analytics DB)
            cursor.execute("SELECT LAST_INSERT_ID()")
            execution_id = cursor.fetchone()[0]

            conn.commit()
            logger.info(f"✓ Created execution record ID: {execution_id} for KPI ID: {kpi_id}")

            return {
                'id': self._convert_java_types(execution_id),
                'kpi_id': kpi_id,
                'execution_status': 'pending',
                'kg_name': kg_name,
                'select_schema': select_schema
            }

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to create execution record for KPI {kpi_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def execute_kpi(self, kpi_id: int, execution_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a KPI and store results in the database."""
        import time
        import json
        from datetime import datetime

        start_time = time.time()

        logger.info("="*120)
        logger.info(f"🚀 KPI EXECUTION FLOW: STARTING FULL KPI EXECUTION")
        logger.info(f"   KPI ID: {kpi_id}")
        logger.info(f"   Execution Params: {execution_params}")
        logger.info(f"   Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*120)

        try:
            # STEP 1: Get the KPI definition
            logger.info(f"📋 STEP 1: Retrieving KPI Definition")
            kpi_start = time.time()

            kpi = self.get_kpi(kpi_id)
            if not kpi:
                raise ValueError(f"KPI with ID {kpi_id} not found")

            kpi_time = (time.time() - kpi_start) * 1000
            logger.info(f"✅ KPI definition retrieved in {kpi_time:.2f}ms")
            logger.info(f"   KPI Name: {kpi.get('name', 'Unknown')}")
            logger.info(f"   KPI Description: {kpi.get('description', 'No description')}")
            logger.info(f"   NL Definition: {kpi.get('nl_definition', 'No NL definition')}")
            logger.info(f"   Business Priority: {kpi.get('business_priority', 'Unknown')}")
            logger.info(f"   Cached SQL Available: {bool(kpi.get('cached_sql'))}")

            # STEP 2: Extract and validate execution parameters
            logger.info(f"⚙️ STEP 2: Processing Execution Parameters")
            params_start = time.time()

            # Extract and validate kg_name
            kg_name = execution_params.get('kg_name')

            # Validate kg_name is provided and not default
            if not kg_name or kg_name.strip() == '' or kg_name.lower() == 'default':
                raise ValueError(
                    "kg_name is required and cannot be empty or 'default'. "
                    "Please provide a valid Knowledge Graph name (e.g., 'New_KG_101', 'KG_102')."
                )

            schemas = execution_params.get('schemas', ['newdqschemanov'])
            select_schema = schemas[0] if schemas else 'newdqschemanov'
            use_llm = execution_params.get('use_llm', True)
            limit_records = execution_params.get('limit', 1000)
            db_type = execution_params.get('db_type', 'sqlserver')

            params_time = (time.time() - params_start) * 1000
            logger.info(f"✅ Execution parameters processed in {params_time:.2f}ms")
            logger.info(f"   Knowledge Graph: {kg_name}")
            logger.info(f"   Schemas: {schemas}")
            logger.info(f"   Select Schema: {select_schema}")
            logger.info(f"   Use LLM: {use_llm}")
            logger.info(f"   Limit Records: {limit_records}")
            logger.info(f"   Database Type: {db_type}")
            logger.info(f"   User ID: {execution_params.get('user_id', 'Not provided')}")
            logger.info(f"   Session ID: {execution_params.get('session_id', 'Not provided')}")

            # STEP 3: Load Knowledge Graph for join column inference
            logger.info(f"🧠 STEP 3: Loading Knowledge Graph")
            kg_start = time.time()

            from kg_builder.services.graphiti_backend import get_graphiti_backend
            from kg_builder.models import KnowledgeGraph, GraphNode, GraphRelationship

            logger.info(f"   Initializing Graphiti backend...")
            graphiti = get_graphiti_backend()

            logger.info(f"   Loading entities for KG: {kg_name}")
            entities_data = graphiti.get_entities(kg_name)

            logger.info(f"   Loading relationships for KG: {kg_name}")
            relationships_data = graphiti.get_relationships(kg_name)

            kg_load_time = (time.time() - kg_start) * 1000
            logger.info(f"✅ Knowledge Graph loaded in {kg_load_time:.2f}ms")
            logger.info(f"   Entities Count: {len(entities_data) if entities_data else 0}")
            logger.info(f"   Relationships Count: {len(relationships_data) if relationships_data else 0}")

            # STEP 4: Convert to KnowledgeGraph object
            logger.info(f"🔧 STEP 4: Constructing Knowledge Graph Object")
            construct_start = time.time()

            logger.info(f"   Converting entities to GraphNode objects...")
            nodes = [GraphNode(**entity) for entity in entities_data] if entities_data else []

            logger.info(f"   Converting relationships to GraphRelationship objects...")
            relationships = [GraphRelationship(**rel) for rel in relationships_data] if relationships_data else []

            # Load metadata including table_aliases
            logger.info(f"   Loading KG metadata and table aliases...")
            table_aliases = {}
            try:
                kg_metadata = graphiti.get_kg_metadata(kg_name)
                if kg_metadata:
                    table_aliases = kg_metadata.get('table_aliases', {})
                    logger.info(f"   Found {len(table_aliases)} table aliases")
                    for table, aliases in table_aliases.items():
                        logger.info(f"      {table}: {aliases}")
                else:
                    logger.warning(f"   No metadata found for KG: {kg_name}")
            except Exception as e:
                logger.warning(f"   Could not load KG metadata: {e}")

            logger.info(f"   Creating KnowledgeGraph object...")
            kg = KnowledgeGraph(
                name=kg_name,
                nodes=nodes,
                relationships=relationships,
                schema_file=select_schema,
                table_aliases=table_aliases
            )

            construct_time = (time.time() - construct_start) * 1000
            logger.info(f"✅ Knowledge Graph object constructed in {construct_time:.2f}ms")
            logger.info(f"   KG Name: {kg.name}")
            logger.info(f"   Schema File: {kg.schema_file}")
            logger.info(f"   Nodes: {len(kg.nodes)}")
            logger.info(f"   Relationships: {len(kg.relationships)}")
            logger.info(f"   Table Aliases: {len(kg.table_aliases)}")

            # STEP 5: Execute the KPI using the existing NL query system with KG
            logger.info(f"🤖 STEP 5: Initializing NL Query Execution System")
            nl_init_start = time.time()

            from kg_builder.services.nl_query_executor import NLQueryExecutor
            from kg_builder.services.nl_query_parser import get_nl_query_parser

            logger.info(f"   Importing NL Query components...")
            nl_init_time = (time.time() - nl_init_start) * 1000
            logger.info(f"✅ NL Query system initialized in {nl_init_time:.2f}ms")

            # STEP 6: Extract schemas_info from KG for LLM prompt
            logger.info(f"📊 STEP 6: Extracting Schema Information from Knowledge Graph")
            schema_extract_start = time.time()

            def _extract_schemas_info_from_kg(kg):
                schemas_info = {}
                table_count = 0
                total_columns = 0

                logger.info(f"   Processing {len(kg.nodes)} nodes...")
                for node in kg.nodes:
                    if node.properties.get("type") == "Table":
                        table_count += 1
                        schema_name = node.properties.get("schema", select_schema)
                        if schema_name not in schemas_info:
                            schemas_info[schema_name] = {"tables": {}}
                            logger.info(f"   Found new schema: {schema_name}")

                        table_name = node.label
                        columns = node.properties.get("columns", [])

                        # Extract column names
                        column_names = []
                        for col in columns:
                            if isinstance(col, dict):
                                col_name = col.get("name")
                                if col_name:
                                    column_names.append(col_name)
                            elif hasattr(col, 'name'):
                                column_names.append(col.name)

                        total_columns += len(column_names)
                        logger.info(f"   Table: {table_name} ({len(column_names)} columns)")

                        schemas_info[schema_name]["tables"][table_name] = {
                            "columns": column_names
                        }
                return schemas_info

            schemas_info = _extract_schemas_info_from_kg(kg)

            # Parse the natural language definition with KG
            parser = get_nl_query_parser(kg=kg, schemas_info=schemas_info)
            intent = parser.parse(kpi['nl_definition'], use_llm=use_llm)

            # Execute the query with KG
            executor = NLQueryExecutor(
                db_type=db_type.lower(),
                kg=kg,
                use_llm=use_llm
            )

            # Get database connection for execution
            from kg_builder.services.landing_kpi_executor import _get_source_database_connection
            connection = _get_source_database_connection(db_type)

            if not connection:
                raise Exception("Could not establish database connection for KPI execution")

            # Generate SQL (simple, no enhancement)
            sql_to_execute = executor.generator.generate(intent)

            logger.info(f"🔍 Generated SQL: {sql_to_execute[:100]}...")

            # Execute the SQL
            from kg_builder.services.nl_query_executor import QueryResult
            try:
                cursor = connection.cursor()
                cursor.execute(sql_to_execute)

                # Fetch results
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []

                # Convert to list of dictionaries with Java type conversion
                from kg_builder.utils.java_type_converter import convert_jdbc_results
                records = convert_jdbc_results(rows, columns)

                result = QueryResult(
                    definition=kpi['nl_definition'],
                    query_type='kpi_execution',
                    operation='execute',
                    sql=sql_to_execute,
                    record_count=len(records),
                    records=records,
                    join_columns=None,
                    confidence=0.95,  # High confidence for successful execution
                    execution_time_ms=(time.time() - start_time) * 1000,
                    error=None,
                    source_table=None,
                    target_table=None
                )

                logger.info(f"✅ Enhanced SQL executed successfully: {len(records)} records found")

            except Exception as e:
                logger.error(f"❌ Enhanced SQL execution failed: {e}")
                result = QueryResult(
                    definition=kpi['nl_definition'],
                    query_type='kpi_execution',
                    operation='execute',
                    sql=sql_to_execute,
                    record_count=0,
                    records=[],
                    join_columns=None,
                    confidence=0.0,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    error=str(e),
                    source_table=None,
                    target_table=None
                )
            finally:
                cursor.close()

            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Prepare execution record
            execution_record = {
                'kpi_id': kpi_id,
                'kg_name': kg_name,
                'select_schema': select_schema,
                'db_type': db_type,
                'limit_records': limit_records,
                'use_llm': use_llm,
                'generated_sql': result.sql,
                'number_of_records': result.record_count,
                'execution_status': 'success' if not result.error else 'error',
                'execution_time_ms': execution_time_ms,
                'confidence_score': result.confidence,
                'error_message': result.error if result.error else None,
                'result_data': json.dumps(result.records) if result.records else None,
                'execution_timestamp': datetime.now()
            }

            # Store execution result in database
            execution_id = self.store_execution_result(execution_record)

            # Convert Java types in result records for JSON serialization
            from kg_builder.utils.java_type_converter import convert_java_list
            converted_records = convert_java_list(result.records) if result.records else []

            # Return comprehensive result
            response = {
                'success': True,
                'execution_id': self._convert_java_types(execution_id),
                'kpi_id': kpi_id,
                'kpi_name': kpi['name'],
                'execution_status': execution_record['execution_status'],
                'record_count': execution_record['number_of_records'],
                'execution_time_ms': execution_time_ms,
                'generated_sql': result.sql,
                'enhanced_sql': result.sql,  # Same as generated_sql for now
                'enhancement_applied': False,  # No enhancement for now
                'material_master_added': False,
                'ops_planner_added': False,
                'confidence_score': execution_record['confidence_score'],
                'data': converted_records,
                'error_message': execution_record['error_message']
            }
            return self._convert_response(response)

        except Exception as e:
            # Store failed execution
            execution_time_ms = int((time.time() - start_time) * 1000)

            execution_record = {
                'kpi_id': kpi_id,
                'kg_name': kg_name,
                'select_schema': execution_params.get('schemas', ['newdqschemanov'])[0],
                'db_type': execution_params.get('db_type', 'sqlserver'),
                'limit_records': execution_params.get('limit', 1000),
                'use_llm': execution_params.get('use_llm', True),
                'generated_sql': None,
                'number_of_records': 0,
                'execution_status': 'error',
                'execution_time_ms': execution_time_ms,
                'confidence_score': 0.0,
                'error_message': str(e),
                'result_data': None,
                'execution_timestamp': datetime.now()
            }

            try:
                execution_id = self.store_execution_result(execution_record)
            except Exception as store_error:
                logger.error(f"Failed to store error execution result: {store_error}")
                execution_id = None

            error_response = {
                'success': False,
                'execution_id': execution_id,
                'kpi_id': kpi_id,
                'execution_status': 'error',
                'error_message': str(e),
                'execution_time_ms': execution_time_ms
            }
            return self._convert_response(error_response)

    def update_execution_result(self, execution_id: int, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update execution result with query results."""
        import json
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Convert complex data to JSON
            joined_columns_json = json.dumps(result_data.get('joined_columns', []))
            result_json = json.dumps(result_data.get('result_data', []))
            evidence_json = json.dumps(result_data.get('evidence_data', []))

            cursor.execute("""
                UPDATE kpi_execution_results
                SET
                    generated_sql = ?,
                    number_of_records = ?,
                    joined_columns = ?,
                    sql_query_type = ?,
                    operation = ?,
                    execution_status = ?,
                    execution_time_ms = ?,
                    confidence_score = ?,
                    error_message = ?,
                    result_data = ?,
                    evidence_data = ?,
                    evidence_count = ?,
                    source_table = ?,
                    target_table = ?,
                    execution_timestamp = COALESCE(execution_timestamp, NOW())
                WHERE id = ?
            """, (
                result_data.get('generated_sql'),
                result_data.get('number_of_records', 0),
                joined_columns_json,
                result_data.get('sql_query_type'),
                result_data.get('operation'),
                result_data.get('execution_status', 'success'),
                result_data.get('execution_time_ms'),
                result_data.get('confidence_score'),
                result_data.get('error_message'),
                result_json,
                evidence_json,
                len(result_data.get('evidence_data', [])),
                result_data.get('source_table'),
                result_data.get('target_table'),
                execution_id
            ))

            conn.commit()
            logger.info(f"✓ Updated execution result ID: {execution_id}")

            # Return updated execution result
            return {
                'id': execution_id,
                'execution_status': result_data.get('execution_status', 'success'),
                'generated_sql': result_data.get('generated_sql'),
                'number_of_records': result_data.get('number_of_records', 0),
                'execution_time_ms': result_data.get('execution_time_ms'),
                'error_message': result_data.get('error_message')
            }

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to update execution result {execution_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def store_execution_result(self, execution_record: Dict[str, Any]) -> int:
        """Store KPI execution result in the database."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Insert execution result (SQL Server syntax)
            cursor.execute("""
                INSERT INTO kpi_execution_results (
                    kpi_id, kg_name, select_schema, db_type, limit_records, use_llm,
                    generated_sql, number_of_records, execution_status, execution_timestamp,
                    execution_time_ms, confidence_score, error_message, result_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution_record['kpi_id'],
                execution_record['kg_name'],
                execution_record['select_schema'],
                execution_record['db_type'],
                execution_record['limit_records'],
                execution_record['use_llm'],
                execution_record['generated_sql'],
                execution_record['number_of_records'],
                execution_record['execution_status'],
                execution_record['execution_timestamp'],
                execution_record['execution_time_ms'],
                execution_record['confidence_score'],
                execution_record['error_message'],
                execution_record['result_data']
            ))

            # Get the inserted ID (MySQL syntax for KPI Analytics DB)
            cursor.execute("SELECT LAST_INSERT_ID()")
            execution_id = cursor.fetchone()[0]

            # Commit the transaction
            conn.commit()

            logger.info(f"✓ Stored execution result with ID {execution_id}")
            return execution_id

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to store execution result: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_execution_result(self, execution_id: int) -> Optional[Dict[str, Any]]:
        """Get execution result by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get execution result (MySQL syntax for KPI Analytics DB)
            cursor.execute("""
                SELECT
                    e.id, e.kpi_id, e.kg_name, e.select_schema, e.db_type,
                    e.limit_records, e.use_llm, e.generated_sql, e.number_of_records,
                    e.joined_columns, e.sql_query_type, e.operation, e.execution_status,
                    e.execution_timestamp, e.execution_time_ms, e.confidence_score,
                    e.error_message, e.result_data, e.evidence_data, e.evidence_count,
                    e.source_table, e.target_table, e.user_id, e.session_id,
                    k.name as kpi_name, k.alias_name
                FROM kpi_execution_results e
                JOIN kpi_definitions k ON e.kpi_id = k.id
                WHERE e.id = ?
                LIMIT 1
            """, (execution_id,))

            row = cursor.fetchone()
            if row:
                result = {
                    'id': self._convert_java_types(row[0]),
                    'kpi_id': self._convert_java_types(row[1]),
                    'kg_name': self._convert_java_types(row[2]),
                    'select_schema': self._convert_java_types(row[3]),
                    'db_type': self._convert_java_types(row[4]),
                    'limit_records': self._convert_java_types(row[5]),
                    'use_llm': bool(self._convert_java_types(row[6])),
                    'generated_sql': self._convert_java_types(row[7]),
                    'number_of_records': self._convert_java_types(row[8]),
                    'joined_columns': json.loads(self._convert_java_types(row[9])) if row[9] else [],
                    'sql_query_type': self._convert_java_types(row[10]),
                    'operation': self._convert_java_types(row[11]),
                    'execution_status': self._convert_java_types(row[12]),
                    'execution_timestamp': str(self._convert_java_types(row[13])) if row[13] else None,
                    'execution_time_ms': self._convert_java_types(row[14]),
                    'confidence_score': self._convert_java_types(row[15]),
                    'error_message': self._convert_java_types(row[16]),
                    'result_data': json.loads(self._convert_java_types(row[17])) if row[17] else [],
                    'evidence_data': json.loads(self._convert_java_types(row[18])) if row[18] else [],
                    'evidence_count': self._convert_java_types(row[19]),
                    'source_table': self._convert_java_types(row[20]),
                    'target_table': self._convert_java_types(row[21]),
                    'user_id': self._convert_java_types(row[22]),
                    'session_id': self._convert_java_types(row[23]),
                    'kpi_name': self._convert_java_types(row[24]),
                    'kpi_alias_name': self._convert_java_types(row[25])
                }
                return self._convert_response(result)

            return None
        finally:
            conn.close()

    def get_latest_results(self, kpi_id: int) -> Optional[Dict[str, Any]]:
        """Get the latest execution results for a specific KPI."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get latest results (MySQL syntax for KPI Analytics DB)
            cursor.execute("""
                SELECT
                    id, kpi_id, kg_name, select_schema, generated_sql,
                    number_of_records, execution_status, execution_timestamp,
                    execution_time_ms, confidence_score, error_message, result_data
                FROM kpi_execution_results
                WHERE kpi_id = ? AND execution_status = 'success' AND result_data IS NOT NULL
                ORDER BY execution_timestamp DESC
                LIMIT 1
            """, (kpi_id,))

            row = cursor.fetchone()
            if not row:
                logger.info(f"No successful execution with result_data found for KPI {kpi_id}")
                return None

            logger.info(f"📊 Raw result for KPI {kpi_id}: execution_id={row[0]}, result_data length={len(str(row[11])) if row[11] else 0}")

            # Parse result data if it exists
            result_data = None
            column_names = None

            if row[11]:  # result_data column
                try:
                    import json
                    parsed_data = json.loads(self._convert_java_types(row[11]))

                    # Log the structure of parsed data
                    if isinstance(parsed_data, dict):
                        logger.info(f"📋 Parsed result_data keys: {list(parsed_data.keys())}")

                        # Handle nested result_data structure
                        if 'result_data' in parsed_data:
                            result_data = parsed_data['result_data']
                            logger.info(f"📊 Found nested result_data with {len(result_data) if isinstance(result_data, list) else 'non-list'} items")
                        else:
                            result_data = parsed_data

                        # Extract column names
                        if 'column_names' in parsed_data:
                            column_names = parsed_data['column_names']
                            logger.info(f"📋 Found column names: {column_names}")
                        elif isinstance(result_data, list) and len(result_data) > 0 and isinstance(result_data[0], dict):
                            column_names = list(result_data[0].keys())
                            logger.info(f"📋 Extracted column names from first row: {column_names}")

                    elif isinstance(parsed_data, list):
                        result_data = parsed_data
                        logger.info(f"📊 Result_data is a list with {len(parsed_data)} items")
                        if len(parsed_data) > 0 and isinstance(parsed_data[0], dict):
                            column_names = list(parsed_data[0].keys())

                except Exception as e:
                    logger.warning(f"Could not parse result_data for execution {row[0]}: {e}")
                    logger.warning(f"Raw result_data: {str(row[11])[:200]}...")
                    result_data = None
            else:
                logger.warning(f"No result_data found for KPI {kpi_id} execution {row[0]}")

            result = {
                'execution_id': self._convert_java_types(row[0]),
                'kpi_id': self._convert_java_types(row[1]),
                'kg_name': row[2],
                'select_schema': row[3],
                'generated_sql': row[4],
                'number_of_records': self._convert_java_types(row[5]),
                'execution_status': row[6],
                'execution_timestamp': str(row[7]) if row[7] else None,
                'execution_time_ms': self._convert_java_types(row[8]),
                'confidence_score': self._convert_java_types(row[9]),
                'error_message': row[10],
                'result_data': result_data,
                'column_names': column_names,
                'record_count': self._convert_java_types(row[5])  # Alias for compatibility
            }
            return self._convert_response(result)

        except Exception as e:
            logger.error(f"Error getting latest results for KPI {kpi_id}: {e}")
            return None

        finally:
            cursor.close()
            conn.close()

    def execute_cached_sql(self, kpi_id: int, execution_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute cached/accepted SQL directly without LLM processing.

        This method bypasses LLM generation and executes the cached SQL directly
        against the target database, creating execution history.

        Args:
            kpi_id: KPI definition ID
            execution_params: Execution parameters (kg_name, schema, etc.)

        Returns:
            Execution record with results

        Raises:
            ValueError: If KPI not found or SQL not cached/accepted
            Exception: If SQL execution fails
        """
        import time
        from datetime import datetime
        from kg_builder.services.nl_query_executor import NLQueryExecutor

        logger.info(f"🚀 DIRECT CACHED SQL EXECUTION for KPI {kpi_id}")
        execution_start_time = time.time()

        # Step 1: Get KPI and validate cached SQL
        kpi = self.get_kpi(kpi_id)
        if not kpi:
            raise ValueError(f"KPI {kpi_id} not found")

        if not kpi.get('isAccept', False):
            raise ValueError(f"KPI {kpi_id} SQL is not accepted (isAccept=False)")

        if not kpi.get('isSQLCached', False):
            raise ValueError(f"KPI {kpi_id} SQL is not cached (isSQLCached=False)")

        cached_sql = kpi.get('cached_sql', '').strip()
        if not cached_sql:
            raise ValueError(f"KPI {kpi_id} has no cached SQL")

        logger.info(f"✅ KPI validation passed - executing cached SQL")
        logger.info(f"   KPI Name: {kpi['name']}")
        logger.info(f"   Cached SQL Length: {len(cached_sql)} characters")

        # Step 2: Create execution record
        execution_record = self.create_execution_record(kpi_id, execution_params)

        execution_id = execution_record['id']
        logger.info(f"📝 Created execution record ID: {execution_id}")

        try:
            # Step 3: Execute cached SQL directly
            logger.info(f"⚙️ Executing cached SQL against target database")
            sql_execution_start = time.time()

            # Initialize query executor for direct SQL execution
            executor = NLQueryExecutor()

            # Execute the cached SQL directly using target database connection
            result = self._execute_sql_on_target_database(
                sql=cached_sql,
                db_type=execution_params.get('db_type', 'sqlserver'),
                limit_records=execution_params.get('limit_records', 1000)
            )

            sql_execution_time = (time.time() - sql_execution_start) * 1000
            total_execution_time = (time.time() - execution_start_time) * 1000

            # Check if SQL execution actually succeeded
            execution_status = result.get('execution_status', 'failed')
            error_message = result.get('error_message')

            if execution_status == 'failed' or error_message:
                logger.error(f"❌ SQL execution failed in {sql_execution_time:.2f}ms")
                logger.error(f"   Error: {error_message}")

                # Update execution record with failure
                update_data = {
                    'execution_status': 'failed',
                    'generated_sql': cached_sql,
                    'number_of_records': 0,
                    'execution_time_ms': int(total_execution_time),
                    'confidence_score': 1.0,
                    'result_data': [],
                    'evidence_data': [],
                    'source_table': '',
                    'target_table': '',
                    'error_message': error_message
                }

                updated_record = self.update_execution_result(execution_id, update_data)

                logger.error(f"💥 CACHED SQL EXECUTION FAILED")
                logger.error(f"   Total Time: {total_execution_time:.2f}ms")
                logger.error(f"   Error: {error_message}")
                logger.error(f"   Execution ID: {execution_id}")

                # Return the failure result
                return updated_record

            else:
                logger.info(f"✅ SQL execution completed in {sql_execution_time:.2f}ms")
                logger.info(f"   Records returned: {len(result.get('data', []))}")

                # Step 4: Update execution record with success results
                update_data = {
                    'execution_status': 'success',
                    'generated_sql': cached_sql,  # Store the executed SQL
                    'number_of_records': len(result.get('data', [])),
                    'execution_time_ms': int(total_execution_time),
                    'confidence_score': 1.0,  # Cached SQL has 100% confidence
                    'result_data': result.get('data', []),
                    'evidence_data': [],  # No evidence needed for cached SQL
                    'source_table': result.get('source_table', ''),
                    'target_table': result.get('target_table', ''),
                    'error_message': None
                }

                updated_record = self.update_execution_result(execution_id, update_data)

                logger.info(f"🎉 CACHED SQL EXECUTION COMPLETED SUCCESSFULLY")
                logger.info(f"   Total Time: {total_execution_time:.2f}ms")
                logger.info(f"   Records: {update_data['number_of_records']}")
                logger.info(f"   Execution ID: {execution_id}")

            return updated_record

        except Exception as e:
            # Step 5: Handle execution errors
            error_message = str(e)
            execution_time = (time.time() - execution_start_time) * 1000

            logger.error(f"❌ CACHED SQL EXECUTION FAILED: {error_message}")

            # Update execution record with error
            update_data = {
                'execution_status': 'failed',
                'generated_sql': cached_sql,  # Still store the SQL that failed
                'execution_time_ms': int(execution_time),
                'error_message': error_message,
                'number_of_records': 0,
                'result_data': [],
                'confidence_score': 1.0  # SQL was cached, failure is execution issue
            }

            updated_record = self.update_execution_result(execution_id, update_data)

            # Re-raise the exception for proper error handling
            raise Exception(f"Cached SQL execution failed: {error_message}")

    def _execute_sql_on_target_database(self, sql: str, db_type: str = 'sqlserver', limit_records: int = 1000) -> Dict[str, Any]:
        """
        Execute SQL directly on target database (where actual data resides) without LLM processing.

        Args:
            sql: SQL query to execute
            db_type: Target database type (sqlserver, mysql, postgresql, oracle)
            limit_records: Maximum number of records to return

        Returns:
            Dict containing execution results
        """
        import time
        from kg_builder.services.landing_kpi_executor import _get_source_database_connection

        start_time = time.time()

        logger.info(f"🚀 CACHED SQL EXECUTION ON TARGET DATABASE")
        logger.info(f"   Target DB Type: {db_type}")
        logger.info(f"   SQL Length: {len(sql)} characters")
        logger.info(f"   Limit: {limit_records}")

        try:
            # Add limit clause if not already present (using correct syntax for database type)
            sql_with_limit = self._add_limit_clause(sql, limit_records, db_type)

            logger.info(f"⚡ Connecting to target database for cached SQL execution")
            logger.info(f"   Requested DB Type: {db_type}")

            # Validate database type and provide warnings
            if db_type.lower() == 'sqlserver':
                logger.info(f"🔧 SQL Server specific optimizations enabled:")
                logger.info(f"   - Using TOP clause instead of LIMIT")
                logger.info(f"   - Using DB_NAME() for database verification")
                logger.info(f"   - Enhanced SQL Server error messages")
            elif db_type.lower() not in ['mysql', 'postgresql', 'postgres', 'oracle']:
                logger.warning(f"⚠️  Unknown database type '{db_type}' - using generic SQL syntax")

            # Debug: Show what database configuration will be used
            from kg_builder.config import get_target_db_config
            db_config = get_target_db_config()
            if db_config:
                logger.info(f"🔍 DATABASE CONFIGURATION BEING USED:")
                logger.info(f"   DB Type: {db_config.db_type}")
                logger.info(f"   Host: {db_config.host}")
                logger.info(f"   Port: {db_config.port}")
                logger.info(f"   Database: {db_config.database}")
                logger.info(f"   Username: {db_config.username}")
                logger.info(f"   Service Name: {db_config.service_name}")

                # CRITICAL CHECK: If database name is wrong, STOP immediately
                db_name_str = str(db_config.database) if db_config.database else ""
                if db_name_str.lower() in ['wrong', 'test', 'invalid', 'fake']:
                    error_msg = f"CRITICAL: Database name '{db_name_str}' appears to be invalid/test name. Refusing to continue."
                    logger.error(f"❌ {error_msg}")
                    raise Exception(error_msg)

            else:
                logger.error(f"❌ No database configuration found! SOURCE_DB_USERNAME or SOURCE_DB_PASSWORD not set")
                raise Exception("No database configuration found")

            # Get connection to target database (where actual data resides)
            from kg_builder.services.landing_kpi_executor import _get_target_database_connection
            target_conn = _get_target_database_connection(db_type)

            if target_conn is None:
                error_msg = f"CRITICAL: Failed to connect to target database (type: {db_type}). Check database configuration and connectivity."
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)

            logger.info(f"✅ Connected to target database successfully")
            logger.info(f"   Connection Type: {type(target_conn).__name__}")
            logger.info(f"   Connection Object: {target_conn}")

            # CRITICAL: Test the connection and verify database name
            try:
                test_cursor = target_conn.cursor()

                # Use database-specific query to get current database name
                if db_type.lower() == 'sqlserver':
                    test_cursor.execute("SELECT DB_NAME() as current_database")
                elif db_type.lower() == 'mysql':
                    test_cursor.execute("SELECT DATABASE() as current_database")
                elif db_type.lower() in ['postgresql', 'postgres']:
                    test_cursor.execute("SELECT current_database() as current_database")
                else:
                    # Fallback for unknown database types
                    test_cursor.execute("SELECT 'UNKNOWN' as current_database")

                db_result = test_cursor.fetchone()
                actual_db_name = db_result[0] if db_result else "UNKNOWN"
                test_cursor.close()

                # Convert Java strings to Python strings
                actual_db_name_str = str(actual_db_name) if actual_db_name else "UNKNOWN"
                expected_db_name_str = str(db_config.database) if db_config.database else "UNKNOWN"

                logger.info(f"🔍 ACTUAL DATABASE CONNECTED TO: '{actual_db_name_str}'")
                logger.info(f"🔍 EXPECTED DATABASE: '{expected_db_name_str}'")

                if actual_db_name_str.lower() != expected_db_name_str.lower():
                    error_msg = f"CRITICAL: Connected to wrong database! Expected '{expected_db_name_str}' but connected to '{actual_db_name_str}'"
                    logger.error(f"❌ {error_msg}")
                    raise Exception(error_msg)

                logger.info(f"✅ Database connection verified - connected to correct database: '{actual_db_name_str}'")

            except Exception as db_test_error:
                logger.error(f"❌ Database connection test failed: {db_test_error}")
                raise Exception(f"Database connection test failed: {db_test_error}")

            try:
                db_exec_start = time.time()
                logger.info(f"   Starting SQL execution on target database...")
                logger.info(f"   SQL to execute: {sql_with_limit[:200]}...")

                cursor = target_conn.cursor()

                # Execute SQL with explicit error handling
                try:
                    cursor.execute(sql_with_limit)
                    db_exec_time = (time.time() - db_exec_start) * 1000
                    logger.info(f"✅ SQL executed successfully on target database in {db_exec_time:.2f}ms")
                except Exception as sql_error:
                    db_exec_time = (time.time() - db_exec_start) * 1000
                    logger.error(f"❌ SQL execution failed on target database in {db_exec_time:.2f}ms")
                    logger.error(f"   SQL Error: {sql_error}")
                    logger.error(f"   SQL that failed: {sql_with_limit}")

                    # Provide more helpful error messages for common SQL Server issues
                    error_str = str(sql_error).lower()
                    if 'incorrect syntax near' in error_str:
                        if 'distinct' in error_str:
                            helpful_msg = "SQL Server syntax error: Use 'SELECT DISTINCT TOP N' instead of 'SELECT TOP N DISTINCT'"
                        elif 'limit' in error_str:
                            helpful_msg = "SQL Server doesn't support LIMIT clause. Use TOP clause instead."
                        else:
                            helpful_msg = f"SQL Server syntax error: {sql_error}"
                    elif 'invalid object name' in error_str:
                        helpful_msg = f"Table or view not found in SQL Server database: {sql_error}"
                    elif 'login failed' in error_str or 'cannot open database' in error_str:
                        helpful_msg = f"SQL Server connection/authentication error: {sql_error}"
                    else:
                        helpful_msg = f"SQL execution failed on SQL Server: {sql_error}"

                    raise Exception(helpful_msg)

                # Fetch results
                logger.info(f"📊 Fetching results from target database...")
                fetch_start = time.time()

                rows = cursor.fetchall()
                fetch_time = (time.time() - fetch_start) * 1000

                logger.info(f"✅ Fetched {len(rows)} rows from target database in {fetch_time:.2f}ms")

                # Convert rows to list of dictionaries with Java-safe conversion
                if rows and hasattr(cursor, 'description') and cursor.description:
                    column_names = [str(desc[0]) for desc in cursor.description]  # Convert Java strings
                    records = []
                    for row in rows:
                        # Convert each field from Java objects to Python objects
                        record = {}
                        for i, value in enumerate(row):
                            key = column_names[i]
                            # Convert Java strings and objects to Python equivalents
                            if value is None:
                                record[key] = None
                            elif hasattr(value, '__class__') and 'java' in str(value.__class__):
                                record[key] = str(value)  # Convert Java objects to strings
                            else:
                                record[key] = value  # Already Python object
                        records.append(record)
                else:
                    records = []
                    column_names = []

                execution_time_ms = (time.time() - start_time) * 1000

                logger.info(f"🎉 CACHED SQL EXECUTION ON TARGET DATABASE COMPLETED")
                logger.info(f"   Total Time: {execution_time_ms:.2f}ms")
                logger.info(f"   Records returned: {len(records)}")
                logger.info(f"   Target DB: {db_type}")

                # Format response
                return {
                    'generated_sql': sql,
                    'number_of_records': len(records),
                    'execution_status': 'success',
                    'execution_time_ms': execution_time_ms,
                    'confidence_score': 1.0,  # Cached SQL has 100% confidence
                    'data': records,
                    'error_message': None,
                    'join_columns': [],
                    'source_table': '',
                    'target_table': '',
                    'column_names': column_names,
                    'db_type': db_type,
                    'used_target_database': True
                }

            finally:
                cursor.close()
                target_conn.close()
                logger.info(f"🔌 Target database connection closed")

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            error_msg = str(e)

            logger.error(f"❌ CACHED SQL EXECUTION ON TARGET DATABASE FAILED")
            logger.error(f"   Error: {error_msg}")
            logger.error(f"   Execution time: {execution_time_ms:.2f}ms")
            logger.error(f"   Target DB Type: {db_type}")
            logger.error(f"   SQL that failed:")
            logger.error(f"\n{sql}\n")

            return {
                'generated_sql': sql,
                'number_of_records': 0,
                'execution_status': 'failed',
                'execution_time_ms': execution_time_ms,
                'confidence_score': 1.0,  # SQL was cached, failure is execution issue
                'data': [],
                'error_message': error_msg,
                'join_columns': [],
                'source_table': '',
                'target_table': '',
                'column_names': [],
                'db_type': db_type,
                'used_target_database': True
            }

    def _add_limit_clause(self, sql: str, limit: int, db_type: str = 'sqlserver') -> str:
        """Add LIMIT clause to SQL if not already present, using correct syntax for database type."""
        # Convert Java String to Python string if needed
        if hasattr(sql, '__class__') and 'java' in str(sql.__class__):
            sql = str(sql)

        sql_upper = str(sql).upper().strip()

        # Check if LIMIT already exists (MySQL/PostgreSQL)
        if 'LIMIT' in sql_upper:
            return sql

        # Check if TOP already exists (SQL Server syntax)
        if 'SELECT TOP' in sql_upper:
            return sql

        # Add appropriate limit syntax based on database type
        if db_type.lower() == 'sqlserver':
            # SQL Server uses TOP syntax
            # Handle different SELECT variations (SELECT, SELECT DISTINCT, etc.)
            if sql_upper.startswith('SELECT DISTINCT '):
                # "SELECT DISTINCT ..." -> "SELECT DISTINCT TOP {limit} ..."
                return f"SELECT DISTINCT TOP {limit} {str(sql)[16:]}"
            elif sql_upper.startswith('SELECT '):
                # "SELECT ..." -> "SELECT TOP {limit} ..."
                return f"SELECT TOP {limit} {str(sql)[7:]}"
            else:
                # Fallback: just return original SQL
                logger.warning(f"Cannot add TOP clause to SQL that doesn't start with SELECT: {sql[:50]}...")
                return str(sql)
        elif db_type.lower() in ['mysql', 'postgresql', 'postgres']:
            # MySQL, PostgreSQL use LIMIT syntax
            return f"{str(sql).rstrip(';')} LIMIT {limit}"
        else:
            # For unknown database types, try LIMIT syntax as fallback
            logger.warning(f"Unknown database type '{db_type}', using LIMIT syntax as fallback")
            return f"{str(sql).rstrip(';')} LIMIT {limit}"


# Singleton instance
_landing_kpi_service_jdbc: Optional[LandingKPIServiceJDBC] = None


def get_landing_kpi_service_jdbc() -> LandingKPIServiceJDBC:
    """Get or create Landing KPI Service JDBC singleton instance."""
    global _landing_kpi_service_jdbc
    if _landing_kpi_service_jdbc is None:
        _landing_kpi_service_jdbc = LandingKPIServiceJDBC()
    return _landing_kpi_service_jdbc
