# SQL Query Logging Guide - Comprehensive Debugging

## 🎯 Overview

Enhanced SQL query logging has been added to the reconciliation executor to help you debug and monitor all SQL queries executed during reconciliation.

---

## ✨ Features

✅ **Formatted SQL Logging** - All queries logged in a clear, readable format
✅ **Query Type Identification** - Each query type clearly labeled
✅ **Attempt Tracking** - Shows FIRST attempt and RETRY attempts
✅ **Rule Association** - Each query linked to its rule
✅ **Separator Lines** - Easy to spot queries in logs
✅ **Comprehensive Coverage** - All 4 query types logged

---

## 📋 Query Types Logged

### 1. MATCHED Query
- **Purpose**: Find records in both source and target
- **Method**: `_execute_matched_query()`
- **Example**: INNER JOIN between source and target tables

### 2. UNMATCHED_SOURCE Query
- **Purpose**: Find records only in source
- **Method**: `_execute_unmatched_source_query()`
- **Example**: NOT EXISTS query for source records

### 3. UNMATCHED_TARGET Query
- **Purpose**: Find records only in target
- **Method**: `_execute_unmatched_target_query()`
- **Example**: NOT EXISTS query for target records

### 4. INACTIVE_COUNT Query
- **Purpose**: Count inactive records (is_active = 0 or NULL)
- **Method**: `_count_inactive_records()`
- **Example**: COUNT query with WHERE clause

---

## 📝 Log Output Format

### Example: MATCHED Query (First Attempt)
```
====================================================================================================
[FIRST ATTEMPT] MATCHED QUERY - Rule: Material_To_Material
====================================================================================================
SQL:

            SELECT s.*, t.*
            FROM newdqschema.hana_material_master s
            INNER JOIN newdqschema.brz_lnd_RBP_GPU t
                ON s.MATERIAL = t.Material
            LIMIT 1000
            
====================================================================================================
```

### Example: MATCHED Query (Retry After Schema Fallback)
```
WARNING: Query with schema prefix failed: Invalid object name 'newdqschema.hana_material_master'. 
         Trying without schema prefix...

====================================================================================================
[RETRY ATTEMPT] MATCHED QUERY - Rule: Material_To_Material
====================================================================================================
SQL:

            SELECT s.*, t.*
            FROM hana_material_master s
            INNER JOIN brz_lnd_RBP_GPU t
                ON s.MATERIAL = t.Material
            LIMIT 1000
            
====================================================================================================
```

### Example: UNMATCHED_SOURCE Query
```
====================================================================================================
[FIRST ATTEMPT] UNMATCHED_SOURCE QUERY - Rule: Material_To_Material
====================================================================================================
SQL:

            SELECT s.*
            FROM newdqschema.hana_material_master s
            WHERE NOT EXISTS (
                SELECT 1
                FROM newdqschema.brz_lnd_RBP_GPU t
                WHERE s.MATERIAL = t.Material
            )
            LIMIT 1000
            
====================================================================================================
```

### Example: INACTIVE_COUNT Query
```
====================================================================================================
[FIRST ATTEMPT] INACTIVE_COUNT QUERY - Rule: newdqschema.hana_material_master
====================================================================================================
SQL:

            SELECT COUNT(*) as inactive_count
            FROM newdqschema.hana_material_master
            WHERE is_active = 0 OR is_active IS NULL
            
====================================================================================================
```

---

## 🔍 How to Find Queries in Logs

### Using grep (Linux/Mac)
```bash
# Find all SQL queries
grep -A 20 "FIRST ATTEMPT" app.log

# Find specific query type
grep -A 20 "MATCHED QUERY" app.log

# Find retry attempts
grep -A 20 "RETRY ATTEMPT" app.log

# Find specific rule
grep -A 20 "Material_To_Material" app.log
```

### Using findstr (Windows)
```bash
# Find all SQL queries
findstr /A:20 "FIRST ATTEMPT" app.log

# Find specific query type
findstr /A:20 "MATCHED QUERY" app.log

# Find retry attempts
findstr /A:20 "RETRY ATTEMPT" app.log
```

---

## 📊 Log Levels

### INFO Level (Default)
- All SQL queries are logged at INFO level
- Formatted with separators for easy reading
- Includes query type, rule name, and SQL

### WARNING Level
- Schema fallback warnings
- Query execution failures
- Connection issues

