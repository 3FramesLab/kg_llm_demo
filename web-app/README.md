# DQ-POC Web Application

Modern React web interface for the Data Quality Knowledge Graph Builder.

## Features

- **Dashboard**: System health and statistics overview
- **Schemas**: View and manage database schemas
- **Knowledge Graph**: Generate and visualize knowledge graphs with interactive graph visualization
- **Reconciliation**: Generate data matching rules from knowledge graphs
- **Natural Language**: Define relationships using plain English
- **Execution**: Execute reconciliation rules and view results

## Tech Stack

- React 18
- Material-UI (MUI) v5
- React Router v6
- Axios for API calls
- React Force Graph 2D for graph visualization

## Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm start
```

The app will be available at http://localhost:3000

### Environment Variables

Create a `.env` file in the root directory:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## Docker Deployment

### Build the image

```bash
docker build -t dq-poc-web .
```

### Run the container

```bash
docker run -p 3000:80 dq-poc-web
```

### Using Docker Compose

The web app is included in the main docker-compose.yml file:

```bash
# From the project root
docker-compose up -d
```

Access the web app at http://localhost:3000

## Project Structure

```
web-app/
├── public/                 # Static files
├── src/
│   ├── components/        # Reusable components
│   │   ├── Layout.js      # Main layout with navigation
│   │   └── GraphVisualization.js  # Graph visualization component
│   ├── pages/            # Page components
│   │   ├── Dashboard.js
│   │   ├── Schemas.js
│   │   ├── KnowledgeGraph.js
│   │   ├── Reconciliation.js
│   │   ├── NaturalLanguage.js
│   │   └── Execution.js
│   ├── services/         # API services
│   │   └── api.js        # Axios API client
│   ├── App.js            # Main app component
│   └── index.js          # Entry point
├── Dockerfile            # Docker build configuration
├── nginx.conf           # Nginx configuration for production
└── package.json         # Dependencies
```

## Available Scripts

- `npm start` - Start development server (port 3000)
- `npm build` - Build production bundle
- `npm test` - Run tests
- `npm eject` - Eject from create-react-app (not recommended)

## API Integration

The app communicates with the backend API at `/api/v1`. All API endpoints are defined in `src/services/api.js`.

### API Endpoints Used

- `/health` - System health check
- `/schemas` - List available schemas
- `/kg/generate` - Generate knowledge graphs
- `/kg/{name}/entities` - Get KG entities
- `/kg/{name}/relationships` - Get KG relationships
- `/reconciliation/generate` - Generate reconciliation rules
- `/reconciliation/execute` - Execute rules
- `/kg/relationships/natural-language` - Parse NL relationships

## Features Guide

### 1. Dashboard

View system status, health checks, and statistics:
- FalkorDB connection status
- Graphiti availability
- LLM service status
- Schema, KG, and ruleset counts

### 2. Schemas

Browse available database schemas that can be used to generate knowledge graphs.

### 3. Knowledge Graph

**Generate Tab**: Create new knowledge graphs from one or more schemas
- Select schemas
- Enable/disable LLM enhancement
- Configure backends (FalkorDB, Graphiti)

**View Tab**: Visualize knowledge graph structure
- Interactive force-directed graph
- Entity and relationship lists
- Zoom and pan controls

**Manage Tab**: List, export, and delete knowledge graphs

### 4. Reconciliation

**Generate Tab**: Create reconciliation rules from knowledge graphs
- Select schemas and knowledge graph
- Configure minimum confidence threshold
- Enable LLM-based semantic rule generation

**View Tab**: Browse generated rules
- View rule details
- Export rules as SQL

**Manage Tab**: Manage rulesets
- List all rulesets
- Delete rulesets

### 5. Natural Language

Define custom relationships using natural language:
- Plain English: "Products are supplied by Vendors"
- Semi-structured: "catalog.product_id → vendor.vendor_id (SUPPLIED_BY)"
- Pseudo-SQL: "SELECT * FROM products JOIN vendors..."
- Business rules: "IF product.status='active' THEN..."

### 6. Execution

Execute reconciliation rules in two modes:

**SQL Export Mode**: Generate SQL queries for manual execution
- No database credentials required
- Copy queries to your database client

**Direct Execution Mode**: Execute rules directly against databases
- Configure source and target database connections
- View matched and unmatched records
- See reconciliation statistics

## Troubleshooting

### API Connection Issues

If the web app can't connect to the backend API:

1. Check the API URL in `.env` file
2. Ensure backend is running: `docker-compose ps`
3. Check backend logs: `docker-compose logs app`

### Development Server Issues

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear npm cache
npm cache clean --force
```

### Docker Build Issues

```bash
# Rebuild without cache
docker build --no-cache -t dq-poc-web .

# Check Docker logs
docker logs <container-id>
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

Part of the DQ-POC project.
