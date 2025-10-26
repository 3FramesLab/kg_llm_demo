# Field Preferences Format Error - Fixed! ✅

## 🔴 Problem

When creating a Knowledge Graph with field preferences, you got this error:

```json
{
  "type": "list_type",
  "loc": ["body", "field_preferences"],
  "msg": "Input should be a valid list",
  "input": {
    "field_preferences": [...]
  }
}
```

---

## 🔍 Root Cause

The backend expects `field_preferences` to be a **list/array**, but the frontend was sending it wrapped in an object:

```javascript
// WRONG: Wrapped in object
{
  "field_preferences": [
    { "table_name": "...", ... }
  ]
}

// RIGHT: Direct array
[
  { "table_name": "...", ... }
]
```

When you pasted JSON with the outer wrapper, it was being sent as-is to the backend, causing validation to fail.

---

## ✅ Solution

Updated the frontend to handle **both formats**:

```javascript
// Parse field preferences
let parsed = JSON.parse(fieldPreferencesInput);

// Handle both formats:
// 1. Direct array: [{ table_name: "...", ... }]
// 2. Wrapped object: { field_preferences: [{ table_name: "...", ... }] }
if (parsed.field_preferences && Array.isArray(parsed.field_preferences)) {
  payload.field_preferences = parsed.field_preferences;
} else if (Array.isArray(parsed)) {
  payload.field_preferences = parsed;
} else {
  setError('Field preferences must be a JSON array or object with field_preferences array');
  return;
}
```

---

## 📁 Files Modified

| File | Changes |
|------|---------|
| `web-app/src/pages/KnowledgeGraph.js` | Added dual format support for field_preferences |

---

## 🔧 What's Fixed

✅ **Accepts direct array format**: `[{ table_name: "...", ... }]`
✅ **Accepts wrapped format**: `{ field_preferences: [{ table_name: "...", ... }] }`
✅ **Better error messages**: Clear feedback if format is wrong
✅ **Console logging**: Shows parsed field preferences
✅ **Helper text**: Explains both formats are supported

---

## 📊 Supported Formats

### Format 1: Direct Array (Recommended)
```json
[
  {
    "table_name": "hana_material_master",
    "priority_fields": ["MATERIAL"],
    "exclude_fields": ["Business Unit", "Product Line"],
    "field_hints": {
      "MATERIAL": "PLANNING_SKU"
    }
  },
  {
    "table_name": "brz_lnd_OPS_EXCEL_GPU",
    "priority_fields": ["PLANNING_SKU"],
    "field_hints": {
      "PLANNING_SKU": "MATERIAL"
    },
    "filter_hints": {
      "Active_Inactive": "Inactive"
    }
  }
]
```

### Format 2: Wrapped Object
```json
{
  "field_preferences": [
    {
      "table_name": "hana_material_master",
      "priority_fields": ["MATERIAL"],
      "exclude_fields": ["Business Unit", "Product Line"],
      "field_hints": {
        "MATERIAL": "PLANNING_SKU"
      }
    },
    {
      "table_name": "brz_lnd_OPS_EXCEL_GPU",
      "priority_fields": ["PLANNING_SKU"],
      "field_hints": {
        "PLANNING_SKU": "MATERIAL"
      },
      "filter_hints": {
        "Active_Inactive": "Inactive"
      }
    }
  ]
}
```

---

## 🚀 How to Use

### Step 1: Go to Generate KG Tab
1. Click **Generate KG** tab
2. Enter KG name
3. Select schemas
4. Enable **Use LLM Enhancement**

### Step 2: Add Field Preferences
1. Click **Field Preferences (Optional - Advanced)**
2. Paste your JSON (either format works!)
3. Click **Generate Knowledge Graph**

### Step 3: Verify
- ✅ No validation errors
- ✅ KG created successfully
- ✅ Console shows: "✅ Field preferences parsed: [...]"

---

## 🧪 Testing

### Test 1: Direct Array Format
```json
[
  {
    "table_name": "hana_material_master",
    "priority_fields": ["MATERIAL"],
    "field_hints": {
      "MATERIAL": "PLANNING_SKU"
    }
  }
]
```
✅ Should work

### Test 2: Wrapped Object Format
```json
{
  "field_preferences": [
    {
      "table_name": "hana_material_master",
      "priority_fields": ["MATERIAL"],
      "field_hints": {
        "MATERIAL": "PLANNING_SKU"
      }
    }
  ]
}
```
✅ Should work

### Test 3: Invalid Format
```json
{
  "invalid": "format"
}
```
❌ Should show error: "Field preferences must be a JSON array or object with field_preferences array"

---

## 🔍 Console Logging

### Success
```
✅ Field preferences parsed: [
  {
    "table_name": "hana_material_master",
    "priority_fields": ["MATERIAL"],
    ...
  }
]
```

### Error
```
Invalid JSON in field preferences: Unexpected token
```

---

## 📋 Field Preference Structure

Each preference object should have:

```json
{
  "table_name": "string (required)",
  "priority_fields": ["array of field names (optional)"],
  "exclude_fields": ["array of field names to skip (optional)"],
  "field_hints": {
    "source_field": "target_field (optional)"
  },
  "filter_hints": {
    "field_name": "value or [array of values] (optional)"
  }
}
```

---

## 💡 Tips

### Tip 1: Use Direct Array Format
Simpler and cleaner:
```json
[{ "table_name": "...", ... }]
```

### Tip 2: Copy from Documentation
Use the placeholder example in the UI as a starting point.

### Tip 3: Validate JSON
Use an online JSON validator before pasting.

### Tip 4: Check Console
Open DevTools (F12) to see if field preferences were parsed correctly.

---

## ✨ Summary

✅ Accepts both JSON array and wrapped object formats
✅ Better error messages for invalid formats
✅ Console logging for debugging
✅ Helper text explains both formats
✅ Backward compatible with existing code

Now you can paste field preferences in either format! 🎉


