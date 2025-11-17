-- ============================================================================
-- Comprehensive KPI Database Creation Script
-- Creates complete KPI Analytics database with all tables and relationships
-- Database: KPI_Analytics
-- Version: 2.0
-- Date: 2024-11-10
-- ============================================================================

-- Create database if it doesn't exist
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'KPI_Analytics')
BEGIN
    CREATE DATABASE KPI_Analytics;
    PRINT 'Database KPI_Analytics created successfully.';
END
ELSE
BEGIN
    PRINT 'Database KPI_Analytics already exists.';
END
GO

USE KPI_Analytics;
GO

-- ============================================================================
-- 1. KPI DEFINITIONS TABLE
-- Stores KPI metadata, definitions, and configuration
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='kpi_definitions' AND xtype='U')
BEGIN
    CREATE TABLE kpi_definitions (
        -- Primary identification
        id INTEGER PRIMARY KEY IDENTITY(1,1),
        name VARCHAR(255) NOT NULL,
        alias_name VARCHAR(255),
        group_name VARCHAR(255),
        
        -- KPI content and definition
        description TEXT,
        nl_definition TEXT NOT NULL,
        
        -- Audit fields
        created_at DATETIME2 DEFAULT GETDATE(),
        updated_at DATETIME2 DEFAULT GETDATE(),
        created_by VARCHAR(100),
        
        -- Status and configuration
        is_active BIT DEFAULT 1,
        business_priority VARCHAR(50) DEFAULT 'medium',
        target_sla_seconds INT DEFAULT 30,
        execution_frequency VARCHAR(50) DEFAULT 'on_demand',
        data_retention_days INT DEFAULT 90,
        
        -- SQL caching and optimization
        isAccept BIT DEFAULT 0,
        isSQLCached BIT DEFAULT 0,
        cached_sql TEXT,
        sql_generation_method VARCHAR(50) DEFAULT 'llm',
        
        -- Thresholds and alerting
        warning_threshold DECIMAL(10,4),
        critical_threshold DECIMAL(10,4),
        threshold_operator VARCHAR(20) DEFAULT 'less_than',
        
        -- Metadata
        tags VARCHAR(500),
        documentation_url VARCHAR(500),
        owner_email VARCHAR(255),
        
        -- Constraints
        CONSTRAINT chk_priority CHECK (business_priority IN ('low', 'medium', 'high', 'critical')),
        CONSTRAINT chk_frequency CHECK (execution_frequency IN ('on_demand', 'hourly', 'daily', 'weekly', 'monthly')),
        CONSTRAINT chk_threshold_op CHECK (threshold_operator IN ('less_than', 'greater_than', 'equal_to', 'not_equal_to')),
        CONSTRAINT chk_sql_method CHECK (sql_generation_method IN ('llm', 'cached', 'template'))
    );
    
    -- Indexes for performance
    CREATE INDEX idx_kpi_definitions_name ON kpi_definitions(name);
    CREATE INDEX idx_kpi_definitions_group ON kpi_definitions(group_name);
    CREATE INDEX idx_kpi_definitions_active ON kpi_definitions(is_active);
    CREATE INDEX idx_kpi_definitions_priority ON kpi_definitions(business_priority);
    CREATE INDEX idx_kpi_definitions_created ON kpi_definitions(created_at);
    
    PRINT 'Table kpi_definitions created successfully.';
END
ELSE
BEGIN
    PRINT 'Table kpi_definitions already exists.';
END
GO

