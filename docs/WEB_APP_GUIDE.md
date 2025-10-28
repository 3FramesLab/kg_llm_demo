# DQ-POC Web Application Guide

## Overview

A modern, clean React web application for the DQ-POC Knowledge Graph Builder system. Built with Material-UI for a professional look and feel, with interactive graph visualization and comprehensive forms for all API operations.

## Features

### 🎯 Complete Feature Set

1. **Dashboard**
   - System health monitoring
   - FalkorDB, Graphiti, and LLM status
   - Real-time statistics (schemas, KGs, rulesets)
   - Quick start guide

2. **Schema Management**
   - View available database schemas
   - List all JSON schema files
   - Refresh capability

3. **Knowledge Graph Builder**
   - **Generate Tab**: Create KGs from schemas
     - Multi-schema selection
     - LLM enhancement toggle
     - Backend selection (FalkorDB/Graphiti)
   - **View Tab**: Interactive graph visualization
     - Force-directed graph layout
     - Zoom and pan controls
     - Entity and relationship lists
   - **Manage Tab**: KG management
     - Export to JSON
     - Delete KGs

4. **Reconciliation Rules**
   - **Generate Tab**: Create reconciliation rules
     - Schema and KG selection
     - Confidence threshold slider
     - LLM enhancement option
   - **View Tab**: Browse and analyze rules
     - Detailed rule information
     - Confidence scores
     - Export to SQL
   - **Manage Tab**: Ruleset management

5. **Natural Language Relationships**
   - Multi-format input support:
     - Plain English
     - Semi-structured
     - Pseudo-SQL
     - Business rules
   - LLM-powered parsing
   - Validation and confidence scoring
   - Result visualization

6. **Reconciliation Execution**
   - **SQL Export Mode**: Generate queries for manual execution
   - **Direct Execution Mode**: Execute against databases
   - Database configuration forms
   - Results visualization with statistics

## Tech Stack

- **React 18**: Modern React with hooks
- **Material-UI v5**: Professional UI components
- **React Router v6**: Client-side routing
- **React Force Graph 2D**: Interactive graph visualization
- **Axios**: API communication

## Quick Start

### Development Mode

```bash
cd web-app

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Edit .env with your API URL
echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > .env

# Start development server
npm start
```

Access at: http://localhost:3000

### Docker Mode

```bash
# From project root
docker-compose up -d

# Web app will be available at http://localhost:3000
# API will be available at http://localhost:8000
```

## Application Structure

```
web-app/
├── public/
│   └── index.html                 # HTML template
├── src/
│   ├── components/
│   │   ├── Layout.js              # Main layout with sidebar navigation
│   │   └── GraphVisualization.js  # Force-directed graph component
│   ├── pages/
│   │   ├── Dashboard.js           # System overview
│   │   ├── Schemas.js             # Schema listing
│   │   ├── KnowledgeGraph.js      # KG generation & visualization
│   │   ├── Reconciliation.js      # Rule generation
│   │   ├── NaturalLanguage.js     # NL relationship parsing
│   │   └── Execution.js           # Rule execution
│   ├── services/
│   │   └── api.js                 # Axios API client
│   ├── App.js                     # Main app with routing
│   └── index.js                   # Entry point
├── Dockerfile                     # Multi-stage build
├── nginx.conf                     # Production web server config
├── package.json                   # Dependencies
└── README.md                      # Documentation
```

## Component Details

### Layout Component (`components/Layout.js`)

**Features:**
- Persistent sidebar navigation
- Responsive drawer for mobile
- Active route highlighting
- Clean Material-UI AppBar

**Navigation Items:**
- Dashboard
- Schemas
- Knowledge Graph
- Reconciliation
- Natural Language
- Execution

### Dashboard (`pages/Dashboard.js`)

**Displays:**
- System health status
- FalkorDB connection status
- Graphiti availability
- LLM service status and model
- Statistics cards (schemas, KGs, rulesets)
- Quick start guide

