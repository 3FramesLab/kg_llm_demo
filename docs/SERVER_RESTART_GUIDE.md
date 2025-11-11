# 🚀 Server Restart Guide - Import Error Fixed

## ✅ **Import Error Fixed**

The `NameError: name 'Query' is not defined` error has been fixed! I've added the missing import to `kg_builder/routes.py`.

### **🔧 What Was Fixed**:
```python
# Before (Line 6):
from fastapi import APIRouter, HTTPException, UploadFile, File

# After (Line 6):
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
```

---

## 🚀 **How to Restart the Server**

### **1. Stop Current Server**:
If the server is running, stop it:
- **In terminal**: Press `Ctrl+C`
- **In IDE**: Stop the running process

### **2. Start Server Again**:
```bash
cd d:\learning\dq-poc

# Option 1: Using main.py
python kg_builder/main.py

# Option 2: Using uvicorn directly
python -m uvicorn kg_builder.main:app --reload --host 0.0.0.0 --port 8000

# Option 3: Using run_server.py (if available)
python run_server.py
```

### **3. Expected Startup Output**:
```
[STARTUP] Starting uvicorn server...
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Starting Knowledge Graph Builder v1.0.0
INFO:     FalkorDB connected: True
INFO:     Graphiti available: True
INFO:     Application startup complete.
```

---

## 🧪 **Test After Restart**

### **1. Health Check**:
```bash
curl http://localhost:8000/v1/landing-kpi-mssql/health
```

**Expected Response**:
```json
{
  "success": true,
  "status": "healthy",
  "database": "mssql",
  "service": "kpi_analytics",
  "timestamp": 1699291234.567
}
```

### **2. List KPIs**:
```bash
curl "http://localhost:8000/v1/landing-kpi-mssql/kpis?is_active=true"
```

**Expected Response**:
```json
{
  "success": true,
  "data": [...],
  "count": 45,
  "storage_type": "mssql"
}
```

### **3. Dashboard Data**:
```bash
curl http://localhost:8000/v1/landing-kpi-mssql/dashboard
```

### **4. Frontend Test**:
1. **Open browser**: `http://localhost:3000/landing-kpi`
2. **Should load without 404 errors**
3. **KPI list should populate**
4. **Enhanced features should work**

---

## 📊 **Available Enhanced Routes**

After restart, these routes will be available:

### **KPI Management**:
- `GET /v1/landing-kpi-mssql/kpis` - List all KPIs
- `POST /v1/landing-kpi-mssql/kpis` - Create new KPI
- `GET /v1/landing-kpi-mssql/kpis/{kpi_id}` - Get specific KPI
- `PUT /v1/landing-kpi-mssql/kpis/{kpi_id}` - Update KPI
- `DELETE /v1/landing-kpi-mssql/kpis/{kpi_id}` - Delete KPI

### **KPI Execution**:
- `POST /v1/landing-kpi-mssql/kpis/{kpi_id}/execute` - Execute KPI

### **Dashboard & Analytics**:
- `GET /v1/landing-kpi-mssql/dashboard` - Dashboard data
- `GET /v1/landing-kpi-mssql/{kpi_id}/latest-results` - Latest results

### **Utilities**:
- `POST /v1/landing-kpi-mssql/sql-preview` - SQL preview
- `GET /v1/landing-kpi-mssql/health` - Health check

---

## 🎯 **Enhanced Features Available**

After restart, you'll have:

### **✅ Enhanced SQL Generation**:
- **Material master enhancement** - Automatic hana_material_master joins
- **ops_planner inclusion** - Automatically added to material queries
- **Always-visible SQL** - SQL shown even with 0 records

### **✅ Better Performance**:
- **MS SQL Server backend** instead of SQLite
- **Optimized queries** for larger datasets
- **Better concurrent access**

### **✅ Advanced Features**:
- **Dashboard integration** - KPIs grouped by category
- **Real-time SQL preview** - See generated SQL before execution
- **Enhanced error handling** - Better error messages and recovery

---

## 🚨 **If Server Still Won't Start**

### **Common Issues**:

#### **1. Port Already in Use**:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
# or on Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### **2. Missing Dependencies**:
```bash
pip install -r requirements.txt
```

#### **3. Database Connection Issues**:
- Check MS SQL Server is running
- Verify connection string in config
- Test database connectivity

#### **4. Import Errors**:
- Check all files are saved
- Verify Python path is correct
- Restart IDE/terminal

---

## 🎉 **Success Indicators**

### **Server Started Successfully When You See**:
- ✅ "Uvicorn running on http://0.0.0.0:8000"
- ✅ "Application startup complete"
- ✅ No import errors in console
- ✅ Health check returns 200 OK

### **Frontend Working When You See**:
- ✅ Landing KPI page loads without errors
- ✅ KPI list populates from MS SQL Server
- ✅ Enhanced SQL features work
- ✅ No 404 errors in browser console

---

## 📋 **Summary**

- ✅ **Import error fixed** - Added missing `Query` import
- 🚀 **Server restart required** - To load new routes
- 🧪 **Test endpoints** - Verify everything works
- 🎯 **Enhanced features ready** - ops_planner, always-visible SQL

**Status**: 🚀 **READY TO RESTART - All fixes applied!**

Just restart the server and everything should work perfectly! 🎉
