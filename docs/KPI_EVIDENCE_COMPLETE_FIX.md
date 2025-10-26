# KPI Evidence Records - Complete Fix ✅

## 🎯 Issue

KPI Results screen's "View Evidence" button was not showing any records, even though reconciliation data existed.

---

## 🔍 Root Cause Analysis

### Problem 1: No KPI Type Filtering
The evidence query was retrieving ALL records from the reconciliation_results table without filtering by KPI type.

```python
# BROKEN: No filtering by KPI type
query = """
    SELECT * FROM reconciliation_results
    WHERE ruleset_id = ?
"""
# This returns all records regardless of what the KPI measures!
```

### Problem 2: Missing Logging
No logging to help debug why records weren't appearing.

### Problem 3: Poor Error Messages
Frontend showed generic "No evidence records found" without helpful diagnostics.

---

## ✅ Solution Implemented

### 1. Backend: KPI Type-Based Filtering

Added intelligent filtering based on KPI type:

```python
def _query_evidence_data(self, kpi_type, ruleset_id, match_status, limit, offset):
    # Filter by KPI type
    if kpi_type == "match_rate" or kpi_type == "match_percentage":
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
    
    # Apply user filter if provided
    if match_status:
        query += " AND match_status = ?"
        params.append(match_status)
```

### 2. Backend: Enhanced Logging

Added detailed logging for debugging:

```python
logger.info(f"Executing evidence query for KPI type {kpi_type}, ruleset {ruleset_id}")
logger.debug(f"Evidence query: {query}, params: {params}")
logger.info(f"Retrieved {len(rows)} evidence records")
```

### 3. Frontend: Console Logging

Added detailed console logs:

```javascript
console.log('📊 Loading evidence for KPI:', kpi.kpi_id);
console.log('📋 Payload:', payload);
console.log(`📡 Evidence API Response Status: ${response.status}`);
console.log('✅ Evidence response:', data);
console.log(`📊 Total records: ${data.total_count}`);
```

### 4. Frontend: Better Error Messages

Enhanced "no records" message with diagnostics:

```
ℹ️ No evidence records found

This could mean:
• No reconciliation data exists for this ruleset
• No records match the selected filter
• Check browser console for detailed error logs
```

### 5. Frontend: KPI Context

Shows KPI type and ruleset in the evidence dialog:

```
KPI Type: match_rate
Ruleset: RECON_9240A5F7
```

---

## 📊 Evidence Filtering Logic

### By KPI Type

| KPI Type | Records Shown | Filter Applied |
|----------|---------------|----------------|
| match_rate | All | None |
| match_percentage | All | None |
| unmatched_source_count | Unmatched Source | match_status = 'unmatched_source' |
| unmatched_target_count | Unmatched Target | match_status = 'unmatched_target' |
| inactive_record_count | Inactive | match_status = 'inactive' |
| data_quality_score | Matched | match_status = 'matched' |

### User Filters

User can further filter by:
- **Status**: All, Matched, Unmatched Source, Unmatched Target, Inactive
- **Limit**: Number of records to display
- **Offset**: Pagination (via Refresh button)

---

## 🚀 How It Works Now

### Step 1: User Clicks "View Evidence"
```
Frontend sends: POST /v1/reconciliation/kpi/{kpi_id}/evidence
Payload: {
  kpi_id: "KPI_001",
  match_status: null,
  limit: 100,
  offset: 0
}
```

### Step 2: Backend Processes Request
```
1. Get KPI definition
2. Extract KPI type (e.g., "match_rate")
3. Build query with KPI type filter
4. Apply user filters (if any)
5. Execute query
6. Return results
```

### Step 3: Frontend Displays Results
```
1. Receive response
2. Log details to console
3. Show records in table
4. Or show diagnostic message if empty
```

---

## 🧪 Testing

### Test 1: Match Rate KPI
```
1. Create KPI with type "match_rate"
2. Execute KPI
3. View Evidence
4. Should show all reconciliation records
```

### Test 2: Unmatched Source Count KPI
```
1. Create KPI with type "unmatched_source_count"
2. Execute KPI
3. View Evidence
4. Should show only unmatched_source records
```

### Test 3: Filter by Status
```
1. View Evidence
2. Select "Matched" from filter
3. Click Refresh
4. Should show only matched records
```

### Test 4: Check Console
```
1. Open DevTools (F12)
2. Go to Console tab
3. Look for: "📊 Total records: X"
4. Verify count matches table
```

---

## 🔍 Debugging

### If Still No Records

#### Check 1: Database
```bash
SELECT COUNT(*) FROM reconciliation_results 
WHERE ruleset_id = 'RECON_9240A5F7';
```

#### Check 2: Console Logs
```
F12 → Console → Look for error messages
```

#### Check 3: Backend Logs
```bash
grep "Evidence query" backend.log
grep "Retrieved.*evidence records" backend.log
```

#### Check 4: API Response
```
F12 → Network → Find evidence request
Check response body for errors
```

---

## 📁 Files Modified

| File | Changes |
|------|---------|
| `kg_builder/services/kpi_file_service.py` | Added KPI type filtering in `_query_evidence_data()` method |
| `web-app/src/pages/KPIResults.js` | Enhanced logging, error messages, and KPI context display |

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

## 🎯 Evidence Dialog Features

### Information Box
- Shows KPI Type
- Shows Ruleset ID

### Filters
- **Filter by Status**: Dropdown with all status options
- **Limit**: Input field for number of records
- **Refresh**: Button to reload with new filters

### Evidence Table
- **Record ID**: Unique identifier
- **Status**: Color-coded chip (green=matched, orange=inactive, red=unmatched)
- **Rule**: Rule name that matched
- **Data**: JSON preview of source/target data

### No Records Message
Shows diagnostic information when no records found

---

## ✨ Summary

✅ **KPI type filtering** - Evidence now shows relevant records
✅ **Enhanced logging** - Detailed console logs for debugging
✅ **Better error messages** - Diagnostic info when no records
✅ **KPI context** - Shows KPI type and ruleset in dialog
✅ **User filters** - Can filter by status and limit
✅ **Pagination** - Can refresh with different limits

---

## 🚀 Next Steps

1. **Start Backend**
   ```bash
   python -m kg_builder.main
   ```

2. **Start Frontend**
   ```bash
   cd web-app && npm start
   ```

3. **Test Evidence**
   - Go to KPI Management
   - Create a KPI
   - Execute it
   - Go to KPI Results
   - Click "View Evidence"
   - Records should appear!

4. **Check Console**
   - Open DevTools (F12)
   - Go to Console tab
   - Verify logs show records loaded

---

## 📚 Related Documentation

- **KPI_EVIDENCE_QUICK_FIX.md** - Quick reference
- **KPI_EVIDENCE_TROUBLESHOOTING.md** - Detailed troubleshooting
- **KPI_EXECUTE_BUTTON_ADDED.md** - Execute button documentation
- **WHEN_KPI_GETS_EXECUTED.md** - KPI execution details

---

Now evidence records should display properly! 🎉


