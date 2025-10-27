# Key Performance Index (KPI) CRUD Management - Implementation Approach

## Document Version
- **Version**: 1.0
- **Date**: 2025-10-27
- **Status**: Design Approved - Ready for Implementation

---

## 1. EXECUTIVE SUMMARY

This document outlines the implementation approach for building a comprehensive KPI CRUD Management system that integrates with the existing Natural Language Query Execution engine. The system will be completely independent from the existing file-based KPI system.

### Key Features
- Full CRUD operations for KPI definitions
- Dynamic execution of KPIs using NL Query engine
- Historical tracking of all KPI executions
- Drill-down capability to view detailed query results
- Modern React-based UI with tabular data presentation

---

## 2. DATABASE DESIGN

### 2.1 Database Selection
**Database**: SQLite
**Location**: `D:\learning\dq-poc\data\landing_kpi.db`
**Rationale**: Lightweight, file-based, consistent with existing project patterns

### 2.2 Schema Design

#### Table: `kpi_definitions`
Stores the master KPI configuration.

```sql
CREATE TABLE kpi_definitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    alias_name VARCHAR(255),
    group_name VARCHAR(255),
    description TEXT,
    nl_definition TEXT NOT NULL,          -- Natural language query definition
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    is_active BOOLEAN DEFAULT 1,
    UNIQUE(name)
);
```

**Field Descriptions**:
- `id`: Auto-incrementing primary key
- `name`: Unique KPI name (e.g., "Product Match Rate")
- `alias_name`: Business-friendly alias (e.g., "PMR")
- `group_name`: Logical grouping (e.g., "Data Quality", "Reconciliation")
- `description`: Detailed description of what KPI measures
- `nl_definition`: Natural language query to execute (e.g., "Show me all products in RBP that are not in OPS")
- `created_at`: Record creation timestamp
- `updated_at`: Last modification timestamp
- `created_by`: User who created the KPI
- `is_active`: Soft delete flag

#### Table: `kpi_execution_results`
Stores execution history and results for each KPI run.

```sql
CREATE TABLE kpi_execution_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kpi_id INTEGER NOT NULL,

    -- Execution Parameters (dynamic inputs)
    kg_name VARCHAR(255) NOT NULL,
    select_schema VARCHAR(255) NOT NULL,
    ruleset_name VARCHAR(255),
    db_type VARCHAR(50) DEFAULT 'mysql',
    limit_records INTEGER DEFAULT 1000,
    use_llm BOOLEAN DEFAULT 1,
    excluded_fields TEXT,                 -- JSON array

    -- Execution Results
    generated_sql TEXT,
    number_of_records INTEGER DEFAULT 0,
    joined_columns TEXT,                  -- JSON array of join column pairs
    sql_query_type VARCHAR(100),          -- COMPARISON_QUERY, DATA_QUERY, etc.
    operation VARCHAR(50),                -- NOT_IN, IN, EQUALS, AGGREGATE, etc.

    -- Additional Metadata
    execution_status VARCHAR(50) DEFAULT 'pending',  -- pending, success, failed
    execution_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_time_ms REAL,
    confidence_score REAL,
    error_message TEXT,

    -- Query Result Data Storage
    result_data TEXT,                     -- JSON array of actual query results
    source_table VARCHAR(255),
    target_table VARCHAR(255),

    FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id) ON DELETE CASCADE
);
```

**Field Descriptions**:
- `kpi_id`: Foreign key to kpi_definitions
- **Execution Parameters** (provided by user at runtime):
  - `kg_name`: Knowledge Graph name to use
  - `select_schema`: Schema(s) to query against
  - `ruleset_name`: Optional ruleset reference
  - `db_type`: Database type (mysql, postgresql, oracle, etc.)
  - `limit_records`: Max records to return
  - `use_llm`: Whether to use LLM for parsing
  - `excluded_fields`: Fields to exclude from joins
- **Execution Results** (from NL Query Execution):
  - `generated_sql`: The actual SQL query generated
  - `number_of_records`: Count of records returned
  - `joined_columns`: JSON array like `[["col1", "col2"], ["col3", "col4"]]`
  - `sql_query_type`: Classification type from NL classifier
  - `operation`: Operation type (NOT_IN, IN, etc.)
- **Additional Metadata**:
  - `execution_status`: Tracks success/failure
  - `execution_timestamp`: When execution occurred
  - `execution_time_ms`: Performance metric
  - `confidence_score`: Parsing confidence (0.0-1.0)
  - `error_message`: Error details if failed
  - `result_data`: Actual query results stored as JSON
  - `source_table`, `target_table`: Tables involved in query

#### Indexes for Performance
```sql
CREATE INDEX idx_kpi_name ON kpi_definitions(name);
CREATE INDEX idx_kpi_active ON kpi_definitions(is_active);
CREATE INDEX idx_execution_kpi_id ON kpi_execution_results(kpi_id);
CREATE INDEX idx_execution_timestamp ON kpi_execution_results(execution_timestamp DESC);
CREATE INDEX idx_execution_status ON kpi_execution_results(execution_status);
```

---

## 3. BACKEND API DESIGN