-- ============================================================================
-- 2. KPI EXECUTION RESULTS TABLE
-- Stores execution history, results, and performance metrics
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='kpi_execution_results' AND xtype='U')
BEGIN
    CREATE TABLE kpi_execution_results (
        -- Primary identification
        id INTEGER PRIMARY KEY IDENTITY(1,1),
        kpi_id INTEGER NOT NULL,
        
        -- Execution metadata
        execution_timestamp DATETIME2 DEFAULT GETDATE(),
        execution_status VARCHAR(50) NOT NULL DEFAULT 'pending',
        execution_type VARCHAR(50) DEFAULT 'manual',
        
        -- Execution parameters
        execution_params TEXT,
        user_id VARCHAR(100),
        session_id VARCHAR(100),

        -- Schema and database context
        select_schema VARCHAR(255) NOT NULL DEFAULT 'default',
        kg_name VARCHAR(255),
        db_type VARCHAR(50) DEFAULT 'sqlserver',
        schemas TEXT, -- JSON array of schemas
        definitions TEXT, -- JSON array of definitions
        
        -- SQL and query information
        generated_sql TEXT,
        final_sql TEXT,
        sql_generation_time_ms DECIMAL(10,2),
        query_execution_time_ms DECIMAL(10,2),
        
        -- Results and metrics
        number_of_records INTEGER DEFAULT 0,
        result_data TEXT,
        calculated_value DECIMAL(15,6),
        
        -- Performance metrics
        total_execution_time_ms DECIMAL(10,2),
        memory_usage_mb DECIMAL(10,2),
        cpu_usage_percent DECIMAL(5,2),

        -- Additional execution settings
        use_llm BIT DEFAULT 1,
        min_confidence DECIMAL(5,4) DEFAULT 0.7,
        limit_records INTEGER DEFAULT 1000,
        
        -- Status and error handling
        confidence_score DECIMAL(5,4),
        error_message TEXT,
        error_type VARCHAR(100),
        retry_count INTEGER DEFAULT 0,
        
        -- Data lineage and traceability
        source_tables VARCHAR(1000),
        join_columns VARCHAR(500),
        filters_applied VARCHAR(1000),
        
        -- Caching and optimization
        used_cached_sql BIT DEFAULT 0,
        cache_hit BIT DEFAULT 0,
        
        -- Foreign key constraint
        CONSTRAINT fk_execution_kpi FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id) ON DELETE CASCADE,
        
        -- Check constraints
        CONSTRAINT chk_execution_status CHECK (execution_status IN ('pending', 'running', 'success', 'failed', 'timeout', 'cancelled')),
        CONSTRAINT chk_execution_type CHECK (execution_type IN ('manual', 'scheduled', 'api', 'batch', 'test'))
    );
    
    -- Indexes for performance
    CREATE INDEX idx_execution_kpi_id ON kpi_execution_results(kpi_id);
    CREATE INDEX idx_execution_timestamp ON kpi_execution_results(execution_timestamp);
    CREATE INDEX idx_execution_status ON kpi_execution_results(execution_status);
    CREATE INDEX idx_execution_user ON kpi_execution_results(user_id);
    CREATE INDEX idx_execution_type ON kpi_execution_results(execution_type);
    
    PRINT 'Table kpi_execution_results created successfully.';
END
ELSE
BEGIN
    PRINT 'Table kpi_execution_results already exists.';
END
GO

-- ============================================================================
-- 3. KPI SCHEDULES TABLE
-- Stores KPI scheduling configuration and cron expressions
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='kpi_schedules' AND xtype='U')
BEGIN
    CREATE TABLE kpi_schedules (
        -- Primary identification
        id INTEGER PRIMARY KEY IDENTITY(1,1),
        kpi_id INTEGER NOT NULL,

        -- Schedule identification
        schedule_name VARCHAR(255) NOT NULL,
        description TEXT,

        -- Schedule configuration
        cron_expression VARCHAR(100) NOT NULL,
        timezone VARCHAR(50) DEFAULT 'UTC',
        is_active BIT DEFAULT 1,

        -- Execution parameters
        execution_params TEXT,
        max_execution_time_seconds INTEGER DEFAULT 300,
        retry_count INTEGER DEFAULT 3,
        retry_delay_seconds INTEGER DEFAULT 60,

        -- Schedule metadata
        created_at DATETIME2 DEFAULT GETDATE(),
        updated_at DATETIME2 DEFAULT GETDATE(),
        created_by VARCHAR(100),

        -- Next execution tracking
        next_execution_time DATETIME2,
        last_execution_time DATETIME2,
        last_execution_status VARCHAR(50),

        -- Notification settings
        notify_on_success BIT DEFAULT 0,
        notify_on_failure BIT DEFAULT 1,
        notification_emails VARCHAR(1000),

        -- Schedule limits and controls
        max_concurrent_executions INTEGER DEFAULT 1,
        execution_timeout_action VARCHAR(50) DEFAULT 'kill',

        -- Foreign key constraint
        CONSTRAINT fk_schedule_kpi FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id) ON DELETE CASCADE,

        -- Check constraints
        CONSTRAINT chk_schedule_status CHECK (last_execution_status IN ('success', 'failed', 'timeout', 'cancelled', 'pending') OR last_execution_status IS NULL),
        CONSTRAINT chk_timeout_action CHECK (execution_timeout_action IN ('kill', 'wait', 'notify'))
    );

    -- Indexes for performance
    CREATE INDEX idx_schedules_kpi_id ON kpi_schedules(kpi_id);
    CREATE INDEX idx_schedules_active ON kpi_schedules(is_active);
    CREATE INDEX idx_schedules_next_exec ON kpi_schedules(next_execution_time);
    CREATE INDEX idx_schedules_cron ON kpi_schedules(cron_expression);

    PRINT 'Table kpi_schedules created successfully.';
