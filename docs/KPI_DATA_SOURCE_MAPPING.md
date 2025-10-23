# KPI Data Source Mapping

## 📊 Where Does Each KPI Data Come From?

### Overview
KPIs receive data from **reconciliation execution results**, not from SQL queries.

---

## 🔍 Data Source Mapping

### KPI 1: Reconciliation Coverage Rate (RCR)

**Data Required**:
```
- matched_count: int
- total_source_count: int
```

**Where It Comes From**:
```
Reconciliation Execution Results
    ↓
Matched Records Count
    ↓
Total Source Records Count
    ↓
Passed to KPI Service
```

**Example**:
```
matched_count = 1247
total_source_count = 1300
unmatched = 1300 - 1247 = 53

RCR = (1247 / 1300) × 100 = 95.92%
```

**Data Flow**:
```
Reconciliation Engine
    ├─ Loads source data (1300 records)
    ├─ Applies reconciliation rules
    ├─ Produces matched records (1247)
    └─ Returns: matched_count=1247, total_source_count=1300
        ↓
    KPI Service receives data
        ↓
    Calculates RCR = 95.92%
```

---

### KPI 2: Data Quality Confidence Score (DQCS)

**Data Required**:
```
- matched_records: List[Dict]
  - Each record must have: match_confidence (0.0-1.0)
```

**Where It Comes From**:
```
Reconciliation Execution Results
    ↓
Matched Records with Confidence Scores
    ↓
Passed to KPI Service
```

**Example**:
```
matched_records = [
    {"match_confidence": 0.95, "rule_used": "RULE_57DFE374"},
    {"match_confidence": 0.85, "rule_used": "RULE_538D152A"},
    {"match_confidence": 0.75, "rule_used": "RULE_4A051192"},
    ...
]

DQCS = mean([0.95, 0.85, 0.75, ...]) = 0.862
```

**Data Flow**:
```
Reconciliation Engine
    ├─ Applies each reconciliation rule
    ├─ Calculates match confidence for each match
    │  (based on rule type and match quality)
    ├─ Produces matched records with confidence
    └─ Returns: matched_records=[...]
        ↓
    KPI Service receives data
        ↓
    Extracts confidence scores
        ↓
    Calculates DQCS = 0.862
```

**Confidence Score Sources**:
```
Rule Type → Confidence Score
├─ Exact Match → 0.95-1.0
├─ Semantic Match → 0.80-0.95
├─ Fuzzy Match → 0.70-0.85
└─ Pattern Match → 0.60-0.80
```

---

### KPI 3: Reconciliation Efficiency Index (REI)

**Data Required**:
```
- matched_count: int
- total_source_count: int
- active_rules: int (rules that produced matches)
- total_rules: int (total rules in ruleset)
- execution_time_ms: float (milliseconds)
```

**Where It Comes From**:
```
Reconciliation Execution Results
    ├─ Matched count
    ├─ Total source count
    ├─ Active rules count
    ├─ Total rules count
    └─ Execution time
        ↓
    Passed to KPI Service
```

**Example**:
```
matched_count = 1247
total_source_count = 1300
active_rules = 18
total_rules = 22
execution_time_ms = 2500

Components:
- match_success_rate = (1247/1300) × 100 = 95.92%
- rule_utilization = (18/22) × 100 = 81.82%
- target_time = (1300/1000) × 1000 = 1300ms
- speed_factor = (1300/2500) × 100 = 52%

REI = (95.92 × 81.82 × 52) / 10000 = 40.8
```

**Data Flow**:
```
Reconciliation Engine
    ├─ Loads ruleset (22 rules)
    ├─ Applies each rule
    ├─ Tracks which rules produced matches (18)
    ├─ Measures execution time (2500ms)
    └─ Returns: active_rules=18, total_rules=22, execution_time_ms=2500
        ↓
    KPI Service receives data
        ↓
    Calculates efficiency components
        ↓
    Calculates REI = 40.8
```

---

## 📋 KPI Request Structure

