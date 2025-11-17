#!/usr/bin/env python3
"""
Robust Standalone KPI Executor Script - NO FALLBACKS VERSION
Mimics the API call to /api/v1/landing-kpi-mssql/kpis/19/execute

This version has strict error handling with NO fallbacks or silent failures.
All errors are explicitly raised and logged.
"""

import logging
import time
import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('kpi_execution_robust.log')
    ]
)
logger = logging.getLogger(__name__)

# ==================== STRICT CONFIGURATION VALIDATION ====================
def validate_configuration():
    """Validate all configuration before starting - NO FALLBACKS."""
    logger.info("🔍 Validating configuration...")
    
    # Validate OpenAI configuration
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is required and cannot be empty")
    
    if OPENAI_API_KEY == "your-openai-api-key-here":
        raise ValueError("OPENAI_API_KEY must be set to a real API key")
    
    if not OPENAI_MODEL:
        raise ValueError("OPENAI_MODEL is required")
    
    if not isinstance(OPENAI_TEMPERATURE, (int, float)) or OPENAI_TEMPERATURE < 0 or OPENAI_TEMPERATURE > 2:
        raise ValueError("OPENAI_TEMPERATURE must be a number between 0 and 2")
    
    if not isinstance(OPENAI_MAX_TOKENS, int) or OPENAI_MAX_TOKENS <= 0:
        raise ValueError("OPENAI_MAX_TOKENS must be a positive integer")
    
    # Validate database configurations
    for config_name, config in [("DB_CONFIG", DB_CONFIG), ("SOURCE_DB_CONFIG", SOURCE_DB_CONFIG)]:
        if not isinstance(config, dict):
            raise ValueError(f"{config_name} must be a dictionary")
        
        required_keys = ['host', 'port', 'database', 'username', 'password']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"{config_name} missing required key: {key}")
            if not config[key]:
                raise ValueError(f"{config_name}[{key}] cannot be empty")
        
        if not isinstance(config['port'], int) or config['port'] <= 0:
            raise ValueError(f"{config_name}['port'] must be a positive integer")
    
    # Validate KPI ID
    if not isinstance(KPI_ID, int) or KPI_ID <= 0:
        raise ValueError("KPI_ID must be a positive integer")
    
    # Validate execution parameters
    if not isinstance(EXECUTION_PARAMS, dict):
        raise ValueError("EXECUTION_PARAMS must be a dictionary")
    
    required_params = ['kg_name', 'select_schema', 'limit_records', 'use_llm', 'db_type']
    for param in required_params:
        if param not in EXECUTION_PARAMS:
            raise ValueError(f"EXECUTION_PARAMS missing required parameter: {param}")
    
    if not isinstance(EXECUTION_PARAMS['limit_records'], int) or EXECUTION_PARAMS['limit_records'] <= 0:
        raise ValueError("EXECUTION_PARAMS['limit_records'] must be a positive integer")
    
    logger.info("✅ Configuration validation passed")

# ==================== CONFIGURATION ====================
# Embedded configuration - modify these values as needed

# OpenAI Configuration
OPENAI_API_KEY = "Test"
OPENAI_MODEL = "gpt-4o"
OPENAI_TEMPERATURE = 0.0
OPENAI_MAX_TOKENS = 2000

# Database Configuration (MS SQL Server)
DB_CONFIG = {
    'host': 'DESKTOP-41O1AL9\\LOCALHOST',
    'port': 1433,
    'database': 'KPI_Analytics',
    'username': 'mithun',
    'password': 'mithun123'
}

# Source Database Configuration (for data queries)
SOURCE_DB_CONFIG = {
    'host': 'DESKTOP-41O1AL9\\LOCALHOST',
    'port': 1433,
    'database': 'NewDQ',
    'username': 'mithun',
    'password': 'mithun123'
}

# KPI Execution Parameters
KPI_ID = 19
EXECUTION_PARAMS = {
    'kg_name': 'default',
    'select_schema': 'newdqschemanov',
    'limit_records': 1000,
    'use_llm': True,
    'db_type': 'sqlserver',
    'user_id': 'standalone_script',
    'session_id': f'standalone_{int(time.time())}'
}