### 3.1 Technology Stack
- **Framework**: FastAPI (existing)
- **Database**: SQLite with sqlite3 library
- **API Prefix**: `/v1/landing-kpi/`

### 3.2 Service Layer Architecture

#### New Service File: `kg_builder/services/landing_kpi_service.py`

**Responsibilities**:
1. Database connection management
2. CRUD operations for KPI definitions
3. KPI execution orchestration
4. Result storage and retrieval
5. Integration with existing NL query execution service

**Key Methods**:
```python
class LandingKPIService:
    def __init__(self, db_path: str)

    # CRUD Operations
    def create_kpi(self, kpi_data: KPICreateRequest) -> KPIDefinition
    def get_kpi(self, kpi_id: int) -> KPIDefinition
    def list_kpis(self, filters: Dict) -> List[KPIDefinition]
    def update_kpi(self, kpi_id: int, kpi_data: KPIUpdateRequest) -> KPIDefinition
    def delete_kpi(self, kpi_id: int) -> bool

    # Execution Operations
    def execute_kpi(self, kpi_id: int, execution_params: KPIExecutionRequest) -> KPIExecutionResult
    def get_execution_results(self, kpi_id: int, filters: Dict) -> List[KPIExecutionResult]
    def get_execution_result_detail(self, execution_id: int) -> KPIExecutionResult

    # Drill-down Operations
    def get_drilldown_data(self, execution_id: int, pagination: Dict) -> Dict
```

### 3.3 API Endpoints

#### 3.3.1 KPI CRUD Endpoints

```
POST   /v1/landing-kpi/kpis
GET    /v1/landing-kpi/kpis
GET    /v1/landing-kpi/kpis/{kpi_id}
PUT    /v1/landing-kpi/kpis/{kpi_id}
DELETE /v1/landing-kpi/kpis/{kpi_id}
```

#### 3.3.2 KPI Execution Endpoints

```
POST   /v1/landing-kpi/kpis/{kpi_id}/execute
GET    /v1/landing-kpi/kpis/{kpi_id}/executions
GET    /v1/landing-kpi/executions/{execution_id}
```

#### 3.3.3 Drill-down Endpoint

```
GET    /v1/landing-kpi/executions/{execution_id}/drilldown
```

### 3.4 Request/Response Models

#### Models File: `kg_builder/models.py` (additions)

```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# ==================== KPI Definition Models ====================

class KPICreateRequest(BaseModel):
    name: str
    alias_name: Optional[str] = None
    group_name: Optional[str] = None
    description: Optional[str] = None
    nl_definition: str
    created_by: Optional[str] = None

class KPIUpdateRequest(BaseModel):
    name: Optional[str] = None
    alias_name: Optional[str] = None
    group_name: Optional[str] = None
    description: Optional[str] = None
    nl_definition: Optional[str] = None
    is_active: Optional[bool] = None

class KPIDefinition(BaseModel):
    id: int
    name: str
    alias_name: Optional[str]
    group_name: Optional[str]
    description: Optional[str]
    nl_definition: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    is_active: bool

class KPIListResponse(BaseModel):
    success: bool
    total: int
    kpis: List[KPIDefinition]

# ==================== KPI Execution Models ====================

class KPIExecutionRequest(BaseModel):
    kg_name: str
    select_schema: str
    ruleset_name: Optional[str] = None
    db_type: str = "mysql"
    limit_records: int = 1000
    use_llm: bool = True
    excluded_fields: Optional[List[str]] = None

class KPIExecutionResult(BaseModel):
    id: int
    kpi_id: int
    kg_name: str
    select_schema: str
    ruleset_name: Optional[str]
    db_type: str
    limit_records: int
    use_llm: bool
    excluded_fields: Optional[List[str]]

    generated_sql: Optional[str]
    number_of_records: int
    joined_columns: Optional[List[List[str]]]
    sql_query_type: Optional[str]
    operation: Optional[str]

    execution_status: str
    execution_timestamp: datetime
    execution_time_ms: Optional[float]
    confidence_score: Optional[float]
    error_message: Optional[str]

    result_data: Optional[List[Dict[str, Any]]]
    source_table: Optional[str]
    target_table: Optional[str]

class KPIExecutionResponse(BaseModel):
    success: bool
    message: str
    execution_result: KPIExecutionResult

class KPIExecutionListResponse(BaseModel):
    success: bool
    total: int
    executions: List[KPIExecutionResult]

# ==================== Drill-down Models ====================

class DrilldownRequest(BaseModel):
    page: int = 1
    page_size: int = 50
    sort_by: Optional[str] = None
    sort_order: str = "asc"  # asc or desc
    filters: Optional[Dict[str, Any]] = None

class DrilldownResponse(BaseModel):
    success: bool
    execution_id: int
    kpi_name: str
    total_records: int
    page: int
    page_size: int
    total_pages: int
    data: List[Dict[str, Any]]
    columns: List[str]
    generated_sql: str
```

### 3.5 Detailed Endpoint Specifications

