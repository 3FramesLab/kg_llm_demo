"""
FastAPI routes for knowledge graph operations.
"""
import logging
import time
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel

from kg_builder.models import (
    SchemaUploadResponse, KGGenerationRequest, KGGenerationResponse,
    QueryRequest, QueryResponse, EntityResponse, GraphExportResponse,
    HealthCheckResponse, LLMExtractionResponse, LLMAnalysisResponse,
    RuleGenerationRequest, RuleGenerationResponse, RuleValidationRequest,
    ValidationResult, RuleExecutionRequest, RuleExecutionResponse,
    NLRelationshipRequest, NLRelationshipResponse, KnowledgeGraph,
    KPICalculationRequest, KPICalculationResponse,
    LandingExecutionRequest, LandingExecutionResponse,
    KPICreateRequest, KPIResultResponse, KPIEvidenceDrillDownRequest,
    KPIEvidenceDrillDownResponse, KPIDefinitionRequest, KPIUpdateRequest,
    KPIExecutionRequest, BatchExecutionRequest, EvidenceRequest,
    KPIListResponse, KPIExecutionResponse, KPIResultsListResponse,
    RelationshipPair, KGRelationshipType,
    NLQueryExecutionRequest, NLQueryExecutionResponse,
    KPIDefinition, KPIUpdateRequest as KPIUpdateRequestNew,
    KPIExecutionResult, DrilldownRequest, DrilldownResponse
)
from kg_builder.services.schema_parser import SchemaParser
from kg_builder.services.falkordb_backend import get_falkordb_backend
from kg_builder.services.graphiti_backend import get_graphiti_backend
from kg_builder.services.llm_service import get_llm_service
from kg_builder.services.reconciliation_service import get_reconciliation_service
from kg_builder.services.rule_storage import get_rule_storage
from kg_builder.services.rule_validator import get_rule_validator
from kg_builder.services.nl_relationship_parser import get_nl_relationship_parser

logger = logging.getLogger(__name__)
router = APIRouter()


