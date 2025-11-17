#!/usr/bin/env python3
"""
Standalone KPI Executor Script

This script mimics the API call to /api/v1/landing-kpi-mssql/kpis/19/execute
and can be run independently outside the project.

Usage:
    python kpi_executor_standalone.py \
        --openai-key "your-openai-key" \
        --temperature 0.0 \
        --kg-name "default" \
        --db-host "localhost" \
        --db-port 1433 \
        --db-name "KPI_Analytics" \
        --db-user "username" \
        --db-password "password" \
        --kpi-id 19 \
        --select-schema "newdqschemanov" \
        --limit-records 1000
"""

import argparse
import logging
import sys
import time
import json
from typing import Dict, Any, Optional
import pyodbc
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('kpi_execution.log')
    ]
)
logger = logging.getLogger(__name__)


class StandaloneKPIExecutor:
    """Standalone KPI Executor that mimics the API functionality."""
    
    def __init__(self, openai_key: str, temperature: float = 0.0):
        """Initialize the executor with OpenAI configuration."""
        self.openai_client = OpenAI(api_key=openai_key)
        self.temperature = temperature
        logger.info(f"✅ Initialized OpenAI client with temperature: {temperature}")
    
    def get_kpi_definition(self, kpi_id: int, db_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieve KPI definition from database."""
        logger.info(f"🔍 STEP 1: Retrieving KPI definition for ID: {kpi_id}")
        
        try:
            # Build connection string
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={db_config['host']},{db_config['port']};"
                f"DATABASE={db_config['database']};"
                f"UID={db_config['username']};"
                f"PWD={db_config['password']};"
                f"TrustServerCertificate=yes;"
            )
            
            logger.info(f"   Connecting to: {db_config['host']}:{db_config['port']}/{db_config['database']}")
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, alias_name, group_name, description, nl_definition,
                       created_at, updated_at, created_by, is_active
                FROM kpi_definitions 
                WHERE id = ?
            """, (kpi_id,))
            
            row = cursor.fetchone()
            if row:
                kpi = {
                    'id': row[0],
                    'name': row[1],
                    'alias_name': row[2],
                    'group_name': row[3],
                    'description': row[4],
                    'nl_definition': row[5],
                    'created_at': row[6].isoformat() if row[6] else None,
                    'updated_at': row[7].isoformat() if row[7] else None,
                    'created_by': row[8],
                    'is_active': bool(row[9])
                }
                logger.info(f"✅ Found KPI: {kpi['name']}")
                logger.info(f"   Description: {kpi['description']}")
                logger.info(f"   NL Definition: {kpi['nl_definition']}")
                return kpi
            else:
                logger.error(f"❌ KPI with ID {kpi_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error retrieving KPI definition: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()
    
    def create_execution_record(self, kpi_id: int, execution_params: Dict[str, Any], 
                              db_config: Dict[str, Any]) -> Optional[int]:
        """Create execution record in database."""
        logger.info(f"📝 STEP 2: Creating execution record for KPI ID: {kpi_id}")
        
        try:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={db_config['host']},{db_config['port']};"
                f"DATABASE={db_config['database']};"
                f"UID={db_config['username']};"
                f"PWD={db_config['password']};"
                f"TrustServerCertificate=yes;"
            )
            
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO kpi_execution_results
                (kpi_id, kg_name, select_schema, db_type, limit_records, use_llm,
                 execution_status, user_id, session_id)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                kpi_id,
                execution_params.get('kg_name'),
                execution_params.get('select_schema'),
                execution_params.get('db_type', 'sqlserver'),
                execution_params.get('limit_records', 1000),
                execution_params.get('use_llm', True),
                'pending',
                execution_params.get('user_id', 'standalone_script'),
                execution_params.get('session_id', f'standalone_{int(time.time())}')
            ))
            
            execution_id = cursor.fetchone()[0]
            conn.commit()
            logger.info(f"✅ Created execution record ID: {execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"❌ Error creating execution record: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def generate_sql_with_llm(self, nl_definition: str, kg_name: str, select_schema: str) -> str:
        """Generate SQL from natural language definition using OpenAI."""
        logger.info(f"🤖 STEP 3: Generating SQL using LLM")
        logger.info(f"   NL Definition: {nl_definition}")
        logger.info(f"   KG Name: {kg_name}")
        logger.info(f"   Schema: {select_schema}")

        try:
            # Create a comprehensive prompt for SQL generation
            prompt = f"""
You are an expert SQL generator. Convert the following natural language definition into a SQL Server query.

Natural Language Definition: {nl_definition}
Knowledge Graph: {kg_name}
Schema: {select_schema}

Requirements:
1. Generate valid SQL Server syntax
2. Use appropriate table names and column names
3. Include proper JOIN conditions if multiple tables are involved
4. Use TOP clause for limiting results (SQL Server syntax)
5. Return only the SQL query without explanations

SQL Query:
"""

            logger.info(f"   Sending request to OpenAI...")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert SQL generator. Generate only valid SQL Server queries without explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=1000
            )

            generated_sql = response.choices[0].message.content.strip()

            # Clean up the SQL (remove markdown formatting if present)
            if generated_sql.startswith('```sql'):
                generated_sql = generated_sql[6:]
            if generated_sql.endswith('```'):
                generated_sql = generated_sql[:-3]
            generated_sql = generated_sql.strip()

            logger.info(f"✅ Generated SQL successfully")
            logger.info(f"   SQL Length: {len(generated_sql)} characters")
            logger.info(f"   SQL Preview: {generated_sql[:200]}...")

            return generated_sql

        except Exception as e:
            logger.error(f"❌ Error generating SQL with LLM: {e}")
            raise

    def execute_sql_query(self, sql: str, db_config: Dict[str, Any], limit_records: int) -> Dict[str, Any]:
        """Execute the generated SQL query against the database."""
        logger.info(f"🗃️ STEP 4: Executing SQL query")
        logger.info(f"   Database: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        logger.info(f"   Limit: {limit_records} records")

        start_time = time.time()

        try:
            # Add TOP clause if not present and limit is specified
            if limit_records and limit_records > 0:
                sql_upper = sql.upper()
                if "SELECT" in sql_upper and "TOP" not in sql_upper:
                    if "SELECT DISTINCT" in sql_upper:
                        sql = sql.replace("SELECT DISTINCT", f"SELECT DISTINCT TOP {limit_records}", 1)
                    else:
                        sql = sql.replace("SELECT", f"SELECT TOP {limit_records}", 1)

            # Build connection string for data database (not KPI database)
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={db_config['data_host']},{db_config['data_port']};"
                f"DATABASE={db_config['data_database']};"
                f"UID={db_config['data_username']};"
                f"PWD={db_config['data_password']};"
                f"TrustServerCertificate=yes;"
            )

            logger.info(f"   Connecting to data database: {db_config['data_host']}:{db_config['data_port']}/{db_config['data_database']}")
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            logger.info(f"   Executing SQL query...")
            logger.info(f"   Final SQL: {sql}")

            cursor.execute(sql)

            # Fetch column names
            columns = [column[0] for column in cursor.description]

            # Fetch all rows
            rows = cursor.fetchall()

            # Convert rows to list of dictionaries
            records = []
            for row in rows:
                record = {}
                for i, value in enumerate(row):
                    # Handle different data types
                    if hasattr(value, 'isoformat'):  # datetime objects
                        record[columns[i]] = value.isoformat()
                    else:
                        record[columns[i]] = value
                records.append(record)

            execution_time_ms = (time.time() - start_time) * 1000

            logger.info(f"✅ Query executed successfully")
            logger.info(f"   Records returned: {len(records)}")
            logger.info(f"   Columns: {len(columns)}")
            logger.info(f"   Execution time: {execution_time_ms:.2f}ms")

            return {
                'success': True,
                'sql': sql,
                'records': records,
                'record_count': len(records),
                'columns': columns,
                'execution_time_ms': execution_time_ms
            }

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            logger.error(f"❌ Error executing SQL query: {e}")
            return {
                'success': False,
                'sql': sql,
                'error': str(e),
                'execution_time_ms': execution_time_ms
            }
        finally:
            if 'conn' in locals():
                conn.close()

    def update_execution_result(self, execution_id: int, result_data: Dict[str, Any],
                              db_config: Dict[str, Any]) -> bool:
        """Update execution record with results."""
        logger.info(f"💾 STEP 5: Updating execution record ID: {execution_id}")

        try:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={db_config['host']},{db_config['port']};"
                f"DATABASE={db_config['database']};"
                f"UID={db_config['username']};"
                f"PWD={db_config['password']};"
                f"TrustServerCertificate=yes;"
            )

            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # Prepare result data
            execution_status = 'completed' if result_data['success'] else 'failed'
            number_of_records = result_data.get('record_count', 0)
            execution_time_ms = result_data.get('execution_time_ms', 0)
            generated_sql = result_data.get('sql', '')
            error_message = result_data.get('error', None)
            result_json = json.dumps(result_data.get('records', [])[:100])  # Store first 100 records

            cursor.execute("""
                UPDATE kpi_execution_results
                SET execution_status = ?,
                    number_of_records = ?,
                    execution_time_ms = ?,
                    generated_sql = ?,
                    result_data = ?,
                    error_message = ?,
                    execution_timestamp = GETDATE()
                WHERE id = ?
            """, (
                execution_status,
                number_of_records,
                execution_time_ms,
                generated_sql,
                result_json,
                error_message,
                execution_id
            ))

            conn.commit()
            logger.info(f"✅ Updated execution record successfully")
            logger.info(f"   Status: {execution_status}")
            logger.info(f"   Records: {number_of_records}")
            logger.info(f"   Execution time: {execution_time_ms:.2f}ms")

            return True

        except Exception as e:
            logger.error(f"❌ Error updating execution record: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    def execute_kpi(self, kpi_id: int, execution_params: Dict[str, Any],
                   db_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute KPI end-to-end."""
        logger.info(f"🚀 Starting KPI execution for ID: {kpi_id}")
        logger.info(f"   Parameters: {execution_params}")

        overall_start_time = time.time()

        try:
            # Step 1: Get KPI definition
            kpi = self.get_kpi_definition(kpi_id, db_config)
            if not kpi:
                return {'success': False, 'error': 'KPI not found'}

            # Step 2: Create execution record
            execution_id = self.create_execution_record(kpi_id, execution_params, db_config)
            if not execution_id:
                return {'success': False, 'error': 'Failed to create execution record'}

            # Step 3: Generate SQL using LLM
            generated_sql = self.generate_sql_with_llm(
                kpi['nl_definition'],
                execution_params.get('kg_name', 'default'),
                execution_params.get('select_schema', 'newdqschemanov')
            )

            # Step 4: Execute SQL query
            query_result = self.execute_sql_query(
                generated_sql,
                db_config,
                execution_params.get('limit_records', 1000)
            )

            # Step 5: Update execution record
            self.update_execution_result(execution_id, query_result, db_config)

            overall_execution_time = (time.time() - overall_start_time) * 1000

            # Prepare final result
            final_result = {
                'success': query_result['success'],
                'kpi_id': kpi_id,
                'execution_id': execution_id,
                'kpi_name': kpi['name'],
                'kpi_description': kpi['description'],
                'nl_definition': kpi['nl_definition'],
                'generated_sql': query_result.get('sql', ''),
                'record_count': query_result.get('record_count', 0),
                'execution_time_ms': query_result.get('execution_time_ms', 0),
                'overall_execution_time_ms': overall_execution_time,
                'records': query_result.get('records', []),
                'columns': query_result.get('columns', []),
                'execution_params': execution_params
            }

            if not query_result['success']:
                final_result['error'] = query_result.get('error', 'Unknown error')

            logger.info(f"🎉 KPI execution completed!")
            logger.info(f"   Success: {final_result['success']}")
            logger.info(f"   Records: {final_result['record_count']}")
            logger.info(f"   Total time: {overall_execution_time:.2f}ms")

            return final_result

        except Exception as e:
            logger.error(f"❌ KPI execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'kpi_id': kpi_id,
                'execution_params': execution_params
            }


def main():
    """Main function to handle command line arguments and execute KPI."""
    parser = argparse.ArgumentParser(
        description='Standalone KPI Executor - Mimics API call to /api/v1/landing-kpi-mssql/kpis/19/execute',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic execution
    python kpi_executor_standalone.py \\
        --openai-key "sk-..." \\
        --kg-name "default" \\
        --db-host "localhost" \\
        --db-user "username" \\
        --db-password "password" \\
        --kpi-id 19

    # With custom parameters
    python kpi_executor_standalone.py \\
        --openai-key "sk-..." \\
        --temperature 0.1 \\
        --kg-name "KG_101" \\
        --db-host "server.example.com" \\
        --db-port 1433 \\
        --db-name "KPI_Analytics" \\
        --db-user "kpi_user" \\
        --db-password "secure_password" \\
        --data-host "data-server.example.com" \\
        --data-db-name "NewDQ" \\
        --data-user "data_user" \\
        --data-password "data_password" \\
        --kpi-id 19 \\
        --select-schema "newdqschemanov" \\
        --limit-records 500
        """
    )

    # Required arguments
    parser.add_argument('--openai-key', required=True, help='OpenAI API key')
    parser.add_argument('--kg-name', required=True, help='Knowledge graph name')
    parser.add_argument('--db-host', required=True, help='KPI database host')
    parser.add_argument('--db-user', required=True, help='KPI database username')
    parser.add_argument('--db-password', required=True, help='KPI database password')
    parser.add_argument('--kpi-id', type=int, required=True, help='KPI ID to execute')

    # Optional arguments with defaults
    parser.add_argument('--temperature', type=float, default=0.0, help='OpenAI temperature (default: 0.0)')
    parser.add_argument('--db-port', type=int, default=1433, help='KPI database port (default: 1433)')
    parser.add_argument('--db-name', default='KPI_Analytics', help='KPI database name (default: KPI_Analytics)')
    parser.add_argument('--select-schema', default='newdqschemanov', help='Schema to query (default: newdqschemanov)')
    parser.add_argument('--limit-records', type=int, default=1000, help='Maximum records to return (default: 1000)')

    # Data database arguments (defaults to same as KPI database)
    parser.add_argument('--data-host', help='Data database host (defaults to --db-host)')
    parser.add_argument('--data-port', type=int, help='Data database port (defaults to --db-port)')
    parser.add_argument('--data-db-name', help='Data database name (defaults to --db-name)')
    parser.add_argument('--data-user', help='Data database username (defaults to --db-user)')
    parser.add_argument('--data-password', help='Data database password (defaults to --db-password)')

    # Output options
    parser.add_argument('--output-file', help='Save results to JSON file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Prepare database configuration
    db_config = {
        'host': args.db_host,
        'port': args.db_port,
        'database': args.db_name,
        'username': args.db_user,
        'password': args.db_password,
        # Data database configuration (defaults to KPI database if not specified)
        'data_host': args.data_host or args.db_host,
        'data_port': args.data_port or args.db_port,
        'data_database': args.data_db_name or args.db_name,
        'data_username': args.data_user or args.db_user,
        'data_password': args.data_password or args.db_password,
    }

    # Prepare execution parameters
    execution_params = {
        'kg_name': args.kg_name,
        'select_schema': args.select_schema,
        'limit_records': args.limit_records,
        'db_type': 'sqlserver',
        'use_llm': True,
        'user_id': 'standalone_script',
        'session_id': f'standalone_{int(time.time())}'
    }

    logger.info("="*80)
    logger.info("🚀 STANDALONE KPI EXECUTOR STARTED")
    logger.info("="*80)
    logger.info(f"KPI ID: {args.kpi_id}")
    logger.info(f"KG Name: {args.kg_name}")
    logger.info(f"Schema: {args.select_schema}")
    logger.info(f"Limit: {args.limit_records}")
    logger.info(f"Temperature: {args.temperature}")
    logger.info(f"KPI DB: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    logger.info(f"Data DB: {db_config['data_host']}:{db_config['data_port']}/{db_config['data_database']}")
    logger.info("="*80)

    try:
        # Initialize executor
        executor = StandaloneKPIExecutor(args.openai_key, args.temperature)

        # Execute KPI
        result = executor.execute_kpi(args.kpi_id, execution_params, db_config)

        # Print results
        logger.info("="*80)
        logger.info("📊 EXECUTION RESULTS")
        logger.info("="*80)
        logger.info(f"Success: {result['success']}")

        if result['success']:
            logger.info(f"KPI Name: {result.get('kpi_name', 'N/A')}")
            logger.info(f"Description: {result.get('kpi_description', 'N/A')}")
            logger.info(f"NL Definition: {result.get('nl_definition', 'N/A')}")
            logger.info(f"Records Returned: {result.get('record_count', 0)}")
            logger.info(f"Execution Time: {result.get('execution_time_ms', 0):.2f}ms")
            logger.info(f"Overall Time: {result.get('overall_execution_time_ms', 0):.2f}ms")
            logger.info(f"Generated SQL: {result.get('generated_sql', 'N/A')[:200]}...")

            if result.get('records'):
                logger.info(f"Sample Records (first 3):")
                for i, record in enumerate(result['records'][:3]):
                    logger.info(f"  Record {i+1}: {record}")
        else:
            logger.error(f"Error: {result.get('error', 'Unknown error')}")

        # Save to file if requested
        if args.output_file:
            with open(args.output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"💾 Results saved to: {args.output_file}")

        logger.info("="*80)
        logger.info("✅ EXECUTION COMPLETED")
        logger.info("="*80)

        # Exit with appropriate code
        sys.exit(0 if result['success'] else 1)

    except KeyboardInterrupt:
        logger.info("❌ Execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
