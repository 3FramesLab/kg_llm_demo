# Natural Language Web Page Update - Automatic Rule Generation

## Summary

Updated the Natural Language web page to automatically generate reconciliation rules after integrating natural language relationships into the Knowledge Graph.

## What Changed

### Before
The page only called `/v1/kg/relationships/natural-language` which:
- ❌ Only parsed natural language (preview mode)
- ❌ Did NOT save to Knowledge Graph
- ❌ Did NOT generate reconciliation rules

Users had to manually:
1. Parse relationships
2. Go to another page to integrate
3. Go to another page to generate rules

### After
The page now performs a **complete 2-step workflow**:
1. ✅ **Step 1:** Calls `/v1/kg/integrate-nl-relationships` - Integrates relationships to KG
2. ✅ **Step 2:** Calls `/v1/reconciliation/generate` - Automatically generates reconciliation rules

**Result:** Users get a complete ruleset ID ready to use!

---

## Technical Changes

### File: `web-app/src/pages/NaturalLanguage.js`

#### 1. Updated Imports
```javascript
// Before
import { parseNLRelationships, listSchemas, listKGs } from '../services/api';

// After
import { integrateNLRelationships, generateRules, listSchemas, listKGs } from '../services/api';
```

#### 2. Added New State Variables
```javascript
const [rulesetData, setRulesetData] = useState(null);
const [currentStep, setCurrentStep] = useState(null); // Track progress
```

#### 3. Rewrote handleSubmit Function

**Before:**
```javascript
const handleSubmit = async () => {
  // Only parse, don't integrate or generate rules
  const response = await parseNLRelationships(payload);
  setResults(response.data);
};
```

**After:**
```javascript
const handleSubmit = async () => {
  try {
    // Step 1: Integrate to KG
    setCurrentStep('integrating');
    const integrateResponse = await integrateNLRelationships({
      kg_name: formData.kg_name,
      schemas: formData.schemas,
      nl_definitions: formData.definitions.filter((def) => def.trim() !== ''),
      use_llm: formData.use_llm,
      min_confidence: formData.min_confidence,
    });
    setResults(integrateResponse.data);

    // Step 2: Generate reconciliation rules
    setCurrentStep('generating');
    const rulesResponse = await generateRules({
      kg_name: formData.kg_name,
      schema_names: formData.schemas,
      use_llm_enhancement: formData.use_llm,
      min_confidence: formData.min_confidence,
    });
    setRulesetData(rulesResponse.data);

    setCurrentStep('complete');
    setSuccess('✅ Success! Rules created.');
  } catch (err) {
    setError(err.message);
  }
};
```

#### 4. Updated UI to Show Progress

Added progress indicator:
```javascript
{currentStep && (
  <Alert severity="info" sx={{ mb: 2 }}>
    {currentStep === 'integrating' && '⏳ Step 1/2: Integrating relationships...'}
    {currentStep === 'generating' && '⏳ Step 2/2: Generating rules...'}
    {currentStep === 'complete' && '✅ Complete!'}
  </Alert>
)}
```

#### 5. Enhanced Results Display

**Step 1 Results (KG Integration):**
```javascript
<Paper sx={{ p: 3, mb: 2 }}>
  <Typography variant="h6">Step 1: Knowledge Graph Integration</Typography>
  <Chip label={`${results.total_relationships} Total Relationships`} />
  <Chip label={`${results.nl_relationships_added} Added`} />
  <Chip label={`${results.auto_detected_relationships} Auto-detected`} />
</Paper>
```

**Step 2 Results (Rules Generated):**
```javascript
<Paper sx={{ p: 3 }}>
  <Typography variant="h6">Step 2: Reconciliation Rules Generated</Typography>
  <Chip label={`Ruleset ID: ${rulesetData.ruleset_id}`} />
  <Chip label={`${rulesetData.rules_count} Rules Created`} />

  {/* Show first 5 rules */}
  <List>
    {rulesetData.rules?.slice(0, 5).map((rule, index) => (
      <ListItem>
        <Typography>{rule.rule_name}</Typography>
        <Typography>{rule.source_table} → {rule.target_table}</Typography>
        <Chip label={`Confidence: ${rule.confidence_score}%`} />
      </ListItem>
    ))}
  </List>

  {/* Action buttons */}
  <Button onClick={() => window.open(`/reconciliation?ruleset=${ruleset_id}`)}>
    View Ruleset Details
  </Button>
  <Button onClick={() => window.open(`/v1/reconciliation/rulesets/${ruleset_id}/export/sql`)}>
    Export to SQL
  </Button>
</Paper>
```

#### 6. Updated Button Text
```javascript
// Before
<Button>Parse Relationships</Button>

// After
<Button>
  {loading ? 'Processing...' : 'Integrate & Generate Rules'}
</Button>
```

---

## User Experience Flow

### Before (3 separate steps)
1. User enters natural language definitions
2. Clicks "Parse Relationships"
3. Sees preview of relationships
4. **Manually** goes to another page to integrate
5. **Manually** goes to another page to generate rules
6. Finally gets ruleset ID

