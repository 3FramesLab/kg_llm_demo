# Docker Quick Start Guide

## 30-Second Setup

```bash
# 1. Navigate to project directory
cd d:\learning\dq-poc

# 2. Build and start
docker-compose up -d

# 3. Wait for services to be healthy (30-40 seconds)
docker-compose ps

# 4. Access the app
# Browser: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Verify Everything Works

```bash
# Check services are running
docker-compose ps

# Test API
curl http://localhost:8000/

# View logs
docker-compose logs app
```

## Common Commands

| Task | Command |
|------|---------|
| **Start** | `docker-compose up -d` |
| **Stop** | `docker-compose down` |
| **Logs** | `docker-compose logs -f app` |
| **Rebuild** | `docker-compose build --no-cache` |
| **Shell** | `docker-compose exec app bash` |
| **Status** | `docker-compose ps` |
| **Clean** | `docker-compose down -v` |

## Configuration

### Set OpenAI API Key

Edit `.env`:
```env
OPENAI_API_KEY=sk-your-key-here
```

Then restart:
```bash
docker-compose restart app
```

### Change Log Level

Edit `.env`:
```env
LOG_LEVEL=DEBUG  # or INFO, WARNING, ERROR
```

Then restart:
```bash
docker-compose restart app
```

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Port 8000 already in use
```bash
# Change port in docker-compose.yml
# Or kill the process using the port
```

### FalkorDB connection error
```bash
# Restart FalkorDB
docker-compose restart falkordb

# Check connection
docker-compose exec app redis-cli -h falkordb ping
```

## Next Steps

1. **Read Full Guide**: See `docs/DOCKER_GUIDE.md`
2. **Test API**: Visit http://localhost:8000/docs
3. **Generate KG**: Use the API endpoints
4. **View Logs**: `docker-compose logs -f app`
5. **Deploy**: See production section in DOCKER_GUIDE.md

## File Structure

```
dq-poc/
├── Dockerfile              # Multi-stage build
├── docker-compose.yml      # Service orchestration
├── .dockerignore           # Build exclusions
├── .env                    # Configuration
├── requirements.txt        # Python dependencies
├── kg_builder/             # Application code
├── schemas/                # JSON schemas
├── data/                   # Persistent data
└── docs/
    ├── DOCKER_GUIDE.md     # Full documentation
    └── DOCKER_QUICK_START.md  # This file
```

## Health Checks

Services have built-in health checks:

```bash
# Check app health
curl http://localhost:8000/

# Check FalkorDB health
docker-compose exec falkordb redis-cli ping

# View health status
docker-compose ps
```

## Performance

- **Startup Time**: 30-40 seconds
- **Memory Usage**: ~400-500MB
- **Disk Space**: ~500MB for image + data
- **CPU**: Minimal when idle

## Security Notes

- App runs as non-root user (appuser)
- Sensitive data in `.env` (not in image)
- Network isolated to `kg-builder-network`
- Health checks enabled

## Getting Help

1. Check logs: `docker-compose logs app`
2. Verify config: Check `.env` file
3. Test connectivity: `docker-compose exec app curl http://falkordb:6379`
4. Read full guide: `docs/DOCKER_GUIDE.md`

---

**Ready to go!** 🚀 Your Knowledge Graph Builder is now running in Docker.

