# Getting Started with Knowledge Graph Builder

## ⚡ 5-Minute Quick Start

### Step 1: Install Dependencies (1 minute)
```bash
pip install -r requirements.txt
```

### Step 2: Start the Server (30 seconds)
```bash
python -m kg_builder.main
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Test the API (1 minute)
```bash
python test_api.py
```

### Step 4: Access the Documentation (1 minute)
Open your browser:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Step 5: Try Your First Request (1 minute)
```bash
# List available schemas
curl http://localhost:8000/api/v1/schemas

# Generate a knowledge graph
curl -X POST http://localhost:8000/api/v1/kg/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_name": "orderMgmt-catalog",
    "kg_name": "my_first_kg",
    "backends": ["graphiti"]
  }'
```

## 📖 Documentation Guide

### For Different Needs:

**I want to understand what this is:**
→ Read [README.md](README.md)

**I want to get started immediately:**
→ Read [QUICKSTART.md](QUICKSTART.md)

**I want to see API examples:**
→ Read [API_EXAMPLES.md](API_EXAMPLES.md)

**I want to understand the architecture:**
→ Read [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

**I want to navigate the project:**
→ Read [PROJECT_INDEX.md](PROJECT_INDEX.md)

**I want to see what was delivered:**
→ Read [DELIVERABLES.md](DELIVERABLES.md)

## 🎯 Common Tasks

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

### Get All Entities
```python
response = requests.get(
    "http://localhost:8000/api/v1/kg/my_kg/entities"
)
entities = response.json()
print(f"Total entities: {entities['count']}")
```

### Get All Relationships
```python
response = requests.get(
    "http://localhost:8000/api/v1/kg/my_kg/relationships"
)
relationships = response.json()
print(f"Total relationships: {relationships['count']}")
```

### Export a Graph
```python
response = requests.get(
    "http://localhost:8000/api/v1/kg/my_kg/export"
)
export_data = response.json()

# Save to file
import json
with open("my_graph.json", "w") as f:
    json.dump(export_data, f, indent=2)
```

### Delete a Graph
```python
response = requests.delete(
    "http://localhost:8000/api/v1/kg/my_kg"
)
print(response.json())
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file (or use `.env.example` as template):
```
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
FALKORDB_PASSWORD=
LOG_LEVEL=INFO
```

### Edit Configuration
Edit `kg_builder/config.py` to customize:
- FalkorDB connection settings
- Graphiti storage path
- API settings
- Logging level

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

# Parse schema
curl -X POST http://localhost:8000/api/v1/schemas/orderMgmt-catalog/parse

# Generate KG
curl -X POST http://localhost:8000/api/v1/kg/generate \
  -H "Content-Type: application/json" \
  -d '{"schema_name":"orderMgmt-catalog","kg_name":"test","backends":["graphiti"]}'

# Get entities
curl http://localhost:8000/api/v1/kg/test/entities

# Get relationships
curl http://localhost:8000/api/v1/kg/test/relationships

# Export graph
curl http://localhost:8000/api/v1/kg/test/export

# Delete graph
curl -X DELETE http://localhost:8000/api/v1/kg/test
```

## 📊 API Endpoints Quick Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/health` | Check health |
| GET | `/api/v1/schemas` | List schemas |
| POST | `/api/v1/schemas/{name}/parse` | Parse schema |
| POST | `/api/v1/kg/generate` | Generate KG |
| GET | `/api/v1/kg` | List graphs |
| GET | `/api/v1/kg/{name}/entities` | Get entities |
| GET | `/api/v1/kg/{name}/relationships` | Get relationships |
| POST | `/api/v1/kg/{name}/query` | Query graph |
| GET | `/api/v1/kg/{name}/export` | Export graph |
| DELETE | `/api/v1/kg/{name}` | Delete graph |

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
# Try a different port:
python -m kg_builder.main --port 8001
```

### FalkorDB connection error
This is normal if FalkorDB is not running. The app will use Graphiti's file-based storage instead.

### Schema file not found
- Ensure JSON files are in `schemas/` directory
- Use schema name without `.json` extension
- Example: `orderMgmt-catalog` (not `orderMgmt-catalog.json`)

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📁 Project Structure

```
kg_builder/              # Main application
├── config.py           # Configuration
├── models.py           # Data models
├── main.py             # FastAPI app
├── routes.py           # API endpoints
└── services/           # Business logic
    ├── schema_parser.py
    ├── falkordb_backend.py
    └── graphiti_backend.py

schemas/                # Input schemas
├── orderMgmt-catalog.json
└── qinspect-designcode.json

data/                   # Generated data
└── graphiti_storage/

Documentation/
├── README.md
├── QUICKSTART.md
├── API_EXAMPLES.md
├── IMPLEMENTATION_SUMMARY.md
├── PROJECT_INDEX.md
├── DELIVERABLES.md
└── GETTING_STARTED.md (this file)
```

## ✨ Key Features

✅ Parse JSON schema files
✅ Extract entities and relationships
✅ Build knowledge graphs
✅ Query graphs with Cypher or pattern matching
✅ Export graphs as JSON
✅ Automatic API documentation
✅ Error handling and validation
✅ Multiple backend support
✅ File-based fallback storage

## 🎓 Learning Path

1. **Start Here**: [QUICKSTART.md](QUICKSTART.md)
2. **Understand**: [README.md](README.md)
3. **Explore**: [API_EXAMPLES.md](API_EXAMPLES.md)
4. **Deep Dive**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
5. **Reference**: [PROJECT_INDEX.md](PROJECT_INDEX.md)

## 🚀 Next Steps

1. ✅ Install dependencies
2. ✅ Start the server
3. ✅ Run tests
4. ✅ Access Swagger UI
5. ✅ Generate your first knowledge graph
6. ✅ Explore the API
7. ✅ Read the documentation
8. ✅ Customize for your needs

## 💡 Tips

- Use Swagger UI (http://localhost:8000/docs) to explore endpoints interactively
- Check logs for debugging information
- Export graphs for backup and analysis
- Use Graphiti backend for development (no external dependencies)
- Monitor health endpoint before operations

## 📞 Support

For issues or questions:
1. Check [QUICKSTART.md](QUICKSTART.md)
2. Review [API_EXAMPLES.md](API_EXAMPLES.md)
3. Check troubleshooting section above
4. Review application logs

## 🎉 You're Ready!

Everything is set up and ready to use. Start with the quick start above and explore the API!

---

**Happy graphing!** 🎊