**API Calls:**
- `GET /health`
- `GET /llm/status`
- `GET /schemas`
- `GET /kg`
- `GET /reconciliation/rulesets`

### Schemas Page (`pages/Schemas.js`)

**Features:**
- List all available schemas
- Refresh button
- Schema file location display
- Instructions for adding new schemas

**API Calls:**
- `GET /schemas`

### Knowledge Graph Page (`pages/KnowledgeGraph.js`)

**Three Tabs:**

**1. Generate Tab:**
- Schema multi-select checkboxes
- KG name input
- LLM enhancement toggle
- Backend selection
- Request/response placeholders

**2. View Tab:**
- Interactive force-directed graph visualization
- Entity count and relationship count chips
- Expandable entity list
- Expandable relationship list

**3. Manage Tab:**
- Card grid of existing KGs
- Backend badges
- View, Export, Delete actions

**API Calls:**
- `POST /kg/generate`
- `GET /kg`
- `GET /kg/{name}/entities`
- `GET /kg/{name}/relationships`
- `GET /kg/{name}/export`
- `DELETE /kg/{name}`

### GraphVisualization Component (`components/GraphVisualization.js`)

**Features:**
- Force-directed graph layout using `react-force-graph-2d`
- Node labels with entity names
- Directional arrows on relationships
- Auto-zoom to fit
- Color-coded by entity type
- Clickable nodes and links
- Legend showing node types

**Props:**
- `entities`: Array of entity objects
- `relationships`: Array of relationship objects

### Reconciliation Page (`pages/Reconciliation.js`)

**Three Tabs:**

**1. Generate Tab:**
- Schema multi-select
- KG dropdown selection
- LLM enhancement toggle
- Confidence threshold slider (0-1)
- Request/response placeholders

**2. View Tab:**
- Ruleset information header
- Export SQL button
- Detailed rules table with:
  - Rule name
  - Source table/columns
  - Target table/columns
  - Match type chip
  - Confidence score chip (color-coded)
  - Expandable details accordion

**3. Manage Tab:**
- Card grid of rulesets
- Rule count and schema badges
- View, Export SQL, Delete actions

**API Calls:**
- `POST /reconciliation/generate`
- `GET /reconciliation/rulesets`
- `GET /reconciliation/rulesets/{id}`
- `GET /reconciliation/rulesets/{id}/export/sql`
- `DELETE /reconciliation/rulesets/{id}`

### Natural Language Page (`pages/NaturalLanguage.js`)

**Features:**
- KG selection dropdown
- Schema multi-select
- Dynamic definition input fields
- Add/remove definition buttons
- LLM toggle
- Confidence threshold slider
- Format examples display
- Parsing results with validation status

**Supported Formats:**
1. Natural Language: "Products are supplied by Vendors"
2. Semi-Structured: "catalog.product_id → vendor.vendor_id (SUPPLIED_BY)"
3. Pseudo-SQL: "SELECT * FROM products JOIN vendors..."
4. Business Rules: "IF condition THEN relationship"

**Results Display:**
- Parsed count, valid count, invalid count chips
- Color-coded result items (green=valid, red=invalid)
- Relationship details for valid items
- Error messages for invalid items

**API Calls:**
- `POST /kg/relationships/natural-language`

### Execution Page (`pages/Execution.js`)

**Three Tabs:**

**1. SQL Export Mode:**
- Ruleset selection
- Limit input
- Generate SQL button
- Request placeholder
- Response placeholder with sample SQL

**2. Direct Execution Mode:**
- Ruleset selection
- Limit input
- Source database configuration accordion:
  - Host, Port, Database
  - Username, Password
- Target database configuration accordion:
  - Host, Port, Database
  - Username, Password
- Execute button
- Response placeholder with sample results

