# Field Hints Visual Guide

## The Problem: Mismatched Field Names

```
HANA Material Master          Data Lake GPU Specs
┌─────────────────────┐       ┌──────────────────────┐
│ MATERIAL            │       │ PLANNING_SKU         │
│ MATERIAL_DESC       │       │ GPU_MODEL            │
│ INTERNAL_NOTES      │       │ PRODUCT_TYPE         │
│ TEMP_FIELD          │       │ STAGING_FLAG         │
└─────────────────────┘       └──────────────────────┘
        ↓                              ↓
   Without hints:              Without hints:
   LLM might miss that         LLM might miss that
   MATERIAL = PLANNING_SKU     these are the same!
```

## The Solution: Field Hints

```
HANA Material Master          Data Lake GPU Specs
┌─────────────────────┐       ┌──────────────────────┐
│ MATERIAL ──────────────────→ PLANNING_SKU         │
│ MATERIAL_DESC       │       │ GPU_MODEL ←────────┐ │
│ INTERNAL_NOTES (X)  │       │ PRODUCT_TYPE ──────┘ │
│ TEMP_FIELD (X)      │       │ STAGING_FLAG (X)     │
└─────────────────────┘       └──────────────────────┘
        ↓                              ↓
   With hints:                 With hints:
   LLM knows MATERIAL =        LLM knows PLANNING_SKU =
   PLANNING_SKU                MATERIAL & GPU_MODEL =
                               PRODUCT_TYPE
```

## JSON Structure Visualization

```
┌─ Field Preferences Array
│
├─ Table 1: hana_material_master
│  ├─ field_hints: { "MATERIAL": "PLANNING_SKU" }
│  │  └─ Tells LLM: "These fields are the same"
│  │
│  ├─ priority_fields: ["MATERIAL", "MATERIAL_DESC"]
│  │  └─ Focus on these first
│  │
│  └─ exclude_fields: ["INTERNAL_NOTES", "TEMP_FIELD"]
│     └─ Skip these entirely
│
└─ Table 2: brz_lnd_OPS_EXCEL_GPU
   ├─ field_hints: { "PLANNING_SKU": "MATERIAL", "GPU_MODEL": "PRODUCT_TYPE" }
   │  └─ Bidirectional mapping + additional hints
   │
   ├─ priority_fields: ["PLANNING_SKU", "GPU_MODEL"]
   │  └─ Focus on these first
   │
   └─ exclude_fields: ["STAGING_FLAG"]
      └─ Skip this field
```

## Data Flow with Field Hints

```
┌─────────────────────────────────────────────────────────────┐
│ User Input: Schemas + Field Hints                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Schemas: hana_material_master, brz_lnd_OPS_EXCEL_GPU   │ │
│ │ Hints: MATERIAL → PLANNING_SKU                          │ │
│ │ Priorities: MATERIAL, PLANNING_SKU                      │ │
│ │ Excludes: INTERNAL_NOTES, STAGING_FLAG                 │ │
│ └─────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ LLM Processing                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 1. Read field hints                                     │ │
│ │ 2. Prioritize MATERIAL, PLANNING_SKU                    │ │
│ │ 3. Skip INTERNAL_NOTES, STAGING_FLAG                   │ │
│ │ 4. Infer relationships                                  │ │
│ │ 5. Generate high-confidence rules                       │ │
│ └─────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Output: Knowledge Graph + Rules                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Relationships:                                          │ │
│ │ • MATERIAL --[MATCHES]--> PLANNING_SKU (confidence: 95%)│ │
│ │ • GPU_MODEL --[MATCHES]--> PRODUCT_TYPE (confidence: 90%)│ │
│ │                                                         │ │
│ │ Rules:                                                  │ │
│ │ • Rule 1: MATERIAL → PLANNING_SKU (EXACT)              │ │
│ │ • Rule 2: GPU_MODEL → PRODUCT_TYPE (SEMANTIC)          │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Field Hints Components

### 1. Field Hints (The Core)
```
"field_hints": {
  "MATERIAL": "PLANNING_SKU",
  "GPU_MODEL": "PRODUCT_TYPE"
}

What it means:
┌──────────────────────────────────────────┐
│ MATERIAL in this table                   │
│ represents the same data as              │
│ PLANNING_SKU in another table            │
└──────────────────────────────────────────┘
```

### 2. Priority Fields (The Focus)
```
"priority_fields": ["MATERIAL", "MATERIAL_DESC"]

