# KPI Execution Flow - How KPIs Are Calculated

## 🎯 Quick Answer

**NO SQL is NOT executed by the KPI service itself.**

The KPI service receives **pre-calculated data** from the reconciliation execution and performs **in-memory calculations** only.

---

## 📊 KPI Execution Flow

### Step 1: Reconciliation Execution Completes
```
Reconciliation Engine
    ↓
Executes reconciliation rules
    ↓
Produces results:
  - matched_count: 1247
  - total_source_count: 1300
  - matched_records: [...]
  - execution_time_ms: 2500
```

### Step 2: KPI Calculation Triggered
```
POST /kpi/calculate
    ↓
KPICalculationRequest received with:
  - execution_id
  - ruleset_id
  - matched_count
  - total_source_count
  - matched_records (with confidence scores)
  - active_rules
  - total_rules
  - execution_time_ms
```

### Step 3: In-Memory Calculations
```
KPIService.calculate_rcr()
  ↓
  Formula: (matched_count / total_source_count) × 100
  ↓
  Result: 95.92%

KPIService.calculate_dqcs()
  ↓
  Formula: Σ(confidence_scores) / count
  ↓
  Result: 0.862

KPIService.calculate_rei()
  ↓
  Formula: (success × utilization × speed) / 10000
  ↓
  Result: 40.8
```

### Step 4: Store in MongoDB
```
KPI Documents stored in:
  - kpi_reconciliation_coverage
  - kpi_data_quality_confidence
  - kpi_reconciliation_efficiency
```

---

## 🔍 Where Does Data Come From?

### Data Source: Reconciliation Execution Results

The KPI service **does NOT query databases**. Instead, it receives data from:

1. **Reconciliation Execution Engine**
   - Executes reconciliation rules
   - Produces matched/unmatched records
   - Calculates execution time
   - Returns results to caller

2. **API Request Body**
   - Caller passes all necessary data
   - No database queries needed
   - All data is in-memory

### Example Request
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
    {"match_confidence": 0.95, "rule_used": "RULE_57DFE374"},
    {"match_confidence": 0.85, "rule_used": "RULE_538D152A"},
    ...
  ],
  "active_rules": 18,
  "total_rules": 22,
  "execution_time_ms": 2500
}
```

---

## 💻 KPI Calculation Details

### RCR Calculation (No SQL)
```python
def calculate_rcr(matched_count, total_source_count):
    # Pure Python calculation
    if total_source_count == 0:
        coverage_rate = 0.0
    else:
        coverage_rate = (matched_count / total_source_count) * 100
    
    # Determine status
    if coverage_rate >= 90:
        status = "HEALTHY"
    elif coverage_rate >= 80:
        status = "WARNING"
    else:
        status = "CRITICAL"
    
    return coverage_rate, status
```

**Data Flow**:
```
Input: matched_count=1247, total_source_count=1300
  ↓
Calculation: (1247 / 1300) × 100 = 95.92%
  ↓
Status: HEALTHY (≥90%)
  ↓
Output: KPI Document
```

### DQCS Calculation (No SQL)
```python
def calculate_dqcs(matched_records):
    # Extract confidence scores from records
    confidence_scores = [
        record.get('match_confidence', 0.0)
        for record in matched_records
    ]
    
    # Calculate average
    overall_score = mean(confidence_scores)
    
    # Count by confidence level
    high_confidence = sum(1 for s in confidence_scores if s >= 0.9)
    medium_confidence = sum(1 for s in confidence_scores if 0.8 <= s < 0.9)
    low_confidence = sum(1 for s in confidence_scores if s < 0.8)
    
    return overall_score, high_confidence, medium_confidence, low_confidence
```

**Data Flow**:
```
Input: matched_records = [
  {"match_confidence": 0.95},
  {"match_confidence": 0.85},
  {"match_confidence": 0.75},
  ...
]
  ↓
Extract scores: [0.95, 0.85, 0.75, ...]
  ↓
Calculate mean: 0.862
  ↓
Count levels: high=850, medium=250, low=147
  ↓
Output: KPI Document
```

### REI Calculation (No SQL)
```python
def calculate_rei(matched_count, total_source_count, active_rules, 
                  total_rules, execution_time_ms):
    # Calculate components
    match_success_rate = (matched_count / total_source_count * 100)
    rule_utilization = (active_rules / total_rules * 100)
    
    # Speed factor: target is 1000ms per 1000 records
    target_time_ms = (total_source_count / 1000) * 1000
    speed_factor = (target_time_ms / execution_time_ms * 100)
    
    # Calculate efficiency
    efficiency_index = (match_success_rate * rule_utilization * speed_factor) / 10000
    
    return efficiency_index
