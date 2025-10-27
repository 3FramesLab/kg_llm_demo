# Natural Language Definitions - Complete Guide

## 📍 Where to Find It

The Natural Language Definitions section is on the **"Natural Language to Reconciliation Rules"** page.

**Navigation**: 
- Click on **"Natural Language"** in the left sidebar
- Or go to: `http://localhost:3000/natural-language`

---

## 🎯 Page Layout

The page has two main sections:

### Left Side (Input Section)
```
┌─────────────────────────────────────────┐
│  Define Relationships                   │
├─────────────────────────────────────────┤
│  1. Select Knowledge Graph              │
│  2. Select Schemas                      │
│  3. Choose Input Mode (NL or Pairs)     │
│  4. Enter Definitions/Pairs             │
│  5. Configure Options                   │
│  6. Click "Integrate & Generate Rules"  │
└─────────────────────────────────────────┘
```

### Right Side (Preview Section)
```
┌─────────────────────────────────────────┐
│  Request Placeholder                    │
│  (Shows JSON preview of your input)     │
├─────────────────────────────────────────┤
│  Results (after submission)             │
│  (Shows integration and rule results)   │
└─────────────────────────────────────────┘
```

---

## 📋 Step-by-Step Guide

### Step 1: Select Knowledge Graph
```
1. Click the "Knowledge Graph" dropdown
2. Select a KG from the list
3. Example: "my_reconciliation_kg"
```

### Step 2: Select Schemas
```
1. Check the schemas you want to use
2. You can select multiple schemas
3. Example: Check "hana_material_master" and "brz_lnd_RBP_GPU"
```

### Step 3: Choose Input Mode

You have two options:

#### Option A: Natural Language (V1)
```
Radio Button: "Natural Language (V1)"

This mode allows you to write relationships in plain English.
Examples:
- "Products are supplied by Vendors"
- "Orders contain Products"
- "Material master references planning SKU"
```

#### Option B: Explicit Pairs (V2 - Recommended)
```
Radio Button: "Explicit Pairs (V2 - Recommended)"

This mode allows you to define exact source→target relationships.
More precise and recommended for production use.
```

---

## 🔤 Natural Language Mode (V1)

### How to Use

1. **Select "Natural Language (V1)" radio button**

2. **Enter Definitions**
   - Click in the text field
   - Type your relationship definition
   - Example: "Material master MATERIAL column matches OPS GPU PLANNING_SKU"

3. **Add More Definitions**
   - Click "Add Definition" button
   - Each definition is processed separately
   - You can have multiple definitions

4. **Remove Definitions**
   - Click the trash icon next to a definition
   - Only available if you have more than 1 definition

### Example Definitions

```
"Products are supplied by Vendors"
"Orders contain Products"
"Inspection results reference design codes"
"Material master provides product information"
"Planning SKU matches material code"
```

### What Happens

1. The system reads your natural language definitions
2. Uses LLM to understand the relationships
3. Extracts table and column names
4. Creates relationship rules
5. Generates reconciliation rules

---

## 📊 Explicit Pairs Mode (V2 - Recommended)

### How to Use

1. **Select "Explicit Pairs (V2 - Recommended)" radio button**

2. **Enter JSON Pairs**
   - Click in the text field
   - Paste or type JSON array
   - Each object defines one relationship

### JSON Format

```json
[
  {
    "source_table": "hana_material_master",
    "source_column": "MATERIAL",
    "target_table": "brz_lnd_OPS_EXCEL_GPU",
    "target_column": "PLANNING_SKU",
    "relationship_type": "MATCHES",
    "confidence": 0.98,
    "bidirectional": true
  },
  {
    "source_table": "brz_lnd_OPS_EXCEL_GPU",
    "source_column": "PLANNING_SKU",
    "target_table": "brz_lnd_RBP_GPU",
    "target_column": "Material",
    "relationship_type": "MATCHES",
    "confidence": 0.95
  }
]
```

### Field Descriptions

