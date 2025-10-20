# LLM Integration Examples

Complete examples showing how to use the LLM-powered intelligent extraction features.

## Setup

First, ensure you have:
1. OpenAI API key set in `.env` or environment
2. Server running: `python -m kg_builder.main`

## Example 1: Check LLM Status

### Python
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Check if LLM is enabled
response = requests.get(f"{BASE_URL}/llm/status")
status = response.json()

print(f"LLM Enabled: {status['enabled']}")
print(f"Model: {status['model']}")
print(f"Temperature: {status['temperature']}")
print(f"Max Tokens: {status['max_tokens']}")
```

### Curl
```bash
curl http://localhost:8000/api/v1/llm/status | python -m json.tool
```

### Response
```json
{
  "enabled": true,
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

---

## Example 2: Extract Entities and Relationships

### Python
```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Extract entities and relationships using LLM
response = requests.post(
    f"{BASE_URL}/llm/extract/orderMgmt-catalog"
)

if response.status_code == 200:
    result = response.json()
    
    print(f"Success: {result['success']}")
    print(f"\nExtracted {len(result['entities'])} Entities:")
    
    for entity in result['entities']:
        print(f"\n  Entity: {entity['name']}")
        print(f"  Purpose: {entity['purpose']}")
        print(f"  Type: {entity['type']}")
        print(f"  Key Attributes: {', '.join(entity['key_attributes'])}")
        print(f"  Description: {entity['description']}")
    
    print(f"\n\nExtracted {len(result['relationships'])} Relationships:")
    
    for rel in result['relationships']:
        print(f"\n  {rel['source']} --[{rel['type']}]--> {rel['target']}")
        print(f"  Cardinality: {rel['cardinality']}")
        print(f"  Description: {rel['description']}")
        if rel['foreign_key']:
            print(f"  Foreign Key: {rel['foreign_key']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### Curl
```bash
curl -X POST http://localhost:8000/api/v1/llm/extract/orderMgmt-catalog | python -m json.tool
```

### Response Example
```json
{
  "success": true,
  "entities": [
    {
      "name": "catalog",
      "purpose": "Stores product catalog information",
      "type": "Master Data",
      "key_attributes": ["id", "product_name", "vendor_uid", "price"],
      "description": "Central repository for all product information including pricing, vendor details, and inventory status"
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

---

## Example 3: Analyze Schema

### Python
```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Get comprehensive schema analysis
response = requests.post(
    f"{BASE_URL}/llm/analyze/orderMgmt-catalog"
)

if response.status_code == 200:
    analysis = response.json()
    
    print("=== Schema Analysis ===\n")
    print(f"Domain: {analysis['domain']}")
    print(f"Purpose: {analysis['purpose']}")
    
    print(f"\nData Patterns:")
    for pattern in analysis['patterns']:
        print(f"  - {pattern}")
    
    print(f"\nKey Entities:")
    for entity in analysis['key_entities']:
        print(f"  - {entity}")
    
    print(f"\nData Flow:")
    print(f"  {analysis['data_flow']}")
    
    print(f"\nBusiness Logic:")
    print(f"  {analysis['business_logic']}")
    
    print(f"\nData Quality Notes:")
    print(f"  {analysis['quality_notes']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### Curl
```bash
curl -X POST http://localhost:8000/api/v1/llm/analyze/orderMgmt-catalog | python -m json.tool
```

### Response Example
```json
{
  "success": true,
  "domain": "E-commerce / Order Management",
  "purpose": "Manages product catalog, inventory, and vendor relationships",
  "patterns": [
    "Master-Detail",
    "Temporal Data",
    "Hierarchical"
  ],
  "key_entities": [
    "catalog - central product repository",
    "vendor - supplier information"
  ],
  "data_flow": "Products flow from vendors through catalog to orders",
  "business_logic": "Products are organized by vendor with pricing tiers",
  "quality_notes": "Timestamps track data changes; nullable fields indicate optional attributes"
}
```

---

## Example 4: Complete Workflow

### Python - Full Integration
```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def analyze_schema_completely(schema_name):
    """Complete schema analysis workflow."""
    
    print(f"Analyzing schema: {schema_name}\n")
    
    # Step 1: Check LLM status
    print("Step 1: Checking LLM status...")
    status = requests.get(f"{BASE_URL}/llm/status").json()
    if not status['enabled']:
        print("ERROR: LLM not enabled!")
        return
    print(f"✓ LLM enabled with model: {status['model']}\n")
    
    # Step 2: Extract entities and relationships
    print("Step 2: Extracting entities and relationships...")
    extraction = requests.post(
        f"{BASE_URL}/llm/extract/{schema_name}"
    ).json()
    
    if extraction['success']:
        print(f"✓ Extracted {len(extraction['entities'])} entities")
        print(f"✓ Extracted {len(extraction['relationships'])} relationships\n")
    else:
        print(f"ERROR: {extraction.get('error')}")
        return
    
    # Step 3: Analyze schema
    print("Step 3: Analyzing schema...")
    analysis = requests.post(
        f"{BASE_URL}/llm/analyze/{schema_name}"
    ).json()
    
    if analysis['success']:
        print(f"✓ Domain: {analysis['domain']}")
        print(f"✓ Purpose: {analysis['purpose']}\n")
    else:
        print(f"ERROR: {analysis.get('error')}")
        return
    
    # Step 4: Generate knowledge graph
    print("Step 4: Generating knowledge graph...")
    kg_request = {
        "schema_name": schema_name,
        "kg_name": f"{schema_name}_kg",
        "backends": ["graphiti"]
    }
    kg_response = requests.post(
        f"{BASE_URL}/kg/generate",
        json=kg_request
    ).json()
    
    if kg_response['success']:
        print(f"✓ Knowledge graph created\n")
    else:
        print(f"ERROR: {kg_response.get('error')}")
        return
    
    # Step 5: Display results
    print("=== ANALYSIS RESULTS ===\n")
    
    print("ENTITIES:")
    for entity in extraction['entities']:
        print(f"  • {entity['name']} ({entity['type']})")
        print(f"    Purpose: {entity['purpose']}")
    
    print("\nRELATIONSHIPS:")
    for rel in extraction['relationships']:
        print(f"  • {rel['source']} --[{rel['type']}]--> {rel['target']}")
        print(f"    Cardinality: {rel['cardinality']}")
    
    print("\nSCHEMA INSIGHTS:")
    print(f"  Domain: {analysis['domain']}")
    print(f"  Patterns: {', '.join(analysis['patterns'])}")
    print(f"  Data Flow: {analysis['data_flow']}")
    
    print("\n✓ Analysis complete!")

# Run the analysis
analyze_schema_completely("orderMgmt-catalog")
```

---

## Example 5: Error Handling

### Python - Robust Error Handling
```python
import requests
from requests.exceptions import RequestException

BASE_URL = "http://localhost:8000/api/v1"

def safe_llm_extract(schema_name):
    """Extract with proper error handling."""
    try:
        # Check LLM status first
        status = requests.get(f"{BASE_URL}/llm/status").json()
        if not status['enabled']:
            print("LLM not enabled. Set OPENAI_API_KEY environment variable.")
            return None
        
        # Extract
        response = requests.post(
            f"{BASE_URL}/llm/extract/{schema_name}",
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        if not result['success']:
            print(f"Extraction failed: {result.get('error')}")
            return None
        
        return result
        
    except requests.exceptions.Timeout:
        print("Request timeout. Try again or increase OPENAI_MAX_TOKENS.")
    except requests.exceptions.ConnectionError:
        print("Connection error. Is the server running?")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e.response.status_code}")
        print(e.response.json())
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return None

# Use it
result = safe_llm_extract("orderMgmt-catalog")
if result:
    print(f"Success! Found {len(result['entities'])} entities")
```

---

## Example 6: Batch Processing

### Python - Process Multiple Schemas
```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def batch_analyze_schemas():
    """Analyze multiple schemas."""
    
    # Get list of schemas
    schemas_response = requests.get(f"{BASE_URL}/schemas")
    schemas = schemas_response.json()['schemas']
    
    results = {}
    
    for schema_name in schemas:
        print(f"Processing {schema_name}...")
        
        try:
            # Extract
            extraction = requests.post(
                f"{BASE_URL}/llm/extract/{schema_name}",
                timeout=30
            ).json()
            
            # Analyze
            analysis = requests.post(
                f"{BASE_URL}/llm/analyze/{schema_name}",
                timeout=30
            ).json()
            
            results[schema_name] = {
                "entities": len(extraction.get('entities', [])),
                "relationships": len(extraction.get('relationships', [])),
                "domain": analysis.get('domain'),
                "purpose": analysis.get('purpose')
            }
            
            print(f"  ✓ Complete\n")
            
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
            results[schema_name] = {"error": str(e)}
    
    # Display summary
    print("\n=== BATCH ANALYSIS SUMMARY ===\n")
    for schema_name, result in results.items():
        print(f"{schema_name}:")
        if 'error' in result:
            print(f"  Error: {result['error']}")
        else:
            print(f"  Entities: {result['entities']}")
            print(f"  Relationships: {result['relationships']}")
            print(f"  Domain: {result['domain']}")
        print()

# Run batch processing
batch_analyze_schemas()
```

---

## Tips & Tricks

1. **Check Status First**: Always verify LLM is enabled before making requests
2. **Handle Timeouts**: Set appropriate timeouts for API calls
3. **Cache Results**: Store extraction results to avoid repeated API calls
4. **Monitor Costs**: Track API usage in your OpenAI dashboard
5. **Use Batch Processing**: Process multiple schemas efficiently
6. **Error Handling**: Always handle potential errors gracefully

---

**For more information, see [LLM_INTEGRATION.md](LLM_INTEGRATION.md) and [LLM_PROMPTS_REFERENCE.md](LLM_PROMPTS_REFERENCE.md)**