END
ELSE
BEGIN
    PRINT 'Table kpi_schedules already exists.';
END
GO

-- ============================================================================
-- 4. KPI SCHEDULE EXECUTIONS TABLE
-- Tracks individual schedule execution instances
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='kpi_schedule_executions' AND xtype='U')
BEGIN
    CREATE TABLE kpi_schedule_executions (
        -- Primary identification
        id INTEGER PRIMARY KEY IDENTITY(1,1),
        schedule_id INTEGER NOT NULL,
        kpi_id INTEGER NOT NULL,

        -- Execution timing
        scheduled_time DATETIME2 NOT NULL,
        actual_start_time DATETIME2,
        actual_end_time DATETIME2,

        -- Execution status and results
        execution_status VARCHAR(50) NOT NULL DEFAULT 'pending',
        execution_id INTEGER, -- Links to kpi_execution_results

        -- Error handling
        error_message TEXT,
        retry_attempt INTEGER DEFAULT 0,

        -- Performance tracking
        queue_wait_time_ms DECIMAL(10,2),
        total_duration_ms DECIMAL(10,2),

        -- Metadata
        triggered_by VARCHAR(100) DEFAULT 'scheduler',
        execution_node VARCHAR(100),

        -- Foreign key constraints
        CONSTRAINT fk_schedule_exec_schedule FOREIGN KEY (schedule_id) REFERENCES kpi_schedules(id) ON DELETE CASCADE,
        CONSTRAINT fk_schedule_exec_kpi FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id) ON DELETE CASCADE,
        CONSTRAINT fk_schedule_exec_result FOREIGN KEY (execution_id) REFERENCES kpi_execution_results(id),

        -- Check constraints
        CONSTRAINT chk_schedule_exec_status CHECK (execution_status IN ('pending', 'running', 'success', 'failed', 'timeout', 'cancelled', 'skipped'))
    );

    -- Indexes for performance
    CREATE INDEX idx_schedule_exec_schedule_id ON kpi_schedule_executions(schedule_id);
    CREATE INDEX idx_schedule_exec_kpi_id ON kpi_schedule_executions(kpi_id);
    CREATE INDEX idx_schedule_exec_scheduled_time ON kpi_schedule_executions(scheduled_time);
    CREATE INDEX idx_schedule_exec_status ON kpi_schedule_executions(execution_status);

    PRINT 'Table kpi_schedule_executions created successfully.';
END
ELSE
BEGIN
    PRINT 'Table kpi_schedule_executions already exists.';
END
GO

-- ============================================================================
-- 5. KPI ALERTS TABLE
-- Stores alert configurations and threshold violations
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='kpi_alerts' AND xtype='U')
BEGIN
    CREATE TABLE kpi_alerts (
        -- Primary identification
        id INTEGER PRIMARY KEY IDENTITY(1,1),
        kpi_id INTEGER NOT NULL,

        -- Alert configuration
        alert_name VARCHAR(255) NOT NULL,
        alert_type VARCHAR(50) NOT NULL,
        severity VARCHAR(20) NOT NULL,

        -- Threshold configuration
        threshold_value DECIMAL(15,6),
        comparison_operator VARCHAR(20),
        consecutive_violations INTEGER DEFAULT 1,

        -- Alert status and timing
        is_active BIT DEFAULT 1,
        created_at DATETIME2 DEFAULT GETDATE(),
        updated_at DATETIME2 DEFAULT GETDATE(),

        -- Notification settings
        notification_channels VARCHAR(500), -- email,slack,webhook
        notification_template TEXT,
        cooldown_minutes INTEGER DEFAULT 60,

        -- Alert metadata
        description TEXT,
        created_by VARCHAR(100),

        -- Foreign key constraint
        CONSTRAINT fk_alert_kpi FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id) ON DELETE CASCADE,

        -- Check constraints
        CONSTRAINT chk_alert_type CHECK (alert_type IN ('threshold', 'execution_failure', 'data_quality', 'performance')),
        CONSTRAINT chk_alert_severity CHECK (severity IN ('info', 'warning', 'critical', 'emergency')),
        CONSTRAINT chk_alert_operator CHECK (comparison_operator IN ('less_than', 'greater_than', 'equal_to', 'not_equal_to'))
    );

    -- Indexes for performance
    CREATE INDEX idx_alerts_kpi_id ON kpi_alerts(kpi_id);
    CREATE INDEX idx_alerts_active ON kpi_alerts(is_active);
    CREATE INDEX idx_alerts_type ON kpi_alerts(alert_type);
    CREATE INDEX idx_alerts_severity ON kpi_alerts(severity);

    PRINT 'Table kpi_alerts created successfully.';
