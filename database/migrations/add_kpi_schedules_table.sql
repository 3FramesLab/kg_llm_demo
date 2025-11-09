-- KPI Scheduling System Database Schema
-- Phase 1: Foundation - Create tables for KPI schedule management

-- Table: kpi_schedules
-- Stores schedule configuration for each KPI
CREATE TABLE kpi_schedules (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    kpi_id BIGINT NOT NULL,
    schedule_name NVARCHAR(255) NOT NULL,
    schedule_type NVARCHAR(50) NOT NULL, -- 'daily', 'weekly', 'monthly', 'cron'
    cron_expression NVARCHAR(100), -- For custom schedules
    timezone NVARCHAR(50) DEFAULT 'UTC',
    is_active BIT DEFAULT 1,
    start_date DATETIME2 NOT NULL,
    end_date DATETIME2 NULL, -- Optional end date
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    created_by NVARCHAR(100),
    
    -- Schedule configuration JSON (for complex schedules)
    schedule_config NVARCHAR(MAX), -- JSON: {"retry_count": 3, "retry_delay": 300, "timeout": 3600}
    
    -- Airflow integration
    airflow_dag_id NVARCHAR(255), -- Generated DAG ID in Airflow
    last_sync_at DATETIME2, -- Last sync with Airflow
    
    -- Constraints
    CONSTRAINT FK_kpi_schedules_kpi_id FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id) ON DELETE CASCADE,
    CONSTRAINT CHK_schedule_type CHECK (schedule_type IN ('daily', 'weekly', 'monthly', 'cron')),
    CONSTRAINT CHK_cron_required CHECK (
        (schedule_type = 'cron' AND cron_expression IS NOT NULL) OR 
        (schedule_type != 'cron')
    )
);

-- Table: kpi_schedule_executions
-- Tracks execution history for scheduled KPIs
CREATE TABLE kpi_schedule_executions (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    schedule_id BIGINT NOT NULL,
    kpi_id BIGINT NOT NULL,
    execution_id BIGINT NULL, -- Links to kpi_execution_results.id
    
    -- Execution metadata
    scheduled_time DATETIME2 NOT NULL, -- When it was supposed to run
    actual_start_time DATETIME2, -- When it actually started
    actual_end_time DATETIME2, -- When it completed
    execution_status NVARCHAR(50) NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'success', 'failed', 'retrying'
    
    -- Airflow integration
    airflow_task_id NVARCHAR(255),
    airflow_run_id NVARCHAR(255),
    
    -- Error handling
    error_message NVARCHAR(MAX),
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    
    -- Timestamps
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    
    -- Constraints
    CONSTRAINT FK_schedule_executions_schedule_id FOREIGN KEY (schedule_id) REFERENCES kpi_schedules(id) ON DELETE CASCADE,
    CONSTRAINT FK_schedule_executions_kpi_id FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id),
    CONSTRAINT FK_schedule_executions_execution_id FOREIGN KEY (execution_id) REFERENCES kpi_execution_results(id),
    CONSTRAINT CHK_execution_status CHECK (execution_status IN ('pending', 'running', 'success', 'failed', 'retrying', 'cancelled'))
);

-- Table: kpi_schedule_notifications
-- Stores notification preferences and history
CREATE TABLE kpi_schedule_notifications (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    schedule_id BIGINT NOT NULL,
    notification_type NVARCHAR(50) NOT NULL, -- 'email', 'webhook'
    notification_config NVARCHAR(MAX), -- JSON: {"email": "user@example.com", "on_failure": true, "on_success": false}
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),

    CONSTRAINT FK_schedule_notifications_schedule_id FOREIGN KEY (schedule_id) REFERENCES kpi_schedules(id) ON DELETE CASCADE,
    CONSTRAINT CHK_notification_type CHECK (notification_type IN ('email', 'webhook'))
);

-- Indexes for performance
CREATE INDEX IX_kpi_schedules_kpi_id ON kpi_schedules(kpi_id);
CREATE INDEX IX_kpi_schedules_is_active ON kpi_schedules(is_active);
CREATE INDEX IX_kpi_schedules_airflow_dag_id ON kpi_schedules(airflow_dag_id);

CREATE INDEX IX_schedule_executions_schedule_id ON kpi_schedule_executions(schedule_id);
CREATE INDEX IX_schedule_executions_scheduled_time ON kpi_schedule_executions(scheduled_time);
CREATE INDEX IX_schedule_executions_status ON kpi_schedule_executions(execution_status);

CREATE INDEX IX_schedule_notifications_schedule_id ON kpi_schedule_notifications(schedule_id);
