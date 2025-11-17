"""
Airflow DAG Generator Service
Dynamically generates and manages Airflow DAGs for KPI schedules
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class AirflowDAGGenerator:
    """Service for generating and managing Airflow DAGs for KPI schedules"""
    
    def __init__(self, airflow_dags_folder: str = None):
        self.airflow_dags_folder = airflow_dags_folder or os.getenv('AIRFLOW_DAGS_FOLDER', '/opt/airflow/dags')
        self.ensure_dags_folder()
    
    def ensure_dags_folder(self):
        """Ensure the Airflow DAGs folder exists"""
        Path(self.airflow_dags_folder).mkdir(parents=True, exist_ok=True)
        logger.info(f"Airflow DAGs folder: {self.airflow_dags_folder}")
    
    def generate_dag(self, schedule: Dict[str, Any]) -> str:
        """
        Generate an Airflow DAG for a KPI schedule
        
        Args:
            schedule: Schedule configuration dictionary
            
        Returns:
            Path to the generated DAG file
        """
        try:
            dag_id = schedule['airflow_dag_id']
            dag_content = self._create_dag_content(schedule)
            
            # Write DAG file
            dag_file_path = os.path.join(self.airflow_dags_folder, f"{dag_id}.py")
            
            with open(dag_file_path, 'w') as f:
                f.write(dag_content)
            
            logger.info(f"✓ Generated DAG file: {dag_file_path}")
            return dag_file_path
            
        except Exception as e:
            logger.error(f"❌ Failed to generate DAG for schedule {schedule.get('id')}: {e}")
            raise
    
    def _create_dag_content(self, schedule: Dict[str, Any]) -> str:
        """Create the Python content for the Airflow DAG"""
        
        # Extract schedule configuration
        schedule_config = schedule.get('schedule_config', {})
        retry_count = schedule_config.get('retry_count', 3)
        retry_delay = schedule_config.get('retry_delay', 300)
        timeout = schedule_config.get('timeout', 3600)
        email_notifications = schedule_config.get('email_notifications', [])
        
        # Determine schedule interval
        schedule_interval = self._get_schedule_interval(schedule)
        
        # Create DAG content
        dag_content = f'''"""
Auto-generated Airflow DAG for KPI Schedule
Schedule ID: {schedule['id']}
KPI ID: {schedule['kpi_id']}
Generated at: {datetime.now().isoformat()}
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.utils.dates import days_ago
import requests
import logging

# DAG Configuration
DAG_ID = '{schedule['airflow_dag_id']}'
SCHEDULE_ID = {schedule['id']}
KPI_ID = {schedule['kpi_id']}
API_BASE_URL = 'http://localhost:8000/v1'

# Default arguments
default_args = {{
    'owner': 'kpi-scheduler',
    'depends_on_past': False,
    'start_date': datetime.fromisoformat('{schedule['start_date']}'),
    'email_on_failure': {len(email_notifications) > 0},
    'email_on_retry': False,
    'retries': {retry_count},
    'retry_delay': timedelta(seconds={retry_delay}),
    'execution_timeout': timedelta(seconds={timeout}),
}}

# Email configuration
{f"default_args['email'] = {email_notifications}" if email_notifications else ""}

# Create DAG
dag = DAG(
    DAG_ID,
    default_args=default_args,
    description='KPI Schedule: {schedule['schedule_name']}',
    schedule_interval='{schedule_interval}',
    catchup=False,
    max_active_runs=1,
    tags=['kpi-scheduler', 'kpi-{schedule['kpi_id']}']
)