**3. Results Tab:**
- Execution mode display
- Summary chips (matched, unmatched source/target, match rate)
- SQL queries accordion (for SQL export mode)
- Results table (for direct execution mode):
  - Rule ID
  - Matched count (green chip)
  - Unmatched source count
  - Unmatched target count
  - Match rate percentage (color-coded)

**API Calls:**
- `POST /reconciliation/execute`

## API Service (`services/api.js`)

**Configuration:**
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
```

**Exported Functions:**
- `checkHealth()`
- `checkLLMStatus()`
- `listSchemas()`
- `generateKG(data)`
- `listKGs()`
- `getKGEntities(kgName)`
- `getKGRelationships(kgName)`
- `exportKG(kgName)`
- `deleteKG(kgName)`
- `generateRules(data)`
- `listRulesets()`
- `getRuleset(rulesetId)`
- `exportRulesetSQL(rulesetId)`
- `deleteRuleset(rulesetId)`
- `executeReconciliation(data)`
- `parseNLRelationships(data)`

## Request/Response Placeholders

Each page that makes API calls includes placeholder sections showing:

### Example Request Format
```json
{
  "kg_name": "example_kg",
  "schema_names": ["schema1", "schema2"],
  "use_llm_enhancement": true,
  "backends": ["falkordb", "graphiti"]
}
```

### Example Response Format
```json
{
  "kg_name": "example_kg",
  "status": "created",
  "node_count": 58,
  "relationship_count": 47,
  "llm_enhanced": true
}
```

These placeholders update based on user input in the forms.

## Styling and Theme

**Material-UI Theme:**
```javascript
{
  palette: {
    mode: 'light',
    primary: { main: '#1976d2' },    // Blue
    secondary: { main: '#dc004e' },  // Pink
    background: { default: '#f5f5f5' }
  }
}
```

**Design Principles:**
- Clean, professional interface
- Consistent spacing and typography
- Color-coded status indicators
- Responsive layout (desktop and mobile)
- Accessible navigation
- Clear visual hierarchy

## Docker Deployment

### Multi-Stage Dockerfile

**Stage 1: Build**
- Node 18 Alpine
- Install dependencies
- Build production bundle

**Stage 2: Production**
- Nginx Alpine
- Copy built files
- Serve static files
- Proxy API requests

### Nginx Configuration

**Features:**
- SPA routing (serve index.html for all routes)
- Static asset caching (1 year)
- Gzip compression
- API proxy to backend at `/api/`
- Proper headers for security

**API Proxy:**
```nginx
location /api/ {
    proxy_pass http://app:8000/api/;
    # ... proxy headers
}
```

## Docker Compose Integration

### Service Definition

```yaml
web:
  build:
    context: ./web-app
    dockerfile: Dockerfile
  container_name: kg-builder-web
  ports:
    - "3000:80"
  environment:
    - REACT_APP_API_URL=http://localhost:8000/api/v1
  depends_on:
    app:
      condition: service_healthy
  networks:
    - kg-network
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 20s
```

### Complete Stack

When you run `docker-compose up`:
1. **FalkorDB** starts on port 6379
2. **Backend API** starts on port 8000 (waits for FalkorDB)
3. **Web App** starts on port 3000 (waits for Backend)

Access:
- Web UI: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development Workflow

### 1. Start Backend First
```bash
# Terminal 1: Start backend services
docker-compose up falkordb app
```

### 2. Start Frontend Separately
```bash
# Terminal 2: Start web app in dev mode
cd web-app
npm start
```

**Benefits:**
- Hot reload for frontend changes
- Faster development iteration
- Backend runs in Docker (consistent environment)

### 3. Full Docker Stack
```bash
# Production-like environment
docker-compose up -d
```

## Environment Variables

### Development (.env)
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### Docker
```yaml
environment:
  - REACT_APP_API_URL=http://localhost:8000/api/v1
