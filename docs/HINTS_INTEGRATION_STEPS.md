# Column Hints - Integration Steps

## Quick Start Guide

This guide shows you how to integrate the column hints system into your existing knowledge graph application.

---

## Step 1: Update Main Routes

Add the hints router to your main `routes.py`:

```python
# In kg_builder/routes.py

from kg_builder.routes_hints import router as hints_router

# Include the hints router
router.include_router(hints_router, prefix="/api/kg", tags=["hints"])
```

**OR** if using FastAPI app directly:

```python
# In your main.py or app.py

from kg_builder.routes_hints import router as hints_router

app.include_router(hints_router, prefix="/api/kg")
```

---

## Step 2: Initialize Hints Dictionary

Run the initialization script to create hints from your existing schema:

```bash
# Basic initialization (rule-based hints)
python scripts/initialize_hints_from_schema.py --schema schemas/newdqschemanov.json

# With LLM generation (requires OPENAI_API_KEY)
python scripts/initialize_hints_from_schema.py --schema schemas/newdqschemanov.json --use-llm

# Overwrite existing hints
python scripts/initialize_hints_from_schema.py --schema schemas/newdqschemanov.json --use-llm --overwrite
```

This will create:
- `schemas/hints/column_hints.json` - Main hints dictionary
- `schemas/hints/versions/column_hints_v1.0_initial.json` - Initial version
- `schemas/hints/versions/metadata.json` - Version history

---

## Step 3: Test the API

Start your FastAPI server and test the endpoints:

```bash
# Get all hints
curl http://localhost:8000/api/kg/hints/

# Get statistics
curl http://localhost:8000/api/kg/hints/statistics

# Get hints for a specific table
curl http://localhost:8000/api/kg/hints/table/hana_material_master

# Search hints
curl -X POST http://localhost:8000/api/kg/hints/search \
  -H "Content-Type: application/json" \
  -d '{"search_term": "material", "limit": 5}'
```

---

## Step 4: Integrate with Knowledge Graph

### Option A: Store Hints in Neo4j/FalkorDB

Update your KG generation to include hints:

```python
# In kg_builder/services/falkordb_backend.py or neo4j_backend.py

from kg_builder.services.hint_manager import get_hint_manager

def create_column_node(self, table_name: str, column_info: dict):
    """Create column node with hints."""
    # Get hints
    hint_manager = get_hint_manager()
    hints = hint_manager.get_column_hints(table_name, column_info['name'])

    if hints:
        query = """
        MERGE (t:Table {name: $table_name})
        MERGE (c:Column {name: $column_name, table_name: $table_name})
        SET c.data_type = $data_type,
            c.business_name = $business_name,
            c.aliases = $aliases,
            c.semantic_type = $semantic_type,
            c.searchable = $searchable
        MERGE (t)-[:HAS_COLUMN]->(c)
        """

        self.execute_query(query, {
            'table_name': table_name,
            'column_name': column_info['name'],
            'data_type': column_info.get('type'),
            'business_name': hints.get('business_name', column_info['name']),
            'aliases': hints.get('aliases', []),
            'semantic_type': hints.get('semantic_type', 'attribute'),
            'searchable': hints.get('searchable', True)
        })
```

### Option B: Use Hints Directly in NL-to-SQL

Create a new NL-to-SQL service that uses hints:

```python
# In kg_builder/services/nl_to_sql_service.py

from kg_builder.services.hint_manager import get_hint_manager
from kg_builder.services.llm_service import get_llm_service

class NLToSQLService:
    """Natural language to SQL query service using column hints."""

    def __init__(self):
        self.hint_manager = get_hint_manager()
        self.llm_service = get_llm_service()

    def process_query(self, nl_query: str, schema_name: str) -> str:
        """Convert natural language to SQL using hints."""
        # Extract key terms
        key_terms = self._extract_key_terms(nl_query)

        # Search hints for matching columns
        matched_columns = []
        for term in key_terms:
            results = self.hint_manager.search_hints(term)
            matched_columns.extend(results)

        # Build context for LLM
        context = self._build_sql_context(matched_columns)

        # Generate SQL using LLM with hints as context
        prompt = f"""Generate SQL query for: {nl_query}

Available columns with hints:
{context}

Generate only the SQL query."""

        response = self.llm_service.create_chat_completion(
            messages=[
                {"role": "system", "content": "You are a SQL expert."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content
```

---

## Step 5: Add Hints to KG Generation Request

Update your KG generation to optionally include hints:

