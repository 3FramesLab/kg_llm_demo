# MongoDB Quick Reference Guide

## 🗄️ Collections Overview

| Collection | Purpose | Records per Execution |
|-----------|---------|----------------------|
| `reconciliation_results` | Main reconciliation results | 1 document |
| `kpi_reconciliation_coverage` | RCR metrics | 1 document |
| `kpi_data_quality_confidence` | DQCS metrics | 1 document |
| `kpi_reconciliation_efficiency` | REI metrics | 1 document |
| `kpi_knowledge_graph_metadata` | KG metadata | 1 document |
| `kpi_ruleset_relationships` | Ruleset-KG relationships | 1 document |

**Total per execution**: 6 documents

---

## 📋 What Gets Stored

### 1. Reconciliation Results
✅ **Matched Records**
- Source record data
- Target record data
- Match confidence score
- Rule used for matching

✅ **Unmatched Source Records**
- All source records that didn't match
- Rule ID and name
- Full record data

✅ **Unmatched Target Records**
- All target records that didn't match
- Rule ID and name
- Full record data

✅ **Execution Metadata**
- Execution time (milliseconds)
- Record limit
- Source/Target DB types
- Include flags

### 2. RCR (Reconciliation Coverage Rate)
✅ **Metrics**
- Matched records count
- Unmatched source count
- Total source records
- Coverage percentage (0-100%)

✅ **Status**
- HEALTHY (≥90%)
- WARNING (80-89%)
- CRITICAL (<80%)

✅ **Breakdown by Rule**
- Per-rule coverage rates
- Per-rule matched counts

### 3. DQCS (Data Quality Confidence Score)
✅ **Metrics**
- Overall confidence score (0.0-1.0)
- Confidence percentage (0-100%)
- Total matched records
- High confidence matches (≥0.9)
- Medium confidence matches (0.8-0.89)
- Low confidence matches (<0.8)

✅ **Status**
- GOOD (≥0.8)
- ACCEPTABLE (0.7-0.79)
- POOR (<0.7)

✅ **Quality Breakdown**
- Per-rule average confidence
- Per-rule matched counts

### 4. REI (Reconciliation Efficiency Index)
✅ **Metrics**
- Efficiency index (0-100)
- Execution time (milliseconds)
- Records processed
- Throughput (records/second)
- Success rate (%)

✅ **Efficiency Breakdown**
- Success factor (0-1.0)
- Utilization factor (0-1.0)
- Speed factor (0-1.0)

---

## 🔍 Common Queries

### Get Latest Reconciliation Results
```javascript
db.reconciliation_results.findOne(
  { ruleset_id: "RECON_07C55A55" },
  { sort: { execution_timestamp: -1 } }
)
```

### Get All KPIs for a Ruleset
```javascript
db.kpi_reconciliation_coverage.findOne(
  { ruleset_id: "RECON_07C55A55" },
  { sort: { timestamp: -1 } }
)

db.kpi_data_quality_confidence.findOne(
  { ruleset_id: "RECON_07C55A55" },
  { sort: { timestamp: -1 } }
)

db.kpi_reconciliation_efficiency.findOne(
  { ruleset_id: "RECON_07C55A55" },
  { sort: { timestamp: -1 } }
)
```

### Get Matched Records
```javascript
db.reconciliation_results.findOne(
  { ruleset_id: "RECON_07C55A55" }
).matched_records
```

### Get Unmatched Source Records
```javascript
db.reconciliation_results.findOne(
  { ruleset_id: "RECON_07C55A55" }
).unmatched_source
```

### Get Unmatched Target Records
```javascript
db.reconciliation_results.findOne(
  { ruleset_id: "RECON_07C55A55" }
).unmatched_target
```

### Get RCR Status
```javascript
db.kpi_reconciliation_coverage.findOne(
  { ruleset_id: "RECON_07C55A55" },
  { sort: { timestamp: -1 } }
).thresholds.status
```

### Get DQCS Score
```javascript
db.kpi_data_quality_confidence.findOne(
  { ruleset_id: "RECON_07C55A55" },
  { sort: { timestamp: -1 } }
).metrics.overall_confidence_score
```

### Get REI Index
```javascript
db.kpi_reconciliation_efficiency.findOne(
  { ruleset_id: "RECON_07C55A55" },
  { sort: { timestamp: -1 } }
).metrics.efficiency_index
```

---

## 📊 Data Size Estimates

| Item | Size |
|------|------|
| Single matched record | 0.5-1 KB |
| Single unmatched record | 0.3-0.5 KB |
| Reconciliation results doc (100 records) | 50-100 KB |
| Single KPI document | 5-10 KB |
| **Total per execution** | **70-130 KB** |

---

## 🔐 Database Configuration

**Database Name**: `reconciliation`

**Connection String**: `mongodb://localhost:27017/`

**Collections**: 6 (auto-created on first use)

**Indexes**: Auto-created for performance

---

## 📈 Typical Workflow

```
1. Execute Reconciliation Rules
   ↓
2. Store Results in reconciliation_results
   ├─ matched_records
   ├─ unmatched_source
   ├─ unmatched_target
   └─ metadata
   ↓
3. Calculate KPIs
   ├─ RCR → kpi_reconciliation_coverage
   ├─ DQCS → kpi_data_quality_confidence
   └─ REI → kpi_reconciliation_efficiency
   ↓
4. Query Results
   └─ Use MongoDB queries to retrieve data
```

---

## 🎯 Key Metrics at a Glance

| Metric | Formula | Range | Status |
|--------|---------|-------|--------|
| **RCR** | (Matched / Total Source) × 100 | 0-100% | HEALTHY ≥90% |
| **DQCS** | Avg(confidence_scores) | 0.0-1.0 | GOOD ≥0.8 |
| **REI** | (Success × Util × Speed) / 10000 | 0-100 | Higher is better |

---

## 💡 Tips

✅ Use `execution_timestamp` to find recent results  
✅ Use `ruleset_id` to group results by ruleset  
✅ Check `thresholds.status` for quick health assessment  
✅ Use `breakdown_by_rule` to identify problematic rules  
✅ Monitor `metrics.throughput_records_per_sec` for performance  

---

**Version**: 1.0  
**Date**: 2025-10-24  
**Status**: ✅ Complete

