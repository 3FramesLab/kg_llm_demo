"""
FastAPI routes for knowledge graph operations.
"""
import logging
import time
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List

from kg_builder.models import (
    SchemaUploadResponse, KGGenerationRequest, KGGenerationResponse,
    QueryRequest, QueryResponse, EntityResponse, GraphExportResponse,
    HealthCheckResponse, LLMExtractionResponse, LLMAnalysisResponse,
    RuleGenerationRequest, RuleGenerationResponse, RuleValidationRequest,
    ValidationResult, RuleExecutionRequest, RuleExecutionResponse
)
from kg_builder.services.schema_parser import SchemaParser
from kg_builder.services.falkordb_backend import get_falkordb_backend
from kg_builder.services.graphiti_backend import get_graphiti_backend
from kg_builder.services.llm_service import get_llm_service
from kg_builder.services.reconciliation_service import get_reconciliation_service
from kg_builder.services.rule_storage import get_rule_storage
from kg_builder.services.rule_validator import get_rule_validator

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Check health status of the application."""
    falkordb = get_falkordb_backend()
    graphiti = get_graphiti_backend()
    
    return HealthCheckResponse(
        status="healthy",
        falkordb_connected=falkordb.is_connected(),
        graphiti_available=graphiti.is_available()
    )


@router.get("/schemas")
async def list_schemas():
    """List available schema files."""
    from kg_builder.config import SCHEMAS_DIR
    
    try:
        schemas = [f.stem for f in SCHEMAS_DIR.glob("*.json")]
        return {
            "success": True,
            "schemas": schemas,
            "count": len(schemas)
        }
    except Exception as e:
        logger.error(f"Error listing schemas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schemas/{schema_name}/parse", response_model=SchemaUploadResponse)
async def parse_schema(schema_name: str):
    """Parse a schema file and extract metadata."""
    try:
        schema = SchemaParser.load_schema(schema_name)
        
        total_columns = sum(len(table.columns) for table in schema.tables.values())
        
        return SchemaUploadResponse(
            success=True,
            message=f"Schema '{schema_name}' parsed successfully",
            schema_name=schema_name,
            tables_count=schema.total_tables,
            total_columns=total_columns
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")
    except Exception as e:
        logger.error(f"Error parsing schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kg/generate", response_model=KGGenerationResponse)
async def generate_knowledge_graph(request: KGGenerationRequest):
    """Generate a knowledge graph from one or multiple schemas."""
    try:
        start_time = time.time()

        # Determine which schemas to process
        schema_names = request.schema_names or [request.schema_name]

        # Build knowledge graph
        if len(schema_names) == 1:
            # Single schema - use original method
            schema = SchemaParser.load_schema(schema_names[0])
            kg = SchemaParser.build_knowledge_graph(
                schema_names[0],
                request.kg_name,
                schema
            )
        else:
            # Multiple schemas - use merged method with cross-schema relationships
            # LLM enhancement is only applied to multi-schema KGs
            kg = SchemaParser.build_merged_knowledge_graph(
                schema_names,
                request.kg_name,
                use_llm=request.use_llm_enhancement
            )

        backends_used = []

        # Store in FalkorDB if requested
        if "falkordb" in request.backends:
            falkordb = get_falkordb_backend()
            if falkordb.is_connected():
                if falkordb.create_graph(kg):
                    backends_used.append("falkordb")
            else:
                logger.warning("FalkorDB not connected, skipping")

        # Store in Graphiti if requested
        if "graphiti" in request.backends:
            graphiti = get_graphiti_backend()
            if graphiti.create_graph(kg):
                backends_used.append("graphiti")

        elapsed_ms = (time.time() - start_time) * 1000

        return KGGenerationResponse(
            success=True,
            schemas_processed=schema_names,
            message=f"Knowledge graph '{request.kg_name}' generated successfully from {len(schema_names)} schema(s)",
            kg_name=request.kg_name,
            nodes_count=len(kg.nodes),
            relationships_count=len(kg.relationships),
            backends_used=backends_used,
            generation_time_ms=elapsed_ms
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating knowledge graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kg/{kg_name}/query", response_model=QueryResponse)
async def query_graph(kg_name: str, request: QueryRequest):
    """Query a knowledge graph."""
    try:
        start_time = time.time()
        
        backend_name = request.backend.lower()
        
        if backend_name == "falkordb":
            backend = get_falkordb_backend()
            if not backend.is_connected():
                raise HTTPException(status_code=503, detail="FalkorDB not connected")
            results = backend.query(kg_name, request.query)
        
        elif backend_name == "graphiti":
            backend = get_graphiti_backend()
            results = backend.query(kg_name, request.query)
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown backend: {backend_name}")
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        return QueryResponse(
            success=True,
            message="Query executed successfully",
            results=results,
            query_time_ms=elapsed_ms
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kg/{kg_name}/entities")
async def get_entities(kg_name: str, backend: str = "graphiti"):
    """Get all entities from a knowledge graph."""
    try:
        if backend.lower() == "falkordb":
            backend_obj = get_falkordb_backend()
            entities = backend_obj.get_entities(kg_name)
        else:
            backend_obj = get_graphiti_backend()
            entities = backend_obj.get_entities(kg_name)
        
        return {
            "success": True,
            "kg_name": kg_name,
            "entities": entities,
            "count": len(entities)
        }
    except Exception as e:
        logger.error(f"Error retrieving entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kg/{kg_name}/relationships")
async def get_relationships(kg_name: str, backend: str = "graphiti"):
    """Get all relationships from a knowledge graph."""
    try:
        if backend.lower() == "falkordb":
            backend_obj = get_falkordb_backend()
            relationships = backend_obj.get_relationships(kg_name)
        else:
            backend_obj = get_graphiti_backend()
            relationships = backend_obj.get_relationships(kg_name)
        
        return {
            "success": True,
            "kg_name": kg_name,
            "relationships": relationships,
            "count": len(relationships)
        }
    except Exception as e:
        logger.error(f"Error retrieving relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kg/{kg_name}/export")
async def export_graph(kg_name: str, backend: str = "graphiti"):
    """Export a knowledge graph."""
    try:
        if backend.lower() == "falkordb":
            backend_obj = get_falkordb_backend()
        else:
            backend_obj = get_graphiti_backend()
        
        entities = backend_obj.get_entities(kg_name)
        relationships = backend_obj.get_relationships(kg_name)
        
        return GraphExportResponse(
            success=True,
            message=f"Graph '{kg_name}' exported successfully",
            format="json",
            data={
                "kg_name": kg_name,
                "entities": entities,
                "relationships": relationships,
                "stats": {
                    "entities_count": len(entities),
                    "relationships_count": len(relationships)
                }
            }
        )
    except Exception as e:
        logger.error(f"Error exporting graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kg")
async def list_graphs():
    """List all knowledge graphs."""
    try:
        graphiti = get_graphiti_backend()
        graphs = graphiti.list_graphs()
        
        return {
            "success": True,
            "graphs": graphs,
            "count": len(graphs)
        }
    except Exception as e:
        logger.error(f"Error listing graphs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/kg/{kg_name}")
async def delete_graph(kg_name: str):
    """Delete a knowledge graph."""
    try:
        falkordb = get_falkordb_backend()
        graphiti = get_graphiti_backend()
        
        falkordb_deleted = falkordb.delete_graph(kg_name)
        graphiti_deleted = graphiti.delete_graph(kg_name)
        
        return {
            "success": True,
            "message": f"Graph '{kg_name}' deleted",
            "falkordb_deleted": falkordb_deleted,
            "graphiti_deleted": graphiti_deleted
        }
    except Exception as e:
        logger.error(f"Error deleting graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# LLM-based extraction endpoints
@router.post("/llm/extract/{schema_name}", response_model=LLMExtractionResponse)
async def llm_extract_schema(schema_name: str):
    """
    Use LLM to intelligently extract entities and relationships from schema.

    Args:
        schema_name: Name of the schema to analyze

    Returns:
        Extracted entities and relationships with descriptions
    """
    try:
        llm_service = get_llm_service()

        if not llm_service.is_enabled():
            raise HTTPException(
                status_code=503,
                detail="LLM service is not enabled. Please set OPENAI_API_KEY environment variable."
            )

        # Load and parse schema
        parser = SchemaParser()
        schema = parser.load_schema(schema_name)

        # Extract entities and relationships using LLM
        entities_result = llm_service.extract_entities(schema)
        relationships_result = llm_service.extract_relationships(schema)

        # Convert to response models
        entities = [
            LLMEntity(**entity)
            for entity in entities_result.get("entities", [])
        ]
        relationships = [
            LLMRelationship(**rel)
            for rel in relationships_result.get("relationships", [])
        ]

        return LLMExtractionResponse(
            success=True,
            entities=entities,
            relationships=relationships
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in LLM extraction: {e}")
        return LLMExtractionResponse(
            success=False,
            error=str(e)
        )


@router.post("/llm/analyze/{schema_name}", response_model=LLMAnalysisResponse)
async def llm_analyze_schema(schema_name: str):
    """
    Use LLM to provide comprehensive schema analysis.

    Args:
        schema_name: Name of the schema to analyze

    Returns:
        Comprehensive schema analysis including domain, purpose, patterns, etc.
    """
    try:
        llm_service = get_llm_service()

        if not llm_service.is_enabled():
            raise HTTPException(
                status_code=503,
                detail="LLM service is not enabled. Please set OPENAI_API_KEY environment variable."
            )

        # Load and parse schema
        parser = SchemaParser()
        schema = parser.load_schema(schema_name)

        # Analyze schema using LLM
        analysis = llm_service.analyze_schema(schema)

        return LLMAnalysisResponse(
            success=True,
            domain=analysis.get("domain"),
            purpose=analysis.get("purpose"),
            patterns=analysis.get("patterns", []),
            key_entities=analysis.get("key_entities", []),
            data_flow=analysis.get("data_flow"),
            business_logic=analysis.get("business_logic"),
            quality_notes=analysis.get("quality_notes")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in LLM analysis: {e}")
        return LLMAnalysisResponse(
            success=False,
            error=str(e)
        )


@router.get("/llm/status")
async def llm_status():
    """Check LLM service status."""
    llm_service = get_llm_service()

    return {
        "enabled": llm_service.is_enabled(),
        "model": llm_service.model if llm_service.is_enabled() else None,
        "temperature": llm_service.temperature,
        "max_tokens": llm_service.max_tokens
    }


# Reconciliation Rule endpoints
@router.post("/reconciliation/generate", response_model=RuleGenerationResponse)
async def generate_reconciliation_rules(request: RuleGenerationRequest):
    """
    Generate reconciliation rules from a knowledge graph.

    This endpoint analyzes a knowledge graph to automatically generate rules
    for matching and linking data across different schemas.

    Example request:
    ```json
    {
      "schema_names": ["orderMgmt-catalog", "vendorDB-suppliers"],
      "kg_name": "unified_kg",
      "use_llm_enhancement": true,
      "min_confidence": 0.7,
      "match_types": ["exact", "semantic"]
    }
    ```

    Args:
        request: Rule generation request parameters

    Returns:
        Generated reconciliation ruleset with rules and metadata
    """
    try:
        start_time = time.time()

        # Get reconciliation service
        recon_service = get_reconciliation_service()

        # Generate rules
        ruleset = recon_service.generate_from_knowledge_graph(
            kg_name=request.kg_name,
            schema_names=request.schema_names,
            use_llm=request.use_llm_enhancement,
            min_confidence=request.min_confidence
        )

        # Save ruleset
        storage = get_rule_storage()
        storage.save_ruleset(ruleset)

        elapsed_ms = (time.time() - start_time) * 1000

        return RuleGenerationResponse(
            success=True,
            ruleset_id=ruleset.ruleset_id,
            rules_count=len(ruleset.rules),
            rules=ruleset.rules,
            generation_time_ms=elapsed_ms,
            message=f"Generated {len(ruleset.rules)} reconciliation rules"
        )

    except Exception as e:
        logger.error(f"Error generating reconciliation rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reconciliation/rulesets")
async def list_rulesets(schema_name: str = None, kg_name: str = None):
    """
    List all saved reconciliation rulesets.

    Query parameters:
    - schema_name: Filter by schema name (optional)
    - kg_name: Filter by source knowledge graph (optional)

    Returns:
        List of ruleset metadata
    """
    try:
        storage = get_rule_storage()

        if schema_name or kg_name:
            rulesets = storage.search_rulesets(
                schema_name=schema_name,
                kg_name=kg_name
            )
        else:
            rulesets = storage.list_rulesets()

        return {
            "success": True,
            "rulesets": rulesets,
            "count": len(rulesets)
        }

    except Exception as e:
        logger.error(f"Error listing rulesets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reconciliation/rulesets/{ruleset_id}")
async def get_ruleset(ruleset_id: str):
    """
    Retrieve a specific reconciliation ruleset.

    Args:
        ruleset_id: ID of the ruleset to retrieve

    Returns:
        Complete ruleset with all rules
    """
    try:
        storage = get_rule_storage()
        ruleset = storage.load_ruleset(ruleset_id)

        if not ruleset:
            raise HTTPException(status_code=404, detail=f"Ruleset '{ruleset_id}' not found")

        return {
            "success": True,
            "ruleset": ruleset.dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving ruleset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reconciliation/rulesets/{ruleset_id}")
async def delete_ruleset(ruleset_id: str):
    """
    Delete a reconciliation ruleset.

    Args:
        ruleset_id: ID of the ruleset to delete

    Returns:
        Success status
    """
    try:
        storage = get_rule_storage()
        deleted = storage.delete_ruleset(ruleset_id)

        if not deleted:
            raise HTTPException(status_code=404, detail=f"Ruleset '{ruleset_id}' not found")

        return {
            "success": True,
            "message": f"Ruleset '{ruleset_id}' deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting ruleset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reconciliation/rulesets/{ruleset_id}/export/sql")
async def export_ruleset_to_sql(
    ruleset_id: str,
    query_type: str = "all"
):
    """
    Export a ruleset as SQL statements.

    Args:
        ruleset_id: ID of the ruleset to export
        query_type: Type of queries to generate:
            - "all": Generate all query types (matched, unmatched source, unmatched target, statistics)
            - "matched": Only matched records query
            - "unmatched_source": Only unmatched source records
            - "unmatched_target": Only unmatched target records

    Returns:
        SQL statements as text

    Example:
        GET /reconciliation/rulesets/RECON_ABC123/export/sql?query_type=all
    """
    try:
        if query_type not in ["all", "matched", "unmatched_source", "unmatched_target"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid query_type: {query_type}. Must be one of: all, matched, unmatched_source, unmatched_target"
            )

        storage = get_rule_storage()
        sql = storage.export_ruleset_to_sql(ruleset_id, query_type=query_type)

        if not sql:
            raise HTTPException(status_code=404, detail=f"Ruleset '{ruleset_id}' not found")

        return {
            "success": True,
            "ruleset_id": ruleset_id,
            "query_type": query_type,
            "sql": sql
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting ruleset to SQL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reconciliation/validate")
async def validate_rule(request: RuleValidationRequest):
    """
    Validate a reconciliation rule against actual database data.

    This endpoint performs comprehensive validation by:
    - Connecting to source and target databases via JDBC
    - Verifying tables and columns exist
    - Checking data type compatibility
    - Testing on sample data to calculate match rates
    - Detecting relationship cardinality (1:1, 1:N, N:M)
    - Estimating query performance

    Args:
        request: Rule validation request with rule, sample size, and DB connections

    Returns:
        Validation result with issues, warnings, and metrics

    Example request:
    ```json
    {
      "rule": {...},
      "sample_size": 100,
      "source_db_config": {
        "db_type": "oracle",
        "host": "localhost",
        "port": 1521,
        "database": "ORCL",
        "username": "user1",
        "password": "pass1"
      },
      "target_db_config": {
        "db_type": "oracle",
        "host": "localhost",
        "port": 1521,
        "database": "ORCL",
        "username": "user2",
        "password": "pass2"
      }
    }
    ```
    """
    try:
        from kg_builder.config import (
            get_source_db_config,
            get_target_db_config,
            USE_ENV_DB_CONFIGS
        )

        # Determine database configurations to use
        # Priority: 1. Request payload, 2. Environment variables, 3. None (basic validation)
        source_db_config = request.source_db_config
        target_db_config = request.target_db_config

        # Use environment configs if enabled and no configs in request
        if USE_ENV_DB_CONFIGS and not source_db_config and not target_db_config:
            logger.info("Attempting to use database configs from environment variables")
            source_db_config = get_source_db_config()
            target_db_config = get_target_db_config()

            if source_db_config and target_db_config:
                logger.info("Using database configurations from environment variables for validation")
            elif source_db_config or target_db_config:
                logger.warning(
                    "Partial database configuration found in environment. "
                    "Both source and target configs are required."
                )
                source_db_config = None
                target_db_config = None

        # Check if database connections are available
        if not source_db_config or not target_db_config:
            # Return basic validation without database connection
            result = ValidationResult(
                rule_id=request.rule.rule_id,
                valid=True,
                exists=True,
                types_compatible=True,
                sample_match_rate=None,
                cardinality=None,
                estimated_performance_ms=None,
                issues=[],
                warnings=[
                    "Database connections not provided - skipping data validation",
                    "Provide 'source_db_config' and 'target_db_config' for full validation",
                    "Or configure database credentials in environment variables"
                ]
            )
            return {
                "success": True,
                "validation": result.dict()
            }

        # Get rule validator
        validator = get_rule_validator()

        # Perform full validation with database connections
        logger.info(f"Validating rule '{request.rule.rule_id}' with database connections")
        result = validator.validate_rule_with_data(
            rule=request.rule,
            source_db_config=source_db_config,
            target_db_config=target_db_config,
            sample_size=request.sample_size
        )

        return {
            "success": True,
            "validation": result.dict()
        }

    except Exception as e:
        logger.error(f"Error validating rule: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reconciliation/execute")
async def execute_reconciliation(request: RuleExecutionRequest):
    """
    Execute reconciliation rules against actual databases.

    This endpoint executes the reconciliation rules using SQL queries to find:
    - Matched records (exist in both source and target)
    - Unmatched source records (only in source)
    - Unmatched target records (only in target)

    **Two execution modes:**

    1. **SQL Export Mode** (No database configs provided):
       - Returns SQL queries that you can run manually
       - Use this when you want to review/customize the queries
       - No actual database execution

    2. **Direct Execution Mode** (Database configs provided):
       - Connects to actual databases via JDBC
       - Executes queries and returns results
       - Requires JayDeBeApi and JDBC drivers

    Args:
        request: Execution request with:
            - ruleset_id: ID of the ruleset to execute
            - limit: Maximum number of records to return (default: 100)
            - source_db_config: (Optional) Source database connection
            - target_db_config: (Optional) Target database connection
            - include_matched: (Optional) Include matched records (default: True)
            - include_unmatched: (Optional) Include unmatched records (default: True)

    Returns:
        RuleExecutionResponse with matched and unmatched records

    Example - SQL Export Mode:
    ```json
    {
      "ruleset_id": "RECON_ABC123",
      "limit": 100
    }
    ```

    Example - Direct Execution Mode:
    ```json
    {
      "ruleset_id": "RECON_ABC123",
      "limit": 100,
      "source_db_config": {
        "db_type": "oracle",
        "host": "localhost",
        "port": 1521,
        "database": "ORCL",
        "username": "user1",
        "password": "pass1"
      },
      "target_db_config": {
        "db_type": "oracle",
        "host": "localhost",
        "port": 1521,
        "database": "ORCL",
        "username": "user2",
        "password": "pass2"
      }
    }
    ```
    """
    try:
        from kg_builder.config import (
            get_source_db_config,
            get_target_db_config,
            USE_ENV_DB_CONFIGS
        )

        # Determine database configurations to use
        # Priority: 1. Request payload, 2. Environment variables, 3. None (SQL export mode)
        source_db_config = request.source_db_config
        target_db_config = request.target_db_config

        # Use environment configs if enabled and no configs in request
        if USE_ENV_DB_CONFIGS and not source_db_config and not target_db_config:
            logger.info("Attempting to use database configs from environment variables")
            source_db_config = get_source_db_config()
            target_db_config = get_target_db_config()

            if source_db_config and target_db_config:
                logger.info("Using database configurations from environment variables")
            elif source_db_config or target_db_config:
                logger.warning(
                    "Partial database configuration found in environment. "
                    "Both source and target configs are required."
                )
                source_db_config = None
                target_db_config = None

        # Check if database connections are available
        if not source_db_config or not target_db_config:
            # SQL Export Mode - return SQL queries
            logger.info(f"SQL Export Mode: Generating SQL for ruleset '{request.ruleset_id}'")

            storage = get_rule_storage()
            sql = storage.export_ruleset_to_sql(request.ruleset_id, query_type="all")

            if not sql:
                raise HTTPException(
                    status_code=404,
                    detail=f"Ruleset '{request.ruleset_id}' not found"
                )

            return {
                "success": True,
                "mode": "sql_export",
                "message": "SQL queries generated. Execute these queries manually in your database.",
                "sql": sql,
                "matched_count": 0,
                "unmatched_source_count": 0,
                "unmatched_target_count": 0,
                "matched_records": [],
                "unmatched_source": [],
                "unmatched_target": [],
                "execution_time_ms": 0.0,
                "instructions": [
                    "Copy the SQL queries from the 'sql' field",
                    "Run them in your database client (SQL Developer, DBeaver, etc.)",
                    "Review the matched and unmatched records",
                    "For automated execution, provide source_db_config and target_db_config"
                ]
            }

        # Direct Execution Mode - execute against actual databases
        logger.info(f"Direct Execution Mode: Executing ruleset '{request.ruleset_id}' against databases")

        from kg_builder.services.reconciliation_executor import get_reconciliation_executor

        executor = get_reconciliation_executor()

        result = executor.execute_ruleset(
            ruleset_id=request.ruleset_id,
            source_db_config=source_db_config,
            target_db_config=target_db_config,
            limit=request.limit,
            include_matched=getattr(request, 'include_matched', True),
            include_unmatched=getattr(request, 'include_unmatched', True)
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing reconciliation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

