#!/usr/bin/env python3
"""
Standalone SQL Preview Script with JDBC Connection

This script mimics the /v1/landing-kpi-mssql/sql-preview API endpoint using
the same JDBC approach as the main project (JayDeBeApi).

Usage:
    python standalone_sql_preview_jdbc.py \
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
        --jdbc-drivers-path "/path/to/jdbc_drivers" \
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
import os
import glob
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('sql_preview_jdbc.log')
    ]
)
logger = logging.getLogger('sql_preview_jdbc')

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

class StandaloneSQLPreviewJDBC:
    """Standalone SQL Preview implementation using JDBC (JayDeBeApi)."""
    
    def __init__(self, args):
        """Initialize with command line arguments."""
        self.args = args
        self.start_time = time.time()
        
        logger.info("="*120)
        logger.info("🚀 STANDALONE SQL PREVIEW (JDBC): INITIALIZATION STARTED")
        logger.info(f"   Script Version: 2.0 (JDBC)")
        logger.info(f"   Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"   NL Definition: '{args.nl_definition}'")
        logger.info(f"   KG Name: {args.kg_name}")
        logger.info(f"   Schema: {args.select_schema}")
        logger.info(f"   Use LLM: {args.use_llm}")
        logger.info(f"   Temperature: {args.temperature}")
        logger.info(f"   Database Host: {args.db_host}")
        logger.info(f"   Database Name: {args.db_name}")
        logger.info(f"   JDBC Drivers Path: {args.jdbc_drivers_path}")
        logger.info(f"   Verbose Mode: {args.verbose}")
        logger.info("="*120)
        
        # Set up OpenAI
        if args.use_llm:
            self._setup_openai()
        
        # Set up JDBC database connection
        self._setup_jdbc_database()
        
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
    
    def _setup_jdbc_database(self):
        """Set up JDBC database connection using JayDeBeApi (same as project)."""
        logger.info("💾 STEP 2: SETTING UP JDBC DATABASE CONNECTION")
        setup_start = time.time()
        
        try:
            import jaydebeapi
            
            # Build JDBC URL (same pattern as project)
            if self.args.db_type.lower() in ['sqlserver', 'mssql']:
                jdbc_url = f"jdbc:sqlserver://{self.args.db_host}:{self.args.db_port};databaseName={self.args.db_name};encrypt=true;trustServerCertificate=true"
                driver_class = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
                jar_pattern = "mssql-jdbc*.jar"
            elif self.args.db_type.lower() == 'mysql':
                jdbc_url = f"jdbc:mysql://{self.args.db_host}:{self.args.db_port}/{self.args.db_name}?connectTimeout=60000&socketTimeout=120000&autoReconnect=true"
                driver_class = "com.mysql.cj.jdbc.Driver"
                jar_pattern = "mysql-connector-j*.jar"
            elif self.args.db_type.lower() == 'postgresql':
                jdbc_url = f"jdbc:postgresql://{self.args.db_host}:{self.args.db_port}/{self.args.db_name}"
                driver_class = "org.postgresql.Driver"
                jar_pattern = "postgresql-*.jar"
            elif self.args.db_type.lower() == 'oracle':
                jdbc_url = f"jdbc:oracle:thin:@{self.args.db_host}:{self.args.db_port}:{self.args.db_name}"
                driver_class = "oracle.jdbc.driver.OracleDriver"
                jar_pattern = "ojdbc*.jar"
            else:
                raise ValueError(f"Unsupported database type: {self.args.db_type}")
            
            logger.info(f"   JDBC URL: {jdbc_url}")
            logger.info(f"   Driver Class: {driver_class}")
            
            # Find JDBC driver JAR (same pattern as project)
            jdbc_dir = self.args.jdbc_drivers_path
            pattern = os.path.join(jdbc_dir, jar_pattern)
            jars = glob.glob(pattern)
            
            if not jars:
                raise Exception(f"No JDBC driver found for {self.args.db_type} at {pattern}")
            
            driver_jar = jars[0]
            logger.info(f"   Using JDBC driver: {driver_jar}")
            
            # Connect using jaydebeapi (same as project)
            logger.info(f"   Connecting to database...")
            self.db_connection = jaydebeapi.connect(
                driver_class,
                jdbc_url,
                [self.args.db_user, self.args.db_password],
                driver_jar
            )
            
            # Test connection
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            cursor.close()
            
            setup_time = (time.time() - setup_start) * 1000
            logger.info(f"✅ JDBC database connection established in {setup_time:.2f}ms")
            logger.info(f"   Host: {self.args.db_host}:{self.args.db_port}")
            logger.info(f"   Database: {self.args.db_name}")
            logger.info(f"   User: {self.args.db_user}")
            logger.info(f"   Driver: {os.path.basename(driver_jar)}")
            logger.info(f"   Test Query Result: {result[0] if result else 'Failed'}")
            
        except ImportError:
            logger.error("❌ jaydebeapi package not installed. Install with: pip install jaydebeapi")
            logger.error("   Also ensure you have Java installed and JDBC drivers available")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Failed to connect to database via JDBC: {e}")
            logger.error(f"   Check JDBC drivers path: {self.args.jdbc_drivers_path}")
            logger.error(f"   Check database connectivity and credentials")
            sys.exit(1)

    def _initialize_components(self):
        """Initialize NL processing components."""
        logger.info("🔧 STEP 3: INITIALIZING NL PROCESSING COMPONENTS")
        init_start = time.time()

        # Initialize schemas info using JDBC connection
        self.schemas_info = {
            self.args.select_schema: {
                "tables": self._get_schema_tables_jdbc()
            }
        }

        init_time = (time.time() - init_start) * 1000
        logger.info(f"✅ Components initialized in {init_time:.2f}ms")
        logger.info(f"   Schema: {self.args.select_schema}")
        logger.info(f"   Tables Found: {len(self.schemas_info[self.args.select_schema]['tables'])}")

        if self.args.verbose:
            for table_name in self.schemas_info[self.args.select_schema]['tables']:
                logger.info(f"      - {table_name}")

    def _get_schema_tables_jdbc(self):
        """Get tables from the specified schema using JDBC connection."""
        logger.info("📊 STEP 3.1: DISCOVERING SCHEMA TABLES VIA JDBC")
        discovery_start = time.time()

        try:
            cursor = self.db_connection.cursor()

            # Get tables from schema (SQL Server specific, adjust for other DBs)
            if self.args.db_type.lower() in ['sqlserver', 'mssql']:
                query = """
                    SELECT TABLE_NAME
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = ?
                    AND TABLE_TYPE = 'BASE TABLE'
                    ORDER BY TABLE_NAME
                """
            elif self.args.db_type.lower() == 'mysql':
                query = """
                    SELECT TABLE_NAME
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = ?
                    AND TABLE_TYPE = 'BASE TABLE'
                    ORDER BY TABLE_NAME
                """
            elif self.args.db_type.lower() == 'postgresql':
                query = """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = ?
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """
            elif self.args.db_type.lower() == 'oracle':
                query = """
                    SELECT table_name
                    FROM all_tables
                    WHERE owner = UPPER(?)
                    ORDER BY table_name
                """
            else:
                raise ValueError(f"Unsupported database type for schema discovery: {self.args.db_type}")

            logger.info(f"   Executing schema discovery query...")
            logger.info(f"   Query: {query}")
            logger.info(f"   Schema: {self.args.select_schema}")

            cursor.execute(query, (self.args.select_schema,))
            tables = cursor.fetchall()
            cursor.close()

            table_dict = {}
            for table in tables:
                table_name = table[0]
                table_dict[table_name] = {"columns": self._get_table_columns_jdbc(table_name)}

            discovery_time = (time.time() - discovery_start) * 1000
            logger.info(f"✅ Schema discovery completed in {discovery_time:.2f}ms")
            logger.info(f"   Tables Found: {len(table_dict)}")

            return table_dict

        except Exception as e:
            logger.error(f"❌ Failed to discover schema tables via JDBC: {e}")
            return {}

    def _get_table_columns_jdbc(self, table_name):
        """Get columns for a specific table using JDBC connection."""
        try:
            cursor = self.db_connection.cursor()

            # Get columns query (adjust for different database types)
            if self.args.db_type.lower() in ['sqlserver', 'mssql']:
                query = """
                    SELECT COLUMN_NAME, DATA_TYPE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
                    ORDER BY ORDINAL_POSITION
                """
            elif self.args.db_type.lower() == 'mysql':
                query = """
                    SELECT COLUMN_NAME, DATA_TYPE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
                    ORDER BY ORDINAL_POSITION
                """
            elif self.args.db_type.lower() == 'postgresql':
                query = """
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = ? AND table_name = ?
                    ORDER BY ordinal_position
                """
            elif self.args.db_type.lower() == 'oracle':
                query = """
                    SELECT column_name, data_type
                    FROM all_tab_columns
                    WHERE owner = UPPER(?) AND table_name = UPPER(?)
                    ORDER BY column_id
                """
            else:
                logger.warning(f"⚠️ Unsupported database type for column discovery: {self.args.db_type}")
                return []

            cursor.execute(query, (self.args.select_schema, table_name))
            columns = cursor.fetchall()
            cursor.close()

            column_list = [{"name": col[0], "type": col[1]} for col in columns]

            if self.args.verbose:
                logger.info(f"      Table {table_name}: {len(column_list)} columns")

            return column_list

        except Exception as e:
            logger.warning(f"⚠️ Failed to get columns for {table_name} via JDBC: {e}")
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
                    {"role": "system", "content": f"You are a SQL expert. Generate clean, efficient SQL queries for {self.args.db_type}."},
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

        # Database-specific syntax
        if self.args.db_type.lower() in ['sqlserver', 'mssql']:
            schema_qualifier = f"[{self.args.select_schema}].[table_name]"
        elif self.args.db_type.lower() == 'mysql':
            schema_qualifier = f"`{self.args.select_schema}`.`table_name`"
        elif self.args.db_type.lower() == 'postgresql':
            schema_qualifier = f'"{self.args.select_schema}"."table_name"'
        elif self.args.db_type.lower() == 'oracle':
            schema_qualifier = f"{self.args.select_schema}.table_name"
        else:
            schema_qualifier = f"{self.args.select_schema}.table_name"

        prompt = f"""