END
ELSE
BEGIN
    PRINT 'Table kpi_alerts already exists.';
END
GO

-- ============================================================================
-- 6. KPI ALERT HISTORY TABLE
-- Tracks alert firing history and notifications sent
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='kpi_alert_history' AND xtype='U')
BEGIN
    CREATE TABLE kpi_alert_history (
        -- Primary identification
        id INTEGER PRIMARY KEY IDENTITY(1,1),
        alert_id INTEGER NOT NULL,
        kpi_id INTEGER NOT NULL,
        execution_id INTEGER,

        -- Alert event details
        fired_at DATETIME2 DEFAULT GETDATE(),
        alert_status VARCHAR(50) NOT NULL,

        -- Threshold violation details
        actual_value DECIMAL(15,6),
        threshold_value DECIMAL(15,6),
        violation_count INTEGER DEFAULT 1,

        -- Notification tracking
        notifications_sent TEXT, -- JSON array of sent notifications
        notification_status VARCHAR(50),

        -- Resolution tracking
        resolved_at DATETIME2,
        resolved_by VARCHAR(100),
        resolution_notes TEXT,

        -- Metadata
        alert_message TEXT,
        context_data TEXT, -- JSON with additional context

        -- Foreign key constraints
        CONSTRAINT fk_alert_history_alert FOREIGN KEY (alert_id) REFERENCES kpi_alerts(id) ON DELETE CASCADE,
        CONSTRAINT fk_alert_history_kpi FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id) ON DELETE CASCADE,
        CONSTRAINT fk_alert_history_execution FOREIGN KEY (execution_id) REFERENCES kpi_execution_results(id),

        -- Check constraints
        CONSTRAINT chk_alert_history_status CHECK (alert_status IN ('fired', 'resolved', 'suppressed', 'escalated')),
        CONSTRAINT chk_notification_status CHECK (notification_status IN ('pending', 'sent', 'failed', 'skipped'))
    );

    -- Indexes for performance
    CREATE INDEX idx_alert_history_alert_id ON kpi_alert_history(alert_id);
    CREATE INDEX idx_alert_history_kpi_id ON kpi_alert_history(kpi_id);
    CREATE INDEX idx_alert_history_fired_at ON kpi_alert_history(fired_at);
    CREATE INDEX idx_alert_history_status ON kpi_alert_history(alert_status);

    PRINT 'Table kpi_alert_history created successfully.';
END
ELSE
BEGIN
    PRINT 'Table kpi_alert_history already exists.';
END
GO

-- ============================================================================
-- 7. KPI AUDIT LOG TABLE
-- Tracks all changes to KPI definitions and configurations
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='kpi_audit_log' AND xtype='U')
BEGIN
    CREATE TABLE kpi_audit_log (
        -- Primary identification
        id INTEGER PRIMARY KEY IDENTITY(1,1),
        kpi_id INTEGER,

        -- Audit event details
        action VARCHAR(50) NOT NULL,
        table_name VARCHAR(100) NOT NULL,
        record_id INTEGER,

        -- Change tracking
        old_values TEXT, -- JSON of old values
        new_values TEXT, -- JSON of new values
        changed_fields VARCHAR(1000), -- Comma-separated list

        -- Audit metadata
        changed_at DATETIME2 DEFAULT GETDATE(),
        changed_by VARCHAR(100) NOT NULL,
        user_ip VARCHAR(45),
        user_agent VARCHAR(500),
        session_id VARCHAR(100),

        -- Context information
        change_reason VARCHAR(500),
        application_context VARCHAR(100),

        -- Foreign key constraint (nullable for deleted KPIs)
        CONSTRAINT fk_audit_kpi FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id),

        -- Check constraints
        CONSTRAINT chk_audit_action CHECK (action IN ('CREATE', 'UPDATE', 'DELETE', 'EXECUTE', 'SCHEDULE', 'ALERT'))
    );

    -- Indexes for performance
    CREATE INDEX idx_audit_kpi_id ON kpi_audit_log(kpi_id);
    CREATE INDEX idx_audit_changed_at ON kpi_audit_log(changed_at);
    CREATE INDEX idx_audit_changed_by ON kpi_audit_log(changed_by);
    CREATE INDEX idx_audit_action ON kpi_audit_log(action);
    CREATE INDEX idx_audit_table ON kpi_audit_log(table_name);

    PRINT 'Table kpi_audit_log created successfully.';
