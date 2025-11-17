"""
Landing KPI Service

Handles CRUD operations for KPI definitions and execution management.
"""

import sqlite3
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class LandingKPIService:
    """Service for managing Landing KPI definitions and executions."""
    
    def __init__(self, db_path: str = "data/landing_kpi.db"):
        """Initialize the service with database path."""
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database exists and is initialized."""
        if not Path(self.db_path).exists():
            logger.warning(f"Database not found at {self.db_path}. Please run init_landing_kpi_db.py")
    
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ==================== KPI CRUD Operations ====================
    
    def create_kpi(self, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new KPI definition."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO kpi_definitions 
                (name, alias_name, group_name, description, nl_definition, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                kpi_data.get('name'),
                kpi_data.get('alias_name'),
                kpi_data.get('group_name'),
                kpi_data.get('description'),
                kpi_data.get('nl_definition'),
                kpi_data.get('created_by')
            ))
            conn.commit()
            kpi_id = cursor.lastrowid
            logger.info(f"✓ Created KPI: {kpi_data.get('name')} (ID: {kpi_id})")
            return self.get_kpi(kpi_id)
        except sqlite3.IntegrityError as e:
            logger.error(f"❌ KPI name already exists: {e}")
            raise ValueError(f"KPI name '{kpi_data.get('name')}' already exists")
        finally:
            conn.close()
    
    def get_kpi(self, kpi_id: int) -> Optional[Dict[str, Any]]:
        """Get a KPI definition by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM kpi_definitions WHERE id = ?", (kpi_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def list_kpis(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List KPI definitions with optional filters."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            query = "SELECT * FROM kpi_definitions WHERE 1=1"
            params = []
            
            if filters:
                if filters.get('is_active') is not None:
                    query += " AND is_active = ?"
                    params.append(filters['is_active'])
                
                if filters.get('group_name'):
                    query += " AND group_name = ?"
                    params.append(filters['group_name'])
                
                if filters.get('search'):
                    query += " AND (name LIKE ? OR description LIKE ?)"
                    search_term = f"%{filters['search']}%"
                    params.extend([search_term, search_term])
            
            query += " ORDER BY created_at DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def update_kpi(self, kpi_id: int, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a KPI definition."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Build dynamic update query
            updates = []
            params = []
            
            for key in ['name', 'alias_name', 'group_name', 'description', 'nl_definition', 'is_active']:
                if key in kpi_data and kpi_data[key] is not None:
                    updates.append(f"{key} = ?")
                    params.append(kpi_data[key])
            
            if not updates:
                return self.get_kpi(kpi_id)
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(kpi_id)
            
            query = f"UPDATE kpi_definitions SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            logger.info(f"✓ Updated KPI ID: {kpi_id}")
            return self.get_kpi(kpi_id)
        finally:
            conn.close()
    
    def delete_kpi(self, kpi_id: int) -> bool:
        """Soft delete a KPI (mark as inactive)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE kpi_definitions 
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (kpi_id,))
            conn.commit()
            logger.info(f"✓ Deleted KPI ID: {kpi_id}")
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    # ==================== KPI Execution Operations ====================
    
    def execute_kpi(self, kpi_id: int, execution_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a KPI and store results."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Handle new payload structure
            # New structure: kg_name, schemas (list), definitions (list), use_llm, min_confidence, limit, db_type
            # Old structure: kg_name, select_schema, ruleset_name, db_type, limit_records, use_llm, excluded_fields

            # Extract and validate parameters - support both old and new formats
            kg_name = execution_params.get('kg_name')

            # Validate kg_name is provided and not default
            if not kg_name or kg_name.strip() == '' or kg_name.lower() == 'default':
                raise ValueError(
                    "kg_name is required and cannot be empty or 'default'. "
                    "Please provide a valid Knowledge Graph name (e.g., 'New_KG_101', 'KG_102')."
                )

            schemas = execution_params.get('schemas', [])
            select_schema = execution_params.get('select_schema') or (schemas[0] if schemas else None)
            definitions = execution_params.get('definitions', [])
            use_llm = execution_params.get('use_llm', True)
            min_confidence = execution_params.get('min_confidence', 0.7)
            limit_records = execution_params.get('limit', execution_params.get('limit_records', 1000))
            db_type = execution_params.get('db_type', 'sqlserver')

            # Store definitions and min_confidence as JSON
            definitions_json = json.dumps(definitions)

            cursor.execute("""
                INSERT INTO kpi_execution_results
                (kpi_id, kg_name, select_schema, db_type,
                 limit_records, use_llm, execution_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                kpi_id,
                kg_name,
                select_schema,
                db_type,
                limit_records,
                use_llm,
                'pending'
            ))
            conn.commit()
            execution_id = cursor.lastrowid
            logger.info(f"✓ Created execution record ID: {execution_id} for KPI ID: {kpi_id}")
            logger.info(f"  Schemas: {schemas}, Definitions: {definitions}, Min Confidence: {min_confidence}")
            return self.get_execution_result(execution_id)
        finally:
            conn.close()
    
    def update_execution_result(self, execution_id: int, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update execution result with query results."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Prepare data
            result_json = json.dumps(result_data.get('result_data', []))
            joined_columns_json = json.dumps(result_data.get('joined_columns', []))
            
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
                result_data.get('source_table'),
                result_data.get('target_table'),
                execution_id
            ))
            conn.commit()
            logger.info(f"✓ Updated execution result ID: {execution_id}")
            return self.get_execution_result(execution_id)
        finally:
            conn.close()
    
    def get_execution_result(self, execution_id: int) -> Optional[Dict[str, Any]]:
        """Get execution result by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM kpi_execution_results WHERE id = ?
            """, (execution_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            result = dict(row)
            # Parse JSON fields
            if result.get('excluded_fields'):
                result['excluded_fields'] = json.loads(result['excluded_fields'])
            if result.get('joined_columns'):
                result['joined_columns'] = json.loads(result['joined_columns'])
            if result.get('result_data'):
                result['result_data'] = json.loads(result['result_data'])
            
            return result
        finally:
            conn.close()
    
    def get_execution_results(self, kpi_id: int, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get execution results for a KPI."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            query = "SELECT * FROM kpi_execution_results WHERE kpi_id = ?"
            params = [kpi_id]
            
            if filters:
                if filters.get('status'):
                    query += " AND execution_status = ?"
                    params.append(filters['status'])
            
            query += " ORDER BY execution_timestamp DESC"
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                # Parse JSON fields
                if result.get('excluded_fields'):
                    result['excluded_fields'] = json.loads(result['excluded_fields'])
                if result.get('joined_columns'):
                    result['joined_columns'] = json.loads(result['joined_columns'])
                results.append(result)
            
            return results
        finally:
            conn.close()
    
    def get_drilldown_data(self, execution_id: int, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """Get paginated drill-down data for execution result."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get execution result
            execution = self.get_execution_result(execution_id)
            if not execution:
                raise ValueError(f"Execution ID {execution_id} not found")

            result_data = execution.get('result_data', [])
            total = len(result_data)

            # Calculate pagination
            offset = (page - 1) * page_size
            paginated_data = result_data[offset:offset + page_size]
            total_pages = (total + page_size - 1) // page_size

            return {
                'execution_id': execution_id,
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': total_pages,
                'data': paginated_data
            }
        finally:
            conn.close()

    # ==================== Dashboard Operations ====================

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
                                "definition": "Show me all...",
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

            # Group by group_name
            group_dict = {}
            for row in rows:
                row_dict = dict(row)

                # Skip if this is not the latest execution for this KPI
                if row_dict.get('rn') and row_dict['rn'] > 1:
                    continue

                group_name = row_dict.get('group_name') or 'Ungrouped'

                if group_name not in group_dict:
                    group_dict[group_name] = []

                kpi_entry = {
                    'id': row_dict['id'],
                    'name': row_dict['name'],
                    'definition': row_dict['nl_definition'],
                    'description': row_dict.get('description'),
                    'kg_name': row_dict.get('kg_name'),
                    'latest_execution': None
                }

                # Add latest execution if available (excluding execution_time_ms)
                if row_dict.get('execution_timestamp'):
                    kpi_entry['latest_execution'] = {
                        'executed_at': row_dict['execution_timestamp'],
                        'record_count': row_dict.get('number_of_records', 0),
                        'status': row_dict.get('execution_status', 'unknown'),
                        'error_message': row_dict.get('error_message')
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
        Get the SQL results from the most recent execution for a specific KPI.

        Returns:
            Dictionary with SQL query, result data, column names, and metadata
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get the latest execution for this KPI
            cursor.execute("""
                SELECT * FROM kpi_execution_results
                WHERE kpi_id = ?
                ORDER BY execution_timestamp DESC
                LIMIT 1
            """, (kpi_id,))

            row = cursor.fetchone()
            if not row:
                return None

            execution = dict(row)

            # Parse JSON fields
            if execution.get('result_data'):
                execution['result_data'] = json.loads(execution['result_data'])
            if execution.get('joined_columns'):
                execution['joined_columns'] = json.loads(execution['joined_columns'])

            # Extract column names from result data
            column_names = []
            if execution.get('result_data') and len(execution['result_data']) > 0:
                column_names = list(execution['result_data'][0].keys())

            return {
                'execution_id': execution['id'],
                'kpi_id': kpi_id,
                'sql_query': execution.get('generated_sql'),
                'result_data': execution.get('result_data', []),
                'column_names': column_names,
                'record_count': execution.get('number_of_records', 0),
                'execution_status': execution.get('execution_status'),
                'execution_timestamp': execution.get('execution_timestamp'),
                'execution_time_ms': execution.get('execution_time_ms'),
                'confidence_score': execution.get('confidence_score'),
                'error_message': execution.get('error_message'),
                'source_table': execution.get('source_table'),
                'target_table': execution.get('target_table'),
                'operation': execution.get('operation')
            }

        finally:
            conn.close()

