"""
KPI Schedule Service
Handles CRUD operations for KPI schedules and integrates with Airflow
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from croniter import croniter
import pyodbc

from .airflow_dag_generator import AirflowDAGGenerator

logger = logging.getLogger(__name__)

class KPIScheduleService:
    """Service for managing KPI schedules"""
    
    def __init__(self, connection_string: str, airflow_dags_folder: str = None):
        self.connection_string = connection_string
        self.dag_generator = AirflowDAGGenerator(airflow_dags_folder)
    
    def _get_connection(self):
        """Get database connection"""
        return pyodbc.connect(self.connection_string)
    
    def create_schedule(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new KPI schedule
        
        Args:
            schedule_data: Dictionary containing schedule configuration
                {
                    "kpi_id": 123,
                    "schedule_name": "Daily Product Analysis",
                    "schedule_type": "daily",  # daily, weekly, monthly, cron
                    "cron_expression": "0 9 * * *",  # Optional for cron type
                    "timezone": "UTC",
                    "start_date": "2024-01-01T00:00:00",
                    "end_date": "2024-12-31T23:59:59",  # Optional
                    "schedule_config": {
                        "retry_count": 3,
                        "retry_delay": 300,
                        "timeout": 3600,
                        "email_notifications": ["user@example.com"]
                    }
                }
        
        Returns:
            Created schedule with generated ID and Airflow DAG ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Validate schedule data
            self._validate_schedule_data(schedule_data)
            
            # Generate Airflow DAG ID
            airflow_dag_id = f"kpi_schedule_{schedule_data['kpi_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Convert schedule_config to JSON string
            schedule_config_json = json.dumps(schedule_data.get('schedule_config', {}))
            
            # Insert schedule
            insert_query = """
                INSERT INTO kpi_schedules (
                    kpi_id, schedule_name, schedule_type, cron_expression, timezone,
                    start_date, end_date, schedule_config, airflow_dag_id, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(insert_query, (
                schedule_data['kpi_id'],
                schedule_data['schedule_name'],
                schedule_data['schedule_type'],
                schedule_data.get('cron_expression'),
                schedule_data.get('timezone', 'UTC'),
                schedule_data['start_date'],
                schedule_data.get('end_date'),
                schedule_config_json,
                airflow_dag_id,
                schedule_data.get('created_by', 'system')
            ))
            
            # Get the created schedule ID
            cursor.execute("SELECT @@IDENTITY")
            schedule_id = cursor.fetchone()[0]
            
            conn.commit()
            
            # Create notification preferences if provided
            if 'email_notifications' in schedule_data.get('schedule_config', {}):
                self._create_notification_preferences(schedule_id, schedule_data['schedule_config']['email_notifications'])

            # Get the created schedule for Airflow sync
            created_schedule = self.get_schedule(schedule_id)

            # Sync to Airflow
            try:
                self.dag_generator.sync_schedule_to_airflow(created_schedule)
                # Update last_sync_at
                cursor.execute("UPDATE kpi_schedules SET last_sync_at = GETDATE() WHERE id = ?", (schedule_id,))
                conn.commit()
            except Exception as e:
                logger.warning(f"Failed to sync schedule {schedule_id} to Airflow: {e}")

            logger.info(f"✓ Created schedule {schedule_id} for KPI {schedule_data['kpi_id']} with DAG ID {airflow_dag_id}")

            # Return the created schedule
            return created_schedule
            
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to create schedule for KPI {schedule_data.get('kpi_id')}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_schedule(self, schedule_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific schedule by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT 
                    s.id, s.kpi_id, s.schedule_name, s.schedule_type, s.cron_expression,
                    s.timezone, s.is_active, s.start_date, s.end_date, s.created_at,
                    s.updated_at, s.created_by, s.schedule_config, s.airflow_dag_id,
                    s.last_sync_at, k.name as kpi_name, k.alias_name as kpi_alias
                FROM kpi_schedules s
                JOIN kpi_definitions k ON s.kpi_id = k.id
                WHERE s.id = ?
            """
            
            cursor.execute(query, (schedule_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            schedule = {
                'id': row[0],
                'kpi_id': row[1],
                'schedule_name': row[2],
                'schedule_type': row[3],
                'cron_expression': row[4],
                'timezone': row[5],
                'is_active': bool(row[6]),
                'start_date': row[7].isoformat() if row[7] else None,
                'end_date': row[8].isoformat() if row[8] else None,
                'created_at': row[9].isoformat() if row[9] else None,
                'updated_at': row[10].isoformat() if row[10] else None,
                'created_by': row[11],
                'schedule_config': json.loads(row[12]) if row[12] else {},
                'airflow_dag_id': row[13],
                'last_sync_at': row[14].isoformat() if row[14] else None,
                'kpi_name': row[15],
                'kpi_alias': row[16]
            }
            
            # Add next execution time
            schedule['next_execution'] = self._calculate_next_execution(schedule)
            
            # Add recent execution history
            schedule['recent_executions'] = self._get_recent_executions(schedule_id, limit=5)
            
            return schedule
            
        except Exception as e:
            logger.error(f"❌ Failed to get schedule {schedule_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_schedules_by_kpi(self, kpi_id: int) -> List[Dict[str, Any]]:
        """Get all schedules for a specific KPI"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = """
                SELECT
                    s.id, s.schedule_name, s.schedule_type, s.cron_expression,
                    s.timezone, s.is_active, s.start_date, s.end_date,
                    s.created_at, s.airflow_dag_id, s.last_sync_at
                FROM kpi_schedules s
                WHERE s.kpi_id = ?
                ORDER BY s.created_at DESC
            """

            cursor.execute(query, (kpi_id,))
            rows = cursor.fetchall()

            schedules = []
            for row in rows:
                schedule = {
                    'id': row[0],
                    'schedule_name': row[1],
                    'schedule_type': row[2],
                    'cron_expression': row[3],
                    'timezone': row[4],
                    'is_active': bool(row[5]),
                    'start_date': row[6].isoformat() if row[6] else None,
                    'end_date': row[7].isoformat() if row[7] else None,
                    'created_at': row[8].isoformat() if row[8] else None,
                    'airflow_dag_id': row[9],
                    'last_sync_at': row[10].isoformat() if row[10] else None
                }

                # Add next execution time
                schedule['next_execution'] = self._calculate_next_execution(schedule)

                # Add execution status
                schedule['last_execution_status'] = self._get_last_execution_status(schedule['id'])

                schedules.append(schedule)

            return schedules

        except Exception as e:
            logger.error(f"❌ Failed to get schedules for KPI {kpi_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def update_schedule(self, schedule_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing schedule"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Build dynamic update query
            update_fields = []
            params = []

            allowed_fields = [
                'schedule_name', 'schedule_type', 'cron_expression', 'timezone',
                'is_active', 'start_date', 'end_date', 'schedule_config'
            ]

            for field in allowed_fields:
                if field in update_data:
                    if field == 'schedule_config':
                        update_fields.append(f"{field} = ?")
                        params.append(json.dumps(update_data[field]))
                    else:
                        update_fields.append(f"{field} = ?")
                        params.append(update_data[field])

            if not update_fields:
                raise ValueError("No valid fields to update")

            # Add updated_at
            update_fields.append("updated_at = GETDATE()")
            params.append(schedule_id)

            query = f"UPDATE kpi_schedules SET {', '.join(update_fields)} WHERE id = ?"

            cursor.execute(query, params)

            if cursor.rowcount == 0:
                raise ValueError(f"Schedule {schedule_id} not found")

            conn.commit()

            # Get updated schedule for Airflow sync
            updated_schedule = self.get_schedule(schedule_id)

            # Sync to Airflow if schedule configuration changed
            try:
                self.dag_generator.sync_schedule_to_airflow(updated_schedule)
                # Update last_sync_at
                cursor.execute("UPDATE kpi_schedules SET last_sync_at = GETDATE() WHERE id = ?", (schedule_id,))
                conn.commit()
            except Exception as e:
                logger.warning(f"Failed to sync updated schedule {schedule_id} to Airflow: {e}")

            logger.info(f"✓ Updated schedule {schedule_id}")

            # Return updated schedule
            return updated_schedule

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to update schedule {schedule_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def delete_schedule(self, schedule_id: int) -> bool:
        """Delete a schedule"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # First, get the schedule to check if it exists
            schedule = self.get_schedule(schedule_id)
            if not schedule:
                return False

            # Delete the schedule (cascade will handle related records)
            cursor.execute("DELETE FROM kpi_schedules WHERE id = ?", (schedule_id,))

            if cursor.rowcount == 0:
                return False

            conn.commit()

            # Remove from Airflow
            try:
                self.dag_generator.delete_dag(schedule['airflow_dag_id'])
            except Exception as e:
                logger.warning(f"Failed to delete DAG {schedule['airflow_dag_id']} from Airflow: {e}")

            logger.info(f"✓ Deleted schedule {schedule_id} for KPI {schedule['kpi_id']}")

            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to delete schedule {schedule_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def _validate_schedule_data(self, schedule_data: Dict[str, Any]) -> None:
        """Validate schedule data before creation"""
        required_fields = ['kpi_id', 'schedule_name', 'schedule_type', 'start_date']

        for field in required_fields:
            if field not in schedule_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate schedule type
        valid_types = ['daily', 'weekly', 'monthly', 'cron']
        if schedule_data['schedule_type'] not in valid_types:
            raise ValueError(f"Invalid schedule_type. Must be one of: {valid_types}")

        # Validate cron expression if type is cron
        if schedule_data['schedule_type'] == 'cron':
            if not schedule_data.get('cron_expression'):
                raise ValueError("cron_expression is required for cron schedule type")

            try:
                croniter(schedule_data['cron_expression'])
            except Exception as e:
                raise ValueError(f"Invalid cron expression: {e}")

    def _calculate_next_execution(self, schedule: Dict[str, Any]) -> Optional[str]:
        """Calculate the next execution time for a schedule"""
        if not schedule['is_active']:
            return None

        try:
            now = datetime.now()
            start_date = datetime.fromisoformat(schedule['start_date'].replace('Z', '+00:00'))

            if schedule['end_date']:
                end_date = datetime.fromisoformat(schedule['end_date'].replace('Z', '+00:00'))
                if now > end_date:
                    return None

            if schedule['schedule_type'] == 'cron' and schedule['cron_expression']:
                cron = croniter(schedule['cron_expression'], start_time=max(now, start_date))
                next_run = cron.get_next(datetime)
                return next_run.isoformat()

            elif schedule['schedule_type'] == 'daily':
                # Daily at 9 AM (default)
                next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
                return next_run.isoformat()

            elif schedule['schedule_type'] == 'weekly':
                # Weekly on Monday at 9 AM (default)
                days_ahead = 0 - now.weekday()  # Monday is 0
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                next_run = now + timedelta(days=days_ahead)
                next_run = next_run.replace(hour=9, minute=0, second=0, microsecond=0)
                return next_run.isoformat()

            elif schedule['schedule_type'] == 'monthly':
                # Monthly on 1st at 9 AM (default)
                if now.day == 1 and now.hour < 9:
                    next_run = now.replace(day=1, hour=9, minute=0, second=0, microsecond=0)
                else:
                    # Next month
                    if now.month == 12:
                        next_run = now.replace(year=now.year + 1, month=1, day=1, hour=9, minute=0, second=0, microsecond=0)
                    else:
                        next_run = now.replace(month=now.month + 1, day=1, hour=9, minute=0, second=0, microsecond=0)
                return next_run.isoformat()

        except Exception as e:
            logger.warning(f"Failed to calculate next execution for schedule {schedule.get('id')}: {e}")
            return None

        return None

    def _get_recent_executions(self, schedule_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent execution history for a schedule"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = f"""
                SELECT TOP {limit}
                    id, scheduled_time, actual_start_time, actual_end_time,
                    execution_status, error_message, retry_count
                FROM kpi_schedule_executions
                WHERE schedule_id = ?
                ORDER BY scheduled_time DESC
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
                    'retry_count': row[6]
                }
                executions.append(execution)

            return executions

        except Exception as e:
            logger.error(f"❌ Failed to get recent executions for schedule {schedule_id}: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def _get_last_execution_status(self, schedule_id: int) -> Optional[str]:
        """Get the status of the last execution for a schedule"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = """
                SELECT TOP 1 execution_status
                FROM kpi_schedule_executions
                WHERE schedule_id = ?
                ORDER BY scheduled_time DESC
            """

            cursor.execute(query, (schedule_id,))
            row = cursor.fetchone()

            return row[0] if row else None

        except Exception as e:
            logger.error(f"❌ Failed to get last execution status for schedule {schedule_id}: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def _create_notification_preferences(self, schedule_id: int, email_list: List[str]) -> None:
        """Create email notification preferences for a schedule"""
        if not email_list:
            return

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            for email in email_list:
                notification_config = {
                    "email": email,
                    "on_failure": True,
                    "on_success": False,
                    "on_retry": True
                }

                cursor.execute("""
                    INSERT INTO kpi_schedule_notifications (schedule_id, notification_type, notification_config)
                    VALUES (?, ?, ?)
                """, (schedule_id, 'email', json.dumps(notification_config)))

            conn.commit()
            logger.info(f"✓ Created notification preferences for schedule {schedule_id}")

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to create notification preferences for schedule {schedule_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def sync_all_schedules_to_airflow(self) -> Dict[str, Any]:
        """Sync all active schedules to Airflow"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get all active schedules
            cursor.execute("SELECT id FROM kpi_schedules WHERE is_active = 1")
            schedule_ids = [row[0] for row in cursor.fetchall()]

            results = {
                'total_schedules': len(schedule_ids),
                'synced_successfully': 0,
                'sync_failures': 0,
                'errors': []
            }

            for schedule_id in schedule_ids:
                try:
                    schedule = self.get_schedule(schedule_id)
                    if schedule:
                        success = self.dag_generator.sync_schedule_to_airflow(schedule)
                        if success:
                            results['synced_successfully'] += 1
                            # Update last_sync_at
                            cursor.execute("UPDATE kpi_schedules SET last_sync_at = GETDATE() WHERE id = ?", (schedule_id,))
                        else:
                            results['sync_failures'] += 1
                            results['errors'].append(f"Failed to sync schedule {schedule_id}")
                except Exception as e:
                    results['sync_failures'] += 1
                    results['errors'].append(f"Schedule {schedule_id}: {str(e)}")

            conn.commit()

            logger.info(f"✓ Synced {results['synced_successfully']}/{results['total_schedules']} schedules to Airflow")

            return results

        except Exception as e:
            logger.error(f"❌ Failed to sync schedules to Airflow: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def manual_trigger_schedule(self, schedule_id: int) -> Dict[str, Any]:
        """
        Manually trigger a schedule execution

        Creates an execution record and triggers the KPI execution immediately.
        This bypasses the normal Airflow scheduling.

        Args:
            schedule_id: ID of the schedule to trigger

        Returns:
            Dictionary containing execution details and status
        """
        try:
            # Get the schedule
            schedule = self.get_schedule(schedule_id)
            if not schedule:
                raise ValueError(f"Schedule {schedule_id} not found")

            if not schedule['is_active']:
                raise ValueError(f"Schedule {schedule_id} is not active")

            # Import here to avoid circular imports
            from .schedule_execution_service import ScheduleExecutionService
            from .landing_kpi_service_jdbc import get_landing_kpi_service_jdbc
            import threading

            # Create execution record
            execution_service = ScheduleExecutionService(self.connection_string)
            execution_data = {
                'schedule_id': schedule_id,
                'kpi_id': schedule['kpi_id'],
                'scheduled_time': datetime.now().isoformat(),
                'actual_start_time': datetime.now().isoformat(),
                'execution_status': 'running',
                'airflow_task_id': f"manual_trigger_{schedule_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'airflow_run_id': f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }

            execution_record = execution_service.create_execution_record(execution_data)
            execution_id = execution_record['id']

            logger.info(f"✓ Created manual execution record {execution_id} for schedule {schedule_id}")

            # Execute the KPI in background thread
            def execute_kpi_background():
                try:
                    # Get KPI service and executor (for cached SQL support)
                    kpi_service = get_landing_kpi_service_jdbc()
                    from kg_builder.services.landing_kpi_executor import get_landing_kpi_executor

                    # Create execution record first
                    execution_params = {
                        'kg_name': 'manual_trigger',
                        'schemas': ['newdqschemanov'],  # Required: list of schemas
                        'select_schema': 'newdqschemanov',  # Default schema
                        'definitions': [],  # Required: empty list for manual trigger
                        'db_type': 'sqlserver',
                        'limit_records': 1000,
                        'limit': 1000,  # Also add as 'limit' for compatibility
                        'use_llm': True,
                        'min_confidence': 0.7,  # Required parameter
                        'user_id': 'schedule_trigger',
                        'session_id': f"schedule_{schedule_id}"
                    }

                    # Create KPI execution record
                    kpi_execution_record = kpi_service.create_execution_record(schedule['kpi_id'], execution_params)
                    kpi_execution_id = kpi_execution_record.get('id')

                    logger.info(f"🔄 Created KPI execution record {kpi_execution_id} for schedule {schedule_id}")

                    # Use LandingKPIExecutor for cached SQL support
                    executor = get_landing_kpi_executor()

                    # Execute using the executor (which supports cached SQL)
                    logger.info(f"🚀 Executing KPI {schedule['kpi_id']} using LandingKPIExecutor (supports cached SQL)")
                    executor.execute_kpi_async(
                        kpi_id=schedule['kpi_id'],
                        execution_id=kpi_execution_id,
                        execution_params=execution_params
                    )

                    # The LandingKPIExecutor will handle updating the KPI execution record
                    # We just need to update the schedule execution record
                    update_data = {
                        'execution_status': 'success',
                        'actual_end_time': datetime.now().isoformat(),
                        'execution_id': kpi_execution_id
                    }
                    execution_service.update_execution_record(execution_id, update_data)

                    logger.info(f"✓ Manual execution completed successfully: schedule_execution_id={execution_id}, kpi_execution_id={kpi_execution_id}")
                    logger.info(f"✓ Used LandingKPIExecutor which supports cached SQL execution")

                except Exception as e:
                    logger.error(f"❌ Manual execution failed for schedule {schedule_id}: {e}")

                    # Update execution record with failure
                    try:
                        update_data = {
                            'execution_status': 'failed',
                            'actual_end_time': datetime.now().isoformat(),
                            'error_message': str(e)
                        }
                        execution_service.update_execution_record(execution_id, update_data)
                    except Exception as update_error:
                        logger.error(f"❌ Failed to update execution record {execution_id}: {update_error}")

            # Start background execution
            thread = threading.Thread(target=execute_kpi_background, daemon=True)
            thread.start()

            logger.info(f"✓ Manual trigger initiated for schedule {schedule_id}")

            return {
                'success': True,
                'message': f'Schedule {schedule_id} triggered manually',
                'execution_id': execution_id,
                'schedule_id': schedule_id,
                'kpi_id': schedule['kpi_id'],
                'kpi_name': schedule['kpi_name'],
                'execution_status': 'running',
                'triggered_at': datetime.now().isoformat()
            }

        except ValueError as e:
            logger.warning(f"Invalid manual trigger request for schedule {schedule_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to manually trigger schedule {schedule_id}: {e}")
            raise

    def get_airflow_dag_status(self, schedule_id: int) -> Dict[str, Any]:
        """Get Airflow DAG status for a schedule"""
        try:
            schedule = self.get_schedule(schedule_id)
            if not schedule:
                return {'error': 'Schedule not found'}

            dag_status = self.dag_generator.get_dag_status(schedule['airflow_dag_id'])
            return dag_status

        except Exception as e:
            logger.error(f"❌ Failed to get DAG status for schedule {schedule_id}: {e}")
            return {'error': str(e)}
