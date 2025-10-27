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
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata including field_preferences used during generation"
    )


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
        description="Use LLM for relationship inference, descriptions, and confidence scoring"
    )

    # V1: Field preferences (legacy - ambiguous table hints)
    field_preferences: Optional[List['FieldPreference']] = Field(
        default=None,
        description="User-specific field hints to guide LLM relationship inference (v1 - deprecated)"
    )

    # V2: Explicit relationship pairs (recommended)
    relationship_pairs: Optional[List[dict]] = Field(
        default=None,
        description="Explicit source→target relationship pairs to add to KG (v2 - recommended)"
    )

    # Field exclusion configuration
    excluded_fields: Optional[List[str]] = Field(
        default=None,
        description="List of field names to exclude from automatic KG relationship creation (case-sensitive)"
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
    nodes: List[GraphNode] = Field(default=[], description="All nodes in the knowledge graph")
    relationships: List[GraphRelationship] = Field(default=[], description="All relationships in the knowledge graph")
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
    filter_conditions: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Filter conditions to apply (e.g., {'Active_Inactive': 'Active'})"
    )
    confidence_score: float  # 0.0-1.0
    reasoning: str  # LLM explanation
    validation_status: str  # VALID, LIKELY, UNCERTAIN
    llm_generated: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}

    # ===== NEW: Multi-table join support =====
    # For backward compatibility, these are optional
    join_tables: Optional[List[str]] = Field(
        default=None,
        description="List of tables to join (for multi-table joins). If None, uses source_table and target_table."
    )
    join_conditions: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Join conditions between tables. Format: [{'table1': 'name', 'table2': 'name', 'on': 'condition'}, ...]"
    )
    join_order: Optional[List[str]] = Field(
        default=None,
        description="Order in which to join tables. If None, uses join_tables order."
    )
    join_type: Optional[List[str]] = Field(
        default=None,
        description="Join type for each join (INNER, LEFT, RIGHT, FULL). Length should be len(join_tables)-1"
    )
    select_columns: Optional[Dict[str, List[str]]] = Field(
        default=None,
        description="Columns to select from each table. Format: {'table_name': ['col1', 'col2'], ...}. If None, selects all columns."
    )

    def is_multi_table(self) -> bool:
        """Check if this is a multi-table rule."""
        return self.join_tables is not None and len(self.join_tables) > 2

    def get_join_tables(self) -> List[str]:
        """Get list of tables to join."""
        if self.join_tables:
            return self.join_tables
        return [self.source_table, self.target_table]

    def get_join_order(self) -> List[str]:
        """Get join order."""
        if self.join_order:
            return self.join_order
        return self.get_join_tables()

    def get_join_types(self) -> List[str]:
        """Get join types for each join."""
        if self.join_type:
            return self.join_type
        # Default: INNER for all joins
        return ["INNER"] * (len(self.get_join_tables()) - 1)


class ReconciliationRuleSet(BaseModel):
    """Collection of reconciliation rules."""
    ruleset_id: str
    ruleset_name: str
    schemas: List[str]
    rules: List[ReconciliationRule]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    generated_from_kg: str  # KG name


class KGRelationshipType(str, Enum):
    """Types of relationships in Knowledge Graph."""
    MATCHES = "MATCHES"                      # Fields match/equal (e.g., product_id = item_id)
    REFERENCES = "REFERENCES"                # Foreign key reference
    FOREIGN_KEY = "FOREIGN_KEY"              # Explicit foreign key constraint
    CROSS_SCHEMA_REFERENCE = "CROSS_SCHEMA_REFERENCE"  # Reference across schemas
    SEMANTIC_REFERENCE = "SEMANTIC_REFERENCE"  # LLM-inferred semantic relationship
    CONTAINS = "CONTAINS"                    # One-to-many (e.g., Order contains OrderItems)
    BELONGS_TO = "BELONGS_TO"                # Many-to-one (reverse of CONTAINS)
    RELATED_TO = "RELATED_TO"                # Generic relationship


class RelationshipPair(BaseModel):
    """
    Explicit relationship pair for KG creation (v2 - Recommended for KG building).

    This model defines explicit directional relationships between tables/columns
    that will be stored in the Knowledge Graph. Simpler than ReconciliationPair
    since it's for KG creation, not rule execution.
    """
    source_table: str = Field(..., description="Source table name")
    source_column: str = Field(..., description="Source column name")
    target_table: str = Field(..., description="Target table name")
    target_column: str = Field(..., description="Target column name")
    relationship_type: KGRelationshipType = Field(
        default=KGRelationshipType.MATCHES,
        description="Type of relationship (MATCHES, REFERENCES, CONTAINS, etc.)"
    )
    confidence: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
        description="Confidence score for this relationship (0.0-1.0)"
    )
    bidirectional: bool = Field(
        default=False,
        description="If true, also create reverse relationship"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata (e.g., {'source': 'user_defined', 'notes': '...'})"
    )


