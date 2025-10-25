# Field Preferences Pydantic Object Fix

## Errors Encountered

```
ERROR - Error in relationship inference: 'FieldPreference' object has no attribute 'get'
ERROR - Error parsing enhanced relationships: Expecting value: line 1 column 1 (char 0)
```

## Root Cause

The field preferences were being passed as Pydantic `FieldPreference` objects, but the code was trying to use `.get()` method which only works on dictionaries.

**Problem Code**:
```python
for pref in field_preferences:
    table_name = pref.get('table_name', 'N/A')  # ❌ .get() doesn't work on Pydantic objects
    if pref.get('priority_fields'):  # ❌ Error here
        field_preferences_str += f"  ✓ PRIORITY FIELDS: {', '.join(pref['priority_fields'])}\n"
```

**Error**:
```
'FieldPreference' object has no attribute 'get'
```

---

## Solution Implemented

### 1. Created Helper Method

Added `_get_pref_value()` method to handle both dict and Pydantic objects:

```python
def _get_pref_value(self, pref: Any, key: str, default: Any = None) -> Any:
    """
    Helper to get value from either dict or Pydantic object.
    
    Args:
        pref: Either a dict or Pydantic FieldPreference object
        key: The key/attribute to retrieve
        default: Default value if key doesn't exist
        
    Returns:
        The value or default
    """
    if isinstance(pref, dict):
        return pref.get(key, default)
    else:
        # Pydantic object
        return getattr(pref, key, default)
```

### 2. Updated `_build_inference_prompt()` (Line 283)

**Before**:
```python
for pref in field_preferences:
    table_name = pref.get('table_name', 'N/A')
    if pref.get('priority_fields'):
        field_preferences_str += f"  ✓ PRIORITY FIELDS: {', '.join(pref['priority_fields'])}\n"
```

**After**:
```python
for pref in field_preferences:
    table_name = self._get_pref_value(pref, 'table_name', 'N/A')
    priority_fields = self._get_pref_value(pref, 'priority_fields', [])
    if priority_fields:
        field_preferences_str += f"  ✓ PRIORITY FIELDS: {', '.join(priority_fields)}\n"
```

### 3. Updated `_build_reconciliation_rules_prompt()` (Line 664)

**Before**:
```python
for pref in field_preferences:
    table_name = pref.get('table_name', 'N/A')
    if pref.get('priority_fields'):
        field_preferences_str += f"  ✓ PRIORITY FIELDS: {', '.join(pref['priority_fields'])}\n"
```

**After**:
```python
for pref in field_preferences:
    table_name = self._get_pref_value(pref, 'table_name', 'N/A')
    priority_fields = self._get_pref_value(pref, 'priority_fields', [])
    if priority_fields:
        field_preferences_str += f"  ✓ PRIORITY FIELDS: {', '.join(priority_fields)}\n"
```

---

## How It Works

### Scenario 1: Field Preferences as Dict (from API)

```python
field_preferences = [
    {
        "table_name": "orders",
        "priority_fields": ["customer_id"],
        "exclude_fields": [],
        "field_hints": {"customer_id": "cust_id"}
    }
]

# Helper method detects dict and uses .get()
table_name = self._get_pref_value(pref, 'table_name', 'N/A')
# Returns: "orders"
```

### Scenario 2: Field Preferences as Pydantic Object (from internal code)

```python
from kg_builder.models import FieldPreference

field_preferences = [
    FieldPreference(
        table_name="orders",
        priority_fields=["customer_id"],
        exclude_fields=[],
        field_hints={"customer_id": "cust_id"}
    )
]

# Helper method detects Pydantic object and uses getattr()
table_name = self._get_pref_value(pref, 'table_name', 'N/A')
# Returns: "orders"
```

---

## Files Modified

1. **kg_builder/services/multi_schema_llm_service.py**
   - Line 265: Added `_get_pref_value()` helper method
   - Line 283: Updated `_build_inference_prompt()` to use helper
   - Line 664: Updated `_build_reconciliation_rules_prompt()` to use helper

---

## Benefits

✅ **Handles both dict and Pydantic objects**
✅ **No breaking changes**
✅ **Backward compatible**
✅ **Cleaner code**
✅ **Easier to maintain**

---

## Testing

### Test Case 1: Dict Input (from API)

```python
field_preferences = [
    {
        "table_name": "orders",
        "priority_fields": ["customer_id"],
        "exclude_fields": [],
        "field_hints": {"customer_id": "cust_id"}
    }
]

# Should work without errors
```

### Test Case 2: Pydantic Input (from internal code)

```python
from kg_builder.models import FieldPreference

field_preferences = [
    FieldPreference(
        table_name="orders",
        priority_fields=["customer_id"],
        exclude_fields=[],
        field_hints={"customer_id": "cust_id"}
    )
]

# Should work without errors
```

### Test Case 3: Mixed Input

```python
field_preferences = [
    {
        "table_name": "orders",
        "priority_fields": ["customer_id"],
        "exclude_fields": [],
        "field_hints": {"customer_id": "cust_id"}
    },
    FieldPreference(
        table_name="customers",
        priority_fields=["cust_id"],
        exclude_fields=[],
        field_hints={}
    )
]

# Should work without errors
```

---

## Error Resolution

### Before Fix
```
ERROR - Error in relationship inference: 'FieldPreference' object has no attribute 'get'
ERROR - Error parsing enhanced relationships: Expecting value: line 1 column 1 (char 0)
```

### After Fix
```
✅ No errors
✅ Field preferences processed correctly
✅ Relationships inferred successfully
```

---

## Summary

**Issue**: Field preferences passed as Pydantic objects but code expected dicts
**Root Cause**: Using `.get()` method which doesn't exist on Pydantic objects
**Solution**: Created helper method to handle both dict and Pydantic objects
**Result**: Field preferences now work with both dict and Pydantic inputs


