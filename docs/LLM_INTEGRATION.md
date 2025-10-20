# LLM Integration Guide - OpenAI

## Overview

The Knowledge Graph Builder now includes **intelligent entity and relationship extraction** powered by **OpenAI's GPT models**. This allows the system to understand database schemas at a semantic level and extract meaningful business entities and relationships.

## Features

### 1. **Intelligent Entity Extraction**
- Analyzes database schemas to identify key business entities
- Extracts entity purposes and business meanings
- Identifies entity types (Master Data, Transaction, Reference, etc.)
- Extracts key attributes for each entity
- Provides detailed descriptions

### 2. **Intelligent Relationship Extraction**
- Identifies relationships between entities
- Determines relationship types (HAS, BELONGS_TO, REFERENCES, CONTAINS, etc.)
- Infers cardinality (1:1, 1:N, N:N)
- Provides business meaning for each relationship
- Maps to foreign keys when applicable

### 3. **Comprehensive Schema Analysis**
- Determines overall business domain
- Identifies data model patterns
- Analyzes data flow
- Infers business logic
- Provides data quality considerations

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key

### 3. Configure Environment
Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000
ENABLE_LLM_EXTRACTION=true
ENABLE_LLM_ANALYSIS=true
```

Or set environment variables:
```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

### 4. Start the Server
```bash
python -m kg_builder.main
```

## API Endpoints

### 1. LLM Extract Entities & Relationships
```
POST /api/v1/llm/extract/{schema_name}
```

**Description**: Use LLM to intelligently extract entities and relationships from a schema.

**Parameters**:
- `schema_name` (path): Name of the schema (e.g., "orderMgmt-catalog")

**Response**:
```json
{
  "success": true,
  "entities": [
    {
      "name": "catalog",
      "purpose": "Stores product catalog information",
      "type": "Master Data",
      "key_attributes": ["id", "product_name", "vendor_uid"],
      "description": "Central repository for all product information including pricing and vendor details"
    }
  ],
  "relationships": [
    {
      "source": "catalog",
      "target": "vendor",
      "type": "HAS_VENDOR",
      "cardinality": "N:1",
      "description": "Each product belongs to a vendor",
      "foreign_key": "vendor_uid"
    }
  ]
}
```

### 2. LLM Analyze Schema
```
POST /api/v1/llm/analyze/{schema_name}
```

**Description**: Get comprehensive schema analysis including domain, purpose, patterns, and business logic.

**Parameters**:
- `schema_name` (path): Name of the schema

**Response**:
```json
{
  "success": true,
  "domain": "E-commerce / Order Management",
  "purpose": "Manages product catalog, inventory, and vendor relationships",
  "patterns": ["Master-Detail", "Temporal Data", "Hierarchical"],
  "key_entities": ["catalog", "vendor", "pricing"],
  "data_flow": "Products flow from vendors through catalog to orders",
  "business_logic": "Products are organized by vendor with pricing tiers",
  "quality_notes": "Timestamps track data changes; nullable fields indicate optional attributes"
}
```

### 3. LLM Status
```
GET /api/v1/llm/status
```

**Description**: Check if LLM service is enabled and get configuration.

**Response**:
```json
{
  "enabled": true,
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

## Usage Examples

### Python Example
```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Check LLM status
response = requests.get(f"{BASE_URL}/llm/status")
print("LLM Status:", response.json())

# Extract entities and relationships
response = requests.post(
    f"{BASE_URL}/llm/extract/orderMgmt-catalog"
)
extraction = response.json()
print(f"Extracted {len(extraction['entities'])} entities")
print(f"Extracted {len(extraction['relationships'])} relationships")

# Analyze schema
response = requests.post(
    f"{BASE_URL}/llm/analyze/orderMgmt-catalog"
)
analysis = response.json()
print(f"Domain: {analysis['domain']}")
print(f"Purpose: {analysis['purpose']}")
```

### Curl Examples
```bash
# Check LLM status
curl http://localhost:8000/api/v1/llm/status

# Extract entities and relationships
curl -X POST http://localhost:8000/api/v1/llm/extract/orderMgmt-catalog