#### **POST /v1/landing-kpi/kpis** - Create KPI
**Request Body**:
```json
{
  "name": "Product Mismatch - RBP vs OPS",
  "alias_name": "PMR_RBP_OPS",
  "group_name": "Data Quality",
  "description": "Identifies products present in RBP GPU but missing in OPS Excel",
  "nl_definition": "Show me all products in RBP GPU which are not in OPS Excel",
  "created_by": "admin"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "KPI created successfully",
  "kpi": {
    "id": 1,
    "name": "Product Mismatch - RBP vs OPS",
    "alias_name": "PMR_RBP_OPS",
    "group_name": "Data Quality",
    "description": "Identifies products present in RBP GPU but missing in OPS Excel",
    "nl_definition": "Show me all products in RBP GPU which are not in OPS Excel",
    "created_at": "2025-10-27T10:30:00",
    "updated_at": "2025-10-27T10:30:00",
    "created_by": "admin",
    "is_active": true
  }
}
```

#### **GET /v1/landing-kpi/kpis** - List KPIs
**Query Parameters**:
- `group_name` (optional): Filter by group
- `is_active` (optional): Filter by active status
- `search` (optional): Search in name/description

**Response** (200 OK):
```json
{
  "success": true,
  "total": 5,
  "kpis": [
    {
      "id": 1,
      "name": "Product Mismatch - RBP vs OPS",
      "alias_name": "PMR_RBP_OPS",
      "group_name": "Data Quality",
      "description": "...",
      "nl_definition": "...",
      "created_at": "2025-10-27T10:30:00",
      "updated_at": "2025-10-27T10:30:00",
      "created_by": "admin",
      "is_active": true
    }
  ]
}
```

#### **GET /v1/landing-kpi/kpis/{kpi_id}** - Get KPI Details
**Response** (200 OK):
```json
{
  "success": true,
  "kpi": {
    "id": 1,
    "name": "Product Mismatch - RBP vs OPS",
    ...
  }
}
```

#### **PUT /v1/landing-kpi/kpis/{kpi_id}** - Update KPI
**Request Body**:
```json
{
  "description": "Updated description",
  "nl_definition": "Updated NL query"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "KPI updated successfully",
  "kpi": { ... }
}
```

#### **DELETE /v1/landing-kpi/kpis/{kpi_id}** - Delete KPI
**Response** (200 OK):
```json
{
  "success": true,
  "message": "KPI deleted successfully"
}
```

#### **POST /v1/landing-kpi/kpis/{kpi_id}/execute** - Execute KPI
**Request Body**:
```json
{
  "kg_name": "KG_101",
  "select_schema": "newdqschema",
  "ruleset_name": "RECON_20251027_001",
  "db_type": "mysql",
  "limit_records": 1000,
  "use_llm": true,
  "excluded_fields": ["created_date", "modified_date"]
}
```

**Process Flow**:
1. Retrieve KPI definition from database
2. Prepare NL query execution request with KPI's `nl_definition`
3. Call existing `execute_nl_queries()` from `nl_query_executor.py`
4. Store execution result in `kpi_execution_results` table
5. Return execution result to caller

**Response** (200 OK):
```json
{
  "success": true,
  "message": "KPI executed successfully",
  "execution_result": {
    "id": 101,
    "kpi_id": 1,
    "kg_name": "KG_101",
    "select_schema": "newdqschema",
    "generated_sql": "SELECT DISTINCT rbp.* FROM brz_lnd_RBP_GPU rbp LEFT JOIN brz_lnd_OPS_EXCEL ops ON rbp.PLANNING_SKU = ops.PLANNING_SKU WHERE ops.PLANNING_SKU IS NULL LIMIT 1000",
    "number_of_records": 42,
    "joined_columns": [["PLANNING_SKU", "PLANNING_SKU"]],
    "sql_query_type": "COMPARISON_QUERY",
    "operation": "NOT_IN",
    "execution_status": "success",
    "execution_timestamp": "2025-10-27T11:00:00",
    "execution_time_ms": 125.5,
    "confidence_score": 0.95,
    "source_table": "brz_lnd_RBP_GPU",
    "target_table": "brz_lnd_OPS_EXCEL",
    "result_data": [
      {"PLANNING_SKU": "SKU001", "PRODUCT_NAME": "Product A", ...},
      {"PLANNING_SKU": "SKU002", "PRODUCT_NAME": "Product B", ...}
    ]
  }
}
```

**Error Response** (200 OK - execution failed):
```json
{
  "success": false,
  "message": "KPI execution failed",
  "execution_result": {
    "id": 102,
    "kpi_id": 1,
    "execution_status": "failed",
    "error_message": "Unable to find join columns between tables",
    "execution_timestamp": "2025-10-27T11:05:00",
    ...
  }
}
```

#### **GET /v1/landing-kpi/kpis/{kpi_id}/executions** - Get Execution History
**Query Parameters**:
- `status` (optional): Filter by execution_status
- `limit` (optional): Limit number of results
- `offset` (optional): Pagination offset

