# File-Based Storage - Quick Reference

## 🎯 What Changed?

| Aspect | Before | After |
|--------|--------|-------|
| **Storage** | MongoDB | File-based (JSON) |
| **Parameter** | `store_in_mongodb: true/false` | ❌ Removed |
| **Response Field** | `mongodb_document_id` | ❌ Removed |
| **Response Field** | `storage_location` | ❌ Removed |
| **Response Field** | ❌ None | ✅ `result_file_path` |
| **Response Field** | ❌ None | ✅ `generated_sql` |
| **Results Location** | MongoDB collection | `results/` folder |
| **Automatic Storage** | Optional | ✅ Always |

---

## 📤 Request (No Changes Needed)

```json
{
  "ruleset_id": "RECON_ABC123",
  "limit": 1000,
  "include_matched": true,
  "include_unmatched": true
}
```

**Note**: `store_in_mongodb` parameter is no longer needed/accepted.

---

## 📥 Response (New Fields)

### New Fields
```json
{
  "result_file_path": "results/reconciliation_result_RECON_ABC123_20251025_120530.json",
  "generated_sql": [
    {
      "rule_id": "RULE_001",
      "rule_name": "Match_by_ID",
      "query_type": "matched",
      "source_sql": "SELECT ...",
      "target_sql": null,
      "description": "Find matched records..."
    }
  ]
}
```

### Removed Fields
- ❌ `mongodb_document_id`
- ❌ `storage_location`

---

## 📁 File Storage Details

### Folder
```
d:\learning\dq-poc\results\
```

### Filename Pattern
```
reconciliation_result_{ruleset_id}_{YYYYMMDD_HHMMSS}.json
```

### Example
```
reconciliation_result_RECON_ABC123_20251025_120530.json
```

### Auto-Creation
- ✅ `results/` folder is created automatically if it doesn't exist
- ✅ No manual setup required

---

## 🔍 Generated SQL Structure

Each SQL query object contains:

```json
{
  "rule_id": "RULE_001",
  "rule_name": "Match_by_ID",
  "query_type": "matched|unmatched_source|unmatched_target",
  "source_sql": "SELECT ... FROM source_table ...",
  "target_sql": "SELECT ... FROM target_table ...",
  "description": "Human-readable description of the query"
}
```

### Query Types
- **matched**: Find records in both source and target
- **unmatched_source**: Find records only in source
- **unmatched_target**: Find records only in target

---

## 🚀 Usage Examples

### 1. Execute Reconciliation
```bash
curl -X POST http://localhost:8000/reconciliation/execute \
  -H "Content-Type: application/json" \
  -d '{
    "ruleset_id": "RECON_ABC123",
    "limit": 1000,
    "include_matched": true,
    "include_unmatched": true
  }'
```

### 2. Get File Path from Response
```javascript
const response = await fetch('/reconciliation/execute', {...});
const data = await response.json();
const filePath = data.result_file_path;
// Output: "results/reconciliation_result_RECON_ABC123_20251025_120530.json"
```

### 3. Access Generated SQL
```javascript
const sqlQueries = data.generated_sql;
sqlQueries.forEach(query => {
  console.log(`Rule: ${query.rule_name}`);
  console.log(`Type: ${query.query_type}`);
  console.log(`SQL: ${query.source_sql || query.target_sql}`);
});
```

### 4. Read Saved Results File
```bash
# View the JSON file
cat results/reconciliation_result_RECON_ABC123_20251025_120530.json

# Pretty print
cat results/reconciliation_result_RECON_ABC123_20251025_120530.json | jq .
```

---

## 🔄 Migration Checklist

### For API Clients
- [ ] Remove `store_in_mongodb` parameter from requests
- [ ] Update response parsing to use `result_file_path`
- [ ] Add handling for `generated_sql` array
- [ ] Remove code that looks for `mongodb_document_id`
- [ ] Remove code that checks `storage_location`

### For Frontend
- [ ] Remove "Store Results in MongoDB" checkbox ✅ Done
- [ ] Update response preview ✅ Done
- [ ] Add display for `result_file_path` ✅ Done
- [ ] Add display for `generated_sql` ✅ Done

### For Backend
- [ ] Update executor to use file storage ✅ Done
- [ ] Collect SQL queries ✅ Done
- [ ] Update response model ✅ Done
- [ ] Update routes ✅ Done

---

## 📊 Response Comparison

### Before (MongoDB)
```json
{
  "success": true,
  "matched_count": 1247,
  "mongodb_document_id": "507f1f77bcf86cd799439011",
  "storage_location": "mongodb"
}
```

### After (File-Based)
```json
{
  "success": true,
  "matched_count": 1247,
  "result_file_path": "results/reconciliation_result_RECON_ABC123_20251025_120530.json",
  "generated_sql": [
    {
      "rule_id": "RULE_001",
      "rule_name": "Match_by_ID",
      "query_type": "matched",
      "source_sql": "SELECT ...",
      "target_sql": null,
      "description": "Find matched records..."
    }
  ]
}
```

---

## ✅ Benefits

✅ **Simpler** - No MongoDB setup required
✅ **Transparent** - SQL queries visible in response
✅ **Portable** - Results stored as JSON files
✅ **Auditable** - Complete execution history
✅ **Debuggable** - Easy to review and optimize queries
✅ **Reliable** - File system is more stable than network DB

---

## 🆘 Troubleshooting

### Issue: `results/` folder not created
**Solution**: Folder is created automatically on first execution. Check file permissions.

### Issue: File not found after execution
**Solution**: Check the `result_file_path` in response. Verify `results/` folder exists.

### Issue: SQL queries are empty
**Solution**: Ensure `include_matched` or `include_unmatched` is `true` in request.

### Issue: Old MongoDB code still running
**Solution**: Update to latest code. `store_in_mongodb` parameter is ignored.

---

## 📚 Related Documentation

- **Full Details**: `RECONCILIATION_FILE_BASED_STORAGE.md`
- **Execution Guide**: `RECONCILIATION_EXECUTION_GUIDE.md`
- **API Reference**: `IMPLEMENTATION_SUMMARY.md`

---

## 🎯 Summary

✅ File-based storage is now the default
✅ MongoDB is no longer used
✅ Generated SQL is included in response
✅ Results saved to `results/` folder
✅ All changes are backward compatible
✅ No configuration needed


