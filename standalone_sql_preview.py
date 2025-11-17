#!/usr/bin/env python3
"""
Standalone SQL Preview Script

This script generates SQL from natural language definitions using OpenAI,
similar to the SQL preview functionality in the API, but without executing the queries.

Configuration:
    Update the DEFAULT_CONFIG section below with your values, then run:
    python standalone_sql_preview.py

Command Line Usage (optional):
    python standalone_sql_preview.py \
        --nl-definition "get products from hana_material_master where OPS_PLANNER is missing" \
        --kg-name "KG_Test_001" \
        --select-schema "newdqnov7" \
        --openai-key "your-openai-key" \
        --temperature 0 \
        --db-host "localhost" \
        --db-name "NewDQ" \
        --db-user "username" \
        --db-password "password" \
        --use-llm \
        --verbose
"""

import argparse
import logging
import sys
import time
import json
from typing import Dict, Any, Optional, List
import pyodbc
from openai import OpenAI

# =============================================================================
# DEFAULT CONFIGURATION - UPDATE THESE VALUES
# =============================================================================

DEFAULT_CONFIG = {
    # REQUIRED SETTINGS - Update these with your values
    'nl_definition': 'get products from hana_material_master where OPS_PLANNER is missing',
    'kg_name': 'KG_Test_001',
    'select_schema': 'newdqnov7',
    'openai_key': 'test',
    'db_host': 'DESKTOP-41O1AL9\\LOCALHOST',
    'db_user': 'mithun',
    'db_password': 'mithun123',

    # OPTIONAL SETTINGS - Modify as needed
    'temperature': 0.0,
    'db_port': 1433,
    'db_name': 'NewDQ',
    'use_llm': True,
    'verbose': True,
    'output_file': None,  # Set to filename to save results, e.g., 'sql_preview.json'
}

# =============================================================================
# SCRIPT IMPLEMENTATION
# =============================================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('sql_preview.log')
    ]
)
logger = logging.getLogger(__name__)


class QueryIntent:
    """Simple QueryIntent class to hold parsed query information."""
    
    def __init__(self, definition: str, query_type: str = "data", operation: str = "select"):
        self.definition = definition
        self.query_type = query_type
        self.operation = operation
        self.source_table = None
        self.target_table = None
        self.join_columns = []
        self.confidence = 0.8
        self.additional_columns = []


