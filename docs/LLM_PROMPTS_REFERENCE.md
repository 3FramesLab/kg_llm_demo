# LLM Prompts Reference

This document shows all the prompts used by the Knowledge Graph Builder for intelligent schema analysis.

## 1. Entity Extraction Prompt

### System Message
```
You are a database schema analyst. Extract entities and their business purposes 
from database schemas. Always return valid JSON.
```

### User Prompt
```
Analyze this database schema and extract key entities with their business purposes.

Schema:
{schema_json}

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

### Expected Output Example
```json
{
    "entities": [
        {
            "name": "catalog",
            "purpose": "Stores product catalog information",
            "type": "Master Data",
            "key_attributes": ["id", "product_name", "vendor_uid", "price"],
            "description": "Central repository for all product information including pricing, vendor details, and inventory status"
        },
        {
            "name": "vendor",
            "purpose": "Stores vendor/supplier information",
            "type": "Master Data",
            "key_attributes": ["vendor_uid", "vendor_name", "contact_info"],
            "description": "Reference data for vendors who supply products"
        }
    ]
}
```

---

## 2. Relationship Extraction Prompt

### System Message
```
You are a database schema analyst. Extract relationships between entities 
from database schemas. Always return valid JSON.
```

### User Prompt
```
Analyze this database schema and extract all relationships between entities.

Schema:
{schema_json}

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

### Expected Output Example
```json
{
    "relationships": [
        {
            "source": "catalog",
            "target": "vendor",
            "type": "HAS_VENDOR",
            "cardinality": "N:1",
            "description": "Each product in catalog belongs to exactly one vendor",
            "foreign_key": "vendor_uid"
        },
        {
            "source": "catalog",
            "target": "pricing",
            "type": "HAS_PRICING",
            "cardinality": "1:N",
            "description": "Each product can have multiple pricing tiers",
            "foreign_key": "product_id"
        }
    ]
}
```

---

## 3. Schema Analysis Prompt

### System Message
```
You are a database architect. Analyze database schemas and provide insights 
about their structure, purpose, and business logic. Always return valid JSON.
```

### User Prompt
```
Provide a comprehensive analysis of this database schema.

Schema:
{schema_json}

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

### Expected Output Example
```json
{
    "domain": "E-commerce / Order Management",
    "purpose": "Manages product catalog, inventory, and vendor relationships for an e-commerce platform",
    "patterns": [
        "Master-Detail (Catalog-Pricing)",
        "Temporal Data (timestamps)",
        "Hierarchical (Vendor-Product)",
        "Reference Data (Vendor, Category)"
    ],
    "key_entities": [
        "catalog - central product repository",
        "vendor - supplier information",
        "pricing - product pricing tiers",
        "inventory - stock levels"
    ],
    "data_flow": "Vendors supply products → Products added to catalog → Pricing defined → Inventory tracked → Orders fulfilled",
    "business_logic": "Products are organized by vendor with multiple pricing tiers. Inventory is tracked per product. Timestamps track all changes for audit purposes.",
    "quality_notes": "Nullable fields indicate optional attributes. Timestamps on all tables enable audit trails. Foreign keys ensure referential integrity. Consider adding constraints for data validation."
}
```

---

## Prompt Engineering Tips

### 1. Schema Formatting
- Schemas are provided as JSON for clarity
- Include table names, column names, and types
- Include foreign key information when available

### 2. JSON Structure
- Always request JSON output for consistency
- Provide example structure in the prompt
- This ensures parseable responses

### 3. System Messages
- Set clear role (database analyst, architect)
- Emphasize JSON output requirement
- This improves response quality

### 4. Context
- Include schema context in the prompt
- Provide specific instructions for each field
- This reduces ambiguity

## Customizing Prompts

You can customize prompts by editing `kg_builder/services/llm_service.py`:

```python
# Example: Add more specific instructions
prompt = f"""Analyze this database schema and extract key entities...

Additional Requirements:
1. Focus on business entities, not technical tables
2. Identify temporal patterns
3. Flag potential data quality issues

Schema:
{schema_str}
..."""
```

## Prompt Performance Tips

1. **Be Specific**: More specific prompts yield better results
2. **Provide Examples**: Show expected output format
3. **Use Clear Language**: Avoid ambiguous terms
4. **Set Context**: Explain the domain/purpose
5. **Request JSON**: Always request structured output

## Token Usage

Typical token usage per operation:

| Operation | Input Tokens | Output Tokens | Total |
|-----------|-------------|---------------|-------|
| Entity Extraction | 100-300 | 100-200 | 200-500 |
| Relationship Extraction | 100-300 | 150-300 | 250-600 |
| Schema Analysis | 100-300 | 200-400 | 300-700 |

## Cost Optimization

1. **Batch Operations**: Process multiple schemas together
2. **Cache Results**: Store extraction results
3. **Use gpt-3.5-turbo**: Most cost-effective model
4. **Limit Max Tokens**: Set appropriate limits
5. **Monitor Usage**: Track API calls and costs

## Troubleshooting Prompts

### Issue: Invalid JSON Response
**Solution**: Increase `OPENAI_MAX_TOKENS` or simplify the schema

### Issue: Missing Fields
**Solution**: Add explicit field requirements to the prompt

### Issue: Inconsistent Results
**Solution**: Lower `OPENAI_TEMPERATURE` for consistency

### Issue: Timeout
**Solution**: Reduce schema size or increase timeout

---

**For more information, see [LLM_INTEGRATION.md](LLM_INTEGRATION.md)**

