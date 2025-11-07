"""
Landing KPI Service - MS SQL Server Version
Manages KPI definitions and execution results in MS SQL Server instead of SQLite.
"""

import logging
import json
import pyodbc
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from kg_builder.config import (
    SOURCE_DB_HOST, SOURCE_DB_PORT, SOURCE_DB_DATABASE, 
    SOURCE_DB_USERNAME, SOURCE_DB_PASSWORD
)

logger = logging.getLogger(__name__)


class LandingKPIServiceMSSQL:
    """Service for managing Landing KPI definitions and executions in MS SQL Server."""
    
    def __init__(self, 
                 host: str = None, 
                 port: int = None, 
                 database: str = None,
                 username: str = None, 
                 password: str = None):
        """Initialize the service with MS SQL Server connection parameters."""
        self.host = host or SOURCE_DB_HOST
        self.port = port or SOURCE_DB_PORT
        self.database = database or SOURCE_DB_DATABASE
        self.username = username or SOURCE_DB_USERNAME
        self.password = password or SOURCE_DB_PASSWORD
        
        logger.info(f"Initialized KPI Service for MS SQL Server: {self.host}:{self.port}/{self.database}")
    
    def _get_connection(self):
        """Get MS SQL Server database connection."""
        try:
            # Build connection string
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.host},{self.port};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
                f"TrustServerCertificate=yes;"
            )
            
            conn = pyodbc.connect(conn_str)
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to MS SQL Server: {e}")
            raise
    
    # ==================== KPI CRUD Operations ====================
    
    def create_kpi(self, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new KPI definition."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO kpi_definitions 
                (name, alias_name, group_name, description, nl_definition, created_by)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                kpi_data.get('name'),
                kpi_data.get('alias_name'),
                kpi_data.get('group_name'),
                kpi_data.get('description'),
                kpi_data.get('nl_definition'),
                kpi_data.get('created_by')
            ))
            
            kpi_id = cursor.fetchone()[0]
            conn.commit()
            logger.info(f"✓ Created KPI: {kpi_data.get('name')} (ID: {kpi_id})")
            return self.get_kpi(kpi_id)
            
        except pyodbc.IntegrityError as e:
            logger.error(f"❌ KPI name already exists: {e}")
            raise ValueError(f"KPI name '{kpi_data.get('name')}' already exists")
        finally:
            conn.close()
    
    def get_kpi(self, kpi_id: int) -> Optional[Dict[str, Any]]:
        """Get KPI by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, name, alias_name, group_name, description, nl_definition,
                       created_at, updated_at, created_by, is_active
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
                    'is_active': bool(row[9])
                }
            return None
        finally:
            conn.close()
    
    def get_all_kpis(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """Get all KPIs with their latest execution status."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            where_clause = "" if include_inactive else "WHERE k.is_active = 1"
            
            cursor.execute(f"""
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
                    'latest_execution': {
                        'id': row[10],
                        'timestamp': row[11].isoformat() if row[11] else None,
                        'status': row[12],
                        'record_count': row[13],
                        'generated_sql': row[14],  # Always include SQL
                        'error_message': row[15]
                    } if row[10] else None
                }
                kpis.append(kpi)
            
            logger.info(f"Retrieved {len(kpis)} KPIs")
            return kpis
        finally:
            conn.close()
    
    def update_kpi(self, kpi_id: int, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update KPI definition."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE kpi_definitions 
                SET name = ?, alias_name = ?, group_name = ?, description = ?, 
                    nl_definition = ?, updated_at = GETDATE()
                WHERE id = ?
            """, (
                kpi_data.get('name'),
                kpi_data.get('alias_name'),
                kpi_data.get('group_name'),
                kpi_data.get('description'),
                kpi_data.get('nl_definition'),
                kpi_id
            ))
            
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

    def execute_kpi(self, kpi_id: int, execution_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a KPI and return results with enhanced SQL."""
        # For now, just create an execution record
        # The actual execution will be handled by the executor service
        return self.create_execution_record(kpi_id, execution_params)

    def create_execution_record(self, kpi_id: int, execution_params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new execution record for a KPI."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO kpi_execution_results
                (kpi_id, kg_name, select_schema, db_type, limit_records, use_llm,
                 execution_status, user_id, session_id)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                kpi_id,
                execution_params.get('kg_name'),
                execution_params.get('select_schema'),
                execution_params.get('db_type', 'sqlserver'),
                execution_params.get('limit_records', 1000),
                execution_params.get('use_llm', True),
                'pending',
                execution_params.get('user_id'),
                execution_params.get('session_id')
            ))

            execution_id = cursor.fetchone()[0]
            conn.commit()
            logger.info(f"✓ Created execution record ID: {execution_id} for KPI ID: {kpi_id}")
            return self.get_execution_result(execution_id)
        finally:
            conn.close()

    def update_execution_result(self, execution_id: int, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update execution result with query results and ALWAYS store generated SQL."""
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
                result_data.get('generated_sql'),  # ALWAYS store SQL, even if execution failed
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
            logger.info(f"✓ Updated execution result ID: {execution_id} (SQL always stored)")
            return self.get_execution_result(execution_id)
        finally:
            conn.close()

    def get_execution_result(self, execution_id: int) -> Optional[Dict[str, Any]]:
        """Get execution result by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
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
            """, (execution_id,))

            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'kpi_id': row[1],
                    'kg_name': row[2],
                    'select_schema': row[3],
                    'db_type': row[4],
                    'limit_records': row[5],
                    'use_llm': bool(row[6]),
                    'generated_sql': row[7],  # Always include SQL
                    'number_of_records': row[8],
                    'joined_columns': json.loads(row[9]) if row[9] else [],
                    'sql_query_type': row[10],
                    'operation': row[11],
                    'execution_status': row[12],
                    'execution_timestamp': row[13].isoformat() if row[13] else None,
                    'execution_time_ms': row[14],
                    'confidence_score': row[15],
                    'error_message': row[16],
                    'result_data': json.loads(row[17]) if row[17] else [],
                    'evidence_data': json.loads(row[18]) if row[18] else [],
                    'evidence_count': row[19],
                    'source_table': row[20],
                    'target_table': row[21],
                    'user_id': row[22],
                    'session_id': row[23],
                    'kpi_name': row[24],
                    'kpi_alias_name': row[25]
                }
            return None
        finally:
            conn.close()

    def get_kpi_executions(self, kpi_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get execution history for a KPI."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(f"""
                SELECT TOP {limit}
                    id, execution_timestamp, execution_status, number_of_records,
                    execution_time_ms, generated_sql, error_message, evidence_count
                FROM kpi_execution_results
                WHERE kpi_id = ?
                ORDER BY execution_timestamp DESC
            """, (kpi_id,))

            executions = []
            for row in cursor.fetchall():
                executions.append({
                    'id': row[0],
                    'timestamp': row[1].isoformat() if row[1] else None,
                    'status': row[2],
                    'record_count': row[3],
                    'execution_time_ms': row[4],
                    'generated_sql': row[5],  # Always include SQL
                    'error_message': row[6],
                    'evidence_count': row[7]
                })

            return executions
        finally:
            conn.close()

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get all KPIs grouped by group name with their latest execution summary.

        Returns:
            Dictionary with structure:
            {
                "groups": [
                    {
                        "group_name": "Data Quality",
                        "kpis": [
                            {
                                "id": 1,
                                "name": "Inactive Products",
                                "nl_definition": "Show me all...",
                                "latest_execution": {
                                    "executed_at": "2025-10-28T13:50:55",
                                    "record_count": 42,
                                    "status": "success"
                                }
                            }
                        ]
                    }
                ]
            }
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get all active KPIs with their latest execution
            cursor.execute("""
                SELECT
                    k.id,
                    k.name,
                    k.nl_definition,
                    k.description,
                    k.group_name,
                    e.kg_name,
                    e.execution_timestamp,
                    e.number_of_records,
                    e.execution_status,
                    e.execution_time_ms,
                    e.error_message,
                    ROW_NUMBER() OVER (PARTITION BY k.id ORDER BY e.execution_timestamp DESC) as rn
                FROM kpi_definitions k
                LEFT JOIN kpi_execution_results e ON k.id = e.kpi_id
                WHERE k.is_active = 1
                ORDER BY k.created_at DESC
            """)

            rows = cursor.fetchall()

            # Group KPIs by group name
            group_dict = {}
            processed_kpis = set()

            for row in rows:
                kpi_id = row[0]

                # Only process the latest execution for each KPI (rn = 1)
                if row[11] != 1 and row[11] is not None:  # rn column
                    continue

                # Skip if we've already processed this KPI
                if kpi_id in processed_kpis:
                    continue

                processed_kpis.add(kpi_id)

                group_name = row[4] or 'Ungrouped'

                if group_name not in group_dict:
                    group_dict[group_name] = []

                kpi_entry = {
                    'id': kpi_id,
                    'name': row[1],
                    'nl_definition': row[2],
                    'description': row[3],
                    'kg_name': row[5]
                }

                # Add latest execution if available
                if row[6]:  # execution_timestamp
                    kpi_entry['latest_execution'] = {
                        'executed_at': row[6].isoformat() if hasattr(row[6], 'isoformat') else str(row[6]),
                        'record_count': row[7] or 0,
                        'status': row[8] or 'unknown',
                        'error_message': row[10]
                    }

                group_dict[group_name].append(kpi_entry)

            # Convert to list format
            groups = [
                {
                    'group_name': group_name,
                    'kpis': kpis
                }
                for group_name, kpis in sorted(group_dict.items())
            ]

            logger.info(f"✓ Dashboard data retrieved: {len(groups)} Groups with {sum(len(group['kpis']) for group in groups)} KPIs")
            return {'groups': groups}

        finally:
            conn.close()

    def get_latest_results(self, kpi_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the latest execution results for a specific KPI.

        Args:
            kpi_id: ID of the KPI

        Returns:
            Dictionary with execution results or None if no results found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get the latest execution for this KPI
            cursor.execute("""
                SELECT TOP 1
                    id,
                    kpi_id,
                    kg_name,
                    select_schema,
                    execution_timestamp,
                    execution_status,
                    number_of_records,
                    execution_time_ms,
                    generated_sql,
                    enhanced_sql,
                    result_data,
                    error_message,
                    evidence_count
                FROM kpi_execution_results
                WHERE kpi_id = ?
                ORDER BY execution_timestamp DESC
            """, (kpi_id,))

            row = cursor.fetchone()

            if not row:
                return None

            # Parse result_data if it's JSON
            result_data = []
            if row[10]:  # result_data column
                try:
                    result_data = json.loads(row[10]) if isinstance(row[10], str) else row[10]
                except (json.JSONDecodeError, TypeError):
                    result_data = []

            # Extract column names from result data
            column_names = []
            if result_data and len(result_data) > 0:
                column_names = list(result_data[0].keys()) if isinstance(result_data[0], dict) else []

            return {
                'execution_id': row[0],
                'kpi_id': row[1],
                'kg_name': row[2],
                'select_schema': row[3],
                'execution_timestamp': row[4].isoformat() if hasattr(row[4], 'isoformat') else str(row[4]),
                'execution_status': row[5],
                'record_count': row[6] or 0,
                'execution_time_ms': row[7],
                'sql_query': row[8],  # generated_sql
                'enhanced_sql': row[9],  # enhanced_sql with ops_planner
                'result_data': result_data,
                'column_names': column_names,
                'error_message': row[11],
                'evidence_count': row[12] or 0
            }

        finally:
            conn.close()
