# KPI System Migration to MS SQL Server ✅

## 🎯 Overview

This document outlines the implementation of three major changes to the KPI system:

1. **Move kpi_execution_results to MS SQL Server** (from SQLite)
2. **Include ops_planner column in all generated queries**
3. **Always show generated SQL regardless of execution results**

---

## 📊 **Change 1: MS SQL Server Migration**

### **Files Created/Modified**:

#### **1. Database Schema** 📁 `scripts/create_kpi_tables_mssql.sql`
```sql
-- Creates MS SQL Server tables:
CREATE TABLE kpi_definitions (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL UNIQUE,
    alias_name NVARCHAR(255) NULL,
    group_name NVARCHAR(255) NULL,
    description NVARCHAR(MAX) NULL,
    nl_definition NVARCHAR(MAX) NOT NULL,
    -- ... additional fields
);

CREATE TABLE kpi_execution_results (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    kpi_id BIGINT NOT NULL,
    generated_sql NVARCHAR(MAX) NULL,  -- Always stored
    result_data NVARCHAR(MAX) NULL,    -- JSON format
    evidence_data NVARCHAR(MAX) NULL,  -- JSON format (NEW)
    -- ... additional fields
);
```

#### **2. Service Layer** 📁 `kg_builder/services/landing_kpi_service_mssql.py`
- **MS SQL Server connection** using pyodbc
- **CRUD operations** for KPI definitions
- **Execution result management** with JSON storage
- **Always stores generated SQL** even on execution failure

#### **3. API Layer** 📁 `api/routes/landing_kpi_mssql.py`
- **New API endpoints** with `/v1/landing-kpi-mssql` prefix
- **Enhanced error handling** with SQL preservation
- **SQL preview endpoint** for testing queries

### **Benefits**:
- ✅ **Centralized storage** in main database
- ✅ **Better performance** for large datasets
- ✅ **ACID compliance** for data integrity
- ✅ **Unified backup/recovery** with main system

---

## 🔧 **Change 2: OPS_PLANNER Column Inclusion**

### **File Created**: 📁 `kg_builder/services/enhanced_sql_generator.py`

### **Enhancement Logic**:
```python
def enhance_sql_with_ops_planner(self, sql: str, query_intent: Dict[str, Any]) -> str:
    """Automatically add ops_planner column to queries involving hana_material_master."""
    
    # 1. Check if query involves hana_material_master
    if not self._involves_hana_material_master(sql):
        return sql  # Skip if not relevant
    
    # 2. Find table alias (e.g., 'h' in 'FROM hana_material_master h')
    alias = self._find_hana_material_master_alias(sql)
    
    # 3. Add ops_planner to SELECT clause
    # Before: SELECT s.Material, s.Product_Line FROM ...
    # After:  SELECT s.Material, s.Product_Line, h.OPS_PLANNER as ops_planner FROM ...
    
    return enhanced_sql
```

### **Integration**:
```python
# In API execution
original_generator = LLMSQLGenerator()
enhanced_generator = EnhancedSQLGenerator(original_generator)
executor.sql_generator = enhanced_generator  # Use enhanced version
```

### **Benefits**:
- ✅ **Automatic inclusion** of ops_planner in all relevant queries
- ✅ **No manual intervention** required
- ✅ **Backward compatible** - doesn't break existing queries
- ✅ **Smart detection** - only adds when hana_material_master is involved

---

## 📋 **Change 3: Always Show Generated SQL**

### **Implementation Locations**:

#### **1. Database Storage** (Always Store SQL)
```python
# In landing_kpi_service_mssql.py
def update_execution_result(self, execution_id: int, result_data: Dict[str, Any]):
    cursor.execute("""
        UPDATE kpi_execution_results
        SET generated_sql = ?, ...  -- ALWAYS store SQL, even on error
        WHERE id = ?
    """, (
        result_data.get('generated_sql'),  # Never None
        # ... other fields
    ))
```

#### **2. API Responses** (Always Return SQL)
```python
# Success response
return jsonify({
    'success': True,
    'data': {
        'generated_sql': result_data['generated_sql'],  # Always included
        'number_of_records': result_data['number_of_records'],
        # ... other fields
    }
})

# Error response
return jsonify({
    'success': False,
    'error': str(exec_error),
    'generated_sql': error_result_data.get('generated_sql'),  # Even on error
})
```

#### **3. SQL Preview Endpoint**
```python
@landing_kpi_mssql_bp.route('/sql-preview', methods=['POST'])
def preview_sql():
    """Preview generated SQL without executing."""
    # Generates and returns SQL without running the query
    return jsonify({
        'generated_sql': generated_sql,  # Always shown
        'includes_ops_planner': 'ops_planner' in generated_sql.lower()
    })
```

### **Benefits**:
- ✅ **Debugging capability** - Always see what SQL was generated
- ✅ **Transparency** - Users can verify query logic
- ✅ **Error diagnosis** - SQL available even when execution fails
- ✅ **Preview mode** - Test SQL generation without execution

---

## 🚀 **Deployment Instructions**

### **Step 1: Create MS SQL Server Tables**
```sql
sqlcmd -S your_server -d NewDQ -i scripts/create_kpi_tables_mssql.sql
```

### **Step 2: Update Application Configuration**
```python
# In your main application
from api.routes.landing_kpi_mssql import landing_kpi_mssql_bp

# Register new blueprint
app.register_blueprint(landing_kpi_mssql_bp)
```

### **Step 3: Test New Endpoints**
```bash
# Health check
curl http://localhost:5000/v1/landing-kpi-mssql/health

# Preview SQL with ops_planner
curl -X POST http://localhost:5000/v1/landing-kpi-mssql/sql-preview \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me products in RBP GPU missing in OPS Excel"}'

# Execute KPI
curl -X POST http://localhost:5000/v1/landing-kpi-mssql/kpis/1/execute \
  -H "Content-Type: application/json" \
  -d '{"kg_name": "default", "select_schema": "newdqschemanov"}'
```

---

## 📈 **API Endpoints Summary**

### **New MS SQL Server Endpoints**:
- `GET /v1/landing-kpi-mssql/kpis` - Get all KPIs
- `POST /v1/landing-kpi-mssql/kpis` - Create KPI
- `GET /v1/landing-kpi-mssql/kpis/{id}` - Get KPI by ID
- `PUT /v1/landing-kpi-mssql/kpis/{id}` - Update KPI
- `DELETE /v1/landing-kpi-mssql/kpis/{id}` - Delete KPI
- `POST /v1/landing-kpi-mssql/kpis/{id}/execute` - Execute KPI
- `GET /v1/landing-kpi-mssql/kpis/{id}/executions` - Get execution history
- `GET /v1/landing-kpi-mssql/executions/{id}` - Get execution details
- `POST /v1/landing-kpi-mssql/sql-preview` - Preview SQL generation
- `GET /v1/landing-kpi-mssql/health` - Health check

### **Enhanced Features**:
- ✅ **Always returns generated_sql** in all responses
- ✅ **Includes ops_planner** in queries involving hana_material_master
- ✅ **Stores evidence_data** directly in MS SQL Server
- ✅ **JSON storage** for complex data structures
- ✅ **Performance indexes** for fast queries
