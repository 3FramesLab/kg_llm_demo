"""
Landing KPI Executor Service

Handles execution of Landing KPI definitions using the NL Query Executor.
Integrates KPI definitions with NL query execution pipeline.
"""

import logging
import time
from typing import Any, Dict, Optional
from kg_builder.services.landing_kpi_service import LandingKPIService
from kg_builder.services.nl_query_classifier import get_nl_query_classifier
from kg_builder.services.nl_query_parser import get_nl_query_parser
from kg_builder.services.nl_query_executor import get_nl_query_executor

logger = logging.getLogger(__name__)


class LandingKPIExecutor:
    """Execute Landing KPI definitions using NL Query Executor."""
    
    def __init__(self):
        """Initialize Landing KPI executor."""
        self.kpi_service = LandingKPIService()
    
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

            graphiti = get_graphiti_backend()
            entities_data = graphiti.get_entities(kg_name)
            relationships_data = graphiti.get_relationships(kg_name)

            # Convert to KnowledgeGraph object
            nodes = [GraphNode(**entity) for entity in entities_data] if entities_data else []
            relationships = [GraphRelationship(**rel) for rel in relationships_data] if relationships_data else []

            # Load metadata including table_aliases
            table_aliases = {}
            try:
                kg_metadata = graphiti.get_kg_metadata(kg_name)
                if kg_metadata:
                    table_aliases = kg_metadata.get('table_aliases', {})
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
            parser = get_nl_query_parser(kg=kg)
            intent = parser.parse(
                nl_definition,
                use_llm=use_llm
            )
            logger.info(f"Parsed Intent: {intent}")

            # Step 4: Get database connection
            connection = _get_source_database_connection(db_type=db_type)

            if not connection:
                raise ValueError("Could not establish database connection")

            # Step 5: Execute the query
            executor = get_nl_query_executor(db_type)
            query_result = executor.execute(
                intent,
                connection,
                limit=limit
            )

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


def get_landing_kpi_executor() -> LandingKPIExecutor:
    """Get Landing KPI executor instance."""
    return LandingKPIExecutor()

