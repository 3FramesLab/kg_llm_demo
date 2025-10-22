# Natural Language Relationships - Technical Design Document

## 1. SYSTEM ARCHITECTURE

### 1.1 High-Level Flow

```
User Input (Natural Language)
    ↓
[NL Relationship Parser Service]
    ├─ Entity Recognition
    ├─ Relationship Type Inference
    ├─ Property Extraction
    └─ Validation & Scoring
    ↓
[Structured Relationship]
    ├─ source_id
    ├─ target_id
    ├─ relationship_type
    ├─ properties
    ├─ confidence_score
    └─ validation_status
    ↓
[Knowledge Graph Backend]
    ├─ FalkorDB
    └─ Graphiti
```

### 1.2 Component Interaction

```
FastAPI Routes
    ↓
NLRelationshipService (NEW)
    ├─ LLMParser (uses MultiSchemaLLMService)
    ├─ EntityMatcher (uses SchemaParser)
    ├─ RelationshipValidator (uses existing validation)
    └─ ConfidenceScorer (uses LLM)
    ↓
MultiSchemaLLMService (ENHANCED)
    ├─ parse_relationship_from_text()
    ├─ extract_entities()
    ├─ infer_relationship_type()
    └─ score_confidence()
    ↓
SchemaParser (ENHANCED)
    ├─ match_entities_to_schema()
    └─ validate_relationship()
```

---

## 2. NEW SERVICE: NLRelationshipService

### 2.1 Core Methods

```python
class NLRelationshipService:
    """Service for parsing natural language relationship definitions."""
    
    def parse_single_relationship(
        self,
        nl_description: str,
        kg_name: str,
        available_entities: List[str]
    ) -> ParsedRelationship:
        """Parse single NL relationship description."""
        # 1. Extract entities
        # 2. Infer relationship type
        # 3. Extract properties
        # 4. Validate
        # 5. Score confidence
        
    def parse_batch_relationships(
        self,
        nl_descriptions: List[str],
        kg_name: str
    ) -> List[ParsedRelationship]:
        """Parse multiple NL descriptions efficiently."""
        
    def interactive_parse(
        self,
        nl_description: str,
        kg_name: str,
        clarification_history: List[Dict]
    ) -> InteractiveParseResult:
        """Multi-turn parsing with clarifications."""
        
    def validate_relationship(
        self,
        parsed_rel: ParsedRelationship,
        schema: DatabaseSchema
    ) -> ValidationResult:
        """Validate parsed relationship against schema."""
```

### 2.2 Data Models

```python
class ParsedRelationship(BaseModel):
    """Result of NL parsing."""
    source_entity: str
    target_entity: str
    relationship_type: str
    properties: Dict[str, str]
    cardinality: Optional[str]  # 1:1, 1:N, N:N
    confidence_score: float
    validation_status: str  # VALID, LIKELY, UNCERTAIN, INVALID
    reasoning: str  # Why this interpretation
    alternatives: List[Dict]  # Other possible interpretations
    
class InteractiveParseResult(BaseModel):
    """Result of interactive parsing."""
    parsed_relationship: ParsedRelationship
    clarification_questions: List[str]
    user_feedback: Optional[str]
    
class NLRelationshipRequest(BaseModel):
    """Request for NL relationship parsing."""
    description: str
    kg_name: str
    mode: str = "single"  # single, batch, interactive
    confidence_threshold: float = 0.7
    auto_create: bool = False
```

---

## 3. LLM PROMPT ENGINEERING

### 3.1 Entity Recognition Prompt

```
System: You are an expert database analyst. Extract entity names from 
natural language descriptions and match them to database tables.

User: "Products are supplied by Vendors with delivery_date"

Task:
1. Identify entities mentioned
2. Match to available tables: [products, vendors, orders, customers, ...]
3. Handle synonyms and abbreviations
4. Return confidence for each match

Output JSON:
{
    "entities": [
        {
            "mentioned": "Products",
            "matched_table": "products",
            "confidence": 0.98,
            "synonyms": ["items", "goods"]
        },
        {
            "mentioned": "Vendors",
            "matched_table": "vendors",
            "confidence": 0.95,
            "synonyms": ["suppliers", "providers"]
        }
    ]
}
```

### 3.2 Relationship Type Inference Prompt

```
System: Map natural language descriptions to relationship types.
Available types: FOREIGN_KEY, REFERENCES, BELONGS_TO, 
CROSS_SCHEMA_REFERENCE, SEMANTIC_REFERENCE, BUSINESS_LOGIC

User: "Products are supplied by Vendors"

Task:
1. Analyze the verb and context
2. Determine cardinality (1:1, 1:N, N:N)
3. Map to appropriate relationship type
4. Suggest custom type if needed

Output JSON:
{
    "relationship_type": "SUPPLIES",
    "base_type": "SEMANTIC_REFERENCE",
    "cardinality": "1:N",
    "direction": "vendors → products",
    "confidence": 0.92,
    "reasoning": "Verb 'supplied by' indicates one vendor supplies many products"
}
```