```python
# In routes.py

@router.post("/kg/generate")
async def generate_kg(request: KGGenerationRequest):
    """Generate knowledge graph with optional hints."""
    # ... existing code ...

    # Option to include hints in KG
    if request.include_hints:
        hint_manager = get_hint_manager()

        for table in schema['tables']:
            table_hints = hint_manager.get_table_hints(table['name'])
            if table_hints:
                # Add hints to KG
                backend.add_table_with_hints(table['name'], table_hints)
```

---

## Step 6: Create User-Facing Endpoints

Add endpoints for end users to manage hints through your UI:

```python
# Example React/Vue.js integration

// Get all hints
const response = await fetch('/api/kg/hints/');
const hints = await response.json();

// Update column hint
const updateHint = async (table, column, field, value) => {
  await fetch(`/api/kg/hints/column/${table}/${column}/${field}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      field_value: value,
      user: currentUser.email
    })
  });
};

// Search hints
const searchHints = async (term) => {
  const response = await fetch('/api/kg/hints/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ search_term: term, limit: 10 })
  });
  return await response.json();
};
```

---

## Step 7: Setup Scheduled Hint Regeneration (Optional)

For periodic LLM-based hint updates:

```python
# In a scheduled task or cron job

from kg_builder.services.hint_manager import get_hint_manager
from kg_builder.services.llm_service import get_llm_service
import schedule
import time

def update_hints_with_llm():
    """Periodically update hints using LLM."""
    hint_manager = get_hint_manager()
    llm_service = get_llm_service()

    # Get all hints
    all_hints = hint_manager.load_hints()

    # Update hints that haven't been manually verified
    for table_name, table_data in all_hints['tables'].items():
        for column_name, column_hints in table_data['columns'].items():
            if not column_hints.get('manual_verified', False):
                # Regenerate with LLM
                result = llm_service.extract_column_hints(
                    table_name=table_name,
                    column_name=column_name,
                    column_type=column_hints['data_type']
                )

                # Update hints
                updated_hints = result.get('hints', {})
                updated_hints['auto_generated'] = True
                updated_hints['data_type'] = column_hints['data_type']

                hint_manager.add_column_hints(
                    table_name=table_name,
                    column_name=column_name,
                    column_hints=updated_hints,
                    user='scheduled_task'
                )

# Schedule weekly updates
schedule.every().monday.at("02:00").do(update_hints_with_llm)
```

---

## Step 8: Add Hints to Existing Reconciliation Rules

Enhance reconciliation rules with hints context:

```python
# In reconciliation_service.py

from kg_builder.services.hint_manager import get_hint_manager

def generate_reconciliation_rules_with_hints(self, ...):
    """Generate rules using column hints for better matching."""
    hint_manager = get_hint_manager()

    # Get hints for source and target tables
    source_hints = hint_manager.get_table_hints(source_table)
    target_hints = hint_manager.get_table_hints(target_table)

    # Use hints to find semantic matches
    for source_col in source_columns:
        source_col_hints = hint_manager.get_column_hints(source_table, source_col)

        for target_col in target_columns:
            target_col_hints = hint_manager.get_column_hints(target_table, target_col)

            # Check if aliases match
            if self._aliases_match(source_col_hints, target_col_hints):
                # Generate rule based on hint metadata
                rule = self._create_rule_from_hints(
                    source_table, source_col, source_col_hints,
                    target_table, target_col, target_col_hints
                )
                rules.append(rule)
```

---

## Verification Checklist

- [ ] Hints router added to main app
- [ ] Initial hints dictionary created
- [ ] API endpoints accessible
- [ ] Hints integrated with KG generation
- [ ] NL-to-SQL using hints (if applicable)
- [ ] UI for hint management (optional)
- [ ] Version snapshots working
- [ ] Export/import tested
- [ ] Search functionality working
- [ ] LLM generation tested

---

## Common Issues & Solutions

### Issue: Hints file not found
**Solution**: Run the initialization script first

### Issue: LLM generation fails
**Solution**: Check that `OPENAI_API_KEY` is set in environment

### Issue: Can't update hints
**Solution**: Verify write permissions on `schemas/hints/` directory

### Issue: Search returns no results
**Solution**: Check that `searchable: true` and hints are populated

---

## Next Steps

1. **Customize Hints**: Review and update auto-generated hints with domain knowledge
2. **Add Examples**: Include real sample values from your data
3. **Document Rules**: Add business rules to column hints
4. **Create Versions**: Take snapshots before major changes
5. **Train Users**: Show end users how to search and update hints
6. **Monitor Usage**: Track which hints are used most in queries

---

## Support

For detailed API documentation, see:
- `docs/COLUMN_HINTS_GUIDE.md` - Full user guide
- `examples/hints_usage_examples.py` - Code examples
- `kg_builder/services/hint_manager.py` - Service implementation
