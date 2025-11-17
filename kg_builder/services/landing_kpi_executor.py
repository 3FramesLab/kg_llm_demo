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
from kg_builder.services.kpi_performance_monitor import create_performance_monitor

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
        execution_start_time = time.time()

        # Initialize performance monitoring
        perf_monitor = create_performance_monitor(
            kpi_id=str(kpi_id),
            kpi_type="landing_kpi",
            execution_id=str(execution_id)
        )
        perf_monitor.start_memory_monitoring()

        logger.info("="*120)
        logger.info(f"🚀 LANDING KPI EXECUTOR: STARTING ASYNC KPI EXECUTION")
        logger.info(f"   KPI ID: {kpi_id}")
        logger.info(f"   Execution ID: {execution_id}")
        logger.info(f"   Execution Params: {execution_params}")
        logger.info(f"   Start Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"   Performance Monitor: {type(perf_monitor).__name__}")
        logger.info("="*120)

        try:
            # Step 1: Validate input parameters
            perf_monitor.start_step("parameter_validation")
            logger.info(f"📋 STEP 1: Validating Input Parameters")
            logger.info(f"   KPI ID Type: {type(kpi_id)} = {kpi_id}")
            logger.info(f"   Execution ID Type: {type(execution_id)} = {execution_id}")
            logger.info(f"   Execution Params Keys: {list(execution_params.keys())}")
            logger.info(f"   Execution Params: {execution_params}")

            if not isinstance(kpi_id, int) or kpi_id <= 0:
                raise ValueError(f"Invalid KPI ID: {kpi_id}")
            if not isinstance(execution_id, int) or execution_id <= 0:
                raise ValueError(f"Invalid Execution ID: {execution_id}")
            if not execution_params:
                raise ValueError("Execution parameters cannot be empty")

            logger.info(f"✅ Input parameters validated successfully")
            perf_monitor.end_step("parameter_validation")

            # Step 2: Retrieve KPI definition
            perf_monitor.start_step("kpi_definition_retrieval")
            logger.info(f"📖 STEP 2: Retrieving KPI Definition")
            logger.info(f"   Fetching KPI ID: {kpi_id}")

            kpi_fetch_start = time.time()
            kpi = self.kpi_service.get_kpi(kpi_id)
            kpi_fetch_time = (time.time() - kpi_fetch_start) * 1000

            if not kpi:
                raise ValueError(f"KPI ID {kpi_id} not found in database")

            logger.info(f"✅ KPI definition retrieved in {kpi_fetch_time:.2f}ms")
            perf_monitor.end_step("kpi_definition_retrieval")
            logger.info(f"🔍 KPI Definition Details:")
            logger.info(f"   KPI ID: {kpi.get('id')}")
            logger.info(f"   KPI Name: '{kpi.get('name', 'UNNAMED')}'")
            logger.info(f"   NL Definition: '{kpi.get('nl_definition', 'NOT_SET')}'")
            logger.info(f"   Description: '{kpi.get('description', 'NOT_SET')}'")
            logger.info(f"   Created Date: {kpi.get('created_date', 'NOT_SET')}")
            logger.info(f"   Modified Date: {kpi.get('modified_date', 'NOT_SET')}")
            logger.info(f"   isAccept: {kpi.get('isAccept', 'NOT_SET')}")
            logger.info(f"   isSQLCached: {kpi.get('isSQLCached', 'NOT_SET')}")
            logger.info(f"   cached_sql exists: {bool(kpi.get('cached_sql'))}")
            if kpi.get('cached_sql'):
                cached_sql_preview = kpi['cached_sql'][:200].replace('\n', ' ').replace('\r', '')
                logger.info(f"   cached_sql preview: {cached_sql_preview}...")
            logger.info(f"   All KPI keys: {list(kpi.keys())}")

            # Step 3: Execute KPI internal logic
            logger.info(f"⚙️ STEP 3: Starting Internal KPI Execution")
            internal_start_time = time.time()

            result = self._execute_kpi_internal(kpi, execution_params)

            internal_execution_time = (time.time() - internal_start_time) * 1000
            logger.info(f"✅ Internal execution completed in {internal_execution_time:.2f}ms")

            # Step 4: Update execution record with results
            logger.info(f"💾 STEP 4: Updating Execution Record")
            logger.info(f"   Execution ID: {execution_id}")
            logger.info(f"   Result Status: {result.get('execution_status', 'UNKNOWN')}")
            logger.info(f"   Records Count: {result.get('number_of_records', 0)}")
            logger.info(f"   Has Error: {bool(result.get('error_message'))}")

            update_start_time = time.time()
            self.kpi_service.update_execution_result(execution_id, result)
            update_time = (time.time() - update_start_time) * 1000

            logger.info(f"✅ Execution record updated in {update_time:.2f}ms")

            # Step 5: Log final success summary with performance metrics
            total_execution_time = (time.time() - execution_start_time) * 1000

            # Finalize performance monitoring
            perf_monitor.record_processing_stats(result.get('number_of_records', 0))
            final_metrics = perf_monitor.finalize()

            logger.info("="*100)
            logger.info(f"🎉 KPI EXECUTION COMPLETED SUCCESSFULLY")
            logger.info(f"   KPI ID: {kpi_id}")
            logger.info(f"   Execution ID: {execution_id}")
            logger.info(f"   Total Execution Time: {total_execution_time:.2f}ms")
            logger.info(f"   Records Processed: {result.get('number_of_records', 0)}")
            logger.info(f"   Final Status: {result.get('execution_status', 'UNKNOWN')}")
            logger.info("="*100)

            # Log detailed performance summary
            perf_monitor.log_performance_summary()

        except Exception as e:
            total_execution_time = (time.time() - execution_start_time) * 1000

            # Finalize performance monitoring even on error
            try:
                if 'perf_monitor' in locals():
                    final_metrics = perf_monitor.finalize()
            except Exception as perf_error:
                logger.warning(f"Error finalizing performance monitoring: {perf_error}")

            logger.error("="*100)
            logger.error(f"❌ KPI EXECUTION FAILED")
            logger.error(f"   KPI ID: {kpi_id}")
            logger.error(f"   Execution ID: {execution_id}")
            logger.error(f"   Total Execution Time: {total_execution_time:.2f}ms")
            logger.error(f"   Error Type: {type(e).__name__}")
            logger.error(f"   Error Message: {str(e)}")
            logger.error("="*100)
            logger.error(f"Full error details:", exc_info=True)

            # Log performance summary even on error for debugging
            try:
                if 'perf_monitor' in locals():
                    perf_monitor.log_performance_summary()
            except Exception as perf_error:
                logger.warning(f"Error logging performance summary: {perf_error}")

            # Create detailed error result
            error_result = {
                'execution_status': 'failed',
                'error_message': str(e),
                'error_type': type(e).__name__,
                'execution_time_ms': total_execution_time,
                'number_of_records': 0,
                'result_data': [],
                'failed_at_step': self._determine_failure_step(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }

            try:
                logger.info(f"💾 Updating execution record with error details")
                self.kpi_service.update_execution_result(execution_id, error_result)
                logger.info(f"✅ Error details saved to execution record")
            except Exception as update_err:
                logger.error(f"❌ Failed to update execution record with error: {update_err}")
                logger.error(f"   Original error: {str(e)}")
                logger.error(f"   Update error: {str(update_err)}")

    def _determine_failure_step(self, error: Exception) -> str:
        """Determine which step the execution failed at based on error type and message."""
        error_msg = str(error).lower()

        if "kpi id" in error_msg and "not found" in error_msg:
            return "KPI_DEFINITION_RETRIEVAL"
        elif "invalid kpi id" in error_msg or "invalid execution id" in error_msg:
            return "PARAMETER_VALIDATION"
        elif "knowledge graph" in error_msg or "kg_name" in error_msg:
            return "KNOWLEDGE_GRAPH_LOADING"
        elif "database connection" in error_msg or "connection" in error_msg:
            return "DATABASE_CONNECTION"
        elif "sql" in error_msg and ("syntax" in error_msg or "execution" in error_msg):
            return "SQL_EXECUTION"
        elif "parse" in error_msg or "intent" in error_msg:
            return "QUERY_PARSING"
        elif "llm" in error_msg or "language model" in error_msg:
            return "LLM_PROCESSING"
        else:
            return "UNKNOWN_STEP"
    
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
        logger.info("🔧 INTERNAL KPI EXECUTION STARTED")

        try:
            # Step A: Extract and validate execution parameters
            logger.info(f"📋 STEP A: Extracting and Validating Execution Parameters")
            param_start = time.time()

            kg_name = execution_params.get('kg_name')

            # Validate kg_name is provided and not default
            if not kg_name or kg_name.strip() == '' or kg_name.lower() == 'default':
                raise ValueError(
                    "kg_name is required and cannot be empty or 'default'. "
                    "Please provide a valid Knowledge Graph name (e.g., 'New_KG_101', 'KG_102')."
                )

            schemas = execution_params.get('schemas', [])
            definitions = execution_params.get('definitions', [])
            use_llm = execution_params.get('use_llm', True)
            min_confidence = execution_params.get('min_confidence', 0.7)
            limit = execution_params.get('limit', 1000)
            db_type = execution_params.get('db_type', 'sqlserver')

            param_time = (time.time() - param_start) * 1000
            logger.info(f"✅ Parameters extracted in {param_time:.2f}ms")
            logger.info(f"   📊 EXECUTION PARAMETERS SUMMARY:")
            logger.info(f"      KG Name: '{kg_name}' (type: {type(kg_name).__name__})")
            logger.info(f"      Schemas: {schemas} (count: {len(schemas) if schemas else 0})")
            logger.info(f"      Definitions: {definitions} (count: {len(definitions) if definitions else 0})")
            logger.info(f"      Use LLM: {use_llm}")
            logger.info(f"      Min Confidence: {min_confidence}")
            logger.info(f"      Limit: {limit}")
            logger.info(f"      DB Type: '{db_type}'")
            logger.info(f"      User ID: {execution_params.get('user_id', 'Not provided')}")
            logger.info(f"      Session ID: {execution_params.get('session_id', 'Not provided')}")

            # Validation checks
            logger.info(f"   🔍 PARAMETER VALIDATION:")
            validation_issues = []
            if not kg_name:
                validation_issues.append("KG Name is missing or empty")
            if not schemas:
                validation_issues.append("Schemas list is empty")
            if not definitions and not kpi.get('nl_definition'):
                validation_issues.append("No definitions provided and KPI has no NL definition")

            if validation_issues:
                logger.warning(f"      ⚠️ Validation Issues Found:")
                for issue in validation_issues:
                    logger.warning(f"         - {issue}")
            else:
                logger.info(f"      ✅ All parameters validated successfully")
            logger.info(f"   Schemas: {schemas} (count: {len(schemas)})")
            logger.info(f"   Definitions: {definitions} (count: {len(definitions)})")
            logger.info(f"   Use LLM: {use_llm}")
            logger.info(f"   Min Confidence: {min_confidence}")
            logger.info(f"   Limit: {limit}")
            logger.info(f"   DB Type: '{db_type}'")
            logger.info(f"   KPI Name: '{kpi.get('name', 'UNNAMED')}'")

            # Step B: Determine NL definition to use
            logger.info(f"📝 STEP B: Determining NL Definition")

            nl_definition = definitions[0] if definitions else kpi.get('nl_definition')
            if not nl_definition:
                raise ValueError("No NL definition provided in execution_params or KPI definition")

            logger.info(f"   Using NL Definition: '{nl_definition}'")
            logger.info(f"   Source: {'execution_params' if definitions else 'kpi_definition'}")

            # Step C: Determine schema to use
            logger.info(f"🗂️ STEP C: Determining Schema")

            schema = schemas[0] if schemas else None
            if not schema:
                raise ValueError("No schema provided in execution_params")

            logger.info(f"   Using Schema: '{schema}'")
            logger.info(f"   Available Schemas: {schemas}")

            # Step D: Validate required parameters
            logger.info(f"✅ STEP D: Validating Required Parameters")

            required_params = ['kg_name', 'schemas']
            missing_params = []

            for param in required_params:
                value = execution_params.get(param)
                if not value:
                    missing_params.append(param)
                logger.info(f"   {param}: {'✓' if value else '✗'} = {value}")

            if missing_params:
                raise ValueError(f"Missing required parameters: {missing_params}")

            logger.info(f"✅ All required parameters validated successfully")

            # Step E: Load Knowledge Graph from storage
            logger.info(f"🧠 STEP E: Loading Knowledge Graph")
            logger.info(f"   Target KG Name: '{kg_name}'")

            kg_load_start = time.time()

            from kg_builder.services.graphiti_backend import get_graphiti_backend
            from kg_builder.models import KnowledgeGraph, GraphNode, GraphRelationship

            logger.info(f"   Initializing Graphiti backend...")
            graphiti = get_graphiti_backend()
            logger.info(f"   ✅ Graphiti backend initialized")

            # Load entities
            logger.info(f"   Loading entities for KG: '{kg_name}'")
            entities_start = time.time()
            entities_data = graphiti.get_entities(kg_name)
            entities_time = (time.time() - entities_start) * 1000

            entities_count = len(entities_data) if entities_data else 0
            logger.info(f"   ✅ Entities loaded: {entities_count} entities in {entities_time:.2f}ms")

            # Load relationships
            logger.info(f"   Loading relationships for KG: '{kg_name}'")
            relationships_start = time.time()
            relationships_data = graphiti.get_relationships(kg_name)
            relationships_time = (time.time() - relationships_start) * 1000

            relationships_count = len(relationships_data) if relationships_data else 0
            logger.info(f"   ✅ Relationships loaded: {relationships_count} relationships in {relationships_time:.2f}ms")

            # Convert to KnowledgeGraph objects
            logger.info(f"   Converting data to KnowledgeGraph objects...")
            conversion_start = time.time()

            nodes = [GraphNode(**entity) for entity in entities_data] if entities_data else []
            relationships = [GraphRelationship(**rel) for rel in relationships_data] if relationships_data else []

            conversion_time = (time.time() - conversion_start) * 1000
            logger.info(f"   ✅ Data conversion completed in {conversion_time:.2f}ms")
            logger.info(f"      Nodes created: {len(nodes)}")
            logger.info(f"      Relationships created: {len(relationships)}")

            # Load metadata including table_aliases
            logger.info(f"   Loading KG metadata...")
            metadata_start = time.time()
            table_aliases = {}

            try:
                kg_metadata = graphiti.get_kg_metadata(kg_name)
                metadata_time = (time.time() - metadata_start) * 1000

                if kg_metadata:
                    table_aliases = kg_metadata.get('table_aliases', {})
                    logger.info(f"   ✅ KG metadata loaded in {metadata_time:.2f}ms")
                    logger.info(f"      Table aliases found: {len(table_aliases)}")
                    if table_aliases:
                        logger.info(f"      Aliases: {list(table_aliases.keys())}")
                        for alias, table in table_aliases.items():
                            logger.debug(f"        {alias} -> {table}")
                else:
                    logger.info(f"   ⚠️ No KG metadata found in {metadata_time:.2f}ms")

            except Exception as e:
                metadata_time = (time.time() - metadata_start) * 1000
                logger.warning(f"   ⚠️ Could not load KG metadata in {metadata_time:.2f}ms: {e}")

            # Create final KnowledgeGraph object
            logger.info(f"   Creating final KnowledgeGraph object...")
            kg_creation_start = time.time()

            kg = KnowledgeGraph(
                name=kg_name,
                nodes=nodes,
                relationships=relationships,
                schema_file=schema,
                table_aliases=table_aliases
            )

            kg_creation_time = (time.time() - kg_creation_start) * 1000
            total_kg_time = (time.time() - kg_load_start) * 1000

            logger.info(f"   ✅ KnowledgeGraph object created in {kg_creation_time:.2f}ms")
            logger.info(f"✅ STEP E COMPLETED: KG '{kg_name}' loaded in {total_kg_time:.2f}ms")
            logger.info(f"   Final KG Stats:")
            logger.info(f"      Name: '{kg.name}'")
            logger.info(f"      Nodes: {len(kg.nodes)}")
            logger.info(f"      Relationships: {len(kg.relationships)}")
            logger.info(f"      Schema File: '{kg.schema_file}'")
            logger.info(f"      Table Aliases: {len(kg.table_aliases)}")

            # Step F: Classify the query
            logger.info(f"🔍 STEP F: Classifying Query")
            logger.info(f"   NL Definition: '{nl_definition}'")

            classification_start = time.time()
            classifier = get_nl_query_classifier()
            query_type = classifier.classify(nl_definition)
            classification_time = (time.time() - classification_start) * 1000

            logger.info(f"✅ STEP F COMPLETED: Query classified in {classification_time:.2f}ms")
            logger.info(f"   Classified Query Type: '{query_type}'")

            # Step G: Parse the query
            logger.info(f"🧩 STEP G: Parsing Query")
            logger.info(f"   Use LLM: {use_llm}")
            logger.info(f"   Min Confidence: {min_confidence}")

            # Extract schemas_info from KG for LLM prompt
            logger.info(f"   Extracting schemas info from KG...")
            schema_extraction_start = time.time()
            schemas_info = _extract_schemas_info_from_kg(kg)
            schema_extraction_time = (time.time() - schema_extraction_start) * 1000

            logger.info(f"   ✅ Schemas info extracted in {schema_extraction_time:.2f}ms")
            logger.info(f"   Schemas found: {len(schemas_info)}")
            for schema_name, schema_obj in schemas_info.items():
                if hasattr(schema_obj, 'tables'):
                    table_count = len(schema_obj.tables.keys()) if hasattr(schema_obj.tables, 'keys') else 0
                    logger.info(f"      Schema '{schema_name}': {table_count} tables")

            logger.info(f"   Creating NL Query Parser...")
            parser_creation_start = time.time()
            parser = get_nl_query_parser(kg=kg, schemas_info=schemas_info)
            parser_creation_time = (time.time() - parser_creation_start) * 1000
            logger.info(f"   ✅ Parser created in {parser_creation_time:.2f}ms")

            # Check if LLM service is available
            logger.info(f"   Checking LLM service availability...")
            llm_check_start = time.time()
            from kg_builder.services.llm_service import get_llm_service
            llm_service = get_llm_service()
            llm_enabled = llm_service.is_enabled()
            llm_check_time = (time.time() - llm_check_start) * 1000

            logger.info(f"   ✅ LLM service checked in {llm_check_time:.2f}ms")
            logger.info(f"   LLM Service Enabled: {llm_enabled}")
            logger.info(f"   Will Use LLM: {use_llm and llm_enabled}")

            logger.info(f"   Starting query parsing...")
            parsing_start = time.time()
            intent = parser.parse(
                nl_definition,
                use_llm=use_llm
            )
            parsing_time = (time.time() - parsing_start) * 1000

            logger.info(f"✅ STEP G COMPLETED: Query parsed in {parsing_time:.2f}ms")
            logger.info(f"   Parsed Intent Details:")
            logger.info(f"      Query Type: '{intent.query_type}'")
            logger.info(f"      Source Table: '{intent.source_table}'")
            logger.info(f"      Target Table: '{intent.target_table}'")
            logger.info(f"      Operation: '{intent.operation}'")
            logger.info(f"      Join Columns: {intent.join_columns}")
            logger.info(f"      Confidence: {intent.confidence}")
            logger.info(f"      Filters: {intent.filters}")
            logger.info(f"      Definition: '{intent.definition}'")

            # Step H: Get database connection
            logger.info(f"🔌 STEP H: Establishing Database Connection")
            logger.info(f"   Database Type: '{db_type}'")

            connection_start = time.time()
            connection = _get_target_database_connection(db_type=db_type)
            connection_time = (time.time() - connection_start) * 1000

            if not connection:
                logger.error(f"❌ Database connection failed in {connection_time:.2f}ms")
                raise ValueError(f"Could not establish database connection for {db_type}")

            logger.info(f"✅ STEP H COMPLETED: Database connected in {connection_time:.2f}ms")
            logger.info(f"   Connection Type: {type(connection).__name__}")

            # Step I: Check if SQL is cached and should be used instead of LLM generation
            logger.info(f"🔍 STEP I: Analyzing SQL Cache Status")

            cache_check_start = time.time()

            # Extract cache-related fields
            is_sql_cached = kpi.get('isSQLCached', False)
            cached_sql = kpi.get('cached_sql', '')
            is_accept = kpi.get('isAccept', False)

            logger.info(f"   Cache Field Analysis:")
            logger.info(f"      isSQLCached: {is_sql_cached} (type: {type(is_sql_cached)})")
            logger.info(f"      cached_sql exists: {bool(cached_sql)}")
            logger.info(f"      cached_sql length: {len(cached_sql) if cached_sql else 0}")
            logger.info(f"      cached_sql preview: '{cached_sql[:100]}...' " if cached_sql else "      cached_sql preview: (empty)")
            logger.info(f"      isAccept: {is_accept} (type: {type(is_accept)})")

            # More explicit cache check
            is_cached = bool(is_sql_cached)
            has_cached_sql = bool(cached_sql and cached_sql.strip())
            will_use_cache = is_cached and has_cached_sql

            cache_check_time = (time.time() - cache_check_start) * 1000

            logger.info(f"✅ STEP I COMPLETED: Cache analysis in {cache_check_time:.2f}ms")
            logger.info(f"   Cache Decision Matrix:")
            logger.info(f"      is_cached: {is_cached}")
            logger.info(f"      has_cached_sql: {has_cached_sql}")
            logger.info(f"      will_use_cache: {will_use_cache}")
            logger.info(f"   Execution Path: {'CACHED_SQL' if will_use_cache else 'LLM_GENERATION'}")

            # Step J: Execute SQL (Cached or LLM-generated)
            if will_use_cache:
                logger.info(f"🔄 STEP J: EXECUTING CACHED SQL")
                logger.info(f"   Using pre-cached SQL instead of LLM generation")
                logger.info(f"   Cached SQL length: {len(cached_sql)} characters")
                logger.info(f"   Cached SQL preview: {cached_sql[:200]}...")

                sql_execution_start = time.time()
                query_result = self._execute_cached_sql(
                    cached_sql,
                    connection,
                    limit,
                    intent.definition,
                    db_type
                )
                sql_execution_time = (time.time() - sql_execution_start) * 1000

                logger.info(f"✅ STEP J COMPLETED: Cached SQL executed in {sql_execution_time:.2f}ms")
                logger.info(f"   Execution Status: {query_result.get('execution_status', 'UNKNOWN')}")
                logger.info(f"   Records Returned: {query_result.get('number_of_records', 0)}")

            else:
                logger.info(f"🤖 STEP J: EXECUTING LLM-GENERATED SQL")
                logger.info(f"   Using LLM to generate and execute SQL")

                if not is_cached:
                    logger.info(f"   Reason for LLM: isSQLCached is False")
                if not has_cached_sql:
                    logger.info(f"   Reason for LLM: No cached SQL available")

                logger.info(f"   Creating NL Query Executor...")
                executor_creation_start = time.time()
                executor = get_nl_query_executor(db_type, kg=kg, use_llm=True)  # Pass KG and force LLM for SQL generation
                executor_creation_time = (time.time() - executor_creation_start) * 1000
                logger.info(f"   ✅ Executor created in {executor_creation_time:.2f}ms")

                logger.info(f"   Executing query with LLM...")
                logger.info(f"      Intent: {intent.definition}")
                logger.info(f"      Limit: {limit}")
                logger.info(f"      DB Type: {db_type}")

                sql_execution_start = time.time()
                query_result = executor.execute(
                    intent,
                    connection,
                    limit=limit
                )
                sql_execution_time = (time.time() - sql_execution_start) * 1000

                logger.info(f"✅ STEP J COMPLETED: LLM SQL executed in {sql_execution_time:.2f}ms")
                logger.info(f"   Generated SQL: {getattr(query_result, 'sql', 'N/A')[:200]}...")
                logger.info(f"   Records Returned: {getattr(query_result, 'record_count', 0)}")
                logger.info(f"   Query Confidence: {getattr(query_result, 'confidence', 'N/A')}")
                logger.info(f"   Has Error: {bool(getattr(query_result, 'error', None))}")

            # Step K: Prepare and validate result data
            logger.info(f"📊 STEP K: Processing Query Results")

            result_processing_start = time.time()
            execution_time_ms = (time.time() - start_time) * 1000

            # Determine result type and extract data
            logger.info(f"   Query Result Type: {type(query_result).__name__}")

            if isinstance(query_result, dict):
                # Handle dict response (from cached SQL)
                record_count = query_result.get('number_of_records', 0)
                execution_status = query_result.get('execution_status', 'success')
                error_message = query_result.get('error_message')

                logger.info(f"   Processing cached SQL result...")
                logger.info(f"      Records: {record_count}")
                logger.info(f"      Status: {execution_status}")
                logger.info(f"      Has Error: {bool(error_message)}")

                result = {
                    'generated_sql': query_result.get('generated_sql', ''),
                    'number_of_records': record_count,
                    'joined_columns': query_result.get('joined_columns', ''),
                    'sql_query_type': query_result.get('sql_query_type', 'cached_sql'),
                    'operation': query_result.get('operation', 'CACHED'),
                    'execution_status': execution_status,
                    'execution_time_ms': execution_time_ms,
                    'confidence_score': query_result.get('confidence_score', 1.0),
                    'error_message': error_message,
                    'result_data': query_result.get('result_data', []),
                    'source_table': query_result.get('source_table', ''),
                    'target_table': query_result.get('target_table', ''),
                    'used_cached_sql': True,
                    'kpi_id': kpi.get('id'),
                    'kpi_name': kpi.get('name')
                }

            else:
                # Handle QueryResult response (from LLM)
                record_count = query_result.record_count
                has_error = bool(query_result.error)
                execution_status = 'failed' if has_error else 'success'

                logger.info(f"   Processing LLM-generated result...")
                logger.info(f"      Records: {record_count}")
                logger.info(f"      Status: {execution_status}")
                logger.info(f"      Has Error: {has_error}")
                logger.info(f"      Confidence: {query_result.confidence}")

                result = {
                    'generated_sql': query_result.sql,
                    'number_of_records': record_count,
                    'joined_columns': query_result.join_columns or [],
                    'sql_query_type': str(query_result.query_type),
                    'operation': query_result.operation,
                    'execution_status': execution_status,
                    'execution_time_ms': execution_time_ms,
                    'confidence_score': query_result.confidence,
                    'error_message': query_result.error,
                    'result_data': query_result.records,
                    'source_table': query_result.source_table,
                    'target_table': query_result.target_table,
                    'used_cached_sql': False,
                    'kpi_id': kpi.get('id'),
                    'kpi_name': kpi.get('name')
                }

            result_processing_time = (time.time() - result_processing_start) * 1000

            logger.info(f"✅ STEP K COMPLETED: Results processed in {result_processing_time:.2f}ms")
            logger.info(f"   Final Result Summary:")
            logger.info(f"      Execution Status: {result['execution_status']}")
            logger.info(f"      Records Processed: {result['number_of_records']}")
            logger.info(f"      Total Execution Time: {execution_time_ms:.2f}ms")
            logger.info(f"      Confidence Score: {result['confidence_score']}")
            logger.info(f"      Used Cached SQL: {result.get('used_cached_sql', False)}")
            logger.info(f"      Has Error: {bool(result['error_message'])}")

            if result['error_message']:
                logger.warning(f"      Error Details: {result['error_message']}")

            logger.info(f"🎯 INTERNAL KPI EXECUTION COMPLETED SUCCESSFULLY")
            return result
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            error_type = type(e).__name__
            error_message = str(e)

            logger.error("="*80)
            logger.error(f"❌ INTERNAL KPI EXECUTION FAILED")
            logger.error(f"   KPI ID: {kpi.get('id', 'UNKNOWN')}")
            logger.error(f"   KPI Name: '{kpi.get('name', 'UNKNOWN')}'")
            logger.error(f"   Execution Time: {execution_time_ms:.2f}ms")
            logger.error(f"   Error Type: {error_type}")
            logger.error(f"   Error Message: {error_message}")
            logger.error(f"   Failed Step: {self._determine_failure_step(e)}")
            logger.error("="*80)
            logger.error(f"Full error traceback:", exc_info=True)

            # Create comprehensive error result
            error_result = {
                'execution_status': 'failed',
                'error_message': error_message,
                'error_type': error_type,
                'execution_time_ms': execution_time_ms,
                'number_of_records': 0,
                'result_data': [],
                'failed_at_step': self._determine_failure_step(e),
                'kpi_id': kpi.get('id'),
                'kpi_name': kpi.get('name'),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'generated_sql': '',
                'confidence_score': 0.0,
                'used_cached_sql': False
            }

            logger.error(f"   Returning error result with {len(error_result)} fields")
            return error_result

    def _execute_cached_sql(self, cached_sql: str, connection, limit: int, definition: str, db_type: str = 'sqlserver') -> Dict[str, Any]:
        """Execute cached SQL directly without LLM generation."""
        import time
        from kg_builder.services.nl_query_executor import NLQueryExecutor

        start_time = time.time()
        logger.info("🔄 CACHED SQL EXECUTION STARTED")
        logger.info(f"   Definition: '{definition}'")
        logger.info(f"   DB Type: '{db_type}'")
        logger.info(f"   Limit: {limit}")
        logger.info(f"   SQL Length: {len(cached_sql)} characters")

        try:
            # Step 1: Prepare SQL with limit clause
            logger.info(f"📝 STEP 1: Preparing SQL with Limit")

            limit_start = time.time()
            executor = NLQueryExecutor(db_type=db_type)
            sql_with_limit = executor._add_limit_clause(cached_sql, limit)
            limit_time = (time.time() - limit_start) * 1000

            logger.info(f"✅ SQL prepared in {limit_time:.2f}ms")
            logger.info(f"   Original SQL length: {len(cached_sql)}")
            logger.info(f"   Modified SQL length: {len(sql_with_limit)}")
            logger.info(f"   Limit clause added: {len(sql_with_limit) > len(cached_sql)}")

            # Log the SQL being executed
            logger.info("="*100)
            logger.info(f"📝 CACHED SQL EXECUTION DETAILS")
            logger.info(f"   Query Definition: {definition}")
            logger.info(f"   Database Type: {db_type}")
            logger.info(f"   Record Limit: {limit}")
            logger.info(f"   Using Cached SQL (isSQLCached=true)")
            logger.info("-"*100)
            logger.info("🔹 FINAL SQL TO BE EXECUTED:")
            logger.info(f"\n{sql_with_limit}\n")
            logger.info("="*100)

            # Step 2: Execute the SQL
            logger.info(f"⚡ STEP 2: Executing SQL Query")

            execution_start = time.time()
            cursor = connection.cursor()
            cursor.execute(sql_with_limit)
            query_execution_time = (time.time() - execution_start) * 1000

            logger.info(f"✅ SQL query executed in {query_execution_time:.2f}ms")

            # Step 3: Fetch and process results
            logger.info(f"📊 STEP 3: Fetching Results")

            fetch_start = time.time()

            # Get column information
            columns = [desc[0] for desc in cursor.description]
            logger.info(f"   Columns found: {len(columns)}")
            logger.info(f"   Column names: {columns}")

            # Fetch all rows
            rows = cursor.fetchall()
            fetch_time = (time.time() - fetch_start) * 1000

            logger.info(f"✅ Data fetched in {fetch_time:.2f}ms")
            logger.info(f"   Rows retrieved: {len(rows)}")

            # Step 4: Convert to structured format
            logger.info(f"🔄 STEP 4: Converting to Structured Format")

            conversion_start = time.time()
            records = []

            for row_idx, row in enumerate(rows):
                record = {}
                for col_idx, value in enumerate(row):
                    record[columns[col_idx]] = value
                records.append(record)

                # Log first few records for debugging
                if row_idx < 3:
                    logger.debug(f"   Record {row_idx + 1}: {record}")

            conversion_time = (time.time() - conversion_start) * 1000
            total_execution_time = (time.time() - start_time) * 1000

            logger.info(f"✅ Data conversion completed in {conversion_time:.2f}ms")
            logger.info(f"   Records created: {len(records)}")

            # Step 5: Create success result
            logger.info(f"📋 STEP 5: Creating Success Result")

            result = {
                'execution_status': 'success',
                'generated_sql': cached_sql,
                'final_sql': sql_with_limit,
                'number_of_records': len(records),
                'result_data': records,
                'execution_time_ms': total_execution_time,
                'query_execution_time_ms': query_execution_time,
                'fetch_time_ms': fetch_time,
                'conversion_time_ms': conversion_time,
                'sql_query_type': 'cached_sql',
                'operation': 'CACHED',
                'confidence_score': 1.0,  # High confidence for cached SQL
                'joined_columns': '',
                'used_cached_sql': True,
                'columns': columns,
                'db_type': db_type,
                'limit_applied': limit
            }

            logger.info("="*100)
            logger.info(f"🎉 CACHED SQL EXECUTION COMPLETED SUCCESSFULLY")
            logger.info(f"   Total Execution Time: {total_execution_time:.2f}ms")
            logger.info(f"   Records Returned: {len(records)}")
            logger.info(f"   Columns: {len(columns)}")
            logger.info(f"   Status: SUCCESS")
            logger.info("="*100)

            return result

        except Exception as e:
            total_execution_time = (time.time() - start_time) * 1000
            error_type = type(e).__name__
            error_message = str(e)

            logger.error("="*100)
            logger.error(f"❌ CACHED SQL EXECUTION FAILED")
            logger.error(f"   Total Execution Time: {total_execution_time:.2f}ms")
            logger.error(f"   Error Type: {error_type}")
            logger.error(f"   Error Message: {error_message}")
            logger.error(f"   SQL Length: {len(cached_sql)}")
            logger.error(f"   DB Type: {db_type}")
            logger.error("="*100)
            logger.error(f"Full error details:", exc_info=True)

            error_result = {
                'execution_status': 'failed',
                'error_message': f"Cached SQL execution failed: {error_message}",
                'error_type': error_type,
                'generated_sql': cached_sql,
                'execution_time_ms': total_execution_time,
                'number_of_records': 0,
                'result_data': [],
                'used_cached_sql': True,
                'sql_query_type': 'cached_sql',
                'operation': 'CACHED',
                'confidence_score': 0.0,
                'db_type': db_type,
                'limit_applied': limit
            }

            logger.error(f"   Returning error result with {len(error_result)} fields")
            return error_result


def _get_source_database_connection(db_type: str = 'sqlserver') -> Optional[Any]:
    """
    Get a connection to the source database for KPI execution.

    Args:
        db_type: Database type (sqlserver, mysql, postgresql, oracle)

    Returns:
        Database connection object or None if not configured
    """
    connection_start_time = time.time()
    logger.info("🔌 DATABASE CONNECTION PROCESS STARTED")
    logger.info(f"   Requested DB Type: '{db_type}'")
    logger.info(f"   Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Step 1: Import required modules
        logger.info(f"📦 STEP 1: Importing Required Modules")
        import_start = time.time()

        import jaydebeapi
        import glob
        import os
        from kg_builder.config import get_source_db_config, JDBC_DRIVERS_PATH

        import_time = (time.time() - import_start) * 1000
        logger.info(f"✅ Modules imported in {import_time:.2f}ms")

        # Step 2: Load database configuration
        logger.info(f"⚙️ STEP 2: Loading Database Configuration")
        config_start = time.time()

        db_config = get_source_db_config()
        config_time = (time.time() - config_start) * 1000

        if not db_config:
            logger.error(f"❌ Database configuration not found in {config_time:.2f}ms")
            logger.error(f"   Please configure source database settings")
            return None

        logger.info(f"✅ Configuration loaded in {config_time:.2f}ms")
        logger.info(f"   Host: {db_config.host}")
        logger.info(f"   Port: {db_config.port}")
        logger.info(f"   Database: {db_config.database}")
        logger.info(f"   Username: {db_config.username}")
        logger.info(f"   Password: {'*' * len(db_config.password) if db_config.password else 'NOT_SET'}")

        # Step 3: Determine database-specific settings
        logger.info(f"🎯 STEP 3: Determining Database-Specific Settings")
        settings_start = time.time()

        db_type_lower = db_type.lower()
        logger.info(f"   Processing DB type: '{db_type_lower}'")

        if db_type_lower == "sqlserver":
            jdbc_url = f"jdbc:sqlserver://{db_config.host}:{db_config.port};databaseName={db_config.database};encrypt=true;trustServerCertificate=true"
            driver_class = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
            jar_pattern = "mssql-jdbc*.jar"
            logger.info(f"   SQL Server configuration selected")

        elif db_type_lower == "mysql":
            jdbc_url = f"jdbc:mysql://{db_config.host}:{db_config.port}/{db_config.database}?connectTimeout=60000&socketTimeout=120000&autoReconnect=true"
            driver_class = "com.mysql.cj.jdbc.Driver"
            jar_pattern = "mysql-connector-j*.jar"
            logger.info(f"   MySQL configuration selected")

        elif db_type_lower == "postgresql":
            jdbc_url = f"jdbc:postgresql://{db_config.host}:{db_config.port}/{db_config.database}"
            driver_class = "org.postgresql.Driver"
            jar_pattern = "postgresql-*.jar"
            logger.info(f"   PostgreSQL configuration selected")

        elif db_type_lower == "oracle":
            service_name = db_config.service_name or db_config.database
            jdbc_url = f"jdbc:oracle:thin:@{db_config.host}:{db_config.port}:{service_name}"
            driver_class = "oracle.jdbc.driver.OracleDriver"
            jar_pattern = "ojdbc*.jar"
            logger.info(f"   Oracle configuration selected")
            logger.info(f"   Service Name: {service_name}")

        else:
            settings_time = (time.time() - settings_start) * 1000
            logger.error(f"❌ Unsupported database type '{db_type}' in {settings_time:.2f}ms")
            logger.error(f"   Supported types: sqlserver, mysql, postgresql, oracle")
            raise ValueError(f"Unsupported database type: {db_type}")

        settings_time = (time.time() - settings_start) * 1000
        logger.info(f"✅ Database settings determined in {settings_time:.2f}ms")
        logger.info(f"   JDBC URL: {jdbc_url}")
        logger.info(f"   Driver Class: {driver_class}")
        logger.info(f"   JAR Pattern: {jar_pattern}")

        # Step 4: Find JDBC driver JAR
        logger.info(f"🔍 STEP 4: Locating JDBC Driver")
        driver_search_start = time.time()

        driver_pattern = os.path.join(JDBC_DRIVERS_PATH, jar_pattern)
        logger.info(f"   Search Pattern: {driver_pattern}")
        logger.info(f"   JDBC Drivers Path: {JDBC_DRIVERS_PATH}")
        logger.info(f"   Path Exists: {os.path.exists(JDBC_DRIVERS_PATH)}")

        jars = glob.glob(driver_pattern)
        driver_search_time = (time.time() - driver_search_start) * 1000

        logger.info(f"   Driver search completed in {driver_search_time:.2f}ms")
        logger.info(f"   JARs found: {len(jars)}")

        if not jars:
            logger.error(f"❌ No JDBC driver found for {db_type}")
            logger.error(f"   Search pattern: {driver_pattern}")

            if os.path.exists(JDBC_DRIVERS_PATH):
                available_files = os.listdir(JDBC_DRIVERS_PATH)
                logger.error(f"   Available files in {JDBC_DRIVERS_PATH}:")
                for file in available_files:
                    logger.error(f"      - {file}")
            else:
                logger.error(f"   JDBC drivers directory not found: {JDBC_DRIVERS_PATH}")
            return None

        driver_jar = jars[0]
        logger.info(f"✅ JDBC driver located: {driver_jar}")
        logger.info(f"   Driver file size: {os.path.getsize(driver_jar)} bytes")

        # Step 5: Establish connection
        logger.info(f"🔗 STEP 5: Establishing Database Connection")
        logger.info(f"   Target: {db_type} at {db_config.host}:{db_config.port}/{db_config.database}")

        connection_attempt_start = time.time()

        conn = jaydebeapi.connect(
            driver_class,
            jdbc_url,
            [db_config.username, db_config.password],
            driver_jar
        )

        connection_attempt_time = (time.time() - connection_attempt_start) * 1000
        total_connection_time = (time.time() - connection_start_time) * 1000

        logger.info(f"✅ Database connection established in {connection_attempt_time:.2f}ms")
        logger.info(f"   Connection Type: {type(conn).__name__}")
        logger.info(f"   Connection Object: {conn}")

        # Step 6: Test connection
        logger.info(f"🧪 STEP 6: Testing Connection")
        test_start = time.time()

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            test_result = cursor.fetchone()
            cursor.close()
            test_time = (time.time() - test_start) * 1000

            logger.info(f"✅ Connection test passed in {test_time:.2f}ms")
            logger.info(f"   Test query result: {test_result}")

        except Exception as test_error:
            test_time = (time.time() - test_start) * 1000
            logger.warning(f"⚠️ Connection test failed in {test_time:.2f}ms: {test_error}")
            logger.warning(f"   Connection may still be usable for actual queries")

        logger.info("="*100)
        logger.info(f"🎉 DATABASE CONNECTION COMPLETED SUCCESSFULLY")
        logger.info(f"   Database Type: {db_type}")
        logger.info(f"   Host: {db_config.host}:{db_config.port}")
        logger.info(f"   Database: {db_config.database}")
        logger.info(f"   Total Connection Time: {total_connection_time:.2f}ms")
        logger.info(f"   Driver: {os.path.basename(driver_jar)}")
        logger.info("="*100)

        return conn

    except Exception as e:
        total_connection_time = (time.time() - connection_start_time) * 1000
        error_type = type(e).__name__
        error_message = str(e)

        logger.error("="*100)
        logger.error(f"❌ DATABASE CONNECTION FAILED")
        logger.error(f"   Database Type: {db_type}")
        logger.error(f"   Total Attempt Time: {total_connection_time:.2f}ms")
        logger.error(f"   Error Type: {error_type}")
        logger.error(f"   Error Message: {error_message}")
        logger.error("="*100)
        logger.error(f"Full connection error details:", exc_info=True)

        return None


def _get_target_database_connection(db_type: str = 'sqlserver') -> Optional[Any]:
    """
    Get a connection to the target database for KPI execution.

    Args:
        db_type: Database type (sqlserver, mysql, postgresql, oracle)

    Returns:
        Database connection object or None if failed
    """
    import time
    from typing import Optional, Any

    connection_start_time = time.time()
    logger.info("="*100)
    logger.info(f"🎯 TARGET DATABASE CONNECTION INITIATED")
    logger.info(f"   Database Type: {db_type}")
    logger.info(f"   Connection Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*100)

    try:
        # Step 1: Import required modules
        logger.info(f"📦 STEP 1: Importing Required Modules")
        import_start = time.time()

        import jaydebeapi
        import glob
        import os
        from kg_builder.config import get_target_db_config, JDBC_DRIVERS_PATH

        import_time = (time.time() - import_start) * 1000
        logger.info(f"✅ Modules imported in {import_time:.2f}ms")

        # Step 2: Load database configuration
        logger.info(f"⚙️ STEP 2: Loading Target Database Configuration")
        config_start = time.time()

        db_config = get_target_db_config()
        config_time = (time.time() - config_start) * 1000

        if not db_config:
            logger.error(f"❌ Target database configuration not found in {config_time:.2f}ms")
            logger.error(f"   Please configure target database settings")
            return None

        logger.info(f"✅ Configuration loaded in {config_time:.2f}ms")
        logger.info(f"   Host: {db_config.host}")
        logger.info(f"   Port: {db_config.port}")
        logger.info(f"   Database: {db_config.database}")
        logger.info(f"   Username: {db_config.username}")
        logger.info(f"   DB Type: {db_config.db_type}")

        # Step 3: Build JDBC connection parameters
        logger.info(f"🔧 STEP 3: Building JDBC Connection Parameters")
        jdbc_start = time.time()

        db_type_lower = db_type.lower()

        if db_type_lower == "sqlserver":
            jdbc_url = f"jdbc:sqlserver://{db_config.host}:{db_config.port};databaseName={db_config.database};encrypt=true;trustServerCertificate=true"
            driver_class = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
            jar_pattern = "mssql-jdbc*.jar"
            logger.info(f"   SQL Server configuration selected")

        elif db_type_lower == "mysql":
            jdbc_url = f"jdbc:mysql://{db_config.host}:{db_config.port}/{db_config.database}?connectTimeout=60000&socketTimeout=120000&autoReconnect=true"
            driver_class = "com.mysql.cj.jdbc.Driver"
            jar_pattern = "mysql-connector-j*.jar"
            logger.info(f"   MySQL configuration selected")

        elif db_type_lower == "postgresql":
            jdbc_url = f"jdbc:postgresql://{db_config.host}:{db_config.port}/{db_config.database}"
            driver_class = "org.postgresql.Driver"
            jar_pattern = "postgresql-*.jar"
            logger.info(f"   PostgreSQL configuration selected")

        elif db_type_lower == "oracle":
            service_name = db_config.service_name or db_config.database
            jdbc_url = f"jdbc:oracle:thin:@{db_config.host}:{db_config.port}:{service_name}"
            driver_class = "oracle.jdbc.driver.OracleDriver"
            jar_pattern = "ojdbc*.jar"
            logger.info(f"   Oracle configuration selected")
            logger.info(f"   Service Name: {service_name}")

        else:
            logger.error(f"❌ Unsupported database type: {db_type}")
            raise ValueError(f"Unsupported database type: {db_type}")

        jdbc_time = (time.time() - jdbc_start) * 1000
        logger.info(f"✅ JDBC parameters built in {jdbc_time:.2f}ms")
        logger.info(f"   JDBC URL: {jdbc_url}")
        logger.info(f"   Driver Class: {driver_class}")

        # Step 4: Locate JDBC driver
        logger.info(f"🔍 STEP 4: Locating JDBC Driver")
        driver_search_start = time.time()

        jdbc_dir = JDBC_DRIVERS_PATH
        pattern = os.path.join(jdbc_dir, jar_pattern)
        jars = glob.glob(pattern)

        if not jars:
            logger.error(f"❌ No JDBC driver found for {db_type} at {pattern}")
            logger.error(f"   Please ensure the JDBC driver is available in {jdbc_dir}")
            raise Exception(f"No JDBC driver found for {db_type} at {pattern}")

        driver_search_time = (time.time() - driver_search_start) * 1000
        logger.info(f"✅ Driver search completed in {driver_search_time:.2f}ms")
        logger.info(f"   Found {len(jars)} driver(s)")

        driver_jar = jars[0]
        logger.info(f"✅ JDBC driver located: {driver_jar}")
        logger.info(f"   Driver file size: {os.path.getsize(driver_jar)} bytes")

        # Step 5: Establish connection
        logger.info(f"🔗 STEP 5: Establishing Target Database Connection")
        logger.info(f"   Target: {db_type} at {db_config.host}:{db_config.port}/{db_config.database}")

        connection_attempt_start = time.time()

        # Use centralized JDBC connection manager
        from kg_builder.services.jdbc_connection_manager import get_jdbc_connection
        conn = get_jdbc_connection(driver_class, jdbc_url, db_config.username, db_config.password)

        connection_attempt_time = (time.time() - connection_attempt_start) * 1000
        logger.info(f"✅ Connection established in {connection_attempt_time:.2f}ms")

        # Step 6: Test connection
        logger.info(f"🧪 STEP 6: Testing Target Database Connection")
        test_start = time.time()

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            test_result = cursor.fetchone()
            cursor.close()
            test_time = (time.time() - test_start) * 1000
            logger.info(f"✅ Connection test passed in {test_time:.2f}ms")
            logger.info(f"   Test result: {test_result}")

        except Exception as test_error:
            test_time = (time.time() - test_start) * 1000
            logger.warning(f"⚠️ Connection test failed in {test_time:.2f}ms: {test_error}")
            logger.warning(f"   Connection may still be usable for actual queries")

        total_connection_time = (time.time() - connection_start_time) * 1000

        logger.info("="*100)
        logger.info(f"🎉 TARGET DATABASE CONNECTION COMPLETED SUCCESSFULLY")
        logger.info(f"   Database Type: {db_type}")
        logger.info(f"   Host: {db_config.host}:{db_config.port}")
        logger.info(f"   Database: {db_config.database}")
        logger.info(f"   Total Connection Time: {total_connection_time:.2f}ms")
        logger.info(f"   Driver: {os.path.basename(driver_jar)}")
        logger.info("="*100)

        return conn

    except Exception as e:
        total_connection_time = (time.time() - connection_start_time) * 1000
        error_type = type(e).__name__
        error_message = str(e)

        logger.error("="*100)
        logger.error(f"❌ TARGET DATABASE CONNECTION FAILED")
        logger.error(f"   Database Type: {db_type}")
        logger.error(f"   Total Attempt Time: {total_connection_time:.2f}ms")
        logger.error(f"   Error Type: {error_type}")
        logger.error(f"   Error Message: {error_message}")
        logger.error("="*100)
        logger.error(f"Full connection error details:", exc_info=True)

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

