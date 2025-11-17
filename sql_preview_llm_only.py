#!/usr/bin/env python3
"""
SQL Preview Script - Pure LLM Mode

This script uses OpenAI LLM exclusively for all natural language processing and SQL generation.
No rule-based parsing, no fallbacks - pure AI-powered SQL generation.

Features:
- 100% LLM-driven parsing and SQL generation
- Schema-aware SQL generation with database context
- Enhanced error handling for LLM failures
- Material master table enhancements
- Comprehensive logging

Usage:
    Update the configuration below and run: python sql_preview_llm_only.py
"""

import logging
import sys
import time
import json
from typing import Dict, Any, Optional, List

# Check for required dependencies
try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False
    print("❌ ERROR: pyodbc is not installed")
    print("   Install with: pip install pyodbc")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("❌ ERROR: openai is not installed")
    print("   Install with: pip install openai")

if not PYODBC_AVAILABLE or not OPENAI_AVAILABLE:
    print("\n💡 Install dependencies: pip install pyodbc openai")
    sys.exit(1)

# =============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# =============================================================================

# Natural Language Definition
NL_DEFINITION = "get products from hana_material_master where OPS_PLANNER is missing"

# Knowledge Graph Settings
KG_NAME = "KG_Test_001"
SELECT_SCHEMA = "newdqnov7"

# OpenAI Settings (LLM-Only Mode)
OPENAI_KEY = "TEST"
TEMPERATURE = 0.0
MODEL = "gpt-4o"  # LLM model to use

# Database Settings
DB_HOST = "DESKTOP-41O1AL9\\LOCALHOST"
DB_PORT = 1433
DB_NAME = "NewDQ"
DB_USER = "mithun"
DB_PASSWORD = "mithun123"

# Script Settings
VERBOSE = True
OUTPUT_FILE = None  # Set to filename to save results

# =============================================================================
# CONFIGURATION VALIDATION
# =============================================================================

def validate_configuration():
    """Validate configuration for LLM-only mode."""
    errors = []
    
    if not NL_DEFINITION or NL_DEFINITION.strip() == "":
        errors.append("NL_DEFINITION cannot be empty")
    
    if not OPENAI_KEY or OPENAI_KEY.strip() == "" or "your-openai-key" in OPENAI_KEY:
        errors.append("OPENAI_KEY must be set to a valid OpenAI API key")
    
    if not isinstance(TEMPERATURE, (int, float)) or TEMPERATURE < 0 or TEMPERATURE > 2:
        errors.append("TEMPERATURE must be between 0 and 2")
    
    if not MODEL or MODEL.strip() == "":
        errors.append("MODEL cannot be empty")
    
    if not DB_HOST or DB_HOST.strip() == "":
        errors.append("DB_HOST cannot be empty")
    
    if not DB_USER or DB_USER.strip() == "":
        errors.append("DB_USER cannot be empty")
    
    if not DB_PASSWORD or DB_PASSWORD.strip() == "":
        errors.append("DB_PASSWORD cannot be empty")
    
    if errors:
        print("❌ CONFIGURATION ERRORS:")
        for error in errors:
            print(f"   - {error}")
        print("\n💡 Please update the configuration and try again.")
        return False
    
    return True

# =============================================================================
# LLM-ONLY SQL PREVIEW ENGINE
# =============================================================================

# Configure logging
log_level = logging.DEBUG if VERBOSE else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('sql_preview_llm.log')
    ]
)
logger = logging.getLogger(__name__)


class QueryIntent:
    """Query intent parsed by LLM."""
    
    def __init__(self, definition: str, query_type: str = "data", operation: str = "select"):
        self.definition = definition
        self.query_type = query_type
        self.operation = operation
        self.source_table = None
        self.target_table = None
        self.confidence = 0.8