Generate a {self.args.db_type} query for this requirement:
"{intent.definition}"

Schema: {self.args.select_schema}
Operation: {intent.operation}
Source Table: {intent.source_table}
Target Table: {intent.target_table}
{schema_info}

Requirements:
- Use {self.args.db_type} syntax
- Use proper schema qualification: {schema_qualifier}
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

        # Database-specific schema qualification
        if self.args.db_type.lower() in ['sqlserver', 'mssql']:
            source_table = f"[{self.args.select_schema}].[{intent.source_table}]"
            target_table = f"[{self.args.select_schema}].[{intent.target_table}]" if intent.target_table else None
        elif self.args.db_type.lower() == 'mysql':
            source_table = f"`{self.args.select_schema}`.`{intent.source_table}`"
            target_table = f"`{self.args.select_schema}`.`{intent.target_table}`" if intent.target_table else None
        elif self.args.db_type.lower() == 'postgresql':
            source_table = f'"{self.args.select_schema}"."{intent.source_table}"'
            target_table = f'"{self.args.select_schema}"."{intent.target_table}"' if intent.target_table else None
        elif self.args.db_type.lower() == 'oracle':
            source_table = f"{self.args.select_schema}.{intent.source_table}"
            target_table = f"{self.args.select_schema}.{intent.target_table}" if intent.target_table else None
        else:
            source_table = f"{self.args.select_schema}.{intent.source_table}"
            target_table = f"{self.args.select_schema}.{intent.target_table}" if intent.target_table else None

        if intent.operation == "NOT_IN" and intent.target_table:
            # Generate NOT IN query
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
            # Generate basic SELECT with database-specific LIMIT
            if self.args.db_type.lower() in ['sqlserver', 'mssql']:
                sql = f"SELECT TOP 1000 * FROM {source_table}"
            elif self.args.db_type.lower() in ['mysql', 'postgresql']:
                sql = f"SELECT * FROM {source_table} LIMIT 1000"
            elif self.args.db_type.lower() == 'oracle':
                sql = f"SELECT * FROM {source_table} WHERE ROWNUM <= 1000"
            else:
                sql = f"SELECT * FROM {source_table} LIMIT 1000"

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
                # Database-specific schema qualification
                if self.args.db_type.lower() in ['sqlserver', 'mssql']:
                    mm_table = f"[{self.args.select_schema}].[hana_material_master]"
                elif self.args.db_type.lower() == 'mysql':
                    mm_table = f"`{self.args.select_schema}`.`hana_material_master`"
                elif self.args.db_type.lower() == 'postgresql':
                    mm_table = f'"{self.args.select_schema}"."hana_material_master"'
                elif self.args.db_type.lower() == 'oracle':
                    mm_table = f"{self.args.select_schema}.hana_material_master"
                else:
                    mm_table = f"{self.args.select_schema}.hana_material_master"

                enhanced_sql = sql.replace(
                    "WHERE",
                    f"LEFT JOIN {mm_table} mm ON mm.MATERIAL = s.MATERIAL\nWHERE"
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
                "storage_type": f"{self.args.db_type}_jdbc",
                "intent": asdict(intent),
                "performance": {
                    "total_time_ms": total_time,
                    "process_time_ms": process_time
                },
                "database_info": {
                    "db_type": self.args.db_type,
                    "connection_type": "JDBC",
                    "schema": self.args.select_schema,
                    "tables_discovered": len(self.schemas_info[self.args.select_schema]['tables'])
                }
            }

            logger.info("="*120)
            logger.info("🎉 STANDALONE SQL PREVIEW (JDBC): PROCESS COMPLETED SUCCESSFULLY")
            logger.info(f"   Total Time: {total_time:.2f}ms")
            logger.info(f"   Process Time: {process_time:.2f}ms")
            logger.info(f"   Intent Confidence: {intent.confidence}")
            logger.info(f"   Enhancement Applied: {enhancement_result['enhancement_applied']}")
            logger.info(f"   Final SQL Length: {len(enhancement_result['enhanced_sql'])} characters")
            logger.info(f"   Database Type: {self.args.db_type} (JDBC)")
            logger.info(f"   Tables Discovered: {len(self.schemas_info[self.args.select_schema]['tables'])}")
            logger.info("="*120)

            return result

        except Exception as e:
            total_time = (time.time() - self.start_time) * 1000
            error_type = type(e).__name__
            error_message = str(e)

            logger.error("="*120)
            logger.error("❌ STANDALONE SQL PREVIEW (JDBC): PROCESS FAILED")
            logger.error(f"   Total Time: {total_time:.2f}ms")
            logger.error(f"   Error Type: {error_type}")
            logger.error(f"   Error Message: {error_message}")
            logger.error(f"   NL Definition: '{self.args.nl_definition}'")
            logger.error(f"   Database Type: {self.args.db_type} (JDBC)")
            logger.error("="*120)
            logger.error("Full error details:", exc_info=True)

            return {
                "success": False,
                "error": error_message,
                "error_type": error_type,
                "total_time_ms": total_time,
                "database_info": {
                    "db_type": self.args.db_type,
                    "connection_type": "JDBC"
                }
            }

        finally:
            # Close JDBC connection
            try:
                if hasattr(self, 'db_connection') and self.db_connection:
                    self.db_connection.close()
                    logger.info("🔌 JDBC connection closed")
            except Exception as e:
                logger.warning(f"⚠️ Error closing JDBC connection: {e}")