class ReconciliationPair(BaseModel):
    """Explicit source-to-target reconciliation pair (v2 - Recommended)."""
    source_table: str = Field(..., description="Source table name")
    source_columns: List[str] = Field(..., description="Source columns to match")
    target_table: str = Field(..., description="Target table name")
    target_columns: List[str] = Field(..., description="Target columns to match")
    match_type: ReconciliationMatchType = Field(
        default=ReconciliationMatchType.EXACT,
        description="Type of match (EXACT, FUZZY, SEMANTIC)"
    )
    source_filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Filter conditions for source table (e.g., {'status': 'active'})"
    )
    target_filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Filter conditions for target table (e.g., {'Active_Inactive': 'Active'})"
    )
    transformation: Optional[str] = Field(
        default=None,
        description="SQL transformation to apply (e.g., 'UPPER(source_column)')"
    )
    bidirectional: bool = Field(
        default=False,
        description="If true, also create reverse rule (target -> source)"
    )
    priority: str = Field(
        default="normal",
        description="Priority level: high, normal, low"
    )
    confidence_override: Optional[float] = Field(
        default=None,
        description="Override auto-calculated confidence score"
    )


class TableHint(BaseModel):
    """Table-level hints for discovery (v2 - Optional supplement to reconciliation_pairs)."""
    table_name: str = Field(..., description="Table name")
    priority_fields: List[str] = Field(
        default=[],
        description="Fields to prioritize for matching"
    )
    exclude_fields: List[str] = Field(
        default=[],
        description="Fields to exclude from auto-discovery"
    )


class FieldPreference(BaseModel):
    """User preference for specific fields in rule generation (v1 - Legacy)."""
    table_name: str = Field(..., description="Table name")
    priority_fields: List[str] = Field(
        default=[],
        description="Fields to prioritize for matching (high priority)"
    )
    exclude_fields: List[str] = Field(
        default=[],
        description="Fields to exclude from rule generation"
    )
    field_hints: Dict[str, str] = Field(
        default={},
        description="Hints about field relationships (e.g., {'vendor_id': 'supplier_id'})"
    )
    filter_hints: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Filter conditions for this table (e.g., {'Active_Inactive': 'Active', 'deleted': False})"
    )