# ==================== STRICT DEPENDENCY CHECKING ====================
def check_dependencies():
    """Check dependencies with NO fallbacks - fail fast if missing."""
    logger.info("🔍 Checking dependencies...")
    
    try:
        import pyodbc
        logger.info("✅ pyodbc available")
    except ImportError as e:
        raise ImportError("pyodbc is required but not installed. Run: pip install pyodbc") from e
    
    try:
        import openai
        from openai import OpenAI
        logger.info("✅ openai available")
    except ImportError as e:
        raise ImportError("openai is required but not installed. Run: pip install openai") from e
    
    # Test ODBC driver availability
    try:
        drivers = pyodbc.drivers()
        if 'ODBC Driver 17 for SQL Server' not in drivers:
            available_drivers = ', '.join(drivers)
            raise RuntimeError(f"ODBC Driver 17 for SQL Server not found. Available drivers: {available_drivers}")
        logger.info("✅ ODBC Driver 17 for SQL Server available")
    except Exception as e:
        raise RuntimeError("Failed to check ODBC drivers") from e

# ==================== STRICT DATABASE CONNECTIONS ====================
def get_kpi_db_connection():
    """Get connection to KPI Analytics database - NO fallbacks."""
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_CONFIG['host']},{DB_CONFIG['port']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        f"TrustServerCertificate=yes;"
    )

    logger.info(f"🔌 Connecting to KPI database: {DB_CONFIG['host']}/{DB_CONFIG['database']}")

    try:
        import pyodbc
        conn = pyodbc.connect(conn_str, timeout=30)

        # Test the connection immediately
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()

        logger.info("✅ KPI database connection established and tested")
        return conn

    except Exception as e:
        error_msg = f"Failed to connect to KPI database {DB_CONFIG['host']}/{DB_CONFIG['database']}: {e}"
        logger.error(error_msg)
        raise ConnectionError(error_msg) from e

def get_source_db_connection():
    """Get connection to source data database - NO fallbacks."""
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SOURCE_DB_CONFIG['host']},{SOURCE_DB_CONFIG['port']};"
        f"DATABASE={SOURCE_DB_CONFIG['database']};"
        f"UID={SOURCE_DB_CONFIG['username']};"
        f"PWD={SOURCE_DB_CONFIG['password']};"
        f"TrustServerCertificate=yes;"
    )

    logger.info(f"🔌 Connecting to source database: {SOURCE_DB_CONFIG['host']}/{SOURCE_DB_CONFIG['database']}")

    try:
        import pyodbc
        conn = pyodbc.connect(conn_str, timeout=30)

        # Test the connection immediately
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()

        logger.info("✅ Source database connection established and tested")
        return conn

    except Exception as e:
        error_msg = f"Failed to connect to source database {SOURCE_DB_CONFIG['host']}/{SOURCE_DB_CONFIG['database']}: {e}"
        logger.error(error_msg)
        raise ConnectionError(error_msg) from e

