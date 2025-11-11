-- KPI Analytics Database Schema Creation Script
-- Run this on your MS SQL Server to create the KPI database and tables

-- Create KPI_Analytics database if it doesn't exist
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'KPI_Analytics')
BEGIN
    CREATE DATABASE KPI_Analytics;
    PRINT 'Created KPI_Analytics database';
END
ELSE
BEGIN
    PRINT 'KPI_Analytics database already exists';
END
GO

-- Use the KPI_Analytics database
USE [KPI_Analytics];
GO

-- Create kpi_definitions table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='kpi_definitions' AND xtype='U')
BEGIN
    CREATE TABLE kpi_definitions (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(255) NOT NULL UNIQUE,
        alias_name NVARCHAR(100),
        group_name NVARCHAR(100),
        description NVARCHAR(MAX),
        nl_definition NVARCHAR(MAX),
        created_at DATETIME2 DEFAULT GETDATE(),
        updated_at DATETIME2 DEFAULT GETDATE(),
        created_by NVARCHAR(100),
        is_active BIT DEFAULT 1
    );
    
    PRINT 'Created kpi_definitions table';
END
ELSE
BEGIN
    PRINT 'kpi_definitions table already exists';
END
GO

-- Create kpi_execution_results table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='kpi_execution_results' AND xtype='U')
BEGIN
    CREATE TABLE kpi_execution_results (
        id INT IDENTITY(1,1) PRIMARY KEY,
        kpi_id INT NOT NULL,
        kg_name NVARCHAR(100),
        select_schema NVARCHAR(100),
        ruleset_name NVARCHAR(255),
        db_type NVARCHAR(50),
        limit_records INT,
        use_llm BIT,
        excluded_fields NVARCHAR(MAX),
        generated_sql NVARCHAR(MAX),
        number_of_records INT,
        joined_columns NVARCHAR(MAX),
        sql_query_type NVARCHAR(100),
        operation NVARCHAR(100),
        execution_status NVARCHAR(50),
        execution_timestamp DATETIME2 DEFAULT GETDATE(),
        execution_time_ms INT,
        confidence_score FLOAT,
        error_message NVARCHAR(MAX),
        result_data NVARCHAR(MAX),
        evidence_data NVARCHAR(MAX),
        evidence_count INT,
        source_table NVARCHAR(255),
        target_table NVARCHAR(255),
        user_id NVARCHAR(100),
        session_id NVARCHAR(100),
        client_ip NVARCHAR(50),
        user_agent NVARCHAR(500),
        
        CONSTRAINT FK_kpi_execution_results_kpi_id 
            FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id)
    );
    
    PRINT 'Created kpi_execution_results table';
END
ELSE
BEGIN
    PRINT 'kpi_execution_results table already exists';
END
GO

-- Create indexes for better performance
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_kpi_definitions_name')
BEGIN
    CREATE INDEX IX_kpi_definitions_name ON kpi_definitions(name);
    PRINT 'Created index on kpi_definitions.name';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_kpi_definitions_group_name')
BEGIN
    CREATE INDEX IX_kpi_definitions_group_name ON kpi_definitions(group_name);
    PRINT 'Created index on kpi_definitions.group_name';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_kpi_execution_results_kpi_id')
BEGIN
    CREATE INDEX IX_kpi_execution_results_kpi_id ON kpi_execution_results(kpi_id);
    PRINT 'Created index on kpi_execution_results.kpi_id';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_kpi_execution_results_timestamp')
BEGIN
    CREATE INDEX IX_kpi_execution_results_timestamp ON kpi_execution_results(execution_timestamp);
    PRINT 'Created index on kpi_execution_results.execution_timestamp';
END
GO

-- Insert sample KPI for testing
IF NOT EXISTS (SELECT * FROM kpi_definitions WHERE name = 'Test KPI Connection')
BEGIN
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition, created_by
    ) VALUES (
        'Test KPI Connection',
        'TEST_CONN',
        'System Test',
        'Test KPI to verify database connection and API functionality',
        'Show me a simple test query to verify the system is working',
        'system'
    );
    
    PRINT 'Inserted test KPI';
END
GO

-- Verify schema creation
PRINT 'Schema verification:';
SELECT 
    'kpi_definitions' as table_name,
    COUNT(*) as record_count
FROM kpi_definitions
UNION ALL
SELECT 
    'kpi_execution_results' as table_name,
    COUNT(*) as record_count
FROM kpi_execution_results;
GO

PRINT 'KPI Analytics database schema setup complete!';
PRINT 'You can now use the enhanced KPI API endpoints.';
GO
