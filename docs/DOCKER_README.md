# Docker Setup for Knowledge Graph Builder

## 🎯 Overview

This project is fully containerized with Docker and ready for deployment in any environment:
- **Local Development** - Docker Compose
- **Staging** - Docker Compose on server
- **Production** - Docker Swarm or Kubernetes

## 🚀 Quick Start (30 seconds)

```bash
# 1. Start services
docker-compose up -d

# 2. Wait for services to be healthy (30-40 seconds)
docker-compose ps

# 3. Access the application
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
```

## 📦 What's Included

### Docker Files
- **Dockerfile** - Multi-stage build (optimized ~500MB)
- **docker-compose.yml** - Orchestrates app + FalkorDB
- **.dockerignore** - Excludes unnecessary files

### Services
- **kg-builder-app** - FastAPI application (port 8000)
- **kg-builder-falkordb** - Graph database (port 6379)

### Documentation
- **DOCKER_QUICK_START.md** - 30-second setup
- **DOCKER_GUIDE.md** - Complete reference
- **DOCKER_DEPLOYMENT.md** - Production guide
- **k8s-deployment.yaml** - Kubernetes template

## 🔧 Configuration

### Environment Variables

Edit `.env` file:

```env
# FalkorDB
FALKORDB_HOST=falkordb
FALKORDB_PORT=6379
FALKORDB_PASSWORD=

# OpenAI (for LLM features)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# Logging
LOG_LEVEL=INFO

# LLM Features
ENABLE_LLM_EXTRACTION=true
ENABLE_LLM_ANALYSIS=true
```

Then restart:
```bash
docker-compose restart app
```

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│     Knowledge Graph Builder API         │
│     (FastAPI + Uvicorn)                 │
│     Port: 8000                          │
└──────────────────┬──────────────────────┘
                   │
                   │ (Redis Protocol)
                   │
┌──────────────────▼──────────────────────┐
│     FalkorDB (Graph Database)           │
│     (Redis-based)                       │
│     Port: 6379                          │
└─────────────────────────────────────────┘
```

## 🎮 Common Commands

| Command | Purpose |
|---------|---------|
| `docker-compose up -d` | Start all services |
| `docker-compose down` | Stop all services |
| `docker-compose logs -f app` | View app logs |
| `docker-compose ps` | Check service status |
| `docker-compose build --no-cache` | Rebuild image |
| `docker-compose exec app bash` | Access container shell |
| `docker-compose restart app` | Restart app service |
| `docker-compose down -v` | Stop and remove volumes |

## 📋 Verification

### Check Services

```bash
docker-compose ps
```

Expected:
```
NAME                    STATUS
kg-builder-app          Up (healthy)
kg-builder-falkordb     Up (healthy)
```

### Test API

```bash
# Health check
curl http://localhost:8000/health

# API documentation
curl http://localhost:8000/docs

# List schemas
curl http://localhost:8000/api/v1/schemas
```

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

## 💾 Data Persistence

| Path | Purpose |
|------|---------|
| `./data` | Graphiti storage, reconciliation rules |
| `./schemas` | JSON schema files |
| `./jdbc_drivers` | Database driver JARs |
| `./logs` | Application logs |
| `falkordb-data` | FalkorDB graph data (Docker volume) |

### Backup

```bash
# Backup FalkorDB
docker run --rm -v kg-builder-falkordb-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/falkordb-backup.tar.gz -C /data .

# Backup application data
tar czf app-data-backup.tar.gz data/ schemas/ logs/
```

## 🐛 Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose logs

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Port already in use

```bash
# Change port in docker-compose.yml
# Or kill process using port
# Windows: netstat -ano | findstr :8000
# Linux: lsof -i :8000
```

### FalkorDB connection error

```bash
# Restart FalkorDB
docker-compose restart falkordb

# Test connection
docker-compose exec app redis-cli -h falkordb ping
```

### Out of memory

```bash
# Increase Docker memory limit
# Docker Desktop: Settings → Resources → Memory
```

## 📈 Performance

| Metric | Value |
|--------|-------|
| Image Size | ~500MB |
| Startup Time | 30-40 seconds |
| Memory Usage | ~400-500MB |
| Disk Space | ~500MB image + data |
| CPU (idle) | <1% |

## 🔐 Security

- ✅ Non-root user (appuser)
- ✅ Network isolation
- ✅ Secrets in .env (not in image)
- ✅ Health checks enabled
- ✅ Minimal base image

## 🚢 Deployment

### Local Development
```bash
docker-compose up -d
```

### Staging Server
See `docs/DOCKER_DEPLOYMENT.md` for detailed instructions

### Production (Docker Swarm)
```bash
docker stack deploy -c docker-compose.yml kg-builder
```

### Production (Kubernetes)
```bash
kubectl apply -f k8s-deployment.yaml
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **DOCKER_QUICK_START.md** | 30-second setup guide |
| **DOCKER_GUIDE.md** | Complete Docker reference |
| **DOCKER_DEPLOYMENT.md** | Production deployment |
| **k8s-deployment.yaml** | Kubernetes template |

## ✨ Features

### Development
- ✅ Hot reload enabled
- ✅ Debug logging available
- ✅ Easy shell access
- ✅ Volume mounts for code changes

### Production Ready
- ✅ Multi-stage build (optimized)
- ✅ Non-root user (security)
- ✅ Health checks (auto-restart)
- ✅ Persistent volumes
- ✅ Network isolation
- ✅ Resource limits

## 🔍 Health Checks

Services have built-in health checks:

```bash
# App health
curl http://localhost:8000/health

# FalkorDB health
docker-compose exec falkordb redis-cli ping

# View health status
docker-compose ps
```

## 📞 Support

1. **Quick Setup**: Read `DOCKER_QUICK_START.md`
2. **Full Reference**: Read `DOCKER_GUIDE.md`
3. **Production**: Read `DOCKER_DEPLOYMENT.md`
4. **Check Logs**: `docker-compose logs -f app`
5. **API Docs**: http://localhost:8000/docs

## ✅ Next Steps

1. Start services: `docker-compose up -d`
2. Verify health: `curl http://localhost:8000/health`
3. Access API: http://localhost:8000/docs
4. Read documentation: `docs/DOCKER_QUICK_START.md`
5. Deploy: Follow `docs/DOCKER_DEPLOYMENT.md`

---

**Your project is fully dockerized and ready to deploy!** 🎉

For detailed information, see the documentation files in the `docs/` directory.

