# Landing KPI Executor - Improvements & Debugging ✅

## Summary

Enhanced `landing_kpi_executor.py` with comprehensive logging to help debug issues and verify that LLM is being used correctly during KPI execution.

## Key Findings

### ✅ LLM IS Being Used Correctly

The `use_llm` parameter is properly passed through the entire chain:

```
Execution Params (use_llm=true)
    ↓
landing_kpi_executor.py line 93: use_llm = execution_params.get('use_llm', True)
    ↓
landing_kpi_executor.py line 166: parser.parse(nl_definition, use_llm=use_llm)
    ↓
nl_query_parser.py line 89: if use_llm and self.llm_service.is_enabled():
    ↓
nl_query_parser.py line 90: intent = self._parse_with_llm(...)
```

## Improvements Made

### 1. **Enhanced KG Loading Logging** (Lines 113-148)

Now logs:
- ✅ KG name being loaded
- ✅ Number of entities found
- ✅ Number of relationships found
- ✅ Number of table aliases loaded
- ✅ Actual aliases (debug level)

**Example Output:**
```
Loading Knowledge Graph: KG_102
  - Entities found: 45
  - Relationships found: 120
  - Table aliases loaded: 12
    Aliases: {'RBP GPU': 'rbp_gpu_table', ...}
✓ Loaded KG 'KG_102' with 45 nodes and 120 relationships
```

### 2. **Enhanced Parsing Logging** (Lines 155-175)

Now logs:
- ✅ Whether LLM is enabled in request
- ✅ Whether LLM service is available
- ✅ Parsed query type
- ✅ Source and target tables
- ✅ Operation type
- ✅ Join columns found
- ✅ Confidence score
- ✅ Filters applied

**Example Output:**
```
Parsing with LLM enabled: true
LLM Service enabled: true
✓ Parsed Intent:
  - Query Type: comparison_query
  - Source Table: rbp_gpu_table
  - Target Table: ops_excel_table
  - Operation: NOT_IN
  - Join Columns: [('gpu_id', 'product_id')]
  - Confidence: 0.85
  - Filters: [{'column': 'status', 'operator': 'equals', 'value': 'inactive'}]
```

## Debugging Guide

### Issue 1: LLM Service Not Enabled

**Symptom:** Log shows `LLM Service enabled: false`

**Solution:**
1. Check `.env` file:
   ```bash
   OPENAI_API_KEY=sk-proj-...
   ENABLE_LLM_EXTRACTION=true
   ```
2. Verify API key is valid
3. Restart application

### Issue 2: KG Not Loading

**Symptom:** Log shows `Entities found: 0` or `Relationships found: 0`

**Solution:**
1. Verify KG exists in Graphiti backend
2. Check KG name matches exactly (case-sensitive)
3. Verify KG was created successfully
4. Check Graphiti backend connection

### Issue 3: Table Names Not Resolving

**Symptom:** Log shows `Source Table: None` or `Target Table: None`

**Solution:**
1. Check table aliases are loaded: `Table aliases loaded: X`
2. Verify business names in NL definition match aliases
3. Check if LLM is parsing correctly
4. Review parsed intent filters

### Issue 4: Low Confidence Score

**Symptom:** Log shows `Confidence: 0.3` or similar low value

**Solution:**
1. Check if join columns were found
2. Verify KG has relationships between tables
3. Check if LLM parsing is working
4. Review min_confidence threshold in request

### Issue 5: Database Connection Failed

**Symptom:** Error during Step 4

**Solution:**
1. Verify database credentials in `.env`
2. Check database is running and accessible
3. Verify JDBC driver is in `jdbc_drivers/` directory
4. Check SSL certificate settings (already fixed)

## Execution Flow with Logging

```
1. Extract Parameters
   ├─ kg_name: KG_102
   ├─ schemas: ['newdqschema']
   ├─ definitions: ['Show me all products...']
   ├─ use_llm: true
   ├─ min_confidence: 0.7
   ├─ limit: 1000
   └─ db_type: sqlserver

2. Load Knowledge Graph
   ├─ Loading Knowledge Graph: KG_102
   ├─ Entities found: 45
   ├─ Relationships found: 120
   ├─ Table aliases loaded: 12
   └─ ✓ Loaded KG 'KG_102' with 45 nodes and 120 relationships

3. Classify Query
   └─ Query Type: comparison_query

4. Parse Query
   ├─ Parsing with LLM enabled: true
   ├─ LLM Service enabled: true
   ├─ ✓ Parsed Intent:
   │  ├─ Query Type: comparison_query
   │  ├─ Source Table: rbp_gpu_table
   │  ├─ Target Table: ops_excel_table
   │  ├─ Operation: NOT_IN
   │  ├─ Join Columns: [('gpu_id', 'product_id')]
   │  ├─ Confidence: 0.85
   │  └─ Filters: [...]

5. Get Database Connection
   ├─ Using JDBC driver: mssql-jdbc-9.4.0.jre11.jar
   └─ ✓ Successfully connected to source database

6. Execute Query
   ├─ SQL TO BE EXECUTED: SELECT ...
   ├─ ✓ SQL executed successfully
   └─ 📊 Query Result: Found 42 records

7. Return Results
   └─ ✓ KPI execution successful: 42 records in 1234.56ms
```

## Files Modified

- **kg_builder/services/landing_kpi_executor.py**
  - Enhanced KG loading logging (lines 113-148)
  - Enhanced parsing logging (lines 155-175)
  - Added LLM service availability check (lines 160-162)

## Testing

To test the improvements:

1. Execute a KPI with `use_llm: true`
2. Check logs for detailed output
3. Verify each step completes successfully
4. Review confidence scores and parsed intent

## Status

✅ **COMPLETE** - Enhanced logging for debugging and verification
✅ **LLM IS BEING USED** - Confirmed in code flow
✅ **Ready for Testing** - Execute KPI and review logs

## Next Steps

1. Execute KPI and review logs
2. Identify any issues from log output
3. Use debugging guide above to resolve
4. Verify results are correct

