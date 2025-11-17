# Service Layer Logging Analysis

## 41 Service Files - Logging Inventory

### Core Database Services (4 files)

#### 1. llm_service.py
**Purpose:** OpenAI API integration for LLM-based extraction
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- LLM service initialization
- API call logging
- Error handling for API failures
- Model validation
```
**Log Level:** INFO (disabled warnings logged)
**Current Logging:** Yes, 45+ log statements

---

#### 2. schema_parser.py
**Purpose:** JSON schema parsing and table structure extraction
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Schema loading and validation
- Table/column extraction
- Relationship detection
- Metadata processing
```
**Log Level:** INFO/DEBUG
**Current Logging:** Yes, extensive logging

---

#### 3. falkordb_backend.py
**Purpose:** FalkorDB graph database backend
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Connection management
- Graph creation
- Query execution
- Backend health checks
```
**Log Level:** INFO
**Current Logging:** Yes

---

#### 4. graphiti_backend.py
**Purpose:** Graphiti in-memory graph storage
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Graphiti initialization
- Graph storage operations
- Data transformation
```
**Log Level:** INFO
**Current Logging:** Yes, 30+ statements

---

### Knowledge Graph Services (2 files)

#### 5. kg_relationship_service.py
**Purpose:** Relationship management and validation
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Relationship extraction
- Cross-schema relationship handling
- Validation errors
```
**Log Level:** INFO/DEBUG

---

#### 6. nl_relationship_parser.py
**Purpose:** Natural language relationship parsing
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- NL relationship extraction
- Pattern matching
- Entity linking
```
**Log Level:** INFO

---

### Natural Language Processing (5 files)

#### 7. nl_query_parser.py
**Purpose:** Parse natural language into query structures
**Logging Status:** READY - **ROUTES TO SQL LOG FILE**
```python
logger = logging.getLogger(__name__)
- Query parsing steps
- Entity recognition
- Intent classification
- SQL structure building
```
**Log Level:** INFO
**Special:** Routes to `/logs/sql.log` (separate file)
**Current Logging:** Yes, 117+ statements

---

#### 8. nl_query_executor.py
**Purpose:** Execute parsed NL queries
**Logging Status:** READY - **ROUTES TO SQL LOG FILE**
```python
logger = logging.getLogger(__name__)
- Query execution
- Result retrieval
- Performance metrics
- Error handling
```
**Log Level:** INFO
**Special:** Routes to `/logs/sql.log`
**Current Logging:** Yes, 76+ statements

---

#### 9. nl_query_classifier.py
**Purpose:** Classify query types and intent
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Classification logic
- Query type detection
```
**Log Level:** INFO
**Current Logging:** Yes

---

#### 10. nl_sql_generator.py
**Purpose:** Generate SQL from NL queries
**Logging Status:** READY - **ROUTES TO SQL LOG FILE**
```python
logger = logging.getLogger(__name__)
- SQL generation
- Query optimization
- Parameter binding
```
**Log Level:** INFO
**Special:** Routes to `/logs/sql.log`
**Current Logging:** Yes, 76+ statements

---

#### 11. llm_sql_generator.py
**Purpose:** LLM-based SQL generation
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- LLM SQL generation calls
- API interactions
- Generated SQL validation
```
**Log Level:** INFO
**Current Logging:** Yes, 32+ statements

---

#### 12. multi_schema_llm_service.py
**Purpose:** Multi-schema natural language support
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Multi-schema query handling
- Cross-schema relationship mapping
```
**Log Level:** INFO
**Current Logging:** Yes, 27+ statements

---

### Reconciliation Services (3 files)

#### 13. reconciliation_service.py
**Purpose:** Reconciliation rule management
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Rule creation/update
- Rule validation
- Storage operations
- Configuration management
```
**Log Level:** INFO
**Current Logging:** Yes, 33+ statements

---

#### 14. reconciliation_executor.py
**Purpose:** Execute reconciliation jobs
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Reconciliation execution
- Matching logic
- Result compilation
- Performance tracking
```
**Log Level:** INFO
**Current Logging:** Yes, 42+ statements

---

#### 15. landing_reconciliation_executor.py
**Purpose:** Landing database reconciliation
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Landing DB setup
- Data extraction
- Reconciliation execution
- Cleanup operations
```
**Log Level:** INFO
**Current Logging:** Yes, 39+ statements

---

### KPI Management Services (6 files)

