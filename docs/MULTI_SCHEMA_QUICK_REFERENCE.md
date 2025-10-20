# Multi-Schema KG - Quick Reference

## TL;DR

Generate unified knowledge graphs from multiple schemas with automatic cross-schema relationship detection.

## Basic Usage

### Single Schema (Old Way - Still Works)
```bash
curl -X POST http://localhost:8000/api/v1/kg/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_name": "orderMgmt-catalog",
    "kg_name": "my_kg",
    "backends": ["graphiti"]
  }'
```

### Multiple Schemas (New Way - Recommended)
```bash
curl -X POST http://localhost:8000/api/v1/kg/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_names": ["orderMgmt-catalog", "qinspect-designcode"],
    "kg_name": "unified_kg",
    "backends": ["graphiti"]
  }'
```

## Python Examples

### Single Schema
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/kg/generate",
    json={
        "schema_name": "orderMgmt-catalog",
        "kg_name": "my_kg",
        "backends": ["graphiti"]
    }
)
print(response.json())
```

### Multiple Schemas
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/kg/generate",
    json={
        "schema_names": ["orderMgmt-catalog", "qinspect-designcode"],
        "kg_name": "unified_kg",
        "backends": ["graphiti"]
    }
)

result = response.json()
print(f"Success: {result['success']}")
print(f"Schemas: {result['schemas_processed']}")
print(f"Nodes: {result['nodes_count']}")
print(f"Relationships: {result['relationships_count']}")
```

## Request Parameters

| Parameter | Type | Required | Example |
|-----------|------|----------|---------|
| `schema_name` | string | No* | `"orderMgmt-catalog"` |
| `schema_names` | array | No* | `["schema1", "schema2"]` |
| `kg_name` | string | Yes | `"my_kg"` |
| `backends` | array | No | `["graphiti"]` |

*Either `schema_name` or `schema_names` must be provided

## Response

```json
{
  "success": true,
  "schemas_processed": ["schema1", "schema2"],
  "message": "Knowledge graph generated from 2 schemas",
  "kg_name": "unified_kg",
  "nodes_count": 79,
  "relationships_count": 77,
  "backends_used": ["graphiti"],
  "generation_time_ms": 22.41
}
```

## What Gets Generated

### Nodes
- Tables from all schemas
- Important columns (IDs, UIDs, keys)

### Relationships
- **Within-schema**: Foreign keys, references, belongs_to
- **Cross-schema**: Detected relationships between schemas

### Example
```
Schema 1: orderMgmt-catalog
  Table: catalog
    - vendor_uid (references vendor)

Schema 2: qinspect-designcode
  Table: vendor
    - uid (primary key)

Generated Relationship:
  catalog.vendor_uid --[CROSS_SCHEMA_REFERENCE]--> vendor.uid
```

## How Cross-Schema Detection Works

1. **Pattern Matching**: Analyzes column names
   - `vendor_uid` → looks for `vendor` table
   - `catalog_id` → looks for `catalog` table

2. **Schema Scanning**: Searches all loaded schemas
   - Finds matching table names
   - Handles partial matches

3. **Relationship Creation**: Creates links
   - Type: `CROSS_SCHEMA_REFERENCE`
   - Includes metadata about source/target schemas

## Common Use Cases

### Combine Multiple Systems
```python
response = requests.post(
    "http://localhost:8000/api/v1/kg/generate",
    json={
        "schema_names": ["crm_system", "erp_system", "inventory_system"],
        "kg_name": "enterprise_kg",
        "backends": ["graphiti"]
    }
)
```

### Data Integration
```python
response = requests.post(
    "http://localhost:8000/api/v1/kg/generate",
    json={
        "schema_names": ["source_db", "target_db"],
        "kg_name": "integration_kg",
        "backends": ["graphiti"]
    }
)
```

### Data Lineage
```python
response = requests.post(
    "http://localhost:8000/api/v1/kg/generate",
    json={
        "schema_names": ["source", "etl", "warehouse"],
        "kg_name": "data_lineage",
        "backends": ["graphiti"]
    }
)
```

## Performance

| Scenario | Time | Nodes | Relationships |
|----------|------|-------|----------------|
| Single schema | ~1ms | 50 | 49 |
| Two schemas | ~22ms | 79 | 77 |
| Three schemas | ~35ms | ~110 | ~110 |

## Error Handling

### Missing Schema
```json
{
  "detail": "Schema file not found: schemas/nonexistent.json"
}
```
Status: 404

### Missing Parameters
```json
{
  "detail": "Either 'schema_name' or 'schema_names' must be provided"
}
```
Status: 422

## Backward Compatibility

✅ Old code still works:
```python
# This still works (deprecated but supported)
response = requests.post(
    "http://localhost:8000/api/v1/kg/generate",
    json={
        "schema_name": "orderMgmt-catalog",
        "kg_name": "my_kg"
    }
)
```

## Testing

Run the test script:
```bash
python test_multi_schema_kg.py
```

## Documentation

- **Full Guide**: [MULTI_SCHEMA_KG.md](MULTI_SCHEMA_KG.md)
- **Implementation**: [MULTI_SCHEMA_IMPLEMENTATION.md](MULTI_SCHEMA_IMPLEMENTATION.md)
- **API Examples**: [API_EXAMPLES.md](API_EXAMPLES.md)

## Key Features

✅ **Unified KG**: Merge multiple schemas into one graph
✅ **Auto-Detection**: Automatically find cross-schema relationships
✅ **Backward Compatible**: Old API calls still work
✅ **Fast**: ~22ms for two schemas
✅ **Flexible**: Use `schema_name` or `schema_names`

## Next Steps

1. **Try it**: Generate a unified KG from multiple schemas
2. **Query it**: Use graph queries to explore relationships
3. **Enhance it**: Use LLM to improve relationship descriptions
4. **Integrate it**: Use in your data pipeline

---

**Ready to use!** 🚀

