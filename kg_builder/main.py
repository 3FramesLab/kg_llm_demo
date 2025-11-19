"""
Main FastAPI application for Knowledge Graph Builder.
"""
import logging
import logging.config
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi

# Load environment variables from .env file
load_dotenv()

from kg_builder.config import (
    API_TITLE, API_VERSION, API_DESCRIPTION,
    CORS_ORIGINS, CORS_CREDENTIALS, CORS_METHODS, CORS_HEADERS,
    LOG_LEVEL
)
from kg_builder.routes import router
from kg_builder.routes_hints import router as hints_router
from kg_builder.routers.kpi_schedule_router import router as schedule_router
from kg_builder.routers.database_router import router as database_router
from kg_builder.logging_config import LOGGING_CONFIG
from kg_builder.middleware import DetailedLoggingMiddleware

# Configure logging with console handler
import sys

# Configure logging that works with uvicorn on Windows (both CLI and python -m)
def setup_logging():
    """Setup logging configuration that works with uvicorn on Windows."""
    # Apply the logging config
    logging.config.dictConfig(LOGGING_CONFIG)

    # Update levels based on LOG_LEVEL from config
    logging.getLogger('kg_builder').setLevel(getattr(logging, LOG_LEVEL))

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured at {LOG_LEVEL} level")
    print(f"[STARTUP] Logging configured at {LOG_LEVEL} level - Console handler active", flush=True)
    return logger

async def initialize_jvm_with_jdbc_drivers():
    """Initialize JVM with all JDBC drivers in classpath."""
    try:
        import jpype
        import glob
        import os
        from kg_builder.config import JDBC_DRIVERS_PATH

        # Check if JVM is already started
        if jpype.isJVMStarted():
            logger.info("JVM already started - skipping JDBC driver initialization")
            return

        logger.info("🚀 Initializing JVM with all JDBC drivers...")

        # Find all JDBC driver JAR files
        jdbc_patterns = [
            "mssql-jdbc*.jar",      # SQL Server
            "mysql-connector-j*.jar", # MySQL
            "postgresql-*.jar",     # PostgreSQL
            "ojdbc*.jar"           # Oracle
        ]

        all_jars = []
        for pattern in jdbc_patterns:
            jar_pattern = os.path.join(JDBC_DRIVERS_PATH, pattern)
            jars = glob.glob(jar_pattern)
            all_jars.extend(jars)

        if not all_jars:
            logger.warning(f"No JDBC drivers found in {JDBC_DRIVERS_PATH}")
            return

        logger.info(f"Found {len(all_jars)} JDBC drivers:")
        for jar in all_jars:
            logger.info(f"  - {os.path.basename(jar)}")

        # Start JVM with all JDBC drivers in classpath
        classpath = os.pathsep.join(all_jars)
        jpype.startJVM(jpype.getDefaultJVMPath(), f"-Djava.class.path={classpath}")

        logger.info("✅ JVM initialized successfully with all JDBC drivers")

    except ImportError:
        logger.warning("JPype not available - JDBC functionality will be limited")
    except Exception as e:
        logger.error(f"Failed to initialize JVM with JDBC drivers: {e}")


class JavaAwareJSONResponse(JSONResponse):
    """Custom JSON response that handles Java objects."""

    def render(self, content) -> bytes:
        from kg_builder.utils.java_json_encoder import convert_java_objects_recursive
        import json

        # Convert all Java objects to Python objects
        converted_content = convert_java_objects_recursive(content)

        # Use standard JSON encoding
        return json.dumps(
            converted_content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


# Setup logging before creating the app
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add detailed logging middleware (must be first to capture all requests)
app.add_middleware(
    DetailedLoggingMiddleware,
    log_request_body=True,
    log_response_body=True
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_CREDENTIALS,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)

# Include routes
app.include_router(router, prefix="/v1", tags=["Knowledge Graph"])
app.include_router(hints_router, prefix="/v1", tags=["Column Hints"])
app.include_router(schedule_router, prefix="/v1", tags=["KPI Schedules"])
app.include_router(database_router, prefix="/v1", tags=["Database Connections"])

# KPI Analytics routes are now included directly in routes.py

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "description": API_DESCRIPTION,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json"
    }


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info(f"Starting {API_TITLE} v{API_VERSION}")

    # Initialize backends
    from kg_builder.services.falkordb_backend import get_falkordb_backend
    from kg_builder.services.graphiti_backend import get_graphiti_backend

    falkordb = get_falkordb_backend()
    graphiti = get_graphiti_backend()

    logger.info(f"FalkorDB connected: {falkordb.is_connected()}")
    logger.info(f"Graphiti available: {graphiti.is_available()}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info(f"Shutting down {API_TITLE}")


def custom_openapi():
    """Customize OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=API_TITLE,
        version=API_VERSION,
        description=API_DESCRIPTION,
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn

    print("[STARTUP] Starting uvicorn server...", flush=True)

    uvicorn.run(
        "kg_builder.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=LOG_LEVEL.lower(),
        log_config=LOGGING_CONFIG,
        use_colors=True  # Enable colors for better visibility on Windows
    )

