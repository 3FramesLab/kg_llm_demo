# Knowledge Graph Builder

A FastAPI application that builds knowledge graphs from JSON schema files using **FalkorDB** and **Graphiti** backends, with **intelligent entity and relationship extraction powered by OpenAI**.

## Features

- 📊 **Parse JSON Schema Files**: Extract entities, relationships, and properties from database schemas
- 🤖 **LLM-Powered Intelligence**:
  - **Intelligent Entity Extraction**: Use OpenAI to understand business entities
  - **Relationship Analysis**: Automatically identify and describe relationships
  - **Schema Analysis**: Get comprehensive insights about your data model
- 🔗 **Dual Backend Support**:
  - **FalkorDB**: High-performance graph database
  - **Graphiti**: Temporal knowledge graph framework with fallback file-based storage
- 🚀 **RESTful API**: Complete FastAPI endpoints for all operations
- 📝 **Automatic Documentation**: Swagger UI and ReDoc available
- 🔍 **Query Support**: Execute queries on generated knowledge graphs
- 💾 **Export Functionality**: Export graphs in JSON format
- ✅ **Health Checks**: Monitor backend connectivity

## Project Structure

```
kg_builder/
├── __init__.py              # Package initialization
├── config.py                # Configuration settings
├── models.py                # Pydantic models
├── main.py                  # FastAPI application
├── routes.py                # API endpoints
└── services/
    ├── __init__.py
    ├── schema_parser.py     # Schema parsing logic
    ├── falkordb_backend.py  # FalkorDB integration
    ├── graphiti_backend.py  # Graphiti integration
    └── llm_service.py       # OpenAI LLM integration

schemas/                      # JSON schema files
├── orderMgmt-catalog.json
└── qinspect-designcode.json

data/
└── graphiti_storage/        # Graphiti local storage
```

## Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Setup

1. **Clone or navigate to the project directory**:
```bash
cd d:\learning\dq-poc
```

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
# or
source venv/bin/activate      # On Linux/Mac
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Optional: Install FalkorDB** (if not already installed):
```bash
pip install falkordb
```

5. **Optional: Install Graphiti** (if not already installed):
```bash
pip install graphiti-core
```

## Configuration

Edit `kg_builder/config.py` to customize:

- **FalkorDB Connection**:
  - `FALKORDB_HOST`: Default is `localhost`
  - `FALKORDB_PORT`: Default is `6379`
  - `FALKORDB_PASSWORD`: Optional password

- **Graphiti Storage**:
  - `GRAPHITI_STORAGE_PATH`: Default is `data/graphiti_storage`

- **API Settings**:
  - `CORS_ORIGINS`: CORS allowed origins
  - `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)

- **OpenAI LLM Settings** (for intelligent extraction):
  - `OPENAI_API_KEY`: Your OpenAI API key (required for LLM features)
  - `OPENAI_MODEL`: Model to use (default: "gpt-3.5-turbo")
  - `OPENAI_TEMPERATURE`: Creativity level 0-2 (default: 0.7)
  - `OPENAI_MAX_TOKENS`: Max response length (default: 2000)
  - `ENABLE_LLM_EXTRACTION`: Enable LLM extraction (default: true)
  - `ENABLE_LLM_ANALYSIS`: Enable LLM analysis (default: true)

See [LLM_INTEGRATION.md](LLM_INTEGRATION.md) for detailed LLM setup instructions.

## Running the Application

### Start the server:
```bash
python -m kg_builder.main
```

Or using uvicorn directly:
```bash
uvicorn kg_builder.main:app --reload --host 0.0.0.0 --port 8000
```

### Access the API:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

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

## Usage Examples

See `API_EXAMPLES.md` for detailed curl and Python examples.

## Architecture

### Schema Parsing
1. Load JSON schema file
2. Extract table entities
3. Identify important columns (UIDs, IDs, codes)
4. Infer relationships from column names and foreign keys
5. Build knowledge graph structure

### Backend Storage
- **FalkorDB**: Stores graphs using Cypher queries
- **Graphiti**: Stores graphs with temporal information (fallback: JSON files)

### Query Execution
- Supports Cypher queries for FalkorDB
- Pattern matching for Graphiti local storage

## Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
black kg_builder/
flake8 kg_builder/
mypy kg_builder/
```

## Troubleshooting

### FalkorDB Connection Issues
- Ensure FalkorDB server is running on configured host/port
- Check firewall settings
- Verify credentials if password is set

### Graphiti Not Available
- Application falls back to file-based JSON storage
- Install graphiti-core for full temporal features

### Schema File Not Found
- Ensure JSON files are in the `schemas/` directory
- Use correct schema name without `.json` extension

## Performance Considerations

- **Large Schemas**: May take time to parse and generate graphs
- **Query Performance**: Depends on graph size and query complexity
- **Storage**: Graphiti local storage uses disk space

## Future Enhancements

- [ ] Support for additional schema formats (YAML, XML)
- [ ] Advanced query builder UI
- [ ] Graph visualization
- [ ] Batch processing
- [ ] Schema versioning
- [ ] Access control and authentication

## License

MIT License

## Support

For issues or questions, please refer to the documentation or create an issue in the repository.

