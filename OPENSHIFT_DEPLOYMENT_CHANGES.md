# OpenShift Deployment Changes Summary

This document summarizes all changes made to deploy the dq-poc application to OpenShift.

## Date: November 10, 2025

---

## Overview
Successfully deployed both backend (proj-api) and frontend (web-app) applications to OpenShift with full MSSQL integration and proper API routing.

---

## Backend Changes (proj-api)

### 1. Dockerfile (`proj-api/Dockerfile`)
**Location**: Lines 41-54
**Purpose**: Install Microsoft ODBC Driver 18 for SQL Server connectivity

**Changes Made**:
```dockerfile
# Install runtime dependencies including ODBC drivers and Microsoft ODBC Driver 18
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    apt-transport-https \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y \
    default-jre \
    unixodbc \
    unixodbc-dev \
    msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*
```

**Why**: Backend needs ODBC Driver 18 to connect to MSSQL database for KPI storage and operations.

---

### 2. Requirements (`proj-api/requirements.txt`)
**Status**: No version pinning (already correct)
**Content**:
```text
fastapi
uvicorn[standard]
pydantic
pydantic-settings
falkordb
graphiti-core
mysql-connector-python
pymysql
jaydebeapi
sqlalchemy
pymongo
pyodbc
openai
python-dotenv
python-multipart
filelock
croniter
pytest
pytest-asyncio
httpx
black
flake8
mypy
```

**Why**: Removed version pinning to allow OpenShift to use compatible versions during build.

---

### 3. Routes Configuration (`proj-api/kg_builder/routes.py`)
**Location**: Lines 3210-3220
**Purpose**: Switch KPI service from SQLite to MSSQL

**Changes Made**:
```python
def get_kpi_analytics_service():
    """Get KPI Analytics service instance using MS SQL Server with pyodbc."""
    from kg_builder.services.landing_kpi_service_mssql import LandingKPIServiceMSSQL
    from kg_builder.config import KPI_DB_HOST, KPI_DB_PORT, KPI_DB_DATABASE, KPI_DB_USERNAME, KPI_DB_PASSWORD
    return LandingKPIServiceMSSQL(
        host=KPI_DB_HOST,
        port=KPI_DB_PORT,
        database=KPI_DB_DATABASE,
        username=KPI_DB_USERNAME,
        password=KPI_DB_PASSWORD
    )
```

**Why**: Backend needs to use MSSQL service instead of SQLite for production KPI storage.

---

### 4. MSSQL KPI Service (`proj-api/kg_builder/services/landing_kpi_service_mssql.py`)

#### 4a. ODBC Driver Configuration
**Location**: Line 44
**Changes Made**:
```python
conn_str = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={self.host},{self.port};"
    f"DATABASE={self.database};"
    f"UID={self.username};"
    f"PWD={self.password};"
    f"TrustServerCertificate=yes;"
)
```

**Why**: Updated to use ODBC Driver 18 (installed in Dockerfile) instead of Driver 17.

#### 4b. Fix NULL select_schema Issue
**Location**: Line 333
**Changes Made**:
```python
execution_params.get('select_schema', 'default'),  # Changed from execution_params.get('select_schema')
```

**Why**: MSSQL table doesn't allow NULL for select_schema column. Provides default value 'default' when not specified.

---

### 5. Backend Deployment Configuration

#### Environment Variables Added:
```yaml
- name: KPI_DB_TYPE
  value: "sqlserver"
- name: KPI_DB_HOST
  value: "mssql.cognito-ai-dq-dev.svc.cluster.local"
- name: KPI_DB_PORT
  value: "1433"
- name: KPI_DB_DATABASE
  value: "KPI_Analytics"
- name: KPI_DB_USERNAME
  value: "sa"
- name: KPI_DB_PASSWORD
  value: "YourStrong!Passw0rd"
```

**Why**: Backend needs these environment variables to connect to the MSSQL pod in OpenShift.

---

## Frontend Changes (web-app)

### 1. Dockerfile (`web-app/Dockerfile`)
**Purpose**: Make frontend OpenShift-compatible

**Changes Made**:

#### 1a. Add --legacy-peer-deps (Line 10)
```dockerfile
RUN npm install --legacy-peer-deps
```

#### 1b. Change Port to 8080 (Line 35)
```dockerfile
EXPOSE 8080
```

#### 1c. Create nginx cache directories and fix permissions (Lines 28-32)
```dockerfile
RUN mkdir -p /var/cache/nginx/client_temp /var/cache/nginx/proxy_temp \
    /var/cache/nginx/fastcgi_temp /var/cache/nginx/uwsgi_temp \
    /var/cache/nginx/scgi_temp /tmp && \
    chgrp -R 0 /var/cache/nginx /var/run /var/log/nginx /usr/share/nginx/html /tmp && \
    chmod -R g=u /var/cache/nginx /var/run /var/log/nginx /usr/share/nginx/html /tmp
```

#### 1d. Add custom nginx.conf for PID file (Lines 24-25)
```dockerfile
COPY nginx-main.conf /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

#### 1e. Set USER nginx (Line 32)
```dockerfile
USER nginx
```

**Why**:
- OpenShift requires non-root containers
- Port 8080 instead of 80 (OpenShift restriction)
- Proper permissions for arbitrary UIDs
- Writable PID file location

---

### 2. Main Nginx Configuration (`web-app/nginx-main.conf`)
**Purpose**: Override default nginx.conf with writable PID location

**Content**:
```nginx
pid /tmp/nginx.pid;
worker_processes auto;
error_log /var/log/nginx/error.log warn;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Client temp directories
    client_body_temp_path /var/cache/nginx/client_temp;
    proxy_temp_path /var/cache/nginx/proxy_temp;
    fastcgi_temp_path /var/cache/nginx/fastcgi_temp;
    uwsgi_temp_path /var/cache/nginx/uwsgi_temp;
    scgi_temp_path /var/cache/nginx/scgi_temp;

    include /etc/nginx/conf.d/*.conf;
}
```

**Why**: Default nginx tries to write PID to `/run/nginx.pid` which is read-only in OpenShift.

---

### 3. Server Nginx Configuration (`web-app/nginx.conf`)
**Purpose**: Configure server and proxy settings

**Changes Made**:

#### 3a. Change listen port (Line 2)
```nginx
listen 8080;
```

#### 3b. Fix API proxy routing (Lines 27-40)
```nginx
# API proxy to backend (using OpenShift service name)
# Rewrites /api/v1/* to /v1/* on the backend
location /api/ {
    rewrite ^/api/(.*)$ /$1 break;
    proxy_pass http://kg-builder-backend-service:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Why**:
- Port 8080 for OpenShift
- Correct OpenShift service name for backend
- Rewrite rule to strip `/api/` prefix before forwarding to backend

---

### 4. API Service Configuration (`web-app/src/services/api.js`)
**Location**: Lines 3-6
**Purpose**: Use relative API path in production

**Changes Made**:
```javascript
// Use relative path for production (goes through nginx proxy), localhost for development
export const API_BASE_URL = process.env.REACT_APP_API_URL || (
  process.env.NODE_ENV === 'production' ? '/api/v1' : 'http://localhost:8000/v1'
);
```

**Why**: In production, frontend should use relative path `/api/v1` to route through nginx proxy to backend service. In development, use localhost for direct connection.

---

## OpenShift Resources Created

### Backend Resources
1. **BuildConfig**: `kg-builder-backend`
   - Type: Docker build from binary source
   - Output: ImageStreamTag `kg-builder-backend:latest`

2. **ImageStream**: `kg-builder-backend`
   - Stores built backend images

3. **Deployment**: `kg-builder-backend`
   - Image: `image-registry.openshift-image-registry.svc:5000/cognito-ai-dq-dev/kg-builder-backend:latest`
   - Port: 8000
   - Environment variables for MSSQL connection
   - Resources: 256Mi-1Gi memory, 250m-1000m CPU

4. **Service**: `kg-builder-backend-service`
   - Type: ClusterIP
   - Port: 8000

5. **Route**: `kg-builder-backend`
   - Host: kg-builder-backend-cognito-ai-dq-dev.apps.rosa.cognitoai.2pcf.p3.openshiftapps.com
   - TLS: Edge termination

### Frontend Resources
1. **BuildConfig**: `kg-builder-web`
   - Type: Docker build from binary source
   - Output: ImageStreamTag `kg-builder-web:latest`

2. **ImageStream**: `kg-builder-web`
   - Stores built frontend images

3. **Deployment**: `kg-builder-web`
   - Image: `image-registry.openshift-image-registry.svc:5000/cognito-ai-dq-dev/kg-builder-web:latest`
   - Port: 8080
   - Resources: 256Mi-512Mi memory, 100m-500m CPU

4. **Service**: `kg-builder-web-service`
   - Type: ClusterIP
   - Port: 8080

5. **Route**: `kg-builder-web`
   - Host: kg-builder-web-cognito-ai-dq-dev.apps.rosa.cognitoai.2pcf.p3.openshiftapps.com
   - TLS: Edge termination

### MSSQL Database Resources
1. **Deployment**: `mssql`
   - Image: mcr.microsoft.com/mssql/server:2022-latest
   - Port: 1433
   - Environment: SA_PASSWORD, ACCEPT_EULA
   - SecurityContext: fsGroup: 10001
   - PVC: mssql-data-pvc (10Gi)

2. **Service**: `mssql`
   - Type: ClusterIP
   - Port: 1433
   - Internal DNS: mssql.cognito-ai-dq-dev.svc.cluster.local

3. **PersistentVolumeClaim**: `mssql-data-pvc`
   - Size: 10Gi
   - Access: ReadWriteOnce

---

## Deployment Commands Used

### Backend Deployment
```bash
# Build from proj-api directory
cd /Users/rchirrareddy/Desktop/dq-poc/proj-api
oc start-build kg-builder-backend --from-dir=. --follow

# Restart deployment
oc rollout restart deployment/kg-builder-backend
oc rollout status deployment/kg-builder-backend
```

**Builds Created**:
- Build 22: Initial deployment with ODBC Driver 18
- Build 24: Updated backend code
- Build 25: Fixed select_schema NULL issue

### Frontend Deployment
```bash
# Build from web-app directory
cd /Users/rchirrareddy/Desktop/dq-poc/web-app
oc start-build kg-builder-web --from-dir=. --follow

# Restart deployment
oc rollout restart deployment/kg-builder-web
oc rollout status deployment/kg-builder-web
```

**Builds Created**:
- Build 7: Initial attempt
- Build 8: Added permissions fix
- Build 9: Added PID file fix
- Build 10: Fixed API routing

---

## Issues Fixed

### 1. ODBC Driver Missing
**Error**: `Can't open lib 'ODBC Driver 17 for SQL Server' : file not found`
**Fix**: Installed ODBC Driver 18 in Dockerfile
**Files Changed**: `proj-api/Dockerfile`

### 2. Nginx Permission Denied
**Error**: `mkdir() "/var/cache/nginx/client_temp" failed (13: Permission denied)`
**Fix**: Created directories and set group permissions
**Files Changed**: `web-app/Dockerfile`

### 3. Nginx PID File Permission
**Error**: `open() "/run/nginx.pid" failed (13: Permission denied)`
**Fix**: Created custom nginx.conf with PID in /tmp
**Files Created**: `web-app/nginx-main.conf`
**Files Changed**: `web-app/Dockerfile`

### 4. API Routing 404
**Error**: Frontend calling `localhost:8000` instead of using nginx proxy
**Fix**: Updated API base URL to use relative path in production
**Files Changed**: `web-app/src/services/api.js`, `web-app/nginx.conf`

### 5. MSSQL select_schema NULL
**Error**: `Cannot insert the value NULL into column 'select_schema'`
**Fix**: Added default value 'default' for select_schema
**Files Changed**: `proj-api/kg_builder/services/landing_kpi_service_mssql.py` (line 333)

### 6. MSSQL Password Mismatch
**Error**: Login failed for user 'sa'
**Fix**: Deleted and recreated MSSQL PVC with fresh database, added fsGroup: 10001
**Commands Used**:
```bash
oc scale deployment/mssql --replicas=0
oc delete pvc mssql-data-pvc
oc create -f mssql-pvc.yaml
oc patch deployment mssql --type='json' -p='[{"op": "add", "path": "/spec/template/spec/securityContext", "value": {"fsGroup": 10001}}]'
oc scale deployment/mssql --replicas=1
```

---

## Current Deployment Status

### Backend
- **Pod**: `kg-builder-backend-648547b9dc-xxxxx` (Running)
- **Status**: Healthy, responding to health checks
- **MSSQL Connection**: Connected successfully
- **ODBC Driver**: 18 for SQL Server

### Frontend
- **Pod**: `kg-builder-web-57d48b6985-24v24` (Running)
- **Status**: Healthy, responding to health checks
- **API Routing**: Working correctly through nginx proxy

### MSSQL Database
- **Pod**: `mssql-xxxxxxxxx-xxxxx` (Running)
- **Database**: KPI_Analytics
- **Connection**: Internal service at mssql.cognito-ai-dq-dev.svc.cluster.local:1433

---

## Application URLs

### Frontend
https://kg-builder-web-cognito-ai-dq-dev.apps.rosa.cognitoai.2pcf.p3.openshiftapps.com/

### Backend API
https://kg-builder-backend-cognito-ai-dq-dev.apps.rosa.cognitoai.2pcf.p3.openshiftapps.com/

### API Flow
```
Browser → Frontend Route (HTTPS)
       → Frontend Pod (nginx:8080)
       → Backend Service (internal:8000)
       → Backend Pod (uvicorn:8000)
       → MSSQL Service (internal:1433)
       → MSSQL Pod (mssql:1433)
```

---

## Files Modified Summary

### Backend (proj-api/)
1. `Dockerfile` - Added ODBC Driver 18 installation
2. `kg_builder/routes.py` - Switched to MSSQL KPI service
3. `kg_builder/services/landing_kpi_service_mssql.py` - Updated driver version and fixed NULL issue
4. `kg_builder/services/landing_kpi_service.py` - Added get_all_kpis compatibility method

### Frontend (web-app/)
1. `Dockerfile` - OpenShift compatibility (permissions, port, user)
2. `nginx-main.conf` - **NEW FILE** - Custom nginx config for PID file
3. `nginx.conf` - Changed port and API proxy settings
4. `src/services/api.js` - Production API path configuration

### OpenShift Configuration (openshift/)
All YAML files for deployments, services, routes, buildconfigs, and imagestreams

---

## Important Notes

1. **Do not revert** the following changes as they are required for OpenShift:
   - Port 8080 in frontend (OpenShift requirement)
   - Group 0 permissions (OpenShift security)
   - Relative API paths in production
   - ODBC Driver 18 installation

2. **Environment-specific settings**:
   - Development: Uses `localhost:8000` for API
   - Production: Uses `/api/v1` for API (routes through nginx)

3. **Build Process**:
   - Always build from the respective folder (`proj-api` or `web-app`)
   - Use `--from-dir=.` to upload current directory
   - Use `--follow` to see build logs

4. **Troubleshooting**:
   - Check pod logs: `oc logs <pod-name>`
   - Check build logs: `oc logs -f build/<build-name>`
   - Check events: `oc get events --sort-by='.lastTimestamp'`
   - Check deployment: `oc describe deployment/<name>`

---

## Next Steps for Future Deployments

1. **To update backend**:
   ```bash
   cd /Users/rchirrareddy/Desktop/dq-poc/proj-api
   oc start-build kg-builder-backend --from-dir=. --follow
   oc rollout restart deployment/kg-builder-backend
   ```

2. **To update frontend**:
   ```bash
   cd /Users/rchirrareddy/Desktop/dq-poc/web-app
   oc start-build kg-builder-web --from-dir=. --follow
   oc rollout restart deployment/kg-builder-web
   ```

3. **To check application health**:
   ```bash
   oc get pods
   oc get routes
   curl https://kg-builder-backend-cognito-ai-dq-dev.apps.rosa.cognitoai.2pcf.p3.openshiftapps.com/
   ```

---

## End of Document
Generated: November 10, 2025
Last Updated: Build 25 (Backend), Build 10 (Frontend)
