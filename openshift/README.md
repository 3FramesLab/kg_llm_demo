# OpenShift Deployment Guide

Complete guide for deploying the Knowledge Graph Builder application to OpenShift.

## Prerequisites

- OpenShift CLI (`oc`) installed and configured
- Access to OpenShift cluster with cluster-admin or project-admin privileges
- Git repository with latest code changes

## Quick Deployment

Run these commands in order from the project root directory:

```bash
# 1. Login to OpenShift
oc login <your-openshift-cluster-url>

# 2. Switch to your project/namespace
oc project cognito-ai-dq-dev

# 3. Apply all configurations in order
oc apply -f openshift/05-secrets.yaml
oc apply -f openshift/04-buildconfigs.yaml
oc apply -f openshift/01-backend-deployment.yaml
oc apply -f openshift/03-web-app-deployment.yaml
oc apply -f openshift/06-routes.yaml

# 4. Build the applications
oc start-build kg-builder-backend --from-dir=. --follow
cd web-app && oc start-build kg-builder-web --from-dir=. --follow && cd ..

# 5. Verify deployment
oc get pods
oc get routes
```

## Deployment Files

### 1. **05-secrets.yaml** - Secrets Configuration
Contains sensitive data:
- `kg-builder-secrets`: OpenAI API key, FalkorDB password
- `openai-secret`: OpenAI API key (primary secret)
- `mssql-secret`: SQL Server SA password

**IMPORTANT**: Update these values before deploying:
```yaml
stringData:
  OPENAI_API_KEY: "your-actual-api-key"
  SA_PASSWORD: "YourStrong!Passw0rd"
```

### 2. **04-buildconfigs.yaml** - Build Configuration
Defines how to build Docker images:
- `kg-builder-backend`: Backend Python application with ODBC Driver 18
- `kg-builder-web`: Frontend React application with nginx

### 3. **01-backend-deployment.yaml** - Backend Deployment
FastAPI backend service configuration:
- **Image**: Built from Dockerfile with ODBC Driver 18 for SQL Server
- **Port**: 8000
- **Service**: `kg-builder-backend-service`
- **Environment Variables**:
  - OpenAI configuration (from `openai-secret`)
  - MSSQL database connection
  - KPI database configuration
  - Source/Target database settings

### 4. **03-web-app-deployment.yaml** - Frontend Deployment
React + Nginx frontend configuration:
- **Image**: Multi-stage build with nginx
- **Port**: 8080 (OpenShift compatible)
- **Service**: `kg-builder-web-service`
- **Nginx**: Proxies `/api/*` to backend service

### 5. **06-routes.yaml** - Routes Configuration
External access routes:
- `kg-builder-backend`: Direct API access
- `kg-builder-web`: Main web application

## Environment Variables

### Backend Environment Variables

