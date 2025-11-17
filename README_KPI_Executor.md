# Standalone KPI Executor Script

This standalone Python script mimics the API call to `/api/v1/landing-kpi-mssql/kpis/19/execute` and can be run independently outside the main project.

## Features

- ✅ **Standalone Operation**: Works independently without the main project dependencies
- ✅ **Complete API Mimicking**: Replicates the exact functionality of the API endpoint
- ✅ **Comprehensive Logging**: Detailed logging for every step of execution
- ✅ **Database Integration**: Connects to both KPI and data databases
- ✅ **OpenAI Integration**: Uses OpenAI GPT-4 for SQL generation
- ✅ **Flexible Configuration**: Command-line arguments for all parameters
- ✅ **Error Handling**: Robust error handling and reporting
- ✅ **Result Storage**: Option to save results to JSON file

## Prerequisites

1. **Python 3.7+** installed
2. **ODBC Driver 17 for SQL Server** installed
3. **OpenAI API Key** with access to GPT-4
4. **Database Access** to both KPI Analytics and data databases

### Installing ODBC Driver

**Windows:**
Download and install from [Microsoft's official page](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

**Linux (Ubuntu/Debian):**
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

**macOS:**
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
HOMEBREW_NO_ENV_FILTERING=1 ACCEPT_EULA=Y brew install msodbcsql17
```

## Installation

1. **Clone or download the script files:**
   ```bash
   # Download the files
   wget https://example.com/kpi_executor_standalone.py
   wget https://example.com/requirements_standalone.txt
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements_standalone.txt
   ```

## Usage

### Basic Usage

```bash
python kpi_executor_standalone.py \
    --openai-key "sk-your-openai-key-here" \
    --kg-name "default" \
    --db-host "localhost" \
    --db-user "username" \
    --db-password "password" \
    --kpi-id 19
```

### Advanced Usage with Custom Parameters

```bash
python kpi_executor_standalone.py \
    --openai-key "sk-your-openai-key-here" \
    --temperature 0.1 \
    --kg-name "KG_101" \
    --db-host "kpi-server.example.com" \
    --db-port 1433 \
    --db-name "KPI_Analytics" \
    --db-user "kpi_user" \
    --db-password "secure_password" \
    --data-host "data-server.example.com" \
    --data-db-name "NewDQ" \
    --data-user "data_user" \
    --data-password "data_password" \
    --kpi-id 19 \
    --select-schema "newdqschemanov" \
    --limit-records 500 \
    --output-file "kpi_results.json" \
    --verbose
```

## Command Line Arguments

### Required Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--openai-key` | OpenAI API key | `sk-proj-...` |
| `--kg-name` | Knowledge graph name | `default`, `KG_101` |
| `--db-host` | KPI database host | `localhost`, `server.com` |
| `--db-user` | KPI database username | `sa`, `kpi_user` |
| `--db-password` | KPI database password | `password123` |
| `--kpi-id` | KPI ID to execute | `19` |

### Optional Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--temperature` | `0.0` | OpenAI temperature (0.0-2.0) |
| `--db-port` | `1433` | KPI database port |
| `--db-name` | `KPI_Analytics` | KPI database name |
| `--select-schema` | `newdqschemanov` | Schema to query |
| `--limit-records` | `1000` | Maximum records to return |
| `--data-host` | Same as `--db-host` | Data database host |
| `--data-port` | Same as `--db-port` | Data database port |
| `--data-db-name` | Same as `--db-name` | Data database name |
| `--data-user` | Same as `--db-user` | Data database username |
| `--data-password` | Same as `--db-password` | Data database password |
| `--output-file` | None | Save results to JSON file |
| `--verbose` | False | Enable verbose logging |

## Script Workflow

The script follows the exact same workflow as the API:

1. **🔍 Retrieve KPI Definition**: Fetches KPI details from the database
2. **📝 Create Execution Record**: Creates a new execution record for tracking
3. **🤖 Generate SQL with LLM**: Uses OpenAI to convert natural language to SQL
4. **🗃️ Execute SQL Query**: Runs the generated SQL against the data database
5. **💾 Update Execution Record**: Updates the record with results and status

## Output

### Console Output
The script provides detailed logging for each step:

```
2024-01-15 10:30:00 - INFO - ✅ Initialized OpenAI client with temperature: 0.0
2024-01-15 10:30:01 - INFO - 🔍 STEP 1: Retrieving KPI definition for ID: 19
2024-01-15 10:30:01 - INFO - ✅ Found KPI: Revenue Analysis
2024-01-15 10:30:02 - INFO - 🤖 STEP 3: Generating SQL using LLM
2024-01-15 10:30:05 - INFO - ✅ Generated SQL successfully
2024-01-15 10:30:05 - INFO - 🗃️ STEP 4: Executing SQL query
2024-01-15 10:30:06 - INFO - ✅ Query executed successfully
2024-01-15 10:30:06 - INFO - 🎉 KPI execution completed!
```

### JSON Output (if --output-file specified)
```json
{
  "success": true,
  "kpi_id": 19,
  "execution_id": 12345,
  "kpi_name": "Revenue Analysis",
  "kpi_description": "Analyze revenue trends",
  "nl_definition": "Show total revenue by month",
  "generated_sql": "SELECT MONTH(date) as month, SUM(revenue) as total_revenue FROM sales GROUP BY MONTH(date)",
  "record_count": 12,
  "execution_time_ms": 1250.5,
  "records": [...],
  "columns": ["month", "total_revenue"]
}
```

## Error Handling

The script includes comprehensive error handling:

- **Database Connection Errors**: Clear messages for connection failures
- **KPI Not Found**: Handles missing KPI definitions gracefully
- **SQL Generation Errors**: Reports OpenAI API issues
- **SQL Execution Errors**: Captures and reports database query errors
- **Permission Errors**: Handles insufficient database permissions

## Logging

Two types of logging are available:

1. **Console Logging**: Real-time progress updates
2. **File Logging**: Detailed logs saved to `kpi_execution.log`

Enable verbose logging with `--verbose` for debugging.

## Database Requirements

### KPI Analytics Database Tables

The script expects these tables in the KPI database:

```sql
-- KPI definitions table
CREATE TABLE kpi_definitions (
    id INT PRIMARY KEY,
    name NVARCHAR(255),
    alias_name NVARCHAR(255),
    group_name NVARCHAR(255),
    description NVARCHAR(MAX),
    nl_definition NVARCHAR(MAX),
    created_at DATETIME,
    updated_at DATETIME,
    created_by NVARCHAR(255),
    is_active BIT
);

-- KPI execution results table
CREATE TABLE kpi_execution_results (
    id INT IDENTITY(1,1) PRIMARY KEY,
    kpi_id INT,
    kg_name NVARCHAR(255),
    select_schema NVARCHAR(255),
    db_type NVARCHAR(50),
    limit_records INT,
    use_llm BIT,
    execution_status NVARCHAR(50),
    user_id NVARCHAR(255),
    session_id NVARCHAR(255),
    number_of_records INT,
    execution_time_ms FLOAT,
    generated_sql NVARCHAR(MAX),
    result_data NVARCHAR(MAX),
    error_message NVARCHAR(MAX),
    execution_timestamp DATETIME
);
```

### Data Database

The data database should contain the actual tables referenced in KPI definitions.

## Security Considerations

- **API Keys**: Never commit OpenAI API keys to version control
- **Database Credentials**: Use environment variables or secure credential storage
- **Network Security**: Ensure database connections use encrypted channels
- **Access Control**: Use database users with minimal required permissions

## Troubleshooting

### Common Issues

1. **ODBC Driver Not Found**
   ```
   Error: ('01000', "[01000] [unixODBC][Driver Manager]Can't open lib...")
   ```
   **Solution**: Install ODBC Driver 17 for SQL Server

2. **OpenAI API Key Invalid**
   ```
   Error: Invalid API key provided
   ```
   **Solution**: Verify your OpenAI API key is correct and has sufficient credits

3. **Database Connection Failed**
   ```
   Error: ('28000', "[28000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Login failed...")
   ```
   **Solution**: Check database credentials and network connectivity

4. **KPI Not Found**
   ```
   Error: KPI with ID 19 not found
   ```
   **Solution**: Verify the KPI ID exists in the kpi_definitions table

### Debug Mode

Run with `--verbose` flag for detailed debugging information:

```bash
python kpi_executor_standalone.py --verbose [other arguments...]
```

## Examples

### Example 1: Basic Execution
```bash
python kpi_executor_standalone.py \
    --openai-key "sk-proj-abc123..." \
    --kg-name "default" \
    --db-host "localhost" \
    --db-user "sa" \
    --db-password "MyPassword123" \
    --kpi-id 19
```

### Example 2: Production Environment
```bash
python kpi_executor_standalone.py \
    --openai-key "$OPENAI_API_KEY" \
    --temperature 0.0 \
    --kg-name "PROD_KG" \
    --db-host "kpi-prod.company.com" \
    --db-port 1433 \
    --db-name "KPI_Analytics" \
    --db-user "kpi_service" \
    --db-password "$KPI_DB_PASSWORD" \
    --data-host "data-prod.company.com" \
    --data-db-name "DataWarehouse" \
    --data-user "data_reader" \
    --data-password "$DATA_DB_PASSWORD" \
    --kpi-id 19 \
    --select-schema "dw_schema" \
    --limit-records 5000 \
    --output-file "results_$(date +%Y%m%d_%H%M%S).json" \
    --verbose
```

### Example 3: Using Environment Variables
```bash
# Set environment variables
export OPENAI_API_KEY="sk-proj-abc123..."
export KPI_DB_PASSWORD="MyPassword123"
export DATA_DB_PASSWORD="DataPassword456"

# Run script
python kpi_executor_standalone.py \
    --openai-key "$OPENAI_API_KEY" \
    --kg-name "default" \
    --db-host "localhost" \
    --db-user "sa" \
    --db-password "$KPI_DB_PASSWORD" \
    --data-password "$DATA_DB_PASSWORD" \
    --kpi-id 19
```

## License

This script is part of the Cognito AI DQ API project. Please refer to the main project license for usage terms.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the log files for detailed error information
3. Ensure all prerequisites are properly installed
4. Verify database connectivity and permissions
```
