# Unified Knowledge Graph Generation Approach

## 🎯 Overview

The Knowledge Graph Builder now uses a **unified approach** for generating knowledge graphs, regardless of whether you have a single schema or multiple schemas.

## ✅ What Changed

### Before (Dual Approach - DEPRECATED)
```python
# Different methods for different schema counts
if len(schema_names) == 1:
    kg = SchemaParser.build_knowledge_graph(...)  # Limited capabilities
else:
    kg = SchemaParser.build_merged_knowledge_graph(...)  # Full capabilities
```

### After (Unified Approach - CURRENT)
```python
# Always use the same method regardless of schema count
kg = SchemaParser.build_merged_knowledge_graph(
    schema_names=schema_names,  # Can be 1 or more schemas
    kg_name=kg_name,
    use_llm=use_llm,
    field_preferences=field_preferences
)
```

## 🚀 Benefits

### 1. **Consistent Capabilities**
- **All relationship types** available for single schemas
- **Full LLM enhancement** for single schemas
- **Same default settings** (use_llm=True) for all schemas

### 2. **Simplified API**
- **No surprises** based on schema count
- **Predictable behavior** across all use cases
- **Easier to understand** and maintain

### 3. **Better Defaults**
- **LLM enhancement enabled** by default
- **All semantic relationship types** available
- **Consistent confidence scoring**

## 📋 Migration Guide

### API Endpoints
**No changes needed** - the `/kg/generate` endpoint automatically uses the unified approach.

### Direct Method Calls
If you're calling the methods directly in your code:

```python
# OLD (still works but shows deprecation warning)
kg = SchemaParser.build_knowledge_graph(
    schema_name="my_schema",
    kg_name="my_kg",
    schema=schema_obj,
    use_llm=True
)

# NEW (recommended)
kg = SchemaParser.build_merged_knowledge_graph(
    schema_names=["my_schema"],  # Note: list format
    kg_name="my_kg",
    use_llm=True
    # No need to pass schema object - it's loaded automatically
)
```

## 🔧 Technical Details

### Relationship Types Available
**Single Schema (Before):** 7 primary relationship types only
**Single Schema (Now):** 7 primary + 5 semantic relationship types (12 total)

- ✅ **REFERENCES** - Foreign key relationships
- ✅ **HAS** - Ownership/containment
- ✅ **BELONGS_TO** - Many-to-one relationships
- ✅ **CONTAINS** - Composition relationships
- ✅ **ASSOCIATES_WITH** - Many-to-many relationships
- ✅ **INHERITS_FROM** - Hierarchical relationships
- ✅ **TRACKS** - Audit/history relationships
- ✅ **SEMANTIC_REFERENCE** - Different names, same meaning
- ✅ **BUSINESS_LOGIC** - Business rule relationships
- ✅ **HIERARCHICAL** - Parent-child relationships
- ✅ **TEMPORAL** - Time-based relationships
- ✅ **LOOKUP** - Master data relationships

### LLM Enhancement
**Single Schema (Before):** Basic LLM enhancement only
**Single Schema (Now):** Full multi-schema LLM service with advanced prompts

## 🧪 Testing

The unified approach has been tested with:
- ✅ Single schema processing
- ✅ Multiple schema processing
- ✅ All relationship types
- ✅ LLM enhancement
- ✅ Table alias extraction
- ✅ Field preferences
- ✅ Backward compatibility

## 📚 Examples

### Single Schema
```python
# Generate KG from single schema
kg = SchemaParser.build_merged_knowledge_graph(
    schema_names=["newdqschemanov"],
    kg_name="single_schema_kg",
    use_llm=True
)
```

### Multiple Schemas
```python
# Generate KG from multiple schemas
kg = SchemaParser.build_merged_knowledge_graph(
    schema_names=["schema1", "schema2", "schema3"],
    kg_name="multi_schema_kg",
    use_llm=True
)
```

### API Usage
```bash
# Single schema via API
curl -X POST http://localhost:8000/api/v1/kg/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_names": ["newdqschemanov"],
    "kg_name": "my_kg",
    "use_llm_enhancement": true
  }'

# Multiple schemas via API
curl -X POST http://localhost:8000/api/v1/kg/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_names": ["schema1", "schema2"],
    "kg_name": "my_kg",
    "use_llm_enhancement": true
  }'
```

## 🎉 Result

**Single schema is now just a special case of multiple schemas (where count = 1).**

This provides consistent, full-featured knowledge graph generation regardless of how many schemas you're working with!
