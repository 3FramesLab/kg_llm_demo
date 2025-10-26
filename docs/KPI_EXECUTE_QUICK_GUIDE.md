# KPI Execute Button - Quick Guide 🚀

## What's New?

**Execute button** is now available in KPI Management page!

---

## 🎯 How to Execute a KPI

### Step 1: Go to KPI Management
```
Sidebar → KPI Management
```

### Step 2: Find Your KPI
Look for the KPI in the table

### Step 3: Click Execute Button
```
Actions Column → Green "Execute" Button
```

### Step 4: View Results
Result dialog appears with:
- ✅ Calculated value
- ✅ Status (OK/WARNING/CRITICAL)
- ✅ Execution timestamp
- ✅ Result ID
- ✅ Metrics
- ✅ Thresholds

---

## 📊 KPI Management Page Layout

```
┌─────────────────────────────────────────────────────────────┐
│ KPI Management                                              │
├─────────────────────────────────────────────────────────────┤
│ Filter: [Ruleset Dropdown]  [Create KPI Button]            │
├─────────────────────────────────────────────────────────────┤
│ KPI Name │ Type │ Ruleset │ Warning │ Critical │ Status │ Actions │
├─────────────────────────────────────────────────────────────┤
│ Match    │ %    │ RECON   │ 80      │ 70       │ OK     │ [Execute] [Edit] [Delete] │
│ Rate     │      │ 9240A5F7│         │          │        │                           │
├─────────────────────────────────────────────────────────────┤
│ Quality  │ %    │ RECON   │ 85      │ 75       │ OK     │ [Execute] [Edit] [Delete] │
│ Score    │      │ 9240A5F7│         │          │        │                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Execute Button

### Normal State
```
[▶ Execute]  (Green button)
```

### Executing State
```
[⏳ Executing...]  (Disabled, shows progress)
```

### After Execution
```
Result Dialog Opens ↓
```

---

## 📋 Result Dialog

```
┌──────────────────────────────────────────┐
│ KPI Execution Result                     │
├──────────────────────────────────────────┤
│ KPI Name                                 │
│ Material Match Rate                      │
│                                          │
│ Calculated Value                         │
│ 95.5                                     │
│                                          │
│ Status                                   │
│ OK  (Green)                              │
│                                          │
│ Execution Timestamp                      │
│ 10/26/2025, 12:59:45 PM                 │
│                                          │
│ Result ID                                │
│ 550e8400-e29b-41d4-a716-446655440000   │
│                                          │
│ Metrics                                  │
│ {                                        │
│   "matched_count": 955,                  │
│   "total_source_count": 1000             │
│ }                                        │
│                                          │
│ Thresholds                               │
│ Warning: 80 | Critical: 70               │
├──────────────────────────────────────────┤
│                              [Close]     │
└──────────────────────────────────────────┘
```

---

## 🎯 Status Colors

| Status | Color | Meaning |
|--------|-------|---------|
| OK | 🟢 Green | Value is good |
| WARNING | 🟠 Orange | Value is concerning |
| CRITICAL | 🔴 Red | Value is critical |

---

## 📊 Example Execution

### Before Execution
```
KPI: Material Match Rate
Status: Enabled
Thresholds: Warning 80%, Critical 70%
```

### Click Execute
```
Button shows: "Executing..."
Button is disabled
```

### After Execution
```
Dialog shows:
  Calculated Value: 95.5%
  Status: OK (Green)
  Timestamp: 10/26/2025, 12:59:45 PM
  Result ID: 550e8400-e29b-41d4-a716-446655440000
```

---

## 🔄 What Happens Behind the Scenes

```
1. Click Execute Button
   ↓
2. Frontend sends: POST /v1/reconciliation/kpi/{kpi_id}/execute
   ↓
3. Backend:
   - Loads KPI definition
   - Queries reconciliation data
   - Calculates KPI value
   - Compares against thresholds
   - Saves result to file
   ↓
4. Frontend receives result
   ↓
5. Shows result in dialog
```

---

## 💡 Tips

1. **Execute anytime** - No restrictions on when to execute
2. **Multiple executions** - Execute same KPI multiple times
3. **Each execution** - Creates new result with timestamp
4. **View history** - Go to KPI Results page to see all results
5. **Check metrics** - Expand metrics section to see details

---

## 🚀 Quick Workflow

```
1. Create KPI
   ↓
2. Click Execute
   ↓
3. View Result
   ↓
4. Check Status
   ↓
5. Go to KPI Results to see history
```

---

## ❓ FAQ

**Q: Can I execute multiple KPIs at once?**
A: Not from UI yet. Use batch API endpoint for that.

**Q: Where are results stored?**
A: In `data/kpi/results/` as JSON files.

**Q: Can I delete results?**
A: Yes, go to KPI Results page.

**Q: What if execution fails?**
A: Error message appears. Check console for details.

**Q: How often can I execute?**
A: As often as you want!

---

## 🎉 That's It!

Execute KPIs directly from the UI now! 🚀