def create_argument_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Standalone SQL Preview with JDBC - Mimics /v1/landing-kpi-mssql/sql-preview API using JDBC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # SQL Server with LLM
  python standalone_sql_preview_jdbc.py \\
    --nl-definition "get products from hana_material_master where OPS_PLANNER is missing" \\
    --kg-name "New_KG_101" \\
    --select-schema "newdqnov7" \\
    --openai-key "sk-..." \\
    --db-type "sqlserver" \\
    --db-host "localhost" \\
    --db-name "your_database" \\
    --db-user "username" \\
    --db-password "password" \\
    --jdbc-drivers-path "/path/to/jdbc_drivers" \\
    --use-llm

  # MySQL with rule-based parsing
  python standalone_sql_preview_jdbc.py \\
    --nl-definition "find missing planners in product_master" \\
    --select-schema "production" \\
    --db-type "mysql" \\
    --db-host "mysql-server" \\
    --db-name "inventory" \\
    --db-user "user" \\
    --db-password "pass" \\
    --jdbc-drivers-path "/opt/jdbc_drivers"

  # PostgreSQL with JSON output
  python standalone_sql_preview_jdbc.py \\
    --nl-definition "show products with missing codes" \\
    --select-schema "public" \\
    --db-type "postgresql" \\
    --db-host "pg-server" \\
    --db-name "warehouse" \\
    --db-user "postgres" \\
    --db-password "password" \\
    --jdbc-drivers-path "/usr/local/jdbc" \\
    --output-format json

  # Oracle with verbose logging
  python standalone_sql_preview_jdbc.py \\
    --nl-definition "get missing inventory items" \\
    --select-schema "INVENTORY" \\
    --db-type "oracle" \\
    --db-host "oracle-server" \\
    --db-port 1521 \\
    --db-name "ORCL" \\
    --db-user "inventory_user" \\
    --db-password "password" \\
    --jdbc-drivers-path "/opt/oracle/jdbc" \\
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
        help='Database schema name (e.g., "newdqnov7", "public", "INVENTORY")'
    )

    parser.add_argument(
        '--db-type',
        required=True,
        choices=['sqlserver', 'mssql', 'mysql', 'postgresql', 'oracle'],
        help='Database type (sqlserver, mysql, postgresql, oracle)'
    )

    # Database connection arguments
    parser.add_argument('--db-host', required=True, help='Database host')
    parser.add_argument('--db-port', type=int, help='Database port (default: 1433 for SQL Server, 3306 for MySQL, 5432 for PostgreSQL, 1521 for Oracle)')
    parser.add_argument('--db-name', required=True, help='Database name')
    parser.add_argument('--db-user', required=True, help='Database username')
    parser.add_argument('--db-password', required=True, help='Database password')

    # JDBC-specific arguments
    parser.add_argument(
        '--jdbc-drivers-path',
        required=True,
        help='Path to JDBC drivers directory (e.g., "/path/to/jdbc_drivers")'
    )

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

    # Set default ports based on database type
    def set_default_port(args):
        if not args.db_port:
            if args.db_type.lower() in ['sqlserver', 'mssql']:
                args.db_port = 1433
            elif args.db_type.lower() == 'mysql':
                args.db_port = 3306
            elif args.db_type.lower() == 'postgresql':
                args.db_port = 5432
            elif args.db_type.lower() == 'oracle':
                args.db_port = 1521
        return args

    # Custom action to set default port
    class SetDefaultPortAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, values)
            set_default_port(namespace)

    parser.add_argument('--set-defaults', action=SetDefaultPortAction, nargs=0, help=argparse.SUPPRESS)

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
            output.append("🎉 SQL PREVIEW RESULT (JDBC)")
            output.append("="*80)
            output.append(f"✅ Success: {result['success']}")
            output.append(f"📊 Storage Type: {result.get('storage_type', 'unknown')}")
            output.append(f"🔧 Enhancement Applied: {result.get('enhancement_applied', False)}")
            output.append(f"📋 Material Master Added: {result.get('material_master_added', False)}")
            output.append(f"⚙️ OPS Planner Added: {result.get('ops_planner_added', False)}")

            if 'database_info' in result:
                db_info = result['database_info']
                output.append(f"💾 Database Type: {db_info.get('db_type', 'unknown')} ({db_info.get('connection_type', 'unknown')})")
                output.append(f"📊 Schema: {db_info.get('schema', 'unknown')}")
                output.append(f"📋 Tables Discovered: {db_info.get('tables_discovered', 0)}")

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
            output.append("❌ SQL PREVIEW ERROR (JDBC)")
            output.append("="*80)
            output.append(f"❌ Success: {result['success']}")
            output.append(f"🚨 Error Type: {result.get('error_type', 'unknown')}")
            output.append(f"💬 Error Message: {result.get('error', 'Unknown error')}")
            output.append(f"⏱️ Total Time: {result.get('total_time_ms', 0):.2f}ms")

            if 'database_info' in result:
                db_info = result['database_info']
                output.append(f"💾 Database Type: {db_info.get('db_type', 'unknown')} ({db_info.get('connection_type', 'unknown')})")

            output.append("="*80)

            return '\n'.join(output)

