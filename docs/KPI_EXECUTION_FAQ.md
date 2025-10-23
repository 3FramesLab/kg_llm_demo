# KPI Execution - Frequently Asked Questions

## ❓ Q1: Does KPI Execution Run SQL?

**A: NO. KPI execution does NOT run SQL queries.**

The KPI service performs **in-memory calculations** only. It receives pre-calculated data from the reconciliation execution and computes the three KPIs using Python formulas.

---

## ❓ Q2: Where Does KPI Data Come From?

**A: From Reconciliation Execution Results**

The data comes from the reconciliation engine after it completes:

```
Reconciliation Engine
    ↓
Produces Results:
  - matched_count: 1247
  - total_source_count: 1300
  - matched_records: [...]
  - execution_time_ms: 2500
    ↓
Passed to KPI Service
    ↓
KPI Calculations (In-Memory)
```

---

## ❓ Q3: What Data Does KPI Service Receive?

**A: Complete Reconciliation Results**

```json
{
  "execution_id": "EXEC_001",
  "ruleset_id": "RECON_23B2B063",
  "matched_count": 1247,
  "total_source_count": 1300,
  "matched_records": [
    {"match_confidence": 0.95},
    {"match_confidence": 0.85},
    ...
  ],
  "active_rules": 18,
  "total_rules": 22,
  "execution_time_ms": 2500
}
```

All data is passed in the API request body. No database queries needed.

---

## ❓ Q4: How Are KPIs Calculated?

**A: Using Simple Mathematical Formulas**

### RCR (Reconciliation Coverage Rate)
```
Formula: (Matched Records / Total Source Records) × 100
Example: (1247 / 1300) × 100 = 95.92%
```

### DQCS (Data Quality Confidence Score)
```
Formula: Average of all confidence scores
Example: mean([0.95, 0.85, 0.75, ...]) = 0.862
```

### REI (Reconciliation Efficiency Index)
```
Formula: (Success Rate × Rule Utilization × Speed Factor) / 10000
Example: (95.92 × 81.82 × 52) / 10000 = 40.8
```

All calculations are done in Python, in-memory.

---

## ❓ Q5: Does KPI Service Query MongoDB?

**A: Only for Storage and Retrieval**

MongoDB is used for:
- ✅ Storing KPI results (insert)
- ✅ Retrieving latest KPIs (query)
- ✅ Creating indexes (one-time)

MongoDB is **NOT** used for KPI calculations.

---

## ❓ Q6: What's the Performance Impact?

**A: Minimal - Very Fast**

```
Reconciliation Execution: ~2500ms
KPI Calculation: ~10-50ms (in-memory)
MongoDB Storage: ~5-20ms
Total Overhead: ~50-100ms
```

KPI calculation adds minimal overhead because:
- ✅ No database queries
- ✅ All calculations in-memory
- ✅ Simple mathematical operations
- ✅ Small data size

---

## ❓ Q7: Can KPIs Be Calculated Without Reconciliation?

**A: No - KPIs Depend on Reconciliation Results**

KPIs require:
- Matched record count
- Total source record count
- Matched records with confidence scores
- Execution time
- Rule utilization metrics

All of these come from reconciliation execution.

---

## ❓ Q8: What If Reconciliation Fails?

**A: KPI Calculation Cannot Proceed**

If reconciliation fails:
- ❌ No matched records
- ❌ No execution time
- ❌ No confidence scores
- ❌ Cannot calculate KPIs

KPI service requires complete reconciliation results.

---

## ❓ Q9: How Are Confidence Scores Generated?

**A: By Reconciliation Rules**

Each reconciliation rule generates a confidence score:

```
Rule Type → Confidence Score
├─ Exact Match → 0.95-1.0
├─ Semantic Match → 0.80-0.95
├─ Fuzzy Match → 0.70-0.85
└─ Pattern Match → 0.60-0.80
```

Confidence scores are calculated during reconciliation, not by KPI service.

---

## ❓ Q10: Can KPIs Be Calculated in Batch?

**A: Yes - Call KPI Service Multiple Times**

```python
for execution in executions:
    kpi_request = KPICalculationRequest(
        execution_id=execution.id,
        matched_count=execution.matched_count,
        ...
    )
    kpi_response = calculate_kpis(kpi_request)
```

Each execution produces its own KPIs.

---

## ❓ Q11: Where Are KPIs Stored?

**A: In MongoDB Collections**

```
kpi_reconciliation_coverage
  └─ RCR metrics

kpi_data_quality_confidence
  └─ DQCS metrics

kpi_reconciliation_efficiency
  └─ REI metrics

kpi_knowledge_graph_metadata
  └─ KG lineage

kpi_ruleset_relationships
  └─ Relationships
```

---

## ❓ Q12: How to Retrieve KPIs?

**A: Via API Endpoints**

```bash
# Get latest RCR
GET /kpi/rcr/RECON_23B2B063

# Get latest DQCS
GET /kpi/dqcs/RECON_23B2B063

# Get latest REI
GET /kpi/rei/RECON_23B2B063
```

Or use KPI service directly:

```python
kpi_service = KPIService()
rcr = kpi_service.get_latest_kpi("RECONCILIATION_COVERAGE_RATE", "RECON_23B2B063")
```

---

## ❓ Q13: What's the Data Lineage?

**A: Complete Tracking**

Each KPI document includes:
- ✅ Execution ID
- ✅ Ruleset ID
- ✅ Source KG
- ✅ Source schemas
- ✅ Timestamp
- ✅ Calculation details

Full traceability from KPI back to source.

---

## ❓ Q14: Can KPIs Be Recalculated?

**A: Yes - Recalculate Anytime**

```python
# Get original execution results
execution = get_execution(execution_id)

# Recalculate KPIs
kpi_request = KPICalculationRequest(
    execution_id=execution.id,
    matched_count=execution.matched_count,
    ...
)
kpi_response = calculate_kpis(kpi_request)
```

New KPI documents are created with new timestamps.

---

## ❓ Q15: What If Data Is Missing?

**A: KPI Service Handles Edge Cases**

```python
# Zero division protection
if total_source_count == 0:
    coverage_rate = 0.0

# Empty records handling
if not matched_records:
    overall_score = 0.0

# Zero execution time protection
if execution_time_ms == 0:
    speed_factor = 0
```

All edge cases are handled gracefully.

---

## 📊 Quick Reference

| Question | Answer |
|----------|--------|
| **SQL Queries?** | NO - In-memory only |
| **Data Source?** | Reconciliation results |
| **Storage?** | MongoDB (not for calculation) |
| **Performance?** | ~50-100ms overhead |
| **Dependency?** | Requires reconciliation |
| **Batch Support?** | YES |
| **Recalculation?** | YES |
| **Edge Cases?** | Handled |

---

## 🔗 Related Documentation

- `docs/KPI_EXECUTION_FLOW.md` - Detailed execution flow
- `docs/KPI_DATA_SOURCE_MAPPING.md` - Data source mapping
- `docs/KPI_DESIGN_AND_ANALYSIS.md` - KPI specifications
- `kg_builder/services/kpi_service.py` - Source code

---

## 💡 Key Takeaway

**KPI execution is a lightweight, in-memory calculation process that:**
- ✅ Does NOT run SQL queries
- ✅ Receives data from reconciliation results
- ✅ Performs simple mathematical calculations
- ✅ Stores results in MongoDB
- ✅ Adds minimal performance overhead

---

**Version**: 1.0
**Date**: 2025-10-23
**Status**: Complete