### 3.3 Property Extraction Prompt

```
System: Extract relationship properties from natural language.

User: "Products are supplied by Vendors with delivery_date and cost"

Task:
1. Identify properties mentioned
2. Match to available columns
3. Infer data types
4. Validate against schema

Output JSON:
{
    "properties": [
        {
            "name": "delivery_date",
            "inferred_type": "date",
            "confidence": 0.95,
            "source_table": "vendors",
            "target_table": "products"
        },
        {
            "name": "cost",
            "inferred_type": "decimal",
            "confidence": 0.90,
            "source_table": "vendors",
            "target_table": "products"
        }
    ]
}
```

### 3.4 Validation & Confidence Prompt

```
System: Assess relationship validity and confidence.

User: Parsed relationship + schema context

Task:
1. Check schema compatibility
2. Identify potential issues
3. Assess overall confidence
4. Suggest improvements

Output JSON:
{
    "validation_status": "VALID",
    "confidence_score": 0.92,
    "issues": [],
    "warnings": [],
    "suggestions": [
        "Consider adding 'quantity' as a property"
    ],
    "reasoning": "Clear semantic relationship with strong naming patterns"
}
```

---

## 4. API ENDPOINT DESIGN

### 4.1 Single Relationship Parsing

```
POST /api/v1/relationships/from-text

Request:
{
    "description": "Products are supplied by Vendors with delivery_date",
    "kg_name": "ecommerce_kg",
    "confidence_threshold": 0.7
}

Response:
{
    "success": true,
    "parsed_relationship": {
        "source_entity": "vendors",
        "target_entity": "products",
        "relationship_type": "SUPPLIES",
        "properties": {"delivery_date": "date"},
        "cardinality": "1:N",
        "confidence_score": 0.92,
        "validation_status": "VALID"
    },
    "alternatives": [
        {
            "relationship_type": "REFERENCES",
            "confidence": 0.78
        }
    ]
}
```

### 4.2 Batch Relationship Parsing

```
POST /api/v1/relationships/batch-from-text

Request:
{
    "descriptions": [
        "Products are supplied by Vendors",
        "Orders contain Products with quantity",
        "Customers place Orders"
    ],
    "kg_name": "ecommerce_kg",
    "auto_create": false
}

Response:
{
    "success": true,
    "total": 3,
    "parsed": 3,
    "failed": 0,
    "relationships": [
        {...},
        {...},
        {...}
    ],
    "processing_time_ms": 2345
}
```

### 4.3 Interactive Parsing

```
POST /api/v1/relationships/interactive

Request (Turn 1):
{
    "description": "Products and Vendors have a relationship",
    "kg_name": "ecommerce_kg",
    "turn": 1
}

Response (Turn 1):
{
    "clarification_questions": [
        "Is this a one-to-many relationship (one vendor supplies many products)?",
        "Should the relationship type be SUPPLIES or REFERENCES?",
        "Are there any properties like delivery_date or cost?"
    ],
    "confidence": 0.65
}

Request (Turn 2):
{
    "description": "Products and Vendors have a relationship",
    "clarifications": {
        "cardinality": "1:N",
        "relationship_type": "SUPPLIES",
        "properties": ["delivery_date", "cost"]
    },
    "turn": 2
}

Response (Turn 2):
{
    "success": true,
    "parsed_relationship": {...},
    "confidence": 0.95
}
```

### 4.4 Template Listing

```
GET /api/v1/relationships/templates

Response:
{
    "templates": [
        {
            "pattern": "[Entity A] [verb] [Entity B]",
            "examples": [
                "Products are supplied by Vendors",
                "Customers place Orders"
            ],
            "description": "Basic relationship"
        },
        {
            "pattern": "[Entity A] has [cardinality] [Entity B]",
            "examples": [
                "Vendors have many Products",
                "Orders have one Customer"
            ],
            "description": "Explicit cardinality"
        },
        {
            "pattern": "[Entity A] [verb] [Entity B] with [properties]",
            "examples": [
                "Products are supplied by Vendors with delivery_date",
                "Orders contain Products with quantity"
            ],
            "description": "With properties"
        }
    ]
}
```

---

## 5. INTEGRATION WITH EXISTING SYSTEMS

### 5.1 KG Generation Flow Enhancement

