# Docker Guide for Knowledge Graph Builder

## Overview

This project is fully dockerized with:
- **FastAPI Application** - Main KG Builder service
- **FalkorDB** - Graph database (Redis-based)
- **Docker Compose** - Orchestration
- **Multi-stage Build** - Optimized image size

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v1.29+
- 4GB+ RAM available
- 2GB+ disk space

## Quick Start

### 1. Build and Run

```bash
# Build the Docker image
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app
```

### 2. Access the Application

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **FalkorDB**: localhost:6379

### 3. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Configuration

### Environment Variables

Create or update `.env` file:

```env
# FalkorDB
FALKORDB_HOST=falkordb
FALKORDB_PORT=6379
FALKORDB_PASSWORD=

# OpenAI
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# Logging
LOG_LEVEL=INFO

# LLM Features
ENABLE_LLM_EXTRACTION=true
ENABLE_LLM_ANALYSIS=true
```

### Database Connections (Optional)

For connecting to source/target databases:

```env
SOURCE_DB_TYPE=oracle
SOURCE_DB_HOST=your_host
SOURCE_DB_PORT=1521
SOURCE_DB_DATABASE=your_db
SOURCE_DB_USERNAME=user
SOURCE_DB_PASSWORD=pass

TARGET_DB_TYPE=oracle
TARGET_DB_HOST=your_host
TARGET_DB_PORT=1521
TARGET_DB_DATABASE=your_db
TARGET_DB_USERNAME=user
TARGET_DB_PASSWORD=pass
```

## Docker Compose Services

### App Service
- **Image**: Built from Dockerfile
- **Port**: 8000
- **Depends on**: FalkorDB
- **Volumes**: 
  - `./data` - Persistent data
  - `./schemas` - Schema files
  - `./jdbc_drivers` - Database drivers
  - `./.env` - Configuration

### FalkorDB Service
- **Image**: falkordb/falkordb:latest
- **Port**: 6379
- **Volume**: `falkordb-data` - Persistent graph data
- **Health Check**: Redis ping

## Common Tasks

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs app
docker-compose logs falkordb

# Follow logs
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app
```

### Execute Commands in Container

```bash
# Run Python command
docker-compose exec app python -c "import kg_builder; print('OK')"

# Run shell
docker-compose exec app /bin/bash

# Run tests
docker-compose exec app pytest
```

### Rebuild Image

```bash
# Rebuild without cache
docker-compose build --no-cache

# Rebuild specific service
docker-compose build --no-cache app
```

### Check Container Status

```bash
# List running containers
docker-compose ps

# Inspect container
docker inspect kg-builder-app

# Check health
docker-compose ps | grep app
```

## Volumes and Data Persistence

### Volumes Used

| Volume | Purpose | Persistence |
|--------|---------|-------------|
| `./data` | Graphiti storage, reconciliation rules | Host directory |
| `./schemas` | JSON schema files | Host directory |
| `./jdbc_drivers` | Database driver JARs | Host directory |
| `./logs` | Application logs | Host directory |
| `falkordb-data` | FalkorDB graph data | Docker volume |

### Backup Data

```bash
# Backup FalkorDB data
docker run --rm -v kg-builder-falkordb-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/falkordb-backup.tar.gz -C /data .

# Backup application data
tar czf app-data-backup.tar.gz data/ schemas/ logs/
```

### Restore Data

```bash
# Restore FalkorDB data
docker run --rm -v kg-builder-falkordb-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/falkordb-backup.tar.gz -C /data

# Restore application data
tar xzf app-data-backup.tar.gz
```

## Networking

### Network Configuration

- **Network Name**: `kg-builder-network`
- **Driver**: Bridge
- **Services**: app, falkordb

### Access Between Containers

- App → FalkorDB: Use hostname `falkordb:6379`
- External → App: Use `localhost:8000`
- External → FalkorDB: Use `localhost:6379`

## Performance Optimization

### Image Size

- **Builder Stage**: ~1.2GB (includes build tools)
- **Runtime Stage**: ~600MB (only runtime dependencies)
- **Final Image**: ~500MB (after optimization)

### Memory Usage

- **App Container**: ~200-300MB
- **FalkorDB Container**: ~100-200MB
- **Total**: ~400-500MB

### CPU Usage

- **App**: 1-2 cores (depends on load)
- **FalkorDB**: <1 core (idle)

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs app

# Check health
docker-compose ps

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### FalkorDB Connection Error

```bash
# Check FalkorDB is running
docker-compose ps falkordb

# Test connection
docker-compose exec app redis-cli -h falkordb ping

# Restart FalkorDB
docker-compose restart falkordb
```

### Port Already in Use

```bash
# Change port in docker-compose.yml
# Or kill process using port
# Windows: netstat -ano | findstr :8000
# Linux: lsof -i :8000
```

### Out of Memory

```bash
# Increase Docker memory limit
# Docker Desktop: Settings → Resources → Memory

# Or limit container memory
# Add to docker-compose.yml:
# mem_limit: 2g
```

## Production Deployment

### Security Considerations

1. **Use secrets** for sensitive data (not .env)
2. **Set FalkorDB password** in production
3. **Use non-root user** (already configured)
4. **Enable HTTPS** with reverse proxy
5. **Restrict network access** with firewall

### Scaling

```bash
# Scale app service (requires load balancer)
docker-compose up -d --scale app=3

# Use Docker Swarm or Kubernetes for production
```

### Monitoring

```bash
# Monitor resource usage
docker stats

# View container events
docker events --filter type=container

# Collect logs
docker-compose logs > app.log
```

## Advanced Usage

### Custom Docker Compose Override

Create `docker-compose.override.yml`:

```yaml
version: '3.8'
services:
  app:
    environment:
      - LOG_LEVEL=DEBUG
    ports:
      - "8001:8000"
```

### Build with Custom Registry

```bash
# Tag image
docker tag kg-builder:latest myregistry.azurecr.io/kg-builder:latest

# Push to registry
docker push myregistry.azurecr.io/kg-builder:latest

# Pull and run
docker pull myregistry.azurecr.io/kg-builder:latest
docker run -p 8000:8000 myregistry.azurecr.io/kg-builder:latest
```

## Useful Commands Reference

```bash
# Build
docker-compose build
docker-compose build --no-cache

# Run
docker-compose up -d
docker-compose up

# Stop
docker-compose stop
docker-compose down
docker-compose down -v

# Logs
docker-compose logs
docker-compose logs -f app
docker-compose logs --tail=100

# Execute
docker-compose exec app bash
docker-compose exec app python -m pytest

# Status
docker-compose ps
docker ps -a

# Clean
docker system prune
docker volume prune
```

## Support

For issues or questions:
1. Check logs: `docker-compose logs app`
2. Verify configuration: Check `.env` file
3. Test connectivity: `docker-compose exec app curl http://falkordb:6379`
4. Review documentation: See README.md and other docs/


