# Enhanced Logging Deployment Summary

## Deployment Status: ✅ SUCCESS

**Date:** November 10, 2025
**Namespace:** cognito-ai-dq-dev
**Pod:** kg-builder-backend-7cf5cbbdf5-xpwpf
**Status:** Running (1/1 Ready)

---

## What Was Deployed

### 1. Enhanced Logging Middleware
- **File:** [kg_builder/middleware/logging_middleware.py](kg_builder/middleware/logging_middleware.py)
- **Features:**
  - ✅ Request/Response body logging (JSON formatted)
  - ✅ Request timing and duration tracking
  - ✅ Client IP address and port logging
  - ✅ Request headers (excluding sensitive ones like Authorization, Cookie)
  - ✅ Response headers
  - ✅ Unique request IDs for correlation
  - ✅ Automatic truncation for large payloads (>2000 chars)
  - ✅ Color-coded log levels (INFO, WARNING, ERROR)

### 2. Updated Logging Configuration
- **File:** [kg_builder/logging_config.py](kg_builder/logging_config.py)
- **Changes:**
  - Set `LOG_LEVEL` to `DEBUG` for all kg_builder modules
  - Added dedicated middleware logger
  - Updated service-level loggers to DEBUG

### 3. Updated Main Application
- **File:** [kg_builder/main.py](kg_builder/main.py)
- **Changes:**
  - Added `DetailedLoggingMiddleware` to FastAPI app
  - Middleware processes ALL incoming requests BEFORE CORS

### 4. OpenShift Configuration

#### ConfigMap Created
- **File:** [openshift/00-complete-configmap.yaml](openshift/00-complete-configmap.yaml)
- **Environment Variables:** 50+ configuration variables including:
  - Logging settings (LOG_LEVEL=DEBUG)
  - FalkorDB configuration
  - OpenAI API settings
  - Source/Target database configs (MSSQL)
  - KPI database settings
  - MongoDB settings
  - Landing database settings
  - JDBC and reconciliation settings

#### Deployment Updated
- **File:** [openshift/01-backend-deployment.yaml](openshift/01-backend-deployment.yaml)
- **Changes:**
  - Updated LOG_LEVEL to "DEBUG"
  - Uses ConfigMap for environment variables
  - Enhanced deployment file created with additional metadata

#### Build Completed
- **Build:** kg-builder-backend-39
- **Image:** image-registry.openshift-image-registry.svc:5000/cognito-ai-dq-dev/kg-builder-backend:latest
- **Status:** Successfully pushed

---

## Log Output Examples

### Startup Logs
```
2025-11-10 20:08:52 - kg_builder.main - INFO - Logging configured at DEBUG level
[STARTUP] Logging configured at DEBUG level - Console handler active
2025-11-10 20:08:52 - uvicorn.error - INFO - Started server process [1]
2025-11-10 20:08:53 - kg_builder.main - INFO - Starting Knowledge Graph Builder v1.0.0
```

### Request Logging Example
```
2025-11-10 20:09:36 - kg_builder.middleware - INFO - [REQUEST-START] [1762805376515848] GET /v1/landing-kpi-mssql/kpis
2025-11-10 20:09:36 - kg_builder.middleware - DEBUG - [REQUEST-QUERY] [1762805376515848] Params: {'is_active': 'true'}
2025-11-10 20:09:36 - kg_builder.middleware - DEBUG - [REQUEST-HEADERS] [1762805376515848] Headers: {
  "connection": "upgrade",
  "host": "kg-builder-web-cognito-ai-dq-dev.apps.rosa.cognitoai.2pcf.p3.openshiftapps.com",
  "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
  ...
}
2025-11-10 20:09:36 - kg_builder.middleware - INFO - [REQUEST-CLIENT] [1762805376515848] Client: 10.128.1.48:43854
```

### Response Logging Example
```
2025-11-10 20:09:36 - kg_builder.middleware - INFO - [RESPONSE] [1762805376515848] GET /v1/landing-kpi-mssql/kpis - Status: 200 - Time: 0.0364s
2025-11-10 20:09:36 - kg_builder.middleware - DEBUG - [RESPONSE-HEADERS] [1762805376515848] Headers: {
  "content-length": "17585",
  "content-type": "application/json"
}
```

### Service-Level Logs
```
2025-11-10 20:09:36 - kg_builder.services.landing_kpi_service_mssql - INFO - Initialized KPI Service for MS SQL Server: mssql.cognito-ai-dq-dev.svc.cluster.local:1433/KPI_Analytics
2025-11-10 20:09:36 - kg_builder.services.landing_kpi_service_mssql - INFO - Retrieved 27 KPIs
```

---

## How to View Logs

### Real-Time Logs (Recommended)
```bash
# Follow logs from the deployment
oc logs -f deployment/kg-builder-backend

# Follow logs from specific pod
oc logs -f kg-builder-backend-7cf5cbbdf5-xpwpf
```

### Filter Logs
```bash
# View only REQUEST logs
oc logs kg-builder-backend-7cf5cbbdf5-xpwpf | grep REQUEST

# View only RESPONSE logs
oc logs kg-builder-backend-7cf5cbbdf5-xpwpf | grep RESPONSE

# View only ERROR logs
oc logs kg-builder-backend-7cf5cbbdf5-xpwpf | grep ERROR

# View logs for specific request ID
oc logs kg-builder-backend-7cf5cbbdf5-xpwpf | grep "1762805376515848"

# View service-level logs
oc logs kg-builder-backend-7cf5cbbdf5-xpwpf | grep "kg_builder.services"
```

