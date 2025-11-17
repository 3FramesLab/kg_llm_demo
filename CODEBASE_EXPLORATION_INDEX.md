# DQ-POC Codebase Exploration - Complete Index

Welcome to the comprehensive exploration of the DQ-POC Knowledge Graph Builder & KPI Analytics Platform codebase.

## Generated Documentation Files

This exploration has generated 4 detailed documentation files:

### 1. **CODEBASE_EXPLORATION.md** (13 KB)
**Complete overview of the entire codebase architecture**

Topics covered:
- Executive summary
- Architecture overview (technology stack)
- Main API entry point (FastAPI)
- Complete route structure (70+ endpoints)
- Logging configuration (4 log files)
- Service layer inventory (41 files)
- Project directory structure
- Database connectivity
- Technology stack
- Environment variables

**Best for:** Getting a complete understanding of the project structure and how everything fits together.

---

### 2. **CODEBASE_STRUCTURE.md** (14 KB)
**Detailed structural analysis with logging insights**

Topics covered:
- Main API entry point (main.py)
- All route files and endpoints:
  - Main routes (/v1) - 50+ endpoints
  - Hints routes (/v1/hints) - 12+ endpoints
  - Schedule routes (/v1/) - 15+ endpoints
- Current logging setup (detailed configuration)
- Log file types and routing:
  - app.log (application logs)
  - error.log (errors only)
  - access.log (HTTP access)
  - sql.log (SQL queries)
- Service layer files (41 files with purpose)
- Overall project structure tree
- Database connectivity options
- Tech stack breakdown
- Configuration details

**Best for:** Understanding the API structure and how logging is currently configured.

---

### 3. **API_ENDPOINTS_REFERENCE.md** (7.9 KB)
**Complete API endpoint inventory with examples**

Topics covered:
- Complete endpoint listing by category:
  - Main routes (50+ endpoints)
  - Hints routes (12+ endpoints)
  - Schedule routes (15+ endpoints)
- API response patterns (success/error/KPI responses)
- Authentication & security configuration
- Common query parameters
- Request body examples:
  - Generate KG
  - Execute NL query
  - Create KPI
  - Create schedule
- Logging for API calls
- API documentation access points

**Best for:** Finding specific endpoints and understanding API contracts.

---

### 4. **SERVICE_LOGGING_ANALYSIS.md** (18 KB)
**Deep dive into all 41 service files and their logging**

Detailed inventory of each service:
- Core Database Services (4 files)
- Knowledge Graph Services (2 files)
- Natural Language Processing (5 files)
- Reconciliation Services (3 files)
- KPI Management Services (6 files)
- Landing Database Services (6 files)
- Rules & Validation Services (2 files)
- Utility & Enhancement Services (12 files)

For each service:
- File purpose
- Logging status (READY)
- What gets logged
- Log level (INFO/DEBUG/etc)
- Special routing (e.g., to sql.log)
- Logging statement count

Special features:
- Logging statistics summary
- Files routing to SQL log (6 services)
- Log file routing configuration
- Recommendations for console output

**Best for:** Understanding what each service does and how to debug it via logging.

---

## Key Information At a Glance

### Main Entry Point
```
/Users/rchirrareddy/Desktop/dq-poc/kg_builder/main.py
FastAPI application running on http://0.0.0.0:8000
```

### Configuration File
```
/Users/rchirrareddy/Desktop/dq-poc/kg_builder/config.py
All database connections, API settings, logging levels
```

### Logging Configuration
```
/Users/rchirrareddy/Desktop/dq-poc/kg_builder/logging_config.py
Defines all handlers, formatters, rotations, log files
```

### Log Files Location
```
/Users/rchirrareddy/Desktop/dq-poc/logs/
├── app.log      (general application logs + console)
├── error.log    (errors only)
├── access.log   (HTTP access)
└── sql.log      (SQL queries and NL executions)
```

### Services Location
```
/Users/rchirrareddy/Desktop/dq-poc/kg_builder/services/
41 service files handling:
- Graph databases (FalkorDB, Graphiti)
- NL to SQL conversion
- KPI definition and execution
- Reconciliation
- Scheduling (Airflow)
- Data validation
- And more...
```

---

## API Endpoints Summary

Total: **77 endpoints** across 3 routers

### By Prefix:
- `/v1` - Main routes (50+ endpoints)
- `/v1/hints` - Hints management (12+ endpoints)
- `/v1/` - Schedule management (15+ endpoints)

### By Category:
- Health & Diagnostics: 2
- Schema Management: 3
- Knowledge Graph: 8
- Table Aliases: 5
- LLM Features: 3
- Natural Language Queries: 4
- Reconciliation: 5
- KPI Management: 9
- Landing Database KPI: 6
- Hints CRUD: 8
- Hints Search/Generation: 3
- Hints Versioning: 3
- Schedule Management: 6
- Execution Tracking: 5
- Manual Triggers/Airflow: 3

---

## Logging System Overview

### Current Setup
- **All 41 services have logging configured:** 100%
- **Total logging statements:** 1,749+
- **Average per service:** 42+ statements
- **Log rotation:** Daily at midnight
- **Retention:** 30 days of backups
- **Console output:** ACTIVE (stderr)
- **File output:** ACTIVE with rotation

### Log Distribution
- INFO level: ~1,200 statements (70%)
- DEBUG level: ~300 statements (17%)
- ERROR/WARNING: ~249 statements (14%)

