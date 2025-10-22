# Natural Language Relationship Definition - Brainstorming Document

## Executive Summary

This document proposes innovative approaches for allowing users to define relationships between entities using natural language instead of structured formats (JSON/API parameters). The feature leverages the existing LLM integration to provide an intuitive, conversational interface for knowledge graph customization.

---

## 1. CONCEPTUAL APPROACHES

### Approach 1: **Conversational Relationship Builder** 🗣️
**Concept**: Multi-turn dialogue where users describe relationships in natural language, and the system iteratively clarifies and refines them.

**How it works:**
- User: "Products are supplied by vendors"
- System: "I found 'products' and 'vendors' tables. Is this a one-to-many relationship? Should I create a SUPPLIES relationship?"
- User: "Yes, and add a property for supply_date"
- System: Creates relationship with confirmation

**Advantages:**
- Most intuitive for non-technical users
- Handles ambiguity through clarification
- Builds relationship incrementally
- Provides feedback at each step

**Challenges:**
- Requires multi-turn API design
- Session management complexity
- LLM token usage for context

---

### Approach 2: **Template-Based Natural Language** 📋
**Concept**: Predefined sentence templates that users fill in with natural language, reducing ambiguity.

**Templates:**
```
"[Entity A] [verb] [Entity B]"
"[Entity A] has [cardinality] [Entity B]"
"[Entity A] is [relationship_type] to [Entity B]"
"When [condition], [Entity A] [action] [Entity B]"
```

**Examples:**
- "Customers place Orders"
- "Orders contain Products"
- "Vendors supply Products with delivery_date"
- "When status=active, Users access Dashboards"

**Advantages:**
- Reduces parsing complexity
- Clear structure for LLM
- Easier validation
- Predictable output

**Challenges:**
- Less flexible than free-form text
- Users need to learn templates
- May not capture complex relationships

---

### Approach 3: **Hybrid Smart Parser** 🧠
**Concept**: Intelligent parser that handles multiple input formats and converts them to structured relationships.

**Input formats supported:**
- Natural language: "Products are sold by vendors"
- Semi-structured: "catalog.product_id → vendor.vendor_id (SOLD_BY)"
- Pseudo-SQL: "SELECT * FROM products JOIN vendors ON products.vendor_id = vendors.id"
- Business rules: "IF product.status='active' THEN product REFERENCES vendor"

**Advantages:**
- Flexible input options
- Accommodates different user preferences
- Gradual learning curve
- Powerful for advanced users

**Challenges:**
- Complex parsing logic
- Multiple validation paths
- Potential ambiguity

---

### Approach 4: **Interactive Visual Builder with NL Input** 🎨
**Concept**: Visual graph editor where users can drag entities and describe relationships in natural language.

**Workflow:**
1. User drags "Products" and "Vendors" onto canvas
2. Draws connection line between them
3. Types: "Products are supplied by vendors with delivery_date"
4. System parses and creates relationship
5. Visual feedback shows relationship properties

**Advantages:**
- Visual + textual = powerful combination
- Immediate visual feedback
- Reduces cognitive load
- Engaging UX

**Challenges:**
- Requires frontend development
- More complex implementation
- Browser compatibility

---

### Approach 5: **Batch Natural Language Definition** 📝
**Concept**: Users provide multiple relationship definitions in a single text block or file.

**Input format:**
```
Relationships:
- Products are supplied by Vendors
- Orders contain Products with quantity
- Customers place Orders with order_date
- Vendors have Locations
```

**Advantages:**
- Efficient for bulk operations
- Can be stored in version control
- Easy to review and modify
- Supports documentation

**Challenges:**
- Less interactive
- Harder to provide real-time feedback
- Requires careful parsing

---

## 2. USER EXPERIENCE EXAMPLES

### Example 1: Conversational Flow
```
User Input: "Tell me about the relationship between orders and products"

System Response:
"I found 'orders' and 'products' tables. Based on your description, 
I'm inferring a relationship. Let me clarify:

1. Is this a one-to-many (one order has many products)?
2. Should the relationship type be 'CONTAINS' or 'INCLUDES'?
3. Are there any properties like quantity or price?"

User Input: "One order has many products, use CONTAINS, add quantity"

System Response:
"Perfect! I've created:
- Source: orders
- Target: products
- Type: CONTAINS
- Properties: quantity
- Cardinality: 1:N

Confidence: 95%
Would you like to add more relationships?"
```

### Example 2: Template-Based Input
```
User Input: "Vendors supply Products with delivery_date and cost"

System Processing:
- Recognizes pattern: "[Entity A] [verb] [Entity B] with [properties]"
- Extracts: 
  - Source: Vendors
  - Verb: supply → SUPPLIES
  - Target: Products
  - Properties: delivery_date, cost
  - Cardinality: 1:N (inferred from verb)

System Response:
{
  "relationship": {
    "source": "vendors",
    "target": "products",
    "type": "SUPPLIES",
    "properties": ["delivery_date", "cost"],
    "cardinality": "1:N",
    "confidence": 0.92
  }
}
```