### Download Logs
```bash
# Save last 1000 lines to file
oc logs kg-builder-backend-7cf5cbbdf5-xpwpf --tail=1000 > app-logs.txt

# Save all logs
oc logs kg-builder-backend-7cf5cbbdf5-xpwpf > full-logs.txt
```

---

## Log Details Being Captured

### For Every Request
| Field | Description | Example |
|-------|-------------|---------|
| Request ID | Unique identifier | `[1762805376515848]` |
| Method | HTTP method | `GET`, `POST`, `PUT`, `DELETE` |
| Path | Request path | `/v1/landing-kpi-mssql/kpis` |
| Query Params | URL parameters | `{'is_active': 'true'}` |
| Headers | Request headers (sanitized) | Full headers minus sensitive keys |
| Client IP | Client address | `10.128.1.48:43854` |
| Request Body | POST/PUT body (if enabled) | JSON formatted |
| Response Status | HTTP status code | `200`, `404`, `500` |
| Response Headers | Response headers | All headers |
| Response Body | Response payload (if enabled) | JSON formatted, truncated if >2000 chars |
| Processing Time | Request duration | `0.0364s` |

### For Services
- Function entry/exit with timing
- SQL queries (in dedicated sql.log)
- Database connections
- LLM API calls
- Error stack traces

---

## Environment Configuration

### Current Settings
```yaml
LOG_LEVEL: "DEBUG"
ENABLE_REQUEST_LOGGING: "true"
ENABLE_RESPONSE_LOGGING: "true"
ENABLE_SQL_LOGGING: "true"
LOG_REQUEST_BODY: "true"
LOG_RESPONSE_BODY: "true"
```

### To Modify Logging Level
```bash
# Edit ConfigMap
oc edit configmap kg-builder-app-config

# Change LOG_LEVEL value, then restart deployment
oc rollout restart deployment/kg-builder-backend
```

Available log levels (in order):
- `DEBUG` - Most verbose, all details
- `INFO` - Standard operational logs
- `WARNING` - Warning messages only
- `ERROR` - Error messages only

---

## Deployment Files Reference

### Core Files
1. [kg_builder/middleware/logging_middleware.py](kg_builder/middleware/logging_middleware.py) - Logging middleware
2. [kg_builder/logging_config.py](kg_builder/logging_config.py) - Logging configuration
3. [kg_builder/main.py](kg_builder/main.py) - Main FastAPI application

### OpenShift Files
1. [openshift/00-complete-configmap.yaml](openshift/00-complete-configmap.yaml) - ConfigMap with all env vars
2. [openshift/01-backend-deployment.yaml](openshift/01-backend-deployment.yaml) - Deployment config
3. [openshift/01-backend-deployment-enhanced.yaml](openshift/01-backend-deployment-enhanced.yaml) - Enhanced deployment
4. [openshift/05-secrets.yaml](openshift/05-secrets.yaml) - Secrets

### Deployment Scripts
1. [deploy-to-openshift.sh](deploy-to-openshift.sh) - Bash deployment script
2. [deploy-to-openshift.ps1](deploy-to-openshift.ps1) - PowerShell deployment script

---

## Quick Commands

```bash
# View pod status
oc get pods -l app=kg-builder-backend

# View real-time logs
oc logs -f deployment/kg-builder-backend

# Check ConfigMap
oc get configmap kg-builder-app-config -o yaml

# Restart deployment
oc rollout restart deployment/kg-builder-backend

# Check deployment status
oc rollout status deployment/kg-builder-backend

# Get route URL
oc get route kg-builder-backend

# Describe pod for troubleshooting
oc describe pod kg-builder-backend-7cf5cbbdf5-xpwpf
```

---

## Troubleshooting

### No Logs Appearing
1. Check if pod is running: `oc get pods`
2. Check pod events: `oc describe pod <pod-name>`
3. Verify LOG_LEVEL in ConfigMap: `oc get configmap kg-builder-app-config -o yaml`

### Too Many Logs
1. Reduce LOG_LEVEL to INFO or WARNING
2. Disable request/response body logging in middleware
3. Edit ConfigMap and restart deployment

### Missing Request Details
1. Verify middleware is loaded in [kg_builder/main.py](kg_builder/main.py:55-59)
2. Check middleware logger level in [kg_builder/logging_config.py](kg_builder/logging_config.py:125-129)

---

## Next Steps

1. **Monitor Performance:** Watch for any performance impact from detailed logging
2. **Set Up Log Aggregation:** Consider forwarding logs to a centralized logging system
3. **Create Alerts:** Set up alerts for ERROR level logs
4. **Adjust Verbosity:** Fine-tune log levels based on operational needs
5. **Archive Logs:** Set up log retention and archival policies

---

## Support

For issues or questions:
1. Check pod logs: `oc logs -f deployment/kg-builder-backend`
2. Review this document
3. Check [DEPLOYMENT_UPDATES.md](DEPLOYMENT_UPDATES.md) for deployment history

---

**Deployment Completed Successfully! 🎉**

All API calls and functions now have detailed logging enabled.