END
ELSE
BEGIN
    PRINT 'Table kpi_audit_log already exists.';
END
GO

-- ============================================================================
-- 8. KPI CONFIGURATION TABLE
-- Stores system-wide KPI configuration and settings
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='kpi_configuration' AND xtype='U')
BEGIN
    CREATE TABLE kpi_configuration (
        -- Primary identification
        id INTEGER PRIMARY KEY IDENTITY(1,1),
        config_key VARCHAR(100) NOT NULL UNIQUE,
        config_value TEXT,

        -- Configuration metadata
        config_type VARCHAR(50) NOT NULL,
        description TEXT,
        default_value TEXT,

        -- Validation and constraints
        validation_regex VARCHAR(500),
        allowed_values VARCHAR(1000), -- Comma-separated for enum types
        min_value DECIMAL(15,6),
        max_value DECIMAL(15,6),

        -- Configuration management
        is_active BIT DEFAULT 1,
        is_system BIT DEFAULT 0, -- System configs cannot be deleted
        requires_restart BIT DEFAULT 0,

        -- Audit fields
        created_at DATETIME2 DEFAULT GETDATE(),
        updated_at DATETIME2 DEFAULT GETDATE(),
        updated_by VARCHAR(100),

        -- Check constraints
        CONSTRAINT chk_config_type CHECK (config_type IN ('string', 'integer', 'decimal', 'boolean', 'json', 'enum', 'url', 'email'))
    );

    -- Indexes for performance
    CREATE INDEX idx_config_key ON kpi_configuration(config_key);
    CREATE INDEX idx_config_type ON kpi_configuration(config_type);
    CREATE INDEX idx_config_active ON kpi_configuration(is_active);

    PRINT 'Table kpi_configuration created successfully.';
END
ELSE
BEGIN
    PRINT 'Table kpi_configuration already exists.';
END
GO

-- ============================================================================
-- 9. VIEWS FOR KPI ANALYTICS
-- Create useful views for reporting and analytics
-- ============================================================================