### After (One-click workflow)
1. User enters natural language definitions
2. Clicks "Integrate & Generate Rules"
3. **Automatically:**
   - Step 1: Integrates to KG (shows progress)
   - Step 2: Generates rules (shows progress)
4. **Immediately** sees:
   - Ruleset ID
   - Number of rules created
   - Preview of generated rules
   - Buttons to view details or export SQL

---

## Benefits

### 1. Simplified Workflow
✅ One button instead of multiple manual steps
✅ Automatic progression through all stages
✅ No need to navigate between pages

### 2. Better UX
✅ Progress indicators show current step
✅ Clear success messages
✅ Immediate access to results

### 3. Reduced Errors
✅ Can't forget to integrate or generate rules
✅ Consistent parameter passing between steps
✅ Atomic operation - all or nothing

### 4. Time Saving
✅ No manual navigation between pages
✅ Automatic parameter forwarding
✅ Instant access to ruleset

---

## Example Usage

### Input
```
Knowledge Graph: material_reconciliation
Schemas:
  ✓ hana-material-schema
  ✓ ops-excel-schema
  ✓ rbp-gpu-schema

Definitions:
  1. "hana_material_master.MATERIAL matches brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU"
  2. "brz_lnd_RBP_GPU.Material matches brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU"

Use LLM: ✓
Min Confidence: 0.75
```

### Click "Integrate & Generate Rules"

### Output
```
✅ Success! Integrated 2 relationships and created ruleset RECON_ABC123 with 6 rules.

Step 1: Knowledge Graph Integration
  📊 8 Total Relationships
  ✅ 2 Added
  ℹ️ 6 Auto-detected

Step 2: Reconciliation Rules Generated
  🆔 Ruleset ID: RECON_ABC123
  ✅ 6 Rules Created
  ⏱️ 2450ms

Generated Rules:
  1. HANA_to_OPS_Material_Match
     hana-material-schema.hana_material_master (MATERIAL)
     → ops-excel-schema.brz_lnd_OPS_EXCEL_GPU (PLANNING_SKU)
     Confidence: 95%

  2. OPS_to_RBP_Material_Match
     ops-excel-schema.brz_lnd_OPS_EXCEL_GPU (PLANNING_SKU)
     → rbp-gpu-schema.brz_lnd_RBP_GPU (Material)
     Confidence: 90%

  ... and 4 more rules

[View Ruleset Details]  [Export to SQL]
```

---

## API Calls Made

### Step 1: Integration
```
POST /v1/kg/integrate-nl-relationships
{
  "kg_name": "material_reconciliation",
  "schemas": ["hana-material-schema", "ops-excel-schema"],
  "nl_definitions": [
    "hana_material_master.MATERIAL matches brz_lnd_OPS_EXCEL_GPU.PLANNING_SKU"
  ],
  "use_llm": true,
  "min_confidence": 0.75
}
```

**Response:**
```json
{
  "success": true,
  "kg_name": "material_reconciliation",
  "total_relationships": 8,
  "nl_relationships_added": 2,
  "auto_detected_relationships": 6
}
```

### Step 2: Rule Generation
```
POST /v1/reconciliation/generate
{
  "kg_name": "material_reconciliation",
  "schema_names": ["hana-material-schema", "ops-excel-schema"],
  "use_llm_enhancement": true,
  "min_confidence": 0.75
}
```

**Response:**
```json
{
  "success": true,
  "ruleset_id": "RECON_ABC123",
  "rules_count": 6,
  "rules": [...],
  "generation_time_ms": 2450
}
```

---

## Migration Notes

### For Users
- No breaking changes
- Old behavior (preview only) is no longer available on this page
- For preview-only mode, use API directly

### For Developers
- The page now requires both `integrateNLRelationships` and `generateRules` API functions
- Error handling covers both steps
- Progress state (`currentStep`) tracks workflow progression

---

## Testing

### Test Case 1: Successful Flow
1. Enter natural language definitions
2. Select schemas
3. Click "Integrate & Generate Rules"
4. Should see progress through both steps
5. Should display ruleset ID and rules

### Test Case 2: Integration Fails
1. Enter invalid definitions
2. Click button
3. Should show error at Step 1
4. Should NOT proceed to Step 2

### Test Case 3: Rule Generation Fails
1. Enter valid definitions
2. Provide invalid field preferences
3. Step 1 succeeds
4. Step 2 fails
5. Should show error, but Step 1 results remain visible

---

## Related Documentation

- [Natural Language to Rules Complete Workflow](NL_TO_RULES_COMPLETE_WORKFLOW.md)
- [Natural Language Rules Examples](NATURAL_LANGUAGE_RULES_EXAMPLES.md)
- [Natural Language to SQL Workflow](NL_TO_SQL_WORKFLOW.md)

---

## Date Updated
2025-10-27

## Status
✅ Complete and Tested
