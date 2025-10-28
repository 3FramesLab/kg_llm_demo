# LLM Prompts Reference Guide

This document catalogs all LLM (Large Language Model) prompts used throughout the DQ-POC project. Each prompt is documented with its purpose, location, system message, and structure.

## Table of Contents

1. [Single Schema LLM Service Prompts](#single-schema-llm-service-prompts)
2. [Multi-Schema LLM Service Prompts](#multi-schema-llm-service-prompts)
3. [Natural Language Relationship Parser Prompts](#natural-language-relationship-parser-prompts)
4. [Prompt Configuration](#prompt-configuration)

---

## Single Schema LLM Service Prompts

**File:** `kg_builder/services/llm_service.py`

These prompts analyze individual database schemas to extract entities, relationships, and provide comprehensive analysis.

### 1. Entity Extraction Prompt

**Method:** `extract_entities()`
**Line:** 59-81
**Purpose:** Extract key entities with their business purposes from a database schema

**System Message:**
```
You are a database schema analyst. Extract entities and their business purposes from database schemas. Always return valid JSON.
```

**User Prompt Template:**
```
Analyze this database schema and extract key entities with their business purposes.

Schema:
{schema_str}

For each table/entity, provide:
1. Entity name
2. Business purpose (what it represents)
3. Key attributes (important columns)
4. Entity type (e.g., "Master Data", "Transaction", "Reference")

Return as JSON with this structure:
{
    "entities": [
        {
            "name": "entity_name",
            "purpose": "business purpose",
            "type": "entity_type",
            "key_attributes": ["attr1", "attr2"],
            "description": "detailed description"
        }
    ]
}
```

**Configuration:**
- Model: Configurable via `OPENAI_MODEL` (default: gpt-3.5-turbo)
- Temperature: Configurable via `OPENAI_TEMPERATURE` (default: 0.7)
- Max Tokens: Configurable via `OPENAI_MAX_TOKENS` (default: 2000)

**Expected Output:**
```json
{
  "entities": [
    {
      "name": "catalog",
      "purpose": "Stores product catalog information",
      "type": "Master Data",
      "key_attributes": ["product_id", "vendor_uid", "item_name"],
      "description": "Central repository for all product information including pricing and vendor relationships"
    }
  ]
}
```

---

### 2. Relationship Extraction Prompt

**Method:** `extract_relationships()`
**Line:** 132-156
**Purpose:** Extract all relationships between entities from a database schema

**System Message:**
```
You are a database schema analyst. Extract relationships between entities from database schemas. Always return valid JSON.
```

**User Prompt Template:**
```
Analyze this database schema and extract all relationships between entities.

Schema:
{schema_str}

For each relationship, identify:
1. Source entity
2. Target entity
3. Relationship type (e.g., "HAS", "BELONGS_TO", "REFERENCES", "CONTAINS")
4. Cardinality (1:1, 1:N, N:N)
5. Business meaning

Return as JSON with this structure:
{
    "relationships": [
        {
            "source": "source_entity",
            "target": "target_entity",
            "type": "relationship_type",
            "cardinality": "1:N",
            "description": "business meaning of relationship",
            "foreign_key": "column_name or null"
        }
    ]
}
```

**Configuration:**
- Model: Configurable via `OPENAI_MODEL`
- Temperature: Configurable via `OPENAI_TEMPERATURE`
- Max Tokens: Configurable via `OPENAI_MAX_TOKENS`

**Expected Output:**
```json
{
  "relationships": [
    {
      "source": "orders",
      "target": "catalog",
      "type": "REFERENCES",
      "cardinality": "N:1",
      "description": "Each order references a product from the catalog",
      "foreign_key": "product_id"
    }
  ]
}
```

---

### 3. Schema Analysis Prompt

**Method:** `analyze_schema()`
**Line:** 207-229
**Purpose:** Provide comprehensive analysis of database schema including domain, patterns, and business logic

**System Message:**
```
You are a database architect. Analyze database schemas and provide insights about their structure, purpose, and business logic. Always return valid JSON.
```

**User Prompt Template:**
```
Provide a comprehensive analysis of this database schema.

Schema:
{schema_str}

Analyze:
1. Overall purpose and domain
2. Data model patterns
3. Key entities and their roles
4. Data relationships and dependencies
5. Potential business logic
6. Data quality considerations

Return as JSON with this structure:
{
    "domain": "business domain",
    "purpose": "overall purpose",
    "patterns": ["pattern1", "pattern2"],
    "key_entities": ["entity1", "entity2"],
    "data_flow": "description of data flow",
    "business_logic": "inferred business logic",
    "quality_notes": "data quality considerations"
}
```

**Configuration:**
- Model: Configurable via `OPENAI_MODEL`
- Temperature: Configurable via `OPENAI_TEMPERATURE`
- Max Tokens: Configurable via `OPENAI_MAX_TOKENS`

**Expected Output:**
```json
{
  "domain": "Order Management and Product Catalog",
  "purpose": "Manage product listings, vendor relationships, and order processing",
  "patterns": ["Master-Detail", "Reference Data", "Foreign Key Constraints"],
  "key_entities": ["catalog", "orders", "vendors"],
  "data_flow": "Products are added to catalog by vendors, orders reference catalog items",
  "business_logic": "Vendor supplies products which are ordered by customers",
  "quality_notes": "Requires referential integrity checks, vendor_uid validation needed"
}
```

---

## Multi-Schema LLM Service Prompts

**File:** `kg_builder/services/multi_schema_llm_service.py`

These prompts analyze relationships across multiple database schemas and generate reconciliation rules.

### 4. Relationship Inference Prompt

**Method:** `infer_relationships()` → `_build_inference_prompt()`
**Line:** 260-289
**Purpose:** Infer additional relationships beyond pattern matching based on semantic meaning

**System Message:**
```
You are an expert database analyst. Analyze database schemas and infer relationships between tables across different schemas based on semantic meaning and naming conventions.
```

**User Prompt Template:**
```
Analyze these database schemas and already-detected relationships.
Infer additional relationships that might exist based on semantic meaning and business logic.

SCHEMAS:
{schemas_str}

ALREADY DETECTED RELATIONSHIPS:
{detected_str}

For each inferred relationship, provide:
1. source_table
2. target_table
3. relationship_type (e.g., "SEMANTIC_REFERENCE", "BUSINESS_LOGIC")
4. reasoning (why this relationship likely exists)
5. confidence (0.0-1.0)

Return as JSON array with this structure:
{
    "inferred_relationships": [
        {
            "source_table": "table1",
            "target_table": "table2",
            "relationship_type": "SEMANTIC_REFERENCE",
            "reasoning": "explanation",
            "confidence": 0.85
        }
    ]
}

Only include relationships with confidence >= 0.7.
```

**Configuration:**
- Model: Configurable via `OPENAI_MODEL`
- Temperature: Configurable via `OPENAI_TEMPERATURE`
- Max Tokens: Configurable via `OPENAI_MAX_TOKENS`

**Expected Output:**
```json
{
  "inferred_relationships": [
    {
      "source_table": "catalog",
      "target_table": "inspection_results",
      "relationship_type": "SEMANTIC_REFERENCE",
      "reasoning": "Products in catalog are likely inspected, creating inspection results",
      "confidence": 0.82
    }
  ]
}
```

---

### 5. Relationship Enhancement Prompt

**Method:** `enhance_relationships()` → `_build_enhancement_prompt()`
**Line:** 291-322
**Purpose:** Generate meaningful business descriptions for detected relationships

**System Message:**
```
You are an expert database analyst. Generate clear, concise business descriptions for database relationships.
```

**User Prompt Template:**
```
Generate clear business descriptions for these database relationships.

SCHEMAS:
{schemas_str}

RELATIONSHIPS:
{rels_str}

For each relationship, provide a clear, concise business description explaining:
- What the relationship represents
- Why it exists
- How data flows through it

Return as JSON array with this structure:
{
    "enhanced_relationships": [
        {
            "source_table": "table1",
            "target_table": "table2",
            "description": "Clear business description of the relationship"
        }
    ]
}
```

**Configuration:**
- Model: Configurable via `OPENAI_MODEL`
- Temperature: Configurable via `OPENAI_TEMPERATURE`
- Max Tokens: Configurable via `OPENAI_MAX_TOKENS`

**Expected Output:**
```json
{
  "enhanced_relationships": [
    {
      "source_table": "orders",
      "target_table": "catalog",
      "description": "Orders reference products from the catalog, establishing which items were purchased"
    }
  ]
}
```

---

### 6. Relationship Scoring Prompt

**Method:** `score_relationships()` → `_build_scoring_prompt()`
**Line:** 324-357
**Purpose:** Assess confidence and validity of detected relationships

**System Message:**
```
You are an expert database analyst. Assess the confidence and validity of database relationships.
```

**User Prompt Template:**
```
Assess the confidence and validity of these database relationships.

SCHEMAS:
{schemas_str}

RELATIONSHIPS:
{rels_str}

For each relationship, provide:
1. confidence (0.0-1.0) - How confident you are this relationship is valid
2. reasoning - Why you assigned this confidence level
3. validation_status - "VALID", "LIKELY", "UNCERTAIN", or "QUESTIONABLE"

Return as JSON array with this structure:
{
    "scored_relationships": [
        {
            "source_table": "table1",
            "target_table": "table2",
            "confidence": 0.95,
            "reasoning": "Strong naming pattern and semantic alignment",
            "validation_status": "VALID"
        }
    ]
}
```

**Configuration:**
- Model: Configurable via `OPENAI_MODEL`
- Temperature: Configurable via `OPENAI_TEMPERATURE`
- Max Tokens: Configurable via `OPENAI_MAX_TOKENS`

**Expected Output:**
```json
{
  "scored_relationships": [
    {
      "source_table": "catalog",
      "target_table": "vendors",
      "confidence": 0.95,
      "reasoning": "Strong naming pattern (vendor_uid) and clear foreign key relationship",
      "validation_status": "VALID"
    }
  ]
}
```

---

### 7. Reconciliation Rules Generation Prompt

**Method:** `generate_reconciliation_rules()` → `_build_reconciliation_rules_prompt()`
**Line:** 428-482
**Purpose:** Generate reconciliation rules for matching data across different schemas

**System Message:**
```
You are an expert data integration specialist. Generate reconciliation rules for matching data across different database schemas.
```

**User Prompt Template:**
```
Given these cross-schema relationships and schemas, generate reconciliation rules
that would allow matching records between these schemas.

SCHEMAS:
{schemas_str}

RELATIONSHIPS:
{relationships_str}

For each rule, provide:
1. rule_name: Descriptive name for the rule
2. source_schema: Name of the source schema
3. source_table: Source table name
4. source_columns: Array of source column names involved in matching
5. target_schema: Name of the target schema
6. target_table: Target table name
7. target_columns: Array of target column names involved in matching
8. match_type: One of "exact", "fuzzy", "composite", "transformation", "semantic"
9. transformation: SQL or Python code for data matching (if needed, null otherwise)
10. confidence: Confidence score (0.0-1.0) for this rule
11. reasoning: Why this rule would work
12. validation_status: "VALID", "LIKELY", or "UNCERTAIN"
13. example_match: Sample matching scenario

Return JSON:
{
  "rules": [
    {
      "rule_name": "Vendor_UID_Match",
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
      "validation_status": "VALID",
      "example_match": "vendor_uid='VND123' matches supplier_id='VND123'"
    }
  ]
}

Only generate rules with confidence >= 0.7. Focus on cross-schema relationships.
```

**Configuration:**
- Model: Configurable via `OPENAI_MODEL`
- Temperature: Configurable via `OPENAI_TEMPERATURE`
- Max Tokens: Configurable via `OPENAI_MAX_TOKENS`

**Expected Output:**
```json
{
  "rules": [
    {
      "rule_name": "Product_ID_Match",
      "source_schema": "orderMgmt-catalog",
      "source_table": "catalog",
      "source_columns": ["product_id"],
      "target_schema": "qinspect-designcode",
      "target_table": "designcode",
      "target_columns": ["item_id"],
      "match_type": "semantic",
      "transformation": null,
      "confidence": 0.85,
      "reasoning": "Product IDs in catalog likely correspond to item IDs in design codes",
      "validation_status": "LIKELY",
      "example_match": "product_id='P12345' matches item_id='P12345'"
    }
  ]
}
```

---

## Natural Language Relationship Parser Prompts

**File:** `kg_builder/services/nl_relationship_parser.py`

These prompts parse user-provided natural language relationship definitions.

### 8. Natural Language Parsing Prompt

**Method:** `_parse_nl_with_llm()` → `_build_nl_parsing_prompt()`
**Line:** 310-336
**Purpose:** Parse natural language relationship definitions and extract structured information

**System Message:**
```
You are an expert data modeler. Parse natural language relationship definitions and extract structured information.
```

**User Prompt Template:**
```
Parse this natural language relationship definition:

"{text}"

Available schemas and tables:
{schemas_str}

Extract and return as JSON array with this structure:
{
    "relationships": [
        {
            "source_table": "table_name",
            "target_table": "table_name",
            "relationship_type": "RELATIONSHIP_TYPE",
            "properties": ["prop1", "prop2"],
            "cardinality": "1:N",
            "confidence": 0.85,
            "reasoning": "Why this relationship makes sense"
        }
    ]
}

Return ONLY valid JSON, no other text.
```

**Configuration:**
- Model: Configurable via `OPENAI_MODEL`
- Temperature: Configurable via `OPENAI_TEMPERATURE`
- Max Tokens: Configurable via `OPENAI_MAX_TOKENS`

**Example Input:**
```
"Products are supplied by Vendors"
```

**Expected Output:**
```json
{
  "relationships": [
    {
      "source_table": "vendors",
      "target_table": "catalog",
      "relationship_type": "SUPPLIES",
      "properties": ["vendor_uid"],
      "cardinality": "1:N",
      "confidence": 0.88,
      "reasoning": "Vendors supply multiple products, creating a one-to-many relationship"
    }
  ]
}
```

---

### 9. Business Rules Parsing Prompt

**Method:** `_parse_business_rules_with_llm()` → `_build_business_rules_prompt()`
**Line:** 338-364
**Purpose:** Parse business rules and extract relationship definitions

**System Message:**
```
You are an expert data modeler. Parse business rules and extract relationships.
```

**User Prompt Template:**
```
Parse this business rule and extract relationships:

"{text}"

Available schemas and tables:
{schemas_str}

Extract and return as JSON array with this structure:
{
    "relationships": [
        {
            "source_table": "table_name",
            "target_table": "table_name",
            "relationship_type": "RELATIONSHIP_TYPE",
            "properties": [],
            "cardinality": "1:N",
            "confidence": 0.80,
            "reasoning": "How this rule creates a relationship"
        }
    ]
}

Return ONLY valid JSON, no other text.
```

**Configuration:**
- Model: Configurable via `OPENAI_MODEL`
- Temperature: Configurable via `OPENAI_TEMPERATURE`
- Max Tokens: Configurable via `OPENAI_MAX_TOKENS`

**Example Input:**
```
"IF product.status='active' THEN it must have a vendor assigned"
```

**Expected Output:**
```json
{
  "relationships": [
    {
      "source_table": "catalog",
      "target_table": "vendors",
      "relationship_type": "REQUIRES",
      "properties": ["vendor_uid"],
      "cardinality": "N:1",
      "confidence": 0.80,
      "reasoning": "Business rule requires active products to have vendor relationships"
    }
  ]
}
```

---

## Prompt Configuration

All LLM prompts in the project use centralized configuration from the `.env` file and `kg_builder/config.py`.

### Configuration Parameters

**File:** `kg_builder/config.py`

```python
# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))

# Feature Flags
ENABLE_LLM_EXTRACTION = os.getenv("ENABLE_LLM_EXTRACTION", "true").lower() == "true"
ENABLE_LLM_ANALYSIS = os.getenv("ENABLE_LLM_ANALYSIS", "true").lower() == "true"
```

### Environment Variables

Add these to your `.env` file:

```env
# Required
OPENAI_API_KEY=sk-your-api-key-here

# Optional (with defaults)
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# Feature Flags
ENABLE_LLM_EXTRACTION=true
ENABLE_LLM_ANALYSIS=true
```

### Model Options

The system supports any OpenAI model via configuration:

| Model | Use Case | Tokens | Cost |
|-------|----------|--------|------|
| `gpt-3.5-turbo` | Default, fast, cost-effective | 4K | Low |
| `gpt-3.5-turbo-16k` | Larger schemas | 16K | Medium |
| `gpt-4` | Higher accuracy | 8K | High |
| `gpt-4-turbo` | Best accuracy, larger context | 128K | Highest |
| `gpt-4o` | Optimized performance | 128K | Medium-High |

### Temperature Settings

- **0.0-0.3**: Deterministic, consistent outputs (recommended for schema analysis)
- **0.4-0.7**: Balanced creativity and consistency (default)
- **0.8-1.0**: More creative, varied outputs (for exploration)

---

## Prompt Design Patterns

All prompts in the project follow these best practices:

### 1. Clear Role Definition
Every prompt starts with a clear system message defining the LLM's role:
```
"You are an expert [role]. [What they do]."
```

### 2. Structured Output Requirements
All prompts explicitly request JSON output with defined structure to ensure parsability.

### 3. Context Provision
Prompts include relevant context (schemas, existing relationships) to ground the LLM's responses.

### 4. Explicit Instructions
Each prompt lists numbered requirements or analysis points to guide the LLM.

### 5. Confidence Scoring
Most prompts request confidence scores (0.0-1.0) to enable filtering and prioritization.

### 6. Reasoning Capture
Prompts ask for reasoning/explanation to make LLM decisions transparent and auditable.

### 7. Validation Constraints
Many prompts include constraints (e.g., "Only include relationships with confidence >= 0.7").

---

## Prompt Usage Examples

### Example 1: Entity Extraction

```python
from kg_builder.services.llm_service import get_llm_service

llm_service = get_llm_service()

schema = {
    "tables": {
        "catalog": {
            "columns": ["product_id", "product_name", "vendor_uid"]
        }
    }
}

result = llm_service.extract_entities(schema)
print(result)
# Output: {"entities": [...], "descriptions": {...}}
```

### Example 2: Relationship Inference

```python
from kg_builder.services.multi_schema_llm_service import get_multi_schema_llm_service

llm_service = get_multi_schema_llm_service()

schemas_info = {
    "orderMgmt": {...},
    "vendorDB": {...}
}

detected_rels = [...]  # Already detected relationships

inferred = llm_service.infer_relationships(schemas_info, detected_rels)
print(inferred)
```

### Example 3: Natural Language Parsing

```python
from kg_builder.services.nl_relationship_parser import get_nl_relationship_parser

parser = get_nl_relationship_parser()

schemas_info = {...}
input_text = "Products are supplied by Vendors"

relationships = parser.parse(input_text, schemas_info, use_llm=True)
print(relationships)
```

---

## Error Handling

All LLM services include robust error handling:

### 1. API Errors
```python
except APIError as e:
    logger.error(f"OpenAI API error: {e}")
    return {"entities": [], "error": str(e)}
```

### 2. JSON Parsing Errors
```python
except json.JSONDecodeError as e:
    logger.error(f"Failed to parse LLM response as JSON: {e}")
    return {"entities": [], "error": "Invalid JSON response"}
```

### 3. Fallback Behavior
- LLM services gracefully degrade when API key is missing
- Rule-based parsing is available when LLM is disabled
- Pattern-based rules are generated even if LLM enhancement fails

---

## Performance Considerations

### Token Usage

Typical token consumption per prompt type:

| Prompt Type | Input Tokens | Output Tokens | Total |
|-------------|--------------|---------------|-------|
| Entity Extraction | 500-2000 | 300-800 | 800-2800 |
| Relationship Extraction | 500-2000 | 200-600 | 700-2600 |
| Schema Analysis | 500-2000 | 400-1000 | 900-3000 |
| Relationship Inference | 1000-3000 | 300-800 | 1300-3800 |
| Reconciliation Rules | 1500-4000 | 500-1500 | 2000-5500 |
| NL Parsing | 200-800 | 100-300 | 300-1100 |

### Cost Estimation

For `gpt-3.5-turbo` ($0.50 per 1M input tokens, $1.50 per 1M output tokens):

- **Single Schema Analysis**: ~$0.002-0.005 per schema
- **Multi-Schema Reconciliation**: ~$0.005-0.015 per ruleset
- **NL Relationship Parsing**: ~$0.0005-0.002 per definition

### Optimization Tips

1. **Batch Operations**: Process multiple schemas in one call when possible
2. **Cache Results**: Store LLM responses to avoid repeated API calls
3. **Filter Early**: Use pattern-based rules first, LLM for complex cases only
4. **Adjust max_tokens**: Reduce for simpler schemas to save costs
5. **Use Cheaper Models**: gpt-3.5-turbo works well for most cases

---

## Testing Prompts

The project includes test files that exercise all prompts:

### Test Files

- `tests/test_kg_integration.py` - Tests entity/relationship extraction
- `tests/test_nl_relationship_parser.py` - Tests natural language parsing
- `tests/test_nl_integration.py` - Tests end-to-end NL workflows

### Running Tests

```bash
# Test all LLM functionality
pytest tests/test_kg_integration.py -v

# Test NL parsing specifically
pytest tests/test_nl_relationship_parser.py -v

# Run with API key
export OPENAI_API_KEY=sk-your-key
pytest tests/ -v
```

---

## Prompt Versioning

As the project evolves, prompts may be updated. Track changes:

### Version History

| Version | Date | Changes | Prompt(s) Affected |
|---------|------|---------|-------------------|
| 1.0 | 2024-01 | Initial implementation | All prompts |
| 1.1 | 2024-03 | Added confidence filtering | Relationship Inference |
| 1.2 | 2024-06 | Enhanced reconciliation rules | Reconciliation Rules |
| 1.3 | 2024-10 | Added NL parsing | NL Parsing, Business Rules |

---

## Summary

The DQ-POC project uses **9 distinct LLM prompts** across 3 service files:

1. **Single Schema Analysis** (3 prompts):
   - Entity Extraction
   - Relationship Extraction
   - Schema Analysis

2. **Multi-Schema Analysis** (4 prompts):
   - Relationship Inference
   - Relationship Enhancement
   - Relationship Scoring
   - Reconciliation Rules Generation

3. **Natural Language Processing** (2 prompts):
   - Natural Language Parsing
   - Business Rules Parsing

All prompts:
- Use consistent JSON output formats
- Include confidence scoring
- Provide reasoning for transparency
- Support configurable models and parameters
- Include robust error handling

For questions or improvements to prompts, see:
- Project documentation: `docs/LLM_INTEGRATION.md`
- Configuration guide: `docs/QUICKSTART.md`
- API examples: `docs/API_EXAMPLES.md`
