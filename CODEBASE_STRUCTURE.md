# DQ-POC Codebase Structure & Logging Analysis

## 1. MAIN API ENTRY POINT

**Framework:** FastAPI
**Main File:** `/Users/rchirrareddy/Desktop/dq-poc/kg_builder/main.py`
**Entry Point:** `app = FastAPI()` (lines 45-52)
**Server:** Uvicorn (running on 0.0.0.0:8000)

### Key Features:
- **CORS Middleware:** Configured with `*` origins, credentials, methods, and headers
- **Root Endpoint:** `GET /` - Returns API information with docs links
- **Startup Events:** Initializes FalkorDB and Graphiti backends
- **OpenAPI Schema:** Customizable schema at `/docs` and `/redoc`

---

## 2. ROUTE FILES & API ENDPOINTS

### A. Main Routes: `/kg_builder/routes.py` (Core Knowledge Graph Operations)

**Router Prefix:** `/v1`
**Total Endpoints:** 50+ endpoints

#### Key Endpoint Groups:

**Health & Schema Management:**
- `GET /health` - Health check (FalkorDB, Graphiti status)
- `GET /schemas` - List available schemas
- `GET /schemas/{schema_name}/tables` - Get tables from schema
- `POST /schemas/{schema_name}/parse` - Parse schema metadata

**Knowledge Graph Operations:**
- `POST /kg/generate` - Generate KG from schemas
- `POST /kg/{kg_name}/query` - Query knowledge graph
- `GET /kg/{kg_name}/entities` - Get KG entities
- `GET /kg/{kg_name}/relationships` - Get KG relationships
- `GET /kg/{kg_name}/metadata` - Get KG metadata
- `GET /kg` - List all graphs
- `DELETE /kg/{kg_name}` - Delete graph

**Table Aliases Management:**
- `GET /table-aliases` - Get all aliases
- `GET /kg/{kg_name}/table-aliases` - Get KG-specific aliases
- `POST /kg/{kg_name}/table-aliases` - Create alias
- `PUT /kg/{kg_name}/table-aliases/{table_name}` - Update alias
- `DELETE /kg/{kg_name}/table-aliases/{table_name}` - Delete alias

**LLM Features:**
- `POST /llm/extract/{schema_name}` - LLM schema extraction
- `POST /llm/analyze/{schema_name}` - LLM analysis
- `GET /llm/status` - LLM service status

**Natural Language & Query Execution:**
- `POST /nl/query` - NL query execution
- `POST /nl/parse` - Parse NL query
- `POST /nl/execute` - Execute NL with reconciliation
- `POST /nl/relationships` - Extract relationships from NL

**Reconciliation:**
- `POST /reconciliation/execute` - Execute reconciliation
- `GET /reconciliation/results/{result_id}` - Get reconciliation results
- `GET /reconciliation/progress/{execution_id}` - Get execution progress
- `POST /reconciliation/rules` - Save reconciliation rules
- `GET /reconciliation/rules` - Get saved rules

**KPI Management:**
- `POST /kpi` - Create KPI
- `GET /kpi/{kpi_id}` - Get KPI details
- `PUT /kpi/{kpi_id}` - Update KPI
- `DELETE /kpi/{kpi_id}` - Delete KPI
- `GET /kpi` - List all KPIs
- `POST /kpi/{kpi_id}/execute` - Execute KPI
- `GET /kpi/{kpi_id}/results` - Get KPI results
- `POST /kpi/batch-execute` - Execute multiple KPIs
- `GET /kpi/results/{result_id}` - Get specific result

**Landing Database KPI:**
- `POST /landing-kpi` - Create landing KPI
- `GET /landing-kpi/{kpi_id}` - Get landing KPI
- `PUT /landing-kpi/{kpi_id}` - Update landing KPI
- `DELETE /landing-kpi/{kpi_id}` - Delete landing KPI
- `GET /landing-kpi` - List landing KPIs
- `POST /landing-kpi/{kpi_id}/execute` - Execute landing KPI

---

### B. Hints Routes: `/kg_builder/routes_hints.py` (Column Hints Management)

**Router Prefix:** `/v1/hints`
**Total Endpoints:** 12+ endpoints

#### Key Endpoints:

**CRUD Operations:**
- `GET /` - Get all hints
- `GET /statistics` - Get hint statistics
- `GET /table/{table_name}` - Get table hints
- `GET /column/{table_name}/{column_name}` - Get column hints
- `POST /table` - Update table hints
- `POST /column` - Update column hints
- `PATCH /column/{table_name}/{column_name}/{field_name}` - Update specific field
- `DELETE /hints` - Delete hints

**Search & Generation:**
- `POST /search` - Search hints with filters
- `POST /generate` - Generate hints with LLM
- `POST /generate/bulk` - Bulk generate hints

**Versioning & Export:**
- `POST /version` - Create version snapshot
- `GET /export` - Export hints to JSON
- `POST /import` - Import hints from JSON

---

### C. KPI Schedule Router: `/kg_builder/routers/kpi_schedule_router.py`