What it means:
┌──────────────────────────────────────────┐
│ When inferring relationships,            │
│ focus on these fields first              │
│ They are important for matching          │
└──────────────────────────────────────────┘
```

### 3. Exclude Fields (The Filter)
```
"exclude_fields": ["INTERNAL_NOTES", "TEMP_FIELD"]

What it means:
┌──────────────────────────────────────────┐
│ Skip these fields entirely               │
│ They are not relevant for matching       │
│ They are internal/temporary/staging      │
└──────────────────────────────────────────┘
```

## Impact Comparison

### Without Field Hints
```
LLM Processing:
┌─────────────────────────────────────────┐
│ • Analyze all fields                    │
│ • Guess relationships                   │
│ • Include internal/staging fields       │
│ • Generate generic rules                │
└─────────────────────────────────────────┘
         ↓
Results:
┌─────────────────────────────────────────┐
│ Rules: 5-8                              │
│ Confidence: 0.6-0.7 (Medium)            │
│ Accuracy: ~60%                          │
│ May miss MATERIAL ↔ PLANNING_SKU        │
└─────────────────────────────────────────┘
```

### With Field Hints
```
LLM Processing:
┌─────────────────────────────────────────┐
│ • Read field hints                      │
│ • Focus on priority fields              │
│ • Skip excluded fields                  │
│ • Generate guided rules                 │
└─────────────────────────────────────────┘
         ↓
Results:
┌─────────────────────────────────────────┐
│ Rules: 8-12                             │
│ Confidence: 0.8-0.95 (High)             │
│ Accuracy: ~95%                          │
│ Explicit MATERIAL ↔ PLANNING_SKU match  │
└─────────────────────────────────────────┘
```

## Step-by-Step Usage

```
Step 1: Prepare
┌─────────────────────────────────────────┐
│ Identify:                               │
│ • Source table: hana_material_master    │
│ • Target table: brz_lnd_OPS_EXCEL_GPU  │
│ • Matching fields: MATERIAL, PLANNING_SKU│
│ • Key fields: MATERIAL, GPU_MODEL       │
│ • Skip fields: INTERNAL_NOTES, STAGING  │
└─────────────────────────────────────────┘
         ↓
Step 2: Create JSON
┌─────────────────────────────────────────┐
│ Build field preferences JSON            │
│ (See examples in docs)                  │
└─────────────────────────────────────────┘
         ↓
Step 3: Paste in UI
┌─────────────────────────────────────────┐
│ Knowledge Graph or Reconciliation page  │
│ → Field Preferences accordion           │
│ → Paste JSON                            │
└─────────────────────────────────────────┘
         ↓
Step 4: Generate
┌─────────────────────────────────────────┐
│ Click "Generate Knowledge Graph"        │
│ or "Generate Rules"                     │
└─────────────────────────────────────────┘
         ↓
Step 5: Review Results
┌─────────────────────────────────────────┐
│ Check generated relationships/rules     │
│ Verify confidence scores                │
│ Validate accuracy                       │
└─────────────────────────────────────────┘
```

## Common Mistakes to Avoid

```
❌ WRONG: Typo in field name
"field_hints": { "MATERIAL": "PLANNING_SKUU" }
                                      ↑ typo

✅ RIGHT: Exact field name
"field_hints": { "MATERIAL": "PLANNING_SKU" }

---

❌ WRONG: Field doesn't exist
"priority_fields": ["MATERIAL", "NONEXISTENT_FIELD"]

✅ RIGHT: Only existing fields
"priority_fields": ["MATERIAL", "MATERIAL_DESC"]

---

❌ WRONG: Exclude fields you need
"exclude_fields": ["MATERIAL", "PLANNING_SKU"]

✅ RIGHT: Exclude only internal/staging
"exclude_fields": ["INTERNAL_NOTES", "STAGING_FLAG"]
```

## Quick Decision Tree

```
Do you have fields with
different names but same meaning?
    │
    ├─ YES → Use field_hints
    │
    └─ NO → Skip field_hints

Do you have key identifiers
to prioritize?
    │
    ├─ YES → Use priority_fields
    │
    └─ NO → Leave empty

Do you have internal/staging
fields to skip?
    │
    ├─ YES → Use exclude_fields
    │
    └─ NO → Leave empty
```


