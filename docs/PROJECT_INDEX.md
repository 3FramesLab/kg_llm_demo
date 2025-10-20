# Knowledge Graph Builder - Project Index

## 📚 Documentation Files

### Getting Started
1. **[QUICKSTART.md](QUICKSTART.md)** - Start here! 5-minute quick start guide
2. **[README.md](README.md)** - Complete setup and usage documentation
3. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What was built and tested

### API Documentation
4. **[API_EXAMPLES.md](API_EXAMPLES.md)** - Detailed curl and Python examples
5. **[.env.example](.env.example)** - Configuration template

### Testing
6. **[test_api.py](test_api.py)** - Automated test script for all endpoints

## 🏗️ Project Structure

```
kg_builder/                          # Main application package
├── __init__.py                      # Package initialization
├── config.py                        # Configuration settings
├── models.py                        # Pydantic data models
├── main.py                          # FastAPI application
├── routes.py                        # API endpoints
└── services/                        # Business logic
    ├── __init__.py
    ├── schema_parser.py             # JSON schema parsing
    ├── falkordb_backend.py          # FalkorDB integration
    └── graphiti_backend.py          # Graphiti integration

schemas/                             # Input schema files
├── orderMgmt-catalog.json
└── qinspect-designcode.json

data/                                # Generated data
└── graphiti_storage/                # Graphiti graph storage

requirements.txt                     # Python dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python -m kg_builder.main
```

### 3. Test the API
```bash
python test_api.py
```

### 4. Access Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📋 API Endpoints

### Health & Status
- `GET /api/v1/health` - Check application health

### Schema Management
- `GET /api/v1/schemas` - List available schemas
- `POST /api/v1/schemas/{schema_name}/parse` - Parse a schema

### Knowledge Graph Operations
- `POST /api/v1/kg/generate` - Generate a knowledge graph
- `GET /api/v1/kg` - List all knowledge graphs
- `GET /api/v1/kg/{kg_name}/entities` - Get all entities
- `GET /api/v1/kg/{kg_name}/relationships` - Get all relationships
- `POST /api/v1/kg/{kg_name}/query` - Query a knowledge graph
- `GET /api/v1/kg/{kg_name}/export` - Export a knowledge graph
- `DELETE /api/v1/kg/{kg_name}` - Delete a knowledge graph

## 🔑 Key Features

✅ **Dual Backend Support**
- FalkorDB: High-performance graph database
- Graphiti: Temporal knowledge graph with file-based fallback

✅ **Automatic Schema Parsing**
- Extracts entities from database tables
- Identifies relationships from foreign keys
- Infers relationships from column naming patterns

✅ **RESTful API**
- Complete CRUD operations
- Automatic Swagger/OpenAPI documentation
- Comprehensive error handling

✅ **Production Ready**
- Proper logging and monitoring
- CORS support
- Environment-based configuration
- Graceful error handling

## 📖 Usage Examples

### Generate a Knowledge Graph
```python
import requests

payload = {
    "schema_name": "orderMgmt-catalog",
    "kg_name": "my_kg",
    "backends": ["graphiti"]
}

response = requests.post(
    "http://localhost:8000/api/v1/kg/generate",
    json=payload
)
print(response.json())
```

### Retrieve Entities
```python
response = requests.get(
    "http://localhost:8000/api/v1/kg/my_kg/entities"
)
entities = response.json()
print(f"Total entities: {entities['count']}")
```

### Export Graph
```python
response = requests.get(
    "http://localhost:8000/api/v1/kg/my_kg/export"
)
export_data = response.json()
```

## 🧪 Testing

### Run Automated Tests
```bash
python test_api.py
```

### Manual Testing with curl
```bash
# Health check
curl http://localhost:8000/api/v1/health

# List schemas
curl http://localhost:8000/api/v1/schemas

# Generate KG
curl -X POST http://localhost:8000/api/v1/kg/generate \
  -H "Content-Type: application/json" \
  -d '{"schema_name":"orderMgmt-catalog","kg_name":"test_kg","backends":["graphiti"]}'
```

## 🔧 Configuration

### Environment Variables
```bash
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
FALKORDB_PASSWORD=
LOG_LEVEL=INFO
```

### Configuration File
Edit `kg_builder/config.py` to customize:
- FalkorDB connection settings
- Graphiti storage path
- API settings (CORS, logging, etc.)

## 📊 Data Models

### Schema Models
- `ColumnSchema`: Database column definition
- `TableSchema`: Database table definition
- `DatabaseSchema`: Complete database schema

### Graph Models
- `GraphNode`: Entity in the knowledge graph
- `GraphRelationship`: Connection between entities
- `KnowledgeGraph`: Complete graph structure

### API Models
- `KGGenerationRequest`: Request to generate a graph
- `QueryRequest`: Query request
- `GraphExportResponse`: Export response

## 🎯 Workflow

1. **Load Schema** → Parse JSON schema file
2. **Extract Entities** → Identify tables and important columns
3. **Identify Relationships** → Find connections between entities
4. **Build Graph** → Create graph structure
5. **Store Graph** → Save to FalkorDB or Graphiti
6. **Query Graph** → Retrieve entities and relationships
7. **Export Graph** → Export as JSON

## 🐛 Troubleshooting

### FalkorDB Connection Error
- This is normal if FalkorDB server is not running
- Application will use Graphiti file-based storage instead

### Port Already in Use
- Change port in `kg_builder/config.py`
- Or use: `python -m kg_builder.main --port 8001`

### Schema File Not Found
- Ensure JSON files are in `schemas/` directory
- Use schema name without `.json` extension

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **FalkorDB Documentation**: https://www.falkordb.com/
- **Graphiti Documentation**: https://github.com/Contextual-AI/graphiti

## ✨ What's Included

✅ Complete FastAPI application
✅ Schema parsing service
✅ FalkorDB backend integration
✅ Graphiti backend integration
✅ 11 API endpoints
✅ Comprehensive documentation
✅ Automated test script
✅ Example API calls
✅ Configuration templates
✅ Error handling and logging

## 🎉 Ready to Use!

The Knowledge Graph Builder is fully implemented, tested, and ready for use. Start with [QUICKSTART.md](QUICKSTART.md) to get up and running in 5 minutes!

---

**Last Updated**: 2025-10-19
**Status**: ✅ Complete and Tested