| Field | Description | Example |
|-------|-------------|---------|
| `source_table` | Source table name | `hana_material_master` |
| `source_column` | Source column name | `MATERIAL` |
| `target_table` | Target table name | `brz_lnd_OPS_EXCEL_GPU` |
| `target_column` | Target column name | `PLANNING_SKU` |
| `relationship_type` | Type of relationship | `MATCHES`, `REFERENCES`, `CONTAINS` |
| `confidence` | Confidence score (0-1) | `0.98` |
| `bidirectional` | Is it bidirectional? | `true` or `false` |

---

## ⚙️ Configuration Options

### Use LLM for Enhanced Parsing
```
Checkbox: "Use LLM for Enhanced Parsing"

✓ Checked (default): Uses OpenAI to understand relationships
☐ Unchecked: Uses simple pattern matching
```

### Minimum Confidence
```
Slider: "Minimum Confidence: 0.7"

Range: 0 to 1
- 0.7 = Accept relationships with 70% confidence or higher
- 0.9 = Only accept high-confidence relationships
- 1.0 = Only accept perfect matches
```

---

## 🚀 Submit Your Definitions

### Button: "Integrate & Generate Rules"

```
1. Fill in all required fields:
   ✓ Knowledge Graph selected
   ✓ Schemas selected
   ✓ Definitions/Pairs entered

2. Click "Integrate & Generate Rules"

3. Wait for processing:
   ⏳ Step 1/2: Integrating relationships to Knowledge Graph...
   ⏳ Step 2/2: Generating reconciliation rules...
   ✅ Complete! Rules generated successfully.

4. View results on the right side
```

---

## 📊 Results

After submission, you'll see:

### Integration Results
```json
{
  "kg_name": "my_kg",
  "nl_relationships_added": 5,
  "explicit_pairs_added": 0,
  "total_relationships": 5
}
```

### Rule Generation Results
```json
{
  "ruleset_id": "ruleset_123",
  "rules_count": 12,
  "rules": [
    {
      "rule_id": "rule_1",
      "rule_name": "Material to Planning SKU",
      "source_table": "hana_material_master",
      "target_table": "brz_lnd_OPS_EXCEL_GPU",
      "confidence_score": 0.95
    }
  ]
}
```

---

## ❓ Troubleshooting

### Problem: "Integrate & Generate Rules" button is disabled

**Solution**: Check that you have:
- ✓ Selected a Knowledge Graph
- ✓ Selected at least one Schema
- ✓ Entered at least one Definition (NL mode) or Pairs (Pairs mode)

### Problem: Invalid JSON error

**Solution**: 
- Check your JSON syntax
- Use an online JSON validator
- Make sure all strings are quoted
- Make sure all commas are in the right place

### Problem: No definitions showing

**Solution**:
- Make sure you're in "Natural Language (V1)" mode
- Click "Add Definition" to add a new one
- The first definition field should be visible by default

### Problem: Relationships not being recognized

**Solution**:
- Use clearer language
- Include table and column names
- Example: "Material master MATERIAL column matches OPS GPU PLANNING_SKU"
- Or use Explicit Pairs mode for more control

---

## 💡 Tips & Best Practices

### Tip 1: Use Explicit Pairs for Production
- More precise
- No ambiguity
- Easier to debug

### Tip 2: Start with Natural Language
- Good for exploration
- Helps understand relationships
- Useful for documentation

### Tip 3: Use High Confidence Threshold
- Set minimum confidence to 0.8 or higher
- Ensures quality relationships
- Reduces false positives

### Tip 4: Test with Small Sets First
- Start with 1-2 definitions
- Verify results
- Then add more

### Tip 5: Check the Request Placeholder
- Shows what will be sent to the backend
- Helps verify your input
- Useful for debugging

---

## ✅ Summary

The Natural Language Definitions section allows you to:
- ✅ Define relationships in plain English (V1)
- ✅ Define explicit source→target pairs (V2)
- ✅ Integrate relationships into the Knowledge Graph
- ✅ Automatically generate reconciliation rules
- ✅ Configure confidence thresholds
- ✅ Use LLM for enhanced parsing

**Location**: Natural Language page in the left sidebar
**URL**: `http://localhost:3000/natural-language`