-- KPI Dashboard View
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'vw_kpi_dashboard')
BEGIN
    EXEC('
    CREATE VIEW vw_kpi_dashboard AS
    SELECT
        k.id,
        k.name,
        k.group_name,
        k.business_priority,
        k.is_active,
        k.created_at,

        -- Latest execution info
        e.execution_timestamp as last_execution,
        e.execution_status as last_status,
        e.number_of_records as last_record_count,
        e.total_execution_time_ms as last_execution_time,
        e.confidence_score as last_confidence,

        -- Schedule info
        s.cron_expression,
        s.next_execution_time,
        s.is_active as schedule_active,

        -- Performance metrics
        AVG(CAST(e_avg.total_execution_time_ms AS FLOAT)) as avg_execution_time,
        COUNT(e_count.id) as total_executions,
        SUM(CASE WHEN e_count.execution_status = ''success'' THEN 1 ELSE 0 END) as successful_executions,

        -- Alert status
        COUNT(a.id) as active_alerts

    FROM kpi_definitions k
    LEFT JOIN kpi_execution_results e ON k.id = e.kpi_id
        AND e.execution_timestamp = (
            SELECT MAX(execution_timestamp)
            FROM kpi_execution_results
            WHERE kpi_id = k.id
        )
    LEFT JOIN kpi_schedules s ON k.id = s.kpi_id AND s.is_active = 1
    LEFT JOIN kpi_execution_results e_avg ON k.id = e_avg.kpi_id
        AND e_avg.execution_timestamp >= DATEADD(day, -30, GETDATE())
    LEFT JOIN kpi_execution_results e_count ON k.id = e_count.kpi_id
    LEFT JOIN kpi_alerts a ON k.id = a.kpi_id AND a.is_active = 1

    WHERE k.is_active = 1
    GROUP BY
        k.id, k.name, k.group_name, k.business_priority, k.is_active, k.created_at,
        e.execution_timestamp, e.execution_status, e.number_of_records,
        e.total_execution_time_ms, e.confidence_score,
        s.cron_expression, s.next_execution_time, s.is_active
    ');

    PRINT 'View vw_kpi_dashboard created successfully.';
END
ELSE
BEGIN
    PRINT 'View vw_kpi_dashboard already exists.';
END
GO

-- KPI Performance View
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'vw_kpi_performance')
BEGIN
    EXEC('
    CREATE VIEW vw_kpi_performance AS
    SELECT
        k.id as kpi_id,
        k.name as kpi_name,
        k.group_name,

        -- Execution statistics
        COUNT(e.id) as total_executions,
        SUM(CASE WHEN e.execution_status = ''success'' THEN 1 ELSE 0 END) as successful_executions,
        SUM(CASE WHEN e.execution_status = ''failed'' THEN 1 ELSE 0 END) as failed_executions,

        -- Performance metrics
        AVG(CAST(e.total_execution_time_ms AS FLOAT)) as avg_execution_time_ms,
        MIN(e.total_execution_time_ms) as min_execution_time_ms,
        MAX(e.total_execution_time_ms) as max_execution_time_ms,

        -- Data metrics
        AVG(CAST(e.number_of_records AS FLOAT)) as avg_records_processed,
        SUM(e.number_of_records) as total_records_processed,

        -- Quality metrics
        AVG(CAST(e.confidence_score AS FLOAT)) as avg_confidence_score,

        -- Time ranges
        MIN(e.execution_timestamp) as first_execution,
        MAX(e.execution_timestamp) as last_execution,

        -- Success rate
        CASE
            WHEN COUNT(e.id) > 0
            THEN CAST(SUM(CASE WHEN e.execution_status = ''success'' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(e.id) * 100
            ELSE 0
        END as success_rate_percent

    FROM kpi_definitions k
    LEFT JOIN kpi_execution_results e ON k.id = e.kpi_id
        AND e.execution_timestamp >= DATEADD(day, -30, GETDATE())

    WHERE k.is_active = 1
    GROUP BY k.id, k.name, k.group_name
    ');

    PRINT 'View vw_kpi_performance created successfully.';
END
ELSE
BEGIN
    PRINT 'View vw_kpi_performance already exists.';
END
GO

-- ============================================================================
-- 10. TRIGGERS FOR AUDIT LOGGING
-- Automatically track changes to KPI definitions
-- ============================================================================

-- Trigger for KPI definitions audit
IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'tr_kpi_definitions_audit')
BEGIN
    EXEC('
    CREATE TRIGGER tr_kpi_definitions_audit
    ON kpi_definitions
    AFTER INSERT, UPDATE, DELETE
    AS
    BEGIN
        SET NOCOUNT ON;

        -- Handle INSERT
        IF EXISTS (SELECT * FROM inserted) AND NOT EXISTS (SELECT * FROM deleted)
        BEGIN
            INSERT INTO kpi_audit_log (kpi_id, action, table_name, record_id, new_values, changed_by, changed_at)
            SELECT
                i.id,
                ''CREATE'',
                ''kpi_definitions'',
                i.id,
                (SELECT * FROM inserted i2 WHERE i2.id = i.id FOR JSON AUTO),
                SYSTEM_USER,
                GETDATE()
            FROM inserted i;
        END

        -- Handle UPDATE
        IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
        BEGIN
            INSERT INTO kpi_audit_log (kpi_id, action, table_name, record_id, old_values, new_values, changed_by, changed_at)
            SELECT
                i.id,
                ''UPDATE'',
                ''kpi_definitions'',
                i.id,
                (SELECT * FROM deleted d WHERE d.id = i.id FOR JSON AUTO),
                (SELECT * FROM inserted i2 WHERE i2.id = i.id FOR JSON AUTO),
                SYSTEM_USER,
                GETDATE()
            FROM inserted i;
        END

        -- Handle DELETE
        IF NOT EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
        BEGIN
            INSERT INTO kpi_audit_log (kpi_id, action, table_name, record_id, old_values, changed_by, changed_at)
            SELECT
                d.id,
                ''DELETE'',
                ''kpi_definitions'',
                d.id,
                (SELECT * FROM deleted d2 WHERE d2.id = d.id FOR JSON AUTO),
                SYSTEM_USER,
                GETDATE()
            FROM deleted d;
        END
    END
    ');

    PRINT 'Trigger tr_kpi_definitions_audit created successfully.';
END
ELSE
BEGIN
    PRINT 'Trigger tr_kpi_definitions_audit already exists.';
END
GO

-- Trigger to update updated_at timestamp
IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'tr_kpi_definitions_updated_at')
BEGIN
    EXEC('
    CREATE TRIGGER tr_kpi_definitions_updated_at
    ON kpi_definitions
    BEFORE UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        UPDATE kpi_definitions
        SET updated_at = GETDATE()
        FROM kpi_definitions k
        INNER JOIN inserted i ON k.id = i.id;
    END
    ');

    PRINT 'Trigger tr_kpi_definitions_updated_at created successfully.';
END
ELSE
BEGIN
    PRINT 'Trigger tr_kpi_definitions_updated_at already exists.';
END
GO

-- ============================================================================
-- 11. STORED PROCEDURES
-- Useful procedures for KPI management
-- ============================================================================

-- Procedure to cleanup old execution results
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_cleanup_old_executions')
BEGIN
    EXEC('
    CREATE PROCEDURE sp_cleanup_old_executions
        @retention_days INT = 90,
        @batch_size INT = 1000
    AS
    BEGIN
        SET NOCOUNT ON;

        DECLARE @deleted_count INT = 0;
        DECLARE @total_deleted INT = 0;
        DECLARE @cutoff_date DATETIME2 = DATEADD(day, -@retention_days, GETDATE());

        PRINT ''Starting cleanup of execution results older than '' + CAST(@retention_days AS VARCHAR) + '' days'';
        PRINT ''Cutoff date: '' + CAST(@cutoff_date AS VARCHAR);

        WHILE 1 = 1
        BEGIN
            DELETE TOP (@batch_size)
            FROM kpi_execution_results
            WHERE execution_timestamp < @cutoff_date;

            SET @deleted_count = @@ROWCOUNT;
            SET @total_deleted = @total_deleted + @deleted_count;

            IF @deleted_count = 0 BREAK;

            PRINT ''Deleted '' + CAST(@deleted_count AS VARCHAR) + '' records (Total: '' + CAST(@total_deleted AS VARCHAR) + '')'';
            WAITFOR DELAY ''00:00:01''; -- Small delay to avoid blocking
        END

        PRINT ''Cleanup completed. Total records deleted: '' + CAST(@total_deleted AS VARCHAR);
    END
    ');

    PRINT 'Stored procedure sp_cleanup_old_executions created successfully.';
END
ELSE
BEGIN
    PRINT 'Stored procedure sp_cleanup_old_executions already exists.';
END
GO

-- Procedure to get KPI health status
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_get_kpi_health_status')
BEGIN
    EXEC('
    CREATE PROCEDURE sp_get_kpi_health_status
        @kpi_id INT = NULL
    AS
    BEGIN
        SET NOCOUNT ON;

        SELECT
            k.id,
            k.name,
            k.group_name,
            k.is_active,

            -- Recent execution status
            CASE
                WHEN e.execution_timestamp IS NULL THEN ''Never Executed''
                WHEN e.execution_timestamp < DATEADD(day, -7, GETDATE()) THEN ''Stale''
                WHEN e.execution_status = ''success'' THEN ''Healthy''
                WHEN e.execution_status = ''failed'' THEN ''Unhealthy''
                ELSE ''Unknown''
            END as health_status,

            e.execution_timestamp as last_execution,
            e.execution_status as last_status,
            e.error_message as last_error,

            -- Performance indicators
            CASE
                WHEN e.total_execution_time_ms > 30000 THEN ''Slow''
                WHEN e.total_execution_time_ms > 10000 THEN ''Moderate''
                ELSE ''Fast''
            END as performance_status,

            -- Schedule status
            s.is_active as scheduled,
            s.next_execution_time,

            -- Alert status
            COUNT(a.id) as active_alerts

        FROM kpi_definitions k
        LEFT JOIN kpi_execution_results e ON k.id = e.kpi_id
            AND e.execution_timestamp = (
                SELECT MAX(execution_timestamp)
                FROM kpi_execution_results
                WHERE kpi_id = k.id
            )
        LEFT JOIN kpi_schedules s ON k.id = s.kpi_id AND s.is_active = 1
        LEFT JOIN kpi_alerts a ON k.id = a.kpi_id AND a.is_active = 1

        WHERE (@kpi_id IS NULL OR k.id = @kpi_id)
            AND k.is_active = 1

        GROUP BY
            k.id, k.name, k.group_name, k.is_active,
            e.execution_timestamp, e.execution_status, e.error_message, e.total_execution_time_ms,
            s.is_active, s.next_execution_time

        ORDER BY k.name;
    END
    ');

    PRINT 'Stored procedure sp_get_kpi_health_status created successfully.';
END
ELSE
BEGIN
    PRINT 'Stored procedure sp_get_kpi_health_status already exists.';
END
GO

-- ============================================================================
-- 12. INITIAL CONFIGURATION DATA
-- Insert default system configuration values
-- ============================================================================

-- Insert default configuration values
IF NOT EXISTS (SELECT 1 FROM kpi_configuration WHERE config_key = 'default_execution_timeout')
BEGIN
    INSERT INTO kpi_configuration (config_key, config_value, config_type, description, default_value, is_system)
    VALUES
    ('default_execution_timeout', '300', 'integer', 'Default KPI execution timeout in seconds', '300', 1),
    ('max_concurrent_executions', '10', 'integer', 'Maximum number of concurrent KPI executions', '10', 1),
    ('default_retry_count', '3', 'integer', 'Default number of retries for failed executions', '3', 1),
    ('cleanup_retention_days', '90', 'integer', 'Number of days to retain execution results', '90', 1),
    ('enable_audit_logging', 'true', 'boolean', 'Enable audit logging for all KPI changes', 'true', 1),
    ('default_confidence_threshold', '0.7', 'decimal', 'Default confidence threshold for LLM-generated SQL', '0.7', 1),
    ('enable_sql_caching', 'true', 'boolean', 'Enable SQL caching for improved performance', 'true', 1),
    ('notification_cooldown_minutes', '60', 'integer', 'Default cooldown period for alert notifications', '60', 1),
    ('dashboard_refresh_interval', '30', 'integer', 'Dashboard auto-refresh interval in seconds', '30', 0),
    ('enable_performance_monitoring', 'true', 'boolean', 'Enable detailed performance monitoring', 'true', 1);

    PRINT 'Default configuration values inserted successfully.';
END
ELSE
BEGIN
    PRINT 'Configuration values already exist.';
END
GO

-- ============================================================================
-- 13. SAMPLE DATA (OPTIONAL)
-- Insert sample KPI definitions for testing
-- ============================================================================

-- Sample KPI definitions
IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = 'Sample Material Match Rate')
BEGIN
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_by, business_priority, execution_frequency,
        warning_threshold, critical_threshold, threshold_operator
    )
    VALUES
    (
        'Sample Material Match Rate',
        'material_match_rate',
        'Data Quality',
        'Percentage of materials successfully matched between source and target systems',
        'Calculate the percentage of materials that have been successfully matched',
        'system',
        'high',
        'daily',
        85.0,
        70.0,
        'less_than'
    ),
    (
        'Sample Execution Performance',
        'execution_performance',
        'System Performance',
        'Average execution time for data reconciliation processes',
        'Calculate the average execution time for all reconciliation processes in the last 24 hours',
        'system',
        'medium',
        'hourly',
        5000.0,
        10000.0,
        'greater_than'
    );

    PRINT 'Sample KPI definitions inserted successfully.';
END
ELSE
BEGIN
    PRINT 'Sample KPI definitions already exist.';
END
GO

-- ============================================================================
-- 14. COMPLETION AND VERIFICATION
-- Final steps and verification queries
-- ============================================================================

-- Verify all tables were created
PRINT '';
PRINT '============================================================================';
PRINT 'DATABASE CREATION COMPLETED';
PRINT '============================================================================';
PRINT '';

-- List all created tables
PRINT 'Created Tables:';
SELECT
    TABLE_NAME,
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = t.TABLE_NAME) as COLUMN_COUNT
FROM INFORMATION_SCHEMA.TABLES t
WHERE TABLE_TYPE = 'BASE TABLE'
    AND TABLE_CATALOG = 'KPI_Analytics'
ORDER BY TABLE_NAME;

-- List all created views
PRINT '';
PRINT 'Created Views:';
SELECT TABLE_NAME as VIEW_NAME
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_CATALOG = 'KPI_Analytics'
ORDER BY TABLE_NAME;

-- List all created stored procedures
PRINT '';
PRINT 'Created Stored Procedures:';
SELECT name as PROCEDURE_NAME
FROM sys.procedures
WHERE type = 'P'
ORDER BY name;

-- Show configuration count
PRINT '';
PRINT 'Configuration Entries:';
SELECT COUNT(*) as CONFIG_COUNT FROM kpi_configuration;

PRINT '';
PRINT '============================================================================';
PRINT 'KPI Analytics Database Setup Complete!';
PRINT '';
PRINT 'Next Steps:';
PRINT '1. Configure your application connection strings';
PRINT '2. Test KPI creation and execution';
PRINT '3. Set up scheduled jobs for cleanup procedures';
PRINT '4. Configure alert notifications';
PRINT '============================================================================';
PRINT '';