```

**Data Flow**:
```
Input:
  - matched_count: 1247
  - total_source_count: 1300
  - active_rules: 18
  - total_rules: 22
  - execution_time_ms: 2500
  ↓
Calculate:
  - match_success_rate: 95.92%
  - rule_utilization: 81.82%
  - speed_factor: 52%
  ↓
Efficiency: (95.92 × 81.82 × 52) / 10000 = 40.8
  ↓
Output: KPI Document
```

---

## 🗄️ MongoDB Operations (Not SQL)

KPI service uses **MongoDB** (NoSQL), not SQL:

### 1. Create Indexes
```python
# MongoDB index creation (not SQL)
rcr_col.create_index([('ruleset_id', 1), ('timestamp', -1)])
rcr_col.create_index([('metrics.coverage_rate', 1)])
```

### 2. Store KPI
```python
# MongoDB insert (not SQL)
collection.insert_one(kpi_doc)
```

### 3. Retrieve KPI
```python
# MongoDB query (not SQL)
collection.find_one(
    {"kpi_type": kpi_type, "ruleset_id": ruleset_id},
    sort=[("timestamp", -1)]
)
```

---

## 🔄 Complete Execution Sequence

```
1. Reconciliation Execution
   ├─ Load source data
   ├─ Load target data
   ├─ Apply reconciliation rules
   ├─ Generate matched records
   └─ Return results

2. KPI Calculation Request
   ├─ POST /kpi/calculate
   ├─ Pass execution results
   └─ No database queries

3. KPI Service Processing
   ├─ Calculate RCR (in-memory)
   ├─ Calculate DQCS (in-memory)
   ├─ Calculate REI (in-memory)
   └─ Create KPI documents

4. MongoDB Storage
   ├─ Store RCR document
   ├─ Store DQCS document
   ├─ Store REI document
   └─ Return KPI IDs

5. Response
   ├─ Return KPI values
   ├─ Return KPI IDs
   └─ Return status
```

---

## ⚡ Performance Characteristics

### No SQL Queries
- ✅ No database round trips during calculation
- ✅ All calculations in-memory
- ✅ Fast execution (milliseconds)

### MongoDB Operations Only
- ✅ Index creation (one-time)
- ✅ Document insertion (one per KPI)
- ✅ Document retrieval (one query per KPI type)

### Data Size
- ✅ Matched records passed in request
- ✅ No large data transfers
- ✅ Efficient memory usage

---

## 📝 Example: Complete KPI Execution

### Request
```bash
curl -X POST http://localhost:8000/kpi/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "execution_id": "EXEC_001",
    "ruleset_id": "RECON_23B2B063",
    "matched_count": 1247,
    "total_source_count": 1300,
    "matched_records": [...],
    "active_rules": 18,
    "total_rules": 22,
    "execution_time_ms": 2500
  }'
```

### Processing (All In-Memory)
```
1. RCR = (1247 / 1300) × 100 = 95.92%
2. DQCS = mean([0.95, 0.85, 0.75, ...]) = 0.862
3. REI = (95.92 × 81.82 × 52) / 10000 = 40.8
```

### Storage (MongoDB)
```
Insert into kpi_reconciliation_coverage
Insert into kpi_data_quality_confidence
Insert into kpi_reconciliation_efficiency
```

### Response
```json
{
  "success": true,
  "rcr_id": "507f1f77bcf86cd799439011",
  "dqcs_id": "507f1f77bcf86cd799439012",
  "rei_id": "507f1f77bcf86cd799439013",
  "rcr_value": 95.92,
  "dqcs_value": 0.862,
  "rei_value": 40.8
}
```

---

## 🎯 Key Takeaways

1. **No SQL Execution**
   - KPI service does NOT run SQL queries
   - All calculations are in-memory Python code

2. **Data Source**
   - Data comes from reconciliation execution results
   - Passed via API request body
   - No database queries needed

3. **Storage Only**
   - MongoDB is used only for storing KPI results
   - Not for calculating KPIs

4. **Performance**
   - Fast in-memory calculations
   - Minimal database operations
   - Efficient resource usage

---

## 🔗 Related Documentation

- `docs/KPI_DESIGN_AND_ANALYSIS.md` - Detailed KPI specifications
- `docs/KPI_IMPLEMENTATION_GUIDE.md` - Implementation details
- `kg_builder/services/kpi_service.py` - Source code

---

**Version**: 1.0
**Date**: 2025-10-23
**Status**: Complete