**Router Prefix:** `/v1/`
**Total Endpoints:** 15+ endpoints

#### Key Endpoints:

**Schedule Management:**
- `POST /` - Create KPI schedule
- `GET /{schedule_id}` - Get schedule details
- `GET /kpi/{kpi_id}` - Get all schedules for KPI
- `PUT /{schedule_id}` - Update schedule
- `DELETE /{schedule_id}` - Delete schedule
- `POST /{schedule_id}/toggle` - Toggle schedule active/inactive

**Execution Management:**
- `POST /executions/` - Create execution record
- `PUT /executions/{execution_id}` - Update execution
- `GET /executions/{execution_id}` - Get execution
- `GET /{schedule_id}/executions` - Get schedule executions
- `GET /{schedule_id}/statistics` - Get execution statistics

**Manual Triggers & Airflow Integration:**
- `POST /{schedule_id}/trigger` - Manually trigger execution
- `GET /{schedule_id}/airflow-status` - Get Airflow DAG status
- `POST /sync-all-to-airflow` - Sync all schedules to Airflow

---

## 3. CURRENT LOGGING SETUP

### Configuration File
**Location:** `/Users/rchirrareddy/Desktop/dq-poc/kg_builder/logging_config.py`

### Logging Features:

#### Formatters:
1. **Default**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
2. **Detailed**: `%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s`
3. **Access**: `%(asctime)s - %(levelname)s - %(message)s`

#### Handlers:
1. **Console Handlers** (stderr output):
   - `console` - Default format output
   - `console_access` - Access format output

2. **File Handlers** (TimedRotatingFileHandler - daily rotation):
   - `file_app` - Application logs at `/logs/app.log`
   - `file_error` - Error logs at `/logs/error.log` (ERROR level only)
   - `file_access` - Access logs at `/logs/access.log`
   - `file_sql` - SQL queries at `/logs/sql.log`

#### Log Rotation:
- Rotation: Daily (midnight)
- Backup Count: 30 days retention
- Encoding: UTF-8
- Delay: False (immediate file creation)

#### Logger Configuration:
```
Root Logger: INFO level with handlers: console, file_app, file_error
uvicorn: INFO → console, file_app
uvicorn.error: INFO → console, file_app, file_error
uvicorn.access: INFO → console_access, file_access
kg_builder: INFO → console, file_app, file_error
kg_builder.services: INFO → console, file_app, file_error
```

#### Specialized Loggers:
- `kg_builder.services.nl_query_executor` → file_sql
- `kg_builder.services.nl_sql_generator` → file_sql
- `kg_builder.services.nl_query_parser` → file_sql
- `kg_builder.services.landing_db_connector` → file_sql
- `kg_builder.services.kpi_executor` → file_sql
- `kg_builder.services.landing_kpi_executor` → file_sql

### Log Directory
**Location:** `/Users/rchirrareddy/Desktop/dq-poc/logs/`
**Existing Log Files:**
- `app.log` (55KB current, 814KB from Oct 28)
- `error.log` (4.8KB current, 99KB from Oct 28)
- `access.log` (20KB current)
- `sql.log` (19KB current, 349KB from Oct 28)

---

## 4. SERVICE LAYER FILES THAT NEED LOGGING

### Total Service Files: 41

**Core Services:**
1. `llm_service.py` - OpenAI API integration (LLM extraction)
2. `schema_parser.py` - JSON schema parsing and validation
3. `falkordb_backend.py` - FalkorDB graph database backend
4. `graphiti_backend.py` - Graphiti backend integration

**Knowledge Graph:**
5. `kg_relationship_service.py` - Relationship management
6. `nl_relationship_parser.py` - Natural language relationship extraction

**Natural Language Processing:**
7. `nl_query_parser.py` - Parse NL queries into SQL-like structures
8. `nl_query_executor.py` - Execute NL queries
9. `nl_query_classifier.py` - Classify query types
10. `nl_sql_generator.py` - Generate SQL from NL
11. `llm_sql_generator.py` - LLM-based SQL generation
12. `multi_schema_llm_service.py` - Multi-schema NL support

**Reconciliation:**
13. `reconciliation_service.py` - Reconciliation rule management
14. `reconciliation_executor.py` - Execute reconciliation jobs
15. `landing_reconciliation_executor.py` - Landing DB reconciliation

**KPI Management:**
16. `kpi_service.py` - KPI CRUD operations
17. `kpi_executor.py` - KPI calculation and execution
18. `kpi_file_service.py` - File-based KPI storage
19. `kpi_schedule_service.py` - Schedule management
20. `kpi_analytics_service.py` - KPI analytics and metrics
21. `kpi_performance_monitor.py` - Performance monitoring

**Landing Database:**
22. `landing_db_connector.py` - Landing DB connections
23. `landing_kpi_service.py` - Landing KPI definitions
24. `landing_kpi_service_jdbc.py` - JDBC-based landing KPI
25. `landing_kpi_service_mssql.py` - MSSQL-specific landing KPI
26. `landing_kpi_executor.py` - Execute landing KPIs
27. `landing_query_builder.py` - Build landing DB queries

