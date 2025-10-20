# Multi-Schema Knowledge Graph Generation

Generate unified knowledge graphs from multiple database schemas with automatic cross-schema relationship detection.

## Overview

The enhanced `/api/v1/kg/generate` endpoint now supports:
- **Single schema** - Original functionality (backward compatible)
- **Multiple schemas** - New! Merge multiple schemas into one unified KG
- **Cross-schema relationships** - Automatically detect relationships between tables across schemas

## Key Features

✅ **Unified Knowledge Graph**
- Merge multiple schemas into a single KG
- All entities and relationships in one graph
- Automatic deduplication

✅ **Cross-Schema Relationship Detection**
- Automatically identifies relationships between tables in different schemas
- Uses intelligent pattern matching on column names
- Detects foreign key patterns (e.g., `vendor_uid` → `vendor` table)

✅ **Backward Compatible**
- Single schema requests work exactly as before
- No breaking changes to existing API

✅ **Flexible Input**
- Use `schema_name` for single schema (deprecated but supported)
- Use `schema_names` for multiple schemas (recommended)

## API Endpoint

### POST `/api/v1/kg/generate`

Generate a knowledge graph from one or multiple schemas.

## Request Format

### Single Schema (Original)
```json
{
  "schema_name": "orderMgmt-catalog",
  "kg_name": "my_kg",
  "backends": ["graphiti"]
}
```