### Specialized SQL Logging
6 services route to `/logs/sql.log`:
1. nl_query_executor.py
2. nl_sql_generator.py
3. nl_query_parser.py
4. landing_db_connector.py
5. kpi_executor.py
6. landing_kpi_executor.py

---

## Technology Stack

### Backend
- **Framework:** FastAPI (async)
- **Server:** Uvicorn
- **Data Validation:** Pydantic
- **LLM:** OpenAI API

### Databases
- **Graph:** FalkorDB (Redis), Graphiti (in-memory)
- **Data:** Oracle, SQL Server, MySQL, PostgreSQL
- **Results:** MongoDB, SQLite

### Frontend
- **Framework:** React
- **HTTP Client:** Axios
- **Visualization:** Chart.js

### Deployment
- **Containerization:** Docker, Docker Compose
- **Orchestration:** OpenShift
- **Scheduling:** Airflow

---

## Quick Navigation

### Understanding the API
Start with: **API_ENDPOINTS_REFERENCE.md**
Then read: **CODEBASE_EXPLORATION.md** (Section 3)

### Understanding Services
Start with: **SERVICE_LOGGING_ANALYSIS.md**
Then read: **CODEBASE_STRUCTURE.md** (Section 4)

### Understanding Logging
Start with: **CODEBASE_STRUCTURE.md** (Section 3)
Then read: **SERVICE_LOGGING_ANALYSIS.md** (Logging Statistics)

### Understanding Full Architecture
Start with: **CODEBASE_EXPLORATION.md**
Then read: **CODEBASE_STRUCTURE.md**

### Finding Specific Endpoints
Use: **API_ENDPOINTS_REFERENCE.md** (organized by category)

### Finding Which Service Handles What
Use: **SERVICE_LOGGING_ANALYSIS.md** (alphabetical listing)

### Understanding Log Files
Use: **SERVICE_LOGGING_ANALYSIS.md** (Log File Routing Configuration)

---

## File Locations (Absolute Paths)

### Critical Files
- Main App: `/Users/rchirrareddy/Desktop/dq-poc/kg_builder/main.py`
- Config: `/Users/rchirrareddy/Desktop/dq-poc/kg_builder/config.py`
- Logging: `/Users/rchirrareddy/Desktop/dq-poc/kg_builder/logging_config.py`
- Routes: `/Users/rchirrareddy/Desktop/dq-poc/kg_builder/routes.py`
- Hints: `/Users/rchirrareddy/Desktop/dq-poc/kg_builder/routes_hints.py`
- Schedules: `/Users/rchirrareddy/Desktop/dq-poc/kg_builder/routers/kpi_schedule_router.py`

### Services (by importance)
- KPI Executor: `/kg_builder/services/kpi_executor.py` (125 statements)
- KPI File Service: `/kg_builder/services/kpi_file_service.py` (165 statements)
- Landing KPI Executor: `/kg_builder/services/landing_kpi_executor.py` (341 statements)
- LLM Service: `/kg_builder/services/llm_service.py`
- Schema Parser: `/kg_builder/services/schema_parser.py`
- NL Query Parser: `/kg_builder/services/nl_query_parser.py` (117 statements)
- NL Query Executor: `/kg_builder/services/nl_query_executor.py`
- Reconciliation Executor: `/kg_builder/services/reconciliation_executor.py`

### Log Files
- Application: `/Users/rchirrareddy/Desktop/dq-poc/logs/app.log`
- Errors: `/Users/rchirrareddy/Desktop/dq-poc/logs/error.log`
- Access: `/Users/rchirrareddy/Desktop/dq-poc/logs/access.log`
- SQL: `/Users/rchirrareddy/Desktop/dq-poc/logs/sql.log`

---

## Running the Application

### Start Server
```bash
cd /Users/rchirrareddy/Desktop/dq-poc
python -m kg_builder.main
```

### Access API
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI: http://localhost:8000/openapi.json

### Monitor Logs
```bash
# Real-time app logs
tail -f /Users/rchirrareddy/Desktop/dq-poc/logs/app.log

# Real-time SQL logs
tail -f /Users/rchirrareddy/Desktop/dq-poc/logs/sql.log

# Real-time errors
tail -f /Users/rchirrareddy/Desktop/dq-poc/logs/error.log
```

---

## Summary

This exploration provides **complete visibility** into the DQ-POC codebase:

1. **Architecture:** How components fit together
2. **APIs:** What endpoints are available and what they do
3. **Services:** What business logic each service implements
4. **Logging:** How to monitor and debug the application
5. **Configuration:** How to customize for different environments
6. **Deployment:** How to run in production

All documentation is in Markdown format for easy reading and can be opened in any text editor or Markdown viewer.

---

## Document Statistics

| Document | Size | Sections | Topics |
|----------|------|----------|--------|
| CODEBASE_EXPLORATION.md | 13 KB | 12 | Architecture, APIs, Services, Config |
| CODEBASE_STRUCTURE.md | 14 KB | 8 | Routes, Logging, Services, Structure |
| API_ENDPOINTS_REFERENCE.md | 7.9 KB | 8 | Endpoints, Examples, Security |
| SERVICE_LOGGING_ANALYSIS.md | 18 KB | 41+ | Service details, Logging stats |

**Total Documentation:** 52.9 KB covering all aspects of the codebase

---

**Generated:** November 10, 2025
**Platform:** macOS
**Python Project:** DQ-POC Knowledge Graph Builder
**Framework:** FastAPI
**Services:** 41 files
**Endpoints:** 77+ routes
**Logging Statements:** 1,749+