# ==================== STRICT KPI OPERATIONS ====================
def get_kpi_definition(kpi_id: int) -> Dict[str, Any]:
    """Get KPI definition from database - NO fallbacks, must exist."""
    logger.info(f"📋 Fetching KPI definition for ID: {kpi_id}")

    if not isinstance(kpi_id, int) or kpi_id <= 0:
        raise ValueError(f"Invalid KPI ID: {kpi_id}. Must be a positive integer.")

    conn = get_kpi_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, alias_name, group_name, description, nl_definition,
                   is_active, business_priority, target_sla_seconds
            FROM kpi_definitions
            WHERE id = ?
        """, (kpi_id,))

        row = cursor.fetchone()
        if not row:
            raise ValueError(f"KPI {kpi_id} does not exist in the database")

        kpi = {
            'id': row[0],
            'name': row[1],
            'alias_name': row[2],
            'group_name': row[3],
            'description': row[4],
            'nl_definition': row[5],
            'is_active': bool(row[6]),
            'business_priority': row[7],
            'target_sla_seconds': row[8]
        }

        # Strict validation of KPI data
        if not kpi['is_active']:
            raise ValueError(f"KPI {kpi_id} exists but is inactive (is_active=False)")

        if not kpi['nl_definition'] or not kpi['nl_definition'].strip():
            raise ValueError(f"KPI {kpi_id} has empty or null nl_definition")

        if not kpi['name'] or not kpi['name'].strip():
            raise ValueError(f"KPI {kpi_id} has empty or null name")

        logger.info(f"✅ Found active KPI: {kpi['name']}")
        logger.info(f"   📝 NL Definition: {kpi['nl_definition']}")
        logger.info(f"   🎯 Priority: {kpi['business_priority']}")

        return kpi

    except Exception as e:
        if isinstance(e, ValueError):
            raise  # Re-raise validation errors as-is
        error_msg = f"Database error while fetching KPI {kpi_id}: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    finally:
        conn.close()

def create_execution_record(kpi_id: int, execution_params: Dict[str, Any]) -> int:
    """Create execution record in database - NO fallbacks."""
    logger.info(f"📝 Creating execution record for KPI {kpi_id}")

    # Validate inputs strictly
    if not isinstance(kpi_id, int) or kpi_id <= 0:
        raise ValueError(f"Invalid KPI ID: {kpi_id}")

    if not isinstance(execution_params, dict):
        raise ValueError("execution_params must be a dictionary")

    required_params = ['kg_name', 'select_schema', 'db_type', 'limit_records', 'use_llm', 'user_id', 'session_id']
    for param in required_params:
        if param not in execution_params:
            raise ValueError(f"Missing required execution parameter: {param}")
        if execution_params[param] is None:
            raise ValueError(f"Execution parameter {param} cannot be None")

    conn = get_kpi_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO kpi_execution_results
            (kpi_id, kg_name, select_schema, db_type, limit_records, use_llm,
             execution_status, user_id, session_id, created_at)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
        """, (
            kpi_id,
            str(execution_params['kg_name']),
            str(execution_params['select_schema']),
            str(execution_params['db_type']),
            int(execution_params['limit_records']),
            bool(execution_params['use_llm']),
            'pending',
            str(execution_params['user_id']),
            str(execution_params['session_id'])
        ))

        result = cursor.fetchone()
        if not result:
            raise RuntimeError("Failed to create execution record - no ID returned")

        execution_id = result[0]
        if not isinstance(execution_id, int) or execution_id <= 0:
            raise RuntimeError(f"Invalid execution ID returned: {execution_id}")

        conn.commit()
        logger.info(f"✅ Created execution record ID: {execution_id}")
        return execution_id

    except Exception as e:
        conn.rollback()
        error_msg = f"Failed to create execution record for KPI {kpi_id}: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    finally:
        conn.close()

# ==================== STRICT LLM SERVICE ====================
class StrictLLMService:
    """LLM service with NO fallbacks - all errors are raised."""

    def __init__(self):
        logger.info("🤖 Initializing strict LLM service...")

        # Validate OpenAI availability
        try:
            from openai import OpenAI
        except ImportError as e:
            raise ImportError("OpenAI library not available") from e

        # Validate API key
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")

        if OPENAI_API_KEY == "your-openai-api-key-here":
            raise ValueError("OPENAI_API_KEY must be set to a real API key")

        # Initialize client
        try:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI client: {e}") from e

        # Test the connection immediately
        self._test_connection()

        logger.info(f"✅ LLM Service initialized with model: {OPENAI_MODEL}")

    def _test_connection(self):
        """Test OpenAI connection immediately - NO fallbacks."""
        logger.info("🧪 Testing OpenAI connection...")

        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": "Test connection - respond with 'OK'"}],
                max_tokens=5,
                temperature=0
            )

            if not response.choices or not response.choices[0].message.content:
                raise RuntimeError("OpenAI returned empty response")

            content = response.choices[0].message.content.strip()
            logger.info(f"✅ OpenAI connection test successful: '{content}'")

        except Exception as e:
            error_msg = f"OpenAI connection test failed: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e

    def generate_sql(self, nl_definition: str) -> str:
        """Generate SQL from natural language - NO fallbacks."""
        if not nl_definition or not nl_definition.strip():
            raise ValueError("nl_definition cannot be empty")

        logger.info(f"🤖 Generating SQL for: {nl_definition}")

        prompt = f"""You are a SQL expert. Convert the following natural language query to SQL Server T-SQL.

Database Schema Context:
- Database: NewDQ (SQL Server)
- Main tables available:
  - hana_material_master (columns: MATERIAL, PRODUCT_TYPE, OPS_PLANNER, etc.)
  - ibp_product_master (columns: MATERIAL, PRODUCT_TYPE, etc.)
  - brz_lnd_RBP_GPU (columns: Material, Product_Line, etc.)
  - brz_lnd_OPS_EXCEL_GPU (columns: PLANNING_SKU, Product_Line, etc.)

Natural Language Query: {nl_definition}

Requirements:
1. Generate valid SQL Server T-SQL syntax
2. Use appropriate JOINs when multiple tables are involved
3. Include relevant columns in SELECT
4. Add appropriate WHERE clauses for filtering
5. Use proper table aliases
6. Return ONLY the SQL query, no explanations or markdown

SQL Query:"""

        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=OPENAI_TEMPERATURE,
                max_tokens=OPENAI_MAX_TOKENS
            )

            if not response.choices:
                raise RuntimeError("OpenAI returned no choices")

            if not response.choices[0].message.content:
                raise RuntimeError("OpenAI returned empty content")

            sql = response.choices[0].message.content.strip()

            # Clean up the SQL (remove markdown formatting if present)
            if sql.startswith('```sql'):
                sql = sql[6:].strip()
            if sql.startswith('```'):
                sql = sql[3:].strip()
            if sql.endswith('```'):
                sql = sql[:-3].strip()

            # Validate the generated SQL
            if not sql:
                raise RuntimeError("Generated SQL is empty after cleanup")

            if len(sql) < 10:
                raise RuntimeError(f"Generated SQL too short (likely invalid): {sql}")

            # Basic SQL validation
            sql_upper = sql.upper()
            if not sql_upper.startswith('SELECT'):
                raise RuntimeError(f"Generated SQL does not start with SELECT: {sql[:50]}...")

            logger.info(f"✅ Generated SQL ({len(sql)} characters)")
            logger.info(f"📝 SQL Preview: {sql[:100]}...")

            return sql

        except Exception as e:
            if isinstance(e, (ValueError, RuntimeError)):
                raise  # Re-raise validation errors as-is
            error_msg = f"Failed to generate SQL: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

