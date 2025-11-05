"""
Configuration settings for the Knowledge Graph Builder application.
"""
import os
from pathlib import Path
from typing import Optional

# Project paths
BASE_DIR = Path(__file__).parent.parent
SCHEMAS_DIR = BASE_DIR / "schemas"
DATA_DIR = BASE_DIR / "data"

# Ensure directories exist
SCHEMAS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# FastAPI settings
API_TITLE = "Knowledge Graph Builder"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Build knowledge graphs from JSON schema files using FalkorDB and Graphiti"

# FalkorDB settings
FALKORDB_HOST = os.getenv("FALKORDB_HOST", "localhost")
FALKORDB_PORT = int(os.getenv("FALKORDB_PORT", 6379))
FALKORDB_DB = int(os.getenv("FALKORDB_DB", 0))
FALKORDB_PASSWORD: Optional[str] = os.getenv("FALKORDB_PASSWORD", None)

# Graphiti settings
GRAPHITI_STORAGE_PATH = DATA_DIR / "graphiti_storage"
GRAPHITI_STORAGE_PATH.mkdir(exist_ok=True)

# Schema processing settings
MAX_SCHEMA_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_SCHEMA_FORMATS = [".json"]

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")  # Temporarily force DEBUG

# API settings
CORS_ORIGINS = ["*"]
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))

# LLM Feature flags
ENABLE_LLM_EXTRACTION = os.getenv("ENABLE_LLM_EXTRACTION", "true").lower() == "true"
ENABLE_LLM_ANALYSIS = os.getenv("ENABLE_LLM_ANALYSIS", "true").lower() == "true"

# Reconciliation settings
RECON_STORAGE_PATH = DATA_DIR / os.getenv("RECON_STORAGE_PATH", "reconciliation_rules")
RECON_MIN_CONFIDENCE = float(os.getenv("RECON_MIN_CONFIDENCE", "0.7"))
RECON_ENABLE_LLM = os.getenv("RECON_ENABLE_LLM", "true").lower() == "true"
RECON_SAMPLE_SIZE = int(os.getenv("RECON_SAMPLE_SIZE", "100"))

# Ensure reconciliation storage exists
RECON_STORAGE_PATH.mkdir(exist_ok=True, parents=True)

# JDBC settings for rule validation
JDBC_DRIVERS_PATH = os.getenv("JDBC_DRIVERS_PATH", str(BASE_DIR / "jdbc_drivers"))

# Database connection settings for reconciliation
# Source Database Configuration
SOURCE_DB_TYPE = os.getenv("SOURCE_DB_TYPE", "oracle")
SOURCE_DB_HOST = os.getenv("SOURCE_DB_HOST", "localhost")
SOURCE_DB_PORT = int(os.getenv("SOURCE_DB_PORT", "1521"))
SOURCE_DB_DATABASE = os.getenv("SOURCE_DB_DATABASE", "ORCL")
SOURCE_DB_USERNAME = os.getenv("SOURCE_DB_USERNAME", "")
SOURCE_DB_PASSWORD = os.getenv("SOURCE_DB_PASSWORD", "")
SOURCE_DB_SERVICE_NAME = os.getenv("SOURCE_DB_SERVICE_NAME", "")  # For Oracle

# Target Database Configuration
TARGET_DB_TYPE = os.getenv("TARGET_DB_TYPE", "oracle")
TARGET_DB_HOST = os.getenv("TARGET_DB_HOST", "localhost")
TARGET_DB_PORT = int(os.getenv("TARGET_DB_PORT", "1521"))
TARGET_DB_DATABASE = os.getenv("TARGET_DB_DATABASE", "ORCL")
TARGET_DB_USERNAME = os.getenv("TARGET_DB_USERNAME", "")
TARGET_DB_PASSWORD = os.getenv("TARGET_DB_PASSWORD", "")
TARGET_DB_SERVICE_NAME = os.getenv("TARGET_DB_SERVICE_NAME", "")  # For Oracle

# Execution settings
USE_ENV_DB_CONFIGS = os.getenv("USE_ENV_DB_CONFIGS", "true").lower() == "true"

# MongoDB settings (for reconciliation results storage)
MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
MONGODB_PORT = int(os.getenv("MONGODB_PORT", "27017"))
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME", "admin")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "admin123")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "reconciliation")
MONGODB_AUTH_SOURCE = os.getenv("MONGODB_AUTH_SOURCE", "admin")
MONGODB_RESULTS_COLLECTION = os.getenv("MONGODB_RESULTS_COLLECTION", "reconciliation_results")

