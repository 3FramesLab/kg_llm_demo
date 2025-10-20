# Quick Start Guide

Get up and running with Knowledge Graph Builder in 5 minutes!

## Prerequisites
- Python 3.8+
- pip

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Application
```bash
python -m kg_builder.main
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Open API Documentation
Visit: http://localhost:8000/docs

## First Steps

### Step 1: Check Health
```bash
curl http://localhost:8000/api/v1/health
```

### Step 2: List Available Schemas
```bash
curl http://localhost:8000/api/v1/schemas
```

You should see:
```json
{
  "success": true,
  "schemas": ["orderMgmt-catalog", "qinspect-designcode"],
  "count": 2
}
```

### Step 3: Parse a Schema
```bash
curl -X POST http://localhost:8000/api/v1/schemas/orderMgmt-catalog/parse
```

### Step 4: Generate Knowledge Graph
```bash
curl -X POST http://localhost:8000/api/v1/kg/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_name": "orderMgmt-catalog",
    "kg_name": "my_first_kg",
    "backends": ["graphiti"]
  }'
```

### Step 5: View the Generated Graph
```bash
curl http://localhost:8000/api/v1/kg/my_first_kg/entities
```

### Step 6: Export the Graph
```bash
curl http://localhost:8000/api/v1/kg/my_first_kg/export > my_graph.json
```

## Using the Interactive API

1. Open http://localhost:8000/docs in your browser
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"

## Common Tasks

### Generate Graph from Second Schema
```bash
curl -X POST http://localhost:8000/api/v1/kg/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_name": "qinspect-designcode",
    "kg_name": "design_kg",
    "backends": ["graphiti"]
  }'
```

### List All Generated Graphs
```bash
curl http://localhost:8000/api/v1/kg
```

### Delete a Graph
```bash
curl -X DELETE http://localhost:8000/api/v1/kg/my_first_kg
```

## Troubleshooting

### Port Already in Use
If port 8000 is already in use:
```bash
python -m kg_builder.main --port 8001
```

### Module Not Found
Make sure you're in the correct directory:
```bash
cd d:\learning\dq-poc
python -m kg_builder.main
```

### FalkorDB Connection Error
This is normal if FalkorDB is not running. The application will use Graphiti's file-based storage instead.

## Next Steps

1. Read the full [README.md](README.md)
2. Explore [API_EXAMPLES.md](API_EXAMPLES.md) for more examples
3. Check the Swagger UI at http://localhost:8000/docs
4. Modify schemas in the `schemas/` folder
5. Customize configuration in `kg_builder/config.py`

## File Locations

- **Schemas**: `schemas/` folder
- **Generated Graphs**: `data/graphiti_storage/` folder
- **Configuration**: `kg_builder/config.py`
- **API Code**: `kg_builder/` folder

## Key Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/health` | Check app status |
| GET | `/api/v1/schemas` | List schemas |
| POST | `/api/v1/schemas/{name}/parse` | Parse schema |
| POST | `/api/v1/kg/generate` | Generate KG |
| GET | `/api/v1/kg` | List KGs |
| GET | `/api/v1/kg/{name}/entities` | Get entities |
| GET | `/api/v1/kg/{name}/relationships` | Get relationships |
| GET | `/api/v1/kg/{name}/export` | Export KG |
| DELETE | `/api/v1/kg/{name}` | Delete KG |

## Tips

- Use Graphiti backend for development (no external dependencies)
- Check health endpoint before operations
- Export graphs for backup and analysis
- Use the Swagger UI to explore endpoints interactively

Happy graphing! 🎉