**Rules & Validation:**
28. `rule_validator.py` - Validate reconciliation rules
29. `rule_storage.py` - Persist rules to storage

**Utilities & Enhancements:**
30. `hint_manager.py` - Column hints CRUD
31. `material_master_enhancer.py` - Master data enhancements
32. `sql_ops_planner_enhancer.py` - SQL optimization
33. `enhanced_sql_generator.py` - Advanced SQL generation
34. `staging_manager.py` - Staging table management
35. `schedule_execution_service.py` - Schedule execution tracking
36. `airflow_dag_generator.py` - Airflow integration
37. `data_extractor.py` - Data extraction utilities
38. `mongodb_storage.py` - MongoDB integration
39. `table_name_mapper.py` - Table name mapping
40. `notification_service.py` - Alert/notification system

**Current Logging Status:**
- All 41 service files already have `logger = logging.getLogger(__name__)` initialized
- Total logging statements: 1,749 log calls found across services
- Most used: `.info()`, `.debug()`, `.error()`, `.warning()`

---

## 5. OVERALL PROJECT STRUCTURE

```
/Users/rchirrareddy/Desktop/dq-poc/
├── kg_builder/                          # Main application package
│   ├── main.py                          # FastAPI entry point
│   ├── config.py                        # Configuration (DB, API, paths)
│   ├── models.py                        # Pydantic data models
│   ├── logging_config.py                # Logging configuration
│   ├── routes.py                        # Main API routes (50+ endpoints)
│   ├── routes_hints.py                  # Hints management routes
│   ├── routes_kpi_analytics.py          # KPI analytics routes
│   ├── routers/
│   │   └── kpi_schedule_router.py       # KPI scheduling routes
│   ├── services/                        # Business logic (41 files)
│   │   ├── llm_service.py
│   │   ├── schema_parser.py
│   │   ├── kpi_executor.py
│   │   ├── landing_kpi_executor.py
│   │   ├── kpi_schedule_service.py
│   │   ├── ... (38 more service files)
│   └── __init__.py
├── logs/                                # Log files directory
│   ├── app.log                          # Application logs
│   ├── error.log                        # Error logs
│   ├── access.log                       # HTTP access logs
│   └── sql.log                          # SQL query logs
├── schemas/                             # JSON schema files
├── data/                                # Data storage directory
├── scripts/                             # Utility scripts
├── tests/                               # Test files
├── web-app/                             # React frontend
│   └── src/
│       ├── components/                  # React components
│       ├── pages/                       # Page components
│       └── services/
│           └── api.js                   # API client
└── requirements.txt                     # Python dependencies
```

---

## 6. DATABASE CONNECTIVITY

### Supported Databases:
1. **FalkorDB** - Graph database (Redis-based)
2. **Graphiti** - In-memory graph storage
3. **Oracle** - Source/Target databases
4. **SQL Server** - KPI analytics database
5. **MySQL** - Landing database
6. **PostgreSQL** - Supported option
7. **MongoDB** - Reconciliation results storage
8. **SQLite** - Local reconciliation results cache

### Connection Configuration:
- All DB configs in `config.py`
- JDBC support for enterprise databases
- Environment variable-based credentials
- Connection pooling for performance

---

## 7. KEY TECHNOLOGIES STACK

**Backend:**
- FastAPI (async web framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)
- OpenAI API (LLM features)
- SQLAlchemy/PyODBC (DB access)
- Croniter (scheduling)

**Frontend:**
- React (UI framework)
- Axios (HTTP client)
- Chart.js (visualization)

**Databases:**
- FalkorDB (graph DB)
- Graphiti (knowledge graph)
- Oracle/SQL Server/MySQL (data)
- MongoDB (results storage)

**Deployment:**
- Docker & Docker Compose
- Airflow (task scheduling)
- OpenShift compatibility

---

## 8. ENVIRONMENT VARIABLES (config.py)

**Key Configs:**
- `LOG_LEVEL`: DEBUG (default)
- `FALKORDB_HOST`, `FALKORDB_PORT`: Graph DB connection
- `OPENAI_API_KEY`, `OPENAI_MODEL`: LLM settings
- `SOURCE_DB_*`, `TARGET_DB_*`: Reconciliation DB configs
- `KPI_DB_*`: KPI analytics DB config
- `LANDING_DB_*`: Landing zone DB config
- `MONGODB_*`: Results storage config
- `CORS_ORIGINS`: `["*"]` for open CORS

---

## SUMMARY

This is a comprehensive **Knowledge Graph Builder & KPI Analytics Platform** built on:

1. **FastAPI** for REST APIs with 70+ endpoints across 3 routers
2. **Advanced logging** with daily rotation, console + file outputs, separate SQL logs
3. **41 service files** handling graph DBs, LLM, reconciliation, KPI, scheduling
4. **Multi-database support** (graph, relational, document DBs)
5. **Natural language processing** for query translation
6. **Scheduling & automation** with Airflow integration
7. **Cloud-ready** deployment (Docker, OpenShift)

All services properly initialized with logging from the start.

