"""
Pydantic models for request/response validation.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# LLM-related models
class LLMEntity(BaseModel):
    """Represents an entity extracted by LLM."""
    name: str
    purpose: str
    type: str
    key_attributes: List[str] = []
    description: str


class LLMRelationship(BaseModel):
    """Represents a relationship extracted by LLM."""
    source: str
    target: str
    type: str
    cardinality: str
    description: str
    foreign_key: Optional[str] = None


class LLMExtractionResponse(BaseModel):
    """Response from LLM extraction."""
    success: bool
    entities: List[LLMEntity] = []
    relationships: List[LLMRelationship] = []
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class LLMAnalysisResponse(BaseModel):
    """Response from LLM schema analysis."""
    success: bool
    domain: Optional[str] = None
    purpose: Optional[str] = None
    patterns: List[str] = []
    key_entities: List[str] = []
    data_flow: Optional[str] = None
    business_logic: Optional[str] = None
    quality_notes: Optional[str] = None
    error: Optional[str] = None


# Schema-related models
class ColumnSchema(BaseModel):
    """Represents a database column."""
    name: str
    type: str
    nullable: bool
    default: Optional[Any] = None
    primary_key: bool = False


class TableSchema(BaseModel):
    """Represents a database table."""
    table_name: str
    columns: List[ColumnSchema]
    primary_keys: List[str] = []
    foreign_keys: List[Dict[str, Any]] = []
    indexes: List[Dict[str, Any]] = []


class DatabaseSchema(BaseModel):
    """Represents a complete database schema."""
    database: str
    tables: Dict[str, TableSchema]
    total_tables: int
    metadata: Optional[Dict[str, Any]] = None


# Knowledge Graph models
class GraphNode(BaseModel):
    """Represents a node in the knowledge graph."""
    id: str
    label: str
    properties: Dict[str, Any] = {}
    source_table: Optional[str] = None
    source_column: Optional[str] = None


class GraphRelationship(BaseModel):
    """Represents a relationship between nodes."""
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any] = {}
    source_column: Optional[str] = None
    target_column: Optional[str] = None


class KnowledgeGraph(BaseModel):
    """Represents a complete knowledge graph."""
    name: str
    nodes: List[GraphNode]
    relationships: List[GraphRelationship]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    schema_file: str


# API Request/Response models
class SchemaUploadRequest(BaseModel):
    """Request model for schema upload."""
    schema_name: str = Field(..., description="Name of the schema")
    description: Optional[str] = Field(None, description="Schema description")


class SchemaUploadResponse(BaseModel):
    """Response model for schema upload."""
    success: bool
    message: str
    schema_name: str
    tables_count: int
    total_columns: int


class KGGenerationRequest(BaseModel):
    """Request model for KG generation."""
    schema_name: str = Field(..., description="Name of the schema to process")
    kg_name: str = Field(..., description="Name for the generated knowledge graph")
    backends: List[str] = Field(
        default=["falkordb", "graphiti"],
        description="Backends to use: 'falkordb', 'graphiti', or both"
    )


class KGGenerationResponse(BaseModel):
    """Response model for KG generation."""
    success: bool
    message: str
    kg_name: str
    nodes_count: int
    relationships_count: int
    backends_used: List[str]
    generation_time_ms: float


class QueryRequest(BaseModel):
    """Request model for graph queries."""
    kg_name: str = Field(..., description="Name of the knowledge graph")
    query: str = Field(..., description="Query string or Cypher query")
    backend: str = Field(default="falkordb", description="Backend to query")


class QueryResponse(BaseModel):
    """Response model for graph queries."""
    success: bool
    message: str
    results: List[Dict[str, Any]] = []
    query_time_ms: float


class EntityResponse(BaseModel):
    """Response model for entity retrieval."""
    entity_id: str
    entity_label: str
    properties: Dict[str, Any]
    relationships: List[Dict[str, Any]] = []


class GraphExportResponse(BaseModel):
    """Response model for graph export."""
    success: bool
    message: str
    format: str
    data: Dict[str, Any]


class HealthCheckResponse(BaseModel):
    """Response model for health check."""
    status: str
    falkordb_connected: bool
    graphiti_available: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)