class RuleGenerationRequest(BaseModel):
    """Request model for generating reconciliation rules (supports v1 and v2)."""
    schema_names: List[str] = Field(..., description="List of schema names to reconcile")
    kg_name: str = Field(..., description="Knowledge graph to use for rule generation")
    use_llm_enhancement: bool = Field(default=True, description="Use LLM for semantic rule generation")
    min_confidence: float = Field(default=0.7, description="Minimum confidence score for rules")
    match_types: List[ReconciliationMatchType] = Field(
        default=[ReconciliationMatchType.EXACT, ReconciliationMatchType.SEMANTIC],
        description="Types of matches to generate"
    )

    # V2: Explicit reconciliation pairs (recommended)
    reconciliation_pairs: Optional[List[ReconciliationPair]] = Field(
        default=None,
        description="Explicit source-target pairs (v2 recommended approach). Takes precedence over field_preferences."
    )

    # V2: Table-level hints for auto-discovery
    table_hints: Optional[List[TableHint]] = Field(
        default=None,
        description="Table-level hints for auto-discovery (v2). Used alongside reconciliation_pairs."
    )

    # V2: Auto-discovery control
    auto_discover_additional: bool = Field(
        default=True,
        description="Allow KG to discover additional relationships beyond reconciliation_pairs"
    )

    # V1: Legacy field preferences (maintained for backward compatibility)
    field_preferences: Optional[List[FieldPreference]] = Field(
        default=None,
        description="User-specific field preferences (v1 legacy). Use reconciliation_pairs instead."
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
    schema: Optional[str] = Field(default=None, description="Database schema (for PostgreSQL/MySQL landing DB)")

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
    inactive_count: int = Field(
        default=0,
        description="Number of inactive records (is_active = 0 or NULL) in source data"
    )
    generated_sql: List[Dict[str, Any]] = Field(
        default=[],
        description="Array of SQL queries executed during reconciliation with structure: [{rule_id, source_sql, target_sql, description}, ...]"
    )
    result_file_path: Optional[str] = Field(
        default=None,
        description="Path to the saved JSON file containing full execution results (e.g., results/reconciliation_result_RECON_ABC123_20251025_120530.json)"
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


# KPI Models
class KPIMetrics(BaseModel):
    """Base model for KPI metrics."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ruleset_id: str
    ruleset_name: str
    execution_id: str


class ReconciliationCoverageRateKPI(KPIMetrics):
    """Reconciliation Coverage Rate KPI."""
    matched_records: int
    unmatched_source: int
    total_source_records: int
    coverage_rate: float = Field(..., ge=0, le=100, description="Coverage percentage 0-100")
    status: str = Field(..., description="HEALTHY, WARNING, or CRITICAL")
    source_kg: str
    source_schemas: List[str]


class DataQualityConfidenceScoreKPI(KPIMetrics):
    """Data Quality Confidence Score KPI."""
    overall_confidence_score: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    total_matched_records: int
    high_confidence_matches: int
    medium_confidence_matches: int
    low_confidence_matches: int
    status: str = Field(..., description="GOOD, ACCEPTABLE, or POOR")
    source_kg: str


class ReconciliationEfficiencyIndexKPI(KPIMetrics):
    """Reconciliation Efficiency Index KPI."""
    efficiency_index: float = Field(..., ge=0, description="Efficiency score")
    match_success_rate: float = Field(..., ge=0, le=100)
    rule_utilization: float = Field(..., ge=0, le=100)
    speed_factor: float = Field(..., ge=0, le=100)
    total_records_processed: int
    execution_time_ms: float
    records_per_second: float
    status: str = Field(..., description="EXCELLENT, GOOD, ACCEPTABLE, WARNING, or CRITICAL")
    source_kg: str


class KPICalculationRequest(BaseModel):
    """Request to calculate KPIs for an execution."""
    execution_id: str
    ruleset_id: str
    ruleset_name: str
    source_kg: str
    source_schemas: List[str]
    matched_count: int
    total_source_count: int
    matched_records: List[Dict[str, Any]] = []
    active_rules: int
    total_rules: int
    execution_time_ms: float
    resource_metrics: Optional[Dict[str, Any]] = None


class KPICalculationResponse(BaseModel):
    """Response from KPI calculation."""
    success: bool
    rcr_id: Optional[str] = None
    dqcs_id: Optional[str] = None
    rei_id: Optional[str] = None
    rcr_value: Optional[float] = None
    dqcs_value: Optional[float] = None
    rei_value: Optional[float] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Landing Database Models
class LandingExecutionRequest(BaseModel):
    """Request model for executing reconciliation with landing database."""
    ruleset_id: str = Field(..., description="Ruleset ID to execute")
    source_db_config: DatabaseConnectionInfo = Field(..., description="Source database connection")
    target_db_config: DatabaseConnectionInfo = Field(..., description="Target database connection")
    landing_db_config: Optional[DatabaseConnectionInfo] = Field(
        default=None,
        description="Landing database connection (uses config if not provided)"
    )
    limit: int = Field(default=None, description="Limit rows per staging table (None for all)")
    include_matched: bool = Field(default=True, description="Include matched records")
    include_unmatched: bool = Field(default=True, description="Include unmatched records")
    store_in_mongodb: bool = Field(default=True, description="Store results in MongoDB")
    keep_staging: bool = Field(default=True, description="Keep staging tables for audit (24h TTL)")


class StagingTableInfo(BaseModel):
    """Information about a staging table."""
    table_name: str
    row_count: int
    created_at: datetime
    size_mb: Optional[float] = None
    indexes: List[str] = []


class LandingExecutionResponse(BaseModel):
    """Response from landing-based reconciliation execution."""
    success: bool
    execution_id: str
    matched_count: int
    unmatched_source_count: int
    unmatched_target_count: int
    total_source_count: int
    total_target_count: int

    # KPIs calculated directly in landing DB
    rcr: float = Field(..., description="Reconciliation Coverage Rate (%)")
    rcr_status: str = Field(..., description="HEALTHY, WARNING, or CRITICAL")
    dqcs: float = Field(..., description="Data Quality Confidence Score")
    dqcs_status: str = Field(..., description="GOOD, ACCEPTABLE, or POOR")
    rei: float = Field(..., description="Reconciliation Efficiency Index")

    # Staging table information
    source_staging: StagingTableInfo
    target_staging: StagingTableInfo

    # Execution metrics
    extraction_time_ms: float
    reconciliation_time_ms: float
    total_time_ms: float

    # Storage
    mongodb_document_id: Optional[str] = None
    staging_retained: bool = True
    staging_ttl_hours: int = 24

    error: Optional[str] = None


class StagingTableMetadata(BaseModel):
    """Metadata for tracking staging tables."""
    table_name: str
    execution_id: str
    ruleset_id: str
    source_or_target: str  # 'source' or 'target'
    source_db_type: str
    source_db_host: str
    row_count: int
    created_at: datetime
    expires_at: datetime
    size_bytes: Optional[int] = None
    status: str = Field(default="active", description="active, expired, deleted")


# KPI Models
class KPIType(str, Enum):
    """Types of KPIs that can be created."""
    MATCH_RATE = "match_rate"                          # Percentage of matched records
    UNMATCHED_SOURCE_COUNT = "unmatched_source_count"  # Count of unmatched source records
    UNMATCHED_TARGET_COUNT = "unmatched_target_count"  # Count of unmatched target records
    INACTIVE_RECORD_COUNT = "inactive_record_count"    # Count of inactive records
    MATCH_PERCENTAGE = "match_percentage"              # Match percentage (0-100)
    DATA_QUALITY_SCORE = "data_quality_score"          # Overall data quality score


class KPIThresholds(BaseModel):
    """Threshold configuration for KPI alerts."""
    warning_threshold: float = Field(..., description="Warning threshold value")
    critical_threshold: float = Field(..., description="Critical threshold value")
    comparison_operator: str = Field(
        default="less_than",
        description="Comparison operator: less_than, greater_than, equal_to"
    )


class KPICreateRequest(BaseModel):
    """Request to create a new KPI."""
    kpi_name: str = Field(..., description="Name of the KPI")
    kpi_description: Optional[str] = Field(default=None, description="Description of the KPI")
    kpi_type: KPIType = Field(..., description="Type of KPI")
    ruleset_id: str = Field(..., description="Associated ruleset ID")
    thresholds: KPIThresholds = Field(..., description="Warning and critical thresholds")
    enabled: bool = Field(default=True, description="Whether KPI is enabled")


class KPIConfiguration(BaseModel):
    """Stored KPI configuration."""
    kpi_id: str = Field(..., description="Unique KPI identifier")
    kpi_name: str
    kpi_description: Optional[str] = None
    kpi_type: KPIType
    ruleset_id: str
    thresholds: KPIThresholds
    enabled: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class KPIEvidenceRecord(BaseModel):
    """Evidence record for KPI drill-down."""
    record_id: Optional[str] = Field(default=None, description="Primary key of the record")
    record_data: Dict[str, Any] = Field(..., description="Full record data from master table")
    match_status: str = Field(..., description="matched, unmatched_source, unmatched_target, inactive")
    rule_name: Optional[str] = Field(default=None, description="Rule that matched/failed")


class KPIResult(BaseModel):
    """Result of KPI calculation."""
    kpi_id: str
    kpi_name: str
    kpi_type: KPIType
    ruleset_id: str
    calculated_value: float = Field(..., description="The calculated KPI value")
    thresholds: KPIThresholds
    status: str = Field(..., description="pass, warning, or critical")
    execution_timestamp: datetime = Field(default_factory=datetime.utcnow)
    evidence_count: int = Field(default=0, description="Number of evidence records")
    evidence_file_path: Optional[str] = Field(default=None, description="Path to evidence data file")
    calculation_details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Details of how KPI was calculated"
    )


class KPIResultResponse(BaseModel):
    """Response containing KPI result."""
    success: bool
    kpi_result: Optional[KPIResult] = None
    result_file_path: Optional[str] = Field(default=None, description="Path to saved KPI result file")
    error: Optional[str] = None


class KPIEvidenceDrillDownRequest(BaseModel):
    """Request to retrieve evidence data for a KPI."""
    kpi_id: str
    match_status: Optional[str] = Field(
        default=None,
        description="Filter by match_status: matched, unmatched_source, unmatched_target, inactive"
    )
    limit: int = Field(default=1000, description="Maximum number of records to return")
    offset: int = Field(default=0, description="Offset for pagination")


class KPIEvidenceDrillDownResponse(BaseModel):
    """Response containing evidence data for drill-down."""
    success: bool
    kpi_id: str
    kpi_name: str
    total_evidence_count: int
    returned_count: int
    evidence_records: List[KPIEvidenceRecord] = []
    error: Optional[str] = None


# File-based KPI Management Models
class KPIDefinitionRequest(BaseModel):
    """Request to create a new KPI definition."""
    kpi_name: str = Field(..., description="Name of the KPI")
    kpi_description: Optional[str] = Field(default=None, description="Description of the KPI")
    kpi_type: str = Field(..., description="Type of KPI (match_rate, unmatched_source_count, etc.)")
    ruleset_id: str = Field(..., description="Associated ruleset ID")
    thresholds: Dict[str, Any] = Field(..., description="Warning and critical thresholds")
    enabled: bool = Field(default=True, description="Whether KPI is enabled")


class KPIUpdateRequest(BaseModel):
    """Request to update a KPI definition."""
    kpi_name: Optional[str] = Field(default=None, description="Updated KPI name")
    kpi_description: Optional[str] = Field(default=None, description="Updated description")
    thresholds: Optional[Dict[str, Any]] = Field(default=None, description="Updated thresholds")
    enabled: Optional[bool] = Field(default=None, description="Updated enabled status")


class KPIExecutionRequest(BaseModel):
    """Request to execute a KPI."""
    ruleset_id: Optional[str] = Field(default=None, description="Override ruleset ID if needed")


class BatchExecutionRequest(BaseModel):
    """Request to execute multiple KPIs."""
    kpi_ids: List[str] = Field(..., description="List of KPI IDs to execute")
    ruleset_id: Optional[str] = Field(default=None, description="Override ruleset ID if needed")


class EvidenceRequest(BaseModel):
    """Request to retrieve evidence data."""
    match_status: Optional[str] = Field(default=None, description="Filter by match status")
    limit: int = Field(default=100, description="Maximum number of records to return")
    offset: int = Field(default=0, description="Offset for pagination")


class KPIListResponse(BaseModel):
    """Response containing list of KPIs."""
    success: bool
    kpis: List[Dict[str, Any]] = Field(default=[], description="List of KPI definitions")
    total_count: int = Field(default=0, description="Total number of KPIs")
    error: Optional[str] = None


class KPIExecutionResponse(BaseModel):
    """Response from KPI execution."""
    success: bool
    result: Optional[Dict[str, Any]] = Field(default=None, description="KPI execution result")
    result_id: Optional[str] = Field(default=None, description="Result ID")
    error: Optional[str] = None


class KPIResultsListResponse(BaseModel):
    """Response containing list of KPI results."""
    success: bool
    results: List[Dict[str, Any]] = Field(default=[], description="List of KPI results")
    total_count: int = Field(default=0, description="Total number of results")
    error: Optional[str] = None


# NL Query Execution Models
class NLQueryExecutionRequest(BaseModel):
    """Request to execute NL definitions as data queries."""
    kg_name: str = Field(..., description="Knowledge graph name")
    schemas: List[str] = Field(..., description="List of schema names")
    definitions: List[str] = Field(..., description="List of NL definitions to execute")
    use_llm: bool = Field(default=True, description="Use LLM for parsing")
    min_confidence: float = Field(default=0.7, description="Minimum confidence threshold")
    limit: int = Field(default=1000, description="Maximum records per query")
    db_type: str = Field(default="mysql", description="Database type")
    excluded_fields: Optional[List[str]] = Field(
        default=None,
        description="List of field names to exclude from query generation (prevents using these columns as join keys)"
    )


class NLQueryResultItem(BaseModel):
    """Result from executing a single NL query."""
    definition: str = Field(..., description="Original definition")
    query_type: str = Field(..., description="Type of query")
    operation: Optional[str] = Field(None, description="Operation type")
    sql: str = Field(..., description="Generated SQL")
    record_count: int = Field(..., description="Number of records returned")
    records: List[Dict[str, Any]] = Field(default=[], description="Query results")
    join_columns: Optional[List[List[str]]] = Field(None, description="Join columns used")
    confidence: float = Field(..., description="Confidence score")
    execution_time_ms: float = Field(..., description="Execution time in milliseconds")
    error: Optional[str] = Field(None, description="Error message if any")
    source_table: Optional[str] = Field(None, description="Resolved source table name")
    target_table: Optional[str] = Field(None, description="Resolved target table name")


class NLQueryExecutionResponse(BaseModel):
    """Response from NL query execution."""
    success: bool = Field(..., description="Whether execution was successful")
    kg_name: str = Field(..., description="Knowledge graph name")
    total_definitions: int = Field(..., description="Total definitions processed")
    successful: int = Field(..., description="Number of successful queries")
    failed: int = Field(..., description="Number of failed queries")
    results: List[NLQueryResultItem] = Field(default=[], description="Query results")
    statistics: Optional[Dict[str, Any]] = Field(None, description="Execution statistics")
    error: Optional[str] = Field(None, description="Overall error message")
    table_mapping: Optional[Dict[str, List[str]]] = Field(None, description="Available table aliases and mappings")

