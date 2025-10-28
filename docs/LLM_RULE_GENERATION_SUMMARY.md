# LLM Rule Generation - Quick Summary

## 🎯 What is LLM Rule Generation?

The system automatically creates **reconciliation rules** that tell the system how to match records between two different databases.

**Example:**
- Database 1 has: `catalog` table with columns `id`, `code`, `name`
- Database 2 has: `design_code_master` table with columns `id`, `code`, `design_name`
- **Rule**: Match records where `catalog.id = design_code_master.id`

---

## 🔄 Two Types of Rule Generation

### 1️⃣ Pattern-Based Rules (Simple)
```
Logic: Look for matching column names
Example: If both tables have "id" → Create rule to match on "id"
Speed: ⚡ Fast
Cost: 💰 Free
Confidence: 0.75 (fixed)
Status: ✅ Always used
```

### 2️⃣ LLM-Based Rules (Smart)
```
Logic: Use GPT to understand semantic meaning
Example: GPT sees "name" and "design_name" are similar → Create rule
Speed: 🌐 Slower (API call to OpenAI)
Cost: 💰 Costs money per API call
Confidence: 0.70-0.95 (variable)
Status: ⚠️ Only if OPENAI_API_KEY is set
```

---

## 📊 How It Works (7 Steps)

```
Step 1: Load Schemas
   ↓ Load table and column information from JSON files
   
Step 2: Query Knowledge Graph
   ↓ Get relationships between entities
   
Step 3: Generate Pattern-Based Rules
   ↓ Match columns by name (id=id, code=code, etc.)
   
Step 4: Generate LLM-Based Rules (if enabled)
   ↓ Send schemas to GPT
   ↓ GPT analyzes and suggests smart rules
   ↓ Parse GPT response
   
Step 5: Combine Rules
   ↓ Merge pattern-based + LLM rules
   
Step 6: Filter & Deduplicate
   ↓ Keep only high-confidence rules
   ↓ Remove duplicates
   
Step 7: Create Ruleset
   ↓ Save to MongoDB and file system
   ↓ Return to user
```

---

## 🤖 What GPT Does

### Input to GPT
```
System Message:
"You are an expert data integration specialist. 
Generate reconciliation rules for matching data 
across different database schemas."

User Message:
"Here are two schemas and their relationships. 
Generate rules that match records between them."

Attached:
- Schema 1: Tables, columns, data types
- Schema 2: Tables, columns, data types
- Relationships: How entities relate
```

### Output from GPT
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
      "reasoning": "Both have primary key 'id'"
    },
    {
      "rule_name": "Match_by_Name_Semantic",
      "source_table": "catalog",
      "source_columns": ["name"],
      "target_table": "design_code_master",
      "target_columns": ["design_name"],
      "match_type": "semantic",
      "confidence": 0.80,
      "reasoning": "Column names suggest product name"
    }
  ]
}
```

---

## 📋 Generated Rule Example

```json
{
  "rule_id": "RULE_ABC123",
  "rule_name": "Match_catalog_by_ID",
  "source_schema": "ordermgmt",
  "source_table": "catalog",
  "source_columns": ["id"],
  "target_schema": "newamazon",
  "target_table": "design_code_master",
  "target_columns": ["id"],
  "match_type": "exact",
  "confidence_score": 0.95,
  "reasoning": "Both have primary key 'id' with same data type",
  "validation_status": "VALID",
  "llm_generated": true,
  "created_at": "2025-10-24T12:00:00"
}
```

---

## 🔧 Configuration

### Enable LLM Rules

**Step 1: Get OpenAI API Key**
- Go to: https://platform.openai.com/api-keys
- Create new secret key
- Copy the key

**Step 2: Add to .env**
```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000
ENABLE_LLM_EXTRACTION=true
```

**Step 3: Restart Application**
```bash
docker-compose restart
# or
python -m uvicorn main:app --reload
```

**Step 4: Generate Rules**
```python
ruleset = recon_service.generate_from_knowledge_graph(
    kg_name="kg_20251024_005324",
    schema_names=["orderMgmt-catalog", "qinspect-designcode"],
    use_llm=True  # Now enabled!
)
```

---

## 📊 Current Project Status

**Pattern-Based Rules**: ✅ **WORKING**
- 19 rules generated in your test
- No API calls needed
- Confidence: 0.75

**LLM-Based Rules**: ⚠️ **DISABLED**
- OPENAI_API_KEY not set
- Would generate additional semantic rules
- Higher confidence scores (0.80-0.95)

---

## 🎯 Match Types

| Type | Description | Example |
|------|-------------|---------|
| **exact** | Exact column match | `id = id` |
| **fuzzy** | Similar values | `name ≈ design_name` |
| **semantic** | Meaning-based match | `product_name` matches `item_description` |
| **pattern** | Pattern-based match | `code` matches `product_code` |

---

## 💡 Key Concepts

### Confidence Score
- **0.0-1.0** scale
- **0.95**: Very confident (exact match)
- **0.75**: Moderately confident (pattern match)
- **0.50**: Low confidence (fuzzy match)

### Validation Status
- **VALID**: High confidence, ready to use
- **LIKELY**: Good confidence, probably works
- **UNCERTAIN**: Low confidence, needs review

### LLM Generated Flag
- **true**: Rule created by GPT
- **false**: Rule created by pattern matching

---

## 🚀 Next Steps

1. **Enable LLM** (Optional)
   - Get OpenAI API key
   - Add to .env
   - Restart app

2. **Generate Rules**
   - Call rule generation API
   - System creates pattern-based rules
   - If LLM enabled, also creates semantic rules

3. **Execute Rules**
   - Use rules to match records
   - Execute SQL queries
   - Calculate KPIs

4. **Monitor Results**
   - Check MongoDB for results
   - Review matched/unmatched records
   - Adjust rules if needed

---

## 📚 Related Files

- `LLM_RULE_GENERATION_EXPLAINED.md` - Detailed explanation
- `LLM_RULE_GENERATION_CODE_EXAMPLES.md` - Code examples
- `kg_builder/services/reconciliation_service.py` - Main service
- `kg_builder/services/multi_schema_llm_service.py` - LLM service
- `kg_builder/config.py` - Configuration

---

## ❓ FAQ

**Q: Do I need LLM to generate rules?**
A: No, pattern-based rules work fine. LLM just makes them smarter.

**Q: How much does LLM cost?**
A: ~$0.001-0.01 per rule generation (depends on schema size).

**Q: Can I use GPT-4 instead of GPT-3.5?**
A: Yes, change `OPENAI_MODEL=gpt-4` in .env (costs more).

**Q: What if LLM fails?**
A: System falls back to pattern-based rules automatically.

**Q: How many rules are generated?**
A: Depends on schema complexity. Usually 10-50 rules per execution.

---

**Version**: 1.0  
**Date**: 2025-10-24  
**Status**: ✅ Complete

