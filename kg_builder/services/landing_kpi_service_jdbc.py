"""
Landing KPI Service using JDBC (Working Alternative to pyodbc)
Uses the existing JDBC infrastructure that's already working in the system.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import glob
import os

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
            
            # Connect using jaydebeapi (same as other services)
            conn = jaydebeapi.connect(
                driver_class,
                jdbc_url,
                [self.username, self.password],
                driver_jar
            )
            
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
                # First check if cache fields exist
                cursor.execute("SELECT TOP 1 isAccept FROM kpi_definitions")
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
                kpis.append(kpi)
            
            logger.info(f"Retrieved {len(kpis)} KPIs via JDBC")
            return kpis
            
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
                 isAccept, isSQLCached, cached_sql)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                kpi_data.get('name'),
                kpi_data.get('alias_name'),
                kpi_data.get('group_name'),
                kpi_data.get('description'),
                kpi_data.get('nl_definition'),
                kpi_data.get('created_by'),
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

            # Add updated_at timestamp (SQL Server syntax)
            updates.append("updated_at = GETDATE()")
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
                cursor.execute("SELECT TOP 1 isAccept, isSQLCached, cached_sql FROM kpi_definitions WHERE id = ?", (kpi_id,))
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

            updates.append("updated_at = GETDATE()")
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
                cursor.execute("SELECT TOP 1 isAccept, isSQLCached, cached_sql FROM kpi_definitions WHERE id = ?", (kpi_id,))
                cache_fields_exist = True
            except Exception:
                logger.warning("Cache fields don't exist in database yet. Please run the migration script.")
                cache_fields_exist = False

            if not cache_fields_exist:
                logger.info(f"Cache fields not available, skipping cache clear for KPI {kpi_id}")
                return self.get_kpi(kpi_id)

            cursor.execute("""
                UPDATE kpi_definitions
                SET isAccept = 0, isSQLCached = 0, cached_sql = NULL, updated_at = GETDATE()
                WHERE id = ?
            """, (kpi_id,))

            if cursor.rowcount == 0:
                raise ValueError(f"KPI with ID {kpi_id} not found")

            conn.commit()
            logger.info(f"✓ Cleared cache flags for KPI ID: {kpi_id}")
            return self.get_kpi(kpi_id)

        except Exception as e:
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
                cursor.execute("SELECT TOP 1 isAccept FROM kpi_definitions")
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
            cursor.execute("""
                INSERT INTO kpi_execution_results
                (kpi_id, kg_name, select_schema, db_type, limit_records, use_llm,
                 execution_status, user_id, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                kpi_id,
                execution_params.get('kg_name', 'default'),
                execution_params.get('select_schema', 'newdqschemanov'),
                execution_params.get('db_type', 'sqlserver'),
                execution_params.get('limit_records', 1000),
                execution_params.get('use_llm', True),
                'pending',
                execution_params.get('user_id'),
                execution_params.get('session_id')
            ))

            # Get the inserted ID
            cursor.execute("SELECT @@IDENTITY")
            execution_id = cursor.fetchone()[0]

            conn.commit()
            logger.info(f"✓ Created execution record ID: {execution_id} for KPI ID: {kpi_id}")

            return {
                'id': execution_id,
                'kpi_id': kpi_id,
                'execution_status': 'pending',
                'kg_name': execution_params.get('kg_name', 'default'),
                'select_schema': execution_params.get('select_schema', 'newdqschemanov')
            }

        except Exception as e:
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

        try:
            # Get the KPI definition
            kpi = self.get_kpi(kpi_id)
            if not kpi:
                raise ValueError(f"KPI with ID {kpi_id} not found")

            # Extract execution parameters
            kg_name = execution_params.get('kg_name', 'default')
            schemas = execution_params.get('schemas', ['newdqschemanov'])
            select_schema = schemas[0] if schemas else 'newdqschemanov'
            use_llm = execution_params.get('use_llm', True)
            limit_records = execution_params.get('limit', 1000)
            db_type = execution_params.get('db_type', 'sqlserver')

            # Load Knowledge Graph for join column inference
            from kg_builder.services.graphiti_backend import get_graphiti_backend
            from kg_builder.models import KnowledgeGraph, GraphNode, GraphRelationship

            logger.info(f"Loading Knowledge Graph: {kg_name}")
            graphiti = get_graphiti_backend()
            entities_data = graphiti.get_entities(kg_name)
            relationships_data = graphiti.get_relationships(kg_name)

            # Convert to KnowledgeGraph object
            nodes = [GraphNode(**entity) for entity in entities_data] if entities_data else []
            relationships = [GraphRelationship(**rel) for rel in relationships_data] if relationships_data else []

            # Load metadata including table_aliases
            table_aliases = {}
            try:
                kg_metadata = graphiti.get_kg_metadata(kg_name)
                if kg_metadata:
                    table_aliases = kg_metadata.get('table_aliases', {})
            except Exception as e:
                logger.warning(f"Could not load KG metadata: {e}")

            kg = KnowledgeGraph(
                name=kg_name,
                nodes=nodes,
                relationships=relationships,
                schema_file=select_schema,
                table_aliases=table_aliases
            )
            logger.info(f"✓ Loaded KG '{kg_name}' with {len(nodes)} nodes and {len(relationships)} relationships")

            # Execute the KPI using the existing NL query system with KG
            from kg_builder.services.nl_query_executor import NLQueryExecutor
            from kg_builder.services.nl_query_parser import get_nl_query_parser

            # Extract schemas_info from KG for LLM prompt
            def _extract_schemas_info_from_kg(kg):
                schemas_info = {}
                for node in kg.nodes:
                    if node.properties.get("type") == "Table":
                        schema_name = node.properties.get("schema", select_schema)
                        if schema_name not in schemas_info:
                            schemas_info[schema_name] = {"tables": {}}

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

                # Convert to list of dictionaries
                records = []
                for row in rows:
                    record = {}
                    for i, value in enumerate(row):
                        if i < len(columns):
                            record[columns[i]] = value
                    records.append(record)

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
                'execution_timestamp': datetime.now().isoformat()
            }

            # Store execution result in database
            execution_id = self.store_execution_result(execution_record)

            # Return comprehensive result
            return {
                'success': True,
                'execution_id': execution_id,
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
                'data': result.records,
                'error_message': execution_record['error_message']
            }

        except Exception as e:
            # Store failed execution
            execution_time_ms = int((time.time() - start_time) * 1000)

            execution_record = {
                'kpi_id': kpi_id,
                'kg_name': execution_params.get('kg_name', 'default'),
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
                'execution_timestamp': datetime.now().isoformat()
            }

            try:
                execution_id = self.store_execution_result(execution_record)
            except Exception as store_error:
                logger.error(f"Failed to store error execution result: {store_error}")
                execution_id = None

            return {
                'success': False,
                'execution_id': execution_id,
                'kpi_id': kpi_id,
                'execution_status': 'error',
                'error_message': str(e),
                'execution_time_ms': execution_time_ms
            }

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
                    target_table = ?
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
            # Insert execution result
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

            # Get the inserted ID
            cursor.execute("SELECT @@IDENTITY")
            execution_id = cursor.fetchone()[0]

            # Commit the transaction
            conn.commit()

            logger.info(f"✓ Stored execution result with ID {execution_id}")
            return execution_id

        except Exception as e:
            logger.error(f"❌ Failed to store execution result: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_latest_results(self, kpi_id: int) -> Optional[Dict[str, Any]]:
        """Get the latest execution results for a specific KPI."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT TOP 1
                    id, kpi_id, kg_name, select_schema, generated_sql,
                    number_of_records, execution_status, execution_timestamp,
                    execution_time_ms, confidence_score, error_message, result_data
                FROM kpi_execution_results
                WHERE kpi_id = ? AND execution_status = 'success' AND result_data IS NOT NULL
                ORDER BY execution_timestamp DESC
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
                    parsed_data = json.loads(row[11])

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

            return {
                'execution_id': row[0],
                'kpi_id': row[1],
                'kg_name': row[2],
                'select_schema': row[3],
                'generated_sql': row[4],
                'number_of_records': row[5],
                'execution_status': row[6],
                'execution_timestamp': str(row[7]) if row[7] else None,
                'execution_time_ms': row[8],
                'confidence_score': row[9],
                'error_message': row[10],
                'result_data': result_data,
                'column_names': column_names,
                'record_count': row[5]  # Alias for compatibility
            }

        except Exception as e:
            logger.error(f"Error getting latest results for KPI {kpi_id}: {e}")
            return None

        finally:
            cursor.close()
            conn.close()


# Singleton instance
_landing_kpi_service_jdbc: Optional[LandingKPIServiceJDBC] = None


def get_landing_kpi_service_jdbc() -> LandingKPIServiceJDBC:
    """Get or create Landing KPI Service JDBC singleton instance."""
    global _landing_kpi_service_jdbc
    if _landing_kpi_service_jdbc is None:
        _landing_kpi_service_jdbc = LandingKPIServiceJDBC()
    return _landing_kpi_service_jdbc
