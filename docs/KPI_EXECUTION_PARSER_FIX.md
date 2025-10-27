# KPI Execution Parser Fix ✅

## Problem

When executing a KPI, the following error occurred:

```
TypeError: get_nl_query_parser() got an unexpected keyword argument 'kg_name'
```

The `landing_kpi_executor.py` was calling `get_nl_query_parser()` with incorrect parameters:

```python
# ❌ WRONG - kg_name and db_type are not valid parameters
parser = get_nl_query_parser(
    kg_name=kg_name,
    db_type=db_type
)
```

## Root Cause

The `get_nl_query_parser()` function signature expects:
- `kg`: KnowledgeGraph object (not kg_name string)
- `schemas_info`: Optional schema information dictionary
- `excluded_fields`: Optional list of fields to exclude

```python
def get_nl_query_parser(
    kg: Optional[KnowledgeGraph] = None,
    schemas_info: Optional[Dict] = None,
    excluded_fields: Optional[List[str]] = None
) -> NLQueryParser:
    """Get or create NL query parser instance."""
    return NLQueryParser(kg, schemas_info, excluded_fields)
```

## Solution

Updated `landing_kpi_executor.py` to:

1. **Load KnowledgeGraph from storage** using Graphiti backend
2. **Convert entities and relationships** to KnowledgeGraph object
3. **Load table aliases** from metadata
4. **Pass KG object** to parser (not kg_name string)

### Updated Code

```python
# Step 1: Load Knowledge Graph from storage
from kg_builder.services.graphiti_backend import get_graphiti_backend
from kg_builder.models import KnowledgeGraph, GraphNode, GraphRelationship

graphiti = get_graphiti_backend()
entities_data = graphiti.get_entities(kg_name)
relationships_data = graphiti.get_relationships(kg_name)

# Convert to KnowledgeGraph object
nodes = [GraphNode(**entity) for entity in entities_data] if entities_data else []
relationships = [GraphRelationship(**rel) for rel in relationships_data] if relationships_data else []

# Load metadata including table_aliases
table_aliases = {}
try:
    kg_metadata = graphiti.get_kg_metadata(kg_name)
    if kg_metadata:
        table_aliases = kg_metadata.get('table_aliases', {})
except Exception as e:
    logger.warning(f"Could not load KG metadata: {e}")

kg = KnowledgeGraph(
    name=kg_name,
    nodes=nodes,
    relationships=relationships,
    schema_file=schema,
    table_aliases=table_aliases
)

# Step 3: Parse the query with KG object
parser = get_nl_query_parser(kg=kg)  # ✅ CORRECT - pass KG object
intent = parser.parse(
    nl_definition,
    use_llm=use_llm
)
```

## Execution Flow

```
KPI Execution Request
    ↓
Extract parameters (kg_name, schemas, definitions, etc.)
    ↓
Load KG from Graphiti backend
    ↓
Convert entities/relationships to KnowledgeGraph object
    ↓
Load table aliases from metadata
    ↓
Classify query
    ↓
Parse query with KG object ✅
    ↓
Get database connection
    ↓
Execute query
    ↓
Return results
```

## Files Modified

- **kg_builder/services/landing_kpi_executor.py**
  - Updated `_execute_kpi_internal()` method
  - Added KG loading from Graphiti backend
  - Fixed parser initialization with KG object

## Status

✅ **COMPLETE** - KPI execution now correctly loads and uses KnowledgeGraph objects!

## Testing

The fix enables proper KPI execution with:
- ✅ KG loading from storage
- ✅ Entity and relationship conversion
- ✅ Table alias loading
- ✅ Correct parser initialization
- ✅ Query classification and parsing
- ✅ Database execution

