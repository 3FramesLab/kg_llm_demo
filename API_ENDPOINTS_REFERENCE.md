# DQ-POC API Endpoints Reference

## Complete Endpoint Inventory

### A. MAIN ROUTES (`/v1` prefix) - 50+ Endpoints

#### Health & Diagnostics
```
GET  /health                    Health status of FalkorDB & Graphiti
GET  /                          (Root) API information
```

#### Schema Management
```
GET  /schemas                   List all available schema files
GET  /schemas/{schema_name}/tables          Get tables from a schema
POST /schemas/{schema_name}/parse           Parse and validate schema
```

#### Knowledge Graph Operations
```
POST /kg/generate               Generate KG from schemas with LLM support
POST /kg/{kg_name}/query        Execute graph query
GET  /kg/{kg_name}/entities     Get all entities in graph
GET  /kg/{kg_name}/relationships            Get all relationships
GET  /kg/{kg_name}/metadata     Get KG metadata
GET  /kg/{kg_name}/export       Export graph in various formats
GET  /kg                        List all knowledge graphs
DELETE /kg/{kg_name}            Delete knowledge graph
```

#### Table Aliases Management
```
GET  /table-aliases             Get all table aliases across KGs
GET  /kg/{kg_name}/table-aliases           Get KG-specific aliases
POST /kg/{kg_name}/table-aliases           Create table alias
PUT  /kg/{kg_name}/table-aliases/{table}   Update table alias
DELETE /kg/{kg_name}/table-aliases/{table} Delete table alias
```

#### LLM Features
```
POST /llm/extract/{schema_name} Extract entities/relationships using LLM
POST /llm/analyze/{schema_name} Analyze schema with LLM for insights
GET  /llm/status                Check LLM service availability
```

#### Natural Language Query Execution
```
POST /nl/query                  Execute natural language query
POST /nl/parse                  Parse NL into query structure
POST /nl/execute                Execute NL query with reconciliation
POST /nl/relationships          Extract relationships from natural language
```

#### Reconciliation
```
POST /reconciliation/execute    Execute reconciliation between DBs
GET  /reconciliation/results/{id}           Get reconciliation results
GET  /reconciliation/progress/{id}          Get execution progress
POST /reconciliation/rules      Save/update reconciliation rules
GET  /reconciliation/rules      Retrieve saved rules
```

#### KPI Management
```
POST /kpi                       Create new KPI definition
GET  /kpi/{kpi_id}              Get KPI details
PUT  /kpi/{kpi_id}              Update KPI definition
DELETE /kpi/{kpi_id}            Delete KPI
GET  /kpi                       List all KPIs
POST /kpi/{kpi_id}/execute     Execute KPI calculation
GET  /kpi/{kpi_id}/results     Get KPI execution results
GET  /kpi/results/{result_id}   Get specific KPI result
POST /kpi/batch-execute        Execute multiple KPIs
```

#### Landing Database KPI
```
POST /landing-kpi               Create landing DB KPI
GET  /landing-kpi/{kpi_id}      Get landing KPI details
PUT  /landing-kpi/{kpi_id}      Update landing KPI
DELETE /landing-kpi/{kpi_id}    Delete landing KPI
GET  /landing-kpi               List all landing KPIs
POST /landing-kpi/{kpi_id}/execute         Execute landing KPI
```

---

### B. HINTS ROUTES (`/v1/hints` prefix) - 12+ Endpoints

#### CRUD Operations
```
GET  /                          Get all column/table hints
GET  /statistics                Get hints statistics
GET  /table/{table_name}        Get hints for specific table
GET  /column/{table_name}/{column}         Get hints for specific column
POST /table                     Update/create table hints
POST /column                    Update/create column hints
PATCH /column/{table}/{column}/{field}     Update specific hint field
DELETE /hints                   Delete hints
```

#### Search & Discovery
```
POST /search                    Search hints with filters & pagination
POST /generate                  Generate hints using LLM for single table
POST /generate/bulk             Bulk generate hints for multiple tables
```

#### Versioning & Export
```
POST /version                   Create version snapshot of hints
GET  /export                    Export hints to JSON file
POST /import                    Import hints from JSON file
```

