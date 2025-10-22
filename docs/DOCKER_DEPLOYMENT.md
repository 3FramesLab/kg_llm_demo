# Docker Deployment Guide

## Local Development

### Setup

```bash
# Clone/navigate to project
cd d:\learning\dq-poc

# Create .env file with your settings
cp .env.example .env  # or edit existing .env

# Build and start
docker-compose up -d

# Verify
docker-compose ps
curl http://localhost:8000/health
```

### Development Workflow

```bash
# View logs in real-time
docker-compose logs -f app

# Make code changes (auto-reload enabled)
# Changes are reflected immediately

# Run tests
docker-compose exec app pytest

# Access shell
docker-compose exec app bash
```

## Staging Deployment

### Prerequisites

- Docker and Docker Compose installed
- Server with 4GB+ RAM
- 10GB+ disk space
- Network access to required services

### Deployment Steps

1. **Prepare Server**
```bash
# SSH into server
ssh user@staging-server

# Clone repository
git clone <repo-url>
cd dq-poc

# Create .env with staging config
nano .env
```

2. **Configure Environment**
```env
# .env for staging
FALKORDB_HOST=falkordb
FALKORDB_PORT=6379
FALKORDB_PASSWORD=staging-password-here

OPENAI_API_KEY=sk-staging-key
LOG_LEVEL=INFO

# Database connections (if needed)
SOURCE_DB_HOST=staging-db-host
SOURCE_DB_PORT=1521
SOURCE_DB_USERNAME=staging_user
SOURCE_DB_PASSWORD=staging_pass
```

3. **Deploy**
```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# Verify health
docker-compose ps
curl http://localhost:8000/health
```

4. **Monitor**
```bash
# Check logs
docker-compose logs -f app

# Monitor resources
docker stats

# Check health periodically
watch -n 5 'docker-compose ps'
```

## Production Deployment

### Architecture

```
┌─────────────────────────────────────────┐
│         Load Balancer (Nginx)           │
│         (Port 80/443)                   │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
    ┌───▼────┐           ┌───▼────┐
    │ App 1  │           │ App 2  │
    │ :8000  │           │ :8000  │
    └───┬────┘           └───┬────┘
        │                     │
        └──────────┬──────────┘
                   │
            ┌──────▼──────┐
            │  FalkorDB   │
            │  :6379      │
            └─────────────┘
```

### Prerequisites

- Docker Swarm or Kubernetes cluster
- Persistent storage (NFS, EBS, etc.)
- Load balancer (Nginx, HAProxy, etc.)
- Monitoring stack (Prometheus, Grafana)
- Backup solution

### Production Setup

1. **Create Production .env**
```env
# Security
FALKORDB_PASSWORD=<strong-password>
OPENAI_API_KEY=<production-key>

# Performance
LOG_LEVEL=WARNING
OPENAI_TEMPERATURE=0.5

# Database
SOURCE_DB_HOST=prod-db-host
SOURCE_DB_PORT=1521
SOURCE_DB_USERNAME=prod_user
SOURCE_DB_PASSWORD=<strong-password>
```

2. **Docker Swarm Deployment**
```bash
# Initialize swarm
docker swarm init

# Create secrets
echo "strong-password" | docker secret create falkordb_password -
echo "sk-prod-key" | docker secret create openai_key -

# Deploy stack
docker stack deploy -c docker-compose.yml kg-builder
```

3. **Kubernetes Deployment**
```bash
# Create namespace
kubectl create namespace kg-builder

# Create secrets
kubectl create secret generic kg-secrets \
  --from-literal=falkordb-password=<password> \
  --from-literal=openai-key=<key> \
  -n kg-builder

# Deploy
kubectl apply -f k8s-deployment.yaml -n kg-builder
```

### Scaling

```bash
# Docker Swarm
docker service scale kg-builder_app=3

# Kubernetes
kubectl scale deployment kg-builder-app --replicas=3 -n kg-builder
```

### Monitoring

```bash
# Prometheus metrics
curl http://localhost:8000/metrics

# Health check
curl http://localhost:8000/health

# Logs
docker logs <container-id>
kubectl logs -f deployment/kg-builder-app -n kg-builder
```

## Backup and Recovery

### Backup Strategy

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/kg-builder"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup FalkorDB
docker run --rm \
  -v kg-builder-falkordb-data:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/falkordb_$DATE.tar.gz -C /data .

# Backup application data
tar czf $BACKUP_DIR/app_data_$DATE.tar.gz data/ schemas/

# Keep only last 7 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### Recovery

```bash
# Restore FalkorDB
docker run --rm \
  -v kg-builder-falkordb-data:/data \
  -v /backups/kg-builder:/backup \
  alpine tar xzf /backup/falkordb_YYYYMMDD_HHMMSS.tar.gz -C /data

# Restore application data
tar xzf /backups/kg-builder/app_data_YYYYMMDD_HHMMSS.tar.gz

# Restart services
docker-compose restart
```

## Troubleshooting

### Container Crashes

```bash
# Check logs
docker-compose logs app

# Check resource limits
docker stats

# Increase memory if needed
# Edit docker-compose.yml:
# mem_limit: 4g
```

### Database Connection Issues

```bash
# Test FalkorDB connection
docker-compose exec app redis-cli -h falkordb ping

# Check network
docker network inspect kg-builder-network

# Restart FalkorDB
docker-compose restart falkordb
```

### Performance Issues

```bash
# Monitor resource usage
docker stats

# Check slow queries
docker-compose exec app redis-cli -h falkordb slowlog get 10

# Optimize FalkorDB
docker-compose exec falkordb redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## Security Hardening

### Network Security

```yaml
# docker-compose.yml
services:
  app:
    networks:
      - kg-network
    # Don't expose to host network
    # ports:
    #   - "8000:8000"
```

### Secrets Management

```bash
# Use Docker secrets (Swarm)
echo "password" | docker secret create db_password -

# Use environment files
docker-compose --env-file .env.prod up -d

# Use external secret management
# - HashiCorp Vault
# - AWS Secrets Manager
# - Azure Key Vault
```

### Image Security

```bash
# Scan for vulnerabilities
docker scan kg-builder:latest

# Use minimal base image
# Already using python:3.11-slim

# Sign images
docker trust sign kg-builder:latest
```

## Rollback Procedure

```bash
# Keep previous image versions
docker tag kg-builder:latest kg-builder:v1.0.0

# Rollback to previous version
docker-compose down
docker-compose up -d  # Uses previous image

# Or explicit version
docker pull kg-builder:v1.0.0
docker tag kg-builder:v1.0.0 kg-builder:latest
docker-compose up -d
```

## Maintenance

### Regular Tasks

- **Daily**: Monitor logs and health
- **Weekly**: Backup data
- **Monthly**: Update dependencies
- **Quarterly**: Security audit

### Update Procedure

```bash
# Pull latest code
git pull origin main

# Rebuild image
docker-compose build --no-cache

# Test in staging
docker-compose -f docker-compose.staging.yml up -d

# Deploy to production
docker-compose up -d
```

## Support and Documentation

- **Quick Start**: `docs/DOCKER_QUICK_START.md`
- **Full Guide**: `docs/DOCKER_GUIDE.md`
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health


