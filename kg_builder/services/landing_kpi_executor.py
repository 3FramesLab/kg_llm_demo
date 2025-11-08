"""
Landing KPI Executor Service

Handles execution of Landing KPI definitions using the NL Query Executor.
Integrates KPI definitions with NL query execution pipeline.
"""

import logging
import time
from typing import Any, Dict, Optional
from kg_builder.services.landing_kpi_service_jdbc import LandingKPIServiceJDBC
from kg_builder.services.nl_query_classifier import get_nl_query_classifier
from kg_builder.services.nl_query_parser import get_nl_query_parser
from kg_builder.services.nl_query_executor import get_nl_query_executor

logger = logging.getLogger(__name__)


class LandingKPIExecutor:
    """Execute Landing KPI definitions using NL Query Executor."""
    
    def __init__(self):
        """Initialize Landing KPI executor."""
        self.kpi_service = LandingKPIServiceJDBC()
    
    def execute_kpi_async(
        self,
        kpi_id: int,
        execution_id: int,
        execution_params: Dict[str, Any]
    ) -> None:
        """
        Execute KPI asynchronously and update results.
        
        This method should be called in a background task/thread.
        
        Args:
            kpi_id: KPI definition ID
            execution_id: Execution record ID
            execution_params: Execution parameters (kg_name, schema, etc.)
        """
        try:
            logger.info(f"Starting KPI execution: KPI ID={kpi_id}, Execution ID={execution_id}")
            
            # Get KPI definition
            kpi = self.kpi_service.get_kpi(kpi_id)
            if not kpi:
                raise ValueError(f"KPI ID {kpi_id} not found")

            # Debug: Log the KPI data structure
            logger.info(f"🔍 KPI Data Retrieved:")
            logger.info(f"   KPI ID: {kpi.get('id')}")
            logger.info(f"   KPI Name: {kpi.get('name')}")
            logger.info(f"   isAccept: {kpi.get('isAccept', 'NOT_SET')}")
            logger.info(f"   isSQLCached: {kpi.get('isSQLCached', 'NOT_SET')}")
            logger.info(f"   cached_sql exists: {bool(kpi.get('cached_sql'))}")
            if kpi.get('cached_sql'):
                logger.info(f"   cached_sql preview: {kpi['cached_sql'][:100]}...")
            logger.info(f"   KPI keys: {list(kpi.keys())}")
            
            # Execute the KPI
            result = self._execute_kpi_internal(kpi, execution_params)
            
            # Update execution record with results
            self.kpi_service.update_execution_result(execution_id, result)
            logger.info(f"✓ KPI execution completed: Execution ID={execution_id}")
            
        except Exception as e:
            logger.error(f"✗ KPI execution failed: {str(e)}", exc_info=True)
            # Update execution record with error
            error_result = {
                'execution_status': 'failed',
                'error_message': str(e),
                'number_of_records': 0,
                'result_data': []
            }
            try:
                self.kpi_service.update_execution_result(execution_id, error_result)
            except Exception as update_err:
                logger.error(f"Failed to update execution record with error: {update_err}")
    
    def _execute_kpi_internal(
        self,
        kpi: Dict[str, Any],
        execution_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Internal method to execute KPI and return results.

        Args:
            kpi: KPI definition
            execution_params: Execution parameters with new structure

        Returns:
            Dictionary with execution results
        """
        start_time = time.time()

        try:
            # Extract parameters from new payload structure
            kg_name = execution_params.get('kg_name')
            schemas = execution_params.get('schemas', [])
            definitions = execution_params.get('definitions', [])
            use_llm = execution_params.get('use_llm', True)
            min_confidence = execution_params.get('min_confidence', 0.7)
            limit = execution_params.get('limit', 1000)
            db_type = execution_params.get('db_type', 'sqlserver')

            logger.info(f"Executing KPI: {kpi['name']}")
            logger.info(f"KG: {kg_name}, Schemas: {schemas}, DB Type: {db_type}")
            logger.info(f"Definitions: {definitions}")
            logger.info(f"Use LLM: {use_llm}, Min Confidence: {min_confidence}, Limit: {limit}")

            # Use first definition from the list (or KPI's definition if not provided)
            nl_definition = definitions[0] if definitions else kpi.get('nl_definition')
            if not nl_definition:
                raise ValueError("No NL definition provided")

            # Use first schema from the list
            schema = schemas[0] if schemas else None
            if not schema:
                raise ValueError("No schema provided")

            # Step 1: Load Knowledge Graph from storage
            from kg_builder.services.graphiti_backend import get_graphiti_backend
            from kg_builder.models import KnowledgeGraph, GraphNode, GraphRelationship

            logger.info(f"Loading Knowledge Graph: {kg_name}")
            graphiti = get_graphiti_backend()
            entities_data = graphiti.get_entities(kg_name)
            relationships_data = graphiti.get_relationships(kg_name)

            logger.info(f"  - Entities found: {len(entities_data) if entities_data else 0}")
            logger.info(f"  - Relationships found: {len(relationships_data) if relationships_data else 0}")

            # Convert to KnowledgeGraph object
            nodes = [GraphNode(**entity) for entity in entities_data] if entities_data else []
            relationships = [GraphRelationship(**rel) for rel in relationships_data] if relationships_data else []

            # Load metadata including table_aliases
            table_aliases = {}
            try:
                kg_metadata = graphiti.get_kg_metadata(kg_name)
                if kg_metadata:
                    table_aliases = kg_metadata.get('table_aliases', {})
                    logger.info(f"  - Table aliases loaded: {len(table_aliases)}")
                    if table_aliases:
                        logger.debug(f"    Aliases: {table_aliases}")
            except Exception as e:
                logger.warning(f"Could not load KG metadata: {e}")

            kg = KnowledgeGraph(
                name=kg_name,
                nodes=nodes,
                relationships=relationships,
                schema_file=schema,
                table_aliases=table_aliases
            )
            logger.info(f"✓ Loaded KG '{kg_name}' with {len(nodes)} nodes and {len(relationships)} relationships")

            # Step 2: Classify the query
            classifier = get_nl_query_classifier()
            query_type = classifier.classify(nl_definition)
            logger.info(f"Query Type: {query_type}")

            # Step 3: Parse the query
            logger.info(f"Parsing with LLM enabled: {use_llm}")

            # Extract schemas_info from KG for LLM prompt
            schemas_info = _extract_schemas_info_from_kg(kg)
            logger.info(f"Extracted schemas_info with {len(schemas_info)} schema(s)")

            parser = get_nl_query_parser(kg=kg, schemas_info=schemas_info)

            # Check if LLM service is available
            from kg_builder.services.llm_service import get_llm_service
            llm_service = get_llm_service()
            logger.info(f"LLM Service enabled: {llm_service.is_enabled()}")

            intent = parser.parse(
                nl_definition,
                use_llm=use_llm
            )
            logger.info(f"✓ Parsed Intent:")
            logger.info(f"  - Query Type: {intent.query_type}")
            logger.info(f"  - Source Table: {intent.source_table}")
            logger.info(f"  - Target Table: {intent.target_table}")
            logger.info(f"  - Operation: {intent.operation}")
            logger.info(f"  - Join Columns: {intent.join_columns}")
            logger.info(f"  - Confidence: {intent.confidence}")
            logger.info(f"  - Filters: {intent.filters}")

            # Step 4: Get database connection
            connection = _get_source_database_connection(db_type=db_type)

            if not connection:
                raise ValueError("Could not establish database connection")

            # Step 5: Check if SQL is cached and should be used instead of LLM generation
            logger.info(f"🔍 Cache Status Check:")
            logger.info(f"   isSQLCached: {kpi.get('isSQLCached', False)} (type: {type(kpi.get('isSQLCached'))})")
            logger.info(f"   cached_sql exists: {bool(kpi.get('cached_sql'))}")
            logger.info(f"   cached_sql length: {len(kpi.get('cached_sql', ''))}")
            logger.info(f"   isAccept: {kpi.get('isAccept', False)}")

            # More explicit cache check
            is_cached = kpi.get('isSQLCached', False)
            has_cached_sql = bool(kpi.get('cached_sql', '').strip())

            logger.info(f"🎯 Cache Decision:")
            logger.info(f"   is_cached: {is_cached}")
            logger.info(f"   has_cached_sql: {has_cached_sql}")
            logger.info(f"   will_use_cache: {is_cached and has_cached_sql}")

            if is_cached and has_cached_sql:
                logger.info(f"🔄 USING CACHED SQL instead of LLM generation")
                logger.info(f"   Cached SQL preview: {kpi['cached_sql'][:200]}...")

                # Execute cached SQL directly
                query_result = self._execute_cached_sql(
                    kpi['cached_sql'],
                    connection,
                    limit,
                    intent.definition
                )
                logger.info(f"✅ Cached SQL execution completed")
            else:
                logger.info(f"🤖 USING LLM GENERATION")
                if not is_cached:
                    logger.info(f"   Reason: isSQLCached is False")
                if not has_cached_sql:
                    logger.info(f"   Reason: No cached SQL available")

                # Step 5: Execute the query (Force LLM-only SQL generation)
                executor = get_nl_query_executor(db_type, kg=kg, use_llm=True)  # Pass KG and force LLM for SQL generation
                query_result = executor.execute(
                    intent,
                    connection,
                    limit=limit
                )
                logger.info(f"✅ LLM SQL generation completed")

            # Step 6: Prepare result data
            execution_time_ms = (time.time() - start_time) * 1000
            logger.info(f"✓ Query executed in {execution_time_ms:.2f}ms, returned {query_result.record_count} records")
            
            result = {
                'generated_sql': query_result.sql,
                'number_of_records': query_result.record_count,
                'joined_columns': query_result.join_columns or [],
                'sql_query_type': str(query_result.query_type),
                'operation': query_result.operation,
                'execution_status': 'success' if not query_result.error else 'failed',
                'execution_time_ms': execution_time_ms,
                'confidence_score': query_result.confidence,
                'error_message': query_result.error,
                'result_data': query_result.records,
                'source_table': query_result.source_table,
                'target_table': query_result.target_table
            }
            
            logger.info(f"✓ KPI execution successful: {query_result.record_count} records in {execution_time_ms:.2f}ms")
            return result
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            logger.error(f"✗ KPI execution error: {str(e)}", exc_info=True)
            
            return {
                'execution_status': 'failed',
                'error_message': str(e),
                'execution_time_ms': execution_time_ms,
                'number_of_records': 0,
                'result_data': []
            }

    def _execute_cached_sql(self, cached_sql: str, connection, limit: int, definition: str) -> Dict[str, Any]:
        """Execute cached SQL directly without LLM generation."""
        import time
        from kg_builder.services.nl_query_executor import NLQueryExecutor

        start_time = time.time()

        try:
            logger.info(f"🔄 Executing cached SQL")

            # Add LIMIT clause to cached SQL if needed
            executor = NLQueryExecutor()
            sql_with_limit = executor._add_limit_clause(cached_sql, limit)

            # Log the SQL being executed
            logger.info("="*80)
            logger.info(f"📝 Query Definition: {definition}")
            logger.info(f"🔄 Using Cached SQL (isSQLCached=true)")
            logger.info("-"*80)
            logger.info("🔹 CACHED SQL TO BE EXECUTED:")
            logger.info(f"\n{sql_with_limit}\n")
            logger.info("="*80)

            # Execute the SQL
            cursor = connection.cursor()
            cursor.execute(sql_with_limit)

            # Fetch results
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            # Convert to list of dictionaries
            records = []
            for row in rows:
                record = {}
                for i, value in enumerate(row):
                    record[columns[i]] = value
                records.append(record)

            execution_time_ms = (time.time() - start_time) * 1000

            logger.info(f"✅ Cached SQL executed successfully")
            logger.info(f"   Records returned: {len(records)}")
            logger.info(f"   Execution time: {execution_time_ms:.2f}ms")

            return {
                'execution_status': 'success',
                'generated_sql': cached_sql,
                'number_of_records': len(records),
                'result_data': records,
                'execution_time_ms': execution_time_ms,
                'sql_query_type': 'cached_sql',
                'operation': 'CACHED',
                'confidence_score': 1.0,  # High confidence for cached SQL
                'joined_columns': '',
                'used_cached_sql': True
            }

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            logger.error(f"❌ Cached SQL execution failed: {e}")

            return {
                'execution_status': 'failed',
                'error_message': f"Cached SQL execution failed: {str(e)}",
                'generated_sql': cached_sql,
                'execution_time_ms': execution_time_ms,
                'number_of_records': 0,
                'result_data': [],
                'used_cached_sql': True
            }


def _get_source_database_connection(db_type: str = 'sqlserver') -> Optional[Any]:
    """
    Get a connection to the source database for KPI execution.

    Args:
        db_type: Database type (sqlserver, mysql, postgresql, oracle)

    Returns:
        Database connection object or None if not configured
    """
    try:
        import jaydebeapi
        import glob
        import os
        from kg_builder.config import get_source_db_config, JDBC_DRIVERS_PATH

        db_config = get_source_db_config()
        if not db_config:
            logger.warning("Source database is not configured")
            return None

        # Build JDBC URL based on database type
        db_type_lower = db_type.lower()

        if db_type_lower == "sqlserver":
            jdbc_url = f"jdbc:sqlserver://{db_config.host}:{db_config.port};databaseName={db_config.database};encrypt=true;trustServerCertificate=true"
            driver_class = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
            jar_pattern = "mssql-jdbc*.jar"
        elif db_type_lower == "mysql":
            jdbc_url = f"jdbc:mysql://{db_config.host}:{db_config.port}/{db_config.database}?connectTimeout=60000&socketTimeout=120000&autoReconnect=true"
            driver_class = "com.mysql.cj.jdbc.Driver"
            jar_pattern = "mysql-connector-j*.jar"
        elif db_type_lower == "postgresql":
            jdbc_url = f"jdbc:postgresql://{db_config.host}:{db_config.port}/{db_config.database}"
            driver_class = "org.postgresql.Driver"
            jar_pattern = "postgresql-*.jar"
        elif db_type_lower == "oracle":
            service_name = db_config.service_name or db_config.database
            jdbc_url = f"jdbc:oracle:thin:@{db_config.host}:{db_config.port}:{service_name}"
            driver_class = "oracle.jdbc.driver.OracleDriver"
            jar_pattern = "ojdbc*.jar"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        # Find JDBC driver JAR using proper pattern
        driver_pattern = os.path.join(JDBC_DRIVERS_PATH, jar_pattern)
        jars = glob.glob(driver_pattern)

        if not jars:
            logger.error(f"No JDBC driver found for {db_type} at {driver_pattern}")
            logger.error(f"Available files in {JDBC_DRIVERS_PATH}: {os.listdir(JDBC_DRIVERS_PATH) if os.path.exists(JDBC_DRIVERS_PATH) else 'directory not found'}")
            return None

        driver_jar = jars[0]
        logger.info(f"Using JDBC driver: {driver_jar}")

        logger.info(f"Connecting to source database: {db_type} at {db_config.host}:{db_config.port}/{db_config.database}")

        # Connect
        conn = jaydebeapi.connect(
            driver_class,
            jdbc_url,
            [db_config.username, db_config.password],
            driver_jar
        )

        logger.info("Successfully connected to source database")
        return conn

    except Exception as e:
        logger.error(f"Failed to connect to source database: {e}")
        return None


def _extract_schemas_info_from_kg(kg) -> Dict[str, Any]:
    """
    Extract table and column information from KG nodes for LLM prompt.

    The LLM needs to know what tables exist and their columns to properly
    resolve business terms (e.g., "RBP GPU") to actual table names
    (e.g., "brz_lnd_RBP_GPU").

    Args:
        kg: Knowledge Graph with nodes containing table metadata

    Returns:
        Dictionary in schemas_info format for NL Query Parser
    """
    try:
        table_info = {}

        # Extract table nodes from KG
        for node in kg.nodes:
            if node.properties.get("type") == "Table":
                table_name = node.label
                columns = node.properties.get("columns", [])

                # Extract column names
                column_names = []
                for col in columns:
                    if isinstance(col, dict):
                        col_name = col.get("name")
                        if col_name:
                            column_names.append(col_name)
                    elif hasattr(col, 'name'):
                        column_names.append(col.name)

                table_info[table_name] = {"columns": column_names}
                logger.debug(f"Extracted table '{table_name}' with {len(column_names)} columns")

        if not table_info:
            logger.warning("No table information extracted from KG nodes")
            return {}

        # Create schemas_info structure that NL Query Parser expects
        # The parser expects: schemas_info[schema_name].tables[table_name].columns
        class ColumnSchema:
            def __init__(self, name):
                self.name = name

        class TableSchema:
            def __init__(self, columns_list):
                self.columns = [ColumnSchema(col) for col in columns_list]

        class TablesContainer:
            def __init__(self, tables_dict):
                for table_name, table_data in tables_dict.items():
                    setattr(self, table_name, TableSchema(table_data["columns"]))

            def keys(self):
                return [attr for attr in dir(self) if not attr.startswith('_')]

            def items(self):
                return [(name, getattr(self, name)) for name in self.keys()]

        class SchemaContainer:
            def __init__(self, tables_dict):
                self.tables = TablesContainer(tables_dict)

        schemas_info = {"schema": SchemaContainer(table_info)}
        logger.info(f"✓ Extracted schemas_info: {len(table_info)} tables")
        return schemas_info

    except Exception as e:
        logger.error(f"Error extracting schemas_info from KG: {e}")
        return {}


def get_landing_kpi_executor() -> LandingKPIExecutor:
    """Get Landing KPI executor instance."""
    return LandingKPIExecutor()

