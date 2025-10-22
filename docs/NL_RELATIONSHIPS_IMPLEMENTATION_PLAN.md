# Natural Language Relationships - Implementation Plan

## 🎯 OBJECTIVE

Implement a feature that allows users to define custom relationships between entities using natural language, which will enhance the knowledge graph and improve reconciliation rule generation.

---

## 📋 IMPLEMENTATION PHASES

### PHASE 1: Core NL Parser (Week 1)

#### Task 1.1: Create NL Relationship Parser Service
**File**: `kg_builder/services/nl_relationship_parser.py`

```python
class NaturalLanguageRelationshipParser:
    """Parse natural language relationship definitions."""
    
    def __init__(self):
        self.llm_service = get_multi_schema_llm_service()
        self.schema_parser = SchemaParser()
    
    def parse(self, input_text: str, schemas_info: Dict) -> List[RelationshipDefinition]:
        """
        Parse natural language input.
        
        Supports:
        1. Natural language: "Products are supplied by Vendors"
        2. Semi-structured: "catalog.product_id → vendor.vendor_id (SUPPLIED_BY)"
        3. Pseudo-SQL: "SELECT * FROM products JOIN vendors ON ..."
        4. Business rules: "IF product.status='active' THEN ..."
        """
        # Stage 1: Detect input format
        input_format = self._detect_format(input_text)
        
        # Stage 2: Parse based on format
        if input_format == "natural_language":
            return self._parse_natural_language(input_text, schemas_info)
        elif input_format == "semi_structured":
            return self._parse_semi_structured(input_text, schemas_info)
        elif input_format == "pseudo_sql":
            return self._parse_pseudo_sql(input_text, schemas_info)
        elif input_format == "business_rules":
            return self._parse_business_rules(input_text, schemas_info)
    
    def _parse_natural_language(self, text: str, schemas_info: Dict) -> List[RelationshipDefinition]:
        """Parse natural language using LLM."""
        # Use LLM to extract entities, relationship type, properties
        pass
    
    def _parse_semi_structured(self, text: str, schemas_info: Dict) -> List[RelationshipDefinition]:
        """Parse semi-structured format."""
        # Parse: "table1.col1 → table2.col2 (RELATIONSHIP_TYPE)"
        pass
    
    def _parse_pseudo_sql(self, text: str, schemas_info: Dict) -> List[RelationshipDefinition]:
        """Parse pseudo-SQL format."""
        # Parse: "SELECT * FROM t1 JOIN t2 ON t1.id = t2.id"
        pass
    
    def _parse_business_rules(self, text: str, schemas_info: Dict) -> List[RelationshipDefinition]:
        """Parse business rule format."""
        # Parse: "IF condition THEN relationship"
        pass
```

**Deliverables:**
- ✅ Parser service with multi-format support
- ✅ LLM integration for NL parsing
- ✅ Format detection logic
- ✅ Unit tests

---

#### Task 1.2: Create Data Models
**File**: `kg_builder/models.py` (add to existing file)

```python
class RelationshipDefinition(BaseModel):
    """Natural language relationship definition."""
    source_table: str
    target_table: str
    relationship_type: str
    properties: List[str] = []
    cardinality: str = "1:N"
    confidence: float
    reasoning: str
    input_format: str  # "natural_language", "semi_structured", etc.

class NLRelationshipRequest(BaseModel):
    """Request to add NL-defined relationships."""
    kg_name: str
    definitions: List[str]  # List of NL definitions
    schemas: List[str]
    use_llm: bool = True

class NLRelationshipResponse(BaseModel):
    """Response with parsed relationships."""
    success: bool
    relationships: List[RelationshipDefinition]
    parsed_count: int
    failed_count: int
    errors: List[str] = []
```

**Deliverables:**
- ✅ Pydantic models for requests/responses
- ✅ Validation rules
- ✅ Type hints

---

#### Task 1.3: Create API Endpoint
**File**: `kg_builder/routes.py` (add to existing file)

