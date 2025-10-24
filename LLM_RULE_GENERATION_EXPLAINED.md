# How LLM Generates Reconciliation Rules - Simple Explanation

## 🎯 The Big Picture

The system generates reconciliation rules in **TWO WAYS**:

1. **Pattern-Based Rules** (Simple, Fast) ✅
2. **LLM-Based Rules** (Smart, Semantic) 🤖

---

## 📊 Step-by-Step Process

### Step 1: Load Schemas
```
Input: Schema names (e.g., "orderMgmt-catalog", "qinspect-designcode")
↓
Output: Schema information (tables, columns, data types)
```

### Step 2: Query Knowledge Graph
```
Input: Knowledge graph name
↓
Output: Relationships between entities (e.g., "catalog.id relates to design_code_master.id")
```

### Step 3: Generate Pattern-Based Rules (Always Done)
```
Logic: Look for matching column names
Example:
  - If both schemas have "id" column → Create rule: match on id
  - If both schemas have "code" column → Create rule: match on code
  - If both schemas have "name" column → Create rule: match on name

Output: Basic rules with 0.75 confidence
```

### Step 4: Generate LLM-Based Rules (If Enabled)
```
IF use_llm = true:
  ↓
  1. Prepare prompt with:
     - All schemas information
     - All relationships from KG
     - Instructions for rule generation
  ↓
  2. Send to OpenAI GPT-3.5-turbo (or GPT-4)
  ↓
  3. GPT analyzes and suggests:
     - Matching columns
     - Match strategies (exact, fuzzy, semantic)
     - Confidence scores
     - Transformation logic if needed
  ↓
  4. Parse GPT response and create rules
  ↓
  Output: Smart semantic rules
```

### Step 5: Combine & Filter
```
All Rules = Pattern-Based Rules + LLM Rules
↓
Filter: Keep only rules with confidence ≥ min_confidence (default 0.7)
↓
Remove: Duplicate rules
↓
Output: Final ruleset
```

---

## 🤖 What Does GPT Do?

### System Prompt (Role)
```
"You are an expert data integration specialist. 
Generate reconciliation rules for matching data across 
different database schemas."
```

### User Prompt (Task)
```
Given these schemas and relationships, generate rules that:
1. Identify matching columns across schemas
2. Suggest match strategies (exact, fuzzy, composite)
3. Provide SQL/Python transformation logic if needed
4. Score confidence for each rule

SCHEMAS:
{
  "orderMgmt-catalog": {
    "tables": {
      "catalog": {
        "columns": ["id", "code", "name", "category"]
      }
    }
  },
  "qinspect-designcode": {
    "tables": {
      "design_code_master": {
        "columns": ["id", "code", "design_name", "category_id"]
      }
    }
  }
}

RELATIONSHIPS:
[
  {
    "source_table": "catalog",
    "target_table": "design_code_master",
    "confidence": 0.85,
    "reasoning": "Both contain product information"
  }
]
```

### GPT Response (Example)
```json
{
  "rules": [
    {
      "rule_name": "Match_by_ID",
      "source_table": "catalog",
      "source_columns": ["id"],
      "target_table": "design_code_master",
      "target_columns": ["id"],
      "match_type": "exact",
      "confidence": 0.95,
      "reasoning": "Both have primary key 'id' with same data type"
    },
    {
      "rule_name": "Match_by_Code",
      "source_table": "catalog",
      "source_columns": ["code"],
      "target_table": "design_code_master",
      "target_columns": ["code"],
      "match_type": "exact",
      "confidence": 0.90,
      "reasoning": "Both have product code column"
    },
    {
      "rule_name": "Match_by_Name_Semantic",
      "source_table": "catalog",
      "source_columns": ["name"],
      "target_table": "design_code_master",
      "target_columns": ["design_name"],
      "match_type": "semantic",
      "confidence": 0.80,
      "reasoning": "Column names suggest product name matching"
    }
  ]
}
```

---

## 📋 Generated Rule Structure

Each rule contains:

```json
{
  "rule_id": "RULE_ABC123",
  "rule_name": "Match_by_ID",
  "source_schema": "ordermgmt",
  "source_table": "catalog",
  "source_columns": ["id"],
  "target_schema": "newamazon",
  "target_table": "design_code_master",
  "target_columns": ["id"],
  "match_type": "exact",           // exact, fuzzy, semantic, pattern
  "transformation": null,           // SQL/Python if needed
  "confidence_score": 0.95,         // 0.0 to 1.0
  "reasoning": "Both have primary key 'id'",
  "validation_status": "LIKELY",    // VALID, LIKELY, UNCERTAIN
  "llm_generated": true,            // true if from LLM, false if pattern-based
  "created_at": "2025-10-24T..."
}
```

---

## 🔄 Complete Workflow

```
User Request: Generate Rules
    ↓
Load Schemas (orderMgmt-catalog, qinspect-designcode)
    ↓
Query Knowledge Graph for relationships
    ↓
Generate Pattern-Based Rules
    ├─ Rule 1: Match on "id" (confidence: 0.75)
    ├─ Rule 2: Match on "code" (confidence: 0.75)
    └─ Rule 3: Match on "name" (confidence: 0.75)
    ↓
Generate LLM-Based Rules (if enabled)
    ├─ Call OpenAI GPT-3.5-turbo
    ├─ Send schemas + relationships
    ├─ GPT analyzes and suggests rules
    └─ Parse response
    ↓
Combine Rules
    ├─ Pattern-Based: 3 rules
    ├─ LLM-Based: 5 rules
    └─ Total: 8 rules
    ↓
Filter by Confidence (≥ 0.7)
    └─ All 8 rules pass
    ↓
Remove Duplicates
    └─ Final: 8 unique rules
    ↓
Create Ruleset
    ├─ Ruleset ID: RECON_07C55A55
    ├─ Total Rules: 8
    ├─ Pattern-Based: 3
    └─ LLM-Based: 5
    ↓
Save to MongoDB & File System
    ↓
Return to User
```

---

## ⚙️ Configuration

### Enable/Disable LLM
```python
# In .env file
OPENAI_API_KEY=sk-...              # Your OpenAI API key
OPENAI_MODEL=gpt-3.5-turbo         # Model to use
OPENAI_TEMPERATURE=0.7             # Creativity (0=deterministic, 1=creative)
OPENAI_MAX_TOKENS=2000             # Max response length
ENABLE_LLM_EXTRACTION=true         # Enable LLM features
```

### If LLM is Disabled
```
- Only pattern-based rules are generated
- Faster execution
- Lower cost (no API calls)
- Less intelligent matching
```

---

## 📊 Current Project Status

**In Your Project:**
- ✅ Pattern-based rules: **WORKING** (19 rules generated)
- ⚠️ LLM-based rules: **DISABLED** (OPENAI_API_KEY not set)

**To Enable LLM:**
1. Get OpenAI API key from https://platform.openai.com/api-keys
2. Add to `.env` file: `OPENAI_API_KEY=sk-...`
3. Restart the application
4. Re-run rule generation

---

## 🎯 Key Takeaways

| Aspect | Pattern-Based | LLM-Based |
|--------|---------------|-----------|
| **Speed** | Fast ⚡ | Slower (API call) 🌐 |
| **Cost** | Free | Costs money 💰 |
| **Intelligence** | Simple matching | Semantic understanding 🧠 |
| **Accuracy** | Good for exact matches | Better for fuzzy/semantic |
| **Confidence** | 0.75 (fixed) | Variable (0.7-0.95) |

---

**Version**: 1.0  
**Date**: 2025-10-24  
**Status**: ✅ Complete