**Response** (200 OK):
```json
{
  "success": true,
  "total": 10,
  "executions": [
    {
      "id": 105,
      "kpi_id": 1,
      "execution_status": "success",
      "execution_timestamp": "2025-10-27T11:30:00",
      "number_of_records": 38,
      "execution_time_ms": 110.2,
      ...
    },
    {
      "id": 104,
      "kpi_id": 1,
      "execution_status": "success",
      "execution_timestamp": "2025-10-27T11:00:00",
      "number_of_records": 42,
      "execution_time_ms": 125.5,
      ...
    }
  ]
}
```

#### **GET /v1/landing-kpi/executions/{execution_id}** - Get Execution Detail
**Response** (200 OK):
```json
{
  "success": true,
  "execution": {
    "id": 101,
    "kpi_id": 1,
    "kg_name": "KG_101",
    "generated_sql": "SELECT...",
    "number_of_records": 42,
    ...
  }
}
```

#### **GET /v1/landing-kpi/executions/{execution_id}/drilldown** - Drill-down Data
**Query Parameters**:
- `page` (default: 1): Page number
- `page_size` (default: 50): Records per page
- `sort_by` (optional): Column to sort by
- `sort_order` (optional): "asc" or "desc"

**Response** (200 OK):
```json
{
  "success": true,
  "execution_id": 101,
  "kpi_name": "Product Mismatch - RBP vs OPS",
  "total_records": 42,
  "page": 1,
  "page_size": 50,
  "total_pages": 1,
  "columns": ["PLANNING_SKU", "PRODUCT_NAME", "CATEGORY", "STATUS"],
  "data": [
    {
      "PLANNING_SKU": "SKU001",
      "PRODUCT_NAME": "Product A",
      "CATEGORY": "Electronics",
      "STATUS": "Active"
    },
    {
      "PLANNING_SKU": "SKU002",
      "PRODUCT_NAME": "Product B",
      "CATEGORY": "Home",
      "STATUS": "Active"
    }
  ],
  "generated_sql": "SELECT DISTINCT rbp.* FROM brz_lnd_RBP_GPU rbp..."
}
```

---

## 4. BACKEND IMPLEMENTATION DETAILS

### 4.1 Database Initialization

#### File: `kg_builder/services/landing_kpi_db_init.py`

```python
import sqlite3
import os
from pathlib import Path

def init_landing_kpi_database(db_path: str = "data/landing_kpi.db"):
    """Initialize Landing KPI database with schema"""

    # Ensure data directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create kpi_definitions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kpi_definitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            alias_name VARCHAR(255),
            group_name VARCHAR(255),
            description TEXT,
            nl_definition TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(100),
            is_active BOOLEAN DEFAULT 1,
            UNIQUE(name)
        )
    """)

    # Create kpi_execution_results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kpi_execution_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kpi_id INTEGER NOT NULL,
            kg_name VARCHAR(255) NOT NULL,
            select_schema VARCHAR(255) NOT NULL,
            ruleset_name VARCHAR(255),
            db_type VARCHAR(50) DEFAULT 'mysql',
            limit_records INTEGER DEFAULT 1000,
            use_llm BOOLEAN DEFAULT 1,
            excluded_fields TEXT,
            generated_sql TEXT,
            number_of_records INTEGER DEFAULT 0,
            joined_columns TEXT,
            sql_query_type VARCHAR(100),
            operation VARCHAR(50),
            execution_status VARCHAR(50) DEFAULT 'pending',
            execution_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            execution_time_ms REAL,
            confidence_score REAL,
            error_message TEXT,
            result_data TEXT,
            source_table VARCHAR(255),
            target_table VARCHAR(255),
            FOREIGN KEY (kpi_id) REFERENCES kpi_definitions(id) ON DELETE CASCADE
        )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_kpi_name ON kpi_definitions(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_kpi_active ON kpi_definitions(is_active)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_execution_kpi_id ON kpi_execution_results(kpi_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_execution_timestamp ON kpi_execution_results(execution_timestamp DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_execution_status ON kpi_execution_results(execution_status)")

    conn.commit()
    conn.close()

    print(f"Landing KPI database initialized at: {db_path}")
    return True
```

### 4.2 Service Implementation Structure

#### File: `kg_builder/services/landing_kpi_service.py`

**Key Implementation Notes**:

1. **Database Connection**: Use context managers for safe connection handling
2. **Row Factories**: Convert sqlite3.Row to dict for JSON serialization
3. **JSON Fields**: Store arrays as JSON strings (joined_columns, excluded_fields, result_data)
4. **Integration**: Import and use existing `nl_query_executor.py` functions
5. **Error Handling**: Wrap all database operations in try-except blocks
6. **Timestamps**: Use SQLite's CURRENT_TIMESTAMP for automatic timestamps

**Integration with NL Query Executor**:

