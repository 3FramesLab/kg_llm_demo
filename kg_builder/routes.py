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
    HealthCheckResponse, LLMExtractionResponse, LLMAnalysisResponse
)
from kg_builder.services.schema_parser import SchemaParser
from kg_builder.services.falkordb_backend import get_falkordb_backend
from kg_builder.services.graphiti_backend import get_graphiti_backend
from kg_builder.services.llm_service import get_llm_service

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
    """Generate a knowledge graph from a schema."""
    try:
        start_time = time.time()
        
        # Load schema
        schema = SchemaParser.load_schema(request.schema_name)
        
        # Build knowledge graph
        kg = SchemaParser.build_knowledge_graph(
            request.schema_name,
            request.kg_name,
            schema
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
            message=f"Knowledge graph '{request.kg_name}' generated successfully",
            kg_name=request.kg_name,
            nodes_count=len(kg.nodes),
            relationships_count=len(kg.relationships),
            backends_used=backends_used,
            generation_time_ms=elapsed_ms
        )
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Schema '{request.schema_name}' not found")
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