| Variable | Description | Default/Value |
|----------|-------------|---------------|
| `OPENAI_API_KEY` | OpenAI API key | From `openai-secret` |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o` |
| `OPENAI_TEMPERATURE` | Model temperature | `0.0` |
| `FALKORDB_HOST` | FalkorDB/Redis host | `redis-cluster-service...` |
| `MSSQL_HOST` | SQL Server host | `mssql.cognito-ai-dq-dev...` |
| `KPI_DB_HOST` | KPI database host | `mssql.cognito-ai-dq-dev...` |
| `KPI_DB_DATABASE` | KPI database name | `KPI_Analytics` |

### Frontend Environment Variables

| Variable | Description | Value |
|----------|-------------|-------|
| `REACT_APP_API_URL` | Backend API URL | `/api/v1` (production) |

Configured in `web-app/.env.production`

## Key Features & Fixes

### ✅ ODBC Driver 18 Support
- Backend Dockerfile installs `msodbcsql18`
- Connection strings use `ODBC Driver 18 for SQL Server`

### ✅ OpenShift Compatibility
- Non-root user (UID 1001, GID 0)
- Port 8080 for frontend (non-privileged)
- Proper file permissions (`chmod -R g=u`)
- Writable directories for nginx

### ✅ Service Discovery
- Pod labels include both `app` and `deployment` labels
- Service selector uses `app=kg-builder-backend`
- Ensures proper endpoint registration

### ✅ API Routing
- Frontend nginx proxies `/api/v1/*` to backend
- Rewrites to `/v1/*` before forwarding
- Internal service communication via Kubernetes DNS

## Build Process

### Backend Build
```bash
oc start-build kg-builder-backend --from-dir=. --follow
```

Builds from root directory, includes:
- Python dependencies (requirements.txt)
- ODBC Driver 18 installation
- All source code and schemas

### Frontend Build
```bash
cd web-app
oc start-build kg-builder-web --from-dir=. --follow
```

Builds from web-app directory, includes:
- npm dependencies
- React production build
- nginx configuration

## Post-Deployment Verification

### 1. Check Pods
```bash
oc get pods
# Should see: kg-builder-backend and kg-builder-web Running
```

### 2. Check Services
```bash
oc get svc
# Should see both backend and web services with ClusterIP
```

### 3. Check Endpoints
```bash
oc get endpoints
# Should show IP:PORT for both services
```

### 4. Check Routes
```bash
oc get routes
# Get the public URLs for accessing the application
```

### 5. Test API
```bash
# Get the web route URL
WEB_URL=$(oc get route kg-builder-web -o jsonpath='{.spec.host}')

# Test health endpoint
curl https://$WEB_URL/api/v1/health

# Test LLM status
curl https://$WEB_URL/api/v1/llm/status

# Test KPI dashboard
curl https://$WEB_URL/api/v1/landing-kpi-mssql/dashboard
```

## Troubleshooting

### Pod Not Starting
```bash
# Check pod logs
oc logs <pod-name>

# Check pod events
oc describe pod <pod-name>
```

### Service Endpoints Empty
```bash
# Check if pod labels match service selector
oc get pod <pod-name> --show-labels
oc get svc <service-name> -o yaml | grep selector -A 5

# Fix: Add missing label to pod
oc label pod <pod-name> app=kg-builder-backend
```

### API 502 Errors
1. Check if backend pod is running
2. Verify service endpoints are populated
3. Check nginx configuration in frontend pod
4. Review backend logs for errors

### ODBC Driver Errors
If you see "Can't open lib 'ODBC Driver 17'":
- Ensure Dockerfile installs `msodbcsql18`
- Update connection strings to use `ODBC Driver 18 for SQL Server`
- Rebuild the backend image

### Database Connection Issues
```bash
# Check environment variables
oc exec <backend-pod> -- env | grep DB

# Test database connectivity
oc exec <backend-pod> -- curl localhost:8000/v1/health
```

## Updating the Application

### Code Changes
```bash
# 1. Build new image
oc start-build kg-builder-backend --from-dir=. --follow

# 2. Deployment will auto-update (imagePullPolicy: Always)
# Or manually restart:
oc rollout restart deployment/kg-builder-backend
oc rollout status deployment/kg-builder-backend
```

### Configuration Changes
```bash
# Update secrets
oc apply -f openshift/05-secrets.yaml

# Update deployment
oc apply -f openshift/01-backend-deployment.yaml

# Restart to pick up changes
oc rollout restart deployment/kg-builder-backend
```

### Environment Variable Changes
```bash
# Quick update without editing YAML
oc set env deployment/kg-builder-backend OPENAI_MODEL=gpt-4o-mini

# Update from secret
oc set env deployment/kg-builder-backend --from=secret/openai-secret
```

## URLs

After deployment, access your application at:
- **Frontend**: https://kg-builder-web-cognito-ai-dq-dev.apps.rosa.cognitoai.2pcf.p3.openshiftapps.com
- **Backend API**: https://kg-builder-backend-cognito-ai-dq-dev.apps.rosa.cognitoai.2pcf.p3.openshiftapps.com

## Security Notes

1. **Never commit secrets** to version control
2. **Rotate API keys** regularly
3. **Use read-only database users** where possible
4. **Enable network policies** for production
5. **Set resource limits** to prevent resource exhaustion
6. **Review pod security** contexts regularly

## Support

For issues or questions:
1. Check pod logs: `oc logs <pod-name>`
2. Check events: `oc get events --sort-by='.lastTimestamp'`
3. Review this guide's troubleshooting section
4. Check OpenShift documentation

---

**Last Updated**: November 10, 2025
**OpenShift Version**: 4.x (ROSA)
**Namespace**: cognito-ai-dq-dev
