# Standalone SQL Preview Generator

This standalone Python script generates SQL from natural language definitions using OpenAI, similar to the SQL preview functionality in the API, but **without executing the queries**. It's perfect for testing, validation, and understanding how natural language gets converted to SQL.

## 🚀 Features

- ✅ **SQL Generation Only**: Generates SQL without executing it
- ✅ **OpenAI Integration**: Uses GPT-4 for intelligent SQL generation
- ✅ **Schema-Aware**: Retrieves database schema for accurate SQL generation
- ✅ **Enhancement Detection**: Identifies material master and OPS_PLANNER enhancements
- ✅ **Comprehensive Logging**: Detailed step-by-step logging
- ✅ **Command Line Interface**: Easy-to-use CLI with all parameters
- ✅ **JSON Output**: Optional JSON output for integration

## 📋 Prerequisites

1. **Python 3.7+** installed
2. **ODBC Driver 17 for SQL Server** installed
3. **OpenAI API Key** with access to GPT-4
4. **Database Access** for schema retrieval (read-only)

## 🔧 Installation

1. **Download the script files:**
   ```bash
   # Download the main script and requirements
   curl -O https://example.com/standalone_sql_preview.py
   curl -O https://example.com/requirements_sql_preview.txt
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements_sql_preview.txt
   ```

3. **Test the setup:**
   ```bash
   python test_sql_preview_args.py
   ```

## 💻 Usage

### Basic Usage

```bash
python standalone_sql_preview.py \
     --nl-definition "get products from hana_material_master where OPS_PLANNER is missing" \
     --kg-name "KG_Test_001" \
     --select-schema "newdqnov7" \
     --openai-key "sk-proj-your-key-here" \
     --temperature 0 \
     --db-host "DESKTOP-41O1AL9\LOCALHOST" \
     --db-name "NewDQ" \
     --db-user "mithun" \
     --db-password "mithun123" \
     --use-llm \
     --verbose
```

### Advanced Usage with Output File

```bash
python standalone_sql_preview.py \
     --nl-definition "count products by category from inventory table" \
     --kg-name "Production_KG" \
     --select-schema "production" \
     --openai-key "sk-proj-your-key-here" \
     --temperature 0.1 \
     --db-host "prod-server.company.com" \
     --db-port 1433 \
     --db-name "DataWarehouse" \
     --db-user "analyst" \
     --db-password "secure_password" \
     --use-llm \
     --output-file "sql_preview_$(date +%Y%m%d_%H%M%S).json" \
     --verbose
```

## 📝 Command Line Arguments

### Required Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--nl-definition` | Natural language definition to convert to SQL | `"get products where price > 100"` |
| `--kg-name` | Knowledge graph name | `"KG_Test_001"` |
| `--select-schema` | Database schema to query | `"newdqnov7"` |
| `--openai-key` | OpenAI API key | `"sk-proj-..."` |
| `--db-host` | Database host | `"localhost"` |
| `--db-user` | Database username | `"mithun"` |
| `--db-password` | Database password | `"password123"` |

### Optional Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--temperature` | `0.0` | OpenAI temperature (0.0-2.0) |
| `--db-port` | `1433` | Database port |
| `--db-name` | `NewDQ` | Database name |
| `--use-llm` | `False` | Use LLM for parsing (vs rule-based) |
| `--output-file` | None | Save results to JSON file |
| `--verbose` | `False` | Enable verbose logging |

## 🔄 Script Workflow

The script follows these steps:

1. **🔍 Schema Retrieval**: Connects to database and retrieves table/column information
2. **🧠 NL Parsing**: Parses natural language using LLM or rule-based approach
3. **🤖 SQL Generation**: Uses OpenAI to generate SQL with schema context
4. **🔧 Enhancement**: Applies enhancements (material master, OPS_PLANNER)
5. **📊 Results**: Returns generated SQL with metadata

## 📊 Output Examples

### Console Output
```
================================================================================
🚀 STANDALONE SQL PREVIEW GENERATOR STARTED
================================================================================
NL Definition: get products from hana_material_master where OPS_PLANNER is missing
KG Name: KG_Test_001
Schema: newdqnov7
Use LLM: True
Temperature: 0.0
Database: DESKTOP-41O1AL9\LOCALHOST:1433/NewDQ
================================================================================

🔍 STEP 1: Retrieving database schema information
   Database: DESKTOP-41O1AL9\LOCALHOST\NewDQ
   Schema: newdqnov7
✅ Retrieved schema information
   Tables found: 15
   Table: hana_material_master (25 columns)
   Table: ops_excel (12 columns)

🧠 STEP 2: Parsing natural language definition
   Definition: get products from hana_material_master where OPS_PLANNER is missing
   Use LLM: True
   Sending request to OpenAI...
✅ Parsed with LLM successfully
   Query Type: filter
   Operation: select
   Source Table: hana_material_master
   Confidence: 0.9

🤖 STEP 3: Generating SQL using LLM
   Intent: get products from hana_material_master where OPS_PLANNER is missing
   Source Table: hana_material_master
   Database Type: sqlserver
   Sending SQL generation request to OpenAI...
✅ Generated SQL successfully
   SQL Length: 156 characters

🔧 STEP 4: Applying SQL enhancements
   Detected hana_material_master table usage
   Adding OPS_PLANNER column enhancement
✅ SQL enhancements completed
   - Material master table detected
   - Added OPS_PLANNER column to SELECT
   - OPS_PLANNER column included

🎉 SQL preview generation completed!
   Success: True
   Query Type: filter
   Source Table: hana_material_master
   Confidence: 0.9
   Total time: 2847.32ms

================================================================================
📊 SQL PREVIEW RESULTS
================================================================================
Success: True
Query Type: filter
Operation: select
Source Table: hana_material_master
Confidence: 0.9
Execution Time: 2847.32ms

📝 GENERATED SQL:
------------------------------------------------------------
SELECT TOP 1000 *, OPS_PLANNER 
FROM hana_material_master 
WHERE OPS_PLANNER IS NULL
------------------------------------------------------------

🔧 ENHANCEMENTS APPLIED:
  - Material master table detected
  - Added OPS_PLANNER column to SELECT
  - OPS_PLANNER column included

📊 SCHEMA INFO:
  Schema: newdqnov7
  Tables: 15
  Available tables: hana_material_master, ops_excel, inventory, products, sales

================================================================================
✅ SQL PREVIEW GENERATION COMPLETED
================================================================================
```