# ==================== STRICT SQL EXECUTION ====================
def execute_sql_query(sql: str, limit: int) -> Dict[str, Any]:
    """Execute SQL query against source database - NO fallbacks."""
    if not sql or not sql.strip():
        raise ValueError("SQL query cannot be empty")

    if not isinstance(limit, int) or limit <= 0:
        raise ValueError(f"Limit must be a positive integer, got: {limit}")

    logger.info(f"🔍 Executing SQL query (limit: {limit})")
    logger.info(f"📝 SQL: {sql}")

    # Add TOP clause if not present (strict validation)
    sql_upper = sql.upper().strip()
    if not sql_upper.startswith('SELECT TOP'):
        if sql_upper.startswith('SELECT'):
            sql = sql.replace('SELECT', f'SELECT TOP {limit}', 1)
        else:
            raise ValueError(f"SQL must start with SELECT, got: {sql[:50]}...")

    conn = get_source_db_connection()
    start_time = time.time()

    try:
        cursor = conn.cursor()

        # Set query timeout
        cursor.execute(f"SET LOCK_TIMEOUT 30000")  # 30 seconds

        # Execute the main query
        cursor.execute(sql)

        # Get column information
        if not cursor.description:
            raise RuntimeError("Query returned no column information")

        columns = [desc[0] for desc in cursor.description]
        if not columns:
            raise RuntimeError("Query returned no columns")

        # Fetch results
        rows = cursor.fetchall()

        # Convert to list of dictionaries with strict type handling
        records = []
        for row_idx, row in enumerate(rows):
            if len(row) != len(columns):
                raise RuntimeError(f"Row {row_idx} has {len(row)} values but {len(columns)} columns")

            record = {}
            for col_idx, value in enumerate(row):
                column_name = columns[col_idx]

                # Handle different data types strictly
                if isinstance(value, datetime):
                    record[column_name] = value.isoformat()
                elif value is None:
                    record[column_name] = None
                else:
                    record[column_name] = value

            records.append(record)

        execution_time = (time.time() - start_time) * 1000

        logger.info(f"✅ Query executed successfully")
        logger.info(f"📊 Found {len(records)} records in {execution_time:.2f}ms")
        logger.info(f"📋 Columns: {', '.join(columns)}")

        return {
            'success': True,
            'records': records,
            'record_count': len(records),
            'columns': columns,
            'execution_time_ms': execution_time,
            'sql': sql
        }

    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        error_msg = f"SQL execution failed after {execution_time:.2f}ms: {e}"
        logger.error(error_msg)
        logger.error(f"Failed SQL: {sql}")

        return {
            'success': False,
            'error': str(e),
            'execution_time_ms': execution_time,
            'sql': sql,
            'records': [],
            'record_count': 0,
            'columns': []
        }

    finally:
        cursor.close()
        conn.close()