### Multiple Schemas (New)
```json
{
  "schema_names": ["orderMgmt-catalog", "qinspect-designcode"],
  "kg_name": "unified_kg",
  "backends": ["graphiti"]
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `schema_name` | string | No* | Single schema name (deprecated, use schema_names) |
| `schema_names` | array | No* | List of schema names to merge |
| `kg_name` | string | Yes | Name for the generated knowledge graph |
| `backends` | array | No | Backends to use: ["falkordb"], ["graphiti"], or both |

*Either `schema_name` or `schema_names` must be provided

## Response Format

```json
{
  "success": true,
  "schemas_processed": ["orderMgmt-catalog", "qinspect-designcode"],
  "message": "Knowledge graph 'unified_kg' generated successfully from 2 schema(s)",
  "kg_name": "unified_kg",
  "nodes_count": 45,
  "relationships_count": 78,
  "backends_used": ["graphiti"],
  "generation_time_ms": 1234.56
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether generation succeeded |
| `schemas_processed` | array | List of schemas that were processed |
| `message` | string | Human-readable status message |
| `kg_name` | string | Name of the generated KG |
| `nodes_count` | integer | Total number of nodes in the KG |
| `relationships_count` | integer | Total number of relationships |
| `backends_used` | array | Which backends successfully stored the KG |
| `generation_time_ms` | float | Time taken to generate the KG |

## Examples

### Example 1: Single Schema (Backward Compatible)
```bash
curl -X POST http://localhost:8000/api/v1/kg/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_name": "orderMgmt-catalog",
    "kg_name": "catalog_kg",
    "backends": ["graphiti"]
  }'
```

### Example 2: Multiple Schemas - Unified KG
```bash
curl -X POST http://localhost:8000/api/v1/kg/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_names": ["orderMgmt-catalog", "qinspect-designcode"],
    "kg_name": "unified_kg",
    "backends": ["graphiti"]
  }'
```

### Example 3: Python - Multiple Schemas
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Generate unified KG from multiple schemas
response = requests.post(
    f"{BASE_URL}/kg/generate",
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

## Cross-Schema Relationship Detection

### How It Works

1. **Pattern Matching**: Analyzes column names for reference patterns
   - `vendor_uid` → references `vendor` table
   - `catalog_id` → references `catalog` table
   - `design_code` → references `design` table

2. **Schema Scanning**: Searches across all loaded schemas
   - Looks for matching table names
   - Handles partial matches and variations

3. **Relationship Creation**: Creates `CROSS_SCHEMA_REFERENCE` relationships
   - Links tables across different schemas
   - Includes metadata about source and target schemas
   - Marks relationships as inferred

### Example Detection

**Schema 1: orderMgmt-catalog**
```
Table: catalog
  - id (PK)
  - product_name
  - vendor_uid  ← References vendor table
```

**Schema 2: qinspect-designcode**
```
Table: vendor
  - uid (PK)
  - vendor_name
```

**Generated Relationship**:
```
catalog.vendor_uid --[CROSS_SCHEMA_REFERENCE]--> vendor.uid
```

## Relationship Types

### Within-Schema Relationships
- `FOREIGN_KEY` - Explicit foreign key constraints
- `REFERENCES` - Inferred from column naming patterns
- `BELONGS_TO` - Column belongs to table

### Cross-Schema Relationships
- `CROSS_SCHEMA_REFERENCE` - Inferred relationship between schemas
  - Properties include source/target schema names
  - Marked as inferred for validation

## Use Cases

### 1. Data Integration
Combine multiple database schemas into a unified knowledge graph for analysis.

```python
# Combine order management and design systems
response = requests.post(
    f"{BASE_URL}/kg/generate",
    json={
        "schema_names": ["orderMgmt-catalog", "qinspect-designcode"],
        "kg_name": "integrated_system",
        "backends": ["graphiti"]
    }
)
```

### 2. Data Lineage
Track data flow across multiple systems.

```python
# Create unified view of data lineage
response = requests.post(
    f"{BASE_URL}/kg/generate",
    json={
        "schema_names": ["source_system", "etl_system", "target_system"],
        "kg_name": "data_lineage",
        "backends": ["graphiti"]
    }
)
```

### 3. Master Data Management
Identify master data entities across systems.

```python
# Find common entities across systems
response = requests.post(
    f"{BASE_URL}/kg/generate",
    json={
        "schema_names": ["crm_system", "erp_system", "inventory_system"],
        "kg_name": "master_data",
        "backends": ["graphiti"]
    }
)
```

## Error Handling

### Schema Not Found
```json
{
  "detail": "Schema file not found: schemas/nonexistent.json"
}
```
Status: 404

### Invalid Request
```json
{
  "detail": "Either 'schema_name' or 'schema_names' must be provided"
}
```
Status: 422

### Server Error
```json
{
  "detail": "Error message describing what went wrong"
}
```
Status: 500

## Performance Considerations

### Single Schema
- Fast: ~100-500ms for typical schemas
- Minimal memory usage

### Multiple Schemas
- Time scales with number of schemas
- Cross-schema detection adds ~10-20% overhead
- Memory usage increases with total entities

### Optimization Tips
1. **Batch Processing**: Generate multiple KGs in parallel
2. **Schema Size**: Smaller schemas process faster
3. **Backend Selection**: Graphiti is faster for large graphs
4. **Caching**: Store generated KGs for reuse

## Backward Compatibility

The endpoint maintains full backward compatibility:

```python
# Old code still works
response = requests.post(
    f"{BASE_URL}/kg/generate",
    json={
        "schema_name": "orderMgmt-catalog",  # Still supported
        "kg_name": "my_kg",
        "backends": ["graphiti"]
    }
)
```

## Migration Guide

### From Single to Multiple Schemas

**Before**:
```python
# Generate separate KGs
kg1 = requests.post(f"{BASE_URL}/kg/generate", json={
    "schema_name": "schema1",
    "kg_name": "kg1"
})
kg2 = requests.post(f"{BASE_URL}/kg/generate", json={
    "schema_name": "schema2",
    "kg_name": "kg2"
})
```

**After**:
```python
# Generate unified KG
unified = requests.post(f"{BASE_URL}/kg/generate", json={
    "schema_names": ["schema1", "schema2"],
    "kg_name": "unified_kg"
})
```

## Troubleshooting

### No Cross-Schema Relationships Detected
- Check column naming conventions
- Ensure table names match expected patterns
- Review logs for detection details

### Too Many Relationships
- Some inferred relationships may be false positives
- Validate relationships in the generated KG
- Consider using explicit foreign keys

### Performance Issues
- Reduce number of schemas per request
- Use smaller schemas
- Consider splitting into multiple KGs

---

**For more information, see:**
- [README.md](../README.md) - Project overview
- [LLM_INTEGRATION.md](LLM_INTEGRATION.md) - LLM features
- [API_EXAMPLES.md](API_EXAMPLES.md) - More API examples

