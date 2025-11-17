# Complete DQ-POC Codebase Exploration Summary

## Executive Summary

This document provides a comprehensive overview of the DQ-POC (Data Quality Proof of Concept) codebase, a sophisticated Knowledge Graph Builder and KPI Analytics Platform built with FastAPI.

**Base Directory:** `/Users/rchirrareddy/Desktop/dq-poc/`

---

## 1. ARCHITECTURE OVERVIEW

### Technology Stack
- **Backend Framework:** FastAPI (async)
- **Server:** Uvicorn (ASGI)
- **Graph Databases:** FalkorDB (Redis-based), Graphiti (in-memory)
- **Data Databases:** Oracle, SQL Server, MySQL, PostgreSQL
- **Results Storage:** MongoDB, SQLite
- **LLM Integration:** OpenAI API
- **Frontend:** React
- **Deployment:** Docker, Docker Compose, OpenShift

### Core Components
1. **API Server** - FastAPI application with 70+ endpoints
2. **Graph Layer** - Knowledge graph generation and querying
3. **NL Processing** - Natural language to SQL conversion
4. **KPI Engine** - KPI definition, execution, and analytics
5. **Reconciliation** - Data reconciliation and validation
6. **Scheduling** - Airflow-based task scheduling

---

## 2. MAIN API ENTRY POINT

**File:** `/Users/rchirrareddy/Desktop/dq-poc/kg_builder/main.py`
**Type:** FastAPI Application
**Port:** 8000
**Host:** 0.0.0.0

### Key Features
- CORS middleware configured for all origins
- Startup/shutdown event handlers
- OpenAPI schema customization
- Three main routers included:
  1. Main routes (knowledge graph operations)
  2. Hints routes (column metadata)
  3. Schedule routes (KPI scheduling)

### Server Configuration
```python
uvicorn.run(
    "kg_builder.main:app",
    host="0.0.0.0",
    port=8000,
    reload=True,
    log_level="DEBUG",
    use_colors=True
)
```

---

## 3. COMPLETE ROUTE STRUCTURE

### A. Main Routes - `/v1` prefix
**File:** `/Users/rchirrareddy/Desktop/dq-poc/kg_builder/routes.py`
**Total Endpoints:** 50+

**Categories:**
- Health & Schema Management (3 endpoints)
- Knowledge Graph Operations (8 endpoints)
- Table Aliases (5 endpoints)
- LLM Features (3 endpoints)
- Natural Language Queries (4 endpoints)
- Reconciliation (5 endpoints)
- KPI Management (9 endpoints)
- Landing Database KPI (6 endpoints)

**Key Endpoints:**
```
POST   /kg/generate                     Generate knowledge graph
POST   /kg/{kg_name}/query             Query KG
POST   /nl/query                       Execute NL query
POST   /kpi                             Create KPI
POST   /kpi/{kpi_id}/execute           Execute KPI
POST   /landing-kpi/{id}/execute       Execute Landing KPI
POST   /reconciliation/execute         Execute reconciliation
GET    /health                         Health check
```

### B. Hints Routes - `/v1/hints` prefix
**File:** `/Users/rchirrareddy/Desktop/dq-poc/kg_builder/routes_hints.py`
**Total Endpoints:** 12+

**Categories:**
- CRUD Operations (8 endpoints)
- Search & Discovery (3 endpoints)
- Versioning & Export (3 endpoints)

### C. Schedule Routes - `/v1/` prefix
**File:** `/Users/rchirrareddy/Desktop/dq-poc/kg_builder/routers/kpi_schedule_router.py`
**Total Endpoints:** 15+

**Categories:**
- Schedule Management (6 endpoints)
- Execution Tracking (5 endpoints)
- Manual Triggers & Airflow (3 endpoints)

---

## 4. LOGGING CONFIGURATION

### Configuration File
**Location:** `/Users/rchirrareddy/Desktop/dq-poc/kg_builder/logging_config.py`

### Log Files Directory
**Location:** `/Users/rchirrareddy/Desktop/dq-poc/logs/`

### Current Log Files
- `app.log` - Application logs (console + file)
- `error.log` - Error-level logs only
- `access.log` - HTTP access logs
- `sql.log` - SQL query logs (6 specialized services)

### Logger Configuration
```python
Root Logger → console, file_app, file_error
uvicorn → console, file_app
uvicorn.access → console_access, file_access
kg_builder.services.* → console, file_app (or sql.log for 6 services)
```

### Logging Features
- Daily rotation at midnight
- 30-day backup retention
- UTF-8 encoding
- Detailed formatting with file:line numbers
- Separate SQL log for query tracking
- Console output for real-time monitoring

---

## 5. SERVICE LAYER (41 Files)

### Directory
**Location:** `/Users/rchirrareddy/Desktop/dq-poc/kg_builder/services/`