def update_execution_result(execution_id: int, result_data: Dict[str, Any]) -> None:
    """Update execution record with results - NO fallbacks."""
    if not isinstance(execution_id, int) or execution_id <= 0:
        raise ValueError(f"Invalid execution_id: {execution_id}")

    if not isinstance(result_data, dict):
        raise ValueError("result_data must be a dictionary")

    required_fields = ['execution_status', 'generated_sql', 'number_of_records', 'execution_time_ms']
    for field in required_fields:
        if field not in result_data:
            raise ValueError(f"Missing required field in result_data: {field}")

    logger.info(f"💾 Updating execution record {execution_id} with results")

    conn = get_kpi_db_connection()

    try:
        cursor = conn.cursor()

        # Prepare evidence data as JSON string
        evidence_data = result_data.get('evidence_data', [])
        evidence_json = json.dumps(evidence_data) if evidence_data else None

        cursor.execute("""
            UPDATE kpi_execution_results
            SET execution_status = ?,
                generated_sql = ?,
                number_of_records = ?,
                execution_time_ms = ?,
                evidence_data = ?,
                error_message = ?,
                completed_at = GETDATE()
            WHERE id = ?
        """, (
            str(result_data['execution_status']),
            str(result_data['generated_sql']),
            int(result_data['number_of_records']),
            float(result_data['execution_time_ms']),
            evidence_json,
            result_data.get('error_message'),
            execution_id
        ))

        if cursor.rowcount == 0:
            raise RuntimeError(f"No execution record found with ID {execution_id}")

        conn.commit()
        logger.info(f"✅ Updated execution record {execution_id}")

    except Exception as e:
        conn.rollback()
        error_msg = f"Failed to update execution record {execution_id}: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    finally:
        conn.close()