```python
from kg_builder.services.nl_query_executor import execute_nl_queries
from kg_builder.services.schema_parser import load_kg_with_schemas

def execute_kpi(self, kpi_id: int, execution_params: KPIExecutionRequest):
    start_time = time.time()

    # 1. Get KPI definition
    kpi = self.get_kpi(kpi_id)

    # 2. Prepare NL query execution request
    nl_request = NLQueryExecutionRequest(
        kg_name=execution_params.kg_name,
        schemas=[execution_params.select_schema],
        definitions=[kpi.nl_definition],  # Use KPI's NL definition
        use_llm=execution_params.use_llm,
        limit=execution_params.limit_records,
        db_type=execution_params.db_type,
        excluded_fields=execution_params.excluded_fields
    )

    # 3. Execute via existing NL query executor
    try:
        nl_result = execute_nl_queries(nl_request)

        if nl_result.successful > 0:
            query_result = nl_result.results[0]

            # 4. Store execution result
            execution_result = self._store_execution_result(
                kpi_id=kpi_id,
                execution_params=execution_params,
                query_result=query_result,
                execution_time_ms=(time.time() - start_time) * 1000,
                status="success"
            )
        else:
            # Execution failed
            execution_result = self._store_execution_result(
                kpi_id=kpi_id,
                execution_params=execution_params,
                query_result=None,
                execution_time_ms=(time.time() - start_time) * 1000,
                status="failed",
                error_message=nl_result.results[0].error if nl_result.results else "Unknown error"
            )

    except Exception as e:
        # Handle exceptions
        execution_result = self._store_execution_result(...)

    return execution_result
```

### 4.3 Routes Implementation

#### File: `kg_builder/routes.py` (additions)

Add new router group:

```python
from kg_builder.services.landing_kpi_service import LandingKPIService
from kg_builder.models import (
    KPICreateRequest, KPIUpdateRequest, KPIExecutionRequest,
    KPIDefinition, KPIListResponse, KPIExecutionResponse,
    DrilldownRequest, DrilldownResponse
)

# Initialize service
landing_kpi_service = LandingKPIService()

# ==================== KPI CRUD Routes ====================

@app.post("/v1/landing-kpi/kpis", response_model=dict, tags=["Landing KPI"])
async def create_kpi(request: KPICreateRequest):
    """Create a new KPI definition"""
    pass

@app.get("/v1/landing-kpi/kpis", response_model=KPIListResponse, tags=["Landing KPI"])
async def list_kpis(
    group_name: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
):
    """List all KPI definitions with optional filters"""
    pass

@app.get("/v1/landing-kpi/kpis/{kpi_id}", response_model=dict, tags=["Landing KPI"])
async def get_kpi(kpi_id: int):
    """Get KPI definition by ID"""
    pass

@app.put("/v1/landing-kpi/kpis/{kpi_id}", response_model=dict, tags=["Landing KPI"])
async def update_kpi(kpi_id: int, request: KPIUpdateRequest):
    """Update KPI definition"""
    pass

@app.delete("/v1/landing-kpi/kpis/{kpi_id}", response_model=dict, tags=["Landing KPI"])
async def delete_kpi(kpi_id: int):
    """Delete KPI definition"""
    pass

# ==================== KPI Execution Routes ====================

@app.post("/v1/landing-kpi/kpis/{kpi_id}/execute", response_model=KPIExecutionResponse, tags=["Landing KPI"])
async def execute_kpi(kpi_id: int, request: KPIExecutionRequest):
    """Execute a KPI with specified parameters"""
    pass

@app.get("/v1/landing-kpi/kpis/{kpi_id}/executions", response_model=dict, tags=["Landing KPI"])
async def get_kpi_executions(
    kpi_id: int,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get execution history for a KPI"""
    pass

@app.get("/v1/landing-kpi/executions/{execution_id}", response_model=dict, tags=["Landing KPI"])
async def get_execution_detail(execution_id: int):
    """Get detailed execution result"""
    pass

# ==================== Drill-down Route ====================

@app.get("/v1/landing-kpi/executions/{execution_id}/drilldown", response_model=DrilldownResponse, tags=["Landing KPI"])
async def get_drilldown_data(
    execution_id: int,
    page: int = 1,
    page_size: int = 50,
    sort_by: Optional[str] = None,
    sort_order: str = "asc"
):
    """Get paginated drill-down data for an execution result"""
    pass
```

---

## 5. FRONTEND IMPLEMENTATION

### 5.1 Technology Stack
- **Framework**: React 18
- **UI Library**: Material-UI (MUI)
- **HTTP Client**: Axios
- **Routing**: React Router v6
- **Data Grid**: MUI DataGrid
- **State Management**: React Hooks (useState, useEffect)

### 5.2 Page Structure

#### New Page: `web-app/src/pages/LandingKPI.js`

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  Landing KPI Management                          [+ New KPI] │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ KPI Definitions Table                               │   │
│  │                                                       │   │
│  │ ID | Name | Alias | Group | Description | Actions   │   │
│  │ 1  | ...  | ...   | ...   | ...         | [Execute] │   │
│  │                                           [Edit]     │   │
│  │                                           [Delete]   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Features**:
1. **KPI List View**:
   - Data table showing all KPIs
   - Search/filter by name, group
   - Sort by any column
   - Actions: Execute, Edit, Delete
   - Click on row to view details

2. **Create/Edit KPI Dialog**:
   - Form with fields: name, alias_name, group_name, description, nl_definition
   - Validation for required fields
   - Save/Cancel buttons

