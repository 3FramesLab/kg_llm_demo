# LLM-Learned Table Aliases - Quick Start Guide

## 🚀 How to Use

### 1. Generate KG with Learned Aliases

```python
from kg_builder.services.schema_parser import SchemaParser

# Generate KG with LLM alias extraction
kg = SchemaParser.build_merged_knowledge_graph(
    schema_names=["newdqschema"],
    kg_name="KG_102",
    use_llm=True  # ← Enables alias extraction
)

# Check learned aliases
print(f"Learned aliases: {kg.table_aliases}")
# Output: {
#   "brz_lnd_RBP_GPU": ["RBP", "RBP GPU"],
#   "brz_lnd_OPS_EXCEL_GPU": ["OPS", "OPS Excel"],
#   ...
# }
```

### 2. Use in Natural Language Queries

```python
from kg_builder.services.nl_query_parser import NLQueryParser

# Parser automatically uses learned aliases
parser = NLQueryParser(kg=kg, schemas_info=schemas)

# Query with business terms
intent = parser.parse("Show me products in RBP not in OPS Excel")

print(f"Source table: {intent.source_table}")
# Output: brz_lnd_RBP_GPU (resolved from "RBP")

print(f"Target table: {intent.target_table}")
# Output: brz_lnd_OPS_EXCEL_GPU (resolved from "OPS Excel")
```

### 3. Aliases Persist Across Sessions

```python
# First session: Generate KG
kg = SchemaParser.build_merged_knowledge_graph(
    schema_names=["newdqschema"],
    kg_name="KG_102",
    use_llm=True
)
# Aliases are stored in metadata.json

# Second session: Load KG
# Aliases are automatically restored from storage
parser = NLQueryParser(kg=kg, schemas_info=schemas)
# Parser has access to learned aliases!
```

---

## 📊 How It Works

### Alias Extraction Process

```
1. For each table in schema:
   ├─ Get table name (e.g., "brz_lnd_RBP_GPU")
   ├─ Get table description
   ├─ Get column names
   └─ Send to LLM

2. LLM analyzes and suggests:
   ├─ Business-friendly names
   ├─ Common abbreviations
   └─ Reasoning

3. Store in KG:
   └─ table_aliases: {
        "brz_lnd_RBP_GPU": ["RBP", "RBP GPU", "GPU"],
        ...
      }
```

### Query Resolution Process

```
Query: "Show me products in RBP"

1. Parse query → Extract "RBP"
2. Resolve "RBP":
   ├─ Check learned aliases first ✓ Found!
   ├─ "RBP" → "brz_lnd_RBP_GPU"
   └─ Use resolved table name
3. Execute query with correct table
```

---

## 🎯 Key Features

✅ **Automatic Learning**: No manual configuration needed
✅ **Persistent**: Aliases saved with KG
✅ **Scalable**: Works with any number of tables
✅ **Accurate**: LLM-informed, not guesswork
✅ **Flexible**: Learned aliases override hardcoded ones
✅ **Backward Compatible**: Works with existing code

---

## 🔍 Monitoring Learned Aliases

### View Aliases for a KG

```python
from kg_builder.services.graphiti_backend import get_graphiti_backend

graphiti = get_graphiti_backend()
metadata = graphiti.get_kg_metadata("KG_102")

print("Table Aliases:")
for table, aliases in metadata.get("table_aliases", {}).items():
    print(f"  {table}: {aliases}")
```

### Example Output

```
Table Aliases:
  brz_lnd_RBP_GPU: ['RBP', 'RBP GPU', 'GPU']
  brz_lnd_OPS_EXCEL_GPU: ['OPS', 'OPS Excel', 'Excel GPU']
  brz_lnd_SKU_LIFNR_Excel: ['SKU', 'SKU LIFNR', 'Excel']
  hana_material_master: ['Material', 'Material Master', 'HANA']
```

---

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/test_learned_table_aliases.py -v
```

Expected output:
```
12 passed in 1.48s ✓
```

---

## 🐛 Troubleshooting

### Aliases Not Being Extracted

**Check**:
1. Is LLM enabled? `use_llm=True` in KG generation
2. Is OPENAI_API_KEY set in `.env`?
3. Check logs for LLM errors

**Solution**:
```python
# Verify LLM is enabled
from kg_builder.services.llm_service import get_llm_service
llm = get_llm_service()
print(f"LLM enabled: {llm.is_enabled()}")
```

### Aliases Not Being Used

**Check**:
1. Is KG passed to NLQueryParser?
2. Are aliases in KG.table_aliases?

**Solution**:
```python
# Verify aliases are in KG
print(f"KG aliases: {kg.table_aliases}")

# Verify parser has aliases
parser = NLQueryParser(kg=kg, schemas_info=schemas)
print(f"Parser aliases: {parser.table_mapper.learned_aliases}")
```

### Aliases Not Persisting

**Check**:
1. Is metadata.json being saved?
2. Is table_aliases in metadata?

**Solution**:
```bash
# Check metadata file
cat kg_storage/KG_102/metadata.json | grep table_aliases
```

---

## 📈 Performance

- **Extraction Time**: ~1-2 seconds per table (LLM call)
- **Resolution Time**: <1ms per query (dictionary lookup)
- **Storage**: ~100 bytes per alias

---

## 🎓 Example: Complete Workflow

```python
# 1. Generate KG with aliases
kg = SchemaParser.build_merged_knowledge_graph(
    schema_names=["newdqschema"],
    kg_name="KG_102",
    use_llm=True
)
print(f"✓ Generated KG with {len(kg.table_aliases)} tables")

# 2. Create parser
parser = NLQueryParser(kg=kg, schemas_info=schemas)
print(f"✓ Parser initialized with learned aliases")

# 3. Parse query
intent = parser.parse("Show me products in RBP not in OPS Excel")
print(f"✓ Parsed query:")
print(f"  - Source: {intent.source_table}")
print(f"  - Target: {intent.target_table}")

# 4. Generate SQL
from kg_builder.services.nl_sql_generator import NLSQLGenerator
generator = NLSQLGenerator(kg=kg, schemas_info=schemas)
sql = generator.generate(intent)
print(f"✓ Generated SQL:\n{sql}")

# 5. Execute query
from kg_builder.services.nl_query_executor import NLQueryExecutor
executor = NLQueryExecutor(db_connection=db_conn)
results = executor.execute(sql)
print(f"✓ Query executed: {len(results)} rows returned")
```

---

## 📚 Related Documentation

- [LLM-Learned Table Aliases Feature](LLM_LEARNED_TABLE_ALIASES_FEATURE.md)
- [Table Name Mapping Solution](TABLE_NAME_MAPPING_SOLUTION.md)
- [Natural Language Query Processing](NL_QUERY_PROCESSING.md)

---

**Status**: 🎉 **READY TO USE!**

Start using learned aliases in your KG generation today! 🚀

