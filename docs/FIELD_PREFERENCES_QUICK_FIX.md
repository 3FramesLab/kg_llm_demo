# Field Preferences Format Error - Quick Fix ✅

## Problem
```
Input should be a valid list
```

Error when creating KG with field preferences.

---

## Root Cause
Backend expects `field_preferences` as a **list**, but frontend was sending it wrapped in an object.

---

## Solution
Frontend now accepts **both formats**:

### Format 1: Direct Array (Recommended)
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

### Format 2: Wrapped Object
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

---

## What's Fixed

✅ Accepts direct array format
✅ Accepts wrapped object format
✅ Better error messages
✅ Console logging
✅ Helper text in UI

---

## How to Use

### Step 1: Go to Generate KG
1. Click **Generate KG** tab
2. Enter KG name
3. Select schemas
4. Enable **Use LLM Enhancement**

### Step 2: Add Field Preferences
1. Click **Field Preferences (Optional - Advanced)**
2. Paste your JSON (either format!)
3. Click **Generate Knowledge Graph**

### Step 3: Verify
- ✅ No validation errors
- ✅ KG created successfully
- ✅ Console shows: "✅ Field preferences parsed: [...]"

---

## Supported Formats

| Format | Example | Status |
|--------|---------|--------|
| Direct Array | `[{ table_name: "...", ... }]` | ✅ Works |
| Wrapped Object | `{ field_preferences: [...] }` | ✅ Works |
| Invalid | `{ invalid: "..." }` | ❌ Error |

---

## Field Preference Structure

```json
{
  "table_name": "string (required)",
  "priority_fields": ["array (optional)"],
  "exclude_fields": ["array (optional)"],
  "field_hints": {
    "source_field": "target_field"
  },
  "filter_hints": {
    "field_name": "value"
  }
}
```

---

## Testing

### Test 1: Direct Array
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
✅ Works

### Test 2: Wrapped Object
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
✅ Works

---

## Console Logging

### Success
```
✅ Field preferences parsed: [...]
```

### Error
```
Invalid JSON in field preferences: Unexpected token
```

---

## Tips

1. **Use direct array format** - Simpler and cleaner
2. **Copy from placeholder** - Use UI example as starting point
3. **Validate JSON** - Use online JSON validator
4. **Check console** - Open F12 to see parsing results

---

## Files Modified

- `web-app/src/pages/KnowledgeGraph.js` - Dual format support

---

## Summary

✅ Accepts both JSON array and wrapped object formats
✅ Better error messages
✅ Console logging for debugging
✅ Helper text in UI

Now create KGs with field preferences! 🎉