3. **Execute KPI Dialog**:
   - Dynamic form for execution parameters:
     - KG Name (dropdown - fetch from `/kg` endpoint)
     - Select Schema (dropdown - fetch from `/schemas` endpoint)
     - Ruleset Name (optional text input)
     - DB Type (dropdown: mysql, postgresql, oracle, sqlserver)
     - Limit Records (number input, default 1000)
     - Use LLM (checkbox, default true)
     - Excluded Fields (multi-select or text input)
   - Execute button
   - Progress indicator during execution
   - On success: Show success message + link to execution history

4. **Execution History Panel**:
   - Expandable panel below KPI table
   - Shows all execution runs for selected KPI
   - Columns: Timestamp, Status, Records, Execution Time, Actions
   - Actions: View Details, Drill Down

#### New Page: `web-app/src/pages/LandingKPIDrilldown.js`

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  ← Back to KPI Management                                    │
├─────────────────────────────────────────────────────────────┤
│  KPI: Product Mismatch - RBP vs OPS                         │
│  Execution: 2025-10-27 11:30:00                             │
│  Status: Success | Records: 42 | Time: 125.5ms              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Generated SQL:                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ SELECT DISTINCT rbp.* FROM brz_lnd_RBP_GPU rbp      │   │
│  │ LEFT JOIN brz_lnd_OPS_EXCEL ops                     │   │
│  │   ON rbp.PLANNING_SKU = ops.PLANNING_SKU            │   │
│  │ WHERE ops.PLANNING_SKU IS NULL LIMIT 1000           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Query Results (42 records):                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [Export CSV] [Export Excel]          Search: [____] │   │
│  │                                                       │   │
│  │ ┌─────────────────────────────────────────────┐    │   │
│  │ │ MUI DataGrid (paginated, sortable)          │    │   │
│  │ │                                               │    │   │
│  │ │ PLANNING_SKU | PRODUCT_NAME | CATEGORY | ... │    │   │
│  │ │ SKU001       | Product A    | Electron  | ... │    │   │
│  │ │ SKU002       | Product B    | Home      | ... │    │   │
│  │ │ ...                                           │    │   │
│  │ └─────────────────────────────────────────────┘    │   │
│  │                                                       │   │
│  │ Showing 1-50 of 42 records         [< 1 2 3 4 5 >] │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Features**:
1. **Header Section**:
   - Back button to KPI list
   - KPI name and execution metadata
   - Status badge with color coding
   - Execution statistics

2. **SQL Display**:
   - Syntax-highlighted SQL query
   - Copy to clipboard button

3. **Data Grid**:
   - MUI DataGrid with all query results
   - Pagination (50 records per page)
   - Column sorting
   - Column filtering
   - Search across all columns
   - Export to CSV/Excel

4. **Metadata Panel** (optional):
   - Join columns used
   - Query type
   - Operation
   - Confidence score
   - Source/Target tables

### 5.3 Component Structure

```
web-app/src/
├── pages/
│   ├── LandingKPI.js                    # Main KPI management page
│   └── LandingKPIDrilldown.js           # Drill-down data viewer
│
├── components/
│   ├── LandingKPI/
│   │   ├── KPIList.js                   # KPI data table
│   │   ├── KPIFormDialog.js             # Create/Edit dialog
│   │   ├── KPIExecuteDialog.js          # Execute parameters dialog
│   │   ├── KPIExecutionHistory.js       # Execution history panel
│   │   └── KPIDrilldownGrid.js          # Drill-down data grid
│   │
│   └── common/
│       ├── ConfirmDialog.js             # Confirmation dialogs
│       └── StatusBadge.js               # Status indicator component
│
└── services/
    └── landingKpiApi.js                 # API service functions
```

### 5.4 API Service

#### File: `web-app/src/services/landingKpiApi.js`

```javascript
import api from './api';

// KPI CRUD
export const createKPI = (data) =>
  api.post('/landing-kpi/kpis', data);

export const listKPIs = (params) =>
  api.get('/landing-kpi/kpis', { params });

export const getKPI = (kpiId) =>
  api.get(`/landing-kpi/kpis/${kpiId}`);

export const updateKPI = (kpiId, data) =>
  api.put(`/landing-kpi/kpis/${kpiId}`, data);

export const deleteKPI = (kpiId) =>
  api.delete(`/landing-kpi/kpis/${kpiId}`);

// KPI Execution
export const executeKPI = (kpiId, params) =>
  api.post(`/landing-kpi/kpis/${kpiId}/execute`, params);

export const getKPIExecutions = (kpiId, params) =>
  api.get(`/landing-kpi/kpis/${kpiId}/executions`, { params });

export const getExecutionDetail = (executionId) =>
  api.get(`/landing-kpi/executions/${executionId}`);

// Drill-down
export const getDrilldownData = (executionId, params) =>
  api.get(`/landing-kpi/executions/${executionId}/drilldown`, { params });

// Helper: Get available KGs
export const getAvailableKGs = () =>
  api.get('/kg');

// Helper: Get available schemas
export const getAvailableSchemas = () =>
  api.get('/schemas');
```

### 5.5 Routing Addition

#### File: `web-app/src/App.js` (additions)