```
Current Flow:
Schema → Auto-detect relationships → Generate KG

Enhanced Flow:
Schema → Auto-detect relationships → 
    ↓
    User provides NL definitions (optional)
    ↓
    Parse NL relationships → Merge with auto-detected →
    ↓
    Generate unified KG
```

### 5.2 Relationship Update Flow

```
Existing KG → User provides NL updates →
    ↓
    Parse NL relationships →
    ↓
    Validate against existing KG →
    ↓
    Merge/Update relationships →
    ↓
    Regenerate KG
```

---

## 6. ERROR HANDLING & FALLBACKS

### 6.1 Error Scenarios

```python
class NLParsingError(Exception):
    """Base exception for NL parsing errors."""
    
class EntityNotFoundError(NLParsingError):
    """Entity not found in schema."""
    
class AmbiguousEntityError(NLParsingError):
    """Multiple entities match the description."""
    
class LowConfidenceError(NLParsingError):
    """Confidence score below threshold."""
    
class ValidationError(NLParsingError):
    """Relationship fails validation."""
```

### 6.2 Fallback Strategies

```
If LLM unavailable:
    → Use rule-based pattern matching
    → Return cached results
    → Suggest manual entry

If confidence < threshold:
    → Request user clarification
    → Suggest alternatives
    → Provide manual override

If entity not found:
    → Suggest similar entities
    → Ask for clarification
    → Provide entity list
```

---

## 7. PERFORMANCE OPTIMIZATION

### 7.1 Caching Strategy

```python
# Cache entity mappings
entity_cache = {
    "products": "products_table",
    "vendors": "vendors_table",
    "orders": "orders_table"
}

# Cache relationship type mappings
rel_type_cache = {
    "supplied by": "SUPPLIES",
    "contains": "CONTAINS",
    "placed by": "PLACES"
}

# Cache LLM results
llm_result_cache = {
    "hash(description)": parsed_relationship
}
```

### 7.2 Batch Processing

```python
# Process multiple relationships efficiently
def parse_batch_relationships(descriptions):
    # Group similar descriptions
    # Batch LLM calls
    # Parallel validation
    # Return results
```

### 7.3 Token Usage Estimation

```
Per relationship:
- Entity extraction: 100 tokens
- Type inference: 150 tokens
- Property extraction: 100 tokens
- Validation: 100 tokens
- Total: ~450 tokens

Batch of 10: ~4500 tokens
Cost: ~$0.002 per batch
```

---

## 8. TESTING STRATEGY

### 8.1 Unit Tests

```python
# Test entity recognition
test_entity_extraction()

# Test relationship type inference
test_relationship_type_mapping()

# Test property extraction
test_property_extraction()

# Test validation
test_relationship_validation()

# Test confidence scoring
test_confidence_scoring()
```

### 8.2 Integration Tests

```python
# Test end-to-end parsing
test_single_relationship_parsing()

# Test batch parsing
test_batch_relationship_parsing()

# Test interactive parsing
test_interactive_parsing()

# Test KG integration
test_kg_generation_with_nl()
```

### 8.3 Test Data

```python
test_cases = [
    {
        "input": "Products are supplied by Vendors",
        "expected": {
            "source": "vendors",
            "target": "products",
            "type": "SUPPLIES"
        }
    },
    # ... more test cases
]
```

---

## 9. MONITORING & LOGGING

### 9.1 Metrics to Track

```python
# Parsing success rate
parsing_success_rate = successful_parses / total_parses

# Average confidence score
avg_confidence = sum(scores) / len(scores)

# LLM token usage
total_tokens_used = sum(token_counts)

# Processing time
avg_processing_time = sum(times) / len(times)

# User satisfaction
user_satisfaction_score = feedback_score
```

### 9.2 Logging

```python
logger.debug(f"NL Input: {description}")
logger.debug(f"Extracted entities: {entities}")
logger.debug(f"Inferred type: {rel_type}")
logger.debug(f"Confidence: {confidence}")
logger.info(f"Successfully parsed relationship: {rel_type}")
logger.warning(f"Low confidence ({confidence}): {description}")
logger.error(f"Parsing failed: {error}")
```

---

## 10. SECURITY CONSIDERATIONS

### 10.1 Input Validation

```python
# Sanitize input
description = sanitize_input(description)

# Check length
if len(description) > 1000:
    raise ValueError("Description too long")

# Check for injection attempts
if contains_sql_injection(description):
    raise ValueError("Invalid input")
```

### 10.2 Rate Limiting

```python
# Limit API calls per user
rate_limit = 100 calls per hour

# Limit LLM calls
llm_rate_limit = 1000 calls per day
```

---

**Document Status**: Technical Design Complete ✅
**Ready for**: Implementation & Development

