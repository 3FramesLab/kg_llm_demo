"""
KPI Schedule Router
REST API endpoints for KPI schedule management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from kg_builder.services.kpi_schedule_service import KPIScheduleService
from kg_builder.services.schedule_execution_service import ScheduleExecutionService
from kg_builder.config import get_mssql_connection_string

logger = logging.getLogger(__name__)

# Pydantic models for request/response
class ScheduleConfigModel(BaseModel):
    """Schedule configuration model"""
    retry_count: int = Field(default=3, ge=0, le=10)
    retry_delay: int = Field(default=300, ge=60, le=3600)  # seconds
    timeout: int = Field(default=3600, ge=300, le=7200)  # seconds
    email_notifications: List[str] = Field(default_factory=list)

class CreateScheduleRequest(BaseModel):
    """Request model for creating a KPI schedule"""
    kpi_id: int = Field(..., gt=0)
    schedule_name: str = Field(..., min_length=1, max_length=255)
    schedule_type: str = Field(..., pattern="^(daily|weekly|monthly|cron)$")
    cron_expression: Optional[str] = Field(None, max_length=100)
    timezone: str = Field(default="UTC", max_length=50)
    start_date: datetime
    end_date: Optional[datetime] = None
    schedule_config: ScheduleConfigModel = Field(default_factory=ScheduleConfigModel)
    created_by: Optional[str] = Field(None, max_length=100)
    
    @validator('cron_expression')
    def validate_cron_expression(cls, v, values):
        if values.get('schedule_type') == 'cron' and not v:
            raise ValueError('cron_expression is required for cron schedule type')
        return v
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

class UpdateScheduleRequest(BaseModel):
    """Request model for updating a KPI schedule"""
    schedule_name: Optional[str] = Field(None, min_length=1, max_length=255)
    schedule_type: Optional[str] = Field(None, pattern="^(daily|weekly|monthly|cron)$")
    cron_expression: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    schedule_config: Optional[ScheduleConfigModel] = None

class ScheduleResponse(BaseModel):
    """Response model for schedule data"""
    id: int
    kpi_id: int
    kpi_name: str
    kpi_alias: Optional[str]
    schedule_name: str
    schedule_type: str
    cron_expression: Optional[str]
    timezone: str
    is_active: bool
    start_date: str
    end_date: Optional[str]
    created_at: str
    updated_at: str
    created_by: Optional[str]
    schedule_config: Dict[str, Any]
    airflow_dag_id: str
    last_sync_at: Optional[str]
    next_execution: Optional[str]
    recent_executions: List[Dict[str, Any]]

class ScheduleListResponse(BaseModel):
    """Response model for schedule list"""
    id: int
    schedule_name: str
    schedule_type: str
    cron_expression: Optional[str]
    timezone: str
    is_active: bool
    start_date: str
    end_date: Optional[str]
    created_at: str
    airflow_dag_id: str
    last_sync_at: Optional[str]
    next_execution: Optional[str]
    last_execution_status: Optional[str]

# Router setup
router = APIRouter(prefix="/kpi-schedules", tags=["KPI Schedules"])

def get_schedule_service() -> KPIScheduleService:
    """Dependency to get KPI schedule service"""
    connection_string = get_mssql_connection_string()
    return KPIScheduleService(connection_string)

def get_execution_service() -> ScheduleExecutionService:
    """Dependency to get schedule execution service"""
    connection_string = get_mssql_connection_string()
    return ScheduleExecutionService(connection_string)

@router.post("/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    request: CreateScheduleRequest,
    service: KPIScheduleService = Depends(get_schedule_service)
):
    """
    Create a new KPI schedule
    
    Creates a new schedule for executing a KPI at specified intervals.
    The schedule will be automatically synced with Apache Airflow.
    """
    try:
        # Convert Pydantic model to dict
        schedule_data = request.dict()
        
        # Convert datetime objects to ISO strings
        schedule_data['start_date'] = request.start_date.isoformat()
        if request.end_date:
            schedule_data['end_date'] = request.end_date.isoformat()
        
        # Create the schedule
        schedule = service.create_schedule(schedule_data)
        
        logger.info(f"✓ Created schedule {schedule['id']} for KPI {request.kpi_id}")
        
        return schedule
        
    except ValueError as e:
        logger.warning(f"Invalid schedule data: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create schedule"
        )

@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: int,
    service: KPIScheduleService = Depends(get_schedule_service)
):
    """
    Get a specific schedule by ID
    
    Returns detailed information about a schedule including recent execution history.
    """
    try:
        schedule = service.get_schedule(schedule_id)
        
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule {schedule_id} not found"
            )
        
        return schedule
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get schedule {schedule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve schedule"
        )

@router.get("/kpi/{kpi_id}", response_model=List[ScheduleListResponse])
async def get_schedules_by_kpi(
    kpi_id: int,
    service: KPIScheduleService = Depends(get_schedule_service)
):
    """
    Get all schedules for a specific KPI

    Returns a list of all schedules configured for the given KPI.
    """
    try:
        schedules = service.get_schedules_by_kpi(kpi_id)
        return schedules

    except Exception as e:
        logger.error(f"Failed to get schedules for KPI {kpi_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve schedules"
        )

@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    request: UpdateScheduleRequest,
    service: KPIScheduleService = Depends(get_schedule_service)
):
    """
    Update an existing schedule

    Updates schedule configuration. Changes will be synced with Airflow.
    """
    try:
        # Convert Pydantic model to dict, excluding None values
        update_data = request.dict(exclude_none=True)

        # Convert datetime objects to ISO strings
        if 'start_date' in update_data and update_data['start_date']:
            update_data['start_date'] = request.start_date.isoformat()
        if 'end_date' in update_data and update_data['end_date']:
            update_data['end_date'] = request.end_date.isoformat()

        # Update the schedule
        schedule = service.update_schedule(schedule_id, update_data)

        logger.info(f"✓ Updated schedule {schedule_id}")

        return schedule

    except ValueError as e:
        logger.warning(f"Invalid update data for schedule {schedule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to update schedule {schedule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update schedule"
        )

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    service: KPIScheduleService = Depends(get_schedule_service)
):
    """
    Delete a schedule

    Removes the schedule and stops future executions. The schedule will be removed from Airflow.
    """
    try:
        success = service.delete_schedule(schedule_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule {schedule_id} not found"
            )

        logger.info(f"✓ Deleted schedule {schedule_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete schedule {schedule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete schedule"
        )

@router.post("/{schedule_id}/toggle", response_model=ScheduleResponse)
async def toggle_schedule(
    schedule_id: int,
    service: KPIScheduleService = Depends(get_schedule_service)
):
    """
    Toggle schedule active/inactive status

    Convenience endpoint to enable/disable a schedule.
    """
    try:
        # Get current schedule
        schedule = service.get_schedule(schedule_id)

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule {schedule_id} not found"
            )

        # Toggle the active status
        new_status = not schedule['is_active']
        updated_schedule = service.update_schedule(schedule_id, {'is_active': new_status})

        status_text = "enabled" if new_status else "disabled"
        logger.info(f"✓ Schedule {schedule_id} {status_text}")

        return updated_schedule

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle schedule {schedule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle schedule"
        )

# Schedule Execution Endpoints

class CreateExecutionRequest(BaseModel):
    """Request model for creating a schedule execution record"""
    schedule_id: int = Field(..., gt=0)
    kpi_id: int = Field(..., gt=0)
    scheduled_time: datetime
    actual_start_time: Optional[datetime] = None
    execution_status: str = Field(default="pending", pattern="^(pending|running|success|failed|retrying|cancelled)$")
    airflow_task_id: Optional[str] = Field(None, max_length=255)
    airflow_run_id: Optional[str] = Field(None, max_length=255)

class UpdateExecutionRequest(BaseModel):
    """Request model for updating a schedule execution record"""
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    execution_status: Optional[str] = Field(None, pattern="^(pending|running|success|failed|retrying|cancelled)$")
    error_message: Optional[str] = None
    retry_count: Optional[int] = Field(None, ge=0)
    execution_id: Optional[int] = None  # Link to kpi_execution_results

@router.post("/executions/", status_code=status.HTTP_201_CREATED)
async def create_execution_record(
    request: CreateExecutionRequest,
    service: ScheduleExecutionService = Depends(get_execution_service)
):
    """
    Create a new schedule execution record

    Used by Airflow DAGs to track execution progress.
    """
    try:
        execution_data = request.dict()
        execution_data['scheduled_time'] = request.scheduled_time.isoformat()
        if request.actual_start_time:
            execution_data['actual_start_time'] = request.actual_start_time.isoformat()

        execution = service.create_execution_record(execution_data)

        logger.info(f"✓ Created execution record {execution['id']}")

        return execution

    except ValueError as e:
        logger.warning(f"Invalid execution data: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create execution record: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create execution record"
        )

@router.put("/executions/{execution_id}")
async def update_execution_record(
    execution_id: int,
    request: UpdateExecutionRequest,
    service: ScheduleExecutionService = Depends(get_execution_service)
):
    """
    Update a schedule execution record

    Used by Airflow DAGs to update execution status and results.
    """
    try:
        update_data = request.dict(exclude_none=True)

        # Convert datetime objects to ISO strings
        if 'actual_start_time' in update_data and update_data['actual_start_time']:
            update_data['actual_start_time'] = request.actual_start_time.isoformat()
        if 'actual_end_time' in update_data and update_data['actual_end_time']:
            update_data['actual_end_time'] = request.actual_end_time.isoformat()

        execution = service.update_execution_record(execution_id, update_data)

        logger.info(f"✓ Updated execution record {execution_id}")

        return execution

    except ValueError as e:
        logger.warning(f"Invalid update data for execution {execution_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to update execution record {execution_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update execution record"
        )

@router.get("/executions/{execution_id}")
async def get_execution_record(
    execution_id: int,
    service: ScheduleExecutionService = Depends(get_execution_service)
):
    """Get a specific execution record by ID"""
    try:
        execution = service.get_execution_record(execution_id)

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution record {execution_id} not found"
            )

        return execution

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get execution record {execution_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve execution record"
        )

@router.get("/{schedule_id}/executions")
async def get_schedule_executions(
    schedule_id: int,
    limit: int = 50,
    service: ScheduleExecutionService = Depends(get_execution_service)
):
    """Get execution history for a specific schedule"""
    try:
        executions = service.get_executions_by_schedule(schedule_id, limit)
        return executions

    except Exception as e:
        logger.error(f"Failed to get executions for schedule {schedule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve execution history"
        )

@router.get("/{schedule_id}/statistics")
async def get_schedule_statistics(
    schedule_id: int,
    days: int = 30,
    service: ScheduleExecutionService = Depends(get_execution_service)
):
    """Get execution statistics for a schedule"""
    try:
        stats = service.get_execution_statistics(schedule_id, days)
        return stats

    except Exception as e:
        logger.error(f"Failed to get statistics for schedule {schedule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve execution statistics"
        )

@router.post("/{schedule_id}/trigger")
async def trigger_schedule_manually(
    schedule_id: int,
    service: KPIScheduleService = Depends(get_schedule_service)
):
    """Manually trigger a schedule execution"""
    try:
        result = service.manual_trigger_schedule(schedule_id)
        return result

    except ValueError as e:
        logger.warning(f"Invalid trigger request for schedule {schedule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to trigger schedule {schedule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger schedule"
        )

@router.get("/{schedule_id}/airflow-status")
async def get_schedule_airflow_status(
    schedule_id: int,
    service: KPIScheduleService = Depends(get_schedule_service)
):
    """Get Airflow DAG status for a schedule"""
    try:
        status_info = service.get_airflow_dag_status(schedule_id)
        return status_info

    except Exception as e:
        logger.error(f"Failed to get Airflow status for schedule {schedule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Airflow status"
        )

@router.post("/sync-all-to-airflow")
async def sync_all_schedules_to_airflow(
    service: KPIScheduleService = Depends(get_schedule_service)
):
    """Sync all active schedules to Airflow"""
    try:
        result = service.sync_all_schedules_to_airflow()
        return result

    except Exception as e:
        logger.error(f"Failed to sync schedules to Airflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync schedules to Airflow"
        )

@router.get("/dashboard-overview")
async def get_dashboard_overview(
    service: KPIScheduleService = Depends(get_schedule_service),
    execution_service: ScheduleExecutionService = Depends(get_execution_service)
):
    """Get comprehensive dashboard overview for monitoring"""
    try:
        # Get all schedules
        conn = service._get_connection()
        cursor = conn.cursor()

        # Get schedule counts
        cursor.execute("""
            SELECT
                COUNT(*) as total_schedules,
                SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_schedules
            FROM kpi_schedules
        """)
        schedule_counts = cursor.fetchone()

        # Get 24h execution statistics
        cursor.execute("""
            SELECT
                COUNT(*) as total_executions,
                SUM(CASE WHEN execution_status = 'success' THEN 1 ELSE 0 END) as successful_executions,
                SUM(CASE WHEN execution_status = 'failed' THEN 1 ELSE 0 END) as failed_executions
            FROM kpi_schedule_executions
            WHERE scheduled_time >= DATEADD(hour, -24, GETDATE())
        """)
        execution_stats = cursor.fetchone()

        # Get recent executions with schedule and KPI info
        cursor.execute("""
            SELECT TOP 10
                e.id, e.execution_status, e.scheduled_time, e.actual_start_time, e.actual_end_time,
                s.schedule_name, s.next_execution, k.name as kpi_name,
                CASE
                    WHEN e.actual_start_time IS NOT NULL AND e.actual_end_time IS NOT NULL
                    THEN CONCAT(DATEDIFF(second, e.actual_start_time, e.actual_end_time), 's')
                    ELSE NULL
                END as duration
            FROM kpi_schedule_executions e
            JOIN kpi_schedules s ON e.schedule_id = s.id
            JOIN kpi_definitions k ON e.kpi_id = k.id
            ORDER BY e.scheduled_time DESC
        """)
        recent_executions = cursor.fetchall()

        cursor.close()
        conn.close()

        # Calculate success rate
        total_24h = execution_stats[0] or 0
        successful_24h = execution_stats[1] or 0
        success_rate = (successful_24h / total_24h * 100) if total_24h > 0 else 0

        # Format recent executions
        recent_executions_data = []
        for row in recent_executions:
            execution = {
                'id': row[0],
                'execution_status': row[1],
                'scheduled_time': row[2].isoformat() if row[2] else None,
                'actual_start_time': row[3].isoformat() if row[3] else None,
                'actual_end_time': row[4].isoformat() if row[4] else None,
                'schedule_name': row[5],
                'next_execution': row[6].isoformat() if row[6] else None,
                'kpi_name': row[7],
                'duration': row[8]
            }
            recent_executions_data.append(execution)

        # Get sync status (placeholder for now)
        sync_status = {
            'total_schedules': schedule_counts[0] or 0,
            'synced_successfully': schedule_counts[1] or 0,  # Active schedules assumed synced
            'sync_failures': 0
        }

        # Generate alerts based on data
        alerts = []
        if execution_stats[2] and execution_stats[2] > 5:  # More than 5 failures in 24h
            alerts.append({
                'severity': 'warning',
                'message': f'{execution_stats[2]} executions failed in the last 24 hours'
            })

        if success_rate < 80 and total_24h > 0:
            alerts.append({
                'severity': 'error',
                'message': f'Success rate is low: {success_rate:.1f}%'
            })

        dashboard_data = {
            'total_schedules': schedule_counts[0] or 0,
            'active_schedules': schedule_counts[1] or 0,
            'total_executions_24h': total_24h,
            'successful_executions_24h': successful_24h,
            'failed_executions_24h': execution_stats[2] or 0,
            'success_rate': success_rate,
            'recent_executions': recent_executions_data,
            'airflow_sync_status': sync_status,
            'alerts': alerts,
            'last_updated': datetime.now().isoformat()
        }

        return dashboard_data

    except Exception as e:
        logger.error(f"Failed to get dashboard overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard overview"
        )
