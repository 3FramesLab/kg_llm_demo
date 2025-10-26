# Ruleset Dropdown Troubleshooting Guide 🔧

## Problem: "No rulesets available" Even Though Rulesets Exist

### Quick Diagnosis

Run the diagnostic test script:

```bash
python test_ruleset_dropdown.py
```

This will check:
1. ✅ Backend is running
2. ✅ Rulesets folder exists
3. ✅ API endpoint responds
4. ✅ Response format is correct
5. ✅ Rulesets have required fields

---

## 🚀 Quick Fix Steps

### Step 1: Start Backend
```bash
python -m uvicorn kg_builder.main:app --reload
```

### Step 2: Verify Rulesets Exist
```bash
# Check if rulesets folder exists
ls -la data/reconciliation_rules/

# Should show .json files like:
# RECON_9240A5F7.json
# RECON_ABC123.json
```

### Step 3: Test API Endpoint
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

### Step 4: Start Frontend
```bash
cd web-app
npm start
```

### Step 5: Check Browser Console
1. Open DevTools (F12)
2. Go to Console tab
3. Navigate to KPI Management page
4. Look for: `Loaded X valid rulesets`

---

## 🔍 Common Issues

### Issue 1: "No rulesets available" - Empty Array

**Symptom:** API returns `"rulesets": []`

**Cause:** No rulesets created yet

**Solution:**
1. Go to Reconciliation page
2. Create a ruleset first
3. Then try KPI Management again

---

### Issue 2: HTTP 404 Error

**Symptom:** Network tab shows 404 status

**Cause:** Backend not running or route not fixed

**Solution:**
```bash
# Start backend
python -m uvicorn kg_builder.main:app --reload

# Test endpoint
curl http://localhost:8000/v1/reconciliation/rulesets
```

---

### Issue 3: "Server returned non-JSON response"

**Symptom:** Error in browser console

**Cause:** Backend returning HTML error page

**Solution:**
1. Check backend logs for errors
2. Restart backend
3. Verify endpoint URL

---

### Issue 4: Rulesets Loaded But Dropdown Empty

**Symptom:** Console shows "Loaded X valid rulesets" but dropdown is empty

**Cause:** Rulesets missing required fields

**Solution:**
1. Check console: "First ruleset: {...}"
2. Verify it has `ruleset_id` and `ruleset_name`
3. Check backend response format

---

## 📋 Verification Checklist

### Backend
- [ ] Backend running: `python -m uvicorn kg_builder.main:app --reload`
- [ ] No errors in backend logs
- [ ] Rulesets folder exists: `data/reconciliation_rules/`
- [ ] Folder contains `.json` files
- [ ] API returns 200 OK: `curl http://localhost:8000/v1/reconciliation/rulesets`
- [ ] Response contains `"success": true`
- [ ] Response contains `"rulesets": [...]`

### Frontend
- [ ] Frontend running: `cd web-app && npm start`
- [ ] No errors in browser console
- [ ] Network request shows 200 OK
- [ ] Response is valid JSON
- [ ] Console shows "Loaded X valid rulesets"

### Dropdown
- [ ] Dropdown shows rulesets (not "No rulesets available")
- [ ] Can click dropdown to see list
- [ ] Can select a ruleset
- [ ] Selected value appears in form

---

## 🧪 Manual Testing

### Test 1: Backend Response
```bash
curl -s http://localhost:8000/v1/reconciliation/rulesets | python -m json.tool
```

Should show:
- `"success": true`
- `"rulesets": [...]` with at least one ruleset
- Each ruleset has `ruleset_id` and `ruleset_name`

### Test 2: Browser Console
1. Open DevTools (F12)
2. Go to Console tab
3. Navigate to KPI Management
4. Look for logs:
   ```
   Raw rulesets response: {...}
   Rulesets array: [...]
   First ruleset: {...}
   Loaded 1 valid rulesets
   ```

### Test 3: Network Tab
1. Open DevTools (F12)
2. Go to Network tab
3. Navigate to KPI Management
4. Look for `/v1/reconciliation/rulesets` request
5. Should show:
   - Status: **200 OK**
   - Type: **fetch**
   - Response: Valid JSON

---

## 🔧 Enhanced Frontend Logging

The frontend now logs detailed information:

```javascript
// In browser console, you'll see:
Raw rulesets response: {success: true, rulesets: [...], count: 1}
Rulesets array: [{ruleset_id: "RECON_9240A5F7", ...}]
First ruleset: {ruleset_id: "RECON_9240A5F7", ruleset_name: "...", ...}
Loaded 1 valid rulesets
```

This helps identify:
- ✅ API is responding
- ✅ Response format is correct
- ✅ Rulesets have required fields
- ✅ Frontend is processing correctly

---

## 📁 Files Modified

| File | Changes |
|------|---------|
| `web-app/src/pages/KPIManagement.js` | Enhanced logging in `loadRulesets()` |
| `test_ruleset_dropdown.py` | New diagnostic test script |

---

## 🚀 Next Steps

1. **Run diagnostic test:**
   ```bash
   python test_ruleset_dropdown.py
   ```

2. **Check output:**
   - All checks should pass ✅
   - If any fail, follow the suggestions

3. **Test dropdown:**
   - Navigate to KPI Management
   - Click "Create KPI"
   - Ruleset dropdown should show values

4. **Create KPI:**
   - Select a ruleset
   - Fill in other fields
   - Click "Create"

---

## 📞 If Still Not Working

**Collect this information:**

1. **Diagnostic test output:**
   ```bash
   python test_ruleset_dropdown.py
   ```

2. **API response:**
   ```bash
   curl http://localhost:8000/v1/reconciliation/rulesets
   ```

3. **Browser console logs:**
   - Screenshot or copy console output

4. **Backend logs:**
   - Copy any error messages

5. **File system:**
   ```bash
   ls -la data/reconciliation_rules/
   ```

---

## ✨ Summary

The ruleset dropdown should work if:
1. ✅ Backend is running
2. ✅ Rulesets exist in `data/reconciliation_rules/`
3. ✅ API returns 200 OK with valid JSON
4. ✅ Rulesets have `ruleset_id` and `ruleset_name`
5. ✅ Frontend console shows "Loaded X valid rulesets"

Use the diagnostic test script to identify the issue!