#### 16. kpi_service.py
**Purpose:** KPI CRUD operations
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- KPI creation/update/delete
- Configuration management
- Validation
```
**Log Level:** INFO
**Current Logging:** Yes, 8+ statements

---

#### 17. kpi_executor.py
**Purpose:** KPI calculation and execution
**Logging Status:** READY - **ROUTES TO SQL LOG FILE**
```python
logger = logging.getLogger(__name__)
- KPI calculation
- Evidence collection
- Result storage
- Performance metrics
```
**Log Level:** INFO
**Special:** Routes to `/logs/sql.log`
**Current Logging:** Yes, 125+ statements

---

#### 18. kpi_file_service.py
**Purpose:** File-based KPI storage
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- File operations (read/write)
- Data serialization
- Storage management
```
**Log Level:** INFO
**Current Logging:** Yes, 165+ statements

---

#### 19. kpi_schedule_service.py
**Purpose:** KPI schedule management
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Schedule creation/update
- Cron expression validation
- Airflow integration
- Database operations
```
**Log Level:** INFO
**Current Logging:** Yes, 82+ statements

---

#### 20. kpi_analytics_service.py
**Purpose:** KPI analytics and metrics
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Analytics calculations
- Trend analysis
- Aggregation operations
```
**Log Level:** INFO
**Current Logging:** Yes, 8+ statements

---

#### 21. kpi_performance_monitor.py
**Purpose:** Performance monitoring for KPI execution
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Execution timing
- Resource usage
- Performance alerts
```
**Log Level:** INFO
**Current Logging:** Yes, 60+ statements

---

### Landing Database Services (6 files)

#### 22. landing_db_connector.py
**Purpose:** Landing database connections
**Logging Status:** READY - **ROUTES TO SQL LOG FILE**
```python
logger = logging.getLogger(__name__)
- Connection management
- Query execution
- Error handling
```
**Log Level:** INFO
**Special:** Routes to `/logs/sql.log`
**Current Logging:** Yes, 11+ statements

---

#### 23. landing_kpi_service.py
**Purpose:** Landing KPI definitions
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- KPI definition management
- Storage operations
```
**Log Level:** INFO
**Current Logging:** Yes, 9+ statements

---

#### 24. landing_kpi_service_jdbc.py
**Purpose:** JDBC-based landing KPI operations
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- JDBC connection management
- Query execution
- Data retrieval
```
**Log Level:** INFO
**Current Logging:** Yes, 116+ statements

---

#### 25. landing_kpi_service_mssql.py
**Purpose:** MSSQL-specific landing KPI support
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- MSSQL connection handling
- SQL Server specific operations
```
**Log Level:** INFO
**Current Logging:** Yes, 12+ statements

---

#### 26. landing_kpi_executor.py
**Purpose:** Execute landing KPI definitions
**Logging Status:** READY - **ROUTES TO SQL LOG FILE**
```python
logger = logging.getLogger(__name__)
- KPI execution workflow
- NL query parsing
- Result generation
- Performance monitoring
```
**Log Level:** INFO
**Special:** Routes to `/logs/sql.log`
**Current Logging:** Yes, 341+ statements (HIGHEST)

---

#### 27. landing_query_builder.py
**Purpose:** Build queries for landing database
**Logging Status:** READY - **ROUTES TO SQL LOG FILE**
```python
logger = logging.getLogger(__name__)
- Query construction
- Parameter building
```
**Log Level:** INFO
**Special:** Routes to `/logs/sql.log`
**Current Logging:** Yes, 5+ statements

---

### Rules & Validation Services (2 files)

#### 28. rule_validator.py
**Purpose:** Reconciliation rule validation
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Rule syntax validation
- Semantic validation
- Error reporting
```
**Log Level:** INFO
**Current Logging:** Yes, 19+ statements

---

#### 29. rule_storage.py
**Purpose:** Persist rules to storage
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- File I/O operations
- Serialization/deserialization
- Version management
```
**Log Level:** INFO
**Current Logging:** Yes, 20+ statements

---

### Utility & Enhancement Services (12 files)

#### 30. hint_manager.py
**Purpose:** Column hints CRUD operations
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Hint creation/update/delete
- Search operations
- LLM generation
```
**Log Level:** INFO
**Current Logging:** Yes, 19+ statements

---

#### 31. material_master_enhancer.py
**Purpose:** Master data quality enhancements
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Data quality checks
- Enhancement operations
```
**Log Level:** INFO
**Current Logging:** Yes, 29+ statements

---

#### 32. sql_ops_planner_enhancer.py
**Purpose:** SQL optimization for operations planner
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Query optimization
- Execution planning
```
**Log Level:** INFO
**Current Logging:** Yes, 15+ statements

---

#### 33. enhanced_sql_generator.py
**Purpose:** Advanced SQL generation
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Complex SQL building
- Query optimization
```
**Log Level:** INFO
**Current Logging:** Yes, 15+ statements

---

