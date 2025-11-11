"""
Schedule Execution Service
Manages KPI schedule execution records and integrates with Airflow
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import pyodbc

logger = logging.getLogger(__name__)

class ScheduleExecutionService:
    """Service for managing KPI schedule execution records"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    def _get_connection(self):
        """Get database connection"""
        return pyodbc.connect(self.connection_string)
    
    def create_execution_record(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new execution record
        
        Args:
            execution_data: Dictionary containing execution information
                {
                    "schedule_id": 123,
                    "kpi_id": 456,
                    "scheduled_time": "2024-01-01T09:00:00",
                    "actual_start_time": "2024-01-01T09:00:05",
                    "execution_status": "running",
                    "airflow_task_id": "execute_kpi",
                    "airflow_run_id": "scheduled__2024-01-01T09:00:00+00:00"
                }
        
        Returns:
            Created execution record with ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            insert_query = """
                INSERT INTO kpi_schedule_executions (
                    schedule_id, kpi_id, scheduled_time, actual_start_time,
                    execution_status, airflow_task_id, airflow_run_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(insert_query, (
                execution_data['schedule_id'],
                execution_data['kpi_id'],
                execution_data['scheduled_time'],
                execution_data.get('actual_start_time'),
                execution_data.get('execution_status', 'pending'),
                execution_data.get('airflow_task_id'),
                execution_data.get('airflow_run_id')
            ))
            
            # Get the created execution ID
            cursor.execute("SELECT @@IDENTITY")
            execution_id = cursor.fetchone()[0]
            
            conn.commit()
            
            logger.info(f"✓ Created execution record {execution_id} for schedule {execution_data['schedule_id']}")
            
            # Return the created execution record
            return self.get_execution_record(execution_id)
            
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to create execution record: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_execution_record(self, execution_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an execution record"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Build dynamic update query
            update_fields = []
            params = []
            
            allowed_fields = [
                'actual_start_time', 'actual_end_time', 'execution_status',
                'error_message', 'retry_count', 'execution_id'
            ]
            
            for field in allowed_fields:
                if field in update_data:
                    update_fields.append(f"{field} = ?")
                    params.append(update_data[field])
            
            if not update_fields:
                raise ValueError("No valid fields to update")
            
            # Add updated_at
            update_fields.append("updated_at = GETDATE()")
            params.append(execution_id)
            
            query = f"UPDATE kpi_schedule_executions SET {', '.join(update_fields)} WHERE id = ?"
            
            cursor.execute(query, params)
            
            if cursor.rowcount == 0:
                raise ValueError(f"Execution record {execution_id} not found")
            
            conn.commit()
            
            logger.info(f"✓ Updated execution record {execution_id}")
            
            # Return updated execution record
            return self.get_execution_record(execution_id)
            
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to update execution record {execution_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_execution_record(self, execution_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific execution record by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT 
                    e.id, e.schedule_id, e.kpi_id, e.execution_id,
                    e.scheduled_time, e.actual_start_time, e.actual_end_time,
                    e.execution_status, e.airflow_task_id, e.airflow_run_id,
                    e.error_message, e.retry_count, e.max_retries,
                    e.created_at, e.updated_at,
                    s.schedule_name, k.name as kpi_name
                FROM kpi_schedule_executions e
                JOIN kpi_schedules s ON e.schedule_id = s.id
                JOIN kpi_definitions k ON e.kpi_id = k.id
                WHERE e.id = ?
            """
            
            cursor.execute(query, (execution_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            execution = {
                'id': row[0],
                'schedule_id': row[1],
                'kpi_id': row[2],
                'execution_id': row[3],
                'scheduled_time': row[4].isoformat() if row[4] else None,
                'actual_start_time': row[5].isoformat() if row[5] else None,
                'actual_end_time': row[6].isoformat() if row[6] else None,
                'execution_status': row[7],
                'airflow_task_id': row[8],
                'airflow_run_id': row[9],
                'error_message': row[10],
                'retry_count': row[11],
                'max_retries': row[12],
                'created_at': row[13].isoformat() if row[13] else None,
                'updated_at': row[14].isoformat() if row[14] else None,
                'schedule_name': row[15],
                'kpi_name': row[16]
            }
            
            return execution
            
        except Exception as e:
            logger.error(f"❌ Failed to get execution record {execution_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_executions_by_schedule(self, schedule_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get execution history for a specific schedule"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = f"""
                SELECT TOP {limit}
                    e.id, e.scheduled_time, e.actual_start_time, e.actual_end_time,
                    e.execution_status, e.error_message, e.retry_count,
                    e.airflow_task_id, e.airflow_run_id, e.execution_id
                FROM kpi_schedule_executions e
                WHERE e.schedule_id = ?
                ORDER BY e.scheduled_time DESC
            """

            cursor.execute(query, (schedule_id,))
            rows = cursor.fetchall()

            executions = []
            for row in rows:
                execution = {
                    'id': row[0],
                    'scheduled_time': row[1].isoformat() if row[1] else None,
                    'actual_start_time': row[2].isoformat() if row[2] else None,
                    'actual_end_time': row[3].isoformat() if row[3] else None,
                    'execution_status': row[4],
                    'error_message': row[5],
                    'retry_count': row[6],
                    'airflow_task_id': row[7],
                    'airflow_run_id': row[8],
                    'execution_id': row[9]
                }
                executions.append(execution)

            return executions

        except Exception as e:
            logger.error(f"❌ Failed to get executions for schedule {schedule_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_execution_statistics(self, schedule_id: int, days: int = 30) -> Dict[str, Any]:
        """Get execution statistics for a schedule"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = """
                SELECT
                    COUNT(*) as total_executions,
                    SUM(CASE WHEN execution_status = 'success' THEN 1 ELSE 0 END) as successful_executions,
                    SUM(CASE WHEN execution_status = 'failed' THEN 1 ELSE 0 END) as failed_executions,
                    SUM(CASE WHEN execution_status = 'running' THEN 1 ELSE 0 END) as running_executions,
                    AVG(CASE
                        WHEN actual_start_time IS NOT NULL AND actual_end_time IS NOT NULL
                        THEN DATEDIFF(second, actual_start_time, actual_end_time)
                        ELSE NULL
                    END) as avg_execution_time_seconds
                FROM kpi_schedule_executions
                WHERE schedule_id = ?
                    AND scheduled_time >= DATEADD(day, -?, GETDATE())
            """

            cursor.execute(query, (schedule_id, days))
            row = cursor.fetchone()

            if row:
                stats = {
                    'total_executions': row[0] or 0,
                    'successful_executions': row[1] or 0,
                    'failed_executions': row[2] or 0,
                    'running_executions': row[3] or 0,
                    'avg_execution_time_seconds': float(row[4]) if row[4] else None,
                    'success_rate': (row[1] / row[0] * 100) if row[0] > 0 else 0,
                    'period_days': days
                }
                return stats
            else:
                return {
                    'total_executions': 0,
                    'successful_executions': 0,
                    'failed_executions': 0,
                    'running_executions': 0,
                    'avg_execution_time_seconds': None,
                    'success_rate': 0,
                    'period_days': days
                }

        except Exception as e:
            logger.error(f"❌ Failed to get execution statistics for schedule {schedule_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