### DEBUG Level
- Detailed execution flow
- Connection establishment
- Result processing

---

## 🔧 Implementation Details

### New Helper Method: `_log_sql_query()`

```python
def _log_sql_query(self, query_type: str, rule_name: str, sql: str, attempt: str = "FIRST"):
    """
    Log SQL query in a formatted way for debugging.
    
    Args:
        query_type: Type of query (MATCHED, UNMATCHED_SOURCE, UNMATCHED_TARGET, INACTIVE_COUNT)
        rule_name: Name of the rule being executed
        sql: The SQL query to log
        attempt: Attempt number (FIRST, RETRY)
    """
    separator = "=" * 100
    logger.info(f"\n{separator}")
    logger.info(f"[{attempt} ATTEMPT] {query_type} QUERY - Rule: {rule_name}")
    logger.info(f"{separator}")
    logger.info(f"SQL:\n{sql}")
    logger.info(f"{separator}\n")
```

---

## 📋 Updated Methods

All 4 query execution methods now use the logging helper:

| Method | Query Type | Logged |
|--------|-----------|--------|
| `_execute_matched_query()` | MATCHED | ✅ |
| `_execute_unmatched_source_query()` | UNMATCHED_SOURCE | ✅ |
| `_execute_unmatched_target_query()` | UNMATCHED_TARGET | ✅ |
| `_count_inactive_records()` | INACTIVE_COUNT | ✅ |

---

## 🚀 Usage Examples

### Example 1: Monitor Reconciliation Execution
```bash
# Run reconciliation and capture logs
python -m kg_builder.routes > reconciliation.log 2>&1

# View all SQL queries
grep "ATTEMPT" reconciliation.log | head -20
```

### Example 2: Debug Failed Query
```bash
# Find the failed query
grep -B 5 "Invalid object name" reconciliation.log

# View the query that failed
grep -A 15 "FIRST ATTEMPT" reconciliation.log | grep -A 15 "Material_To_Material"
```

### Example 3: Check Schema Fallback
```bash
# Find all retry attempts
grep "RETRY ATTEMPT" reconciliation.log

# View the fallback queries
grep -A 15 "RETRY ATTEMPT" reconciliation.log
```

---

## 📊 Log Analysis

### Check Query Execution Order
```bash
grep "ATTEMPT" reconciliation.log | grep -E "MATCHED|UNMATCHED|INACTIVE"
```

### Count Query Types
```bash
grep "ATTEMPT" reconciliation.log | grep -c "MATCHED"
grep "ATTEMPT" reconciliation.log | grep -c "UNMATCHED_SOURCE"
grep "ATTEMPT" reconciliation.log | grep -c "UNMATCHED_TARGET"
grep "ATTEMPT" reconciliation.log | grep -c "INACTIVE_COUNT"
```

### Find Failed Queries
```bash
grep -B 20 "Error executing" reconciliation.log | grep "ATTEMPT"
```

---

## 🎯 Troubleshooting with Logs

### Issue: Query Returns No Results
**Solution**: Check the logged SQL query
```bash
grep -A 15 "MATCHED QUERY" reconciliation.log
# Review the JOIN condition and WHERE clause
```

### Issue: Schema Prefix Error
**Solution**: Look for RETRY attempts
```bash
grep -B 5 "RETRY ATTEMPT" reconciliation.log
# Check if fallback query succeeded
```

### Issue: Slow Query Performance
**Solution**: Review the logged SQL
```bash
grep -A 15 "UNMATCHED_SOURCE QUERY" reconciliation.log
# Check for missing indexes or complex joins
```

---

## 📝 Log Configuration

### Set Log Level to INFO (Default)
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Set Log Level to DEBUG (Verbose)
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log to File
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    filename='reconciliation.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## 🔗 Related Files

- **Executor**: `kg_builder/services/reconciliation_executor.py`
- **Models**: `kg_builder/models.py`
- **Routes**: `kg_builder/routes.py`

---

## 🎉 Summary

✅ **All SQL queries logged** - Easy to debug
✅ **Formatted output** - Clear and readable
✅ **Query type identification** - Know what query is running
✅ **Attempt tracking** - See FIRST and RETRY attempts
✅ **Rule association** - Link queries to rules
✅ **Comprehensive coverage** - All 4 query types

Use these logs to monitor, debug, and optimize your reconciliation queries!