```

**Note:** In Docker, the web app is served by nginx on port 80 (container) mapped to 3000 (host).

## Common Tasks

### Adding a New Page

1. Create page component in `src/pages/NewPage.js`
2. Add route in `src/App.js`:
   ```javascript
   <Route path="/new-page" element={<NewPage />} />
   ```
3. Add menu item in `src/components/Layout.js`:
   ```javascript
   { text: 'New Page', icon: <Icon />, path: '/new-page' }
   ```

### Adding a New API Endpoint

1. Add function to `src/services/api.js`:
   ```javascript
   export const newEndpoint = (data) => api.post('/new-endpoint', data);
   ```
2. Import and use in component:
   ```javascript
   import { newEndpoint } from '../services/api';

   const handleSubmit = async () => {
     const response = await newEndpoint(data);
   };
   ```

### Customizing Theme

Edit `src/App.js`:
```javascript
const theme = createTheme({
  palette: {
    primary: { main: '#your-color' },
    secondary: { main: '#your-color' }
  }
});
```

## Troubleshooting

### API Connection Failed

**Symptom:** Network errors in browser console

**Solutions:**
1. Check backend is running: `docker-compose ps`
2. Verify API URL in `.env`
3. Check CORS settings in backend
4. Inspect network tab in browser dev tools

### Graph Not Rendering

**Symptom:** Blank graph visualization

**Solutions:**
1. Check if entities and relationships are loaded
2. Open browser console for errors
3. Verify data format matches expected structure
4. Check if `react-force-graph-2d` is installed

### Docker Build Fails

**Symptom:** Build errors during `docker-compose up`

**Solutions:**
```bash
# Clear cache and rebuild
docker-compose build --no-cache web

# Check Dockerfile syntax
docker build -t test ./web-app

# Verify node_modules not in build context
cat web-app/.dockerignore
```

### Page Not Found (404)

**Symptom:** Refreshing page gives 404 error

**Solution:** This is handled by nginx.conf serving index.html for all routes. If using a different web server, configure SPA routing.

## Performance Optimization

### Production Build

```bash
# Build optimized bundle
npm run build

# Analyze bundle size
npm install --save-dev webpack-bundle-analyzer
```

### Lazy Loading

Implement code splitting:
```javascript
const KnowledgeGraph = lazy(() => import('./pages/KnowledgeGraph'));

<Suspense fallback={<CircularProgress />}>
  <KnowledgeGraph />
</Suspense>
```

### Memoization

Use React.memo for expensive components:
```javascript
export default React.memo(GraphVisualization);
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` files
2. **API Keys**: Backend handles OpenAI keys, not exposed to frontend
3. **Database Credentials**: Only sent in POST requests, not stored
4. **XSS Protection**: Material-UI components escape content by default
5. **CORS**: Backend configures allowed origins

## Future Enhancements

Potential additions:
- [ ] User authentication and authorization
- [ ] Saved query history
- [ ] Export results to CSV/Excel
- [ ] Real-time updates with WebSockets
- [ ] Dark mode toggle
- [ ] Advanced graph filtering and search
- [ ] Rule versioning and comparison
- [ ] Scheduled reconciliation jobs
- [ ] Email notifications for results
- [ ] Multi-language support

## Resources

- [React Documentation](https://react.dev)
- [Material-UI Documentation](https://mui.com)
- [React Router Documentation](https://reactrouter.com)
- [React Force Graph](https://github.com/vasturiano/react-force-graph)
- [Nginx Documentation](https://nginx.org/en/docs/)

## Support

For issues or questions:
1. Check the console for error messages
2. Review API response in Network tab
3. Verify backend is healthy: `curl http://localhost:8000/health`
4. Check Docker logs: `docker-compose logs web`

---

**Congratulations!** You now have a fully functional, modern web interface for the DQ-POC Knowledge Graph Builder system.

Access the application at **http://localhost:3000** after running `docker-compose up -d`