### JSON Output (if --output-file specified)
```json
{
  "success": true,
  "nl_definition": "get products from hana_material_master where OPS_PLANNER is missing",
  "kg_name": "KG_Test_001",
  "select_schema": "newdqnov7",
  "use_llm": true,
  "query_intent": {
    "definition": "get products from hana_material_master where OPS_PLANNER is missing",
    "query_type": "filter",
    "operation": "select",
    "source_table": "hana_material_master",
    "target_table": null,
    "confidence": 0.9
  },
  "generated_sql": "SELECT TOP 1000 *, OPS_PLANNER FROM hana_material_master WHERE OPS_PLANNER IS NULL",
  "original_sql": "SELECT TOP 1000 * FROM hana_material_master WHERE OPS_PLANNER IS NULL",
  "enhancements": {
    "applied": [
      "Material master table detected",
      "Added OPS_PLANNER column to SELECT",
      "OPS_PLANNER column included"
    ],
    "material_master_detected": true,
    "ops_planner_included": true
  },
  "schema_info": {
    "schema_name": "newdqnov7",
    "tables_count": 15,
    "tables": ["hana_material_master", "ops_excel", "inventory", "products", "sales"]
  },
  "execution_time_ms": 2847.32
}
```

## 🎯 Use Cases

### 1. **SQL Validation**
Test how natural language gets converted to SQL before executing expensive queries.

### 2. **Development & Testing**
Validate SQL generation logic during development without database impact.

### 3. **Training & Learning**
Understand how different natural language phrases translate to SQL.

### 4. **Integration Testing**
Test OpenAI integration and schema retrieval without query execution.

### 5. **Documentation**
Generate SQL examples for documentation and training materials.

## 🔍 Natural Language Examples

| Natural Language | Expected SQL Pattern |
|------------------|---------------------|
| `"get products where OPS_PLANNER is missing"` | `SELECT * FROM products WHERE OPS_PLANNER IS NULL` |
| `"count products by category"` | `SELECT category, COUNT(*) FROM products GROUP BY category` |
| `"show products not in inventory"` | `SELECT p.* FROM products p LEFT JOIN inventory i ON ... WHERE i.id IS NULL` |
| `"sum revenue by month"` | `SELECT MONTH(date), SUM(revenue) FROM sales GROUP BY MONTH(date)` |

## 🛠️ Troubleshooting

### Common Issues

1. **ODBC Driver Not Found**
   ```
   Error: ('01000', "[01000] [unixODBC][Driver Manager]Can't open lib...")
   ```
   **Solution**: Install ODBC Driver 17 for SQL Server

2. **OpenAI API Error**
   ```
   Error: Invalid API key provided
   ```
   **Solution**: Verify your OpenAI API key and credits

3. **Database Connection Failed**
   ```
   Error: Login failed for user 'mithun'
   ```
   **Solution**: Check database credentials and network connectivity

4. **Schema Not Found**
   ```
   Warning: No tables found in schema 'newdqnov7'
   ```
   **Solution**: Verify schema name and user permissions

### Debug Mode

Run with `--verbose` flag for detailed debugging:

```bash
python standalone_sql_preview.py --verbose [other arguments...]
```

## 🔒 Security Notes

- **API Keys**: Never commit OpenAI API keys to version control
- **Database Credentials**: Use environment variables for sensitive data
- **Read-Only Access**: Script only needs SELECT permissions for schema retrieval
- **Network Security**: Ensure secure database connections

## 📚 Related Scripts

- `kpi_executor_standalone.py` - Full KPI execution with query execution
- `test_sql_preview_args.py` - Test command line argument parsing
- `test_setup.py` - Validate installation and prerequisites

## 🎉 Success Indicators

When the script runs successfully, you should see:
- ✅ Schema retrieval with table count
- ✅ Successful NL parsing with confidence score
- ✅ Generated SQL with proper syntax
- ✅ Applied enhancements (if applicable)
- ✅ Complete results in specified format

The script is ready to use with your exact command line format!
```