class StandaloneSQLPreview:
    """Standalone SQL Preview generator that mimics the API functionality."""
    
    def __init__(self, openai_key: str, temperature: float = 0.0):
        """Initialize the SQL preview generator with OpenAI configuration."""
        self.openai_client = OpenAI(api_key=openai_key)
        self.temperature = temperature
        logger.info(f"✅ Initialized OpenAI client with temperature: {temperature}")
    
    def get_database_schema(self, db_config: Dict[str, Any], select_schema: str) -> Dict[str, Any]:
        """Retrieve database schema information."""
        logger.info(f"🔍 STEP 1: Retrieving database schema information")
        logger.info(f"   Database: {db_config['host']}\\{db_config['database']}")
        logger.info(f"   Schema: {select_schema}")
        
        try:
            # Build connection string
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={db_config['host']};"
                f"DATABASE={db_config['database']};"
                f"UID={db_config['username']};"
                f"PWD={db_config['password']};"
                f"TrustServerCertificate=yes;"
            )
            
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            # Get table and column information
            schema_info = {
                "schema_name": select_schema,
                "tables": {}
            }
            
            # Query to get tables and columns
            cursor.execute("""
                SELECT 
                    t.TABLE_NAME,
                    c.COLUMN_NAME,
                    c.DATA_TYPE,
                    c.IS_NULLABLE,
                    c.COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.TABLES t
                LEFT JOIN INFORMATION_SCHEMA.COLUMNS c ON t.TABLE_NAME = c.TABLE_NAME
                WHERE t.TABLE_SCHEMA = ? OR t.TABLE_SCHEMA = 'dbo'
                ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
            """, (select_schema,))
            
            rows = cursor.fetchall()
            
            for row in rows:
                table_name = row[0]
                column_name = row[1]
                data_type = row[2]
                is_nullable = row[3]
                column_default = row[4]
                
                if table_name not in schema_info["tables"]:
                    schema_info["tables"][table_name] = {
                        "columns": []
                    }
                
                if column_name:  # Some tables might not have columns in the result
                    schema_info["tables"][table_name]["columns"].append({
                        "name": column_name,
                        "type": data_type,
                        "nullable": is_nullable == "YES",
                        "default": column_default
                    })
            
            logger.info(f"✅ Retrieved schema information")
            logger.info(f"   Tables found: {len(schema_info['tables'])}")
            
            # Log table information
            for table_name, table_info in schema_info["tables"].items():
                logger.info(f"   Table: {table_name} ({len(table_info['columns'])} columns)")
            
            return schema_info
            
        except Exception as e:
            logger.error(f"❌ Error retrieving database schema: {e}")
            return {"schema_name": select_schema, "tables": {}}
        finally:
            if 'conn' in locals():
                conn.close()
    
    def parse_nl_definition(self, nl_definition: str, schema_info: Dict[str, Any], use_llm: bool = True) -> QueryIntent:
        """Parse natural language definition into QueryIntent."""
        logger.info(f"🧠 STEP 2: Parsing natural language definition")
        logger.info(f"   Definition: {nl_definition}")
        logger.info(f"   Use LLM: {use_llm}")
        
        if use_llm:
            return self._parse_with_llm(nl_definition, schema_info)
        else:
            return self._parse_with_rules(nl_definition)
    
    def _parse_with_llm(self, definition: str, schema_info: Dict[str, Any]) -> QueryIntent:
        """Parse using LLM with schema context."""
        try:
            # Build schema context for the prompt
            schema_context = f"Schema: {schema_info['schema_name']}\n"
            schema_context += "Available tables and columns:\n"
            
            for table_name, table_info in schema_info["tables"].items():
                schema_context += f"- {table_name}: "
                column_names = [col["name"] for col in table_info["columns"]]
                schema_context += ", ".join(column_names[:10])  # Limit to first 10 columns
                if len(column_names) > 10:
                    schema_context += f" (and {len(column_names) - 10} more)"
                schema_context += "\n"
            
            prompt = f"""
You are an expert SQL analyst. Parse the following natural language query and extract structured information.

{schema_context}

Natural Language Query: {definition}

Analyze the query and return a JSON object with the following structure:
{{
    "query_type": "comparison|filter|aggregation|data",
    "operation": "select|count|sum|avg|join",
    "source_table": "primary table name",
    "target_table": "secondary table name if join needed",
    "confidence": 0.0-1.0,
    "explanation": "brief explanation of the query intent"
}}

Focus on identifying:
1. The main table(s) involved
2. The type of operation (SELECT, COUNT, etc.)
3. Whether it's a comparison between tables or a filter on one table
4. Your confidence in the interpretation

Return only valid JSON.
"""
            
            logger.info(f"   Sending request to OpenAI...")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert SQL analyst. Parse natural language queries and return structured JSON information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean up JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON response
            parsed_data = json.loads(response_text)
            
            # Create QueryIntent object
            intent = QueryIntent(definition, parsed_data.get("query_type", "data"), parsed_data.get("operation", "select"))
            intent.source_table = parsed_data.get("source_table")
            intent.target_table = parsed_data.get("target_table")
            intent.confidence = parsed_data.get("confidence", 0.8)
            
            logger.info(f"✅ Parsed with LLM successfully")
            logger.info(f"   Query Type: {intent.query_type}")
            logger.info(f"   Operation: {intent.operation}")
            logger.info(f"   Source Table: {intent.source_table}")
            logger.info(f"   Target Table: {intent.target_table}")
            logger.info(f"   Confidence: {intent.confidence}")
            logger.info(f"   Explanation: {parsed_data.get('explanation', 'N/A')}")
            
            return intent
            
        except Exception as e:
            logger.error(f"❌ Error parsing with LLM: {e}")
            # Fallback to rule-based parsing
            return self._parse_with_rules(definition)

    def _parse_with_rules(self, definition: str) -> QueryIntent:
        """Simple rule-based parsing as fallback."""
        logger.info(f"   Using rule-based parsing...")

        definition_lower = definition.lower()

        # Determine query type and operation
        if "missing" in definition_lower or "not in" in definition_lower or "null" in definition_lower:
            query_type = "filter"
            operation = "select"
        elif "count" in definition_lower:
            query_type = "aggregation"
            operation = "count"
        elif "sum" in definition_lower:
            query_type = "aggregation"
            operation = "sum"
        else:
            query_type = "data"
            operation = "select"

        # Try to extract table name
        source_table = None
        words = definition.split()
        for i, word in enumerate(words):
            if word.lower() in ["from", "in"] and i + 1 < len(words):
                source_table = words[i + 1].strip(".,;")
                break

        intent = QueryIntent(definition, query_type, operation)
        intent.source_table = source_table
        intent.confidence = 0.6  # Lower confidence for rule-based parsing

        logger.info(f"✅ Parsed with rules")
        logger.info(f"   Query Type: {intent.query_type}")
        logger.info(f"   Operation: {intent.operation}")
        logger.info(f"   Source Table: {intent.source_table}")
        logger.info(f"   Confidence: {intent.confidence}")

        return intent

    def generate_sql_with_llm(self, intent: QueryIntent, schema_info: Dict[str, Any], db_type: str = "sqlserver") -> str:
        """Generate SQL from QueryIntent using OpenAI."""
        logger.info(f"🤖 STEP 3: Generating SQL using LLM")
        logger.info(f"   Intent: {intent.definition}")
        logger.info(f"   Source Table: {intent.source_table}")
        logger.info(f"   Database Type: {db_type}")

        try:
            # Build comprehensive schema context
            schema_context = f"Database: {db_type.upper()}\n"
            schema_context += f"Schema: {schema_info['schema_name']}\n\n"
            schema_context += "Available tables and their columns:\n"

            for table_name, table_info in schema_info["tables"].items():
                schema_context += f"\nTable: {table_name}\n"
                for col in table_info["columns"]:
                    schema_context += f"  - {col['name']} ({col['type']})\n"

            # Create specialized prompt based on query type
            if intent.query_type == "filter" and ("missing" in intent.definition.lower() or "null" in intent.definition.lower()):
                prompt_type = "Generate a SQL query to find records where specific columns are NULL or missing."
            elif intent.query_type == "aggregation":
                prompt_type = f"Generate a SQL query to perform {intent.operation.upper()} aggregation."
            else:
                prompt_type = "Generate a SQL query to retrieve data."

            prompt = f"""
You are an expert SQL generator for {db_type.upper()} database.

{schema_context}

Task: {prompt_type}
Natural Language Request: {intent.definition}

Requirements:
1. Generate valid {db_type.upper()} syntax
2. Use proper table and column names from the schema above
3. Handle NULL/missing values appropriately (use IS NULL for missing values)
4. Use appropriate WHERE clauses for filtering
5. Include proper JOIN conditions if multiple tables are involved
6. For SQL Server, use TOP clause for limiting results
7. Return only the SQL query without explanations or markdown formatting

SQL Query:
"""

            logger.info(f"   Sending SQL generation request to OpenAI...")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert {db_type.upper()} SQL generator. Generate only valid SQL queries without explanations."
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
            elif generated_sql.startswith('```'):
                generated_sql = generated_sql[3:]
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

    def enhance_sql(self, sql: str, intent: QueryIntent) -> Dict[str, Any]:
        """Apply enhancements to the generated SQL."""
        logger.info(f"🔧 STEP 4: Applying SQL enhancements")

        enhanced_sql = sql
        enhancements_applied = []

        # Check for material master enhancement
        if "hana_material_master" in sql.lower():
            logger.info(f"   Detected hana_material_master table usage")

            # Check if OPS_PLANNER column is missing and should be added
            if "ops_planner" not in sql.lower() and ("missing" in intent.definition.lower() or "planner" in intent.definition.lower()):
                logger.info(f"   Adding OPS_PLANNER column enhancement")

                # Simple enhancement: ensure OPS_PLANNER is in SELECT if not present
                if "SELECT" in enhanced_sql.upper() and "ops_planner" not in enhanced_sql.lower():
                    # Find the SELECT clause and add OPS_PLANNER
                    select_pos = enhanced_sql.upper().find("SELECT")
                    from_pos = enhanced_sql.upper().find("FROM")

                    if select_pos != -1 and from_pos != -1:
                        select_clause = enhanced_sql[select_pos:from_pos].strip()
                        if not select_clause.endswith("*"):
                            # Add OPS_PLANNER to the select list
                            enhanced_sql = enhanced_sql[:from_pos] + ", OPS_PLANNER " + enhanced_sql[from_pos:]
                            enhancements_applied.append("Added OPS_PLANNER column to SELECT")

            enhancements_applied.append("Material master table detected")

        # Check for ops_planner enhancement
        if "ops_planner" in enhanced_sql.lower():
            enhancements_applied.append("OPS_PLANNER column included")

        logger.info(f"✅ SQL enhancements completed")
        if enhancements_applied:
            for enhancement in enhancements_applied:
                logger.info(f"   - {enhancement}")
        else:
            logger.info(f"   - No enhancements applied")

        return {
            "original_sql": sql,
            "enhanced_sql": enhanced_sql,
            "enhancements_applied": enhancements_applied,
            "material_master_detected": "hana_material_master" in sql.lower(),
            "ops_planner_included": "ops_planner" in enhanced_sql.lower()
        }

    def generate_sql_preview(self, nl_definition: str, kg_name: str, select_schema: str,
                           db_config: Dict[str, Any], use_llm: bool = True) -> Dict[str, Any]:
        """Generate SQL preview from natural language definition."""
        logger.info(f"🚀 Starting SQL preview generation")
        logger.info(f"   NL Definition: {nl_definition}")
        logger.info(f"   KG Name: {kg_name}")
        logger.info(f"   Schema: {select_schema}")
        logger.info(f"   Use LLM: {use_llm}")

        overall_start_time = time.time()

        try:
            # Step 1: Get database schema
            schema_info = self.get_database_schema(db_config, select_schema)

            # Step 2: Parse natural language definition
            intent = self.parse_nl_definition(nl_definition, schema_info, use_llm)

            # Step 3: Generate SQL
            generated_sql = self.generate_sql_with_llm(intent, schema_info, "sqlserver")

            # Step 4: Apply enhancements
            enhancement_result = self.enhance_sql(generated_sql, intent)

            overall_execution_time = (time.time() - overall_start_time) * 1000

            # Prepare final result
            result = {
                'success': True,
                'nl_definition': nl_definition,
                'kg_name': kg_name,
                'select_schema': select_schema,
                'use_llm': use_llm,
                'query_intent': {
                    'definition': intent.definition,
                    'query_type': intent.query_type,
                    'operation': intent.operation,
                    'source_table': intent.source_table,
                    'target_table': intent.target_table,
                    'confidence': intent.confidence
                },
                'generated_sql': enhancement_result['enhanced_sql'],
                'original_sql': enhancement_result['original_sql'],
                'enhancements': {
                    'applied': enhancement_result['enhancements_applied'],
                    'material_master_detected': enhancement_result['material_master_detected'],
                    'ops_planner_included': enhancement_result['ops_planner_included']
                },
                'schema_info': {
                    'schema_name': schema_info['schema_name'],
                    'tables_count': len(schema_info['tables']),
                    'tables': list(schema_info['tables'].keys())
                },
                'execution_time_ms': overall_execution_time
            }

            logger.info(f"🎉 SQL preview generation completed!")
            logger.info(f"   Success: {result['success']}")
            logger.info(f"   Query Type: {intent.query_type}")
            logger.info(f"   Source Table: {intent.source_table}")
            logger.info(f"   Confidence: {intent.confidence}")
            logger.info(f"   Total time: {overall_execution_time:.2f}ms")

            return result

        except Exception as e:
            logger.error(f"❌ SQL preview generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'nl_definition': nl_definition,
                'kg_name': kg_name,
                'select_schema': select_schema,
                'use_llm': use_llm
            }


