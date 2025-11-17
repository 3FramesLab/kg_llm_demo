#!/usr/bin/env python3
"""
Standalone SQL Preview Script

This script mimics the /v1/landing-kpi-mssql/sql-preview API endpoint.
It can be run independently outside the main project and provides the same functionality.

Usage:
    python standalone_sql_preview.py \
        --nl-definition "get products from hana_material_master where OPS_PLANNER is missing" \
        --kg-name "New_KG_101" \
        --select-schema "newdqnov7" \
        --openai-key "your-openai-key" \
        --temperature 0.7 \
        --db-host "your-db-host" \
        --db-port 1433 \
        --db-name "your-database" \
        --db-user "your-username" \
        --db-password "your-password" \
        --use-llm \
        --verbose

Author: AI Assistant
Date: 2025-11-10
"""

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('sql_preview.log')
    ]
)
logger = logging.getLogger('sql_preview')

@dataclass
class QueryIntent:
    """Query intent data structure."""
    definition: str
    query_type: str = "comparison_query"
    operation: str = "NOT_IN"
    source_table: Optional[str] = None
    target_table: Optional[str] = None
    join_columns: List[str] = None
    filters: List[Dict] = None
    confidence: float = 0.0
    additional_columns: List[Dict] = None
    
    def __post_init__(self):
        if self.join_columns is None:
            self.join_columns = []
        if self.filters is None:
            self.filters = []
        if self.additional_columns is None:
            self.additional_columns = []