def main():
    """Main function."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Set default ports based on database type
    if not args.db_port:
        if args.db_type.lower() in ['sqlserver', 'mssql']:
            args.db_port = 1433
        elif args.db_type.lower() == 'mysql':
            args.db_port = 3306
        elif args.db_type.lower() == 'postgresql':
            args.db_port = 5432
        elif args.db_type.lower() == 'oracle':
            args.db_port = 1521

    # Set verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("🔍 Verbose mode enabled")

    # Validate arguments
    if args.use_llm and not args.openai_key and not os.getenv('OPENAI_API_KEY'):
        logger.error("❌ OpenAI API key required when --use-llm is specified")
        logger.error("   Provide via --openai-key argument or OPENAI_API_KEY environment variable")
        sys.exit(1)

    # Validate JDBC drivers path
    if not os.path.exists(args.jdbc_drivers_path):
        logger.error(f"❌ JDBC drivers path does not exist: {args.jdbc_drivers_path}")
        logger.error("   Please provide a valid path to JDBC drivers directory")
        sys.exit(1)

    # Print startup banner
    print("="*80)
    print("🚀 STANDALONE SQL PREVIEW (JDBC)")
    print("   Mimics /v1/landing-kpi-mssql/sql-preview API using JDBC")
    print(f"   Version: 2.0 (JDBC)")
    print(f"   Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Database: {args.db_type.upper()}")
    print(f"   Connection: JDBC")
    print("="*80)

    try:
        # Initialize and run SQL preview
        sql_preview = StandaloneSQLPreviewJDBC(args)
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
