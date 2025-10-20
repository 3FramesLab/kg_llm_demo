# Knowledge Graph Builder - API Examples

This document provides practical examples for using the Knowledge Graph Builder API.

## Base URL
```
http://localhost:8000/api/v1
```

## 1. Health Check

### Check Application Status
```bash
curl -X GET "http://localhost:8000/api/v1/health" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "status": "healthy",
  "falkordb_connected": true,
  "graphiti_available": true,
  "timestamp": "2025-10-19T10:30:00.000000"
}
```

## 2. Schema Management

### List Available Schemas
```bash
curl -X GET "http://localhost:8000/api/v1/schemas" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "success": true,
  "schemas": ["orderMgmt-catalog", "qinspect-designcode"],
  "count": 2
}
```

### Parse a Schema
```bash
curl -X POST "http://localhost:8000/api/v1/schemas/orderMgmt-catalog/parse" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "success": true,
  "message": "Schema 'orderMgmt-catalog' parsed successfully",
  "schema_name": "orderMgmt-catalog",
  "tables_count": 1,
  "total_columns": 150
}
```

## 3. Knowledge Graph Generation

### Generate Knowledge Graph (Both Backends)
```bash
curl -X POST "http://localhost:8000/api/v1/kg/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "schema_name": "orderMgmt-catalog",
    "kg_name": "catalog_kg",
    "backends": ["falkordb", "graphiti"]
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Knowledge graph 'catalog_kg' generated successfully",
  "kg_name": "catalog_kg",
  "nodes_count": 45,
  "relationships_count": 120,
  "backends_used": ["falkordb", "graphiti"],
  "generation_time_ms": 1234.56
}
```

### Generate Knowledge Graph (FalkorDB Only)
```bash
curl -X POST "http://localhost:8000/api/v1/kg/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "schema_name": "qinspect-designcode",
    "kg_name": "design_kg",
    "backends": ["falkordb"]
  }'
```

## 4. Knowledge Graph Queries

### List All Knowledge Graphs
```bash
curl -X GET "http://localhost:8000/api/v1/kg" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "success": true,
  "graphs": ["catalog_kg", "design_kg"],
  "count": 2
}
```

### Get All Entities
```bash
curl -X GET "http://localhost:8000/api/v1/kg/catalog_kg/entities?backend=graphiti" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "success": true,
  "kg_name": "catalog_kg",
  "entities": [
    {
      "id": "table_catalog",
      "label": "catalog",
      "properties": {
        "type": "Table",
        "column_count": 150,
        "primary_keys": ["id"]
      },
      "source_table": "catalog"
    },
    {
      "id": "column_catalog_id",
      "label": "catalog.id",
      "properties": {
        "type": "Column",
        "column_type": "BIGINT",
        "nullable": false,
        "primary_key": false
      },
      "source_table": "catalog",
      "source_column": "id"
    }
  ],
  "count": 45
}
```

### Get All Relationships
```bash
curl -X GET "http://localhost:8000/api/v1/kg/catalog_kg/relationships?backend=graphiti" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "success": true,
  "kg_name": "catalog_kg",
  "relationships": [
    {
      "source_id": "table_catalog",
      "target_id": "column_catalog_id",
      "relationship_type": "BELONGS_TO",
      "properties": {
        "column_name": "id"
      },
      "source_column": "id"
    },
    {
      "source_id": "table_catalog",
      "target_id": "table_brand",
      "relationship_type": "REFERENCES",
      "properties": {
        "inferred": true,
        "column_name": "brand_uid"
      },
      "source_column": "brand_uid"
    }
  ],
  "count": 120
}
```

### Query Knowledge Graph (FalkorDB)
```bash
curl -X POST "http://localhost:8000/api/v1/kg/catalog_kg/query" \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "catalog_kg",
    "query": "MATCH (n) RETURN n LIMIT 10",
    "backend": "falkordb"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Query executed successfully",
  "results": [
    {
      "n": {
        "id": "table_catalog",
        "label": "catalog",
        "properties": {...}
      }
    }
  ],
  "query_time_ms": 45.23
}
```

## 5. Export Knowledge Graph