```javascript
import LandingKPI from './pages/LandingKPI';
import LandingKPIDrilldown from './pages/LandingKPIDrilldown';

// Inside Router
<Route path="/landing-kpi" element={<LandingKPI />} />
<Route path="/landing-kpi/drilldown/:executionId" element={<LandingKPIDrilldown />} />
```

### 5.6 Navigation Addition

#### File: `web-app/src/components/Layout.js` (additions)

Add menu item:
```javascript
{
  label: 'Landing KPI',
  path: '/landing-kpi',
  icon: <AssessmentIcon />
}
```

---

## 6. IMPLEMENTATION SEQUENCE

### Phase 1: Backend Foundation (Day 1)
1. ✅ Create database schema and initialization script
2. ✅ Implement `landing_kpi_service.py` with CRUD operations
3. ✅ Add Pydantic models to `models.py`
4. ✅ Test database operations with pytest

### Phase 2: Backend API (Day 1-2)
1. ✅ Implement KPI CRUD endpoints in `routes.py`
2. ✅ Implement KPI execution endpoint with NL query integration
3. ✅ Implement execution history endpoints
4. ✅ Implement drill-down endpoint with pagination
5. ✅ Test all endpoints with Postman/FastAPI docs

### Phase 3: Frontend - KPI Management (Day 2-3)
1. ✅ Create API service (`landingKpiApi.js`)
2. ✅ Build KPI list page with data table
3. ✅ Implement Create/Edit KPI dialog
4. ✅ Implement Delete KPI with confirmation
5. ✅ Implement Execute KPI dialog with dynamic parameters
6. ✅ Add execution history panel

### Phase 4: Frontend - Drill-down (Day 3)
1. ✅ Create drill-down page
2. ✅ Implement data grid with pagination, sorting, filtering
3. ✅ Add SQL display with syntax highlighting
4. ✅ Add export functionality (CSV/Excel)

### Phase 5: Integration & Testing (Day 4)
1. ✅ End-to-end testing of complete flow
2. ✅ UI/UX refinements
3. ✅ Error handling and validation
4. ✅ Performance optimization
5. ✅ Documentation updates

---

## 7. TECHNICAL CONSIDERATIONS

### 7.1 Data Storage Strategy

**Result Data Storage**:
- Store actual query results in `result_data` column as JSON
- Limit: Store up to 10,000 records per execution (configurable)
- For larger datasets: Store only summary + provide option to re-execute

**JSON Field Serialization**:
```python
import json

# Storing
joined_columns_json = json.dumps([["col1", "col2"], ["col3", "col4"]])
result_data_json = json.dumps(query_results)

# Retrieving
joined_columns = json.loads(row['joined_columns'])
result_data = json.loads(row['result_data'])
```

### 7.2 Performance Optimization

1. **Database Indexes**: Already included in schema
2. **Pagination**: Implement limit/offset for all list endpoints
3. **Lazy Loading**: Don't load result_data in list views
4. **Caching**: Consider caching KG/schema lists
5. **Async Operations**: Use FastAPI async endpoints where appropriate

### 7.3 Error Handling

**Backend**:
- Wrap all database operations in try-except
- Store error messages in execution results
- Return appropriate HTTP status codes
- Log all errors for debugging

**Frontend**:
- Display user-friendly error messages
- Show detailed errors in console for debugging
- Handle network errors gracefully
- Provide retry mechanisms

### 7.4 Security Considerations

1. **SQL Injection**: Using parameterized queries throughout
2. **Input Validation**: Pydantic models validate all inputs
3. **Authentication**: To be added based on project requirements
4. **Authorization**: KPI access control (future enhancement)

### 7.5 Scalability Considerations

1. **Database**: SQLite suitable for moderate usage; migrate to PostgreSQL for production
2. **Result Data**: Consider separate storage for large result sets
3. **Execution Queue**: For heavy usage, implement async execution with job queue
4. **Caching**: Implement Redis cache for frequently accessed KPIs

---

## 8. TESTING STRATEGY

### 8.1 Backend Testing

**Unit Tests** (`tests/test_landing_kpi_service.py`):
- Test CRUD operations
- Test execution logic
- Test drill-down pagination
- Test error scenarios

**Integration Tests** (`tests/test_landing_kpi_api.py`):
- Test all API endpoints
- Test NL query executor integration
- Test database persistence

### 8.2 Frontend Testing

**Manual Testing Checklist**:
- [ ] Create KPI with valid data
- [ ] Create KPI with invalid data (validation)
- [ ] Edit existing KPI
- [ ] Delete KPI with confirmation
- [ ] Execute KPI with different parameters
- [ ] View execution history
- [ ] Navigate to drill-down page
- [ ] Sort/filter drill-down data
- [ ] Export drill-down data
- [ ] Test pagination
- [ ] Test error states

### 8.3 End-to-End Testing

**Test Scenarios**:
1. Create KPI → Execute → View Results → Drill Down
2. Create multiple KPIs → Execute all → Compare results
3. Execute same KPI with different parameters
4. Handle execution failures gracefully
5. Test with large result sets (>1000 records)

---

## 9. DOCUMENTATION