```python
@router.post("/kg/relationships/natural-language", response_model=NLRelationshipResponse)
async def add_natural_language_relationships(request: NLRelationshipRequest):
    """
    Add relationships defined in natural language to knowledge graph.
    
    Example:
    POST /api/v1/kg/relationships/natural-language
    {
      "kg_name": "demo_kg",
      "schemas": ["orderMgmt-catalog", "vendorDB-suppliers"],
      "definitions": [
        "Products are supplied by Vendors",
        "Orders contain Products with quantity",
        "Vendors have Locations"
      ],
      "use_llm": true
    }
    """
    try:
        parser = NaturalLanguageRelationshipParser()
        schemas_info = SchemaParser._prepare_schemas_info(...)
        
        relationships = []
        errors = []
        
        for definition in request.definitions:
            try:
                parsed = parser.parse(definition, schemas_info)
                relationships.extend(parsed)
            except Exception as e:
                errors.append(f"Failed to parse '{definition}': {str(e)}")
        
        # Add to knowledge graph
        kg = get_knowledge_graph(request.kg_name)
        for rel in relationships:
            kg.add_relationship(rel)
        
        return NLRelationshipResponse(
            success=len(errors) == 0,
            relationships=relationships,
            parsed_count=len(relationships),
            failed_count=len(errors),
            errors=errors
        )
    except Exception as e:
        logger.error(f"Error adding NL relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Deliverables:**
- ✅ REST API endpoint
- ✅ Error handling
- ✅ Response formatting

---

### PHASE 2: LLM Integration (Week 2)

#### Task 2.1: Implement LLM Parsing Methods
**File**: `kg_builder/services/nl_relationship_parser.py`

```python
def _parse_natural_language(self, text: str, schemas_info: Dict) -> List[RelationshipDefinition]:
    """Parse natural language using LLM."""
    
    # Build prompt
    prompt = self._build_nl_parsing_prompt(text, schemas_info)
    
    # Call LLM
    response = self.llm_service.client.chat.completions.create(
        model=self.llm_service.model,
        messages=[
            {
                "role": "system",
                "content": "You are an expert data modeler. Parse natural language relationship definitions."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    # Parse response
    return self._parse_llm_response(response.choices[0].message.content)

def _build_nl_parsing_prompt(self, text: str, schemas_info: Dict) -> str:
    """Build prompt for NL parsing."""
    schemas_str = json.dumps(schemas_info, indent=2)
    
    return f"""Parse this natural language relationship definition:

"{text}"

Available schemas and tables:
{schemas_str}

Extract and return as JSON:
{{
    "relationships": [
        {{
            "source_table": "table_name",
            "target_table": "table_name",
            "relationship_type": "RELATIONSHIP_TYPE",
            "properties": ["prop1", "prop2"],
            "cardinality": "1:N",
            "confidence": 0.95,
            "reasoning": "Why this relationship makes sense"
        }}
    ]
}}"""
```

**Deliverables:**
- ✅ LLM-based NL parsing
- ✅ Prompt engineering
- ✅ Response parsing

---

#### Task 2.2: Add Validation Logic
**File**: `kg_builder/services/nl_relationship_parser.py`

```python
def _validate_relationship(self, rel: RelationshipDefinition, schemas_info: Dict) -> Tuple[bool, str]:
    """Validate parsed relationship against schema."""
    
    # Check source table exists
    if rel.source_table not in schemas_info:
        return False, f"Source table '{rel.source_table}' not found"
    
    # Check target table exists
    if rel.target_table not in schemas_info:
        return False, f"Target table '{rel.target_table}' not found"
    
    # Check properties exist in target table
    target_schema = schemas_info[rel.target_table]
    for prop in rel.properties:
        if prop not in target_schema.get('columns', []):
            return False, f"Property '{prop}' not found in target table"
    
    # Check relationship type is valid
    valid_types = ["FOREIGN_KEY", "REFERENCES", "BELONGS_TO", "SUPPLIED_BY", "CONTAINS", "PLACES"]
    if rel.relationship_type not in valid_types:
        return False, f"Invalid relationship type: {rel.relationship_type}"
    
    return True, "Valid"
```

**Deliverables:**
- ✅ Schema validation
- ✅ Error messages
- ✅ Confidence adjustment

---

### PHASE 3: Integration with KG (Week 2)

#### Task 3.1: Extend Knowledge Graph Service
**File**: `kg_builder/services/schema_parser.py`

```python
def add_natural_language_relationships(
    kg: KnowledgeGraph,
    nl_relationships: List[RelationshipDefinition]
) -> KnowledgeGraph:
    """Add NL-defined relationships to knowledge graph."""
    
    for nl_rel in nl_relationships:
        # Create GraphRelationship
        rel = GraphRelationship(
            source_id=nl_rel.source_table,
            target_id=nl_rel.target_table,
            relationship_type=nl_rel.relationship_type,
            properties={
                "confidence": nl_rel.confidence,
                "reasoning": nl_rel.reasoning,
                "source": "natural_language",
                "cardinality": nl_rel.cardinality
            }
        )
        
        kg.relationships.append(rel)
    
    return kg
```

**Deliverables:**
- ✅ KG extension logic
- ✅ Relationship creation
- ✅ Metadata tracking

---

### PHASE 4: Testing (Week 3)

#### Task 4.1: Unit Tests
**File**: `tests/test_nl_relationship_parser.py`

```python
def test_parse_natural_language():
    """Test parsing natural language definitions."""
    parser = NaturalLanguageRelationshipParser()
    
    text = "Products are supplied by Vendors"
    schemas_info = {...}
    
    result = parser.parse(text, schemas_info)
    
    assert len(result) == 1
    assert result[0].source_table == "products"
    assert result[0].target_table == "vendors"
    assert result[0].relationship_type == "SUPPLIED_BY"

def test_parse_semi_structured():
    """Test parsing semi-structured format."""
    parser = NaturalLanguageRelationshipParser()
    
    text = "catalog.product_id → vendor.vendor_id (SUPPLIED_BY)"
    schemas_info = {...}
    
    result = parser.parse(text, schemas_info)
    
    assert len(result) == 1
    assert result[0].confidence > 0.9
```

**Deliverables:**
- ✅ Unit tests (>80% coverage)
- ✅ Integration tests
- ✅ Edge case tests

---

#### Task 4.2: Integration Tests
**File**: `tests/test_nl_integration.py`

```python
def test_nl_relationships_with_reconciliation():
    """Test NL relationships improve reconciliation rules."""
    
    # 1. Generate initial KG
    kg = generate_kg(schemas)
    initial_rules = generate_reconciliation_rules(kg)
    
    # 2. Add NL relationships
    nl_defs = ["Products are supplied by Vendors"]
    enhanced_kg = add_natural_language_relationships(kg, nl_defs)
    
    # 3. Generate rules with NL relationships
    enhanced_rules = generate_reconciliation_rules(enhanced_kg)
    
    # 4. Verify improvement
    assert len(enhanced_rules) > len(initial_rules)
    assert avg_confidence(enhanced_rules) > avg_confidence(initial_rules)
```

**Deliverables:**
- ✅ Integration tests
- ✅ End-to-end tests
- ✅ Performance tests

---

## 📊 IMPLEMENTATION TIMELINE

| Phase | Tasks | Duration | Status |
|-------|-------|----------|--------|
| 1 | Parser + Models + API | Week 1 | 📋 Planned |
| 2 | LLM Integration + Validation | Week 2 | 📋 Planned |
| 3 | KG Integration | Week 2 | 📋 Planned |
| 4 | Testing | Week 3 | 📋 Planned |

---

## 🎯 SUCCESS METRICS

- ✅ Parse 95%+ of natural language definitions correctly
- ✅ Validate relationships against schema with 100% accuracy
- ✅ Improve reconciliation rule count by 20%+
- ✅ Increase average confidence score by 10%+
- ✅ Achieve >80% test coverage
- ✅ API response time <2 seconds for 10 definitions

---

## 🚀 READY TO START?

Would you like me to:
1. **Start implementing Phase 1** - Create the NL parser service
2. **Create test files first** - TDD approach
3. **Set up the project structure** - Create all necessary files
4. **Something else?**