class StandaloneSQLPreview:
    """Standalone SQL Preview implementation."""
    
    def __init__(self, args):
        """Initialize with command line arguments."""
        self.args = args
        self.start_time = time.time()
        
        logger.info("="*120)
        logger.info("🚀 STANDALONE SQL PREVIEW: INITIALIZATION STARTED")
        logger.info(f"   Script Version: 1.0")
        logger.info(f"   Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"   NL Definition: '{args.nl_definition}'")
        logger.info(f"   KG Name: {args.kg_name}")
        logger.info(f"   Schema: {args.select_schema}")
        logger.info(f"   Use LLM: {args.use_llm}")
        logger.info(f"   Temperature: {args.temperature}")
        logger.info(f"   Database Host: {args.db_host}")
        logger.info(f"   Database Name: {args.db_name}")
        logger.info(f"   Verbose Mode: {args.verbose}")
        logger.info("="*120)
        
        # Set up OpenAI
        if args.use_llm:
            self._setup_openai()
        
        # Set up database connection
        self._setup_database()
        
        # Initialize components
        self._initialize_components()
    
    def _setup_openai(self):
        """Set up OpenAI client."""
        logger.info("🤖 STEP 1: SETTING UP OPENAI CLIENT")
        setup_start = time.time()
        
        try:
            import openai
            
            # Set API key
            if self.args.openai_key:
                openai.api_key = self.args.openai_key
                os.environ['OPENAI_API_KEY'] = self.args.openai_key
                logger.info("   ✅ OpenAI API key set from argument")
            elif os.getenv('OPENAI_API_KEY'):
                openai.api_key = os.getenv('OPENAI_API_KEY')
                logger.info("   ✅ OpenAI API key loaded from environment")
            else:
                raise ValueError("OpenAI API key not provided")
            
            # Test connection
            self.openai_client = openai
            
            setup_time = (time.time() - setup_start) * 1000
            logger.info(f"✅ OpenAI client setup completed in {setup_time:.2f}ms")
            logger.info(f"   API Key: {'*' * 20}...{self.args.openai_key[-4:] if self.args.openai_key else 'from_env'}")
            logger.info(f"   Temperature: {self.args.temperature}")
            
        except ImportError:
            logger.error("❌ OpenAI package not installed. Install with: pip install openai")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Failed to setup OpenAI: {e}")
            sys.exit(1)
    
    def _setup_database(self):
        """Set up database connection."""
        logger.info("💾 STEP 2: SETTING UP DATABASE CONNECTION")
        setup_start = time.time()
        
        try:
            import pyodbc
            
            # Build connection string
            conn_str = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={self.args.db_host},{self.args.db_port};"
                f"DATABASE={self.args.db_name};"
                f"UID={self.args.db_user};"
                f"PWD={self.args.db_password};"
                f"TrustServerCertificate=yes;"
            )
            
            logger.info(f"   Connection String: DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={self.args.db_host},{self.args.db_port};DATABASE={self.args.db_name};UID={self.args.db_user};PWD=***;TrustServerCertificate=yes;")
            
            # Test connection
            logger.info("   Testing database connection...")
            self.db_connection = pyodbc.connect(conn_str)
            
            # Test query
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            
            setup_time = (time.time() - setup_start) * 1000
            logger.info(f"✅ Database connection established in {setup_time:.2f}ms")
            logger.info(f"   Host: {self.args.db_host}:{self.args.db_port}")
            logger.info(f"   Database: {self.args.db_name}")
            logger.info(f"   User: {self.args.db_user}")
            logger.info(f"   Test Query Result: {result[0] if result else 'Failed'}")
            
        except ImportError:
            logger.error("❌ pyodbc package not installed. Install with: pip install pyodbc")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            sys.exit(1)
    
    def _initialize_components(self):
        """Initialize NL processing components."""
        logger.info("🔧 STEP 3: INITIALIZING NL PROCESSING COMPONENTS")
        init_start = time.time()
        
        # Initialize schemas info (simplified for standalone)
        self.schemas_info = {
            self.args.select_schema: {
                "tables": self._get_schema_tables()
            }
        }
        
        init_time = (time.time() - init_start) * 1000
        logger.info(f"✅ Components initialized in {init_time:.2f}ms")
        logger.info(f"   Schema: {self.args.select_schema}")
        logger.info(f"   Tables Found: {len(self.schemas_info[self.args.select_schema]['tables'])}")
        
        if self.args.verbose:
            for table_name in self.schemas_info[self.args.select_schema]['tables']:
                logger.info(f"      - {table_name}")
    
    def _get_schema_tables(self):
        """Get tables from the specified schema."""
        logger.info("📊 STEP 3.1: DISCOVERING SCHEMA TABLES")
        discovery_start = time.time()
        
        try:
            cursor = self.db_connection.cursor()
            
            # Get tables from schema
            query = """
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = ? 
                AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """
            
            logger.info(f"   Executing schema discovery query...")
            logger.info(f"   Query: {query}")
            logger.info(f"   Schema: {self.args.select_schema}")
            
            cursor.execute(query, (self.args.select_schema,))
            tables = cursor.fetchall()
            
            table_dict = {}
            for table in tables:
                table_name = table[0]
                table_dict[table_name] = {"columns": self._get_table_columns(table_name)}
            
            discovery_time = (time.time() - discovery_start) * 1000
            logger.info(f"✅ Schema discovery completed in {discovery_time:.2f}ms")
            logger.info(f"   Tables Found: {len(table_dict)}")
            
            return table_dict
            
        except Exception as e:
            logger.error(f"❌ Failed to discover schema tables: {e}")
            return {}
    
    def _get_table_columns(self, table_name):
        """Get columns for a specific table."""
        try:
            cursor = self.db_connection.cursor()
            
            query = """
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
                ORDER BY ORDINAL_POSITION
            """
            
            cursor.execute(query, (self.args.select_schema, table_name))
            columns = cursor.fetchall()
            
            column_list = [{"name": col[0], "type": col[1]} for col in columns]
            
            if self.args.verbose:
                logger.info(f"      Table {table_name}: {len(column_list)} columns")
            
            return column_list
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get columns for {table_name}: {e}")
            return []

    def parse_nl_definition(self):
        """Parse natural language definition into query intent."""
        logger.info("📝 STEP 4: PARSING NATURAL LANGUAGE DEFINITION")
        parse_start = time.time()

        if self.args.use_llm:
            intent = self._parse_with_llm()
        else:
            intent = self._parse_rule_based()

        parse_time = (time.time() - parse_start) * 1000
        logger.info(f"✅ NL definition parsed in {parse_time:.2f}ms")
        logger.info(f"   Method: {'LLM' if self.args.use_llm else 'Rule-based'}")
        logger.info(f"   Query Type: {intent.query_type}")
        logger.info(f"   Operation: {intent.operation}")
        logger.info(f"   Source Table: {intent.source_table}")
        logger.info(f"   Target Table: {intent.target_table}")
        logger.info(f"   Confidence: {intent.confidence}")

        return intent

    def _parse_with_llm(self):
        """Parse using OpenAI LLM."""
        logger.info("🤖 STEP 4.1: LLM-BASED PARSING")
        llm_start = time.time()

        # Prepare table information for LLM
        available_tables = list(self.schemas_info[self.args.select_schema]['tables'].keys())

        # Create LLM prompt
        prompt = self._create_llm_prompt(available_tables)

        try:
            logger.info("   Sending request to OpenAI...")
            logger.info(f"   Model: gpt-3.5-turbo")
            logger.info(f"   Temperature: {self.args.temperature}")
            logger.info(f"   Available Tables: {len(available_tables)}")

            if self.args.verbose:
                logger.info(f"   Prompt: {prompt[:200]}...")

            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a SQL expert that extracts table names and operations from natural language queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.args.temperature,
                max_tokens=500
            )

            llm_time = (time.time() - llm_start) * 1000
            logger.info(f"✅ LLM response received in {llm_time:.2f}ms")

            # Parse LLM response
            response_text = response.choices[0].message.content
            logger.info(f"   Response Length: {len(response_text)} characters")

            if self.args.verbose:
                logger.info(f"   LLM Response: {response_text}")

            return self._parse_llm_response(response_text)

        except Exception as e:
            logger.error(f"❌ LLM parsing failed: {e}")
            logger.info("   Falling back to rule-based parsing...")
            return self._parse_rule_based()

    def _create_llm_prompt(self, available_tables):
        """Create prompt for LLM parsing."""
        prompt = f"""
Extract table names and operation from this natural language query:
"{self.args.nl_definition}"

Available tables in schema '{self.args.select_schema}':
{', '.join(available_tables)}

Return a JSON response with:
{{
    "definition": "{self.args.nl_definition}",
    "source_table": "table_name_or_null",
    "target_table": "table_name_or_null",
    "operation": "NOT_IN|IN|EQUALS|CONTAINS",
    "filters": [],
    "confidence": 0.0-1.0,
    "reasoning": "explanation"
}}

Focus on finding exact table name matches from the available tables list.
"""
        return prompt

    def _parse_llm_response(self, response_text):
        """Parse LLM JSON response into QueryIntent."""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)

                logger.info("   ✅ LLM response parsed successfully")
                logger.info(f"      Source Table: {data.get('source_table')}")
                logger.info(f"      Target Table: {data.get('target_table')}")
                logger.info(f"      Operation: {data.get('operation')}")
                logger.info(f"      Confidence: {data.get('confidence')}")

                return QueryIntent(
                    definition=self.args.nl_definition,
                    source_table=data.get('source_table'),
                    target_table=data.get('target_table'),
                    operation=data.get('operation', 'NOT_IN'),
                    confidence=data.get('confidence', 0.0),
                    filters=data.get('filters', [])
                )
            else:
                raise ValueError("No JSON found in LLM response")

        except Exception as e:
            logger.warning(f"⚠️ Failed to parse LLM response: {e}")
            logger.info("   Falling back to rule-based parsing...")
            return self._parse_rule_based()

    def _parse_rule_based(self):
        """Parse using rule-based approach."""
        logger.info("📋 STEP 4.2: RULE-BASED PARSING")
        rule_start = time.time()

        definition = self.args.nl_definition.lower()
        available_tables = list(self.schemas_info[self.args.select_schema]['tables'].keys())

        # Find tables mentioned in definition
        source_table = None
        target_table = None

        logger.info(f"   Searching for table matches in: '{definition}'")
        logger.info(f"   Available tables: {available_tables}")

        for table in available_tables:
            table_lower = table.lower()
            if table_lower in definition:
                if not source_table:
                    source_table = table
                    logger.info(f"   Found source table: {table}")
                elif not target_table:
                    target_table = table
                    logger.info(f"   Found target table: {table}")

        # Determine operation
        operation = "NOT_IN"
        if "missing" in definition or "not in" in definition or "absent" in definition:
            operation = "NOT_IN"
        elif "in both" in definition or "common" in definition:
            operation = "IN"
        elif "equals" in definition or "same" in definition:
            operation = "EQUALS"

        confidence = 0.8 if source_table else 0.2

        rule_time = (time.time() - rule_start) * 1000
        logger.info(f"✅ Rule-based parsing completed in {rule_time:.2f}ms")
        logger.info(f"   Source Table: {source_table}")
        logger.info(f"   Target Table: {target_table}")
        logger.info(f"   Operation: {operation}")
        logger.info(f"   Confidence: {confidence}")

        return QueryIntent(
            definition=self.args.nl_definition,
            source_table=source_table,
            target_table=target_table,
            operation=operation,
            confidence=confidence
        )

    def generate_sql(self, intent):
        """Generate SQL from query intent."""
        logger.info("🔧 STEP 5: GENERATING SQL FROM INTENT")
        sql_start = time.time()

        logger.info(f"   Intent Definition: '{intent.definition}'")
        logger.info(f"   Query Type: {intent.query_type}")
        logger.info(f"   Operation: {intent.operation}")
        logger.info(f"   Source Table: {intent.source_table}")
        logger.info(f"   Target Table: {intent.target_table}")

        if self.args.use_llm:
            sql = self._generate_sql_with_llm(intent)
        else:
            sql = self._generate_sql_template(intent)

        sql_time = (time.time() - sql_start) * 1000
        logger.info(f"✅ SQL generated in {sql_time:.2f}ms")
        logger.info(f"   Method: {'LLM' if self.args.use_llm else 'Template'}")
        logger.info(f"   SQL Length: {len(sql)} characters")

        if self.args.verbose:
            logger.info(f"   Generated SQL:")
            for i, line in enumerate(sql.split('\n'), 1):
                logger.info(f"      {i:2d}: {line}")

        return sql

    def _generate_sql_with_llm(self, intent):
        """Generate SQL using LLM."""
        logger.info("🤖 STEP 5.1: LLM SQL GENERATION")
        llm_start = time.time()

        try:
            # Create SQL generation prompt
            prompt = self._create_sql_prompt(intent)

            logger.info("   Sending SQL generation request to OpenAI...")
            logger.info(f"   Model: gpt-3.5-turbo")
            logger.info(f"   Temperature: {self.args.temperature}")

            if self.args.verbose:
                logger.info(f"   SQL Prompt: {prompt[:300]}...")

            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a SQL expert. Generate clean, efficient SQL queries for SQL Server."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.args.temperature,
                max_tokens=1000
            )

            llm_time = (time.time() - llm_start) * 1000
            logger.info(f"✅ LLM SQL generation completed in {llm_time:.2f}ms")

            sql = response.choices[0].message.content.strip()

            # Clean up SQL (remove markdown formatting if present)
            sql = self._clean_sql(sql)

            logger.info(f"   Generated SQL Length: {len(sql)} characters")

            return sql

        except Exception as e:
            logger.error(f"❌ LLM SQL generation failed: {e}")
            logger.info("   Falling back to template-based generation...")
            return self._generate_sql_template(intent)

    def _create_sql_prompt(self, intent):
        """Create prompt for SQL generation."""
        schema_info = ""
        if intent.source_table:
            columns = self.schemas_info[self.args.select_schema]['tables'].get(intent.source_table, {}).get('columns', [])
            schema_info += f"\nTable {intent.source_table} columns: {[col['name'] for col in columns]}"

        if intent.target_table:
            columns = self.schemas_info[self.args.select_schema]['tables'].get(intent.target_table, {}).get('columns', [])
            schema_info += f"\nTable {intent.target_table} columns: {[col['name'] for col in columns]}"

        prompt = f"""
Generate a SQL Server query for this requirement:
"{intent.definition}"

Schema: {self.args.select_schema}
Operation: {intent.operation}
Source Table: {intent.source_table}
Target Table: {intent.target_table}
{schema_info}

Requirements:
- Use SQL Server syntax
- Use proper schema qualification: [{self.args.select_schema}].[table_name]
- For NOT_IN operations, find records in source table that don't exist in target table
- For missing/null checks, use IS NULL or IS NOT NULL
- Return clean SQL without markdown formatting
- Add appropriate WHERE clauses for the operation

Return only the SQL query, no explanations.
"""
        return prompt

    def _generate_sql_template(self, intent):
        """Generate SQL using templates."""
        logger.info("📋 STEP 5.2: TEMPLATE-BASED SQL GENERATION")
        template_start = time.time()

        if not intent.source_table:
            logger.warning("⚠️ No source table found, generating basic SELECT")
            return f"SELECT 1 as no_table_found -- Could not identify tables in: {intent.definition}"

        schema = self.args.select_schema
        source_table = f"[{schema}].[{intent.source_table}]"

        if intent.operation == "NOT_IN" and intent.target_table:
            # Generate NOT IN query
            target_table = f"[{schema}].[{intent.target_table}]"
            sql = f"""
SELECT DISTINCT s.*
FROM {source_table} s
WHERE s.MATERIAL NOT IN (
    SELECT t.MATERIAL
    FROM {target_table} t
    WHERE t.MATERIAL IS NOT NULL
)
"""
        elif "missing" in intent.definition.lower() or "null" in intent.definition.lower():
            # Generate NULL check query
            column = self._guess_column_name(intent)
            sql = f"""
SELECT *
FROM {source_table}
WHERE {column} IS NULL
   OR {column} = ''
"""
        else:
            # Generate basic SELECT
            sql = f"""
SELECT TOP 1000 *
FROM {source_table}
"""

        template_time = (time.time() - template_start) * 1000
        logger.info(f"✅ Template SQL generated in {template_time:.2f}ms")

        return sql.strip()

    def _guess_column_name(self, intent):
        """Guess column name from definition."""
        definition = intent.definition.lower()

        if "planner" in definition:
            return "OPS_PLANNER"
        elif "material" in definition:
            return "MATERIAL"
        elif "code" in definition:
            return "MATERIAL_CODE"
        else:
            return "ID"

    def _clean_sql(self, sql):
        """Clean SQL from markdown formatting."""
        # Remove markdown code blocks
        sql = sql.replace("```sql", "").replace("```", "")

        # Remove extra whitespace
        lines = [line.strip() for line in sql.split('\n') if line.strip()]

        return '\n'.join(lines)

    def apply_material_master_enhancement(self, sql):
        """Apply material master enhancement (simplified version)."""
        logger.info("🔧 STEP 6: APPLYING MATERIAL MASTER ENHANCEMENT")
        enhance_start = time.time()

        enhanced_sql = sql
        enhancement_applied = False
        material_master_added = False
        ops_planner_added = False

        # Simple enhancement: add material master join if not present
        if "hana_material_master" not in sql.lower() and "material" in sql.lower():
            logger.info("   Adding material master enhancement...")

            # This is a simplified version - in the real system this would be more complex
            if "WHERE" in sql:
                enhanced_sql = sql.replace(
                    "WHERE",
                    f"LEFT JOIN [{self.args.select_schema}].[hana_material_master] mm ON mm.MATERIAL = s.MATERIAL\nWHERE"
                )
                enhancement_applied = True
                material_master_added = True

                if "planner" in self.args.nl_definition.lower():
                    ops_planner_added = True

        enhance_time = (time.time() - enhance_start) * 1000
        logger.info(f"✅ Enhancement completed in {enhance_time:.2f}ms")
        logger.info(f"   Enhancement Applied: {enhancement_applied}")
        logger.info(f"   Material Master Added: {material_master_added}")
        logger.info(f"   OPS Planner Added: {ops_planner_added}")

        return {
            'original_sql': sql,
            'enhanced_sql': enhanced_sql,
            'enhancement_applied': enhancement_applied,
            'material_master_added': material_master_added,
            'ops_planner_added': ops_planner_added
        }

    def run(self):
        """Run the complete SQL preview process."""
        logger.info("🚀 STEP 7: RUNNING COMPLETE SQL PREVIEW PROCESS")
        process_start = time.time()

        try:
            # Step 1: Parse NL definition
            intent = self.parse_nl_definition()

            # Step 2: Generate SQL
            sql = self.generate_sql(intent)

            # Step 3: Apply enhancements
            enhancement_result = self.apply_material_master_enhancement(sql)

            # Step 4: Prepare final result
            total_time = (time.time() - self.start_time) * 1000
            process_time = (time.time() - process_start) * 1000

            result = {
                "success": True,
                "generated_sql": enhancement_result['original_sql'],
                "enhanced_sql": enhancement_result['enhanced_sql'],
                "enhancement_applied": enhancement_result['enhancement_applied'],
                "material_master_added": enhancement_result['material_master_added'],
                "ops_planner_added": enhancement_result['ops_planner_added'],
                "storage_type": "mssql",
                "intent": asdict(intent),
                "performance": {
                    "total_time_ms": total_time,
                    "process_time_ms": process_time
                }
            }

            logger.info("="*120)
            logger.info("🎉 STANDALONE SQL PREVIEW: PROCESS COMPLETED SUCCESSFULLY")
            logger.info(f"   Total Time: {total_time:.2f}ms")
            logger.info(f"   Process Time: {process_time:.2f}ms")
            logger.info(f"   Intent Confidence: {intent.confidence}")
            logger.info(f"   Enhancement Applied: {enhancement_result['enhancement_applied']}")
            logger.info(f"   Final SQL Length: {len(enhancement_result['enhanced_sql'])} characters")
            logger.info("="*120)

            return result

        except Exception as e:
            total_time = (time.time() - self.start_time) * 1000
            error_type = type(e).__name__
            error_message = str(e)

            logger.error("="*120)
            logger.error("❌ STANDALONE SQL PREVIEW: PROCESS FAILED")
            logger.error(f"   Total Time: {total_time:.2f}ms")
            logger.error(f"   Error Type: {error_type}")
            logger.error(f"   Error Message: {error_message}")
            logger.error(f"   NL Definition: '{self.args.nl_definition}'")
            logger.error("="*120)
            logger.error("Full error details:", exc_info=True)

            return {
                "success": False,
                "error": error_message,
                "error_type": error_type,
                "total_time_ms": total_time
            }