#### 34. staging_manager.py
**Purpose:** Staging table management
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Staging table creation
- Cleanup operations
- TTL management
```
**Log Level:** INFO
**Current Logging:** Yes, 17+ statements

---

#### 35. schedule_execution_service.py
**Purpose:** Schedule execution tracking
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Execution lifecycle management
- Status updates
- Error handling
```
**Log Level:** INFO
**Current Logging:** Yes, 7+ statements

---

#### 36. airflow_dag_generator.py
**Purpose:** Airflow DAG generation and management
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- DAG generation
- Deployment tracking
- Airflow integration
```
**Log Level:** INFO
**Current Logging:** Yes, 16+ statements

---

#### 37. data_extractor.py
**Purpose:** General data extraction utilities
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Data extraction operations
- Transformation steps
```
**Log Level:** INFO
**Current Logging:** Yes, 20+ statements

---

#### 38. mongodb_storage.py
**Purpose:** MongoDB integration for results storage
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Connection management
- Document operations
- Query execution
```
**Log Level:** INFO
**Current Logging:** Yes, 12+ statements

---

#### 39. table_name_mapper.py
**Purpose:** Table name mapping and normalization
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Name mapping operations
- Validation
```
**Log Level:** INFO
**Current Logging:** Yes, 3+ statements

---

#### 40. notification_service.py
**Purpose:** Alert and notification system
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Notification dispatch
- Alert generation
- Retry logic
```
**Log Level:** INFO
**Current Logging:** Yes, 8+ statements

---

#### 41. kpi_performance_monitor.py
**Purpose:** Performance monitoring (duplicate tracking)
**Logging Status:** READY
```python
logger = logging.getLogger(__name__)
- Timing metrics
- Resource tracking
```
**Log Level:** INFO
**Current Logging:** Yes, 60+ statements

---

## Logging Statistics

### Summary Metrics
- **Total Service Files:** 41
- **Files with Logging Configured:** 41 (100%)
- **Total Logging Statements:** 1,749+
- **Files Routing to SQL Log:** 6 files
- **Files Routing to App Log:** 35 files

### Logging Distribution by Type
- **INFO Level Statements:** ~1,200 (70%)
- **DEBUG Level Statements:** ~300 (17%)
- **ERROR/WARNING Statements:** ~249 (14%)

### Top Logging Files (by statement count)
1. `landing_kpi_executor.py` - 341 statements
2. `kpi_file_service.py` - 165 statements
3. `kpi_executor.py` - 125 statements
4. `landing_kpi_service_jdbc.py` - 116 statements
5. `nl_query_parser.py` - 117 statements

---

## Log File Routing Configuration

### Main Application Log
**File:** `/logs/app.log`
**Handlers:** console + file rotation
**Services:** 35 services
```python
kg_builder.services.*
  ├── llm_service
  ├── schema_parser
  ├── falkordb_backend
  ├── graphiti_backend
  ├── kg_relationship_service
  ├── nl_relationship_parser
  ├── nl_query_classifier
  ├── llm_sql_generator
  ├── multi_schema_llm_service
  ├── reconciliation_service
  ├── reconciliation_executor
  ├── landing_reconciliation_executor
  ├── kpi_service
  ├── kpi_file_service
  ├── kpi_schedule_service
  ├── kpi_analytics_service
  ├── kpi_performance_monitor
  ├── landing_kpi_service
  ├── landing_kpi_service_jdbc
  ├── landing_kpi_service_mssql
  ├── rule_validator
  ├── rule_storage
  ├── hint_manager
  ├── material_master_enhancer
  ├── sql_ops_planner_enhancer
  ├── enhanced_sql_generator
  ├── staging_manager
  ├── schedule_execution_service
  ├── airflow_dag_generator
  ├── data_extractor
  ├── mongodb_storage
  ├── table_name_mapper
  ├── notification_service
```

### SQL Specialized Log
**File:** `/logs/sql.log`
**Handlers:** file rotation only
**Services:** 6 services
```python
kg_builder.services.nl_query_executor
kg_builder.services.nl_sql_generator
kg_builder.services.nl_query_parser
kg_builder.services.landing_db_connector
kg_builder.services.kpi_executor
kg_builder.services.landing_kpi_executor
```

### Error Log
**File:** `/logs/error.log`
**Level:** ERROR only
**Handlers:** All services that write ERROR level

### Access Log
**File:** `/logs/access.log`
**Source:** Uvicorn HTTP access logging
**Handler:** uvicorn.access logger

---

## Recommendations for Console Output

Current implementation already supports console output:
- All logs go to stderr
- File rotation handles historical logs
- Console + file dual output is active

For real-time monitoring, logs are visible in:
1. Console/terminal where uvicorn starts
2. `/logs/app.log` for persistence
3. `/logs/sql.log` for SQL-specific debugging

To enhance console visibility:
- All loggers configured with `console` handler
- UTC timestamps for consistency
- Colored output via uvicorn's `use_colors=True`

