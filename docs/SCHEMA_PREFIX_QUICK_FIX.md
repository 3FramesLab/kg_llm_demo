# Schema Prefix Fallback - Quick Reference

## 🎯 What Was Fixed?

**Error**: `Invalid object name 'newdqschema.hana_material_master'`

**Cause**: SQL Server couldn't find tables with the schema prefix specified in reconciliation rules

**Solution**: Automatic fallback to default schema (dbo) if schema prefix fails

---

## 🔄 How It Works

```
Query Execution Flow:
├─ Try with schema prefix (e.g., newdqschema.table_name)
│  ├─ Success → Use results ✅
│  └─ Fail → Continue to fallback
└─ Try without schema prefix (e.g., table_name)
   ├─ Success → Use results ✅
   └─ Fail → Return error ❌
```

---

## 📊 Query Examples

### Matched Query
```sql
-- First attempt (with schema)
SELECT s.*, t.*
FROM newdqschema.hana_material_master s
INNER JOIN newdqschema.brz_lnd_RBP_GPU t
ON s.MATERIAL = t.Material
LIMIT 1000

-- Fallback (without schema)
SELECT s.*, t.*
FROM hana_material_master s
INNER JOIN brz_lnd_RBP_GPU t
ON s.MATERIAL = t.Material
LIMIT 1000
```

### Unmatched Source Query
```sql
-- First attempt (with schema)
SELECT s.*
FROM newdqschema.hana_material_master s
WHERE NOT EXISTS (
    SELECT 1
    FROM newdqschema.brz_lnd_RBP_GPU t
    WHERE s.MATERIAL = t.Material
)
LIMIT 1000

-- Fallback (without schema)
SELECT s.*
FROM hana_material_master s
WHERE NOT EXISTS (
    SELECT 1
    FROM brz_lnd_RBP_GPU t
    WHERE s.MATERIAL = t.Material
)
LIMIT 1000
```

---

## 📝 Logging Output

### When Schema Prefix Works
```
DEBUG: [MATCHED QUERY] Rule: Material_To_Material
DEBUG: [MATCHED QUERY] SQL: SELECT s.*, t.* FROM newdqschema.hana_material_master s ...
DEBUG: Found 1247 matched records for rule Material_To_Material
```

### When Fallback Is Used
```
DEBUG: [MATCHED QUERY] Rule: Material_To_Material
DEBUG: [MATCHED QUERY] SQL: SELECT s.*, t.* FROM newdqschema.hana_material_master s ...
WARNING: Query with schema prefix failed: Invalid object name 'newdqschema.hana_material_master'. 
         Trying without schema prefix...
DEBUG: [MATCHED QUERY - RETRY] SQL: SELECT s.*, t.* FROM hana_material_master s ...
DEBUG: Found 1247 matched records for rule Material_To_Material
```

---

## ✅ What's Included in Response

The `generated_sql` field shows the query that **actually worked**:

```json
{
  "generated_sql": [
    {
      "rule_id": "RULE_001",
      "rule_name": "Material_To_Material",
      "query_type": "matched",
      "source_sql": "SELECT s.*, t.* FROM hana_material_master s INNER JOIN brz_lnd_RBP_GPU t ON s.MATERIAL = t.Material LIMIT 1000",
      "target_sql": null,
      "description": "Find matched records between hana_material_master and brz_lnd_RBP_GPU"
    }
  ]
}
```

---

## 🔧 Updated Methods

| Method | Purpose | Change |
|--------|---------|--------|
| `_execute_matched_query()` | Find matched records | Added schema fallback |
| `_execute_unmatched_source_query()` | Find unmatched source | Added schema fallback |
| `_execute_unmatched_target_query()` | Find unmatched target | Added schema fallback |

---

## 🎯 Benefits

✅ **Automatic** - No manual intervention needed
✅ **Transparent** - Logs all attempts
✅ **Flexible** - Works with any schema configuration
✅ **Backward Compatible** - Still tries with schema first
✅ **Robust** - Handles SQL Server schema issues gracefully

---

## 🚀 Usage

No changes needed! The fix is automatic:

```bash
# Execute reconciliation as usual
curl -X POST http://localhost:8000/reconciliation/execute \
  -H "Content-Type: application/json" \
  -d '{
    "ruleset_id": "RECON_ABC123",
    "limit": 1000,
    "include_matched": true,
    "include_unmatched": true
  }'
```

The system will:
1. Try with schema prefix
2. Fallback to default schema if needed
3. Return results with the working query

---

## 📋 Troubleshooting

### Still getting "Invalid object name" error?

**Check 1**: Verify table exists
```sql
SELECT * FROM information_schema.tables 
WHERE table_name = 'hana_material_master'
```

**Check 2**: Verify user permissions
```sql
SELECT * FROM sys.tables 
WHERE name = 'hana_material_master'
```

**Check 3**: Check table schema
```sql
SELECT table_schema, table_name 
FROM information_schema.tables 
WHERE table_name = 'hana_material_master'
```

### Query returns no results?

1. Check if tables are empty
2. Verify join conditions match actual data
3. Check filter conditions in rule
4. Review logs for the actual query used

---

## 📚 Related Documentation

- **Detailed Guide**: `SCHEMA_PREFIX_FALLBACK_FIX.md`
- **File Storage**: `RECONCILIATION_FILE_BASED_STORAGE.md`
- **Execution Guide**: `RECONCILIATION_EXECUTION_GUIDE.md`

---

## 🎉 Summary

✅ Schema prefix errors are now handled automatically
✅ Queries fallback to default schema if needed
✅ All attempts are logged for debugging
✅ Generated SQL shows the query that worked
✅ No configuration changes needed

Ready to use!