### Example 3: Batch Definition
```
User Input (Text File):
---
# E-Commerce Knowledge Graph Relationships

Products are sold by Vendors
- Cardinality: Many-to-One
- Properties: price, availability

Orders contain Products
- Cardinality: Many-to-Many
- Properties: quantity, line_total

Customers place Orders
- Cardinality: One-to-Many
- Properties: order_date, total_amount

Vendors have Locations
- Cardinality: One-to-Many
- Properties: warehouse_address
---

System Response:
✅ Successfully parsed 4 relationships
- Products → Vendors (SOLD_BY)
- Orders → Products (CONTAINS)
- Customers → Orders (PLACES)
- Vendors → Locations (HAS)

Confidence scores: 0.94, 0.91, 0.93, 0.89
Ready to add to knowledge graph?
```

---

## 3. TECHNICAL CONSIDERATIONS

### 3.1 LLM-Based Parsing Strategy

**Multi-Stage Processing:**

```
Stage 1: Entity Recognition
- Input: "Products are supplied by Vendors"
- Output: entities = ["Products", "Vendors"]
- Method: LLM + fuzzy matching against schema

Stage 2: Relationship Type Inference
- Input: entities + verb "supplied by"
- Output: relationship_type = "SUPPLIES"
- Method: LLM mapping to existing types + semantic similarity

Stage 3: Property Extraction
- Input: full sentence + schema context
- Output: properties = ["delivery_date", "cost"]
- Method: LLM + column name matching

Stage 4: Validation & Confidence Scoring
- Input: extracted relationship
- Output: confidence = 0.92, validation_status = "VALID"
- Method: LLM assessment + schema validation
```

### 3.2 Prompt Engineering

**Core Prompts Needed:**

1. **Entity Extraction Prompt**
   - Identify entities from natural language
   - Match against available tables/entities
   - Handle synonyms and abbreviations

2. **Relationship Type Mapping Prompt**
   - Map natural language verbs to relationship types
   - Consider existing types: FOREIGN_KEY, REFERENCES, BELONGS_TO, CROSS_SCHEMA_REFERENCE, SEMANTIC_REFERENCE, BUSINESS_LOGIC
   - Suggest new types if needed

3. **Property Extraction Prompt**
   - Identify properties mentioned in description
   - Match against available columns
   - Infer data types

4. **Validation Prompt**
   - Check relationship validity
   - Assess confidence level
   - Identify potential issues

### 3.3 Fallback Strategies

**When LLM is unavailable:**
- Use rule-based pattern matching
- Provide structured form as fallback
- Cache previous LLM results

**When confidence is low (<0.7):**
- Request user clarification
- Suggest multiple interpretations
- Provide manual override option

### 3.4 Performance Considerations

**Optimization techniques:**
- Cache entity/relationship mappings
- Batch process multiple relationships
- Use streaming for long responses
- Implement request queuing

**Token usage:**
- Estimate: 200-500 tokens per relationship
- Batch 10 relationships: ~3000 tokens
- Cost: ~$0.001-0.002 per batch

---

## 4. INTEGRATION POINTS

### 4.1 New API Endpoints

```
POST /api/v1/relationships/from-text
- Input: natural language description
- Output: parsed relationship with confidence
- Example: "Products are supplied by Vendors"

POST /api/v1/relationships/batch-from-text
- Input: multiple relationship descriptions
- Output: array of parsed relationships
- Example: text file with multiple definitions

POST /api/v1/relationships/interactive
- Input: initial description + clarification questions
- Output: refined relationship
- Multi-turn conversation

GET /api/v1/relationships/templates
- Output: available sentence templates
- Helps users understand format

POST /api/v1/relationships/validate
- Input: natural language description
- Output: validation result + suggestions
```

### 4.2 Integration with Existing Services

**MultiSchemaLLMService Enhancement:**
- Add `parse_relationship_from_text()` method
- Reuse existing prompt engineering patterns
- Leverage confidence scoring mechanism

**SchemaParser Enhancement:**
- Add `extract_relationships_from_text()` method
- Integrate with existing relationship detection
- Support both auto-detected and user-defined relationships

**Routes Enhancement:**
- Add new endpoints for NL relationship definition
- Integrate with existing KG generation flow
- Support relationship updates/modifications

### 4.3 Data Model Extensions

**New fields for relationships:**
```python
class GraphRelationship(BaseModel):
    # Existing fields
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any]
    
    # New fields
    natural_language_definition: Optional[str]  # Original NL input
    confidence_score: Optional[float]  # LLM confidence
    validation_status: Optional[str]  # VALID, LIKELY, UNCERTAIN
    user_defined: bool = False  # True if user-created
    created_by: Optional[str]  # User who defined it
    created_at: Optional[datetime]
```

