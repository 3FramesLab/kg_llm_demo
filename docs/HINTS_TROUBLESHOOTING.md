# Column Hints - Troubleshooting Guide

## Issue: UI doesn't show any tables

### ✅ Fixed! Here's what was wrong and how to verify:

---

## Problems Found & Fixed

### 1. ❌ Hints router not included in main.py
**Fixed**: Added to `kg_builder/main.py`:
```python
from kg_builder.routes_hints import router as hints_router
app.include_router(hints_router, prefix="/v1", tags=["Column Hints"])
```

### 2. ❌ Wrong API path in frontend
**Fixed**: Changed in `web-app/src/services/api.js`:
- **Before**: `/api/kg/hints/` ❌
- **After**: `/hints/` ✅

### 3. ❌ Hints file didn't exist
**Fixed**: Created directory and initialized:
```bash
mkdir -p schemas/hints/versions
python scripts/initialize_hints_from_schema.py --schema schemas/newdqschemanov.json
```

---

## Verification Steps

### Step 1: Verify Hints File Exists
```bash
# Should show column_hints.json with data
ls -lh schemas/hints/
cat schemas/hints/column_hints.json | head -20
```

**Expected**: File exists with 8 tables, 197 columns

### Step 2: Restart Backend Server
```bash
# Stop your current server (Ctrl+C)
# Then restart:
uvicorn kg_builder.main:app --reload
```

**Expected**: See logs showing routes loading

### Step 3: Test API Directly
```bash
# Test from command line
curl http://localhost:8000/v1/hints/statistics

# Or run test script
python test_hints_api.py
```

**Expected Output**:
```json
{
  "success": true,
  "data": {
    "total_tables": 8,
    "total_columns": 197,
    "auto_generated": 197,
    "manual_verified": 0
  }
}
```

### Step 4: Test in Browser
```bash
# Open in browser:
http://localhost:8000/v1/hints/

# Should show JSON with all hints
```

### Step 5: Restart Frontend
```bash
cd web-app
# Stop if running (Ctrl+C)
npm start
```

### Step 6: Access UI
```bash
# Navigate to:
http://localhost:3000/hints-management

# Or click "Column Hints" in sidebar
```

**Expected**: See 8 table cards displayed

---

## Quick Fix Commands

Run these in order:

```bash
# 1. Verify hints file
cat schemas/hints/column_hints.json | grep "total_columns"

# 2. Restart backend
# Ctrl+C to stop, then:
uvicorn kg_builder.main:app --reload

# 3. Test API
curl http://localhost:8000/v1/hints/statistics

# 4. Restart frontend (in separate terminal)
cd web-app
npm start

# 5. Access UI
# Open browser: http://localhost:3000/hints-management
```

---

## Common Issues

### Issue: Backend shows 404 for /hints/ endpoints
**Solution**: Make sure you restarted the backend after updating main.py

### Issue: Frontend shows network error
**Solutions**:
1. Check backend is running on port 8000
2. Check browser console for CORS errors
3. Verify API base URL in `web-app/src/services/api.js`:
   ```javascript
   export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/v1';
   ```

### Issue: "File not found" error in backend logs
**Solution**: Run initialization script:
```bash
python scripts/initialize_hints_from_schema.py --schema schemas/newdqschemanov.json
```

### Issue: Tables show but no columns
**Solution**: Check hints file has column data:
```bash
cat schemas/hints/column_hints.json | grep -A 5 '"columns":'
```

---

## Debug Checklist

- [ ] Hints file exists at `schemas/hints/column_hints.json`
- [ ] File contains 8 tables, 197 columns
- [ ] Backend routes updated in `main.py`
- [ ] Backend server restarted
- [ ] API endpoint works: `curl http://localhost:8000/v1/hints/statistics`
- [ ] Frontend API paths use `/hints/` not `/api/kg/hints/`
- [ ] Frontend server restarted
- [ ] Browser cache cleared (Ctrl+Shift+R)
- [ ] No console errors in browser dev tools

---

## Test API Endpoints

```bash
# Statistics
curl http://localhost:8000/v1/hints/statistics

# All hints
curl http://localhost:8000/v1/hints/

# Specific table
curl http://localhost:8000/v1/hints/table/hana_material_master

# Search
curl -X POST http://localhost:8000/v1/hints/search \
  -H "Content-Type: application/json" \
  -d '{"search_term": "material", "limit": 5}'
```

---

## File Changes Made

1. **kg_builder/main.py**
   - Added: `from kg_builder.routes_hints import router as hints_router`
   - Added: `app.include_router(hints_router, prefix="/v1", tags=["Column Hints"])`

2. **web-app/src/services/api.js**
   - Changed all `/api/kg/hints/` → `/hints/`

3. **schemas/hints/** (created)
   - `column_hints.json` - Main hints file
   - `versions/` - Version snapshots directory

---

## Still Having Issues?

1. **Check Backend Logs**
   ```bash
   # Look for errors when server starts
   uvicorn kg_builder.main:app --reload --log-level debug
   ```

2. **Check Browser Console**
   - Open DevTools (F12)
   - Look for network errors
   - Check API response in Network tab

3. **Verify File Contents**
   ```bash
   # Should show tables
   cat schemas/hints/column_hints.json | python -m json.tool | head -50
   ```

4. **Test Each Layer**
   - Backend: `python test_hints_api.py`
   - Frontend: Check Network tab in browser

---

## Success Indicators

✅ Backend logs show: `INFO: Application startup complete`
✅ `curl http://localhost:8000/v1/hints/statistics` returns JSON
✅ Browser shows 8 table cards at `/hints-management`
✅ Clicking table shows column list
✅ Search works and finds columns

---

## Need More Help?

Run the test script:
```bash
python test_hints_api.py
```

This will test all 4 main endpoints and show exactly what's working or not.