def execute_kpi(**context):
    """Execute the KPI and track execution"""
    import requests
    import json
    
    logger = logging.getLogger(__name__)
    
    try:
        # Record execution start
        execution_data = {{
            'schedule_id': SCHEDULE_ID,
            'kpi_id': KPI_ID,
            'scheduled_time': context['ds'],
            'actual_start_time': datetime.now().isoformat(),
            'execution_status': 'running',
            'airflow_task_id': context['task_instance'].task_id,
            'airflow_run_id': context['run_id']
        }}
        
        # Create execution record
        response = requests.post(
            f'{{API_BASE_URL}}/kpi-schedule-executions/',
            json=execution_data,
            timeout=30
        )
        
        if response.status_code == 201:
            execution_record = response.json()
            execution_id = execution_record['id']
            logger.info(f"Created execution record {{execution_id}}")
        else:
            logger.warning(f"Failed to create execution record: {{response.status_code}}")
            execution_id = None
        
        # Execute the KPI with proper execution parameters
        execution_params = {{
            'kg_name': 'airflow_scheduled',
            'schemas': ['newdqschemanov'],
            'select_schema': 'newdqschemanov',  # Ensure both formats are provided
            'definitions': [],
            'db_type': 'sqlserver',
            'limit_records': 1000,
            'limit': 1000,
            'use_llm': True,
            'min_confidence': 0.7,
            'user_id': 'airflow_scheduler',
            'session_id': f'airflow_{{context["run_id"]}}'
        }}

        logger.info(f"Executing KPI {{KPI_ID}} with parameters: {{execution_params}}")

        kpi_execution_response = requests.post(
            f'{{API_BASE_URL}}/landing-kpi-mssql/kpis/{{KPI_ID}}/execute',
            json=execution_params,
            timeout={timeout}
        )
        
        if kpi_execution_response.status_code == 200:
            kpi_result = kpi_execution_response.json()
            logger.info(f"KPI execution successful: {{kpi_result.get('execution_id')}}")
            
            # Update execution record with success
            if execution_id:
                update_data = {{
                    'execution_status': 'success',
                    'actual_end_time': datetime.now().isoformat(),
                    'execution_id': kpi_result.get('execution_id')
                }}
                
                requests.put(
                    f'{{API_BASE_URL}}/kpi-schedule-executions/{{execution_id}}',
                    json=update_data,
                    timeout=30
                )
            
            return kpi_result
            
        else:
            error_msg = f"KPI execution failed: {{kpi_execution_response.status_code}} - {{kpi_execution_response.text}}"
            logger.error(error_msg)
            
            # Update execution record with failure
            if execution_id:
                update_data = {{
                    'execution_status': 'failed',
                    'actual_end_time': datetime.now().isoformat(),
                    'error_message': error_msg
                }}
                
                requests.put(
                    f'{{API_BASE_URL}}/kpi-schedule-executions/{{execution_id}}',
                    json=update_data,
                    timeout=30
                )
            
            raise Exception(error_msg)
            
    except Exception as e:
        logger.error(f"KPI execution failed: {{e}}")
        
        # Update execution record with failure
        if 'execution_id' in locals() and execution_id:
            try:
                update_data = {{
                    'execution_status': 'failed',
                    'actual_end_time': datetime.now().isoformat(),
                    'error_message': str(e)
                }}
                
                requests.put(
                    f'{{API_BASE_URL}}/kpi-schedule-executions/{{execution_id}}',
                    json=update_data,
                    timeout=30
                )
            except:
                pass  # Don't fail the task if we can't update the record
        
        raise

# Define tasks
execute_kpi_task = PythonOperator(
    task_id='execute_kpi',
    python_callable=execute_kpi,
    dag=dag
)

# Set task dependencies (single task for now)
execute_kpi_task
'''
        
        return dag_content

    def _get_schedule_interval(self, schedule: Dict[str, Any]) -> str:
        """Convert schedule configuration to Airflow schedule interval"""
        schedule_type = schedule['schedule_type']

        if schedule_type == 'cron':
            return schedule['cron_expression']
        elif schedule_type == 'daily':
            return '0 9 * * *'  # Daily at 9 AM
        elif schedule_type == 'weekly':
            return '0 9 * * 1'  # Weekly on Monday at 9 AM
        elif schedule_type == 'monthly':
            return '0 9 1 * *'  # Monthly on 1st at 9 AM
        else:
            return '@daily'  # Default fallback

    def update_dag(self, schedule: Dict[str, Any]) -> str:
        """Update an existing DAG"""
        return self.generate_dag(schedule)

    def delete_dag(self, dag_id: str) -> bool:
        """Delete a DAG file"""
        try:
            dag_file_path = os.path.join(self.airflow_dags_folder, f"{dag_id}.py")

            if os.path.exists(dag_file_path):
                os.remove(dag_file_path)
                logger.info(f"✓ Deleted DAG file: {dag_file_path}")
                return True
            else:
                logger.warning(f"DAG file not found: {dag_file_path}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to delete DAG {dag_id}: {e}")
            raise

    def sync_schedule_to_airflow(self, schedule: Dict[str, Any]) -> bool:
        """Sync a schedule to Airflow by generating/updating its DAG"""
        try:
            if schedule['is_active']:
                # Generate or update DAG
                self.generate_dag(schedule)
                logger.info(f"✓ Synced active schedule {schedule['id']} to Airflow")
            else:
                # Delete DAG if schedule is inactive
                self.delete_dag(schedule['airflow_dag_id'])
                logger.info(f"✓ Removed inactive schedule {schedule['id']} from Airflow")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to sync schedule {schedule['id']} to Airflow: {e}")
            return False

    def get_dag_status(self, dag_id: str) -> Dict[str, Any]:
        """Get the status of a DAG in Airflow"""
        try:
            # This would typically call Airflow REST API
            # For now, just check if DAG file exists
            dag_file_path = os.path.join(self.airflow_dags_folder, f"{dag_id}.py")

            return {
                'dag_id': dag_id,
                'exists': os.path.exists(dag_file_path),
                'file_path': dag_file_path,
                'last_modified': datetime.fromtimestamp(os.path.getmtime(dag_file_path)).isoformat() if os.path.exists(dag_file_path) else None
            }

        except Exception as e:
            logger.error(f"❌ Failed to get DAG status for {dag_id}: {e}")
            return {
                'dag_id': dag_id,
                'exists': False,
                'error': str(e)
            }
