# Enhanced Logging - Quick Reference

## ✅ Deployment Complete

**Pod:** `kg-builder-backend-7cf5cbbdf5-xpwpf`
**Status:** Running with DEBUG level logging

---

## 🔍 View Logs (Most Common Commands)

```bash
# Real-time logs (recommended)
oc logs -f deployment/kg-builder-backend

# Last 100 lines
oc logs deployment/kg-builder-backend --tail=100

# All logs since deployment
oc logs deployment/kg-builder-backend
```

---

## 📊 What's Being Logged

### Every API Request Shows:
- ✅ **Request ID** - Unique identifier for correlation
- ✅ **HTTP Method & Path** - `GET /v1/landing-kpi-mssql/kpis`
- ✅ **Query Parameters** - `{'is_active': 'true'}`
- ✅ **Request Headers** - Full headers (sensitive ones excluded)
- ✅ **Client IP & Port** - `10.128.1.48:43854`
- ✅ **Request Body** - For POST/PUT/PATCH requests
- ✅ **Response Status** - `200`, `404`, `500`, etc.
- ✅ **Response Headers** - All response headers
- ✅ **Response Body** - JSON formatted (truncated if >2000 chars)
- ✅ **Processing Time** - `0.0364s`

### Service Level Logs:
- ✅ Database connections
- ✅ SQL queries (in dedicated sql.log)
- ✅ Function entry/exit with timing
- ✅ Error stack traces
- ✅ LLM API calls

---

## 🔎 Filter Logs

```bash
# Only requests
oc logs deployment/kg-builder-backend | grep REQUEST

# Only responses
oc logs deployment/kg-builder-backend | grep RESPONSE

# Only errors
oc logs deployment/kg-builder-backend | grep ERROR

# Only a specific service
oc logs deployment/kg-builder-backend | grep "kg_builder.services.landing_kpi"

# Track a specific request by ID
oc logs deployment/kg-builder-backend | grep "[1762805376515848]"
```

---

## 📝 Log Format Examples

### Request Start
```
2025-11-10 20:09:36 - kg_builder.middleware - INFO - [REQUEST-START] [1762805376515848] GET /v1/landing-kpi-mssql/kpis
```

### Request Details
```
2025-11-10 20:09:36 - kg_builder.middleware - DEBUG - [REQUEST-QUERY] [1762805376515848] Params: {'is_active': 'true'}
2025-11-10 20:09:36 - kg_builder.middleware - INFO - [REQUEST-CLIENT] [1762805376515848] Client: 10.128.1.48:43854
```

### Response
```
2025-11-10 20:09:36 - kg_builder.middleware - INFO - [RESPONSE] [1762805376515848] GET /v1/landing-kpi-mssql/kpis - Status: 200 - Time: 0.0364s
```

### Service Logs
```
2025-11-10 20:09:36 - kg_builder.services.landing_kpi_service_mssql - INFO - Retrieved 27 KPIs
```

---

## ⚙️ Configuration

### Current Log Level
```yaml
LOG_LEVEL: "DEBUG"  # Most verbose
```

### Change Log Level
```bash
# Edit ConfigMap
oc edit configmap kg-builder-app-config

# Change LOG_LEVEL to: DEBUG, INFO, WARNING, or ERROR
# Then restart
oc rollout restart deployment/kg-builder-backend
```

---

## 🚀 Deployment Scripts

### To Redeploy with Changes
```bash
# Linux/Mac
./deploy-to-openshift.sh

# Windows PowerShell
.\deploy-to-openshift.ps1
```

---

## 📦 Files Modified

1. **kg_builder/middleware/logging_middleware.py** - New logging middleware
2. **kg_builder/main.py** - Added middleware to app
3. **kg_builder/logging_config.py** - Set DEBUG level
4. **openshift/00-complete-configmap.yaml** - ConfigMap with all env vars
5. **openshift/01-backend-deployment.yaml** - Deployment with DEBUG

---

## 🔧 Troubleshooting

### Restart Deployment
```bash
oc rollout restart deployment/kg-builder-backend
```

### Check Pod Status
```bash
oc get pods -l app=kg-builder-backend
```

### View ConfigMap
```bash
oc get configmap kg-builder-app-config -o yaml
```

### Describe Pod (for issues)
```bash
oc describe pod <pod-name>
```

---

## 📚 Full Documentation

See [ENHANCED_LOGGING_DEPLOYMENT_SUMMARY.md](ENHANCED_LOGGING_DEPLOYMENT_SUMMARY.md) for complete details.

---

**All logging is now active and working! 🎉**
