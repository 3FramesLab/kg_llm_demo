"""
Pydantic models for request/response validation.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum


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
    schema_name: Optional[str] = Field(None, description="Name of a single schema to process (deprecated, use schema_names)")
    schema_names: Optional[List[str]] = Field(None, description="List of schema names to process and merge into single KG")
    kg_name: str = Field(..., description="Name for the generated knowledge graph")
    backends: List[str] = Field(
        default=["falkordb", "graphiti"],
        description="Backends to use: 'falkordb', 'graphiti', or both"
    )
    use_llm_enhancement: bool = Field(
        default=True,
        description="Use LLM for relationship inference, descriptions, and confidence scoring (only for multi-schema)"
    )

    @field_validator('schema_names', mode='before')
    @classmethod
    def validate_schemas(cls, v, info):
        """Ensure at least one schema is provided."""
        schema_name = info.data.get('schema_name')

        # If schema_names not provided, use schema_name for backward compatibility
        if v is None and schema_name:
            return [schema_name]

        if v is None and schema_name is None:
            raise ValueError("Either 'schema_name' or 'schema_names' must be provided")

        return v


class KGGenerationResponse(BaseModel):
    """Response model for KG generation."""
    success: bool
    schemas_processed: List[str] = Field(default=[], description="List of schemas that were processed")
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


# Reconciliation Rule models
class ReconciliationMatchType(str, Enum):
    """Types of reconciliation matches."""
    EXACT = "exact"              # Exact column match
    FUZZY = "fuzzy"              # Fuzzy string matching
    COMPOSITE = "composite"      # Multiple columns
    TRANSFORMATION = "transformation"  # Apply transform function
    SEMANTIC = "semantic"        # LLM-inferred semantic match


class ReconciliationRule(BaseModel):
    """Represents a reconciliation rule between schemas."""
    rule_id: str
    rule_name: str
    source_schema: str
    source_table: str
    source_columns: List[str]
    target_schema: str
    target_table: str
    target_columns: List[str]
    match_type: ReconciliationMatchType
    transformation: Optional[str] = None  # SQL/Python transform
    confidence_score: float  # 0.0-1.0
    reasoning: str  # LLM explanation
    validation_status: str  # VALID, LIKELY, UNCERTAIN
    llm_generated: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}


class ReconciliationRuleSet(BaseModel):
    """Collection of reconciliation rules."""
    ruleset_id: str
    ruleset_name: str
    schemas: List[str]
    rules: List[ReconciliationRule]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    generated_from_kg: str  # KG name


class RuleGenerationRequest(BaseModel):
    """Request model for generating reconciliation rules."""
    schema_names: List[str] = Field(..., description="List of schema names to reconcile")
    kg_name: str = Field(..., description="Knowledge graph to use for rule generation")
    use_llm_enhancement: bool = Field(default=True, description="Use LLM for semantic rule generation")
    min_confidence: float = Field(default=0.7, description="Minimum confidence score for rules")
    match_types: List[ReconciliationMatchType] = Field(
        default=[ReconciliationMatchType.EXACT, ReconciliationMatchType.SEMANTIC],
        description="Types of matches to generate"
    )


class RuleGenerationResponse(BaseModel):
    """Response model for rule generation."""
    success: bool
    ruleset_id: str
    rules_count: int
    rules: List[ReconciliationRule]
    generation_time_ms: float
    message: Optional[str] = None


class ValidationResult(BaseModel):
    """Result of validating a reconciliation rule."""
    rule_id: str
    valid: bool
    exists: bool  # Do tables/columns exist?
    types_compatible: bool  # Are data types compatible?
    sample_match_rate: Optional[float] = None  # Match rate on sample data
    cardinality: Optional[str] = None  # 1:1, 1:N, N:M
    estimated_performance_ms: Optional[float] = None
    issues: List[str] = []
    warnings: List[str] = []


class RuleValidationRequest(BaseModel):
    """Request model for validating a reconciliation rule."""
    rule: ReconciliationRule
    sample_size: int = Field(default=100, description="Number of records to test")
    source_db_config: Optional['DatabaseConnectionInfo'] = Field(default=None, description="Source database connection info")
    target_db_config: Optional['DatabaseConnectionInfo'] = Field(default=None, description="Target database connection info")


class DatabaseConnectionInfo(BaseModel):
    """Database connection information for JDBC connections."""
    db_type: str = Field(..., description="Database type: oracle, sqlserver, postgresql, mysql")
    host: str = Field(..., description="Database host")
    port: int = Field(..., description="Database port")
    database: str = Field(..., description="Database name")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    service_name: Optional[str] = Field(default=None, description="Oracle service name (if applicable)")

    class Config:
        json_schema_extra = {
            "example": {
                "db_type": "oracle",
                "host": "localhost",
                "port": 1521,
                "database": "ORCL",
                "username": "admin",
                "password": "password",
                "service_name": "ORCLPDB"
            }
        }


class RuleExecutionRequest(BaseModel):
    """Request model for executing reconciliation rules."""
    ruleset_id: str
    limit: int = Field(default=100, description="Maximum number of records to process")
    source_db_config: Optional['DatabaseConnectionInfo'] = Field(
        default=None,
        description="Source database connection (optional - for direct execution)"
    )
    target_db_config: Optional['DatabaseConnectionInfo'] = Field(
        default=None,
        description="Target database connection (optional - for direct execution)"
    )
    include_matched: bool = Field(default=True, description="Include matched records in results")
    include_unmatched: bool = Field(default=True, description="Include unmatched records in results")
    store_in_mongodb: bool = Field(
        default=True,
        description="Store results in MongoDB as JSON documents (only applies to direct execution mode)"
    )


class MatchedRecord(BaseModel):
    """Represents a matched record pair."""
    source_record: Dict[str, Any]
    target_record: Dict[str, Any]
    match_confidence: float
    rule_used: str
    rule_name: str


class RuleExecutionResponse(BaseModel):
    """Response model for rule execution."""
    success: bool
    matched_count: int
    unmatched_source_count: int
    unmatched_target_count: int
    matched_records: List[MatchedRecord]
    unmatched_source: List[Dict[str, Any]] = []
    unmatched_target: List[Dict[str, Any]] = []
    execution_time_ms: float
    mongodb_document_id: Optional[str] = Field(
        default=None,
        description="MongoDB document ID if results were stored in MongoDB"
    )
    storage_location: Optional[str] = Field(
        default=None,
        description="Location where results were stored (e.g., 'mongodb', 'memory')"
    )


# Natural Language Relationship models
class NLInputFormat(str, Enum):
    """Supported input formats for natural language relationships."""
    NATURAL_LANGUAGE = "natural_language"      # "Products are supplied by Vendors"
    SEMI_STRUCTURED = "semi_structured"        # "catalog.product_id → vendor.vendor_id (SUPPLIED_BY)"
    PSEUDO_SQL = "pseudo_sql"                  # "SELECT * FROM products JOIN vendors ON ..."
    BUSINESS_RULES = "business_rules"          # "IF product.status='active' THEN ..."


class RelationshipDefinition(BaseModel):
    """Parsed natural language relationship definition."""
    source_table: str = Field(..., description="Source table name")
    target_table: str = Field(..., description="Target table name")
    relationship_type: str = Field(..., description="Type of relationship (e.g., SUPPLIED_BY, CONTAINS)")
    properties: List[str] = Field(default=[], description="Properties/columns for the relationship")
    cardinality: str = Field(default="1:N", description="Cardinality (1:1, 1:N, N:M)")
    confidence: float = Field(default=0.75, description="Confidence score (0.0-1.0)")
    reasoning: str = Field(..., description="Explanation of why this relationship was inferred")
    input_format: NLInputFormat = Field(..., description="Format of the input")
    validation_status: str = Field(default="PENDING", description="VALID, INVALID, PENDING")
    validation_errors: List[str] = Field(default=[], description="Validation errors if any")


class NLRelationshipRequest(BaseModel):
    """Request to add natural language relationships to knowledge graph."""
    kg_name: str = Field(..., description="Name of the knowledge graph")
    definitions: List[str] = Field(..., description="List of natural language relationship definitions")
    schemas: List[str] = Field(..., description="List of schema names involved")
    use_llm: bool = Field(default=True, description="Use LLM for parsing (vs rule-based)")
    min_confidence: float = Field(default=0.7, description="Minimum confidence threshold")


class NLRelationshipResponse(BaseModel):
    """Response from natural language relationship parsing."""
    success: bool = Field(..., description="Whether all definitions were parsed successfully")
    relationships: List[RelationshipDefinition] = Field(default=[], description="Parsed relationships")
    parsed_count: int = Field(..., description="Number of successfully parsed definitions")
    failed_count: int = Field(..., description="Number of failed definitions")
    errors: List[str] = Field(default=[], description="Error messages for failed definitions")
    processing_time_ms: float = Field(..., description="Time taken to process all definitions")