def create_argument_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Standalone SQL Preview - Mimics /v1/landing-kpi-mssql/sql-preview API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with LLM
  python standalone_sql_preview.py \\
    --nl-definition "get products from hana_material_master where OPS_PLANNER is missing" \\
    --kg-name "New_KG_101" \\
    --select-schema "newdqnov7" \\
    --openai-key "sk-..." \\
    --db-host "localhost" \\
    --db-name "your_database" \\
    --db-user "username" \\
    --db-password "password" \\
    --use-llm

  # Rule-based parsing (no LLM)
  python standalone_sql_preview.py \\
    --nl-definition "find missing planners in hana_material_master" \\
    --select-schema "newdqnov7" \\
    --db-host "localhost" \\
    --db-name "your_database" \\
    --db-user "username" \\
    --db-password "password"

  # With custom temperature and verbose output
  python standalone_sql_preview.py \\
    --nl-definition "get products from hana_material_master and brz_lnd_SAR_Excel_NBU where planner is missing in both" \\
    --kg-name "New_KG_101" \\
    --select-schema "newdqnov7" \\
    --openai-key "sk-..." \\
    --temperature 0.3 \\
    --db-host "localhost" \\
    --db-name "your_database" \\
    --db-user "username" \\
    --db-password "password" \\
    --use-llm \\
    --verbose
        """
    )

    # Required arguments
    parser.add_argument(
        '--nl-definition',
        required=True,
        help='Natural language definition of the query (e.g., "get products where planner is missing")'
    )

    parser.add_argument(
        '--select-schema',
        required=True,
        help='Database schema name (e.g., "newdqnov7")'
    )

    # Database connection arguments
    parser.add_argument('--db-host', required=True, help='Database host')
    parser.add_argument('--db-port', type=int, default=1433, help='Database port (default: 1433)')
    parser.add_argument('--db-name', required=True, help='Database name')
    parser.add_argument('--db-user', required=True, help='Database username')
    parser.add_argument('--db-password', required=True, help='Database password')

    # Optional arguments
    parser.add_argument(
        '--kg-name',
        default='default',
        help='Knowledge Graph name (default: "default")'
    )

    parser.add_argument(
        '--openai-key',
        help='OpenAI API key (can also be set via OPENAI_API_KEY environment variable)'
    )

    parser.add_argument(
        '--temperature',
        type=float,
        default=0.7,
        help='OpenAI temperature (0.0-1.0, default: 0.7)'
    )

    parser.add_argument(
        '--use-llm',
        action='store_true',
        help='Use LLM for parsing and SQL generation (requires OpenAI key)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--output-format',
        choices=['json', 'pretty', 'sql-only'],
        default='pretty',
        help='Output format (default: pretty)'
    )

    return parser

def format_output(result, format_type):
    """Format output based on specified format."""
    if format_type == 'json':
        return json.dumps(result, indent=2)

    elif format_type == 'sql-only':
        if result.get('success'):
            return result.get('enhanced_sql', result.get('generated_sql', ''))
        else:
            return f"-- Error: {result.get('error', 'Unknown error')}"

    else:  # pretty format
        if result.get('success'):
            output = []
            output.append("="*80)
            output.append("🎉 SQL PREVIEW RESULT")
            output.append("="*80)
            output.append(f"✅ Success: {result['success']}")
            output.append(f"📊 Storage Type: {result.get('storage_type', 'unknown')}")
            output.append(f"🔧 Enhancement Applied: {result.get('enhancement_applied', False)}")
            output.append(f"📋 Material Master Added: {result.get('material_master_added', False)}")
            output.append(f"⚙️ OPS Planner Added: {result.get('ops_planner_added', False)}")

            if 'performance' in result:
                perf = result['performance']
                output.append(f"⏱️ Total Time: {perf.get('total_time_ms', 0):.2f}ms")
                output.append(f"🚀 Process Time: {perf.get('process_time_ms', 0):.2f}ms")

            if 'intent' in result:
                intent = result['intent']
                output.append(f"🎯 Intent Confidence: {intent.get('confidence', 0):.2f}")
                output.append(f"📝 Query Type: {intent.get('query_type', 'unknown')}")
                output.append(f"⚙️ Operation: {intent.get('operation', 'unknown')}")
                output.append(f"📊 Source Table: {intent.get('source_table', 'none')}")
                output.append(f"📊 Target Table: {intent.get('target_table', 'none')}")

            output.append("")
            output.append("🔧 GENERATED SQL:")
            output.append("-"*80)
            output.append(result.get('generated_sql', 'No SQL generated'))

            if result.get('enhancement_applied'):
                output.append("")
                output.append("✨ ENHANCED SQL:")
                output.append("-"*80)
                output.append(result.get('enhanced_sql', 'No enhanced SQL'))

            output.append("="*80)

            return '\n'.join(output)

        else:
            output = []
            output.append("="*80)
            output.append("❌ SQL PREVIEW ERROR")
            output.append("="*80)
            output.append(f"❌ Success: {result['success']}")
            output.append(f"🚨 Error Type: {result.get('error_type', 'unknown')}")
            output.append(f"💬 Error Message: {result.get('error', 'Unknown error')}")
            output.append(f"⏱️ Total Time: {result.get('total_time_ms', 0):.2f}ms")
            output.append("="*80)

            return '\n'.join(output)

def main():
    """Main function."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Set verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("🔍 Verbose mode enabled")

    # Validate arguments
    if args.use_llm and not args.openai_key and not os.getenv('OPENAI_API_KEY'):
        logger.error("❌ OpenAI API key required when --use-llm is specified")
        logger.error("   Provide via --openai-key argument or OPENAI_API_KEY environment variable")
        sys.exit(1)

    # Print startup banner
    print("="*80)
    print("🚀 STANDALONE SQL PREVIEW")
    print("   Mimics /v1/landing-kpi-mssql/sql-preview API")
    print(f"   Version: 1.0")
    print(f"   Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    try:
        # Initialize and run SQL preview
        sql_preview = StandaloneSQLPreview(args)
        result = sql_preview.run()

        # Format and output result
        formatted_output = format_output(result, args.output_format)
        print(formatted_output)

        # Exit with appropriate code
        sys.exit(0 if result.get('success') else 1)

    except KeyboardInterrupt:
        logger.info("\n🛑 Process interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        logger.error("Full error details:", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