### Core Services (4 files)
1. `llm_service.py` - OpenAI API integration
2. `schema_parser.py` - JSON schema parsing
3. `falkordb_backend.py` - FalkorDB graph DB
4. `graphiti_backend.py` - Graphiti in-memory DB

### Knowledge Graph (2 files)
5. `kg_relationship_service.py` - Relationship management
6. `nl_relationship_parser.py` - NL relationship extraction

### Natural Language Processing (5 files)
7. `nl_query_parser.py` → `/logs/sql.log`
8. `nl_query_executor.py` → `/logs/sql.log`
9. `nl_query_classifier.py`
10. `nl_sql_generator.py` → `/logs/sql.log`
11. `llm_sql_generator.py`
12. `multi_schema_llm_service.py`

### Reconciliation (3 files)
13. `reconciliation_service.py`
14. `reconciliation_executor.py`
15. `landing_reconciliation_executor.py`

### KPI Management (6 files)
16. `kpi_service.py`
17. `kpi_executor.py` → `/logs/sql.log`
18. `kpi_file_service.py`
19. `kpi_schedule_service.py`
20. `kpi_analytics_service.py`
21. `kpi_performance_monitor.py`

### Landing Database (6 files)
22. `landing_db_connector.py` → `/logs/sql.log`
23. `landing_kpi_service.py`
24. `landing_kpi_service_jdbc.py`
25. `landing_kpi_service_mssql.py`
26. `landing_kpi_executor.py` → `/logs/sql.log` (341 log statements)
27. `landing_query_builder.py` → `/logs/sql.log`

### Rules & Validation (2 files)
28. `rule_validator.py`
29. `rule_storage.py`

### Utilities & Enhancements (12 files)
30. `hint_manager.py`
31. `material_master_enhancer.py`
32. `sql_ops_planner_enhancer.py`
33. `enhanced_sql_generator.py`
34. `staging_manager.py`
35. `schedule_execution_service.py`
36. `airflow_dag_generator.py`
37. `data_extractor.py`
38. `mongodb_storage.py`
39. `table_name_mapper.py`
40. `notification_service.py`
41. `kpi_performance_monitor.py`

### Logging Statistics
- **Total Logging Statements:** 1,749+
- **Files with Logger:** 41/41 (100%)
- **Average per file:** 42+ statements
- **Top File:** landing_kpi_executor.py (341 statements)

---

## 6. PROJECT STRUCTURE

```
/Users/rchirrareddy/Desktop/dq-poc/
│
├── kg_builder/                          # Main Python package
│   ├── __init__.py
│   ├── main.py                          # FastAPI entry point
│   ├── config.py                        # Configuration & environment vars
│   ├── models.py                        # Pydantic data models
│   ├── logging_config.py                # Logging setup
│   ├── routes.py                        # Main API routes (50+ endpoints)
│   ├── routes_hints.py                  # Hints management routes
│   ├── routes_kpi_analytics.py          # KPI analytics routes
│   │
│   ├── routers/
│   │   └── kpi_schedule_router.py       # KPI scheduling routes
│   │
│   └── services/                        # Business logic (41 files)
│       ├── llm_service.py
│       ├── schema_parser.py
│       ├── falkordb_backend.py
│       ├── graphiti_backend.py
│       ├── kpi_executor.py
│       ├── landing_kpi_executor.py
│       ├── kpi_schedule_service.py
│       ├── nl_query_parser.py
│       ├── nl_query_executor.py
│       ├── nl_sql_generator.py
│       ├── reconciliation_executor.py
│       ├── landing_db_connector.py
│       ├── landing_kpi_service_jdbc.py
│       ├── kpi_file_service.py
│       ├── hint_manager.py
│       ├── mongodb_storage.py
│       └── ... (26 more service files)
│
├── logs/                                # Log files directory
│   ├── app.log                          # Application logs
│   ├── error.log                        # Error logs
│   ├── access.log                       # HTTP access logs
│   └── sql.log                          # SQL query logs
│
├── schemas/                             # JSON schema definitions
│   ├── orderMgmt-catalog.json
│   ├── qinspect-designcode.json
│   └── hints/
│
├── data/                                # Data storage
│   ├── kpi/                             # KPI definitions & results
│   ├── reconciliation_landing/
│   ├── graphiti_storage/
│   └── landing_kpi.db                   # SQLite for landing KPI
│
├── scripts/                             # Utility scripts (30+ files)
│   ├── init_landing_db.py
│   ├── init_landing_kpi_db.py
│   ├── test_mssql_connection.py
│   ├── standalone_sql_preview.py
│   └── ... (more scripts)
│
├── tests/                               # Test files
│
├── web-app/                             # React frontend
│   ├── src/
│   │   ├── components/                  # React components
│   │   ├── pages/                       # Page components
│   │   ├── services/
│   │   │   └── api.js                   # API client
│   │   └── App.js
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── .env.example                         # Environment variables template
├── .gitignore
├── docker-compose.yml                   # Docker compose configuration
├── Dockerfile                           # Docker build config
├── requirements.txt                     # Python dependencies
└── README.md
```