### 9.1 API Documentation
- FastAPI auto-generates Swagger docs at `/docs`
- All endpoints will be tagged as "Landing KPI"
- Include request/response examples

### 9.2 User Guide
Create `docs/LANDING_KPI_USER_GUIDE.md` with:
- How to create a KPI
- How to execute a KPI
- How to interpret results
- How to use drill-down feature
- Best practices for writing NL definitions

### 9.3 Developer Guide
Create `docs/LANDING_KPI_DEVELOPER_GUIDE.md` with:
- Architecture overview
- Database schema details
- API integration examples
- Extension points

---

## 10. FUTURE ENHANCEMENTS

### Phase 2 Features (Post-MVP)
1. **KPI Scheduling**: Auto-execute KPIs on schedule
2. **Alerting**: Email/Slack alerts when KPI thresholds breached
3. **Dashboards**: Visual dashboards with charts
4. **KPI Versioning**: Track changes to KPI definitions
5. **Comparison View**: Compare execution results over time
6. **Advanced Filters**: Complex drill-down filtering
7. **Data Lineage**: Show data flow from source to result
8. **Export Options**: Export to PDF, Excel with formatting
9. **KPI Templates**: Pre-built KPI templates for common use cases
10. **Collaboration**: Share KPIs with team members

---

## 11. DEPENDENCIES

### Backend
```python
# requirements.txt additions
# (All dependencies already present in project)
```

### Frontend
```json
// package.json additions (if needed)
{
  "dependencies": {
    "@mui/x-data-grid": "^6.x.x",  // If not already installed
    "react-syntax-highlighter": "^15.x.x"  // For SQL highlighting
  }
}
```

---

## 12. DEPLOYMENT CHECKLIST

- [ ] Initialize database with schema
- [ ] Update `.env` with any new configuration
- [ ] Run backend migrations (if any)
- [ ] Install frontend dependencies
- [ ] Build frontend for production
- [ ] Test all endpoints
- [ ] Update API documentation
- [ ] Create user guide
- [ ] Deploy to staging environment
- [ ] Perform UAT (User Acceptance Testing)
- [ ] Deploy to production

---

## 13. SUCCESS METRICS

### Technical Metrics
- API response time < 200ms (excluding NL query execution)
- KPI execution success rate > 95%
- Zero SQL injection vulnerabilities
- Frontend page load time < 2s

### User Metrics
- Users can create KPI in < 2 minutes
- Drill-down data loads in < 3 seconds
- 100% of executions tracked in history
- Export functionality works for all result sets

---

## APPENDIX A: Sample Data

### Sample KPI Definitions
```json
[
  {
    "name": "Product Mismatch - RBP vs OPS",
    "alias_name": "PMR_RBP_OPS",
    "group_name": "Data Quality",
    "description": "Products in RBP GPU not in OPS Excel",
    "nl_definition": "Show me all products in RBP GPU which are not in OPS Excel"
  },
  {
    "name": "Duplicate Planning SKUs",
    "alias_name": "DUP_SKU",
    "group_name": "Data Quality",
    "description": "Find duplicate planning SKUs across systems",
    "nl_definition": "Show me all duplicate planning SKUs in the product master"
  },
  {
    "name": "Inactive Products Count",
    "alias_name": "INACT_PROD",
    "group_name": "Business Metrics",
    "description": "Count of inactive products",
    "nl_definition": "Count all products where status is inactive"
  }
]
```

---

## APPENDIX B: Database ERD

```
┌─────────────────────────────┐
│   kpi_definitions           │
├─────────────────────────────┤
│ PK  id                      │
│     name (UNIQUE)           │
│     alias_name              │
│     group_name              │
│     description             │
│     nl_definition           │
│     created_at              │
│     updated_at              │
│     created_by              │
│     is_active               │
└─────────────────────────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────────────────┐
│  kpi_execution_results      │
├─────────────────────────────┤
│ PK  id                      │
│ FK  kpi_id                  │
│     kg_name                 │
│     select_schema           │
│     ruleset_name            │
│     db_type                 │
│     limit_records           │
│     use_llm                 │
│     excluded_fields (JSON)  │
│     generated_sql           │
│     number_of_records       │
│     joined_columns (JSON)   │
│     sql_query_type          │
│     operation               │
│     execution_status        │
│     execution_timestamp     │
│     execution_time_ms       │
│     confidence_score        │
│     error_message           │
│     result_data (JSON)      │
│     source_table            │
│     target_table            │
└─────────────────────────────┘
```

---

## CONCLUSION

This implementation approach provides a comprehensive, production-ready solution for Landing KPI CRUD Management that seamlessly integrates with your existing Natural Language Query Execution system. The design prioritizes:

1. **Modularity**: Clean separation between database, service, API, and UI layers
2. **Reusability**: Leverages existing NL query execution infrastructure
3. **Scalability**: Database design supports large execution histories
4. **Usability**: Intuitive UI focused on key actions (Execute, Drill Down)
5. **Maintainability**: Clear code structure and comprehensive documentation

The phased implementation approach allows for incremental development and testing, ensuring quality at each stage.

---

**Document End**
