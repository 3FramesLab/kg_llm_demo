# KPI Evidence Not Showing - Quick Fix ✅

## Problem
"View Evidence" button in KPI Results shows no records.

## Solution
Fixed backend evidence query to properly filter by KPI type.

---

## 🚀 Quick Test

### Step 1: Create & Execute KPI
```bash
# 1. Go to KPI Management
# 2. Create a KPI (e.g., "Match Rate")
# 3. Click Execute button
# 4. Wait for completion
```

### Step 2: View Evidence
```bash
# 1. Go to KPI Results
# 2. Click "View Evidence" button
# 3. Records should now appear!
```

### Step 3: Check Console
```bash
# Open DevTools (F12) → Console
# Look for: "📊 Total records: X"
```

---

## 🔧 What Was Fixed

### Backend
```python
# BEFORE: No filtering by KPI type
SELECT * FROM reconciliation_results WHERE ruleset_id = ?

# AFTER: Filter by KPI type
if kpi_type == "match_rate":
    # Show all records
elif kpi_type == "unmatched_source_count":
    query += " AND match_status = 'unmatched_source'"
elif kpi_type == "inactive_record_count":
    query += " AND match_status = 'inactive'"
# etc...
```

### Frontend
- ✅ Added detailed console logging
- ✅ Shows KPI type and ruleset in dialog
- ✅ Better "no records" message with diagnostics

---

## 📊 Evidence Filtering by KPI Type

| KPI Type | Filter Applied |
|----------|----------------|
| match_rate | All records |
| match_percentage | All records |
| unmatched_source_count | match_status = 'unmatched_source' |
| unmatched_target_count | match_status = 'unmatched_target' |
| inactive_record_count | match_status = 'inactive' |
| data_quality_score | match_status = 'matched' |

---

## 🔍 Troubleshooting

### Still No Records?

#### Check 1: Reconciliation Data
```bash
# Query database directly
SELECT COUNT(*) FROM reconciliation_results 
WHERE ruleset_id = 'YOUR_RULESET_ID';
```

#### Check 2: Browser Console
```
F12 → Console → Look for error messages
```

#### Check 3: Backend Logs
```bash
grep "Evidence query" backend.log
```

#### Check 4: KPI Type
Make sure KPI type matches the data you expect.

---

## 📋 Evidence Dialog

### Shows
- KPI Type
- Ruleset ID
- Filter by Status dropdown
- Limit input
- Refresh button
- Evidence table with:
  - Record ID
  - Status (color-coded)
  - Rule Name
  - Data preview

### Filters
- **Status**: All, Matched, Unmatched Source, Unmatched Target, Inactive
- **Limit**: Number of records (default: 100)

---

## 🎯 Console Logs

### Success
```
📊 Loading evidence for KPI: KPI_001
📡 Evidence API Response Status: 200 OK
✅ Evidence response: {...}
📊 Total records: 50
```

### No Records
```
⚠️ No evidence records found for this KPI
```

### Error
```
❌ Exception: Error: HTTP 500
```

---

## 📁 Files Modified

- `kg_builder/services/kpi_file_service.py` - Backend filtering
- `web-app/src/pages/KPIResults.js` - Frontend logging

---

## ✨ Summary

✅ Evidence query now filters by KPI type
✅ Better logging for debugging
✅ Improved error messages
✅ Diagnostic info when no records

**Test it now!** 🎉


