# Natural Language Definitions - Troubleshooting Guide

## 🔴 Problem: "Definitions" Section Not Showing

### Symptom
You go to the Natural Language page but don't see the "Natural Language Definitions" section or the text input fields.

### Root Causes & Solutions

#### Cause 1: Wrong Input Mode Selected

**Problem**: You're in "Explicit Pairs (V2)" mode instead of "Natural Language (V1)" mode

**Solution**:
1. Look for the "Relationship Input Mode" section
2. Find the radio buttons:
   - ☐ Natural Language (V1)
   - ☐ Explicit Pairs (V2 - Recommended)
3. Click on "Natural Language (V1)" radio button
4. The definitions section should now appear

**Visual Guide**:
```
┌─────────────────────────────────────────┐
│ Relationship Input Mode                 │
├─────────────────────────────────────────┤
│ ◉ Natural Language (V1)                 │  ← Click here
│ ○ Explicit Pairs (V2 - Recommended)     │
└─────────────────────────────────────────┘
```

---

#### Cause 2: Page Not Fully Loaded

**Problem**: The page is still loading or didn't load properly

**Solution**:
1. Refresh the page: Press `F5` or `Ctrl+R`
2. Wait for the page to fully load
3. Check browser console for errors: Press `F12` → Console tab
4. Look for any red error messages

**If you see errors**:
- Take a screenshot of the error
- Check that the backend is running: `http://localhost:8000/docs`
- Restart the backend if needed

---

#### Cause 3: Browser Cache Issue

**Problem**: Old version of the page is cached in your browser

**Solution**:
1. Clear browser cache:
   - **Chrome**: Ctrl+Shift+Delete
   - **Firefox**: Ctrl+Shift+Delete
   - **Safari**: Cmd+Shift+Delete
2. Select "All time" or "Everything"
3. Check "Cookies and other site data"
4. Click "Clear data"
5. Refresh the page

---

#### Cause 4: Wrong URL

**Problem**: You're on the wrong page

**Solution**:
1. Check the URL in the address bar
2. Should be: `http://localhost:3000/natural-language`
3. If not, click "Natural Language" in the left sidebar
4. Or manually type the URL

---

## 🔴 Problem: "Integrate & Generate Rules" Button is Disabled

### Symptom
The button is grayed out and you can't click it.

### Root Causes & Solutions

#### Cause 1: Missing Knowledge Graph Selection

**Problem**: You haven't selected a Knowledge Graph

**Solution**:
1. Find the "Knowledge Graph" dropdown
2. Click it
3. Select a KG from the list
4. Example: "my_reconciliation_kg"

**Visual Guide**:
```
┌─────────────────────────────────────────┐
│ Knowledge Graph                         │
├─────────────────────────────────────────┤
│ [Select a knowledge graph ▼]            │  ← Click here
│ - my_reconciliation_kg                  │
│ - test_kg                               │
│ - demo_kg                               │
└─────────────────────────────────────────┘
```

---

#### Cause 2: No Schemas Selected

**Problem**: You haven't selected any schemas

**Solution**:
1. Find the "Select Schemas" section
2. Check at least one schema checkbox
3. Example: Check "hana_material_master"

**Visual Guide**:
```
┌─────────────────────────────────────────┐
│ Select Schemas                          │
├─────────────────────────────────────────┤
│ ☐ hana_material_master                  │  ← Check this
│ ☐ brz_lnd_RBP_GPU                       │
│ ☐ brz_lnd_OPS_EXCEL_GPU                 │
│ ☐ brz_lnd_SKU_LIFNR_Excel               │
└─────────────────────────────────────────┘
```

---

#### Cause 3: No Definitions Entered (NL Mode)

**Problem**: You're in NL mode but haven't entered any definitions

**Solution**:
1. Make sure you're in "Natural Language (V1)" mode
2. Click in the text field
3. Type a definition
4. Example: "Material master MATERIAL matches OPS GPU PLANNING_SKU"

**Visual Guide**:
```
┌─────────────────────────────────────────┐
│ Natural Language Definitions            │
├─────────────────────────────────────────┤
│ [Enter a relationship definition...  ]  │  ← Type here
│                                         │
│ [Add Definition]                        │
└─────────────────────────────────────────┘
```

---

#### Cause 4: No Pairs Entered (Pairs Mode)

**Problem**: You're in Pairs mode but haven't entered any JSON

**Solution**:
1. Make sure you're in "Explicit Pairs (V2)" mode
2. Click in the text field
3. Paste or type JSON array
4. Example:
```json
[
  {
    "source_table": "hana_material_master",
    "source_column": "MATERIAL",
    "target_table": "brz_lnd_OPS_EXCEL_GPU",
    "target_column": "PLANNING_SKU",
    "relationship_type": "MATCHES",
    "confidence": 0.98
  }
]
```

---

