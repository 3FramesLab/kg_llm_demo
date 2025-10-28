# NL Query Executor vs Landing KPI Executor - Analysis & Findings

## Overview

Both `nl_query_executor.py` and `landing_kpi_executor.py` are designed to execute natural language queries, but they have different responsibilities and integration points.

## Key Differences

### 1. **NL Query Executor** (`nl_query_executor.py`)
- **Purpose**: Executes pre-parsed QueryIntent objects
- **Input**: QueryIntent (already parsed)
- **Responsibility**: SQL generation and execution only
- **LLM Usage**: ❌ NOT involved - parsing already done
- **Flow**:
  ```
  QueryIntent → SQL Generation → SQL Execution → Results
  ```

### 2. **Landing KPI Executor** (`landing_kpi_executor.py`)
- **Purpose**: End-to-end KPI execution from NL definition
- **Input**: NL definition string + execution parameters
- **Responsibility**: Classification → Parsing → Execution
- **LLM Usage**: ✅ SHOULD be involved in parsing step
- **Flow**:
  ```
  NL Definition → Classify → Parse (with LLM) → Execute → Results
  ```

## Critical Issue Found: LLM Not Being Used in Landing KPI Executor

### The Problem

In `landing_kpi_executor.py` line 150-153:

```python
parser = get_nl_query_parser(kg=kg)
intent = parser.parse(
    nl_definition,
    use_llm=use_llm  # ✅ Parameter IS passed
)
```

**The parameter IS being passed correctly!** ✅

However, the issue is that the `use_llm` parameter comes from `execution_params`:

```python
use_llm = execution_params.get('use_llm', True)  # Line 93
```

### Verification

The `nl_query_parser.py` parse method (line 71-92) correctly handles the `use_llm` parameter:

```python
def parse(self, definition: str, use_llm: bool = True) -> QueryIntent:
    # ...
    if use_llm and self.llm_service.is_enabled():
        intent = self._parse_with_llm(definition, def_type, operation)
    else:
        intent = self._parse_rule_based(definition, def_type, operation)
```

## Actual Differences Between the Two

### NL Query Executor
- ✅ Handles SQL generation via `NLSQLGenerator`
- ✅ Executes SQL queries
- ✅ Formats results
- ❌ Does NOT parse NL definitions (expects QueryIntent)
- ❌ Does NOT classify queries
- ❌ Does NOT interact with LLM

### Landing KPI Executor
- ✅ Classifies NL definitions
- ✅ Parses NL definitions (with optional LLM)
- ✅ Loads Knowledge Graph
- ✅ Calls NL Query Executor for execution
- ✅ Handles database connections
- ✅ Integrates with KPI service

## Workflow Comparison

### Using NL Query Executor Directly
```
1. Create QueryIntent manually or via parser
2. Get database connection
3. Call executor.execute(intent, connection)
4. Get QueryResult
```

### Using Landing KPI Executor
```
1. Provide NL definition + parameters
2. Executor classifies the definition
3. Executor parses with optional LLM
4. Executor gets database connection
5. Executor calls NL Query Executor
6. Executor formats and returns results
```

## Why Landing KPI Executor Might Be Failing

### Possible Causes

1. **Database Connection Issues** ✅ (Already fixed with SSL certificate)
2. **KG Loading Issues** - Entities/relationships not found
3. **LLM Service Not Enabled** - Check `llm_service.is_enabled()`
4. **Parser Confidence Too Low** - `min_confidence` threshold not met
5. **Table Name Resolution** - Business names not mapping to actual tables

### Debugging Steps

1. Check if LLM service is enabled:
   ```python
   from kg_builder.services.llm_service import get_llm_service
   llm = get_llm_service()
   print(f"LLM Enabled: {llm.is_enabled()}")
   ```

2. Verify KG is loaded correctly:
   ```python
   print(f"Nodes: {len(kg.nodes)}")
   print(f"Relationships: {len(kg.relationships)}")
   print(f"Table Aliases: {kg.table_aliases}")
   ```

3. Check parser output:
   ```python
   intent = parser.parse(nl_definition, use_llm=True)
   print(f"Intent: {intent}")
   print(f"Confidence: {intent.confidence}")
   ```

## Recommendations

### 1. **Ensure LLM Service is Properly Configured**
- Verify `OPENAI_API_KEY` is set in `.env`
- Check `ENABLE_LLM_EXTRACTION` is `true`

### 2. **Verify Knowledge Graph Data**
- Ensure KG has entities and relationships
- Verify table aliases are loaded

### 3. **Add Better Logging**
- Log the parsed intent before execution
- Log confidence scores
- Log table resolution results

### 4. **Test LLM Parsing Separately**
```python
from kg_builder.services.nl_query_parser import get_nl_query_parser
parser = get_nl_query_parser(kg=kg)
intent = parser.parse(definition, use_llm=True)
print(f"Parsed: {intent}")
```

## Status

✅ **LLM IS being used** - The `use_llm` parameter is correctly passed through the chain
✅ **Architecture is correct** - Landing KPI Executor properly delegates to NL Query Executor
⚠️ **Potential issues** - Database connection (fixed), KG loading, LLM service configuration

## Next Steps

1. Verify LLM service is enabled and API key is valid
2. Check KG loading and table alias resolution
3. Add detailed logging to track the parsing process
4. Test with a simple NL definition to isolate the issue

