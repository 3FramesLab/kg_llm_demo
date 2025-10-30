# Quick Start: Web Application

## Option 1: Full Docker Stack (Recommended)

Start everything with one command:

```bash
docker-compose up -d
```

Wait 30-40 seconds for all services to start, then access:
- **Web App**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Option 2: Development Mode

Start backend in Docker, frontend locally for faster development:

```bash
# Terminal 1: Start backend services
docker-compose up falkordb app

# Terminal 2: Start web app
cd web-app
npm install
npm start
```

Access at: http://localhost:3000

## Verify Installation

1. **Check Services:**
   ```bash
   docker-compose ps
   ```
   All services should be "Up" and "healthy"

2. **Test Web App:**
   - Open http://localhost:3000
   - Dashboard should show system health
   - Navigate through all pages

3. **Test API:**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

## Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Troubleshooting

### Web App Not Loading

```bash
# Check logs
docker-compose logs web

# Rebuild
docker-compose build --no-cache web
docker-compose up -d
```

### API Connection Error

1. Verify backend is running: `docker-compose ps`
2. Check backend logs: `docker-compose logs app`
3. Test API directly: `curl http://localhost:8000/api/v1/health`

### Port Already in Use

If port 3000 or 8000 is already in use, edit docker-compose.yml:

```yaml
web:
  ports:
    - "3001:80"  # Change 3000 to 3001

app:
  ports:
    - "8001:8000"  # Change 8000 to 8001
```

## Next Steps

1. Visit **Dashboard** to see system status
2. Go to **Schemas** to see available database schemas
3. Navigate to **Knowledge Graph** to create your first KG
4. Check out **Reconciliation** to generate rules
5. Try **Natural Language** to define relationships in plain English
6. Use **Execution** to run reconciliation and see results

Enjoy using DQ-POC! 🚀