### Complete Request Example
```json
{
  "execution_id": "EXEC_20251023_143022",
  "ruleset_id": "RECON_23B2B063",
  "ruleset_name": "Reconciliation_Test_New_321",
  "source_kg": "Test_New_321",
  "source_schemas": ["orderMgmt-catalog", "qinspect-designcode"],
  
  "matched_count": 1247,
  "total_source_count": 1300,
  
  "matched_records": [
    {
      "match_confidence": 0.95,
      "rule_used": "RULE_57DFE374",
      "source_id": "SRC_001",
      "target_id": "TGT_001"
    },
    {
      "match_confidence": 0.85,
      "rule_used": "RULE_538D152A",
      "source_id": "SRC_002",
      "target_id": "TGT_002"
    },
    ...
  ],
  
  "active_rules": 18,
  "total_rules": 22,
  "execution_time_ms": 2500,
  
  "resource_metrics": {
    "memory_used_mb": 256,
    "cpu_percent": 45
  }
}
```

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Reconciliation Execution                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Load Source Data (1300 records)                        │
│  2. Load Target Data                                       │
│  3. Apply Reconciliation Rules (22 rules)                  │
│  4. Generate Matches (1247 records)                        │
│  5. Calculate Confidence Scores                            │
│  6. Track Active Rules (18 rules)                          │
│  7. Measure Execution Time (2500ms)                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Reconciliation Results                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  matched_count: 1247                                       │
│  total_source_count: 1300                                  │
│  matched_records: [...]                                    │
│  active_rules: 18                                          │
│  total_rules: 22                                           │
│  execution_time_ms: 2500                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ KPI Calculation Request                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  POST /kpi/calculate                                       │
│  Content-Type: application/json                            │
│  Body: {all reconciliation results}                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ KPI Service (In-Memory Calculations)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  RCR = (1247 / 1300) × 100 = 95.92%                       │
│  DQCS = mean(confidence_scores) = 0.862                    │
│  REI = (95.92 × 81.82 × 52) / 10000 = 40.8               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ MongoDB Storage                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  kpi_reconciliation_coverage: {RCR document}              │
│  kpi_data_quality_confidence: {DQCS document}             │
│  kpi_reconciliation_efficiency: {REI document}            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ KPI Response                                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  rcr_id: "507f1f77bcf86cd799439011"                       │
│  dqcs_id: "507f1f77bcf86cd799439012"                      │
│  rei_id: "507f1f77bcf86cd799439013"                       │
│  rcr_value: 95.92                                          │
│  dqcs_value: 0.862                                         │
│  rei_value: 40.8                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Points

### No SQL Queries
- ✅ KPI service does NOT query databases
- ✅ All data comes from reconciliation results
- ✅ Data is passed via API request body

### Data Completeness
- ✅ All required data must be in the request
- ✅ No additional data fetching needed
- ✅ Calculations are self-contained

### Performance
- ✅ Fast in-memory calculations
- ✅ No database round trips
- ✅ Minimal latency

### Data Integrity
- ✅ Data comes from trusted reconciliation engine
- ✅ Confidence scores are calculated by rules
- ✅ Execution metrics are measured accurately

---

## 📝 Integration Points

### Where to Call KPI Service

**Option 1: After Reconciliation Execution**
```python
# In reconciliation executor
execution_results = execute_reconciliation(ruleset)

# Call KPI service
kpi_request = KPICalculationRequest(
    execution_id=execution_results.execution_id,
    ruleset_id=execution_results.ruleset_id,
    matched_count=len(execution_results.matched_records),
    total_source_count=execution_results.total_source_count,
    matched_records=execution_results.matched_records,
    active_rules=execution_results.active_rules,
    total_rules=execution_results.total_rules,
    execution_time_ms=execution_results.execution_time_ms
)

kpi_response = calculate_kpis(kpi_request)
```

**Option 2: Via API Endpoint**
```bash
curl -X POST http://localhost:8000/kpi/calculate \
  -H "Content-Type: application/json" \
  -d '{execution_results}'
```

---

## 🔗 Related Documentation

- `docs/KPI_EXECUTION_FLOW.md` - Execution flow details
- `docs/KPI_DESIGN_AND_ANALYSIS.md` - KPI specifications
- `kg_builder/services/kpi_service.py` - Source code

---

**Version**: 1.0
**Date**: 2025-10-23
**Status**: Complete

