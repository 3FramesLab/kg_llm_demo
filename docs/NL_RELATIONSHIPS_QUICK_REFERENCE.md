# Natural Language Relationships - Quick Reference Guide

## 🎯 FEATURE AT A GLANCE

**What**: Allow users to define knowledge graph relationships using natural language
**Why**: Democratize KG creation, reduce complexity, improve accessibility
**How**: LLM-powered parsing with multi-stage validation
**When**: Ready for implementation planning
**Status**: ✅ Brainstorming & Design Complete

---

## 🔄 SYSTEM FLOW

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INPUT (NL)                          │
│  "Products are supplied by Vendors with delivery_date"      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              STAGE 1: ENTITY RECOGNITION                    │
│  Extract: products, vendors                                 │
│  Match to schema: products_table, vendors_table             │
│  Confidence: 0.98                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           STAGE 2: RELATIONSHIP TYPE INFERENCE              │
│  Verb: "supplied by"                                        │
│  Type: SUPPLIES                                             │
│  Cardinality: 1:N                                           │
│  Confidence: 0.92                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            STAGE 3: PROPERTY EXTRACTION                     │
│  Properties: delivery_date (date)                           │
│  Confidence: 0.95                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         STAGE 4: VALIDATION & CONFIDENCE SCORING            │
│  Schema validation: ✓ PASS                                  │
│  Cardinality check: ✓ PASS                                  │
│  Overall confidence: 0.92                                   │
│  Status: VALID                                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              STRUCTURED RELATIONSHIP                        │
│  {                                                          │
│    "source": "vendors",                                     │
│    "target": "products",                                    │
│    "type": "SUPPLIES",                                      │
│    "properties": {"delivery_date": "date"},                 │
│    "confidence": 0.92,                                      │
│    "status": "VALID"                                        │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 COMPARISON: APPROACHES

| Approach | Ease | Flexibility | LLM Cost | Best For |
|----------|------|-------------|----------|----------|
| **Conversational** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $$$ | Complex relationships |
| **Template-Based** | ⭐⭐⭐⭐ | ⭐⭐⭐ | $ | Quick implementation |
| **Hybrid Smart** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $$ | **RECOMMENDED** |
| **Visual Builder** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | $$ | Visual learners |
| **Batch Definition** | ⭐⭐⭐ | ⭐⭐⭐ | $ | Bulk operations |

**Recommendation**: Start with **Template-Based**, evolve to **Hybrid Smart Parser**

---

## 🎨 INPUT EXAMPLES

### Template 1: Basic Relationship
```
"[Entity A] [verb] [Entity B]"

Examples:
- "Products are supplied by Vendors"
- "Customers place Orders"
- "Orders contain Products"
```

### Template 2: With Cardinality
```
"[Entity A] has [cardinality] [Entity B]"

Examples:
- "Vendors have many Products"
- "Orders have one Customer"
- "Customers have multiple Addresses"
```

### Template 3: With Properties
```
"[Entity A] [verb] [Entity B] with [properties]"

Examples:
- "Products are supplied by Vendors with delivery_date"
- "Orders contain Products with quantity and price"
- "Customers have Addresses with address_type"
```

### Template 4: Conditional
```
"When [condition], [Entity A] [verb] [Entity B]"

Examples:
- "When product status is active, it references active_vendors"
- "If order status is pending, it cannot reference completed_shipments"
```

---

## 🔌 API ENDPOINTS

### 1. Single Relationship
```
POST /api/v1/relationships/from-text

Request:
{
  "description": "Products are supplied by Vendors",
  "kg_name": "ecommerce_kg"
}

Response:
{
  "success": true,
  "parsed_relationship": {
    "source": "vendors",
    "target": "products",
    "type": "SUPPLIES",
    "confidence": 0.92,
    "status": "VALID"
  }
}
```

### 2. Batch Processing
```
POST /api/v1/relationships/batch-from-text

Request:
{
  "descriptions": [
    "Products are supplied by Vendors",
    "Orders contain Products",
    "Customers place Orders"
  ],
  "kg_name": "ecommerce_kg"
}

Response:
{
  "success": true,
  "total": 3,
  "parsed": 3,
  "relationships": [...]
}
```

### 3. Interactive Mode
```
POST /api/v1/relationships/interactive

Turn 1 Request:
{
  "description": "Products and Vendors have a relationship",
  "turn": 1
}

Turn 1 Response:
{
  "clarification_questions": [
    "Is this 1:N (one vendor supplies many products)?",
    "Should type be SUPPLIES or REFERENCES?",
    "Any properties like delivery_date?"
  ]
}

Turn 2 Request:
{
  "clarifications": {
    "cardinality": "1:N",
    "type": "SUPPLIES",
    "properties": ["delivery_date"]
  },
  "turn": 2
}

Turn 2 Response:
{
  "success": true,
  "parsed_relationship": {...}
}
```

### 4. Templates
```
GET /api/v1/relationships/templates

Response:
{
  "templates": [
    {
      "pattern": "[Entity A] [verb] [Entity B]",
      "examples": ["Products are supplied by Vendors"]
    },
    ...
  ]
}
```

---

## 🧠 LLM PROMPTS (Summary)

### Prompt 1: Entity Recognition
Extract entities and match to schema tables

### Prompt 2: Type Inference
Map verbs to relationship types (SUPPLIES, CONTAINS, etc.)

### Prompt 3: Property Extraction
Identify properties and match to columns

### Prompt 4: Validation
Assess confidence and validity

---

## 📈 PERFORMANCE METRICS

| Metric | Value |
|--------|-------|
| Tokens per relationship | ~450 |
| Cost per relationship | ~$0.0002 |
| Processing time | 2-3 seconds |
| Batch of 10 cost | ~$0.002 |
| Cache hit reduction | 80% |
| Confidence threshold | 0.70 |

---

## ✅ VALIDATION STATUSES

| Status | Meaning | Action |
|--------|---------|--------|
| **VALID** | High confidence, passes all checks | Accept |
| **LIKELY** | Good confidence, minor issues | Review |
| **UNCERTAIN** | Medium confidence, needs clarification | Clarify |
| **INVALID** | Low confidence or fails validation | Reject |

---

## 🚀 IMPLEMENTATION PHASES

```
Week 1-2: Foundation
  ├─ Design LLM prompts
  ├─ Create data models
  └─ Entity recognition

Week 3-4: Core Feature
  ├─ Type inference
  ├─ Property extraction
  └─ Validation logic

Week 5-6: API Integration
  ├─ New endpoints
  ├─ Service integration
  └─ Error handling

Week 7-8: Enhancement
  ├─ Conversational interface
  ├─ Batch processing
  └─ Template system

Week 9-10: Polish
  ├─ Performance optimization
  ├─ Testing
  └─ Documentation
```

---

## 🎯 USE CASE MATRIX

| Use Case | Input Mode | Complexity | Value |
|----------|-----------|-----------|-------|
| Business analyst | Interactive | Low | High |
| Data integration | Batch | High | High |
| KG refinement | Single | Medium | Medium |
| Documentation-driven | Batch | Low | High |
| Conversational exploration | Interactive | Medium | Medium |

---

## 🔐 SECURITY CHECKLIST

- [ ] Input sanitization
- [ ] SQL injection prevention
- [ ] Rate limiting (100 calls/hour)
- [ ] LLM rate limiting (1000 calls/day)
- [ ] Authentication required
- [ ] Audit logging
- [ ] Error message sanitization

---

## 📊 RELATIONSHIP TYPES

**Existing Types**:
- FOREIGN_KEY - Explicit foreign key constraints
- REFERENCES - Inferred from column naming
- BELONGS_TO - Column belongs to table
- CROSS_SCHEMA_REFERENCE - Between schemas
- SEMANTIC_REFERENCE - LLM-inferred semantic
- BUSINESS_LOGIC - LLM-inferred business logic

**New Types** (can be added):
- SUPPLIES - Vendor supplies product
- CONTAINS - Order contains product
- PLACES - Customer places order
- SHIPPED_TO - Order shipped to address
- MAPS_TO - Cross-schema mapping
- EQUIVALENT_TO - Semantic equivalence

---

## 🧪 TEST SCENARIOS

### Happy Path
```
Input: "Products are supplied by Vendors"
Expected: SUPPLIES relationship, confidence 0.92+
Status: VALID
```

### Ambiguous Entity
```
Input: "Products are related to Items"
Expected: Suggest multiple matches
Status: Request clarification
```

### Low Confidence
```
Input: "Foo relates to Bar"
Expected: Confidence < 0.70
Status: Request more context
```

### Complex Relationship
```
Input: "When product status is active, it references active_vendors"
Expected: BUSINESS_LOGIC relationship with condition
Status: VALID
```

---

## 💾 DATA MODEL EXTENSION

```python
class GraphRelationship(BaseModel):
    # Existing
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any]
    
    # New
    natural_language_definition: Optional[str]
    confidence_score: Optional[float]
    validation_status: Optional[str]
    user_defined: bool = False
    created_by: Optional[str]
    created_at: Optional[datetime]
```

---

## 🎓 QUICK START FOR DEVELOPERS

1. **Read**: NATURAL_LANGUAGE_RELATIONSHIPS_BRAINSTORM.md
2. **Understand**: NL_RELATIONSHIPS_TECHNICAL_DESIGN.md
3. **Review**: NL_RELATIONSHIPS_PRACTICAL_EXAMPLES.md
4. **Implement**: Start with template-based approach
5. **Test**: Use examples from practical examples doc
6. **Iterate**: Gather user feedback and refine

---

## 📞 SUPPORT RESOURCES

| Document | Purpose |
|----------|---------|
| NATURAL_LANGUAGE_RELATIONSHIPS_BRAINSTORM.md | Conceptual overview |
| NL_RELATIONSHIPS_TECHNICAL_DESIGN.md | Technical details |
| NL_RELATIONSHIPS_PRACTICAL_EXAMPLES.md | Real-world examples |
| NL_RELATIONSHIPS_SUMMARY.md | Executive summary |
| NL_RELATIONSHIPS_QUICK_REFERENCE.md | This document |

---

**Last Updated**: 2025-10-22
**Status**: ✅ Complete & Ready for Implementation

