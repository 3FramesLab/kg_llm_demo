"""
KPI Schedule Service
Handles CRUD operations for KPI schedules and integrates with Airflow
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from croniter import croniter

from .airflow_dag_generator import AirflowDAGGenerator
from kg_builder.services.jdbc_connection_manager import get_jdbc_connection

logger = logging.getLogger(__name__)

class KPIScheduleService:
    """Service for managing KPI schedules"""

    def __init__(self, airflow_dags_folder: str = None):
        from kg_builder.config import KPI_DB_HOST, KPI_DB_PORT, KPI_DB_DATABASE, KPI_DB_USERNAME, KPI_DB_PASSWORD

        self.host = KPI_DB_HOST
        self.port = KPI_DB_PORT
        self.database = KPI_DB_DATABASE
        self.username = KPI_DB_USERNAME
        self.password = KPI_DB_PASSWORD
        self.dag_generator = AirflowDAGGenerator(airflow_dags_folder)

    def _get_connection(self):
        """Get JDBC database connection to MySQL KPI Analytics database"""
        # MySQL JDBC connection
        driver_class = "com.mysql.cj.jdbc.Driver"
        jdbc_url = f"jdbc:mysql://{self.host}:{self.port}/{self.database}?useSSL=false&allowPublicKeyRetrieval=true"

        return get_jdbc_connection(driver_class, jdbc_url, self.username, self.password)

    def _safe_datetime_to_string(self, value, allow_none=True):
        """Safely convert datetime object or string to string format"""
        if value is None:
            return None if allow_none else "1970-01-01T00:00:00"

        # If it's already a string, return as-is
        if isinstance(value, str):
            return value

        # If it's a datetime object, convert to ISO format
        if hasattr(value, 'isoformat'):
            return value.isoformat()

        # Fallback: convert to string
        return str(value)

    def _safe_string_convert(self, value):
        """Safely convert Java String or any value to Python string"""
        if value is None:
            return None

        # Convert Java objects to Python strings
        if hasattr(value, '__class__') and 'java' in str(value.__class__):
            return str(value)

        # Already a Python string or other type
        return value

    def _safe_json_loads(self, value):
        """Safely parse JSON from Java String or Python string"""
        if value is None:
            return {}

        # Convert Java String to Python string if needed
        if hasattr(value, '__class__') and 'java' in str(value.__class__):
            value = str(value)

        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse JSON: {e}, returning empty dict")
            return {}

    def _ensure_tables_exist(self):
        """Ensure KPI scheduling tables exist in MySQL database"""
        conn = self._get_connection()
        if not conn:
            logger.error("❌ Failed to get database connection for table creation")
            return False

        # Disable autocommit for transaction management
        conn.jconn.setAutoCommit(False)

        cursor = conn.cursor()

        try:
            # Check if kpi_schedules table exists
            cursor.execute("SHOW TABLES LIKE 'kpi_schedules'")
            table_exists = cursor.fetchone()

            if not table_exists:
                logger.info("📋 Creating kpi_schedules table...")
                cursor.execute("""
                    CREATE TABLE kpi_schedules (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        kpi_id INT NOT NULL,
                        schedule_name VARCHAR(255) NOT NULL,
                        schedule_type VARCHAR(50) NOT NULL,
                        cron_expression VARCHAR(100),
                        timezone VARCHAR(50) DEFAULT 'UTC',
                        is_active BOOLEAN DEFAULT TRUE,
                        start_date DATETIME NOT NULL,
                        end_date DATETIME,
                        schedule_config JSON,
                        airflow_dag_id VARCHAR(255),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        created_by VARCHAR(100) DEFAULT 'system',
                        last_sync_at DATETIME,
                        INDEX idx_kpi_id (kpi_id),
                        INDEX idx_active (is_active),
                        INDEX idx_schedule_type (schedule_type)
                    )
                """)
                logger.info("✅ Created kpi_schedules table")
            else:
                # Table exists, check if it has the correct columns
                logger.info("📋 Checking existing kpi_schedules table structure...")
                cursor.execute("DESCRIBE kpi_schedules")
                columns = {row[0]: row for row in cursor.fetchall()}

                # Add missing columns if needed
                if 'created_at' not in columns:
                    logger.info("📋 Adding created_at column...")
                    cursor.execute("ALTER TABLE kpi_schedules ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")

                if 'updated_at' not in columns:
                    logger.info("📋 Adding updated_at column...")
                    cursor.execute("ALTER TABLE kpi_schedules ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")

                logger.info("✅ Table structure verified")

            # Fix existing records with null created_at
            cursor.execute("SELECT COUNT(*) FROM kpi_schedules WHERE created_at IS NULL")
            null_count = cursor.fetchone()[0]

            if null_count > 0:
                logger.info(f"📋 Fixing {null_count} records with null created_at...")
                # Set created_at to the earliest reasonable time for existing records
                cursor.execute("""
                    UPDATE kpi_schedules
                    SET created_at = COALESCE(last_sync_at, start_date, CURRENT_TIMESTAMP)
                    WHERE created_at IS NULL
                """)
                logger.info(f"✅ Fixed {null_count} records with null created_at")

            # Fix existing records that are inactive (set them to active by default)
            cursor.execute("SELECT COUNT(*) FROM kpi_schedules WHERE is_active = FALSE OR is_active IS NULL")
            inactive_count = cursor.fetchone()[0]

            if inactive_count > 0:
                logger.info(f"📋 Activating {inactive_count} inactive schedules...")
                cursor.execute("UPDATE kpi_schedules SET is_active = TRUE WHERE is_active = FALSE OR is_active IS NULL")
                logger.info(f"✅ Activated {inactive_count} schedules")

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to ensure tables exist: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
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
                    },
                    "execution_params": {  # Optional: KPI execution parameters
                        "kg_name": "default_kg",
                        "schemas": ["newdqschemanov"],
                        "select_schema": "newdqschemanov",
                        "db_type": "sqlserver",
                        "limit_records": 1000,
                        "use_llm": true,
                        "min_confidence": 0.7
                    }
                }
        
        Returns:
            Created schedule with generated ID and Airflow DAG ID
        """
        conn = self._get_connection()

        # Disable autocommit for transaction management
        conn.jconn.setAutoCommit(False)

        cursor = conn.cursor()

        try:
            # Validate schedule data
            self._validate_schedule_data(schedule_data)

            # Get current timestamp in UTC
            from datetime import timezone
            current_time = datetime.now(timezone.utc)

            # Generate Airflow DAG ID using UTC time
            airflow_dag_id = f"kpi_schedule_{schedule_data['kpi_id']}_{current_time.strftime('%Y%m%d_%H%M%S')}"

            # Convert schedule_config to JSON string
            schedule_config_json = json.dumps(schedule_data.get('schedule_config', {}))

            # Insert schedule (JDBC syntax) - explicitly set all fields including is_active
            insert_query = """
                INSERT INTO kpi_schedules (
                    kpi_id, schedule_name, schedule_type, cron_expression, timezone,
                    is_active, start_date, end_date, schedule_config, airflow_dag_id, created_by,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Debug: Log the timestamp values
            created_at_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
            logger.debug(f"🕐 Inserting schedule with timestamps: created_at={created_at_str}, updated_at={created_at_str}")

            cursor.execute(insert_query, (
                schedule_data['kpi_id'],
                schedule_data['schedule_name'],
                schedule_data['schedule_type'],
                schedule_data.get('cron_expression'),
                schedule_data.get('timezone', 'UTC'),
                schedule_data.get('is_active', True),  # Default to active
                schedule_data['start_date'],
                schedule_data.get('end_date'),
                schedule_config_json,
                airflow_dag_id,
                schedule_data.get('created_by', 'system'),
                created_at_str,  # created_at as string
                created_at_str   # updated_at as string
            ))
            
            # Get the created schedule ID (MySQL syntax)
            cursor.execute("SELECT LAST_INSERT_ID()")
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
                cursor.execute("UPDATE kpi_schedules SET last_sync_at = ? WHERE id = ?", (current_time.strftime('%Y-%m-%d %H:%M:%S'), schedule_id))
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
                'schedule_name': self._safe_string_convert(row[2]),
                'schedule_type': self._safe_string_convert(row[3]),
                'cron_expression': self._safe_string_convert(row[4]),
                'timezone': self._safe_string_convert(row[5]),
                'is_active': bool(row[6]),
                'start_date': self._safe_datetime_to_string(row[7]),
                'end_date': self._safe_datetime_to_string(row[8]),
                'created_at': self._safe_datetime_to_string(row[9]),
                'updated_at': self._safe_datetime_to_string(row[10]),
                'created_by': self._safe_string_convert(row[11]),
                'schedule_config': self._safe_json_loads(row[12]),
                'airflow_dag_id': self._safe_string_convert(row[13]),
                'last_sync_at': self._safe_datetime_to_string(row[14]),
                'kpi_name': self._safe_string_convert(row[15]),
                'kpi_alias': self._safe_string_convert(row[16])
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
        # Ensure tables exist first
        if not self._ensure_tables_exist():
            logger.error("❌ Failed to ensure database tables exist")
            return []

        conn = self._get_connection()

        if not conn:
            logger.error("❌ Failed to get database connection")
            raise Exception("Failed to get database connection")

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

            logger.debug(f"🔍 Executing query for KPI {kpi_id}: {query}")
            cursor.execute(query, (kpi_id,))
            rows = cursor.fetchall()

            schedules = []
            for row in rows:
                try:
                    schedule = {
                        'id': row[0],
                        'schedule_name': self._safe_string_convert(row[1]),
                        'schedule_type': self._safe_string_convert(row[2]),
                        'cron_expression': self._safe_string_convert(row[3]),
                        'timezone': self._safe_string_convert(row[4]),
                        'is_active': bool(row[5]),
                        'start_date': self._safe_datetime_to_string(row[6]),
                        'end_date': self._safe_datetime_to_string(row[7]),
                        'created_at': self._safe_datetime_to_string(row[8]),
                        'airflow_dag_id': self._safe_string_convert(row[9]),
                        'last_sync_at': self._safe_datetime_to_string(row[10])
                    }

                    # Add calculated fields
                    schedule['next_execution'] = self._calculate_next_execution(schedule)
                    schedule['last_execution_status'] = self._get_last_execution_status(schedule['id'])
                    schedules.append(schedule)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to process schedule row: {e}")
                    continue

            logger.info(f"✅ Found {len(schedules)} schedules for KPI {kpi_id}")
            return schedules

        except Exception as e:
            logger.error(f"❌ Failed to get schedules for KPI {kpi_id}: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def update_schedule(self, schedule_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing schedule"""
        conn = self._get_connection()

        # Disable autocommit for transaction management
        conn.jconn.setAutoCommit(False)

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

            # Add updated_at with explicit UTC timestamp
            update_fields.append("updated_at = ?")
            from datetime import timezone
            update_time = datetime.now(timezone.utc)
            params.append(update_time.strftime('%Y-%m-%d %H:%M:%S'))
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
                sync_time = datetime.now(timezone.utc)
                cursor.execute("UPDATE kpi_schedules SET last_sync_at = ? WHERE id = ?", (sync_time.strftime('%Y-%m-%d %H:%M:%S'), schedule_id))
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

        # Disable autocommit for transaction management
        conn.jconn.setAutoCommit(False)

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
            return "Not scheduled (inactive)"

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
                SELECT
                    id, scheduled_time, actual_start_time, actual_end_time,
                    execution_status, error_message, retry_count
                FROM kpi_schedule_executions
                WHERE schedule_id = ?
                ORDER BY scheduled_time DESC
                LIMIT {limit}
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
                SELECT execution_status
                FROM kpi_schedule_executions
                WHERE schedule_id = ?
                ORDER BY scheduled_time DESC
                LIMIT 1
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

        # Disable autocommit for transaction management
        conn.jconn.setAutoCommit(False)

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

        # Disable autocommit for transaction management
        conn.jconn.setAutoCommit(False)

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
                            sync_time = datetime.now(timezone.utc)
                            cursor.execute("UPDATE kpi_schedules SET last_sync_at = ? WHERE id = ?", (sync_time.strftime('%Y-%m-%d %H:%M:%S'), schedule_id))
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
            conn.rollback()
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
                    schedule_execution_start = time.time()
                    logger.info("="*100)
                    logger.info(f"🚀 MANUAL KPI SCHEDULE EXECUTION STARTED")
                    logger.info(f"   Schedule ID: {schedule_id}")
                    logger.info(f"   KPI ID: {schedule['kpi_id']}")
                    logger.info(f"   Execution ID: {execution_id}")
                    logger.info(f"   Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info("="*100)

                    # Step 1: Initialize services and executor
                    logger.info(f"🔧 STEP 1: Initializing Services and Executor")

                    service_init_start = time.time()
                    kpi_service = get_landing_kpi_service_jdbc()
                    from kg_builder.services.landing_kpi_executor import get_landing_kpi_executor
                    service_init_time = (time.time() - service_init_start) * 1000

                    logger.info(f"✅ Services initialized in {service_init_time:.2f}ms")
                    logger.info(f"   KPI Service: {type(kpi_service).__name__}")

                    # Step 2: Prepare execution parameters
                    logger.info(f"📋 STEP 2: Preparing Execution Parameters")

                    params_start = time.time()

                    # Use schedule-specific execution params if available, otherwise use defaults
                    schedule_config = schedule.get('schedule_config', {})
                    custom_execution_params = schedule_config.get('execution_params', {})

                    # Default execution parameters
                    default_params = {
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

                    # Merge custom params with defaults (custom params take precedence)
                    execution_params = {**default_params, **custom_execution_params}

                    # Ensure both schemas and select_schema are set for compatibility
                    if 'schemas' in execution_params and 'select_schema' not in execution_params:
                        execution_params['select_schema'] = execution_params['schemas'][0] if execution_params['schemas'] else 'newdqschemanov'
                    elif 'select_schema' in execution_params and 'schemas' not in execution_params:
                        execution_params['schemas'] = [execution_params['select_schema']]

                    # Always ensure these system fields are set
                    execution_params['user_id'] = 'schedule_trigger'
                    execution_params['session_id'] = f"schedule_{schedule_id}"

                    params_time = (time.time() - params_start) * 1000

                    logger.info(f"✅ Execution parameters prepared in {params_time:.2f}ms")
                    logger.info(f"   Parameters: {execution_params}")

                    # Step 3: Create KPI execution record
                    logger.info(f"💾 STEP 3: Creating KPI Execution Record")
                    logger.info(f"   KPI ID: {schedule['kpi_id']}")
                    logger.info(f"   Execution Params Keys: {list(execution_params.keys())}")

                    record_creation_start = time.time()
                    kpi_execution_record = kpi_service.create_execution_record(schedule['kpi_id'], execution_params)
                    kpi_execution_id = kpi_execution_record.get('id')
                    record_creation_time = (time.time() - record_creation_start) * 1000

                    logger.info(f"✅ KPI execution record created in {record_creation_time:.2f}ms")
                    logger.info(f"   KPI Execution ID: {kpi_execution_id}")
                    logger.info(f"   Record Details: {kpi_execution_record}")

                    # Step 4: Initialize and configure executor
                    logger.info(f"⚙️ STEP 4: Initializing KPI Executor")

                    executor_init_start = time.time()
                    executor = get_landing_kpi_executor()
                    executor_init_time = (time.time() - executor_init_start) * 1000

                    logger.info(f"✅ KPI executor initialized in {executor_init_time:.2f}ms")
                    logger.info(f"   Executor Type: {type(executor).__name__}")
                    logger.info(f"   Supports Cached SQL: True")

                    # Step 5: Execute KPI asynchronously
                    logger.info(f"🚀 STEP 5: Executing KPI Asynchronously")
                    logger.info(f"   KPI ID: {schedule['kpi_id']}")
                    logger.info(f"   Execution ID: {kpi_execution_id}")
                    logger.info(f"   Using LandingKPIExecutor with cached SQL support")

                    kpi_execution_start = time.time()
                    executor.execute_kpi_async(
                        kpi_id=schedule['kpi_id'],
                        execution_id=kpi_execution_id,
                        execution_params=execution_params
                    )
                    kpi_execution_time = (time.time() - kpi_execution_start) * 1000

                    logger.info(f"✅ KPI execution initiated in {kpi_execution_time:.2f}ms")
                    logger.info(f"   Note: Actual KPI processing continues asynchronously")

                    # Step 6: Update schedule execution record
                    logger.info(f"📝 STEP 6: Updating Schedule Execution Record")

                    update_start = time.time()
                    update_data = {
                        'execution_status': 'success',
                        'actual_end_time': datetime.now().isoformat(),
                        'execution_id': kpi_execution_id,
                        'execution_time_ms': kpi_execution_time,
                        'schedule_id': schedule_id
                    }

                    logger.info(f"   Update Data: {update_data}")
                    execution_service.update_execution_record(execution_id, update_data)
                    update_time = (time.time() - update_start) * 1000

                    logger.info(f"✅ Schedule execution record updated in {update_time:.2f}ms")

                    # Step 7: Final success summary
                    total_schedule_time = (time.time() - schedule_execution_start) * 1000

                    logger.info("="*100)
                    logger.info(f"🎉 MANUAL KPI SCHEDULE EXECUTION COMPLETED SUCCESSFULLY")
                    logger.info(f"   Schedule ID: {schedule_id}")
                    logger.info(f"   KPI ID: {schedule['kpi_id']}")
                    logger.info(f"   Schedule Execution ID: {execution_id}")
                    logger.info(f"   KPI Execution ID: {kpi_execution_id}")
                    logger.info(f"   Total Schedule Time: {total_schedule_time:.2f}ms")
                    logger.info(f"   Performance Breakdown:")
                    logger.info(f"      Service Initialization: {service_init_time:.2f}ms")
                    logger.info(f"      Parameter Preparation: {params_time:.2f}ms")
                    logger.info(f"      Record Creation: {record_creation_time:.2f}ms")
                    logger.info(f"      Executor Initialization: {executor_init_time:.2f}ms")
                    logger.info(f"      KPI Execution Initiation: {kpi_execution_time:.2f}ms")
                    logger.info(f"      Record Update: {update_time:.2f}ms")
                    logger.info(f"   Used LandingKPIExecutor with cached SQL support")
                    logger.info("="*100)

                except Exception as e:
                    total_schedule_time = (time.time() - schedule_execution_start) * 1000 if 'schedule_execution_start' in locals() else 0
                    error_type = type(e).__name__
                    error_message = str(e)

                    logger.error("="*100)
                    logger.error(f"❌ MANUAL KPI SCHEDULE EXECUTION FAILED")
                    logger.error(f"   Schedule ID: {schedule_id}")
                    logger.error(f"   KPI ID: {schedule.get('kpi_id', 'UNKNOWN')}")
                    logger.error(f"   Execution ID: {execution_id}")
                    logger.error(f"   Total Schedule Time: {total_schedule_time:.2f}ms")
                    logger.error(f"   Error Type: {error_type}")
                    logger.error(f"   Error Message: {error_message}")
                    logger.error("="*100)
                    logger.error(f"Full schedule execution error details:", exc_info=True)

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