class LLMOnlySQLPreview:
    """Pure LLM-driven SQL preview generator."""
    
    def __init__(self, openai_key: str, temperature: float = 0.0, model: str = "gpt-4o"):
        """Initialize with OpenAI configuration."""
        self.openai_client = OpenAI(api_key=openai_key)
        self.temperature = temperature
        self.model = model
        logger.info(f"✅ Initialized LLM-Only SQL Preview")
        logger.info(f"   Model: {model}")
        logger.info(f"   Temperature: {temperature}")
        logger.info(f"   Mode: Pure LLM (No Rule-Based Fallbacks)")
    
    def get_database_schema(self, db_config: Dict[str, Any], select_schema: str) -> Dict[str, Any]:
        """Retrieve database schema for LLM context."""
        logger.info(f"🔍 STEP 1: Retrieving database schema for LLM context")
        logger.info(f"   Database: {db_config['host']}\\{db_config['database']}")
        logger.info(f"   Schema: {select_schema}")
        
        try:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={db_config['host']};"
                f"DATABASE={db_config['database']};"
                f"UID={db_config['username']};"
                f"PWD={db_config['password']};"
                f"TrustServerCertificate=yes;"
            )
            
            logger.info(f"   Connecting to database for schema retrieval...")
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            logger.info(f"   ✅ Database connection established")
            
            schema_info = {"schema_name": select_schema, "tables": {}}
            
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
                    schema_info["tables"][table_name] = {"columns": []}
                
                if column_name:
                    schema_info["tables"][table_name]["columns"].append({
                        "name": column_name,
                        "type": data_type,
                        "nullable": is_nullable == "YES",
                        "default": column_default
                    })
            
            logger.info(f"✅ Schema retrieved for LLM context")
            logger.info(f"   Tables found: {len(schema_info['tables'])}")
            
            for table_name, table_info in schema_info["tables"].items():
                logger.info(f"   Table: {table_name} ({len(table_info['columns'])} columns)")
            
            return schema_info
            
        except Exception as e:
            logger.error(f"❌ Error retrieving database schema: {e}")
            logger.error(f"   LLM-Only Mode requires database schema for context")
            raise Exception(f"Schema retrieval failed in LLM-only mode: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def parse_with_llm(self, nl_definition: str, schema_info: Dict[str, Any]) -> QueryIntent:
        """Parse natural language using LLM only."""
        logger.info(f"🧠 STEP 2: Parsing natural language with LLM")
        logger.info(f"   Definition: {nl_definition}")
        logger.info(f"   Model: {self.model}")
        logger.info(f"   Mode: Pure LLM parsing (no fallbacks)")

        try:
            # Build comprehensive schema context
            schema_context = f"Schema: {schema_info['schema_name']}\n"
            schema_context += "Available tables and columns:\n"

            for table_name, table_info in schema_info["tables"].items():
                schema_context += f"- {table_name}: "
                column_names = [col["name"] for col in table_info["columns"]]
                schema_context += ", ".join(column_names[:15])  # Show more columns for LLM
                if len(column_names) > 15:
                    schema_context += f" (and {len(column_names) - 15} more)"
                schema_context += "\n"

            prompt = f"""
You are an expert SQL analyst with deep knowledge of database schemas and query patterns.

{schema_context}

Natural Language Query: {nl_definition}

Analyze this query and return a JSON object with the following structure:
{{
    "query_type": "comparison|filter|aggregation|data|join",
    "operation": "select|count|sum|avg|join|insert|update|delete",
    "source_table": "primary table name from schema",
    "target_table": "secondary table name if join needed",
    "confidence": 0.0-1.0,
    "explanation": "detailed explanation of query intent",
    "key_columns": ["list", "of", "important", "columns"],
    "filter_conditions": ["list", "of", "filter", "conditions"]
}}

Focus on:
1. Identifying the exact table names from the schema
2. Understanding the operation type (SELECT, COUNT, etc.)
3. Detecting filter conditions (WHERE clauses)
4. Identifying key columns involved
5. Determining if joins are needed
6. Assessing confidence in interpretation

Return only valid JSON without markdown formatting.
"""

            logger.info(f"   Sending parsing request to {self.model}...")
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert SQL analyst. Parse natural language queries and return structured JSON information. Always return valid JSON without markdown formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=800
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
            intent = QueryIntent(
                nl_definition,
                parsed_data.get("query_type", "data"),
                parsed_data.get("operation", "select")
            )
            intent.source_table = parsed_data.get("source_table")
            intent.target_table = parsed_data.get("target_table")
            intent.confidence = parsed_data.get("confidence", 0.8)

            logger.info(f"✅ LLM parsing completed successfully")
            logger.info(f"   Query Type: {intent.query_type}")
            logger.info(f"   Operation: {intent.operation}")
            logger.info(f"   Source Table: {intent.source_table}")
            logger.info(f"   Target Table: {intent.target_table}")
            logger.info(f"   Confidence: {intent.confidence}")
            logger.info(f"   Explanation: {parsed_data.get('explanation', 'N/A')}")
            logger.info(f"   Key Columns: {parsed_data.get('key_columns', [])}")

            return intent

        except json.JSONDecodeError as e:
            logger.error(f"❌ LLM returned invalid JSON: {e}")
            logger.error(f"   Response: {response_text[:200]}...")
            raise Exception(f"LLM parsing failed - invalid JSON response: {e}")
        except Exception as e:
            logger.error(f"❌ LLM parsing failed: {e}")
            logger.error(f"   This is a critical error in LLM-only mode")
            raise Exception(f"LLM parsing failed: {e}")

    def generate_sql_with_llm(self, intent: QueryIntent, schema_info: Dict[str, Any]) -> str:
        """Generate SQL using LLM with full schema context."""
        logger.info(f"🤖 STEP 3: Generating SQL with LLM")
        logger.info(f"   Intent: {intent.definition}")
        logger.info(f"   Source Table: {intent.source_table}")
        logger.info(f"   Model: {self.model}")
        logger.info(f"   Mode: Pure LLM SQL generation")

        try:
            # Build comprehensive schema context for SQL generation
            schema_context = f"Database: SQL Server\n"
            schema_context += f"Schema: {schema_info['schema_name']}\n\n"
            schema_context += "Complete table definitions:\n"

            for table_name, table_info in schema_info["tables"].items():
                schema_context += f"\nTable: {table_name}\n"
                for col in table_info["columns"]:
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    default = f" DEFAULT {col['default']}" if col['default'] else ""
                    schema_context += f"  - {col['name']} {col['type']} {nullable}{default}\n"

            # Create specialized prompt for SQL generation
            prompt = f"""
You are an expert SQL Server developer. Generate a precise SQL query based on the natural language request and database schema.

{schema_context}

Natural Language Request: {intent.definition}
Query Type: {intent.query_type}
Operation: {intent.operation}
Primary Table: {intent.source_table}

Requirements:
1. Generate valid SQL Server syntax
2. Use exact table and column names from the schema above
3. Handle NULL/missing values with IS NULL or IS NOT NULL
4. Use appropriate WHERE clauses for filtering
5. Include proper JOIN conditions if multiple tables needed
6. Use TOP clause for limiting results (SQL Server syntax)
7. Consider the query type: {intent.query_type}
8. Focus on the operation: {intent.operation}
9. Return ONLY the SQL query without explanations

Special considerations:
- For "missing" values, use IS NULL
- For material master tables, consider OPS_PLANNER column
- Use proper SQL Server date/time functions if needed
- Apply appropriate aggregations if requested

Generate the SQL query:
"""

            logger.info(f"   Sending SQL generation request to {self.model}...")
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert SQL Server developer. Generate only valid SQL queries without explanations or markdown formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=1200
            )

            generated_sql = response.choices[0].message.content.strip()

            # Clean up the SQL
            if generated_sql.startswith('```sql'):
                generated_sql = generated_sql[6:]
            elif generated_sql.startswith('```'):
                generated_sql = generated_sql[3:]
            if generated_sql.endswith('```'):
                generated_sql = generated_sql[:-3]
            generated_sql = generated_sql.strip()

            logger.info(f"✅ LLM SQL generation completed")
            logger.info(f"   SQL Length: {len(generated_sql)} characters")
            logger.info(f"   SQL Preview: {generated_sql[:150]}...")

            return generated_sql

        except Exception as e:
            logger.error(f"❌ LLM SQL generation failed: {e}")
            logger.error(f"   This is a critical error in LLM-only mode")
            raise Exception(f"LLM SQL generation failed: {e}")

    def apply_enhancements(self, sql: str, intent: QueryIntent) -> Dict[str, Any]:
        """Apply intelligent enhancements to generated SQL."""
        logger.info(f"🔧 STEP 4: Applying intelligent SQL enhancements")

        enhanced_sql = sql
        enhancements_applied = []

        # Material master table enhancements
        if "hana_material_master" in sql.lower():
            logger.info(f"   Detected hana_material_master table usage")
            enhancements_applied.append("Material master table detected")

            # OPS_PLANNER column enhancement
            if "ops_planner" in intent.definition.lower():
                if "ops_planner" not in sql.lower():
                    logger.info(f"   Adding OPS_PLANNER column to SELECT")
                    # Simple enhancement for missing OPS_PLANNER
                    if "SELECT *" in enhanced_sql.upper():
                        enhanced_sql = enhanced_sql.replace("SELECT *", "SELECT *, OPS_PLANNER", 1)
                        enhancements_applied.append("Added OPS_PLANNER to SELECT clause")

                enhancements_applied.append("OPS_PLANNER column handling applied")

        # Check for ops_planner in final SQL
        if "ops_planner" in enhanced_sql.lower():
            enhancements_applied.append("OPS_PLANNER column included in query")

        logger.info(f"✅ SQL enhancements completed")
        if enhancements_applied:
            for enhancement in enhancements_applied:
                logger.info(f"   - {enhancement}")
        else:
            logger.info(f"   - No enhancements needed")

        return {
            "original_sql": sql,
            "enhanced_sql": enhanced_sql,
            "enhancements_applied": enhancements_applied,
            "material_master_detected": "hana_material_master" in sql.lower(),
            "ops_planner_included": "ops_planner" in enhanced_sql.lower()
        }

    def generate_sql_preview(self, nl_definition: str, kg_name: str, select_schema: str,
                           db_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SQL preview using pure LLM approach."""
        logger.info(f"🚀 Starting LLM-Only SQL preview generation")
        logger.info(f"   NL Definition: {nl_definition}")
        logger.info(f"   KG Name: {kg_name}")
        logger.info(f"   Schema: {select_schema}")
        logger.info(f"   Model: {self.model}")
        logger.info(f"   Mode: Pure LLM (No Fallbacks)")

        overall_start_time = time.time()

        try:
            # Step 1: Get database schema for LLM context
            schema_info = self.get_database_schema(db_config, select_schema)

            # Step 2: Parse with LLM only
            intent = self.parse_with_llm(nl_definition, schema_info)

            # Step 3: Generate SQL with LLM only
            generated_sql = self.generate_sql_with_llm(intent, schema_info)

            # Step 4: Apply intelligent enhancements
            enhancement_result = self.apply_enhancements(generated_sql, intent)

            overall_execution_time = (time.time() - overall_start_time) * 1000

            # Prepare comprehensive result
            result = {
                'success': True,
                'mode': 'LLM_ONLY',
                'model_used': self.model,
                'temperature': self.temperature,
                'nl_definition': nl_definition,
                'kg_name': kg_name,
                'select_schema': select_schema,
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
                'execution_time_ms': overall_execution_time,
                'llm_calls': 2  # One for parsing, one for SQL generation
            }

            logger.info(f"🎉 LLM-Only SQL preview generation completed!")
            logger.info(f"   Success: {result['success']}")
            logger.info(f"   Query Type: {intent.query_type}")
            logger.info(f"   Source Table: {intent.source_table}")
            logger.info(f"   Confidence: {intent.confidence}")
            logger.info(f"   LLM Calls: {result['llm_calls']}")
            logger.info(f"   Total time: {overall_execution_time:.2f}ms")

            return result

        except Exception as e:
            logger.error(f"❌ LLM-Only SQL preview generation failed: {e}")
            return {
                'success': False,
                'mode': 'LLM_ONLY',
                'model_used': self.model,
                'error': str(e),
                'nl_definition': nl_definition,
                'kg_name': kg_name,
                'select_schema': select_schema,
                'execution_time_ms': (time.time() - overall_start_time) * 1000
            }


def main():
    """Main function for LLM-only SQL preview."""

    # Validate configuration
    if not validate_configuration():
        sys.exit(1)

    # Prepare database configuration
    db_config = {
        'host': DB_HOST,
        'port': DB_PORT,
        'database': DB_NAME,
        'username': DB_USER,
        'password': DB_PASSWORD
    }

    logger.info("="*80)
    logger.info("🚀 LLM-ONLY SQL PREVIEW GENERATOR STARTED")
    logger.info("="*80)
    logger.info(f"NL Definition: {NL_DEFINITION}")
    logger.info(f"KG Name: {KG_NAME}")
    logger.info(f"Schema: {SELECT_SCHEMA}")
    logger.info(f"Model: {MODEL}")
    logger.info(f"Temperature: {TEMPERATURE}")
    logger.info(f"Mode: Pure LLM (No Rule-Based Fallbacks)")
    logger.info(f"Database: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    logger.info("="*80)

    try:
        # Initialize LLM-only generator
        generator = LLMOnlySQLPreview(OPENAI_KEY, TEMPERATURE, MODEL)

        # Generate SQL preview using pure LLM approach
        result = generator.generate_sql_preview(
            NL_DEFINITION,
            KG_NAME,
            SELECT_SCHEMA,
            db_config
        )

        # Display results
        logger.info("="*80)
        logger.info("📊 LLM-ONLY SQL PREVIEW RESULTS")
        logger.info("="*80)
        logger.info(f"Success: {result['success']}")

        if result['success']:
            logger.info(f"Mode: {result['mode']}")
            logger.info(f"Model Used: {result['model_used']}")
            logger.info(f"Query Type: {result['query_intent']['query_type']}")
            logger.info(f"Operation: {result['query_intent']['operation']}")
            logger.info(f"Source Table: {result['query_intent']['source_table']}")
            logger.info(f"Confidence: {result['query_intent']['confidence']}")
            logger.info(f"LLM Calls: {result['llm_calls']}")
            logger.info(f"Execution Time: {result['execution_time_ms']:.2f}ms")

            logger.info(f"\n📝 GENERATED SQL (LLM-Only):")
            logger.info("-" * 60)
            logger.info(result['generated_sql'])
            logger.info("-" * 60)

            if result['enhancements']['applied']:
                logger.info(f"\n🔧 INTELLIGENT ENHANCEMENTS:")
                for enhancement in result['enhancements']['applied']:
                    logger.info(f"  - {enhancement}")

            logger.info(f"\n📊 SCHEMA CONTEXT:")
            logger.info(f"  Schema: {result['schema_info']['schema_name']}")
            logger.info(f"  Tables: {result['schema_info']['tables_count']}")
            logger.info(f"  Available: {', '.join(result['schema_info']['tables'][:5])}")
            if len(result['schema_info']['tables']) > 5:
                logger.info(f"    (and {len(result['schema_info']['tables']) - 5} more)")
        else:
            logger.error(f"Error: {result.get('error', 'Unknown error')}")
            logger.error(f"Mode: {result.get('mode', 'Unknown')}")
            logger.error(f"This error occurred in LLM-only mode - no fallbacks available")

        # Save to file if requested
        if OUTPUT_FILE:
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"💾 Results saved to: {OUTPUT_FILE}")

        logger.info("="*80)
        logger.info("✅ LLM-ONLY SQL PREVIEW COMPLETED")
        logger.info("="*80)

        # Exit with appropriate code
        sys.exit(0 if result['success'] else 1)

    except KeyboardInterrupt:
        logger.info("❌ Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error in LLM-only mode: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