### Export as JSON
```bash
curl -X GET "http://localhost:8000/api/v1/kg/catalog_kg/export?backend=graphiti" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "success": true,
  "message": "Graph 'catalog_kg' exported successfully",
  "format": "json",
  "data": {
    "kg_name": "catalog_kg",
    "entities": [...],
    "relationships": [...],
    "stats": {
      "entities_count": 45,
      "relationships_count": 120
    }
  }
}
```

## 6. Delete Knowledge Graph

### Delete a Graph
```bash
curl -X DELETE "http://localhost:8000/api/v1/kg/catalog_kg" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "success": true,
  "message": "Graph 'catalog_kg' deleted",
  "falkordb_deleted": true,
  "graphiti_deleted": true
}
```

## Python Examples

### Using Python Requests Library

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Generate knowledge graph
payload = {
    "schema_name": "orderMgmt-catalog",
    "kg_name": "catalog_kg",
    "backends": ["falkordb", "graphiti"]
}
response = requests.post(f"{BASE_URL}/kg/generate", json=payload)
print(response.json())

# Query knowledge graph
query_payload = {
    "kg_name": "catalog_kg",
    "query": "MATCH (n) RETURN n LIMIT 10",
    "backend": "falkordb"
}
response = requests.post(f"{BASE_URL}/kg/catalog_kg/query", json=query_payload)
print(response.json())

# Get entities
response = requests.get(f"{BASE_URL}/kg/catalog_kg/entities?backend=graphiti")
print(response.json())

# Export graph
response = requests.get(f"{BASE_URL}/kg/catalog_kg/export?backend=graphiti")
export_data = response.json()
with open("catalog_kg_export.json", "w") as f:
    json.dump(export_data, f, indent=2)

# Delete graph
response = requests.delete(f"{BASE_URL}/kg/catalog_kg")
print(response.json())
```

## Complete Workflow Example

```python
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

# 1. Check health
print("1. Checking health...")
health = requests.get(f"{BASE_URL}/health").json()
print(f"   Status: {health['status']}")

# 2. List schemas
print("\n2. Listing schemas...")
schemas = requests.get(f"{BASE_URL}/schemas").json()
print(f"   Available schemas: {schemas['schemas']}")

# 3. Parse schema
print("\n3. Parsing schema...")
parse_result = requests.post(f"{BASE_URL}/schemas/orderMgmt-catalog/parse").json()
print(f"   Tables: {parse_result['tables_count']}, Columns: {parse_result['total_columns']}")

# 4. Generate knowledge graph
print("\n4. Generating knowledge graph...")
gen_payload = {
    "schema_name": "orderMgmt-catalog",
    "kg_name": "catalog_kg",
    "backends": ["falkordb", "graphiti"]
}
gen_result = requests.post(f"{BASE_URL}/kg/generate", json=gen_payload).json()
print(f"   Nodes: {gen_result['nodes_count']}, Relationships: {gen_result['relationships_count']}")

# 5. Get entities
print("\n5. Retrieving entities...")
entities = requests.get(f"{BASE_URL}/kg/catalog_kg/entities").json()
print(f"   Total entities: {entities['count']}")

# 6. Get relationships
print("\n6. Retrieving relationships...")
rels = requests.get(f"{BASE_URL}/kg/catalog_kg/relationships").json()
print(f"   Total relationships: {rels['count']}")

# 7. Export graph
print("\n7. Exporting graph...")
export = requests.get(f"{BASE_URL}/kg/catalog_kg/export").json()
print(f"   Export successful: {export['success']}")

print("\nWorkflow completed!")
```

## Error Handling

### Schema Not Found
```bash
curl -X POST "http://localhost:8000/api/v1/schemas/nonexistent/parse"
```

**Response (404):**
```json
{
  "detail": "Schema 'nonexistent' not found"
}
```

### FalkorDB Not Connected
```bash
curl -X POST "http://localhost:8000/api/v1/kg/generate" \
  -d '{"schema_name": "orderMgmt-catalog", "kg_name": "test_kg", "backends": ["falkordb"]}'
```

**Response (503):**
```json
{
  "detail": "FalkorDB not connected"
}
```

## Tips

1. **Use Graphiti for Development**: Graphiti has file-based fallback storage
2. **Batch Operations**: Generate multiple graphs for different schemas
3. **Query Optimization**: Use specific queries instead of retrieving all data
4. **Export for Analysis**: Export graphs for external analysis tools
5. **Monitor Health**: Check health endpoint before operations

