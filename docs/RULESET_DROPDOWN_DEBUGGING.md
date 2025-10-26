# Ruleset Dropdown Debugging Guide 🔍

## Problem: "No rulesets available" Even Though Rulesets Exist

### Symptoms
- Ruleset dropdown shows "No rulesets available"
- But rulesets exist in the system
- KPI Management page loads but can't select rulesets

---

## 🧪 Step-by-Step Debugging

### Step 1: Check Backend Response

**Test the API endpoint directly:**

```bash
curl http://localhost:8000/v1/reconciliation/rulesets
```

**Expected response:**
```json
{
  "success": true,
  "rulesets": [
    {
      "ruleset_id": "RECON_9240A5F7",
      "ruleset_name": "Reconciliation_New_KG_123",
      "schemas": ["newdqschema"],
      "rule_count": 5,
      "created_at": "2025-10-25T17:30:12.323851",
      "generated_from_kg": "kg_name"
    }
  ],
  "count": 1
}
```

**If you get 404:**
- Backend server not running
- Route not fixed properly
- Check: `python -m uvicorn kg_builder.main:app --reload`

**If you get empty array:**
- No rulesets saved yet
- Check: `data/reconciliation_rules/` folder
- Should have `.json` files like `RECON_9240A5F7.json`

---

### Step 2: Check Frontend Console Logs

**Open Browser DevTools:**
1. Press `F12` or right-click → Inspect
2. Go to **Console** tab
3. Navigate to KPI Management page
4. Look for logs like:

```
Raw rulesets response: {success: true, rulesets: [...], count: 1}
Rulesets array: [{ruleset_id: "RECON_9240A5F7", ...}]
First ruleset: {ruleset_id: "RECON_9240A5F7", ruleset_name: "Reconciliation_New_KG_123", ...}
Loaded 1 valid rulesets
```

**If you see errors:**
```
Error loading rulesets: HTTP 404: Not Found
Error loading rulesets: Server returned non-JSON response
```

---

### Step 3: Check Network Tab

**In Browser DevTools:**
1. Go to **Network** tab
2. Navigate to KPI Management page
3. Look for request to `/v1/reconciliation/rulesets`
4. Click on it to see details

**Check Response:**
- Status should be **200 OK** (not 404)
- Response should be JSON (not HTML)
- Should contain `"success": true`

**If status is 404:**
- Route not fixed
- Backend not running
- Check backend logs

**If response is HTML:**
- Backend returning error page
- Check backend logs for errors

---

### Step 4: Check Backend Logs

**Look for messages like:**

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
INFO:     GET /v1/reconciliation/rulesets
Found 1 rulesets
```

**If you see errors:**
```
ERROR: Error listing rulesets: [error message]
```

---

## 🔧 Common Issues and Solutions

### Issue 1: Empty Rulesets Array

**Symptom:** Response shows `"rulesets": []`

**Causes:**
1. No rulesets created yet
2. Rulesets folder doesn't exist
3. Rulesets folder is empty

**Solution:**
1. Create a ruleset first
2. Check: `data/reconciliation_rules/` folder exists
3. Check: Folder contains `.json` files

---

### Issue 2: HTTP 404 Error

**Symptom:** Network tab shows 404 status

**Causes:**
1. Backend not running
2. Route not fixed (still has `/v1/v1/` prefix)
3. Wrong URL in frontend

**Solution:**
1. Start backend: `python -m uvicorn kg_builder.main:app --reload`
2. Verify route: `curl http://localhost:8000/v1/reconciliation/rulesets`
3. Check frontend URL: Should be `/v1/reconciliation/rulesets`

---

### Issue 3: Non-JSON Response

**Symptom:** Error "Server returned non-JSON response"

**Causes:**
1. Backend returning HTML error page
2. Backend crashed
3. Wrong endpoint

**Solution:**
1. Check backend logs for errors
2. Restart backend
3. Verify endpoint URL

---

### Issue 4: Rulesets Loaded But Dropdown Empty

**Symptom:** Console shows rulesets loaded, but dropdown is empty

**Causes:**
1. Rulesets missing `ruleset_id` field
2. Rulesets missing `ruleset_name` field
3. Frontend filtering out invalid rulesets

**Solution:**
1. Check console: "First ruleset: {...}"
2. Verify it has `ruleset_id` and `ruleset_name`
3. Check backend response format

---

## 📋 Verification Checklist

### Backend
- [ ] Backend server running on port 8000
- [ ] No errors in backend logs
- [ ] `data/reconciliation_rules/` folder exists
- [ ] Folder contains `.json` ruleset files
- [ ] API endpoint returns 200 OK
- [ ] Response contains `"success": true`
- [ ] Response contains `"rulesets": [...]`

### Frontend
- [ ] Frontend server running on port 3000
- [ ] No errors in browser console
- [ ] Network request shows 200 OK
- [ ] Response is valid JSON
- [ ] Console shows "Loaded X valid rulesets"
- [ ] Rulesets have `ruleset_id` field
- [ ] Rulesets have `ruleset_name` field

### Dropdown
- [ ] Dropdown shows rulesets (not "No rulesets available")
- [ ] Can click dropdown to see list
- [ ] Can select a ruleset
- [ ] Selected value appears in form

---

## 🔍 Expected Response Format

### Backend Response
```json
{
  "success": true,
  "rulesets": [
    {
      "ruleset_id": "RECON_9240A5F7",
      "ruleset_name": "Reconciliation_New_KG_123",
      "schemas": ["newdqschema"],
      "rule_count": 5,
      "created_at": "2025-10-25T17:30:12.323851",
      "generated_from_kg": "kg_name"
    }
  ],
  "count": 1
}
```

### Frontend Expects
- `ruleset_id` - Used as MenuItem key and value
- `ruleset_name` - Displayed in dropdown
- Both fields are **required**

---

## 🚀 Quick Test

### 1. Start Backend
```bash
python -m uvicorn kg_builder.main:app --reload
```

### 2. Test API
```bash
curl http://localhost:8000/v1/reconciliation/rulesets
```

### 3. Start Frontend
```bash
cd web-app
npm start
```

### 4. Check Console
1. Open DevTools (F12)
2. Go to Console tab
3. Navigate to KPI Management
4. Look for "Loaded X valid rulesets" message

### 5. Test Dropdown
1. Click "Create KPI" button
2. Ruleset dropdown should show values
3. Select a ruleset
4. Should work without errors

---

## 📞 If Still Not Working

**Collect this information:**

1. **Backend response:**
   ```bash
   curl http://localhost:8000/v1/reconciliation/rulesets
   ```

2. **Backend logs:**
   - Copy any error messages

3. **Browser console logs:**
   - Screenshot or copy console output

4. **Network response:**
   - Screenshot of Network tab showing the request

5. **File system:**
   - Check if `data/reconciliation_rules/` exists
   - List files: `ls data/reconciliation_rules/`

---

## ✨ Summary

The ruleset dropdown should work if:
1. ✅ Backend is running
2. ✅ Rulesets exist in `data/reconciliation_rules/`
3. ✅ API returns 200 OK with valid JSON
4. ✅ Rulesets have `ruleset_id` and `ruleset_name`
5. ✅ Frontend console shows "Loaded X valid rulesets"

Use this guide to identify where the issue is!