# Landing Database Configuration (for multi-database reconciliation)
LANDING_DB_ENABLED = os.getenv("LANDING_DB_ENABLED", "false").lower() == "true"
LANDING_DB_TYPE = os.getenv("LANDING_DB_TYPE", "mysql")
LANDING_DB_HOST = os.getenv("LANDING_DB_HOST", "localhost")
LANDING_DB_PORT = int(os.getenv("LANDING_DB_PORT", "3306"))
LANDING_DB_DATABASE = os.getenv("LANDING_DB_DATABASE", "reconciliation_landing")
LANDING_DB_USERNAME = os.getenv("LANDING_DB_USERNAME", "")
LANDING_DB_PASSWORD = os.getenv("LANDING_DB_PASSWORD", "")
LANDING_DB_SCHEMA = os.getenv("LANDING_DB_SCHEMA", "staging")  # Schema for staging tables
LANDING_KEEP_STAGING = os.getenv("LANDING_KEEP_STAGING", "true").lower() == "true"  # Keep for 24h
LANDING_STAGING_TTL_HOURS = int(os.getenv("LANDING_STAGING_TTL_HOURS", "24"))  # Auto-cleanup after 24 hours
LANDING_BATCH_SIZE = int(os.getenv("LANDING_BATCH_SIZE", "10000"))  # Rows per batch
LANDING_USE_BULK_COPY = os.getenv("LANDING_USE_BULK_COPY", "true").lower() == "true"  # Use LOAD DATA INFILE


def get_source_db_config():
    """
    Get source database configuration from environment variables.

    Returns:
        DatabaseConnectionInfo if credentials are configured, None otherwise
    """
    if not SOURCE_DB_USERNAME or not SOURCE_DB_PASSWORD:
        return None

    from kg_builder.models import DatabaseConnectionInfo

    config = DatabaseConnectionInfo(
        db_type=SOURCE_DB_TYPE,
        host=SOURCE_DB_HOST,
        port=SOURCE_DB_PORT,
        database=SOURCE_DB_DATABASE,
        username=SOURCE_DB_USERNAME,
        password=SOURCE_DB_PASSWORD,
        service_name=SOURCE_DB_SERVICE_NAME if SOURCE_DB_SERVICE_NAME else None
    )

    return config


def get_target_db_config():
    """
    Get target database configuration from environment variables.

    Returns:
        DatabaseConnectionInfo if credentials are configured, None otherwise
    """
    if not TARGET_DB_USERNAME or not TARGET_DB_PASSWORD:
        return None

    from kg_builder.models import DatabaseConnectionInfo

    config = DatabaseConnectionInfo(
        db_type=TARGET_DB_TYPE,
        host=TARGET_DB_HOST,
        port=TARGET_DB_PORT,
        database=TARGET_DB_DATABASE,
        username=TARGET_DB_USERNAME,
        password=TARGET_DB_PASSWORD,
        service_name=TARGET_DB_SERVICE_NAME if TARGET_DB_SERVICE_NAME else None
    )

    return config


def get_mongodb_connection_string() -> str:
    """
    Build MongoDB connection string from configuration.

    Returns:
        MongoDB connection string
    """
    if MONGODB_USERNAME and MONGODB_PASSWORD:
        return (
            f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}"
            f"@{MONGODB_HOST}:{MONGODB_PORT}/"
            f"?authSource={MONGODB_AUTH_SOURCE}"
        )
    else:
        return f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}/"


def get_landing_db_config():
    """
    Get landing database configuration from environment variables.

    Returns:
        DatabaseConnectionInfo if credentials are configured, None otherwise
    """
    if not LANDING_DB_ENABLED or not LANDING_DB_USERNAME or not LANDING_DB_PASSWORD:
        return None

    from kg_builder.models import DatabaseConnectionInfo

    config = DatabaseConnectionInfo(
        db_type=LANDING_DB_TYPE,
        host=LANDING_DB_HOST,
        port=LANDING_DB_PORT,
        database=LANDING_DB_DATABASE,
        username=LANDING_DB_USERNAME,
        password=LANDING_DB_PASSWORD,
        schema=LANDING_DB_SCHEMA
    )

    return config


# KPI File-Based Storage Configuration
KPI_STORAGE_TYPE = os.getenv("KPI_STORAGE_TYPE", "file")  # Options: "file", "mongodb"
KPI_DATA_DIR = DATA_DIR / "kpi"
KPI_RESULTS_RETENTION_DAYS = int(os.getenv("KPI_RESULTS_RETENTION_DAYS", "90"))
KPI_ENABLE_CACHING = os.getenv("KPI_ENABLE_CACHING", "true").lower() == "true"

# Ensure KPI directories exist
KPI_DATA_DIR.mkdir(exist_ok=True, parents=True)


# Local SQLite database for storing reconciliation results (for KPI queries)
RESULTS_DB_PATH = DATA_DIR / os.getenv("RESULTS_DB_PATH", "reconciliation_results.db")


def get_database_connection():
    """
    Get a connection to the local SQLite database for reconciliation results.

    This database stores reconciliation execution results that can be queried
    by the KPI system for calculations and evidence drill-down.

    Returns:
        sqlite3.Connection: SQLite database connection
    """
    import sqlite3

    # Ensure database directory exists
    RESULTS_DB_PATH.parent.mkdir(exist_ok=True, parents=True)

    conn = sqlite3.connect(str(RESULTS_DB_PATH))

    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")

    return conn