def get_source_database_connection():
    """
    Get JDBC connection to source database.

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

        # Build JDBC URL
        db_type = db_config.db_type.lower()
        if db_type == "oracle":
            if db_config.service_name:
                jdbc_url = f"jdbc:oracle:thin:@{db_config.host}:{db_config.port}/{db_config.service_name}"
            else:
                jdbc_url = f"jdbc:oracle:thin:@{db_config.host}:{db_config.port}:{db_config.database}"
        elif db_type == "sqlserver":
            jdbc_url = f"jdbc:sqlserver://{db_config.host}:{db_config.port};databaseName={db_config.database};encrypt=true;trustServerCertificate=true"
        elif db_type == "mysql":
            jdbc_url = f"jdbc:mysql://{db_config.host}:{db_config.port}/{db_config.database}"
        elif db_type == "postgresql":
            jdbc_url = f"jdbc:postgresql://{db_config.host}:{db_config.port}/{db_config.database}"
        else:
            logger.error(f"Unsupported database type: {db_type}")
            return None

        # Get driver class
        drivers = {
            "oracle": "oracle.jdbc.OracleDriver",
            "sqlserver": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
            "mysql": "com.mysql.cj.jdbc.Driver",
            "postgresql": "org.postgresql.Driver"
        }
        driver_class = drivers.get(db_type)

        # Get driver JAR
        jar_patterns = {
            "oracle": "ojdbc*.jar",
            "sqlserver": "mssql-jdbc*.jar",
            "mysql": "mysql-connector-j*.jar",
            "postgresql": "postgresql-*.jar"
        }
        pattern = os.path.join(JDBC_DRIVERS_PATH, jar_patterns.get(db_type, "*.jar"))
        jars = glob.glob(pattern)

        if not jars:
            logger.error(f"No JDBC driver found for {db_type} at {pattern}")
            return None

        driver_jar = jars[0]

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
    """
    Generate a knowledge graph from one or multiple schemas.

    Supports both auto-detection and explicit relationship pairs (v2).
    """
    try:
        start_time = time.time()

        # Determine which schemas to process
        schema_names = request.schema_names or [request.schema_name]

        # Build knowledge graph
        if len(schema_names) == 1:
            # Single schema - use original method with optional LLM enhancement
            schema = SchemaParser.load_schema(schema_names[0])
            kg = SchemaParser.build_knowledge_graph(
                schema_names[0],
                request.kg_name,
                schema,
                use_llm=request.use_llm_enhancement,
                field_preferences=request.field_preferences
            )
        else:
            # Multiple schemas - use merged method with cross-schema relationships
            kg = SchemaParser.build_merged_knowledge_graph(
                schema_names,
                request.kg_name,
                use_llm=request.use_llm_enhancement,
                field_preferences=request.field_preferences
            )

        # Add explicit relationship pairs if provided (v2)
        explicit_pairs_added = 0
        if request.relationship_pairs:
            logger.info(f"Adding {len(request.relationship_pairs)} explicit relationship pairs to KG")

            from kg_builder.services.kg_relationship_service import add_explicit_relationships_to_kg
            from kg_builder.services.schema_parser import filter_relationship_pairs

            # Prepare excluded fields set
            excluded_fields_set = set(request.excluded_fields) if request.excluded_fields else None
            if excluded_fields_set:
                logger.info(f"Using {len(excluded_fields_set)} user-defined excluded fields")
            else:
                logger.info("Using default excluded fields")

            # Filter out pairs with excluded fields
            filtered_pairs_dict = filter_relationship_pairs(request.relationship_pairs, excluded_fields_set)
            logger.info(f"Filtered pairs: {len(request.relationship_pairs)} → {len(filtered_pairs_dict)}")

            # Prepare schemas info for validation
            schemas_info = {}
            for schema_name in schema_names:
                try:
                    schema = SchemaParser.load_schema(schema_name)
                    schemas_info[schema_name] = {
                        "tables": list(schema.tables.keys()),
                        "columns": {
                            table_name: [col.name for col in table.columns]
                            for table_name, table in schema.tables.items()
                        }
                    }
                except Exception as e:
                    logger.warning(f"Failed to load schema {schema_name}: {e}")

            try:
                # Convert dict pairs to RelationshipPair objects
                pairs = [RelationshipPair(**pair_dict) for pair_dict in filtered_pairs_dict]

                # Add explicit pairs to KG
                kg, explicit_pairs_added = add_explicit_relationships_to_kg(kg, pairs, schemas_info)
                logger.info(f"Added {explicit_pairs_added} explicit relationship pairs to KG")

            except Exception as e:
                logger.error(f"Failed to process explicit relationship pairs: {e}")
                # Continue with KG generation even if pairs fail

        # Final step: Filter ALL relationships in KG to remove excluded fields
        # This ensures that relationships from LLM inference, pattern matching, etc. are also filtered
        if request.excluded_fields:
            excluded_fields_set = set(request.excluded_fields)
            logger.info(f"Applying final filter to remove relationships with excluded fields: {len(excluded_fields_set)} fields")

            from kg_builder.services.schema_parser import is_excluded_field

            original_count = len(kg.relationships)
            filtered_relationships = []

            for rel in kg.relationships:
                # Check if relationship has column properties
                if rel.properties:
                    source_col = rel.properties.get("source_column")
                    target_col = rel.properties.get("target_column")

                    if source_col and target_col:
                        # Check if either column is excluded
                        if is_excluded_field(source_col, excluded_fields_set) or is_excluded_field(target_col, excluded_fields_set):
                            logger.debug(f"⛔ Removing relationship from KG (excluded field): {rel.source_id} ({source_col}) → {rel.target_id} ({target_col})")
                            continue  # Skip this relationship

                # Keep this relationship
                filtered_relationships.append(rel)

            kg.relationships = filtered_relationships
            removed_count = original_count - len(filtered_relationships)

            if removed_count > 0:
                logger.info(f"✓ Filtered KG relationships: {original_count} → {len(filtered_relationships)} (removed {removed_count} with excluded fields)")
            else:
                logger.info(f"✓ No relationships removed by exclusion filter")

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

        # Build message
        message = f"Knowledge graph '{request.kg_name}' generated successfully from {len(schema_names)} schema(s)"
        if explicit_pairs_added > 0:
            message += f" with {explicit_pairs_added} explicit relationship pair(s)"

        return KGGenerationResponse(
            success=True,
            schemas_processed=schema_names,
            message=message,
            kg_name=request.kg_name,
            nodes_count=len(kg.nodes),
            relationships_count=len(kg.relationships),
            nodes=kg.nodes,
            relationships=kg.relationships,
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


@router.get("/kg/{kg_name}/metadata")
async def get_kg_metadata(kg_name: str, backend: str = "graphiti"):
    """Get metadata for a knowledge graph, including table aliases."""
    try:
        backend_obj = get_graphiti_backend()
        metadata = backend_obj.get_kg_metadata(kg_name)

        if not metadata:
            raise HTTPException(status_code=404, detail=f"Metadata not found for KG '{kg_name}'")

        return {
            "success": True,
            "kg_name": kg_name,
            "metadata": metadata,
            "table_aliases": metadata.get("table_aliases", {})
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving KG metadata: {e}")
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

    Supports both v1 (field_preferences) and v2 (reconciliation_pairs) approaches.

    Example v1 request (legacy):
    ```json
    {
      "schema_names": ["orderMgmt-catalog", "vendorDB-suppliers"],
      "kg_name": "unified_kg",
      "use_llm_enhancement": true,
      "min_confidence": 0.7,
      "field_preferences": [
        {
          "table_name": "products",
          "priority_fields": ["product_id"],
          "field_hints": {"product_id": "item_id"}
        }
      ]
    }
    ```

    Example v2 request (recommended):
    ```json
    {
      "schema_names": ["hana-material-schema", "ops-excel-schema", "rbp-gpu-schema"],
      "kg_name": "material_kg",
      "use_llm_enhancement": true,
      "min_confidence": 0.75,
      "reconciliation_pairs": [
        {
          "source_table": "hana_material_master",
          "source_columns": ["MATERIAL"],
          "target_table": "brz_lnd_OPS_EXCEL_GPU",
          "target_columns": ["PLANNING_SKU"],
          "match_type": "exact",
          "source_filters": null,
          "target_filters": {"Active_Inactive": "Active"},
          "bidirectional": true
        },
        {
          "source_table": "brz_lnd_OPS_EXCEL_GPU",
          "source_columns": ["PLANNING_SKU"],
          "target_table": "brz_lnd_RBP_GPU",
          "target_columns": ["Material"],
          "match_type": "exact"
        }
      ],
      "auto_discover_additional": true
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

        # Generate rules (supports both v1 and v2)
        ruleset = recon_service.generate_from_knowledge_graph(
            kg_name=request.kg_name,
            schema_names=request.schema_names,
            use_llm=request.use_llm_enhancement,
            min_confidence=request.min_confidence,
            field_preferences=request.field_preferences,
            reconciliation_pairs=request.reconciliation_pairs,
            table_hints=request.table_hints,
            auto_discover_additional=request.auto_discover_additional
        )

        # Save ruleset
        storage = get_rule_storage()
        storage.save_ruleset(ruleset)

        elapsed_ms = (time.time() - start_time) * 1000

        # Determine how many explicit vs discovered rules
        explicit_count = sum(1 for r in ruleset.rules if r.metadata.get('source', '').startswith('explicit_pair_v2'))
        discovered_count = len(ruleset.rules) - explicit_count

        message = f"Generated {len(ruleset.rules)} reconciliation rules"
        if request.reconciliation_pairs:
            message += f" ({explicit_count} explicit, {discovered_count} auto-discovered)"

        return RuleGenerationResponse(
            success=True,
            ruleset_id=ruleset.ruleset_id,
            rules_count=len(ruleset.rules),
            rules=ruleset.rules,
            generation_time_ms=elapsed_ms,
            message=message
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


@router.post("/reconciliation/execute-with-landing", response_model=LandingExecutionResponse)
async def execute_reconciliation_with_landing(request: LandingExecutionRequest):
    """
    Execute reconciliation using landing database approach.

    This endpoint uses a staging/landing database to handle multi-database reconciliation
    efficiently. It's designed for scenarios where source and target databases are on
    different servers or when dealing with large datasets.

    **How it works:**
    1. Extracts source data to landing database staging table
    2. Extracts target data to landing database staging table
    3. Performs reconciliation entirely in landing database (fast local JOINs)
    4. Calculates all KPIs in a single SQL query
    5. Stores results in MongoDB
    6. Optionally keeps staging tables for 24h for inspection

    **Performance Benefits:**
    - 10-15x faster than traditional approach
    - Constant memory usage (no in-memory data loading)
    - KPIs calculated in milliseconds (SQL aggregation vs Python loops)
    - Scales to billions of records

    **Requirements:**
    - Landing database must be configured (LANDING_DB_ENABLED=true)
    - Run scripts/init_landing_db.py first to initialize

    Args:
        request: Landing execution request with:
            - ruleset_id: ID of the ruleset to execute
            - source_db_config: Source database connection info
            - target_db_config: Target database connection info
            - landing_db_config: (Optional) Landing DB config (uses config if not provided)
            - limit: (Optional) Limit rows per staging table
            - keep_staging: Keep staging tables for inspection (default: True, 24h TTL)
            - store_in_mongodb: Store results in MongoDB (default: True)

    Returns:
        LandingExecutionResponse with:
            - Execution ID and timing metrics
            - Match counts and KPIs (RCR, DQCS, REI)
            - Staging table information
            - MongoDB document ID

    Example Request:
    ```json
    {
        "ruleset_id": "RECON_12345678",
        "source_db_config": {
            "db_type": "oracle",
            "host": "source-db.example.com",
            "port": 1521,
            "database": "ORCL",
            "username": "user",
            "password": "pass"
        },
        "target_db_config": {
            "db_type": "sqlserver",
            "host": "target-db.example.com",
            "port": 1433,
            "database": "TargetDB",
            "username": "user",
            "password": "pass"
        },
        "limit": 10000,
        "keep_staging": true,
        "store_in_mongodb": true
    }
    ```

    Example Response:
    ```json
    {
        "success": true,
        "execution_id": "EXEC_a1b2c3d4",
        "matched_count": 9500,
        "total_source_count": 10000,
        "rcr": 95.0,
        "rcr_status": "HEALTHY",
        "dqcs": 0.875,
        "dqcs_status": "GOOD",
        "rei": 85.5,
        "extraction_time_ms": 2500.0,
        "reconciliation_time_ms": 150.0,
        "total_time_ms": 2800.0,
        "source_staging": {
            "table_name": "recon_stage_EXEC_a1b2c3d4_source_20250124_120000",
            "row_count": 10000,
            "size_mb": 15.2,
            "indexes": ["idx_recon_stage_EXEC_a1b2c3d4_source_20250124_120000_id"]
        },
        "staging_retained": true,
        "staging_ttl_hours": 24
    }
    ```
    """
    try:
        from kg_builder.services.landing_reconciliation_executor import get_landing_reconciliation_executor
        from kg_builder.models import LandingExecutionResponse

        logger.info(f"Landing reconciliation request for ruleset: {request.ruleset_id}")

        # Get landing executor
        executor = get_landing_reconciliation_executor()
        if executor is None:
            raise HTTPException(
                status_code=503,
                detail="Landing database is not configured or not available. "
                       "Set LANDING_DB_ENABLED=true and run scripts/init_landing_db.py"
            )

        # Execute reconciliation
        response = executor.execute(request)

        logger.info(f"Landing reconciliation completed: {response.execution_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing landing reconciliation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reconciliation/results/{document_id}")
async def get_reconciliation_result(document_id: str):
    """
    Retrieve a specific reconciliation result from MongoDB by document ID.

    Args:
        document_id: MongoDB document ID

    Returns:
        Reconciliation result document
    """
    try:
        from kg_builder.services.mongodb_storage import get_mongodb_storage

        mongo_storage = get_mongodb_storage()
        result = mongo_storage.get_reconciliation_result(document_id)

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Reconciliation result with ID '{document_id}' not found"
            )

        return {
            "success": True,
            "result": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving reconciliation result: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reconciliation/results")
async def list_reconciliation_results(
    ruleset_id: Optional[str] = None,
    limit: int = 100,
    skip: int = 0
):
    """
    List reconciliation results from MongoDB.

    Args:
        ruleset_id: Optional filter by ruleset ID
        limit: Maximum number of results to return (default: 100)
        skip: Number of results to skip for pagination (default: 0)

    Returns:
        List of reconciliation result documents
    """
    try:
        from kg_builder.services.mongodb_storage import get_mongodb_storage

        mongo_storage = get_mongodb_storage()
        results = mongo_storage.list_reconciliation_results(
            ruleset_id=ruleset_id,
            limit=limit,
            skip=skip
        )

        return {
            "success": True,
            "results": results,
            "count": len(results),
            "limit": limit,
            "skip": skip
        }

    except Exception as e:
        logger.error(f"Error listing reconciliation results: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reconciliation/statistics")
async def get_reconciliation_statistics(ruleset_id: Optional[str] = None):
    """
    Get summary statistics for reconciliation results.

    Args:
        ruleset_id: Optional filter by ruleset ID

    Returns:
        Summary statistics
    """
    try:
        from kg_builder.services.mongodb_storage import get_mongodb_storage

        mongo_storage = get_mongodb_storage()
        stats = mongo_storage.get_summary_statistics(ruleset_id=ruleset_id)

        return {
            "success": True,
            "statistics": stats
        }

    except Exception as e:
        logger.error(f"Error getting reconciliation statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reconciliation/results/{document_id}")
async def delete_reconciliation_result(document_id: str):
    """
    Delete a specific reconciliation result from MongoDB by document ID.

    Args:
        document_id: MongoDB document ID

    Returns:
        Success status
    """
    try:
        from kg_builder.services.mongodb_storage import get_mongodb_storage

        mongo_storage = get_mongodb_storage()
        deleted = mongo_storage.delete_reconciliation_result(document_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Reconciliation result with ID '{document_id}' not found"
            )

        return {
            "success": True,
            "message": f"Reconciliation result '{document_id}' deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting reconciliation result: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Natural Language Relationship endpoints
@router.post("/kg/relationships/natural-language", response_model=NLRelationshipResponse)
async def add_natural_language_relationships(request: NLRelationshipRequest):
    """
    Add relationships defined in natural language to knowledge graph.

    This endpoint allows users to define custom relationships between entities
    using natural language instead of structured formats. The system parses the
    definitions and adds them to the knowledge graph.

    Supported input formats:
    1. Natural Language: "Products are supplied by Vendors"
    2. Semi-Structured: "catalog.product_id → vendor.vendor_id (SUPPLIED_BY)"
    3. Pseudo-SQL: "SELECT * FROM products JOIN vendors ON ..."
    4. Business Rules: "IF product.status='active' THEN ..."

    Example request:
    ```json
    {
      "kg_name": "demo_kg",
      "schemas": ["orderMgmt-catalog", "vendorDB-suppliers"],
      "definitions": [
        "Products are supplied by Vendors",
        "Orders contain Products with quantity",
        "Vendors have Locations"
      ],
      "use_llm": true,
      "min_confidence": 0.7
    }
    ```

    Args:
        request: NL relationship request with definitions

    Returns:
        NLRelationshipResponse with parsed relationships and status
    """
    try:
        start_time = time.time()

        logger.info(f"Processing {len(request.definitions)} natural language relationship definitions")

        # Get parser
        parser = get_nl_relationship_parser()

        # Load schemas
        try:
            schemas_info = {}
            for schema_name in request.schemas:
                schema = SchemaParser.load_schema(schema_name)
                schemas_info[schema_name] = {
                    "tables": list(schema.tables.keys()),
                    "columns": {
                        table_name: [col.name for col in table.columns]
                        for table_name, table in schema.tables.items()
                    }
                }
            logger.debug(f"Loaded {len(schemas_info)} schemas")
        except Exception as e:
            logger.error(f"Error loading schemas: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to load schemas: {str(e)}")

        # Parse definitions
        all_relationships = []
        errors = []

        for definition in request.definitions:
            try:
                logger.debug(f"Parsing definition: {definition}")
                parsed = parser.parse(definition, schemas_info, use_llm=request.use_llm)

                # Filter by confidence
                filtered = [r for r in parsed if r.confidence >= request.min_confidence]

                if not filtered and parsed:
                    errors.append(
                        f"Definition '{definition}' parsed but all relationships below "
                        f"confidence threshold ({request.min_confidence})"
                    )
                else:
                    all_relationships.extend(filtered)
                    logger.debug(f"Successfully parsed: {len(filtered)} relationships")

            except Exception as e:
                error_msg = f"Failed to parse '{definition}': {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        # Prepare response
        response = NLRelationshipResponse(
            success=len(errors) == 0,
            relationships=all_relationships,
            parsed_count=len(all_relationships),
            failed_count=len(errors),
            errors=errors,
            processing_time_ms=processing_time_ms
        )

        logger.info(
            f"NL relationship parsing complete: {len(all_relationships)} parsed, "
            f"{len(errors)} errors, {processing_time_ms:.2f}ms"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding natural language relationships: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class KGIntegrationRequest(BaseModel):
    """Request model for KG integration with NL relationships and/or explicit pairs."""
    kg_name: str
    schemas: List[str]

    # V1: Natural language definitions (ambiguous)
    nl_definitions: Optional[List[str]] = []

    # V2: Explicit relationship pairs (recommended)
    relationship_pairs: Optional[List[dict]] = []  # Will be converted to RelationshipPair

    # Field exclusion configuration
    excluded_fields: Optional[List[str]] = None

    use_llm: bool = True
    min_confidence: float = 0.7
    merge_strategy: str = "union"


@router.post("/kg/integrate-nl-relationships")
async def integrate_nl_relationships_to_kg(request: KGIntegrationRequest):
    """
    Integrate natural language-defined relationships into an existing knowledge graph.

    This endpoint:
    1. Parses natural language relationship definitions
    2. Adds them to the existing knowledge graph
    3. Merges with auto-detected relationships
    4. Returns updated KG with statistics
    """
    try:
        start_time = time.time()

        # Step 1: Generate or load the knowledge graph
        logger.info(f"Loading knowledge graph: {request.kg_name}")
        try:
            kg = SchemaParser.build_merged_knowledge_graph(request.schemas, request.kg_name, use_llm=request.use_llm)
        except Exception as e:
            logger.error(f"Failed to build KG: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to build KG: {str(e)}")

        logger.info(f"Loaded KG with {len(kg.nodes)} nodes and {len(kg.relationships)} relationships")

        # Prepare schemas info for both NL parsing and pair validation
        schemas_info = {}
        for schema_name in request.schemas:
            try:
                schema = SchemaParser.load_schema(schema_name)
                schemas_info[schema_name] = {
                    "tables": list(schema.tables.keys()),
                    "columns": {
                        table_name: [col.name for col in table.columns]
                        for table_name, table in schema.tables.items()
                    }
                }
            except Exception as e:
                logger.warning(f"Failed to load schema {schema_name}: {e}")

        # Step 2a: Parse natural language definitions (V1)
        all_nl_relationships = []
        parse_errors = []

        if request.nl_definitions:
            logger.info(f"Parsing {len(request.nl_definitions)} NL definitions")
            parser = get_nl_relationship_parser()

            for definition in request.nl_definitions:
                try:
                    parsed = parser.parse(definition, schemas_info, use_llm=request.use_llm)
                    filtered = [r for r in parsed if r.confidence >= request.min_confidence]
                    all_nl_relationships.extend(filtered)
                except Exception as e:
                    error_msg = f"Failed to parse '{definition}': {str(e)}"
                    logger.warning(error_msg)
                    parse_errors.append(error_msg)

            logger.info(f"Parsed {len(all_nl_relationships)} NL relationships")

        # Step 2b: Process explicit relationship pairs (V2 - Recommended)
        explicit_pair_count = 0
        if request.relationship_pairs:
            logger.info(f"Processing {len(request.relationship_pairs)} explicit relationship pairs (v2)")

            from kg_builder.services.kg_relationship_service import add_explicit_relationships_to_kg
            from kg_builder.services.schema_parser import filter_relationship_pairs

            try:
                # Prepare excluded fields set
                excluded_fields_set = set(request.excluded_fields) if request.excluded_fields else None
                if excluded_fields_set:
                    logger.info(f"Using {len(excluded_fields_set)} user-defined excluded fields")
                else:
                    logger.info("Using default excluded fields")

                # Filter out pairs with excluded fields
                filtered_pairs_dict = filter_relationship_pairs(request.relationship_pairs, excluded_fields_set)
                logger.info(f"Filtered pairs: {len(request.relationship_pairs)} → {len(filtered_pairs_dict)}")

                # Convert dict pairs to RelationshipPair objects
                pairs = [RelationshipPair(**pair_dict) for pair_dict in filtered_pairs_dict]

                # Add explicit pairs to KG
                kg, added_count = add_explicit_relationships_to_kg(kg, pairs, schemas_info)
                explicit_pair_count = added_count
                logger.info(f"Added {explicit_pair_count} explicit relationship pairs to KG")

            except Exception as e:
                error_msg = f"Failed to process explicit relationship pairs: {str(e)}"
                logger.error(error_msg)
                parse_errors.append(error_msg)

        # Step 3: Add NL relationships to KG (if any)
        if all_nl_relationships:
            logger.info("Adding NL relationships to knowledge graph")
            kg = SchemaParser.add_nl_relationships_to_kg(kg, all_nl_relationships)

        # Step 4: Merge relationships
        logger.info(f"Merging relationships using strategy: {request.merge_strategy}")
        kg = SchemaParser.merge_relationships(kg, strategy=request.merge_strategy)

        # Step 4.5: Final filter to remove relationships with excluded fields
        # This ensures all relationships from all sources respect exclusions
        if request.excluded_fields:
            excluded_fields_set = set(request.excluded_fields)
            logger.info(f"Applying final filter to remove relationships with excluded fields: {len(excluded_fields_set)} fields")

            from kg_builder.services.schema_parser import is_excluded_field

            original_count = len(kg.relationships)
            filtered_relationships = []

            for rel in kg.relationships:
                # Check if relationship has column properties
                if rel.properties:
                    source_col = rel.properties.get("source_column")
                    target_col = rel.properties.get("target_column")

                    if source_col and target_col:
                        # Check if either column is excluded
                        if is_excluded_field(source_col, excluded_fields_set) or is_excluded_field(target_col, excluded_fields_set):
                            logger.debug(f"⛔ Removing relationship from KG (excluded field): {rel.source_id} ({source_col}) → {rel.target_id} ({target_col})")
                            continue  # Skip this relationship

                # Keep this relationship
                filtered_relationships.append(rel)

            kg.relationships = filtered_relationships
            removed_count = original_count - len(filtered_relationships)

            if removed_count > 0:
                logger.info(f"✓ Filtered KG relationships: {original_count} → {len(filtered_relationships)} (removed {removed_count} with excluded fields)")
            else:
                logger.info(f"✓ No relationships removed by exclusion filter")

        # Step 5: Get statistics
        stats = SchemaParser.get_relationship_statistics(kg)

        processing_time_ms = (time.time() - start_time) * 1000

        logger.info(
            f"KG integration complete: {len(kg.relationships)} total relationships, "
            f"{stats['nl_defined']} NL-defined, {stats['auto_detected']} auto-detected, "
            f"{processing_time_ms:.2f}ms"
        )

        return {
            "success": len(parse_errors) == 0,
            "kg_name": request.kg_name,
            "nodes_count": len(kg.nodes),
            "relationships_count": len(kg.relationships),
            "nl_relationships_added": len(all_nl_relationships),
            "explicit_pairs_added": explicit_pair_count,
            "total_relationships": len(kg.relationships),
            "statistics": stats,
            "errors": parse_errors,
            "processing_time_ms": processing_time_ms,
            "knowledge_graph": kg
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error integrating NL relationships to KG: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kg/statistics")
async def get_kg_statistics(request: KGIntegrationRequest):
    """
    Get statistics about a knowledge graph.
    """
    try:
        logger.info(f"Getting statistics for KG: {request.kg_name}")

        # Build KG
        kg = SchemaParser.build_merged_knowledge_graph(request.schemas, request.kg_name, use_llm=False)

        # Get statistics
        stats = SchemaParser.get_relationship_statistics(kg)

        return {
            "kg_name": request.kg_name,
            "nodes_count": len(kg.nodes),
            "relationships_count": len(kg.relationships),
            "statistics": stats
        }

    except Exception as e:
        logger.error(f"Error getting KG statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# KPI Routes - Data Quality and Reconciliation Monitoring
# ============================================================================

@router.post("/kpi/calculate", response_model=KPICalculationResponse)
async def calculate_kpis(request: KPICalculationRequest):
    """
    Calculate all three KPIs for a reconciliation execution.

    KPIs calculated:
    1. Reconciliation Coverage Rate (RCR) - % of matched records
    2. Data Quality Confidence Score (DQCS) - weighted confidence average
    3. Reconciliation Efficiency Index (REI) - efficiency score
    """
    try:
        from kg_builder.services.kpi_service import KPIService

        logger.info(f"Calculating KPIs for execution: {request.execution_id}")

        kpi_service = KPIService()
        kpi_service._ensure_indexes()

        # Calculate RCR
        rcr_doc = kpi_service.calculate_rcr(
            matched_count=request.matched_count,
            total_source_count=request.total_source_count,
            ruleset_id=request.ruleset_id,
            ruleset_name=request.ruleset_name,
            execution_id=request.execution_id,
            source_kg=request.source_kg,
            source_schemas=request.source_schemas
        )
        rcr_id = kpi_service.store_kpi("RECONCILIATION_COVERAGE_RATE", rcr_doc)
        rcr_value = rcr_doc["metrics"]["coverage_rate"]

        # Calculate DQCS
        dqcs_doc = kpi_service.calculate_dqcs(
            matched_records=request.matched_records,
            ruleset_id=request.ruleset_id,
            ruleset_name=request.ruleset_name,
            execution_id=request.execution_id,
            source_kg=request.source_kg
        )
        dqcs_id = kpi_service.store_kpi("DATA_QUALITY_CONFIDENCE_SCORE", dqcs_doc)
        dqcs_value = dqcs_doc["metrics"]["overall_confidence_score"]

        # Calculate REI
        rei_doc = kpi_service.calculate_rei(
            matched_count=request.matched_count,
            total_source_count=request.total_source_count,
            active_rules=request.active_rules,
            total_rules=request.total_rules,
            execution_time_ms=request.execution_time_ms,
            ruleset_id=request.ruleset_id,
            ruleset_name=request.ruleset_name,
            execution_id=request.execution_id,
            source_kg=request.source_kg,
            resource_metrics=request.resource_metrics
        )
        rei_id = kpi_service.store_kpi("RECONCILIATION_EFFICIENCY_INDEX", rei_doc)
        rei_value = rei_doc["metrics"]["efficiency_index"]

        kpi_service.close()

        logger.info(f"KPIs calculated successfully - RCR: {rcr_value}%, DQCS: {dqcs_value}, REI: {rei_value}")

        return KPICalculationResponse(
            success=True,
            rcr_id=rcr_id,
            dqcs_id=dqcs_id,
            rei_id=rei_id,
            rcr_value=rcr_value,
            dqcs_value=dqcs_value,
            rei_value=rei_value
        )

    except Exception as e:
        logger.error(f"Error calculating KPIs: {e}", exc_info=True)
        return KPICalculationResponse(
            success=False,
            error=str(e)
        )


@router.get("/kpi/rcr/{ruleset_id}")
async def get_latest_rcr(ruleset_id: str):
    """Get latest Reconciliation Coverage Rate for a ruleset."""
    try:
        from kg_builder.services.kpi_service import KPIService

        kpi_service = KPIService()
        kpi = kpi_service.get_latest_kpi("RECONCILIATION_COVERAGE_RATE", ruleset_id)
        kpi_service.close()

        if not kpi:
            raise HTTPException(status_code=404, detail=f"No RCR found for ruleset {ruleset_id}")

        # Convert ObjectId to string for JSON serialization
        kpi['_id'] = str(kpi['_id'])
        return kpi

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving RCR: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpi/dqcs/{ruleset_id}")
async def get_latest_dqcs(ruleset_id: str):
    """Get latest Data Quality Confidence Score for a ruleset."""
    try:
        from kg_builder.services.kpi_service import KPIService

        kpi_service = KPIService()
        kpi = kpi_service.get_latest_kpi("DATA_QUALITY_CONFIDENCE_SCORE", ruleset_id)
        kpi_service.close()

        if not kpi:
            raise HTTPException(status_code=404, detail=f"No DQCS found for ruleset {ruleset_id}")

        kpi['_id'] = str(kpi['_id'])
        return kpi

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving DQCS: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpi/rei/{ruleset_id}")
async def get_latest_rei(ruleset_id: str):
    """Get latest Reconciliation Efficiency Index for a ruleset."""
    try:
        from kg_builder.services.kpi_service import KPIService

        kpi_service = KPIService()
        kpi = kpi_service.get_latest_kpi("RECONCILIATION_EFFICIENCY_INDEX", ruleset_id)
        kpi_service.close()

        if not kpi:
            raise HTTPException(status_code=404, detail=f"No REI found for ruleset {ruleset_id}")

        kpi['_id'] = str(kpi['_id'])
        return kpi

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving REI: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# File-Based KPI Management Endpoints
# ============================================================================

@router.post("/reconciliation/kpi/create")
async def create_kpi(request: KPIDefinitionRequest):
    """
    Create a new KPI configuration (file-based storage).

    This endpoint allows users to create and configure KPIs based on reconciliation results.
    KPI definitions are stored in JSON files without requiring MongoDB.

    Args:
        request: KPI creation request with name, type, thresholds, and ruleset ID

    Returns:
        Success response with created KPI ID

    Example request:
    ```json
    {
      "kpi_name": "Material Match Rate",
      "kpi_description": "Percentage of materials matched between source and target",
      "kpi_type": "match_rate",
      "ruleset_id": "RECON_ABC123",
      "thresholds": {
        "warning_threshold": 80.0,
        "critical_threshold": 70.0,
        "comparison_operator": "less_than"
      },
      "enabled": true
    }
    ```
    """
    try:
        from kg_builder.services.kpi_file_service import KPIFileService

        service = KPIFileService()
        kpi_dict = request.model_dump()
        kpi_id = service.create_kpi_definition(kpi_dict)

        logger.info(f"Created KPI: {kpi_id} - {request.kpi_name}")

        return {
            "success": True,
            "kpi_id": kpi_id,
            "message": f"KPI '{request.kpi_name}' created successfully"
        }

    except Exception as e:
        logger.error(f"Error creating KPI: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/reconciliation/kpi/list")
async def list_kpis(ruleset_id: Optional[str] = None):
    """
    List all KPI configurations, optionally filtered by ruleset (file-based).

    Args:
        ruleset_id: Optional ruleset ID to filter KPIs

    Returns:
        List of KPI configurations
    """
    try:
        from kg_builder.services.kpi_file_service import KPIFileService

        service = KPIFileService()
        kpis = service.list_kpi_definitions(ruleset_id)

        logger.info(f"Listed {len(kpis)} KPIs")

        return {
            "success": True,
            "count": len(kpis),
            "kpis": kpis
        }

    except Exception as e:
        logger.error(f"Error listing KPIs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "kpis": []
        }


@router.get("/reconciliation/kpi/{kpi_id}")
async def get_kpi(kpi_id: str):
    """
    Get KPI configuration by ID (file-based).

    Args:
        kpi_id: KPI ID

    Returns:
        KPI configuration
    """
    try:
        from kg_builder.services.kpi_file_service import KPIFileService

        service = KPIFileService()
        kpi = service.get_kpi_definition(kpi_id)

        if not kpi:
            raise HTTPException(status_code=404, detail=f"KPI not found: {kpi_id}")

        return {
            "success": True,
            "kpi": kpi
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving KPI: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reconciliation/kpi/{kpi_id}/evidence")
async def get_kpi_evidence(kpi_id: str, request: EvidenceRequest):
    """
    Retrieve evidence data for KPI drill-down (file-based).

    This endpoint returns the detailed records that contributed to the KPI calculation,
    allowing users to drill down and analyze specific records. Data is queried directly
    from the source database.

    Args:
        kpi_id: KPI ID
        request: Evidence drill-down request with filters and pagination

    Returns:
        Evidence records with drill-down capability

    Example request:
    ```json
    {
      "match_status": "unmatched_source",
      "limit": 100,
      "offset": 0
    }
    ```
    """
    try:
        from kg_builder.services.kpi_file_service import KPIFileService

        service = KPIFileService()
        result = service.get_evidence_data(
            kpi_id=kpi_id,
            match_status=request.match_status,
            limit=request.limit,
            offset=request.offset
        )

        if not result.get("success"):
            return {
                "success": False,
                "kpi_id": kpi_id,
                "error": result.get("error", "Unknown error"),
                "evidence_records": [],
                "total_count": 0
            }

        logger.info(
            f"Retrieved {result['total_count']} evidence records for KPI {kpi_id}"
        )

        return {
            "success": True,
            "kpi_id": kpi_id,
            "evidence_records": result["evidence_records"],
            "total_count": result["total_count"],
            "limit": result["limit"],
            "offset": result["offset"]
        }

    except Exception as e:
        logger.error(f"Error retrieving KPI evidence: {e}", exc_info=True)
        return {
            "success": False,
            "kpi_id": kpi_id,
            "error": str(e),
            "evidence_records": [],
            "total_count": 0
        }


@router.put("/reconciliation/kpi/{kpi_id}")
async def update_kpi(kpi_id: str, request: KPIUpdateRequest):
    """
    Update an existing KPI configuration (file-based).

    Args:
        kpi_id: KPI ID to update
        request: Update request with fields to modify

    Returns:
        Success response
    """
    try:
        from kg_builder.services.kpi_file_service import KPIFileService

        service = KPIFileService()
        updates = {k: v for k, v in request.model_dump().items() if v is not None}
        success = service.update_kpi_definition(kpi_id, updates)

        if not success:
            raise HTTPException(status_code=404, detail=f"KPI not found: {kpi_id}")

        logger.info(f"Updated KPI: {kpi_id}")

        return {
            "success": True,
            "message": f"KPI {kpi_id} updated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating KPI: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


@router.delete("/reconciliation/kpi/{kpi_id}")
async def delete_kpi(kpi_id: str):
    """
    Delete a KPI configuration (file-based).

    Args:
        kpi_id: KPI ID to delete

    Returns:
        Success response
    """
    try:
        from kg_builder.services.kpi_file_service import KPIFileService

        service = KPIFileService()
        success = service.delete_kpi_definition(kpi_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"KPI not found: {kpi_id}")

        logger.info(f"Deleted KPI: {kpi_id}")

        return {
            "success": True,
            "message": f"KPI {kpi_id} deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting KPI: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/reconciliation/kpi/{kpi_id}/execute")
async def execute_kpi(kpi_id: str, request: KPIExecutionRequest):
    """
    Execute a KPI and calculate its value (file-based).

    This endpoint runs the KPI calculation against the current data and stores the result.

    Args:
        kpi_id: KPI ID to execute
        request: Execution request with optional overrides

    Returns:
        KPI execution result
    """
    try:
        from kg_builder.services.kpi_file_service import KPIFileService

        service = KPIFileService()
        result = service.execute_kpi(kpi_id, request.ruleset_id)

        logger.info(
            f"Executed KPI {kpi_id}: value={result['calculated_value']}, status={result['status']}"
        )

        return {
            "success": True,
            "result": result,
            "result_id": result["result_id"]
        }

    except Exception as e:
        logger.error(f"Error executing KPI: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/reconciliation/kpi/execute/batch")
async def execute_multiple_kpis(request: BatchExecutionRequest):
    """
    Execute multiple KPIs in batch (file-based).

    Args:
        request: Batch execution request with list of KPI IDs

    Returns:
        Results for all executed KPIs
    """
    try:
        from kg_builder.services.kpi_file_service import KPIFileService

        service = KPIFileService()
        results = []
        errors = []

        for kpi_id in request.kpi_ids:
            try:
                result = service.execute_kpi(kpi_id, request.ruleset_id)
                results.append(result)
            except Exception as e:
                errors.append({
                    "kpi_id": kpi_id,
                    "error": str(e)
                })

        logger.info(f"Executed {len(results)} KPIs successfully, {len(errors)} failed")

        return {
            "success": True,
            "results": results,
            "errors": errors,
            "total_executed": len(results),
            "total_failed": len(errors)
        }

    except Exception as e:
        logger.error(f"Error executing batch KPIs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/reconciliation/kpi/results")
async def list_kpi_results(kpi_id: Optional[str] = None, limit: int = 50):
    """
    List KPI execution results (file-based).

    Args:
        kpi_id: Optional KPI ID to filter results
        limit: Maximum number of results to return

    Returns:
        List of KPI results
    """
    try:
        from kg_builder.services.kpi_file_service import KPIFileService

        service = KPIFileService()
        results = service.list_kpi_results(kpi_id, limit)

        logger.info(f"Listed {len(results)} KPI results")

        return {
            "success": True,
            "results": results,
            "count": len(results)
        }

    except Exception as e:
        logger.error(f"Error listing KPI results: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "results": []
        }


@router.get("/reconciliation/kpi/results/{result_id}")
async def get_kpi_result(result_id: str):
    """
    Get a specific KPI result by ID (file-based).

    Args:
        result_id: Result ID

    Returns:
        KPI result details
    """
    try:
        from kg_builder.services.kpi_file_service import KPIFileService

        service = KPIFileService()
        result = service.get_kpi_result(result_id)

        if not result:
            raise HTTPException(status_code=404, detail=f"Result not found: {result_id}")

        return {
            "success": True,
            "result": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving KPI result: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reconciliation/kpi/results/{result_id}")
async def delete_kpi_result(result_id: str):
    """
    Delete a KPI result (file-based).

    Args:
        result_id: Result ID to delete

    Returns:
        Success response
    """
    try:
        from kg_builder.services.kpi_file_service import KPIFileService

        service = KPIFileService()
        success = service.delete_kpi_result(result_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"Result not found: {result_id}")

        logger.info(f"Deleted KPI result: {result_id}")

        return {
            "success": True,
            "message": f"Result {result_id} deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting KPI result: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


# Natural Language Query Execution Endpoints
@router.post("/kg/nl-queries/execute", response_model=NLQueryExecutionResponse)
async def execute_nl_queries(request: NLQueryExecutionRequest):
    """
    Execute natural language definitions as data queries.

    Each definition is:
    1. Classified as a query type (comparison, filter, aggregation, etc.)
    2. Parsed to extract intent (source table, target table, operation, filters)
    3. Uses Knowledge Graph to infer join columns
    4. Generates SQL query
    5. Executes query and returns results

    This is different from /kg/integrate-nl-relationships which adds relationships to KG.
    This endpoint executes queries and returns actual data results.

    Args:
        request: NLQueryExecutionRequest with definitions to execute

    Returns:
        NLQueryExecutionResponse with query results and statistics

    Example:
        POST /v1/kg/nl-queries/execute
        {
            "kg_name": "KG_101",
            "schemas": ["newdqschema"],
            "definitions": [
                "Show me all products in RBP GPU which are not in OPS Excel",
                "Show me all products in RBP GPU which are in active OPS Excel"
            ],
            "use_llm": true,
            "min_confidence": 0.7,
            "limit": 1000,
            "db_type": "mysql"
        }
    """
    try:
        from kg_builder.services.nl_query_classifier import get_nl_query_classifier
        from kg_builder.services.nl_query_parser import get_nl_query_parser
        from kg_builder.services.nl_query_executor import get_nl_query_executor
        from kg_builder.services.schema_parser import SchemaParser

        logger.info(f"Executing {len(request.definitions)} NL queries for KG: {request.kg_name}")

        # Step 1: Load knowledge graph from storage (don't rebuild!)
        try:
            # Try to load from Graphiti first
            from kg_builder.services.graphiti_backend import get_graphiti_backend

            graphiti = get_graphiti_backend()

            # Get entities and relationships from storage
            entities_data = graphiti.get_entities(request.kg_name)
            relationships_data = graphiti.get_relationships(request.kg_name)

            if not entities_data and not relationships_data:
                logger.warning(f"KG '{request.kg_name}' not found in storage, building from scratch")
                kg = SchemaParser.build_merged_knowledge_graph(
                    schema_names=request.schemas,
                    kg_name=request.kg_name,
                    use_llm=request.use_llm
                )
            else:
                # Reconstruct KG from storage
                logger.info(f"Loading KG '{request.kg_name}' from storage: {len(entities_data)} entities, {len(relationships_data)} relationships")

                from kg_builder.models import GraphNode, GraphRelationship, KnowledgeGraph

                # Convert entities
                nodes = []
                for entity in entities_data:
                    # Handle labels (Graphiti stores as array, GraphNode expects single label string)
                    labels = entity.get('labels', [])
                    label = labels[0] if labels else 'Node'

                    node = GraphNode(
                        id=entity.get('id', ''),
                        label=label,
                        properties=entity.get('properties', {}),
                        source_table=entity.get('source_table'),
                        source_column=entity.get('source_column')
                    )
                    nodes.append(node)

                # Convert relationships
                relationships = []
                for rel in relationships_data:
                    relationship = GraphRelationship(
                        source_id=rel.get('source_id', ''),
                        target_id=rel.get('target_id', ''),
                        relationship_type=rel.get('relationship_type', 'RELATES_TO'),
                        properties=rel.get('properties', {}),
                        source_column=rel.get('source_column'),
                        target_column=rel.get('target_column')
                    )
                    relationships.append(relationship)

                # Load metadata including table_aliases
                metadata = {}
                table_aliases = {}
                try:
                    kg_metadata = graphiti.get_kg_metadata(request.kg_name)
                    if kg_metadata:
                        table_aliases = kg_metadata.get('table_aliases', {})
                        # Store other metadata (excluding table_aliases which goes to KG field)
                        metadata = {k: v for k, v in kg_metadata.items() if k != 'table_aliases'}
                except Exception as e:
                    logger.warning(f"Could not load KG metadata: {e}")

                kg = KnowledgeGraph(
                    name=request.kg_name,
                    nodes=nodes,
                    relationships=relationships,
                    schema_file=",".join(request.schemas) if request.schemas else "unknown",
                    metadata=metadata,
                    table_aliases=table_aliases
                )

            logger.info(f"✓ KG loaded: {len(kg.nodes)} nodes, {len(kg.relationships)} relationships, {len(kg.table_aliases)} table aliases")

        except Exception as e:
            logger.error(f"Failed to load KG: {e}")
            return NLQueryExecutionResponse(
                success=False,
                kg_name=request.kg_name,
                total_definitions=len(request.definitions),
                successful=0,
                failed=len(request.definitions),
                error=f"Failed to load knowledge graph: {str(e)}"
            )

        # Step 2: Get schemas info
        schemas_info = {}
        for schema_name in request.schemas:
            try:
                schema_data = SchemaParser.load_schema(schema_name)
                schemas_info[schema_name] = schema_data
            except Exception as e:
                logger.warning(f"Failed to load schema {schema_name}: {e}")

        # Step 3: Parse each definition
        # Pass excluded_fields to parser to filter join columns
        if request.excluded_fields:
            logger.info(f"Using {len(request.excluded_fields)} excluded fields for query generation")
        parser = get_nl_query_parser(kg, schemas_info, request.excluded_fields)
        intents = []

        for definition in request.definitions:
            try:
                intent = parser.parse(definition, use_llm=request.use_llm)
                intents.append(intent)
                logger.debug(f"Parsed intent: {intent.to_dict()}")
            except Exception as e:
                logger.error(f"Failed to parse definition '{definition}': {e}")

        # Step 4: Execute queries
        executor = get_nl_query_executor(request.db_type)

        # Get database connection from source database
        logger.info(f"Getting source database connection for query execution (db_type: {request.db_type})")
        connection = get_source_database_connection()

        results = []
        try:
            if connection:
                logger.info(f"Executing {len(intents)} queries against source database")
                results = executor.execute_batch(intents, connection, request.limit)
            else:
                # Return results with SQL but no execution
                logger.warning("No database connection available - returning SQL only")
                for intent in intents:
                    from kg_builder.services.nl_sql_generator import get_nl_sql_generator
                    generator = get_nl_sql_generator(request.db_type)
                    try:
                        sql = generator.generate(intent)
                        from kg_builder.services.nl_query_executor import QueryResult
                        result = QueryResult(
                            definition=intent.definition,
                            query_type=intent.query_type,
                            operation=intent.operation,
                            sql=sql,
                            record_count=0,
                            records=[],
                            join_columns=intent.join_columns,
                            confidence=intent.confidence,
                            execution_time_ms=0.0,
                            error="No database connection available"
                        )
                        results.append(result)
                    except Exception as e:
                        from kg_builder.services.nl_query_executor import QueryResult
                        result = QueryResult(
                            definition=intent.definition,
                            query_type=intent.query_type,
                            operation=intent.operation,
                            sql="",
                            record_count=0,
                            records=[],
                            join_columns=intent.join_columns,
                            confidence=intent.confidence,
                            execution_time_ms=0.0,
                            error=str(e)
                        )
                        results.append(result)
        finally:
            # Close database connection
            if connection:
                try:
                    connection.close()
                    logger.info("Database connection closed")
                except Exception as e:
                    logger.warning(f"Error closing database connection: {e}")

        # Step 5: Get table mapping information
        from kg_builder.services.table_name_mapper import get_table_name_mapper
        mapper = get_table_name_mapper(schemas_info)
        table_mapping = mapper.get_table_info()

        # Step 6: Build response
        successful = len([r for r in results if r.error is None])
        failed = len([r for r in results if r.error is not None])

        statistics = executor.get_statistics(results)

        response = NLQueryExecutionResponse(
            success=failed == 0,
            kg_name=request.kg_name,
            total_definitions=len(request.definitions),
            successful=successful,
            failed=failed,
            results=[r.to_dict() for r in results],
            statistics=statistics,
            table_mapping=table_mapping
        )

        logger.info(f"NL query execution complete: {successful} successful, {failed} failed")
        return response

    except Exception as e:
        logger.error(f"Error executing NL queries: {e}", exc_info=True)
        return NLQueryExecutionResponse(
            success=False,
            kg_name=request.kg_name,
            total_definitions=len(request.definitions),
            successful=0,
            failed=len(request.definitions),
            error=str(e)
        )


# ==================== Landing KPI CRUD Endpoints ====================

def get_landing_kpi_service():
    """Get Landing KPI service instance."""
    from kg_builder.services.landing_kpi_service import LandingKPIService
    return LandingKPIService()


@router.post("/landing-kpi/kpis", tags=["Landing KPI"], response_model=dict)
async def create_kpi(request: KPICreateRequest):
    """Create a new KPI definition."""
    try:
        service = get_landing_kpi_service()
        kpi = service.create_kpi(request.dict())
        return {
            "success": True,
            "message": f"KPI '{kpi['name']}' created successfully",
            "kpi": kpi
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating KPI: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/landing-kpi/kpis", tags=["Landing KPI"], response_model=dict)
async def list_kpis(
    group_name: Optional[str] = None,
    is_active: Optional[bool] = True,
    search: Optional[str] = None
):
    """List all KPI definitions with optional filters."""
    try:
        service = get_landing_kpi_service()
        filters = {}
        if group_name:
            filters['group_name'] = group_name
        if is_active is not None:
            filters['is_active'] = is_active
        if search:
            filters['search'] = search

        kpis = service.list_kpis(filters if filters else None)
        return {
            "success": True,
            "total": len(kpis),
            "kpis": kpis
        }
    except Exception as e:
        logger.error(f"Error listing KPIs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/landing-kpi/kpis/{kpi_id}", tags=["Landing KPI"], response_model=dict)
async def get_kpi(kpi_id: int):
    """Get a specific KPI definition."""
    try:
        service = get_landing_kpi_service()
        kpi = service.get_kpi(kpi_id)
        if not kpi:
            raise HTTPException(status_code=404, detail=f"KPI ID {kpi_id} not found")
        return {
            "success": True,
            "kpi": kpi
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting KPI: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/landing-kpi/kpis/{kpi_id}", tags=["Landing KPI"], response_model=dict)
async def update_kpi(kpi_id: int, request: KPIUpdateRequestNew):
    """Update a KPI definition."""
    try:
        service = get_landing_kpi_service()
        kpi = service.get_kpi(kpi_id)
        if not kpi:
            raise HTTPException(status_code=404, detail=f"KPI ID {kpi_id} not found")

        updated_kpi = service.update_kpi(kpi_id, request.dict(exclude_unset=True))
        return {
            "success": True,
            "message": f"KPI ID {kpi_id} updated successfully",
            "kpi": updated_kpi
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating KPI: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/landing-kpi/kpis/{kpi_id}", tags=["Landing KPI"], response_model=dict)
async def delete_kpi(kpi_id: int):
    """Delete (soft delete) a KPI definition."""
    try:
        service = get_landing_kpi_service()
        kpi = service.get_kpi(kpi_id)
        if not kpi:
            raise HTTPException(status_code=404, detail=f"KPI ID {kpi_id} not found")

        service.delete_kpi(kpi_id)
        return {
            "success": True,
            "message": f"KPI ID {kpi_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting KPI: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/landing-kpi/kpis/{kpi_id}/execute", tags=["Landing KPI"], response_model=dict)
async def execute_kpi(kpi_id: int, request: KPIExecutionRequest):
    """Execute a KPI and store results.

    This endpoint creates an execution record and starts the KPI execution
    in the background using the NL Query Executor.

    Returns immediately with execution_id for polling results.
    """
    try:
        import threading
        from kg_builder.services.landing_kpi_executor import get_landing_kpi_executor

        service = get_landing_kpi_service()
        kpi = service.get_kpi(kpi_id)
        if not kpi:
            raise HTTPException(status_code=404, detail=f"KPI ID {kpi_id} not found")

        # Create execution record (status: pending)
        execution = service.execute_kpi(kpi_id, request.dict())
        execution_id = execution['id']

        # Start async execution in background thread
        executor = get_landing_kpi_executor()
        thread = threading.Thread(
            target=executor.execute_kpi_async,
            args=(kpi_id, execution_id, request.dict()),
            daemon=True
        )
        thread.start()
        logger.info(f"Started background execution thread for KPI {kpi_id}, Execution {execution_id}")

        return {
            "success": True,
            "message": f"KPI execution started (ID: {execution_id})",
            "execution_id": execution_id,
            "execution_result": execution
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing KPI: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/landing-kpi/kpis/{kpi_id}/executions", tags=["Landing KPI"], response_model=dict)
async def get_kpi_executions(kpi_id: int, status: Optional[str] = None):
    """Get execution history for a KPI."""
    try:
        service = get_landing_kpi_service()
        kpi = service.get_kpi(kpi_id)
        if not kpi:
            raise HTTPException(status_code=404, detail=f"KPI ID {kpi_id} not found")

        filters = {'status': status} if status else None
        executions = service.get_execution_results(kpi_id, filters)
        return {
            "success": True,
            "total": len(executions),
            "executions": executions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting KPI executions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/landing-kpi/executions/{execution_id}", tags=["Landing KPI"], response_model=dict)
async def get_execution_result(execution_id: int):
    """Get a specific execution result."""
    try:
        service = get_landing_kpi_service()
        execution = service.get_execution_result(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail=f"Execution ID {execution_id} not found")

        return {
            "success": True,
            "execution": execution
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution result: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/landing-kpi/executions/{execution_id}/drilldown", tags=["Landing KPI"], response_model=dict)
async def get_drilldown_data(execution_id: int, page: int = 1, page_size: int = 50):
    """Get paginated drill-down data for an execution result."""
    try:
        service = get_landing_kpi_service()
        drilldown = service.get_drilldown_data(execution_id, page, page_size)
        return {
            "success": True,
            **drilldown
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting drilldown data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Landing KPI Dashboard Endpoints ====================

@router.get("/v1/landing-kpi/dashboard", tags=["Landing KPI Dashboard"], response_model=dict)
async def get_kpi_dashboard():
    """
    Get all KPIs grouped by group name with their latest execution summary.

    Returns:
        {
            "success": true,
            "groups": [
                {
                    "group_name": "Data Quality",
                    "kpis": [
                        {
                            "id": 1,
                            "name": "Inactive Products in RBP",
                            "definition": "Show me all...",
                            "description": "...",
                            "kg_name": "KG_102",
                            "latest_execution": {
                                "executed_at": "2025-10-28T13:50:55",
                                "record_count": 42,
                                "status": "success",
                                "error_message": null
                            }
                        }
                    ]
                }
            ]
        }
    """
    try:
        service = get_landing_kpi_service()
        dashboard_data = service.get_dashboard_data()
        return {
            "success": True,
            **dashboard_data
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/v1/landing-kpi/{kpi_id}/latest-results", tags=["Landing KPI Dashboard"], response_model=dict)
async def get_kpi_latest_results(kpi_id: int):
    """
    Get the SQL results from the most recent execution for a specific KPI.

    Returns:
        {
            "success": true,
            "results": {
                "execution_id": 123,
                "kpi_id": 1,
                "sql_query": "SELECT * FROM ...",
                "result_data": [...],
                "column_names": ["col1", "col2", ...],
                "record_count": 42,
                "execution_status": "success",
                "execution_timestamp": "2025-10-28T13:50:55",
                "execution_time_ms": 1234.56,
                "confidence_score": 0.85,
                "error_message": null,
                "source_table": "brz_lnd_RBP_GPU",
                "target_table": "brz_lnd_OPS_EXCEL_GPU",
                "operation": "NOT_IN"
            }
        }
    """
    try:
        service = get_landing_kpi_service()

        # Verify KPI exists
        kpi = service.get_kpi(kpi_id)
        if not kpi:
            raise HTTPException(status_code=404, detail=f"KPI ID {kpi_id} not found")

        # Get latest results
        results = service.get_latest_results(kpi_id)
        if not results:
            return {
                "success": True,
                "results": None,
                "message": "No execution results found for this KPI"
            }

        return {
            "success": True,
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest results for KPI {kpi_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

