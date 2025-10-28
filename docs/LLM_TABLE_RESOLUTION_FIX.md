# LLM Table Resolution Issue - Root Cause & Fix

## Problem

When executing KPI with NL definition:
```
"Show me all the products in RBP GPU which are inactive OPS Excel"
```

The LLM returns:
```json
{
    "source_table": null,
    "target_table": null,
    "operation": "IN",
    "filters": [{"column": "Active_Inactive", "value": "Inactive"}],
    "confidence": 0.85,
    "reasoning": "...no schema information is available to confirm..."
}
```

**Why?** The LLM says: "no schema information is available to confirm"

## Root Cause

The NL Query Parser is initialized WITHOUT `schemas_info`:

```python
# landing_kpi_executor.py line 157
parser = get_nl_query_parser(kg=kg)  # ❌ Missing schemas_info!
```

### What Happens

1. Parser is created with only `kg` parameter
2. `schemas_info` defaults to empty dict: `self.schemas_info = schemas_info or {}`
3. When building LLM prompt, it checks `if self.schemas_info:` (line 468)
4. Since `schemas_info` is empty, the prompt gets:
   ```
   schemas_str = "No schemas provided"
   table_names_str = "No tables available"
   ```
5. LLM receives prompt with NO table names to work with
6. LLM can't map "RBP GPU" to actual table names
7. LLM returns `null` for source_table and target_table

### The LLM Prompt Without schemas_info

```
IMPORTANT RULES:
1. ONLY extract table names from this list: No tables available
2. NEVER treat common English words as table names...
3. Look for business terms that might map to table names...
```

**Problem**: Rule 1 says "No tables available" but Rule 3 says "Look for business terms"
This is contradictory! LLM can't resolve table names.

## Solution

Extract table information from the Knowledge Graph and pass it as `schemas_info` to the parser.

### Step 1: Extract Table Information from KG

The KG has:
- `kg.nodes` - Contains table nodes with column information
- `kg.table_aliases` - Maps actual table names to business names

### Step 2: Build schemas_info Dictionary

```python
# Extract table names and columns from KG nodes
schemas_info = {}
table_info = {}

for node in kg.nodes:
    if node.properties.get("type") == "Table":
        table_name = node.label
        columns = node.properties.get("columns", [])
        column_names = [col.get("name") for col in columns if isinstance(col, dict)]
        table_info[table_name] = {"columns": column_names}

# Create schemas_info structure
schemas_info["schema"] = type('Schema', (), {
    'tables': type('Tables', (), table_info)()
})()
```

### Step 3: Pass to Parser

```python
parser = get_nl_query_parser(kg=kg, schemas_info=schemas_info)
```

### Step 4: LLM Receives Complete Information

Now the LLM prompt includes:

```
IMPORTANT RULES:
1. ONLY extract table names from this list: brz_lnd_RBP_GPU, brz_lnd_OPS_EXCEL_GPU, ...
2. NEVER treat common English words as table names...
3. Look for business terms that might map to table names (e.g., "RBP" → "brz_lnd_RBP_GPU")
```

**Result**: LLM can now resolve:
- "RBP GPU" → "brz_lnd_RBP_GPU" ✅
- "OPS Excel" → "brz_lnd_OPS_EXCEL_GPU" ✅

## Implementation

### Updated landing_kpi_executor.py

```python
# Step 1: Load Knowledge Graph
kg = KnowledgeGraph(...)

# Step 2: Extract schemas_info from KG
schemas_info = _extract_schemas_info_from_kg(kg)

# Step 3: Parse with both KG and schemas_info
parser = get_nl_query_parser(kg=kg, schemas_info=schemas_info)

intent = parser.parse(nl_definition, use_llm=use_llm)
```

### Helper Function

```python
def _extract_schemas_info_from_kg(kg: KnowledgeGraph) -> Dict[str, Any]:
    """
    Extract table and column information from KG nodes.
    
    Args:
        kg: Knowledge Graph with nodes containing table metadata
        
    Returns:
        Dictionary in schemas_info format for NL Query Parser
    """
    table_info = {}
    
    # Extract table nodes from KG
    for node in kg.nodes:
        if node.properties.get("type") == "Table":
            table_name = node.label
            columns = node.properties.get("columns", [])
            
            # Extract column names
            column_names = []
            for col in columns:
                if isinstance(col, dict):
                    column_names.append(col.get("name"))
                elif hasattr(col, 'name'):
                    column_names.append(col.name)
            
            table_info[table_name] = {"columns": column_names}
    
    # Create schemas_info structure
    class Schema:
        def __init__(self, tables_dict):
            self.tables = type('Tables', (), {
                name: type('Table', (), {'columns': [type('Col', (), {'name': c})() for c in cols['columns']]})()
                for name, cols in tables_dict.items()
            })()
    
    schemas_info = {"schema": Schema(table_info)}
    return schemas_info
```

## Expected Results After Fix

### Before Fix
```json
{
    "source_table": null,
    "target_table": null,
    "operation": "IN",
    "filters": [{"column": "Active_Inactive", "value": "Inactive"}],
    "confidence": 0.85,
    "reasoning": "no schema information is available"
}
```

### After Fix
```json
{
    "source_table": "brz_lnd_RBP_GPU",
    "target_table": "brz_lnd_OPS_EXCEL_GPU",
    "operation": "NOT_IN",
    "filters": [{"column": "Active_Inactive", "value": "Inactive"}],
    "confidence": 0.85,
    "reasoning": "RBP GPU maps to brz_lnd_RBP_GPU, OPS Excel maps to brz_lnd_OPS_EXCEL_GPU"
}
```

## Why This Works

1. ✅ LLM receives actual table names from KG
2. ✅ LLM receives column information for each table
3. ✅ LLM can use table_aliases to map business terms
4. ✅ LLM can extract correct filters with actual column names
5. ✅ Parser can resolve table names using table_mapper

## Files to Update

- `kg_builder/services/landing_kpi_executor.py`
  - Add `_extract_schemas_info_from_kg()` helper function
  - Update `_execute_kpi_internal()` to extract and pass schemas_info

## Status

🔴 **ISSUE IDENTIFIED** - Parser not receiving schemas_info
🟡 **FIX READY** - Implementation plan documented
⏳ **PENDING** - Code changes to be applied

## Next Steps

1. Implement `_extract_schemas_info_from_kg()` function
2. Update parser initialization to pass schemas_info
3. Test with KPI execution
4. Verify LLM returns correct table names