# Analyze schema
curl -X POST http://localhost:8000/api/v1/llm/analyze/orderMgmt-catalog
```

## Prompts Used

### Entity Extraction Prompt
The system uses this prompt to extract entities:
```
Analyze this database schema and extract key entities with their business purposes.
For each table/entity, provide:
1. Entity name
2. Business purpose (what it represents)
3. Key attributes (important columns)
4. Entity type (e.g., "Master Data", "Transaction", "Reference")
```

### Relationship Extraction Prompt
The system uses this prompt to extract relationships:
```
Analyze this database schema and extract all relationships between entities.
For each relationship, identify:
1. Source entity
2. Target entity
3. Relationship type (e.g., "HAS", "BELONGS_TO", "REFERENCES", "CONTAINS")
4. Cardinality (1:1, 1:N, N:N)
5. Business meaning
```

### Schema Analysis Prompt
The system uses this prompt for comprehensive analysis:
```
Provide a comprehensive analysis of this database schema.
Analyze:
1. Overall purpose and domain
2. Data model patterns
3. Key entities and their roles
4. Data relationships and dependencies
5. Potential business logic
6. Data quality considerations
```

## Configuration Options

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: "gpt-3.5-turbo")
- `OPENAI_TEMPERATURE`: Creativity level 0-2 (default: 0.7)
- `OPENAI_MAX_TOKENS`: Max response length (default: 2000)
- `ENABLE_LLM_EXTRACTION`: Enable extraction features (default: true)
- `ENABLE_LLM_ANALYSIS`: Enable analysis features (default: true)

### Model Options
- `gpt-3.5-turbo` - Fast and cost-effective (recommended)
- `gpt-4` - More capable but slower and more expensive
- `gpt-4-turbo-preview` - Balance of capability and speed

## Cost Considerations

### Pricing (as of 2024)
- **gpt-3.5-turbo**: ~$0.0005 per 1K tokens
- **gpt-4**: ~$0.03 per 1K tokens
- **gpt-4-turbo**: ~$0.01 per 1K tokens

### Typical Costs
- Entity extraction: ~100-500 tokens (~$0.0001-0.0005)
- Relationship extraction: ~200-800 tokens (~$0.0001-0.0008)
- Schema analysis: ~300-1000 tokens (~$0.0002-0.0010)

## Troubleshooting

### LLM Service Not Enabled
**Error**: "LLM service is not enabled"
**Solution**: Set `OPENAI_API_KEY` environment variable

### Invalid API Key
**Error**: "Invalid API key"
**Solution**: Verify your API key at https://platform.openai.com/api-keys

### Rate Limiting
**Error**: "Rate limit exceeded"
**Solution**: Wait a moment and retry, or upgrade your OpenAI plan

### Invalid JSON Response
**Error**: "Failed to parse LLM response as JSON"
**Solution**: Try again or increase `OPENAI_MAX_TOKENS`

### Timeout
**Error**: "Request timeout"
**Solution**: Increase `OPENAI_MAX_TOKENS` or use a simpler schema

## Best Practices

1. **Use gpt-3.5-turbo for cost efficiency** - Good balance of quality and cost
2. **Set appropriate temperature** - 0.7 is good for analysis, 0.3 for consistency
3. **Monitor API usage** - Check your OpenAI dashboard regularly
4. **Cache results** - Store extraction results to avoid repeated API calls
5. **Test with small schemas first** - Verify behavior before processing large schemas
6. **Handle errors gracefully** - Always check for errors in responses

## Integration with Knowledge Graphs

The LLM extraction results can be used to enhance knowledge graph generation:

```python
# 1. Extract using LLM
extraction = requests.post(
    f"{BASE_URL}/llm/extract/orderMgmt-catalog"
).json()

# 2. Use extracted entities to create richer nodes
for entity in extraction['entities']:
    # Create node with LLM-provided description
    node = {
        "id": entity['name'],
        "label": entity['name'],
        "properties": {
            "purpose": entity['purpose'],
            "type": entity['type'],
            "description": entity['description']
        }
    }

# 3. Use extracted relationships for better graph structure
for rel in extraction['relationships']:
    # Create relationship with business meaning
    relationship = {
        "source": rel['source'],
        "target": rel['target'],
        "type": rel['type'],
        "properties": {
            "cardinality": rel['cardinality'],
            "description": rel['description']
        }
    }
```

## Next Steps

1. Set up your OpenAI API key
2. Start the server
3. Try the LLM endpoints
4. Integrate results into your knowledge graphs
5. Monitor costs and adjust configuration as needed

---

**Happy intelligent graph building!** 🚀