## 🔴 Problem: "Invalid JSON" Error

### Symptom
You get an error message: "Invalid JSON in relationship pairs: ..."

### Root Causes & Solutions

#### Cause 1: Missing Quotes

**Problem**: Strings are not quoted

**Wrong**:
```json
{
  source_table: hana_material_master,  ← Missing quotes!
  source_column: MATERIAL
}
```

**Correct**:
```json
{
  "source_table": "hana_material_master",  ← Quoted!
  "source_column": "MATERIAL"
}
```

---

#### Cause 2: Missing Commas

**Problem**: Missing commas between fields

**Wrong**:
```json
{
  "source_table": "hana_material_master"  ← Missing comma!
  "source_column": "MATERIAL"
}
```

**Correct**:
```json
{
  "source_table": "hana_material_master",  ← Comma added!
  "source_column": "MATERIAL"
}
```

---

#### Cause 3: Trailing Comma

**Problem**: Extra comma at the end

**Wrong**:
```json
[
  {
    "source_table": "hana_material_master",
    "source_column": "MATERIAL",  ← Trailing comma!
  }
]
```

**Correct**:
```json
[
  {
    "source_table": "hana_material_master",
    "source_column": "MATERIAL"  ← No trailing comma!
  }
]
```

---

#### Solution: Use JSON Validator

1. Go to: https://jsonlint.com/
2. Paste your JSON
3. Click "Validate JSON"
4. Fix any errors shown
5. Copy the corrected JSON back

---

## 🔴 Problem: Processing Takes Too Long or Hangs

### Symptom
You click "Integrate & Generate Rules" but nothing happens or it takes forever.

### Root Causes & Solutions

#### Cause 1: Backend Not Running

**Problem**: The backend server is not running

**Solution**:
1. Check if backend is running: `http://localhost:8000/docs`
2. If not, start it:
   ```bash
   cd d:\learning\dq-poc
   python -m uvicorn kg_builder.main:app --reload --host 0.0.0.0 --port 8000
   ```
3. Wait for it to start
4. Try again

---

#### Cause 2: LLM Service Not Available

**Problem**: OpenAI API key is not set or invalid

**Solution**:
1. Uncheck "Use LLM for Enhanced Parsing"
2. Try again
3. Or set your OpenAI API key:
   ```bash
   set OPENAI_API_KEY=your_key_here
   ```

---

#### Cause 3: Large Dataset

**Problem**: You're processing a very large knowledge graph

**Solution**:
1. Wait longer (can take several minutes)
2. Check browser console for progress: Press `F12` → Console
3. Or try with fewer schemas first

---

## 🔴 Problem: No Results After Submission

### Symptom
You submit the form but don't see any results on the right side.

### Root Causes & Solutions

#### Cause 1: Backend Error

**Solution**:
1. Open browser console: Press `F12`
2. Go to "Network" tab
3. Look for failed requests (red)
4. Click on the failed request
5. Check the "Response" tab for error message
6. Fix the error based on the message

---

#### Cause 2: Results Not Displaying

**Solution**:
1. Scroll down on the right side
2. Results might be below the fold
3. Or check the browser console for JavaScript errors

---

## ✅ Verification Checklist

Before submitting, verify:

- ✓ You're on the "Natural Language" page
- ✓ You're in the correct input mode (NL or Pairs)
- ✓ Knowledge Graph is selected
- ✓ At least one schema is checked
- ✓ At least one definition/pair is entered
- ✓ JSON is valid (if using Pairs mode)
- ✓ Backend is running
- ✓ Browser console has no errors

---

## 🆘 Still Having Issues?

### Debug Steps

1. **Check Backend Logs**:
   ```bash
   # Look for error messages in the terminal where backend is running
   ```

2. **Check Browser Console**:
   - Press `F12`
   - Go to "Console" tab
   - Look for red error messages

3. **Check Network Requests**:
   - Press `F12`
   - Go to "Network" tab
   - Click "Integrate & Generate Rules"
   - Look for failed requests
   - Click on them to see error details

4. **Test API Directly**:
   ```bash
   curl -X POST http://localhost:8000/v1/kg/integrate-nl-relationships \
     -H "Content-Type: application/json" \
     -d '{
       "kg_name": "test_kg",
       "schemas": ["schema1"],
       "nl_definitions": ["test definition"],
       "use_llm": false,
       "min_confidence": 0.7
     }'
   ```

5. **Restart Everything**:
   - Stop backend (Ctrl+C)
   - Stop frontend (Ctrl+C)
   - Start backend again
   - Start frontend again
   - Try again

---

## 📞 Getting Help

If you're still stuck:
1. Check the documentation: `docs/NL_DEFINITIONS_GUIDE.md`
2. Check the API documentation: `http://localhost:8000/docs`
3. Review the code: `web-app/src/pages/NaturalLanguage.js`
4. Check backend logs for detailed error messages


