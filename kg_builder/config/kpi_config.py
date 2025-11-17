"""
KPI Analytics Configuration
Configuration settings for separate KPI Analytics database.
"""

import os
from typing import Dict, Any

# ==================== KPI Database Configuration ====================

# KPI Analytics Database Settings
KPI_DB_HOST = os.getenv('KPI_DB_HOST', 'localhost')
KPI_DB_PORT = int(os.getenv('KPI_DB_PORT', '1433'))
KPI_DB_DATABASE = os.getenv('KPI_DB_DATABASE', 'KPI_Analytics')
KPI_DB_USERNAME = os.getenv('KPI_DB_USERNAME', 'sa')
KPI_DB_PASSWORD = os.getenv('KPI_DB_PASSWORD', 'YourPassword123')

# Connection Pool Settings
KPI_DB_POOL_SIZE = int(os.getenv('KPI_DB_POOL_SIZE', '10'))
KPI_DB_MAX_OVERFLOW = int(os.getenv('KPI_DB_MAX_OVERFLOW', '20'))
KPI_DB_POOL_TIMEOUT = int(os.getenv('KPI_DB_POOL_TIMEOUT', '30'))

# ==================== KPI Execution Settings ====================

# Default execution parameters
DEFAULT_KPI_SETTINGS = {
    'limit_records': 1000,
    'use_llm': True,
    'db_type': 'sqlserver',
    'timeout_seconds': 300,
    'retry_attempts': 3,
    'retry_delay_seconds': 5
}

# SLA Settings by Priority
KPI_SLA_SETTINGS = {
    'high': {
        'target_execution_time_ms': 15000,  # 15 seconds
        'max_execution_time_ms': 30000,     # 30 seconds
        'alert_threshold_ms': 20000         # 20 seconds
    },
    'medium': {
        'target_execution_time_ms': 30000,  # 30 seconds
        'max_execution_time_ms': 60000,     # 60 seconds
        'alert_threshold_ms': 45000         # 45 seconds
    },
    'low': {
        'target_execution_time_ms': 60000,  # 60 seconds
        'max_execution_time_ms': 120000,    # 2 minutes
        'alert_threshold_ms': 90000         # 90 seconds
    }
}

# ==================== Data Retention Settings ====================

# Data retention policies
DATA_RETENTION_POLICIES = {
    'high_priority': {
        'execution_results_days': 365,      # 1 year
        'evidence_data_days': 90,           # 3 months
        'error_logs_days': 180              # 6 months
    },
    'medium_priority': {
        'execution_results_days': 180,      # 6 months
        'evidence_data_days': 60,           # 2 months
        'error_logs_days': 90               # 3 months
    },
    'low_priority': {
        'execution_results_days': 90,       # 3 months
        'evidence_data_days': 30,           # 1 month
        'error_logs_days': 60               # 2 months
    }
}

# ==================== Analytics Settings ====================

# Analytics and reporting settings
ANALYTICS_SETTINGS = {
    'enable_performance_tracking': True,
    'enable_usage_analytics': True,
    'enable_error_analytics': True,
    'daily_summary_enabled': True,
    'weekly_reports_enabled': True,
    'monthly_reports_enabled': True
}

# Dashboard refresh intervals (in seconds)
DASHBOARD_REFRESH_INTERVALS = {
    'real_time': 30,        # 30 seconds
    'near_real_time': 300,  # 5 minutes
    'periodic': 1800,       # 30 minutes
    'daily': 86400          # 24 hours
}

# ==================== Security Settings ====================

# Security and access control
SECURITY_SETTINGS = {
    'enable_audit_logging': True,
    'log_sql_queries': True,
    'log_user_actions': True,
    'enable_ip_tracking': True,
    'session_timeout_minutes': 480,  # 8 hours
    'max_concurrent_executions_per_user': 5
}

# ==================== Performance Settings ====================

# Performance optimization settings
PERFORMANCE_SETTINGS = {
    'enable_query_caching': True,
    'cache_ttl_seconds': 3600,          # 1 hour
    'max_result_set_size': 10000,       # Maximum rows to return
    'enable_result_compression': True,
    'enable_parallel_execution': True,
    'max_parallel_executions': 3
}

# ==================== Monitoring Settings ====================

# Monitoring and alerting
MONITORING_SETTINGS = {
    'enable_health_checks': True,
    'health_check_interval_seconds': 60,
    'enable_performance_alerts': True,
    'enable_error_alerts': True,
    'alert_email_enabled': False,
    'alert_webhook_enabled': False
}

# ==================== Feature Flags ====================

# Feature toggles
FEATURE_FLAGS = {
    'enable_ops_planner_enhancement': True,
    'enable_advanced_analytics': True,
    'enable_ml_insights': False,
    'enable_predictive_analytics': False,
    'enable_automated_optimization': False,
    'enable_custom_visualizations': True
}

# ==================== Helper Functions ====================

def get_kpi_connection_string() -> str:
    """Get KPI Analytics database connection string."""
    # Handle named SQL Server instances (contains backslash)
    if '\\' in KPI_DB_HOST:
        # Named instance - don't include port
        server_part = KPI_DB_HOST
    else:
        # Default instance or IP - include port
        server_part = f"{KPI_DB_HOST},{KPI_DB_PORT}"

    return (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server_part};"
        f"DATABASE={KPI_DB_DATABASE};"
        f"UID={KPI_DB_USERNAME};"
        f"PWD={KPI_DB_PASSWORD};"
        f"TrustServerCertificate=yes;"
    )

def get_sla_settings(priority: str) -> Dict[str, Any]:
    """Get SLA settings for a given priority level."""
    return KPI_SLA_SETTINGS.get(priority, KPI_SLA_SETTINGS['medium'])

def get_retention_policy(priority: str) -> Dict[str, Any]:
    """Get data retention policy for a given priority level."""
    return DATA_RETENTION_POLICIES.get(f"{priority}_priority", DATA_RETENTION_POLICIES['medium_priority'])

def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled."""
    return FEATURE_FLAGS.get(feature_name, False)

# ==================== Environment-Specific Overrides ====================

# Override settings based on environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development').lower()

if ENVIRONMENT == 'production':
    # Production-specific settings
    DEFAULT_KPI_SETTINGS['limit_records'] = 5000
    PERFORMANCE_SETTINGS['max_result_set_size'] = 50000
    SECURITY_SETTINGS['enable_audit_logging'] = True
    MONITORING_SETTINGS['enable_performance_alerts'] = True
    
elif ENVIRONMENT == 'staging':
    # Staging-specific settings
    DEFAULT_KPI_SETTINGS['limit_records'] = 2000
    PERFORMANCE_SETTINGS['max_result_set_size'] = 20000
    
elif ENVIRONMENT == 'development':
    # Development-specific settings
    DEFAULT_KPI_SETTINGS['limit_records'] = 500
    SECURITY_SETTINGS['log_sql_queries'] = True
    FEATURE_FLAGS['enable_ml_insights'] = True  # Enable experimental features in dev