---

### C. KPI SCHEDULE ROUTER (`/v1/` prefix) - 15+ Endpoints

#### Schedule Management
```
POST /                          Create new KPI schedule
GET  /{schedule_id}             Get schedule details
GET  /kpi/{kpi_id}              Get all schedules for a KPI
PUT  /{schedule_id}             Update schedule configuration
DELETE /{schedule_id}           Delete schedule
POST /{schedule_id}/toggle      Toggle schedule active/inactive
```

#### Execution Tracking
```
POST /executions/               Create execution record
PUT  /executions/{execution_id} Update execution status
GET  /executions/{execution_id} Get execution details
GET  /{schedule_id}/executions  Get all executions for schedule
GET  /{schedule_id}/statistics  Get execution statistics
```

#### Manual Triggers & Airflow
```
POST /{schedule_id}/trigger     Manually trigger schedule
GET  /{schedule_id}/airflow-status         Check Airflow DAG status
POST /sync-all-to-airflow       Sync all schedules to Airflow
```

---

## API Response Patterns

### Success Response Format
```json
{
  "success": true,
  "data": { /* specific response data */ },
  "message": "Operation completed successfully"
}
```

### Error Response Format
```json
{
  "detail": "Error message explaining what failed",
  "status_code": 400|404|500
}
```

### KPI Execution Response
```json
{
  "execution_id": "unique-uuid",
  "kpi_id": 123,
  "kpi_name": "Revenue KPI",
  "status": "completed|running|failed",
  "value": 1500000,
  "timestamp": "2024-11-10T10:30:00Z",
  "details": { /* execution details */ }
}
```

---

## Authentication & Security

Current Setup:
- CORS: All origins allowed (`["*"]`)
- API Key authentication: Not yet implemented
- Rate limiting: Not yet implemented
- HTTPS: Should be enabled in production

---

## Common Query Parameters

- `limit`: Pagination limit (default varies by endpoint)
- `offset`: Pagination offset
- `sort_by`: Field to sort by
- `order`: ASC or DESC
- `backend`: Graph backend selection (falkordb|graphiti)
- `schema`: Schema name/identifier
- `kg_name`: Knowledge graph identifier

---

## Request Body Examples

### Generate Knowledge Graph
```json
{
  "schema_names": ["schema1", "schema2"],
  "kg_name": "my_kg",
  "use_llm_enhancement": true,
  "backends": ["falkordb", "graphiti"],
  "relationship_pairs": [
    {
      "source_table": "orders",
      "target_table": "customers",
      "source_column": "customer_id",
      "target_column": "id"
    }
  ],
  "excluded_fields": ["internal_id", "temp_field"]
}
```

### Execute Natural Language Query
```json
{
  "query": "Get total revenue by product category",
  "schema_name": "sales_schema",
  "kg_name": "sales_kg",
  "timeout": 30,
  "cache_results": true
}
```

### Create KPI
```json
{
  "name": "Monthly Revenue",
  "description": "Total monthly revenue",
  "kpi_type": "metric",
  "sql": "SELECT SUM(amount) FROM orders WHERE month = CURRENT_MONTH",
  "thresholds": {
    "warning": 900000,
    "critical": 800000
  }
}
```

### Create Schedule
```json
{
  "kpi_id": 1,
  "schedule_name": "Daily Report",
  "schedule_type": "daily",
  "timezone": "UTC",
  "start_date": "2024-11-01T00:00:00",
  "schedule_config": {
    "retry_count": 3,
    "retry_delay": 300,
    "timeout": 3600,
    "email_notifications": ["admin@example.com"]
  }
}
```

---

## Logging for API Calls

All API endpoints automatically log:
- Request method and path
- Request processing time
- Success/error status
- Relevant IDs (KPI, schedule, execution)
- Error stack traces (if applicable)

Log Files:
- `/logs/app.log` - General application logs (includes HTTP requests)
- `/logs/error.log` - Error logs only
- `/logs/access.log` - HTTP access logs
- `/logs/sql.log` - SQL queries and NL executions

---

## API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