# ==================== MAIN EXECUTION FUNCTION - NO FALLBACKS ====================
def execute_kpi_strict(kpi_id: int, execution_params: Dict[str, Any]) -> Dict[str, Any]:
    """Main function to execute a KPI - NO fallbacks, all errors raised."""
    logger.info("="*80)
    logger.info(f"🚀 STARTING STRICT KPI EXECUTION")
    logger.info(f"📋 KPI ID: {kpi_id}")
    logger.info(f"⚙️ Parameters: {json.dumps(execution_params, indent=2)}")
    logger.info("="*80)

    start_time = time.time()
    execution_id = None

    try:
        # Step 1: Validate all inputs strictly
        logger.info("🔍 Step 1: Validating inputs...")
        if not isinstance(kpi_id, int) or kpi_id <= 0:
            raise ValueError(f"Invalid KPI ID: {kpi_id}")

        if not isinstance(execution_params, dict):
            raise ValueError("execution_params must be a dictionary")

        # Step 2: Get KPI definition (strict validation)
        logger.info("📋 Step 2: Fetching KPI definition...")
        kpi = get_kpi_definition(kpi_id)

        # Step 3: Create execution record (strict validation)
        logger.info("📝 Step 3: Creating execution record...")
        execution_id = create_execution_record(kpi_id, execution_params)

        # Step 4: Initialize LLM service (strict validation)
        logger.info("🤖 Step 4: Initializing LLM service...")
        llm_service = StrictLLMService()

        # Step 5: Generate SQL from NL definition (strict validation)
        logger.info("🔧 Step 5: Generating SQL from natural language...")
        generated_sql = llm_service.generate_sql(kpi['nl_definition'])

        # Step 6: Execute SQL query (strict validation)
        logger.info("🔍 Step 6: Executing SQL query...")
        query_result = execute_sql_query(
            generated_sql,
            execution_params['limit_records']
        )

        # Step 7: Prepare result data (strict validation)
        logger.info("📊 Step 7: Preparing results...")
        execution_time_ms = (time.time() - start_time) * 1000

        if query_result['success']:
            # Limit evidence data to first 10 records for storage
            evidence_data = query_result['records'][:10] if query_result['records'] else []

            result_data = {
                'execution_status': 'success',
                'generated_sql': query_result['sql'],
                'number_of_records': query_result['record_count'],
                'execution_time_ms': execution_time_ms,
                'evidence_data': evidence_data,
                'error_message': None
            }

            logger.info(f"✅ KPI execution completed successfully")
            logger.info(f"📊 Records found: {query_result['record_count']}")
            logger.info(f"⏱️ Total execution time: {execution_time_ms:.2f}ms")

        else:
            result_data = {
                'execution_status': 'failed',
                'generated_sql': query_result['sql'],
                'number_of_records': 0,
                'execution_time_ms': execution_time_ms,
                'evidence_data': [],
                'error_message': query_result['error']
            }

            logger.error(f"❌ KPI execution failed: {query_result['error']}")

        # Step 8: Update execution record (strict validation)
        logger.info("💾 Step 8: Updating execution record...")
        update_execution_result(execution_id, result_data)

        # Step 9: Return final result (strict validation)
        final_result = {
            'success': query_result['success'],
            'data': {
                'execution_id': execution_id,
                'kpi_name': kpi['name'],
                'kpi_alias_name': kpi['alias_name'],
                'execution_status': result_data['execution_status'],
                'generated_sql': result_data['generated_sql'],
                'number_of_records': result_data['number_of_records'],
                'execution_time_ms': execution_time_ms,
                'evidence_count': len(result_data['evidence_data']),
                'error_message': result_data.get('error_message')
            },
            'storage_type': 'mssql'
        }

        if not query_result['success']:
            final_result['error'] = query_result['error']

        logger.info("="*80)
        logger.info(f"🏁 STRICT KPI EXECUTION COMPLETED")
        logger.info(f"✅ Success: {final_result['success']}")
        logger.info(f"📊 Records: {final_result['data']['number_of_records']}")
        logger.info(f"⏱️ Time: {final_result['data']['execution_time_ms']:.2f}ms")
        logger.info("="*80)

        return final_result

    except Exception as e:
        execution_time_ms = (time.time() - start_time) * 1000
        error_msg = f"KPI execution failed: {e}"
        logger.error(f"❌ {error_msg}")

        # Try to update execution record with error if we have an execution_id
        if execution_id:
            try:
                error_result_data = {
                    'execution_status': 'failed',
                    'generated_sql': '',
                    'number_of_records': 0,
                    'execution_time_ms': execution_time_ms,
                    'evidence_data': [],
                    'error_message': str(e)
                }
                update_execution_result(execution_id, error_result_data)
            except Exception as update_error:
                logger.error(f"Failed to update execution record with error: {update_error}")

        # Re-raise the original error - NO fallbacks
        raise RuntimeError(error_msg) from e

# ==================== COMMAND LINE INTERFACE ====================
def main():
    """Main function for command line execution - NO fallbacks."""
    print("🚀 Robust Standalone KPI Executor (NO FALLBACKS)")
    print("=" * 60)

    try:
        # Step 1: Validate configuration
        validate_configuration()

        # Step 2: Check dependencies
        check_dependencies()

        print(f"📋 Executing KPI ID: {KPI_ID}")
        print(f"🔧 Configuration:")
        print(f"   - OpenAI Model: {OPENAI_MODEL}")
        print(f"   - Temperature: {OPENAI_TEMPERATURE}")
        print(f"   - KPI Database: {DB_CONFIG['host']}/{DB_CONFIG['database']}")
        print(f"   - Source Database: {SOURCE_DB_CONFIG['host']}/{SOURCE_DB_CONFIG['database']}")
        print(f"   - Knowledge Graph: {EXECUTION_PARAMS['kg_name']}")
        print(f"   - Schema: {EXECUTION_PARAMS['select_schema']}")
        print(f"   - Limit: {EXECUTION_PARAMS['limit_records']}")
        print()

        # Step 3: Execute the KPI
        result = execute_kpi_strict(KPI_ID, EXECUTION_PARAMS)

        # Step 4: Print results
        print("\n" + "="*60)
        print("📊 EXECUTION RESULTS")
        print("="*60)
        print(json.dumps(result, indent=2, default=str))

        # Step 5: Exit with appropriate code
        if result['success']:
            print("\n✅ KPI execution completed successfully!")
            sys.exit(0)
        else:
            print(f"\n❌ KPI execution failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️ Execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logger.exception("Fatal error during execution")
        sys.exit(1)

if __name__ == '__main__':
    main()
