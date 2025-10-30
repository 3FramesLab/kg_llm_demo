# MySQL JDBC Timeout Fix

## Problem Summary

The reconciliation execution was failing with the following error:
```
ERROR - Error executing matched query: com.mysql.cj.jdbc.exceptions.CommunicationsException: Communications link failure

The last packet successfully received from the server was 10,021 milliseconds ago.
The last packet sent successfully to the server was 10,022 milliseconds ago.
```

## Root Cause Analysis

**File:** `kg_builder/services/reconciliation_executor.py:506`

The JDBC connection URL had timeout values that were too short for complex reconciliation queries:
- `connectTimeout=5000` (5 seconds)
- `socketTimeout=5000` (5 seconds)

**What was happening:**
1. Connection to MySQL was established successfully
2. Reconciliation queries involving cross-schema JOINs were executed
3. These complex queries took ~10 seconds to complete
4. The `socketTimeout` of 5 seconds expired before query completion
5. Connection was terminated, causing all subsequent queries to fail

## The Fix

Updated the JDBC connection string in `reconciliation_executor.py`:

### Before:
```python
return f"jdbc:mysql://{db_config.host}:{db_config.port}/{db_config.database}?connectTimeout=5000&socketTimeout=5000"
```

### After:
```python
return f"jdbc:mysql://{db_config.host}:{db_config.port}/{db_config.database}?connectTimeout=60000&socketTimeout=120000&autoReconnect=true"
```

### Changes Made:
- `connectTimeout`: 5000ms → 60000ms (5s → 60s)
- `socketTimeout`: 5000ms → 120000ms (5s → 120s)
- Added `autoReconnect=true` for automatic reconnection

## Why These Values?

1. **connectTimeout (60s)**: Time allowed to establish initial connection
   - Sufficient for slow network conditions
   - Prevents indefinite hanging

2. **socketTimeout (120s)**: Time allowed for queries to execute and return data
   - Complex reconciliation queries with JOINs across schemas can take 10-30 seconds
   - Provides buffer for large result sets
   - Balances between allowing long queries and detecting real connection failures

3. **autoReconnect=true**: Automatically reconnects if connection drops
   - Improves resilience for long-running reconciliation jobs
   - Handles temporary network issues

## Impact

This fix affects all MySQL JDBC connections made through the ReconciliationExecutor:
- Reconciliation rule execution
- Matched/unmatched record queries
- Cross-schema JOIN operations

## Testing the Fix

To verify the fix works, run the end-to-end reconciliation test:

```bash
python test_e2e_reconciliation_simple.py
```

**Expected Results:**
- No more "Communications link failure" errors
- All 19 reconciliation rules execute successfully
- Matched and unmatched records are properly identified
- Results are stored in MongoDB

## Monitoring

Check the log file for successful execution:
```bash
tail -f e2e_reconciliation.log
```

Look for:
- "Database connection established" (connection successful)
- "Execution complete: X matched, Y unmatched source, Z unmatched target" (queries successful)
- "Results stored in MongoDB with document ID: ..." (storage successful)

## Related Files

- `kg_builder/services/reconciliation_executor.py` - JDBC connection logic (FIXED)
- `test_e2e_reconciliation_simple.py` - E2E test script
- `e2e_reconciliation.log` - Execution log file
- `.env` - Database connection configuration

## Additional Considerations

If queries still timeout with these values:
1. Check MySQL server settings (`max_execution_time`, `wait_timeout`)
2. Add indexes to frequently joined columns
3. Consider query optimization or pagination for large datasets
4. Monitor query execution time in logs (DEBUG level)

---
**Fixed by:** Claude Code
**Date:** 2025-10-24
**Issue:** MySQL JDBC timeout during reconciliation execution
