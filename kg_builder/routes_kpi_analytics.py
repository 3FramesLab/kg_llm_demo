"""
FastAPI routes for KPI Analytics (Enhanced MS SQL Server API)
"""

import logging
import time
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from kg_builder.services.landing_kpi_service_mssql import LandingKPIServiceMSSQL
from kg_builder.models import KPICreateRequest, KPIUpdateRequest, KPIExecuteRequest

logger = logging.getLogger(__name__)

# Create router for KPI Analytics
kpi_analytics_router = APIRouter()

# Global service instance
_kpi_service = None

def get_kpi_analytics_service() -> LandingKPIServiceMSSQL:
    """Get KPI Analytics service instance."""
    global _kpi_service
    if _kpi_service is None:
        _kpi_service = LandingKPIServiceMSSQL()
    return _kpi_service


# Response Models
class KPIListResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    count: int
    storage_type: str = "mssql"


class KPIResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    storage_type: str = "mssql"


class KPIExecutionResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    storage_type: str = "mssql"


class HealthResponse(BaseModel):
    success: bool
    status: str
    database: str
    service: str
    timestamp: float


# KPI Management Routes
@kpi_analytics_router.get("/landing-kpi-mssql/kpis", response_model=KPIListResponse, tags=["KPI Analytics"])
async def get_all_kpis(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    group_name: Optional[str] = Query(None, description="Filter by group name"),
    limit: Optional[int] = Query(100, description="Maximum number of KPIs to return"),
    offset: Optional[int] = Query(0, description="Number of KPIs to skip")
):
    """Get all KPI definitions from MS SQL Server."""
    try:
        service = get_kpi_analytics_service()
        kpis = service.get_all_kpis(
            is_active=is_active,
            group_name=group_name,
            limit=limit,
            offset=offset
        )
        
        return KPIListResponse(
            success=True,
            data=kpis,
            count=len(kpis)
        )
    except Exception as e:
        logger.error(f"Error getting KPIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@kpi_analytics_router.post("/landing-kpi-mssql/kpis", response_model=KPIResponse, tags=["KPI Analytics"])
async def create_kpi(request: KPICreateRequest):
    """Create a new KPI definition in MS SQL Server."""
    try:
        service = get_kpi_analytics_service()
        kpi = service.create_kpi(request.dict())
        
        return KPIResponse(
            success=True,
            data=kpi
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating KPI: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@kpi_analytics_router.get("/landing-kpi-mssql/kpis/{kpi_id}", response_model=KPIResponse, tags=["KPI Analytics"])
async def get_kpi(kpi_id: int):
    """Get a specific KPI by ID from MS SQL Server."""
    try:
        service = get_kpi_analytics_service()
        kpi = service.get_kpi(kpi_id)
        
        if not kpi:
            raise HTTPException(status_code=404, detail=f"KPI with ID {kpi_id} not found")
        
        return KPIResponse(
            success=True,
            data=kpi
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting KPI {kpi_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@kpi_analytics_router.put("/landing-kpi-mssql/kpis/{kpi_id}", response_model=KPIResponse, tags=["KPI Analytics"])
async def update_kpi(kpi_id: int, request: KPIUpdateRequest):
    """Update a KPI definition in MS SQL Server."""
    try:
        service = get_kpi_analytics_service()
        kpi = service.update_kpi(kpi_id, request.dict(exclude_unset=True))
        
        if not kpi:
            raise HTTPException(status_code=404, detail=f"KPI with ID {kpi_id} not found")
        
        return KPIResponse(
            success=True,
            data=kpi
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating KPI {kpi_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@kpi_analytics_router.delete("/landing-kpi-mssql/kpis/{kpi_id}", response_model=dict, tags=["KPI Analytics"])
async def delete_kpi(kpi_id: int):
    """Delete (deactivate) a KPI in MS SQL Server."""
    try:
        service = get_kpi_analytics_service()
        success = service.delete_kpi(kpi_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"KPI with ID {kpi_id} not found")
        
        return {
            "success": True,
            "message": f"KPI {kpi_id} deleted successfully",
            "storage_type": "mssql"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting KPI {kpi_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# KPI Execution Routes
@kpi_analytics_router.post("/landing-kpi-mssql/kpis/{kpi_id}/execute", response_model=KPIExecutionResponse, tags=["KPI Analytics"])
async def execute_kpi(kpi_id: int, request: KPIExecuteRequest):
    """Execute a KPI and return results with enhanced SQL."""
    try:
        service = get_kpi_analytics_service()
        result = service.execute_kpi(kpi_id, request.dict())
        
        return KPIExecutionResponse(
            success=True,
            data=result,
            storage_type="mssql_jdbc"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing KPI {kpi_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health Check
@kpi_analytics_router.get("/landing-kpi-mssql/health", response_model=HealthResponse, tags=["KPI Analytics"])
async def health_check():
    """Health check endpoint for KPI Analytics service."""
    try:
        service = get_kpi_analytics_service()
        # Test database connection
        kpis = service.get_all_kpis(limit=1)
        
        return HealthResponse(
            success=True,
            status="healthy",
            database="mssql",
            service="kpi_analytics",
            timestamp=time.time()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            success=False,
            status="unhealthy",
            database="mssql",
            service="kpi_analytics",
            timestamp=time.time()
        )


# Dashboard Routes
@kpi_analytics_router.get("/landing-kpi-mssql/dashboard", response_model=dict, tags=["KPI Analytics"])
async def get_dashboard_data():
    """Get dashboard data with KPIs grouped by group name and their latest execution status."""
    try:
        service = get_kpi_analytics_service()
        dashboard_data = service.get_dashboard_data()

        return {
            "success": True,
            **dashboard_data,
            "storage_type": "mssql"
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@kpi_analytics_router.get("/landing-kpi-mssql/{kpi_id}/latest-results", response_model=dict, tags=["KPI Analytics"])
async def get_latest_results(kpi_id: int):
    """Get the latest execution results for a specific KPI."""
    try:
        service = get_kpi_analytics_service()
        results = service.get_latest_results(kpi_id)

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No execution results found for KPI {kpi_id}"
            )

        return {
            "success": True,
            "results": results,
            "storage_type": "mssql"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest results for KPI {kpi_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# SQL Preview Route
class SQLPreviewRequest(BaseModel):
    nl_definition: str
    kg_name: str = "default"
    select_schema: str = "newdqschemanov"
    use_llm: bool = True


@kpi_analytics_router.post("/landing-kpi-mssql/sql-preview", response_model=dict, tags=["KPI Analytics"])
async def preview_sql(request: SQLPreviewRequest):
    """Preview SQL generation for a natural language definition."""
    try:
        # Import here to avoid circular imports
        from kg_builder.services.nl_query_executor import NLQueryExecutor
        from kg_builder.services.nl_query_parser import NLQueryParser

        # Parse the natural language query
        parser = NLQueryParser()
        intent = parser.parse(request.nl_definition)

        # Load Knowledge Graph if specified
        kg = None
        if request.kg_name and request.kg_name != "default":
            try:
                from kg_builder.services.graphiti_backend import get_graphiti_backend
                from kg_builder.models import KnowledgeGraph, GraphNode, GraphRelationship

                graphiti = get_graphiti_backend()
                entities_data = graphiti.get_entities(request.kg_name)
                relationships_data = graphiti.get_relationships(request.kg_name)

                if entities_data and relationships_data:
                    nodes = [GraphNode(**entity) for entity in entities_data]
                    relationships = [GraphRelationship(**rel) for rel in relationships_data]

                    # Load table aliases
                    table_aliases = {}
                    try:
                        kg_metadata = graphiti.get_kg_metadata(request.kg_name)
                        if kg_metadata:
                            table_aliases = kg_metadata.get('table_aliases', {})
                    except Exception:
                        pass

                    kg = KnowledgeGraph(
                        name=request.kg_name,
                        nodes=nodes,
                        relationships=relationships,
                        schema_file=request.select_schema,
                        table_aliases=table_aliases
                    )
                    logger.info(f"Loaded KG '{request.kg_name}' with {len(nodes)} nodes")
            except Exception as e:
                logger.warning(f"Could not load KG '{request.kg_name}': {e}")

        # Generate SQL without executing
        executor = NLQueryExecutor(
            db_type="sqlserver",
            kg=kg,
            use_llm=request.use_llm
        )

        # Generate SQL (this will include material master enhancement)
        sql = executor.generator.generate(intent)

        # Apply material master enhancement
        from kg_builder.services.material_master_enhancer import material_master_enhancer
        enhancement_result = material_master_enhancer.enhance_sql_with_material_master(sql)

        return {
            "success": True,
            "generated_sql": enhancement_result['original_sql'],
            "enhanced_sql": enhancement_result['enhanced_sql'],
            "enhancement_applied": enhancement_result['enhancement_applied'],
            "material_master_added": enhancement_result.get('material_master_added', False),
            "ops_planner_added": enhancement_result.get('ops_planner_added', False),
            "storage_type": "mssql"
        }
    except Exception as e:
        logger.error(f"Error in SQL preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))