def main():
    """Main function to handle command line arguments and generate SQL preview."""
    parser = argparse.ArgumentParser(
        description='Standalone SQL Preview Generator - Generate SQL from natural language without execution',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration:
    Update the DEFAULT_CONFIG section at the top of this file with your values.
    Then simply run: python standalone_sql_preview.py

Command Line Override (optional):
    You can still override any default value using command line arguments:

    python standalone_sql_preview.py \\
        --nl-definition "count products by category" \\
        --kg-name "KG_Production" \\
        --temperature 0.1 \\
        --output-file "sql_preview.json"
        """
    )

    # All arguments are now optional with defaults from DEFAULT_CONFIG
    parser.add_argument('--nl-definition', default=DEFAULT_CONFIG['nl_definition'],
                       help=f'Natural language definition to convert to SQL (default: "{DEFAULT_CONFIG["nl_definition"]}")')
    parser.add_argument('--kg-name', default=DEFAULT_CONFIG['kg_name'],
                       help=f'Knowledge graph name (default: "{DEFAULT_CONFIG["kg_name"]}")')
    parser.add_argument('--select-schema', default=DEFAULT_CONFIG['select_schema'],
                       help=f'Database schema to query (default: "{DEFAULT_CONFIG["select_schema"]}")')
    parser.add_argument('--openai-key', default=DEFAULT_CONFIG['openai_key'],
                       help='OpenAI API key (default: configured in script)')
    parser.add_argument('--db-host', default=DEFAULT_CONFIG['db_host'],
                       help=f'Database host (default: "{DEFAULT_CONFIG["db_host"]}")')
    parser.add_argument('--db-user', default=DEFAULT_CONFIG['db_user'],
                       help=f'Database username (default: "{DEFAULT_CONFIG["db_user"]}")')
    parser.add_argument('--db-password', default=DEFAULT_CONFIG['db_password'],
                       help='Database password (default: configured in script)')

    # Optional arguments with defaults from DEFAULT_CONFIG
    parser.add_argument('--temperature', type=float, default=DEFAULT_CONFIG['temperature'],
                       help=f'OpenAI temperature (default: {DEFAULT_CONFIG["temperature"]})')
    parser.add_argument('--db-port', type=int, default=DEFAULT_CONFIG['db_port'],
                       help=f'Database port (default: {DEFAULT_CONFIG["db_port"]})')
    parser.add_argument('--db-name', default=DEFAULT_CONFIG['db_name'],
                       help=f'Database name (default: "{DEFAULT_CONFIG["db_name"]}")')
    parser.add_argument('--use-llm', action='store_true', default=DEFAULT_CONFIG['use_llm'],
                       help=f'Use LLM for parsing (default: {DEFAULT_CONFIG["use_llm"]})')
    parser.add_argument('--output-file', default=DEFAULT_CONFIG['output_file'],
                       help=f'Save results to JSON file (default: {DEFAULT_CONFIG["output_file"]})')
    parser.add_argument('--verbose', '-v', action='store_true', default=DEFAULT_CONFIG['verbose'],
                       help=f'Enable verbose logging (default: {DEFAULT_CONFIG["verbose"]})')

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
        'password': args.db_password
    }

    logger.info("="*80)
    logger.info("🚀 STANDALONE SQL PREVIEW GENERATOR STARTED")
    logger.info("="*80)
    logger.info(f"NL Definition: {args.nl_definition}")
    logger.info(f"KG Name: {args.kg_name}")
    logger.info(f"Schema: {args.select_schema}")
    logger.info(f"Use LLM: {args.use_llm}")
    logger.info(f"Temperature: {args.temperature}")
    logger.info(f"Database: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    logger.info("="*80)

    try:
        # Initialize SQL preview generator
        generator = StandaloneSQLPreview(args.openai_key, args.temperature)

        # Generate SQL preview
        result = generator.generate_sql_preview(
            args.nl_definition,
            args.kg_name,
            args.select_schema,
            db_config,
            args.use_llm
        )

        # Print results
        logger.info("="*80)
        logger.info("📊 SQL PREVIEW RESULTS")
        logger.info("="*80)
        logger.info(f"Success: {result['success']}")

        if result['success']:
            logger.info(f"Query Type: {result['query_intent']['query_type']}")
            logger.info(f"Operation: {result['query_intent']['operation']}")
            logger.info(f"Source Table: {result['query_intent']['source_table']}")
            logger.info(f"Confidence: {result['query_intent']['confidence']}")
            logger.info(f"Execution Time: {result['execution_time_ms']:.2f}ms")

            logger.info(f"\n📝 GENERATED SQL:")
            logger.info("-" * 60)
            logger.info(result['generated_sql'])
            logger.info("-" * 60)

            if result['enhancements']['applied']:
                logger.info(f"\n🔧 ENHANCEMENTS APPLIED:")
                for enhancement in result['enhancements']['applied']:
                    logger.info(f"  - {enhancement}")

            logger.info(f"\n📊 SCHEMA INFO:")
            logger.info(f"  Schema: {result['schema_info']['schema_name']}")
            logger.info(f"  Tables: {result['schema_info']['tables_count']}")
            logger.info(f"  Available tables: {', '.join(result['schema_info']['tables'][:5])}")
            if len(result['schema_info']['tables']) > 5:
                logger.info(f"    (and {len(result['schema_info']['tables']) - 5} more)")
        else:
            logger.error(f"Error: {result.get('error', 'Unknown error')}")

        # Save to file if requested
        if args.output_file:
            with open(args.output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"💾 Results saved to: {args.output_file}")

        logger.info("="*80)
        logger.info("✅ SQL PREVIEW GENERATION COMPLETED")
        logger.info("="*80)

        # Exit with appropriate code
        sys.exit(0 if result['success'] else 1)

    except KeyboardInterrupt:
        logger.info("❌ Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

    def _parse_with_rules(self, definition: str) -> QueryIntent:
        """Simple rule-based parsing as fallback."""
        logger.info(f"   Using rule-based parsing...")

        definition_lower = definition.lower()

        # Determine query type and operation
        if "missing" in definition_lower or "not in" in definition_lower or "null" in definition_lower:
            query_type = "filter"
            operation = "select"
        elif "count" in definition_lower:
            query_type = "aggregation"
            operation = "count"
        elif "sum" in definition_lower:
            query_type = "aggregation"
            operation = "sum"
        else:
            query_type = "data"
            operation = "select"

        # Try to extract table name
        source_table = None
        words = definition.split()
        for i, word in enumerate(words):
            if word.lower() in ["from", "in"] and i + 1 < len(words):
                source_table = words[i + 1].strip(".,;")
                break

        intent = QueryIntent(definition, query_type, operation)
        intent.source_table = source_table
        intent.confidence = 0.6  # Lower confidence for rule-based parsing

        logger.info(f"✅ Parsed with rules")
        logger.info(f"   Query Type: {intent.query_type}")
        logger.info(f"   Operation: {intent.operation}")
        logger.info(f"   Source Table: {intent.source_table}")
        logger.info(f"   Confidence: {intent.confidence}")

        return intent

    def generate_sql_with_llm(self, intent: QueryIntent, schema_info: Dict[str, Any], db_type: str = "sqlserver") -> str:
        """Generate SQL from QueryIntent using OpenAI."""
        logger.info(f"🤖 STEP 3: Generating SQL using LLM")
        logger.info(f"   Intent: {intent.definition}")
        logger.info(f"   Source Table: {intent.source_table}")
        logger.info(f"   Database Type: {db_type}")

        try:
            # Build comprehensive schema context
            schema_context = f"Database: {db_type.upper()}\n"
            schema_context += f"Schema: {schema_info['schema_name']}\n\n"
            schema_context += "Available tables and their columns:\n"

            for table_name, table_info in schema_info["tables"].items():
                schema_context += f"\nTable: {table_name}\n"
                for col in table_info["columns"]:
                    schema_context += f"  - {col['name']} ({col['type']})\n"

            # Create specialized prompt based on query type
            if intent.query_type == "filter" and ("missing" in intent.definition.lower() or "null" in intent.definition.lower()):
                prompt_type = "Generate a SQL query to find records where specific columns are NULL or missing."
            elif intent.query_type == "aggregation":
                prompt_type = f"Generate a SQL query to perform {intent.operation.upper()} aggregation."
            else:
                prompt_type = "Generate a SQL query to retrieve data."

            prompt = f"""
You are an expert SQL generator for {db_type.upper()} database.

{schema_context}

Task: {prompt_type}
Natural Language Request: {intent.definition}

Requirements:
1. Generate valid {db_type.upper()} syntax
2. Use proper table and column names from the schema above
3. Handle NULL/missing values appropriately
4. Use appropriate WHERE clauses for filtering
5. Include proper JOIN conditions if multiple tables are involved
6. For SQL Server, use TOP clause for limiting results
7. Return only the SQL query without explanations or markdown formatting

SQL Query:
"""

            logger.info(f"   Sending SQL generation request to OpenAI...")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert {db_type.upper()} SQL generator. Generate only valid SQL queries without explanations."
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
            elif generated_sql.startswith('```'):
                generated_sql = generated_sql[3:]
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

    def enhance_sql(self, sql: str, intent: QueryIntent) -> Dict[str, Any]:
        """Apply enhancements to the generated SQL."""
        logger.info(f"🔧 STEP 4: Applying SQL enhancements")

        enhanced_sql = sql
        enhancements_applied = []

        # Check for material master enhancement
        if "hana_material_master" in sql.lower():
            logger.info(f"   Detected hana_material_master table usage")

            # Check if OPS_PLANNER column is missing and should be added
            if "ops_planner" not in sql.lower() and ("missing" in intent.definition.lower() or "planner" in intent.definition.lower()):
                logger.info(f"   Adding OPS_PLANNER column enhancement")

                # Simple enhancement: ensure OPS_PLANNER is in SELECT if not present
                if "SELECT" in enhanced_sql.upper() and "ops_planner" not in enhanced_sql.lower():
                    # Find the SELECT clause and add OPS_PLANNER
                    select_pos = enhanced_sql.upper().find("SELECT")
                    from_pos = enhanced_sql.upper().find("FROM")

                    if select_pos != -1 and from_pos != -1:
                        select_clause = enhanced_sql[select_pos:from_pos].strip()
                        if not select_clause.endswith("*"):
                            # Add OPS_PLANNER to the select list
                            enhanced_sql = enhanced_sql[:from_pos] + ", OPS_PLANNER " + enhanced_sql[from_pos:]
                            enhancements_applied.append("Added OPS_PLANNER column to SELECT")

            enhancements_applied.append("Material master table detected")

        # Check for ops_planner enhancement
        if "ops_planner" in enhanced_sql.lower():
            enhancements_applied.append("OPS_PLANNER column included")

        logger.info(f"✅ SQL enhancements completed")
        if enhancements_applied:
            for enhancement in enhancements_applied:
                logger.info(f"   - {enhancement}")
        else:
            logger.info(f"   - No enhancements applied")

        return {
            "original_sql": sql,
            "enhanced_sql": enhanced_sql,
            "enhancements_applied": enhancements_applied,
            "material_master_detected": "hana_material_master" in sql.lower(),
            "ops_planner_included": "ops_planner" in enhanced_sql.lower()
        }
