# 🔍 Table Aliases Extraction - Status Report

## ✅ What Was Fixed

### 1. **Bug Found & Fixed**: Single Schema KGs Not Extracting Aliases
**Problem**: When generating a KG with a single schema, the system was using `build_knowledge_graph()` instead of `build_merged_knowledge_graph()`, which didn't extract table aliases.

**Solution**: Added table aliases extraction to `build_knowledge_graph()` method in `kg_builder/services/schema_parser.py`

**Files Modified**:
- `kg_builder/services/schema_parser.py` (lines 248-279)

**Changes**:
```python
# Extract table aliases using LLM if enabled
table_aliases = {}
if use_llm:
    logger.info(f"🔍 Attempting to extract table aliases (use_llm={use_llm})")
    schemas_dict = {schema_name: schema}
    table_aliases = SchemaParser._extract_table_aliases(schemas_dict)
    logger.info(f"✅ Table aliases extraction complete: {len(table_aliases)} tables with aliases")

# Pass to KnowledgeGraph
kg = KnowledgeGraph(
    name=kg_name,
    nodes=nodes,
    relationships=relationships,
    schema_file=schema_name,
    metadata=metadata,
    table_aliases=table_aliases  # ← NOW INCLUDED
)
```

---

## ⚠️ Current Issue: Invalid OpenAI API Key

### The Problem
The OpenAI API key in `.env` is returning **401 Unauthorized** errors:

```
Error code: 401 - {'error': {'message': 'Incorrect API key provided: sk-proj-***...***2WoA'}}
```

### Why This Matters
Without a valid API key, the LLM cannot:
- Extract table aliases
- Enhance relationships
- Analyze schemas

### Evidence from Logs
```
2025-10-27 20:21:39,302 - kg_builder.services.schema_parser - INFO - 🚀 Extracting table aliases using LLM...
2025-10-27 20:21:39,965 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 401 Unauthorized"
2025-10-27 20:21:39,966 - kg_builder.services.llm_service - ERROR - OpenAI API error during alias extraction: Error code: 401
```

---

## 🔧 What Needs to Be Done

### Step 1: Verify/Update OpenAI API Key
The API key in `.env` needs to be:
1. **Valid** - Active and not expired
2. **Correct** - Properly formatted
3. **Authorized** - Has access to GPT-4o model

**Current Key** (from `.env`):
```
OPENAI_API_KEY=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
```

**Action Required**:
- [ ] Go to https://platform.openai.com/account/api-keys
- [ ] Check if the key is valid and active
- [ ] If expired/invalid, generate a new key
- [ ] Update `.env` with the new key
- [ ] Restart the server

### Step 2: Test After Key Update
Once the API key is updated:

```bash
# Restart server
python -m uvicorn kg_builder.main:app --reload

# Test KG generation
curl -X POST http://localhost:8000/v1/kg/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_names": ["newdqschema"],
    "kg_name": "KG_TEST_ALIASES",
    "use_llm": true
  }'

# Check metadata for aliases
curl http://localhost:8000/v1/kg/KG_TEST_ALIASES/metadata
```

---

## 📊 Expected Behavior (After Fix)

### Server Logs Should Show:
```
✅ 🔍 Attempting to extract table aliases (use_llm=True)
✅ 🔍 LLM Service enabled: True
✅ 🚀 Extracting table aliases using LLM...
✅ Extracting aliases for table: hana_material_master
✅ ✓ Extracted aliases for hana_material_master: ['Material', 'Material Master', 'HANA']
✅ Extracting aliases for table: brz_lnd_RBP_GPU
✅ ✓ Extracted aliases for brz_lnd_RBP_GPU: ['RBP', 'RBP GPU', 'GPU']
✅ Extracted aliases for 4 tables
✅ ✅ Table aliases extraction complete: 4 tables with aliases
```

### API Response Should Include:
```json
{
  "success": true,
  "kg_name": "KG_TEST_ALIASES",
  "table_aliases": {
    "hana_material_master": ["Material", "Material Master", "HANA"],
    "brz_lnd_RBP_GPU": ["RBP", "RBP GPU", "GPU"],
    "brz_lnd_OPS_EXCEL_GPU": ["OPS", "OPS Excel"],
    "brz_lnd_SKU_LIFNR_Excel": ["SKU", "SKU LIFNR"]
  }
}
```

### Web UI Should Display:
```
📊 Table Aliases
─────────────────
LLM-Learned Business Names

hana_material_master
  [Material] [Material Master] [HANA]

brz_lnd_RBP_GPU
  [RBP] [RBP GPU] [GPU]

brz_lnd_OPS_EXCEL_GPU
  [OPS] [OPS Excel]

brz_lnd_SKU_LIFNR_Excel
  [SKU] [SKU LIFNR]
```

---

## 🎯 Summary

| Item | Status |
|------|--------|
| **Code Implementation** | ✅ COMPLETE |
| **Single Schema Support** | ✅ FIXED |
| **Web UI Display** | ✅ COMPLETE |
| **API Endpoints** | ✅ COMPLETE |
| **OpenAI API Key** | ❌ INVALID - NEEDS UPDATE |
| **Feature Ready** | ⏳ PENDING API KEY FIX |

---

## 🚀 Next Steps

1. **Update OpenAI API Key** in `.env`
2. **Restart Server**
3. **Test KG Generation** with `use_llm=true`
4. **Verify Aliases** in metadata and web UI
5. **Use Aliases** in natural language queries

---

**Last Updated**: 2025-10-27
**Status**: Awaiting API Key Update

