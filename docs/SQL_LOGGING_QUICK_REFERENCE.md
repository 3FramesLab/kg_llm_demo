# SQL Query Logging - Quick Reference

## 🎯 What's New?

All SQL queries executed during reconciliation are now logged in a **formatted, easy-to-read** way.

---

## 📝 Log Format

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

---

## 🔍 Query Types Logged

| Type | Purpose | Method |
|------|---------|--------|
| **MATCHED** | Find records in both source and target | `_execute_matched_query()` |
| **UNMATCHED_SOURCE** | Find records only in source | `_execute_unmatched_source_query()` |
| **UNMATCHED_TARGET** | Find records only in target | `_execute_unmatched_target_query()` |
| **INACTIVE_COUNT** | Count inactive records | `_count_inactive_records()` |

---

## 🔎 Find Queries in Logs

### Linux/Mac
```bash
# All queries
grep "ATTEMPT" app.log

# Specific query type
grep "MATCHED QUERY" app.log

# Specific rule
grep "Material_To_Material" app.log

# Retry attempts (schema fallback)
grep "RETRY ATTEMPT" app.log
```

### Windows
```bash
findstr "ATTEMPT" app.log
findstr "MATCHED QUERY" app.log
findstr "Material_To_Material" app.log
findstr "RETRY ATTEMPT" app.log
```

---

## 📊 Example Log Output

### MATCHED Query
```
====================================================================================================
[FIRST ATTEMPT] MATCHED QUERY - Rule: Material_To_Material
====================================================================================================
SQL:
SELECT s.*, t.*
FROM hana_material_master s
INNER JOIN brz_lnd_RBP_GPU t
ON s.MATERIAL = t.Material
LIMIT 1000
====================================================================================================
```

### UNMATCHED_SOURCE Query
```
====================================================================================================
[FIRST ATTEMPT] UNMATCHED_SOURCE QUERY - Rule: Material_To_Material
====================================================================================================
SQL:
SELECT s.*
FROM hana_material_master s
WHERE NOT EXISTS (
    SELECT 1
    FROM brz_lnd_RBP_GPU t
    WHERE s.MATERIAL = t.Material
)
LIMIT 1000
====================================================================================================
```

### INACTIVE_COUNT Query
```
====================================================================================================
[FIRST ATTEMPT] INACTIVE_COUNT QUERY - Rule: newdqschema.hana_material_master
====================================================================================================
SQL:
SELECT COUNT(*) as inactive_count
FROM hana_material_master
WHERE is_active = 0 OR is_active IS NULL
====================================================================================================
```

### RETRY Attempt (Schema Fallback)
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

---

## 🚀 Common Use Cases

### 1. Debug Query Failures
```bash
# Find the failed query
grep -B 5 "Error executing" app.log

# View the SQL that failed
grep -A 15 "FIRST ATTEMPT" app.log | grep -A 15 "Material_To_Material"
```

### 2. Monitor Schema Fallback
```bash
# Find all retry attempts
grep "RETRY ATTEMPT" app.log

# Count how many queries needed fallback
grep -c "RETRY ATTEMPT" app.log
```

### 3. Check Query Execution Order
```bash
# View all queries in order
grep "ATTEMPT" app.log | grep -E "MATCHED|UNMATCHED|INACTIVE"
```

### 4. Verify Correct SQL
```bash
# View the actual SQL executed
grep -A 20 "MATCHED QUERY" app.log | grep -A 15 "SQL:"
```

---

## 📋 Log Levels

| Level | Content | Usage |
|-------|---------|-------|
| **INFO** | All SQL queries (formatted) | Default - use this |
| **WARNING** | Schema errors, fallbacks | Debugging issues |
| **DEBUG** | Detailed execution flow | Deep debugging |

---

## 🔧 Implementation

### New Method: `_log_sql_query()`
```python
def _log_sql_query(self, query_type: str, rule_name: str, sql: str, attempt: str = "FIRST"):
    """Log SQL query in formatted way"""
    separator = "=" * 100
    logger.info(f"\n{separator}")
    logger.info(f"[{attempt} ATTEMPT] {query_type} QUERY - Rule: {rule_name}")
    logger.info(f"{separator}")
    logger.info(f"SQL:\n{sql}")
    logger.info(f"{separator}\n")
```

### Usage in Methods
```python
# Log first attempt
self._log_sql_query("MATCHED", rule.rule_name, query, "FIRST")

# Log retry attempt
self._log_sql_query("MATCHED", rule.rule_name, query_no_schema, "RETRY")
```

---

## ✅ Benefits

✅ **Easy Debugging** - See exactly what SQL is running
✅ **Clear Format** - Separator lines make queries easy to spot
✅ **Attempt Tracking** - Know if query needed fallback
✅ **Rule Association** - Link queries to rules
✅ **Comprehensive** - All 4 query types logged
✅ **No Performance Impact** - Logging is efficient

---

## 📚 Related Documentation

- **Full Guide**: `SQL_QUERY_LOGGING_GUIDE.md`
- **Schema Fallback**: `SCHEMA_PREFIX_FALLBACK_COMPLETE_FIX.md`
- **Execution Guide**: `RECONCILIATION_EXECUTION_GUIDE.md`

---

## 🎉 Summary

All SQL queries are now logged in a **clear, formatted way** with:
- Query type identification
- Rule association
- Attempt tracking (FIRST/RETRY)
- Easy-to-read separator lines

Use these logs to monitor and debug your reconciliation queries!


