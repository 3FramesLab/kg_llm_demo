# KPI Execution Dialog - UI Update ✅

## Changes Made

Updated `web-app/src/components/KPIExecutionDialog.js` to simplify the KPI execution interface.

---

## What Changed

### 1. **Knowledge Graph Field** → **Dropdown**
- **Before**: Text input field
- **After**: Material-UI Select dropdown populated from available KGs
- **Data Source**: `listKGs()` API call
- **Behavior**: Loads on dialog open

### 2. **Schema Field** → **Dropdown**
- **Before**: Text input field
- **After**: Material-UI Select dropdown populated from available schemas
- **Data Source**: `listSchemas()` API call
- **Behavior**: Loads on dialog open

### 3. **Ruleset Field** → **Removed**
- Completely removed from the form
- No longer sent to backend

### 4. **Database Type** → **Hardcoded to 'sqlserver'**
- **Before**: Text input field (default: 'mysql')
- **After**: Hardcoded constant value: `'sqlserver'`
- **Behavior**: Not shown in UI, always sent as 'sqlserver'

### 5. **Excluded Fields Section** → **Removed**
- Completely removed from the form
- No longer sent to backend
- Removed all related handlers:
  - `handleAddExcludedField()`
  - `handleRemoveExcludedField()`
  - `excludedFieldInput` state

### 6. **Use LLM Checkbox** → **Hidden & Checked**
- **Before**: Visible checkbox (default: checked)
- **After**: Hidden from UI, always set to `true`
- **Behavior**: Automatically enabled, not shown to user

---

## Form Data Structure

### Before
```javascript
{
  kg_name: '',
  select_schema: '',
  ruleset_name: '',
  db_type: 'mysql',
  limit_records: 1000,
  use_llm: true,
  excluded_fields: [],
}
```

### After
```javascript
{
  kg_name: '',
  select_schema: '',
  db_type: 'sqlserver',
  limit_records: 1000,
  use_llm: true,
}
```

---

## UI Fields (Visible to User)

1. **Knowledge Graph** (Dropdown) - Required
2. **Schema** (Dropdown) - Required
3. **Limit Records** (Number Input) - Optional (default: 1000)

---

## Hidden Fields (Sent to Backend)

- `db_type`: Always `'sqlserver'`
- `use_llm`: Always `true`

---

## API Calls

### On Dialog Open
```javascript
// Fetch available Knowledge Graphs
listKGs() → response.data.graphs

// Fetch available Schemas
listSchemas() → response.data.schemas
```

### On Execute
```javascript
executeKPI(kpiId, {
  kg_name: 'selected_kg',
  select_schema: 'selected_schema',
  db_type: 'sqlserver',
  limit_records: 1000,
  use_llm: true,
})
```

---

## Component Imports

**Added**:
- `MenuItem` from '@mui/material'
- `Select` from '@mui/material'
- `FormControl` from '@mui/material'
- `InputLabel` from '@mui/material'
- `listSchemas` from '../services/api'

**Removed**:
- `FormControlLabel` from '@mui/material'
- `Checkbox` from '@mui/material'
- `Chip` from '@mui/material'
- `Stack` from '@mui/material'

---

## State Changes

**Added**:
```javascript
const [schemas, setSchemas] = useState([]);
```

**Removed**:
```javascript
const [excludedFieldInput, setExcludedFieldInput] = useState('');
```

---

## Benefits

✅ **Simpler UI** - Only 3 visible fields
✅ **Better UX** - Dropdowns prevent invalid entries
✅ **Consistent Database** - Always uses SQL Server
✅ **LLM Always Enabled** - Automatic parsing enabled
✅ **Cleaner Code** - Removed unused functionality

---

## Testing

1. Open KPI Execution Dialog
2. Verify Knowledge Graph dropdown loads with available KGs
3. Verify Schema dropdown loads with available schemas
4. Select a KG and Schema
5. Verify Limit Records field works
6. Click Execute and verify form data is sent correctly

---

## File Modified

- `web-app/src/components/KPIExecutionDialog.js` (186 lines)
  - Reduced from 254 lines
  - Cleaner, more focused implementation

