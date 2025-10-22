# Reconciliation Rule Generation using Knowledge Graph

**Project**: dq-poc Knowledge Graph Builder
**Document**: Implementation Approach for Automated Reconciliation Rule Generation
**Date**: 2025-10-21
**Status**: Design Phase

---

## Table of Contents

1. [Overview & Objectives](#1-overview--objectives)
2. [Architecture Design](#2-architecture-design)
3. [Detailed Implementation Approach](#3-detailed-implementation-approach)
4. [Practical Example](#4-practical-example)
5. [Advanced Features](#5-advanced-features)
6. [Benefits & Use Cases](#6-benefits--use-cases)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Configuration Updates](#8-configuration-updates)
9. [Testing Strategy](#9-testing-strategy)
10. [Summary](#10-summary)

---

## 1. OVERVIEW & OBJECTIVES

### What Are Reconciliation Rules?

Reconciliation rules define how to:
- **Match records** across different database schemas/systems
- **Identify duplicates** or related entities
- **Link data** from disparate sources (e.g., `catalog.vendor_uid` ↔ `supplier.id`)
- **Validate data consistency** across systems
- **Transform and merge** data during ETL processes

### How Knowledge Graph Helps

Your existing KG capabilities can automatically:
1. Discover **semantic relationships** between entities across schemas
2. Identify **matching keys** (primary/foreign keys, UIDs)
3. Infer **business logic** for data matching
4. Generate **confidence-scored rules** using LLM intelligence
5. Handle **multi-schema reconciliation** scenarios

---

## 2. ARCHITECTURE DESIGN

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                       │
│  /api/v1/reconciliation/generate                            │
│  /api/v1/reconciliation/rules/{rule_id}                     │
│  /api/v1/reconciliation/validate                            │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│           Reconciliation Service Layer                       │
│  • ReconciliationRuleGenerator                              │
│  • RuleValidator                                             │
│  • RuleMatcher                                               │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴──────────────────┐
        │                                      │
┌───────▼────────┐                   ┌────────▼────────┐
│  LLM Service   │                   │ Knowledge Graph │
│  (OpenAI)      │                   │  (FalkorDB/     │
│                │                   │   Graphiti)     │
│ • Infer rules  │                   │                 │
│ • Score rules  │                   │ • Entity        │
│ • Validate     │                   │   matching      │
└────────────────┘                   │ • Relationship  │
                                     │   traversal     │
                                     └─────────────────┘
```

### 2.2 New Components to Add

#### A. Data Models (`kg_builder/models.py`)

```python
class ReconciliationMatchType(str, Enum):
    EXACT = "exact"              # Exact column match
    FUZZY = "fuzzy"              # Fuzzy string matching
    COMPOSITE = "composite"      # Multiple columns
    TRANSFORMATION = "transformation"  # Apply transform function
    SEMANTIC = "semantic"        # LLM-inferred semantic match

class ReconciliationRule(BaseModel):
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
    created_at: datetime
    metadata: Dict[str, Any] = {}

class ReconciliationRuleSet(BaseModel):
    ruleset_id: str
    ruleset_name: str
    schemas: List[str]
    rules: List[ReconciliationRule]
    created_at: datetime
    generated_from_kg: str  # KG name

class RuleGenerationRequest(BaseModel):
    schema_names: List[str]
    kg_name: str  # Use existing or generate new KG
    use_llm_enhancement: bool = True
    min_confidence: float = 0.7
    match_types: List[ReconciliationMatchType] = [
        ReconciliationMatchType.EXACT,
        ReconciliationMatchType.SEMANTIC
    ]

class RuleGenerationResponse(BaseModel):
    success: bool
    ruleset_id: str
    rules_count: int
    rules: List[ReconciliationRule]
    generation_time_ms: float
```

#### B. Reconciliation Service (`kg_builder/services/reconciliation_service.py`)

```python
class ReconciliationRuleGenerator:
    """Generate reconciliation rules from knowledge graph."""

    def generate_rules_from_kg(
        self,
        kg_name: str,
        schemas_info: Dict[str, Any],
        use_llm: bool = True,
        min_confidence: float = 0.7
    ) -> List[ReconciliationRule]:
        """
        Generate reconciliation rules by analyzing KG relationships.

        Steps:
        1. Query KG for cross-schema relationships
        2. Identify matching key patterns (PKs, FKs, UIDs)
        3. Use LLM to infer semantic matches
        4. Score each rule for confidence
        5. Return validated rules
        """
        pass
```

---

## 3. DETAILED IMPLEMENTATION APPROACH

### Phase 1: Core Rule Generation Engine

#### Step 1.1: Extend Multi-Schema LLM Service

Location: `kg_builder/services/multi_schema_llm_service.py`

Add new method:

```python
def generate_reconciliation_rules(
    self,
    relationships: List[Dict[str, Any]],
    schemas_info: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Use LLM to generate reconciliation rules from relationships.

    Prompt will ask LLM to:
    - Identify matching columns across schemas
    - Suggest match strategies (exact, fuzzy, composite)
    - Provide SQL/Python transformation logic if needed
    - Score confidence for each rule
    """
```

**LLM Prompt Template**:

```
Given these cross-schema relationships and schemas:

SCHEMAS:
{schemas_json}

RELATIONSHIPS:
{relationships_json}

Generate reconciliation rules that would allow matching records between these schemas.

For each rule, provide:
1. source_schema, source_table, source_columns[]
2. target_schema, target_table, target_columns[]
3. match_type: "exact", "fuzzy", "composite", "transformation", "semantic"
4. transformation: SQL or Python code for data matching (if needed)
5. confidence: 0.0-1.0 score
6. reasoning: Why this rule would work
7. example_match: Sample matching scenario

Return JSON:
{
  "rules": [
    {
      "source_schema": "orderMgmt",
      "source_table": "catalog",
      "source_columns": ["vendor_uid"],
      "target_schema": "vendorDB",
      "target_table": "suppliers",
      "target_columns": ["supplier_id"],
      "match_type": "exact",
      "transformation": null,
      "confidence": 0.95,
      "reasoning": "Both fields are UIDs representing vendors",
      "example_match": "vendor_uid='VND123' matches supplier_id='VND123'"
    }
  ]
}
```

#### Step 1.2: Create Reconciliation Service

File: `kg_builder/services/reconciliation_service.py`

```python
class ReconciliationRuleGenerator:
    def __init__(self):
        self.llm_service = get_multi_schema_llm_service()
        self.schema_parser = SchemaParser()

    def generate_from_knowledge_graph(
        self,
        kg_name: str,
        schema_names: List[str],
        use_llm: bool = True,
        min_confidence: float = 0.7
    ) -> ReconciliationRuleSet:
        """Main entry point for rule generation."""

        # 1. Load schemas
        schemas_info = self._load_schemas(schema_names)

        # 2. Query KG for relationships
        relationships = self._get_kg_relationships(kg_name)

        # 3. Generate basic rules from patterns
        basic_rules = self._generate_pattern_based_rules(
            relationships, schemas_info
        )

        # 4. Enhance with LLM if enabled
        if use_llm and self.llm_service.is_enabled():
            llm_rules = self.llm_service.generate_reconciliation_rules(
                relationships, schemas_info
            )
            all_rules = basic_rules + llm_rules
        else:
            all_rules = basic_rules

        # 5. Filter by confidence
        filtered_rules = [r for r in all_rules if r.confidence >= min_confidence]

        # 6. Create ruleset
        ruleset = ReconciliationRuleSet(
            ruleset_id=generate_uid(),
            ruleset_name=f"Reconciliation_{kg_name}",
            schemas=schema_names,
            rules=filtered_rules,
            created_at=datetime.utcnow(),
            generated_from_kg=kg_name
        )

        return ruleset

    def _generate_pattern_based_rules(
        self,
        relationships: List[Dict],
        schemas_info: Dict
    ) -> List[ReconciliationRule]:
        """Generate rules from naming patterns."""
        rules = []

        for rel in relationships:
            # Pattern 1: Foreign Key relationships
            if rel.get('relationship_type') == 'FOREIGN_KEY':
                rules.append(ReconciliationRule(
                    rule_id=generate_uid(),
                    rule_name=f"FK_{rel['source_table']}_{rel['target_table']}",
                    source_schema=rel['source_schema'],
                    source_table=rel['source_table'],
                    source_columns=[rel.get('source_column')],
                    target_schema=rel['target_schema'],
                    target_table=rel['target_table'],
                    target_columns=[rel.get('target_column')],
                    match_type=ReconciliationMatchType.EXACT,
                    confidence=0.95,
                    reasoning="Foreign key constraint implies exact match",
                    validation_status="VALID",
                    llm_generated=False,
                    created_at=datetime.utcnow()
                ))

            # Pattern 2: UID columns (vendor_uid, user_uid, etc.)
            if self._is_uid_pattern(rel.get('source_column')) and \
               self._is_uid_pattern(rel.get('target_column')):
                rules.append(ReconciliationRule(
                    rule_id=generate_uid(),
                    rule_name=f"UID_Match_{rel['source_column']}",
                    source_schema=rel['source_schema'],
                    source_table=rel['source_table'],
                    source_columns=[rel['source_column']],
                    target_schema=rel['target_schema'],
                    target_table=rel['target_table'],
                    target_columns=[rel['target_column']],
                    match_type=ReconciliationMatchType.EXACT,
                    confidence=0.85,
                    reasoning="UID naming pattern suggests unique identifier match",
                    validation_status="LIKELY",
                    llm_generated=False,
                    created_at=datetime.utcnow()
                ))

            # Pattern 3: Code columns (sap_code, ean_code, etc.)
            # Pattern 4: Name + ID composite keys
            # ... add more pattern-based rules

        return rules

    def _is_uid_pattern(self, column_name: str) -> bool:
        """Check if column follows UID naming pattern."""
        if not column_name:
            return False
        return column_name.endswith('_uid') or column_name.endswith('_id')
```

---

### Phase 2: API Endpoints

#### Step 2.1: Add Routes (`kg_builder/routes.py`)

```python
@router.post("/api/v1/reconciliation/generate", response_model=RuleGenerationResponse)
async def generate_reconciliation_rules(request: RuleGenerationRequest):
    """
    Generate reconciliation rules from knowledge graph.

    Example:
    POST /api/v1/reconciliation/generate
    {
      "schema_names": ["orderMgmt-catalog", "vendorDB-suppliers"],
      "kg_name": "unified_kg",
      "use_llm_enhancement": true,
      "min_confidence": 0.7
    }
    """
    generator = ReconciliationRuleGenerator()

    start_time = time.time()
    ruleset = generator.generate_from_knowledge_graph(
        kg_name=request.kg_name,
        schema_names=request.schema_names,
        use_llm=request.use_llm_enhancement,
        min_confidence=request.min_confidence
    )

    return RuleGenerationResponse(
        success=True,
        ruleset_id=ruleset.ruleset_id,
        rules_count=len(ruleset.rules),
        rules=ruleset.rules,
        generation_time_ms=(time.time() - start_time) * 1000
    )

@router.get("/api/v1/reconciliation/rules/{ruleset_id}")
async def get_reconciliation_ruleset(ruleset_id: str):
    """Retrieve a saved reconciliation ruleset."""
    # Load from storage (file or database)
    pass

@router.post("/api/v1/reconciliation/validate")
async def validate_reconciliation_rule(rule: ReconciliationRule):
    """
    Validate a reconciliation rule against actual data.

    Tests:
    - Do source/target tables exist?
    - Do columns exist and have compatible types?
    - Sample data match test (10 records)
    - Performance estimate
    """
    validator = RuleValidator()
    validation_result = validator.validate_rule(rule)
    return validation_result

@router.post("/api/v1/reconciliation/execute")
async def execute_reconciliation(
    ruleset_id: str,
    limit: int = 100
):
    """
    Execute reconciliation rules and return matched records.

    Returns:
    {
      "matched_records": [
        {
          "source_record": {...},
          "target_record": {...},
          "match_confidence": 0.95,
          "rule_used": "rule_id"
        }
      ],
      "unmatched_source": [...],
      "unmatched_target": [...]
    }
    """
    pass
```

---

### Phase 3: Rule Storage & Management

#### Step 3.1: Storage Backend

File: `kg_builder/services/rule_storage.py`

```python
class ReconciliationRuleStorage:
    """Store and retrieve reconciliation rulesets."""

    def __init__(self, storage_path: str = "data/reconciliation_rules"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def save_ruleset(self, ruleset: ReconciliationRuleSet):
        """Save ruleset to JSON file."""
        filepath = self.storage_path / f"{ruleset.ruleset_id}.json"
        with open(filepath, 'w') as f:
            json.dump(ruleset.dict(), f, indent=2, default=str)

    def load_ruleset(self, ruleset_id: str) -> ReconciliationRuleSet:
        """Load ruleset from storage."""
        filepath = self.storage_path / f"{ruleset_id}.json"
        with open(filepath, 'r') as f:
            data = json.load(f)
        return ReconciliationRuleSet(**data)

    def list_rulesets(self) -> List[str]:
        """List all saved rulesets."""
        return [f.stem for f in self.storage_path.glob("*.json")]
```

---

## 4. PRACTICAL EXAMPLE

### Scenario: Reconcile Order Management & Vendor Database

**Input Schemas**:
1. `orderMgmt-catalog.json` - Product catalog with `vendor_uid`
2. `vendorDB-suppliers.json` - Supplier database with `supplier_id`

**Step 1: Generate Knowledge Graph**

```bash
curl -X POST http://localhost:8000/api/v1/kg/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_names": ["orderMgmt-catalog", "vendorDB-suppliers"],
    "kg_name": "order_vendor_kg",
    "use_llm_enhancement": true
  }'
```

**Step 2: Generate Reconciliation Rules**

```bash
curl -X POST http://localhost:8000/api/v1/reconciliation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_names": ["orderMgmt-catalog", "vendorDB-suppliers"],
    "kg_name": "order_vendor_kg",
    "use_llm_enhancement": true,
    "min_confidence": 0.7
  }'
```

**Expected Output**:

```json
{
  "success": true,
  "ruleset_id": "RECON_12345",
  "rules_count": 5,
  "rules": [
    {
      "rule_id": "RULE_001",
      "rule_name": "Vendor_UID_Match",
      "source_schema": "orderMgmt",
      "source_table": "catalog",
      "source_columns": ["vendor_uid"],
      "target_schema": "vendorDB",
      "target_table": "suppliers",
      "target_columns": ["supplier_id"],
      "match_type": "exact",
      "transformation": null,
      "confidence_score": 0.95,
      "reasoning": "Both fields represent unique vendor identifiers with consistent naming pattern",
      "validation_status": "VALID",
      "llm_generated": true
    },
    {
      "rule_id": "RULE_002",
      "rule_name": "Vendor_Name_Fuzzy_Match",
      "source_schema": "orderMgmt",
      "source_table": "catalog",
      "source_columns": ["vendor_name"],
      "target_schema": "vendorDB",
      "target_table": "suppliers",
      "target_columns": ["company_name"],
      "match_type": "fuzzy",
      "transformation": "LOWER(TRIM(vendor_name))",
      "confidence_score": 0.78,
      "reasoning": "Names may have slight variations; fuzzy matching with normalization recommended",
      "validation_status": "LIKELY",
      "llm_generated": true
    }
  ],
  "generation_time_ms": 2340.5
}
```

---

## 5. ADVANCED FEATURES

### 5.1 Rule Types Supported

| Match Type | Description | Example |
|------------|-------------|---------|
| **EXACT** | Direct column-to-column match | `vendor_uid = supplier_id` |
| **FUZZY** | String similarity matching | `LEVENSHTEIN(name1, name2) < 3` |
| **COMPOSITE** | Multiple columns together | `(first_name, last_name) = (fname, lname)` |
| **TRANSFORMATION** | Apply function before match | `UPPER(TRIM(code))` |
| **SEMANTIC** | LLM-inferred logical match | `order_date correlates with purchase_timestamp` |

### 5.2 Confidence Scoring Criteria

```python
def calculate_confidence(rule_context: Dict) -> float:
    """
    Factors:
    - Foreign key constraint: +0.95
    - Primary key match: +0.90
    - UID pattern match: +0.80
    - Name similarity: +0.70
    - Data type compatibility: +0.15
    - LLM semantic score: variable
    """
    pass
```

### 5.3 Rule Validation

```python
class RuleValidator:
    def validate_rule(self, rule: ReconciliationRule) -> ValidationResult:
        """
        Validation checks:
        1. Schema/table existence
        2. Column existence and data type compatibility
        3. Sample data matching (test on 10-100 records)
        4. Cardinality check (1:1, 1:N, N:M)
        5. Performance estimation
        """
        results = {
            "exists": self._check_existence(rule),
            "types_compatible": self._check_types(rule),
            "sample_match_rate": self._test_sample_data(rule),
            "cardinality": self._detect_cardinality(rule),
            "estimated_performance_ms": self._estimate_performance(rule)
        }
        return ValidationResult(**results)
```

---

## 6. BENEFITS & USE CASES

### Benefits

1. ✅ **Automated Discovery** - No manual rule writing needed
2. ✅ **Intelligence** - LLM finds non-obvious relationships
3. ✅ **Confidence Scores** - Know which rules to trust
4. ✅ **Multi-Schema** - Handle complex integration scenarios
5. ✅ **Validation** - Test rules before production use
6. ✅ **Versioning** - Track rule evolution over time

### Use Cases

- **Data Migration**: Match old system records to new system
- **Master Data Management**: Consolidate duplicate customer/product records
- **ETL Pipelines**: Auto-generate join conditions
- **Data Quality**: Identify inconsistencies across systems
- **API Integration**: Map fields between different APIs
- **Data Warehouse**: Build dimension tables from multiple sources

---

## 7. IMPLEMENTATION ROADMAP

### Week 1: Core Infrastructure

- [ ] Add reconciliation data models to `models.py`
- [ ] Create `reconciliation_service.py` skeleton
- [ ] Implement pattern-based rule generation
- [ ] Add rule storage backend

### Week 2: LLM Integration

- [ ] Extend `MultiSchemaLLMService` with rule generation
- [ ] Implement LLM prompts for rule inference
- [ ] Add confidence scoring logic
- [ ] Test with sample schemas

### Week 3: API & Validation

- [ ] Add API endpoints to `routes.py`
- [ ] Implement rule validation service
- [ ] Add rule execution engine
- [ ] Create test suite

### Week 4: Documentation & Testing

- [ ] Write comprehensive documentation
- [ ] Add API examples
- [ ] Performance testing
- [ ] User acceptance testing

---

## 8. CONFIGURATION UPDATES

### Add to `.env`

```bash
# Reconciliation Settings
RECON_STORAGE_PATH=data/reconciliation_rules
RECON_MIN_CONFIDENCE=0.7
RECON_ENABLE_LLM=true
RECON_SAMPLE_SIZE=100
```

### Add to `config.py`

```python
RECON_STORAGE_PATH = os.getenv("RECON_STORAGE_PATH", "data/reconciliation_rules")
RECON_MIN_CONFIDENCE = float(os.getenv("RECON_MIN_CONFIDENCE", "0.7"))
RECON_ENABLE_LLM = os.getenv("RECON_ENABLE_LLM", "true").lower() == "true"
RECON_SAMPLE_SIZE = int(os.getenv("RECON_SAMPLE_SIZE", "100"))
```

---

## 9. TESTING STRATEGY

### Test Files to Create

1. `tests/test_reconciliation_service.py` - Unit tests
2. `tests/test_reconciliation_api.py` - API endpoint tests
3. `tests/test_rule_validation.py` - Validation logic tests
4. `test_reconciliation_demo.py` - Integration demo

### Sample Test

```python
def test_generate_rules_from_two_schemas():
    """Test rule generation from orderMgmt and vendorDB schemas."""
    generator = ReconciliationRuleGenerator()

    ruleset = generator.generate_from_knowledge_graph(
        kg_name="test_kg",
        schema_names=["orderMgmt-catalog", "vendorDB-suppliers"],
        use_llm=True,
        min_confidence=0.7
    )

    assert ruleset.rules_count > 0
    assert all(r.confidence >= 0.7 for r in ruleset.rules)
    assert any(r.match_type == ReconciliationMatchType.EXACT for r in ruleset.rules)
```

---

## 10. SUMMARY

This approach leverages your existing knowledge graph infrastructure to:

1. **Automatically generate reconciliation rules** from cross-schema relationships
2. **Use LLM intelligence** to discover non-obvious matching patterns
3. **Provide confidence scoring** for data quality assurance
4. **Validate rules** before deployment
5. **Execute reconciliation** and report matched/unmatched records

### Key Files to Create/Modify

| File | Type | Lines | Description |
|------|------|-------|-------------|
| `kg_builder/models.py` | Modify | +171 | Add 5 new Pydantic models |
| `kg_builder/services/reconciliation_service.py` | NEW | 400+ | Core rule generation logic |
| `kg_builder/services/rule_storage.py` | NEW | 100 | Rule persistence layer |
| `kg_builder/services/multi_schema_llm_service.py` | Modify | +80 | Add rule generation method |
| `kg_builder/routes.py` | Modify | +150 | Add 4 API endpoints |
| `kg_builder/config.py` | Modify | +10 | Add configuration variables |
| `.env` | Modify | +4 | Add reconciliation settings |
| `tests/test_reconciliation_*.py` | NEW | 300+ | Test suite |

**Estimated Total**: ~900 lines of new code

### Next Steps

1. Review and approve this design approach
2. Prioritize which phases to implement first
3. Set up development environment for testing
4. Begin implementation with Phase 1 (Core Infrastructure)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-21
