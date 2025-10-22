# Natural Language Relationships - Quick Start Guide

## 🚀 Getting Started

The Natural Language Relationships feature allows you to define custom relationships between entities using natural language instead of structured formats.

---

## 📝 Supported Input Formats

### 1. Natural Language
```
"Products are supplied by Vendors"
"Orders contain Products with quantity"
"Customers place Orders"
```

### 2. Semi-Structured
```
"catalog.product_id → vendors.vendor_id (SUPPLIED_BY)"
"orders.customer_id → customers.id (PLACED_BY)"
```

### 3. Pseudo-SQL
```
"SELECT * FROM catalog JOIN vendors ON catalog.vendor_id = vendors.id"
"FROM orders JOIN customers ON orders.customer_id = customers.id"
```

### 4. Business Rules
```
"IF product.status='active' THEN product REFERENCES vendor"
"IF order.total > 1000 THEN order BELONGS_TO premium_customer"
```

---

## 🔌 API Usage

### Endpoint
```
POST /api/v1/kg/relationships/natural-language
```

### Basic Example
```python
import requests

url = "http://localhost:8000/api/v1/kg/relationships/natural-language"

payload = {
    "kg_name": "demo_kg",
    "schemas": ["orderMgmt-catalog", "vendorDB-suppliers"],
    "definitions": [
        "Products are supplied by Vendors",
        "Orders contain Products",
        "Vendors have Locations"
    ],
    "use_llm": True,
    "min_confidence": 0.7
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Success: {result['success']}")
print(f"Parsed: {result['parsed_count']}")
print(f"Failed: {result['failed_count']}")
print(f"Time: {result['processing_time_ms']:.2f}ms")

for rel in result['relationships']:
    print(f"  {rel['source_table']} --{rel['relationship_type']}--> {rel['target_table']}")
    print(f"    Confidence: {rel['confidence']}")
    print(f"    Status: {rel['validation_status']}")
```

### Advanced Example with Error Handling
```python
import requests
import json

url = "http://localhost:8000/api/v1/kg/relationships/natural-language"

payload = {
    "kg_name": "my_kg",
    "schemas": ["schema1", "schema2"],
    "definitions": [
        "Entity1 supplied by Entity2",
        "Entity3 contains Entity4"
    ],
    "use_llm": False,  # Use rule-based parsing only
    "min_confidence": 0.75
}

try:
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    result = response.json()
    
    if result['success']:
        print("✅ All definitions parsed successfully!")
        for rel in result['relationships']:
            print(f"  ✓ {rel['source_table']} → {rel['target_table']}")
    else:
        print("⚠️ Some definitions failed:")
        for error in result['errors']:
            print(f"  ✗ {error}")
            
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")
```

---

## 🎯 Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `kg_name` | string | Yes | - | Name of the knowledge graph |
| `schemas` | array | Yes | - | List of schema names to validate against |
| `definitions` | array | Yes | - | List of relationship definitions |
| `use_llm` | boolean | No | true | Use LLM for parsing (requires OPENAI_API_KEY) |
| `min_confidence` | float | No | 0.7 | Minimum confidence threshold (0.0-1.0) |

---

## 📊 Response Structure

```json
{
  "success": true,
  "relationships": [
    {
      "source_table": "catalog",
      "target_table": "vendors",
      "relationship_type": "SUPPLIED_BY",
      "confidence": 0.85,
      "reasoning": "Extracted from natural language",
      "input_format": "natural_language",
      "validation_status": "VALID",
      "properties": [],
      "cardinality": "1:N",
      "validation_errors": []
    }
  ],
  "parsed_count": 1,
  "failed_count": 0,
  "errors": [],
  "processing_time_ms": 125.45
}
```

---

## 🔗 Relationship Types

Supported relationship types:
- `SUPPLIED_BY` / `SUPPLIES`
- `CONTAINS` / `CONTAINED_BY`
- `HAS` / `BELONGS_TO`
- `REFERENCES` / `REFERENCED_BY`
- `PLACES` / `PLACED_BY`
- `SOLD_BY` / `SELLS`
- `CREATED_BY` / `CREATES`
- `MANAGED_BY` / `MANAGES`

---

## ⚙️ Configuration

### Enable LLM Parsing
Set `OPENAI_API_KEY` in `.env`:
```env
OPENAI_API_KEY=sk-your-key-here
```

### Disable LLM Parsing
Use rule-based parsing only:
```python
payload = {
    ...
    "use_llm": False
}
```

---

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/test_nl_relationship_parser.py -v
```

### Run Integration Tests
```bash
pytest tests/test_nl_integration.py -v
```

### Run All Tests
```bash
pytest tests/test_nl_relationship_parser.py tests/test_nl_integration.py -v
```

---

## 📈 Performance

- **Average Response Time**: ~125ms
- **Format Detection**: <1ms
- **Parsing**: 10-50ms per definition
- **Validation**: 5-20ms per relationship
- **Confidence Filtering**: <1ms

---

## ❌ Error Handling

### Invalid Schema
```json
{
  "success": false,
  "errors": ["Failed to load schemas: Schema 'nonexistent' not found"]
}
```

### Low Confidence
```json
{
  "success": true,
  "relationships": [],
  "errors": ["Definition 'X' parsed but all relationships below confidence threshold"]
}
```

### Validation Errors
```json
{
  "relationships": [
    {
      "validation_status": "INVALID",
      "validation_errors": ["Source table 'nonexistent' not found in schema"]
    }
  ]
}
```

---

## 💡 Best Practices

1. **Use Clear Language**: "Products are supplied by Vendors" works better than "Prod supp Vend"
2. **Match Schema Names**: Use actual table names from your schemas
3. **Set Appropriate Confidence**: Higher threshold = fewer but more reliable relationships
4. **Validate Results**: Check `validation_status` and `validation_errors`
5. **Monitor Performance**: Track `processing_time_ms` for optimization

---

## 🔍 Troubleshooting

### No Relationships Returned
- Check schema names match exactly
- Lower `min_confidence` threshold
- Verify table names in definitions
- Enable LLM parsing for better accuracy

### High Processing Time
- Reduce number of definitions per request
- Use rule-based parsing (`use_llm: false`)
- Check network latency to LLM service

### Validation Errors
- Verify table names exist in schemas
- Check relationship type is valid
- Ensure source and target tables are different

---

## 📚 Related Documentation

- [Phase 1 Implementation Complete](PHASE_1_IMPLEMENTATION_COMPLETE.md)
- [NL vs LLM Reconciliation](NL_RELATIONSHIPS_VS_LLM_RECONCILIATION.md)
- [Implementation Plan](NL_RELATIONSHIPS_IMPLEMENTATION_PLAN.md)