---

## 5. USE CASES

### Use Case 1: **Business Analyst Defining Domain Relationships**
**Scenario**: Non-technical business analyst needs to define relationships for a new domain.

**Current Process**: 
- Requires JSON knowledge or API documentation
- Time-consuming and error-prone

**With NL Feature**:
- "Customers have multiple Accounts"
- "Accounts contain Transactions"
- "Transactions reference Products"
- System validates and creates relationships in minutes

**Value**: Democratizes KG creation, reduces dependency on technical staff

---

### Use Case 2: **Data Integration Specialist Mapping Schemas**
**Scenario**: Integrating two enterprise systems with complex relationships.

**Current Process**:
- Manual mapping document
- Structured API calls
- Validation and testing

**With NL Feature**:
```
"In the CRM system, Customers have Contacts
In the ERP system, Parties have Addresses
These should be linked as: CRM.Customers MAPS_TO ERP.Parties"
```

**Value**: Faster schema mapping, clearer documentation

---

### Use Case 3: **Knowledge Graph Refinement**
**Scenario**: User wants to add business logic relationships to auto-generated KG.

**Current Process**:
- Export JSON
- Manually edit
- Re-import

**With NL Feature**:
- "When product status is active, it should reference the active_vendors table"
- System adds BUSINESS_LOGIC relationship
- Immediate validation and feedback

**Value**: Iterative KG improvement without technical overhead

---

### Use Case 4: **Documentation-Driven Development**
**Scenario**: Team documents relationships in markdown, then generates KG.

**Current Process**:
- Write documentation
- Manually create relationships
- Keep in sync

**With NL Feature**:
```markdown
# E-Commerce KG Relationships

## Products
- Products are supplied by Vendors
- Products belong to Categories
- Products have Reviews from Customers

## Orders
- Orders contain Products
- Orders are placed by Customers
- Orders are fulfilled by Vendors
```

**Value**: Single source of truth, auto-generated KG

---

### Use Case 5: **Conversational KG Exploration**
**Scenario**: User exploring a complex KG and discovering new relationships.

**Current Process**:
- Query API
- Analyze results
- Manually define new relationships

**With NL Feature**:
- "I notice products and vendors have similar attributes"
- System: "Would you like to create a SIMILAR_TO relationship?"
- User: "Yes, but only for active products"
- System: Creates conditional relationship

**Value**: Interactive discovery and refinement

---

## 6. IMPLEMENTATION ROADMAP (Conceptual)

### Phase 1: Foundation (Week 1-2)
- [ ] Design LLM prompts for NL parsing
- [ ] Create data models for NL relationships
- [ ] Implement basic entity recognition

### Phase 2: Core Feature (Week 3-4)
- [ ] Implement relationship type inference
- [ ] Add property extraction
- [ ] Create validation logic

### Phase 3: API Integration (Week 5-6)
- [ ] Add new API endpoints
- [ ] Integrate with existing services
- [ ] Implement error handling

### Phase 4: Enhancement (Week 7-8)
- [ ] Add conversational interface
- [ ] Implement batch processing
- [ ] Add template system

### Phase 5: Polish (Week 9-10)
- [ ] Performance optimization
- [ ] Comprehensive testing
- [ ] Documentation

---

## 7. POTENTIAL CHALLENGES & SOLUTIONS

| Challenge | Solution |
|-----------|----------|
| Ambiguous entity names | Fuzzy matching + user confirmation |
| Complex relationships | Multi-turn clarification |
| LLM hallucination | Validation against schema + confidence scoring |
| Performance at scale | Caching + batch processing |
| User learning curve | Templates + examples + documentation |
| Cost of LLM calls | Caching + fallback to rules |

---

## 8. SUCCESS METRICS

- **Adoption**: % of users using NL feature
- **Accuracy**: Confidence score distribution
- **Efficiency**: Time to define relationships (before/after)
- **User Satisfaction**: NPS for NL feature
- **Cost**: LLM token usage per relationship
- **Reliability**: Validation success rate

---

## 9. RECOMMENDATIONS

**Recommended Approach**: **Hybrid Smart Parser** (Approach 3)
- Combines flexibility of natural language with structure of templates
- Leverages existing LLM infrastructure
- Provides multiple input options for different user preferences
- Scalable and maintainable

**Quick Win**: Start with **Template-Based** (Approach 2)
- Easier to implement
- Lower LLM token usage
- Good user experience
- Can evolve to full conversational later

---

## 10. NEXT STEPS

1. **Validate with users**: Get feedback on proposed approaches
2. **Design prompts**: Create detailed LLM prompts for each parsing stage
3. **Prototype**: Build MVP with template-based approach
4. **Test**: Validate with real schemas and relationships
5. **Iterate**: Refine based on feedback
6. **Scale**: Add conversational and batch features

---

**Document Status**: Brainstorming Complete ✅
**Ready for**: Design & Implementation Planning

