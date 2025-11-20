"""
KPI Analytics Service - Separate Database Version
Manages KPI definitions and execution results in dedicated KPI_Analytics database.
"""

import logging
import json
import pyodbc
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class KPIAnalyticsService:
    """Service for managing KPI analytics in separate dedicated database."""
    
    def __init__(self, 
                 host: str = None, 
                 port: int = None, 
                 kpi_database: str = "KPI_Analytics",
                 username: str = None, 
                 password: str = None):
        """Initialize the service with KPI Analytics database connection."""
        # Import config here to avoid circular imports
        from kg_builder.config import (
            SOURCE_DB_HOST, SOURCE_DB_PORT, SOURCE_DB_USERNAME, SOURCE_DB_PASSWORD
        )
        
        self.host = host or SOURCE_DB_HOST
        self.port = port or SOURCE_DB_PORT
        self.kpi_database = kpi_database  # Dedicated KPI database
        self.username = username or SOURCE_DB_USERNAME
        self.password = password or SOURCE_DB_PASSWORD
        
        logger.info(f"Initialized KPI Analytics Service: {self.host}:{self.port}/{self.kpi_database}")
    
    def _get_connection(self):
        """Get KPI Analytics database connection."""
        try:
            # Handle named SQL Server instances (contains backslash)
            if '\\' in self.host:
                # Named instance - don't include port
                server_part = self.host
            else:
                # Default instance or IP - include port
                server_part = f"{self.host},{self.port}"

            # Build connection string for KPI database
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server_part};"
                f"DATABASE={self.kpi_database};"
                f"UID={self.username};"
                f"PWD={self.password};"
                f"TrustServerCertificate=yes;"
            )

            conn = pyodbc.connect(conn_str)
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to KPI Analytics database: {e}")
            raise
    
    # ==================== KPI CRUD Operations ====================
    
    def create_kpi(self, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new KPI definition in KPI Analytics database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO kpi_definitions
                (name, alias_name, group_name, description, nl_definition, created_by,
                 business_priority, target_sla_seconds, execution_frequency, data_retention_days,
                 group_id, dashboard_id, dashboard_name)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                kpi_data.get('name'),
                kpi_data.get('alias_name'),
                kpi_data.get('group_name'),
                kpi_data.get('description'),
                kpi_data.get('nl_definition'),
                kpi_data.get('created_by'),
                kpi_data.get('business_priority', 'medium'),
                kpi_data.get('target_sla_seconds', 30),
                kpi_data.get('execution_frequency', 'on_demand'),
                kpi_data.get('data_retention_days', 90),
                kpi_data.get('group_id'),
                kpi_data.get('dashboard_id'),
                kpi_data.get('dashboard_name')
            ))
            
            kpi_id = cursor.fetchone()[0]
            conn.commit()
            logger.info(f"✓ Created KPI in Analytics DB: {kpi_data.get('name')} (ID: {kpi_id})")
            return self.get_kpi(kpi_id)
            
        except pyodbc.IntegrityError as e:
            logger.error(f"❌ KPI name already exists: {e}")
            raise ValueError(f"KPI name '{kpi_data.get('name')}' already exists")
        finally:
            conn.close()
    
    def get_kpi(self, kpi_id: int) -> Optional[Dict[str, Any]]:
        """Get KPI by ID from Analytics database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, name, alias_name, group_name, description, nl_definition,
                       created_at, updated_at, created_by, is_active, business_priority,
                       target_sla_seconds, execution_frequency, data_retention_days,
                       group_id, dashboard_id, dashboard_name
                FROM kpi_definitions
                WHERE id = ?
            """, (kpi_id,))

            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'alias_name': row[2],
                    'group_name': row[3],
                    'description': row[4],
                    'nl_definition': row[5],
                    'created_at': row[6].isoformat() if row[6] else None,
                    'updated_at': row[7].isoformat() if row[7] else None,
                    'created_by': row[8],
                    'is_active': bool(row[9]),
                    'business_priority': row[10],
                    'target_sla_seconds': row[11],
                    'execution_frequency': row[12],
                    'data_retention_days': row[13],
                    'group_id': row[14],
                    'dashboard_id': row[15],
                    'dashboard_name': row[16],
                    'database': self.kpi_database
                }
            return None
        finally:
            conn.close()
    
    def get_all_kpis(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """Get all KPIs with their latest execution status from Analytics database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            where_clause = "" if include_inactive else "WHERE k.is_active = 1"
            
            cursor.execute(f"""
                SELECT
                    k.id, k.name, k.alias_name, k.group_name, k.description, k.nl_definition,
                    k.created_at, k.updated_at, k.created_by, k.is_active, k.business_priority,
                    k.target_sla_seconds, k.execution_frequency, k.data_retention_days,
                    k.group_id, k.dashboard_id, k.dashboard_name,
                    e.id as latest_execution_id,
                    e.execution_timestamp as latest_execution,
                    e.execution_status as latest_status,
                    e.number_of_records as latest_record_count,
                    e.generated_sql as latest_sql,
                    e.enhanced_sql as latest_enhanced_sql,
                    e.error_message as latest_error,
                    e.execution_time_ms as latest_execution_time
                FROM kpi_definitions k
                LEFT JOIN kpi_execution_results e ON k.id = e.kpi_id
                    AND e.execution_timestamp = (
                        SELECT MAX(execution_timestamp)
                        FROM kpi_execution_results
                        WHERE kpi_id = k.id
                    )
                {where_clause}
                ORDER BY k.business_priority DESC, k.group_name, k.name
            """)
            
            kpis = []
            for row in cursor.fetchall():
                kpi = {
                    'id': row[0],
                    'name': row[1],
                    'alias_name': row[2],
                    'group_name': row[3],
                    'description': row[4],
                    'nl_definition': row[5],
                    'created_at': row[6].isoformat() if row[6] else None,
                    'updated_at': row[7].isoformat() if row[7] else None,
                    'created_by': row[8],
                    'is_active': bool(row[9]),
                    'business_priority': row[10],
                    'target_sla_seconds': row[11],
                    'execution_frequency': row[12],
                    'data_retention_days': row[13],
                    'group_id': row[14],
                    'dashboard_id': row[15],
                    'dashboard_name': row[16],
                    'database': self.kpi_database,
                    'latest_execution': {
                        'id': row[17],
                        'timestamp': row[18].isoformat() if row[18] else None,
                        'status': row[19],
                        'record_count': row[20],
                        'generated_sql': row[21],  # Always include original SQL
                        'enhanced_sql': row[22],   # Always include enhanced SQL
                        'error_message': row[23],
                        'execution_time_ms': row[24]
                    } if row[17] else None
                }
                kpis.append(kpi)
            
            logger.info(f"Retrieved {len(kpis)} KPIs from Analytics database")
            return kpis
        finally:
            conn.close()

    def update_kpi(self, kpi_id: int, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update KPI definition in Analytics database."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Build dynamic update query to only update provided fields
            updates = []
            params = []

            field_mappings = {
                'name': 'name',
                'alias_name': 'alias_name',
                'group_name': 'group_name',
                'description': 'description',
                'nl_definition': 'nl_definition',
                'is_active': 'is_active',
                'business_priority': 'business_priority',
                'target_sla_seconds': 'target_sla_seconds',
                'execution_frequency': 'execution_frequency',
                'data_retention_days': 'data_retention_days',
                'group_id': 'group_id',
                'dashboard_id': 'dashboard_id',
                'dashboard_name': 'dashboard_name'
            }

            for key, db_field in field_mappings.items():
                if key in kpi_data and kpi_data[key] is not None:
                    updates.append(f"{db_field} = ?")
                    params.append(kpi_data[key])

            if not updates:
                return self.get_kpi(kpi_id)

            updates.append("updated_at = GETDATE()")
            params.append(kpi_id)

            query = f"UPDATE kpi_definitions SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)

            if cursor.rowcount == 0:
                raise ValueError(f"KPI with ID {kpi_id} not found")

            conn.commit()
            logger.info(f"✓ Updated KPI ID: {kpi_id}")
            return self.get_kpi(kpi_id)
        finally:
            conn.close()

    def delete_kpi(self, kpi_id: int) -> bool:
        """Delete KPI definition (soft delete by setting is_active = False)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE kpi_definitions
                SET is_active = 0, updated_at = GETDATE()
                WHERE id = ?
            """, (kpi_id,))

            if cursor.rowcount == 0:
                return False

            conn.commit()
            logger.info(f"✓ Deactivated KPI ID: {kpi_id}")
            return True
        finally:
            conn.close()

    # ==================== KPI Execution Operations ====================

    def create_execution_record(self, kpi_id: int, execution_params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new execution record in KPI Analytics database."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO kpi_execution_results
                (kpi_id, kg_name, select_schema, db_type, limit_records, use_llm,
                 execution_status, user_id, session_id, client_ip, user_agent)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                kpi_id,
                execution_params.get('kg_name'),
                execution_params.get('select_schema'),
                execution_params.get('db_type', 'sqlserver'),
                execution_params.get('limit_records', 1000),
                execution_params.get('use_llm', True),
                'pending',
                execution_params.get('user_id'),
                execution_params.get('session_id'),
                execution_params.get('client_ip'),
                execution_params.get('user_agent')
            ))

            execution_id = cursor.fetchone()[0]
            conn.commit()
            logger.info(f"✓ Created execution record in Analytics DB: ID {execution_id} for KPI {kpi_id}")
            return self.get_execution_result(execution_id)
        finally:
            conn.close()

    def update_execution_result(self, execution_id: int, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update execution result in KPI Analytics database with BOTH original and enhanced SQL."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Convert complex data to JSON
            joined_columns_json = json.dumps(result_data.get('joined_columns', []))
            result_json = json.dumps(result_data.get('result_data', []))
            evidence_json = json.dumps(result_data.get('evidence_data', []))

            # Enhance the SQL with material master and ops_planner if not already enhanced
            original_sql = result_data.get('generated_sql')
            enhanced_sql = result_data.get('enhanced_sql')

            if original_sql and not enhanced_sql:
                from kg_builder.services.material_master_enhancer import material_master_enhancer
                enhancement_result = material_master_enhancer.enhance_sql_with_material_master(original_sql)
                if enhancement_result['enhancement_applied']:
                    enhanced_sql = enhancement_result['enhanced_sql']
                    logger.info(f"✅ Enhanced SQL with material master and ops_planner for execution ID: {execution_id} - material_master={enhancement_result['material_master_added']}, ops_planner={enhancement_result['ops_planner_added']}")
                else:
                    enhanced_sql = original_sql  # Use original if no enhancement needed

            cursor.execute("""
                UPDATE kpi_execution_results
                SET
                    generated_sql = ?,
                    enhanced_sql = ?,
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
                result_data.get('generated_sql'),      # Original SQL
                result_data.get('enhanced_sql'),       # Enhanced SQL with ops_planner
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
            logger.info(f"✓ Updated execution result in Analytics DB: ID {execution_id}")
            return self.get_execution_result(execution_id)
        finally:
            conn.close()