---

## 7. CONFIGURATION & ENVIRONMENT

### Configuration File
**Location:** `/Users/rchirrareddy/Desktop/dq-poc/kg_builder/config.py`

### Database Configurations
```python
# Graph Databases
FALKORDB_HOST = "localhost"
FALKORDB_PORT = 6379

# Source Database (Oracle/SQL Server/MySQL/PostgreSQL)
SOURCE_DB_TYPE = "oracle"
SOURCE_DB_HOST = "localhost"
SOURCE_DB_PORT = 1521

# KPI Database (SQL Server)
KPI_DB_TYPE = "sqlserver"
KPI_DB_HOST = "localhost"
KPI_DB_PORT = 1433

# Landing Database
LANDING_DB_TYPE = "mysql"
LANDING_DB_HOST = "localhost"
LANDING_DB_PORT = 3306

# MongoDB (Reconciliation Results)
MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
```

### Logging Level
```python
LOG_LEVEL = "DEBUG"  # Default, changeable via env var
```

### API Settings
```python
API_TITLE = "Knowledge Graph Builder"
API_VERSION = "1.0.0"
CORS_ORIGINS = ["*"]
```

---

## 8. EXISTING LOG FILES

### Log Directory Contents
```
/Users/rchirrareddy/Desktop/dq-poc/logs/
├── app.log                              # 55 KB (current)
├── error.log                            # 4.8 KB (current)
├── access.log                           # 20 KB (current)
├── sql.log                              # 19 KB (current)
└── [daily rotated files from Oct 28]
```

### Log Retention
- Daily rotation: YES
- Backup count: 30 days
- Encoding: UTF-8

---

## 9. RUNNING THE APPLICATION

### Start Server
```bash
cd /Users/rchirrareddy/Desktop/dq-poc
python -m kg_builder.main
```

### Access Points
- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

### Docker
```bash
docker-compose up --build
```

---

## 10. KEY FILES QUICK REFERENCE

### Critical Configuration Files
- **Main App:** `/kg_builder/main.py`
- **Logging Config:** `/kg_builder/logging_config.py`
- **Environment Config:** `/kg_builder/config.py`
- **API Routes:** `/kg_builder/routes.py`
- **Hints Routes:** `/kg_builder/routes_hints.py`
- **Schedule Routes:** `/kg_builder/routers/kpi_schedule_router.py`

### Top Service Files (by logging volume)
1. `/kg_builder/services/landing_kpi_executor.py` (341 statements)
2. `/kg_builder/services/kpi_file_service.py` (165 statements)
3. `/kg_builder/services/kpi_executor.py` (125 statements)
4. `/kg_builder/services/landing_kpi_service_jdbc.py` (116 statements)
5. `/kg_builder/services/nl_query_parser.py` (117 statements)

### Log Files
- **App Log:** `/logs/app.log`
- **Error Log:** `/logs/error.log`
- **SQL Log:** `/logs/sql.log`
- **Access Log:** `/logs/access.log`

---

## 11. LOGGING HIGHLIGHTS

### Current Setup
- Console output via stderr: ACTIVE
- File output with rotation: ACTIVE
- SQL-specific logging: ACTIVE (6 services)
- Error tracking: ACTIVE
- Access logging: ACTIVE

### Real-Time Monitoring
1. **Console:** Run uvicorn directly to see logs in terminal
2. **File Monitoring:** `tail -f logs/app.log`
3. **SQL Debugging:** `tail -f logs/sql.log`
4. **Error Tracking:** `tail -f logs/error.log`

### All 41 Services Already Have Logging
- Logger initialization: PRESENT in all files
- Logging levels: INFO, DEBUG, ERROR, WARNING
- Total statements: 1,749+

---

## 12. SUMMARY

This is a comprehensive, production-ready **Knowledge Graph Builder & KPI Analytics Platform** featuring:

1. **FastAPI REST API** with 70+ endpoints
2. **Graph Database Support** (FalkorDB, Graphiti)
3. **Natural Language Processing** (NL to SQL)
4. **Advanced Logging** (console + file + rotation)
5. **KPI Engine** (definition, execution, scheduling)
6. **Multi-Database Support** (Oracle, SQL Server, MySQL, PostgreSQL, MongoDB)
7. **Reconciliation Engine** for data validation
8. **Airflow Integration** for task scheduling
9. **Cloud-Ready** deployment (Docker, OpenShift)

All services properly initialized with comprehensive logging for visibility and debugging.

