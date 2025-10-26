# KPI Evidence Not Showing Records - Fixed! ✅

## 🎯 Problem

KPI Results screen's "View Evidence" button was not showing any records, even though reconciliation data existed.

---

## 🔍 Root Cause

The evidence query was not properly filtering records based on KPI type. It was querying all records without considering what the KPI was measuring.

### Before (Broken)
```python
# Query all records regardless of KPI type
query = """
    SELECT * FROM reconciliation_results
    WHERE ruleset_id = ?
"""
# No filtering by KPI type!
```

### After (Fixed)
```python
# Filter records based on KPI type
if kpi_type == "match_rate":
    # Show all records
    pass
elif kpi_type == "unmatched_source_count":
    query += " AND match_status = 'unmatched_source'"
elif kpi_type == "unmatched_target_count":
    query += " AND match_status = 'unmatched_target'"
elif kpi_type == "inactive_record_count":
    query += " AND match_status = 'inactive'"
elif kpi_type == "data_quality_score":
    query += " AND match_status = 'matched'"
```

---

## ✅ What's Fixed

### 1. Backend Improvements
- ✅ Added KPI type-based filtering
- ✅ Enhanced logging for debugging
- ✅ Better error handling with stack traces

### 2. Frontend Improvements
- ✅ Added detailed console logging
- ✅ Shows KPI type and ruleset in dialog
- ✅ Better "no records" message with diagnostics
- ✅ Shows possible reasons for empty results

### 3. Evidence Query Logic
```
KPI Type → Filter Applied
─────────────────────────────────────────
match_rate → All records
match_percentage → All records
unmatched_source_count → match_status = 'unmatched_source'
unmatched_target_count → match_status = 'unmatched_target'
inactive_record_count → match_status = 'inactive'
data_quality_score → match_status = 'matched'
```

---

## 📁 Files Modified

| File | Changes |
|------|---------|
| `kg_builder/services/kpi_file_service.py` | Added KPI type filtering in `_query_evidence_data()` |
| `web-app/src/pages/KPIResults.js` | Enhanced logging and error messages |

---

## 🚀 How to Test

### Step 1: Create a KPI
1. Go to KPI Management
2. Create a KPI (e.g., "Match Rate")
3. Select a ruleset with reconciliation data

### Step 2: Execute the KPI
1. Click Execute button
2. Wait for execution to complete

### Step 3: View Evidence
1. Go to KPI Results
2. Click "View Evidence" button
3. Check if records appear

### Step 4: Check Console
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for logs like:
   ```
   📊 Loading evidence for KPI: KPI_001
   📡 Evidence API Response Status: 200 OK
   ✅ Evidence response: {...}
   📊 Total records: 50
   ```

---

## 🔧 Debugging

### If Still No Records

#### Check 1: Reconciliation Data Exists
```bash
# Query the database directly
SELECT COUNT(*) FROM reconciliation_results WHERE ruleset_id = 'RECON_9240A5F7';
```

#### Check 2: Browser Console
1. Open DevTools (F12)
2. Go to Console tab
3. Look for error messages
4. Check the API response

#### Check 3: Backend Logs
```bash
# Check backend logs for evidence query
grep "Evidence query" backend.log
grep "Retrieved.*evidence records" backend.log
```

#### Check 4: KPI Type
Make sure KPI type matches the data:
- `match_rate` → Should show all records
- `unmatched_source_count` → Should show unmatched_source records
- `inactive_record_count` → Should show inactive records

---

## 📊 Evidence Dialog Features

### KPI Information Box
Shows:
- KPI Type (e.g., "match_rate")
- Ruleset ID (e.g., "RECON_9240A5F7")

### Filters
- **Filter by Status**: All, Matched, Unmatched Source, Unmatched Target, Inactive
- **Limit**: Number of records to show (default: 100)
- **Refresh**: Reload evidence with new filters

### Evidence Table
Columns:
- **Record ID**: Unique identifier
- **Status**: Match status (color-coded)
- **Rule**: Rule name that matched
- **Data**: Source and target data preview

### No Records Message
If no records found, shows:
```
ℹ️ No evidence records found

This could mean:
• No reconciliation data exists for this ruleset
• No records match the selected filter
• Check browser console for detailed error logs
```

---

## 🎯 Evidence Query Flow

```
1. User clicks "View Evidence"
   ↓
2. Frontend sends POST /v1/reconciliation/kpi/{kpi_id}/evidence
   ↓
3. Backend:
   - Gets KPI definition
   - Gets KPI type
   - Builds query with KPI type filter
   - Applies match_status filter (if provided)
   - Applies pagination (limit/offset)
   - Executes query
   ↓
4. Frontend receives results
   ↓
5. Shows evidence in table
```

---

## 📋 Evidence Record Structure

```json
{
  "record_id": "REC_001",
  "match_status": "matched",
  "rule_name": "RULE_MATERIAL_MATCH",
  "record_data": {
    "source_data": "Material A",
    "target_data": "Material A",
    "match_confidence": 0.95
  }
}
```

---

## 🔍 Console Logging

### Successful Load
```
📊 Loading evidence for KPI: KPI_001
📋 Payload: {kpi_id: "KPI_001", match_status: null, limit: 100, offset: 0}
📡 Evidence API Response Status: 200 OK
✅ Evidence response: {success: true, total_count: 50, evidence_records: [...]}
📊 Total records: 50
📋 Evidence records: 50
```

### No Records
```
📊 Loading evidence for KPI: KPI_001
📋 Payload: {kpi_id: "KPI_001", match_status: null, limit: 100, offset: 0}
📡 Evidence API Response Status: 200 OK
✅ Evidence response: {success: true, total_count: 0, evidence_records: []}
📊 Total records: 0
📋 Evidence records: 0
⚠️ No evidence records found for this KPI
```

### Error
```
📊 Loading evidence for KPI: KPI_001
❌ Exception: Error: HTTP 500: Internal Server Error
❌ Error loading evidence: Error: HTTP 500: Internal Server Error
```

---

## 🧪 Testing Scenarios

### Scenario 1: Match Rate KPI
- Create KPI with type "match_rate"
- Execute KPI
- View Evidence
- Should show all reconciliation records

### Scenario 2: Unmatched Source Count KPI
- Create KPI with type "unmatched_source_count"
- Execute KPI
- View Evidence
- Should show only unmatched_source records

### Scenario 3: Filter by Status
- View Evidence
- Select "Matched" from filter
- Click Refresh
- Should show only matched records

### Scenario 4: Pagination
- View Evidence
- Change Limit to 10
- Click Refresh
- Should show only 10 records

---

## 📚 Related Documentation

- **KPI_EXECUTION_QUICK_REFERENCE.md** - How to execute KPIs
- **WHEN_KPI_GETS_EXECUTED.md** - KPI execution details
- **KPI_EXECUTE_BUTTON_ADDED.md** - Execute button documentation

---

## ✨ Summary

✅ **KPI type filtering** added to evidence query
✅ **Enhanced logging** for debugging
✅ **Better error messages** in UI
✅ **Diagnostic information** shown when no records
✅ **Console logging** for troubleshooting

Now evidence records should display properly! 🎉


