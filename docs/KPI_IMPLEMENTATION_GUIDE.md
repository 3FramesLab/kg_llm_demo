# KPI Implementation Guide

## Quick Reference

### 3 Strategic KPIs for Data Quality & Reconciliation Monitoring

| KPI | Purpose | Formula | Target | Frequency |
|-----|---------|---------|--------|-----------|
| **RCR** | Coverage | (Matched/Total)×100 | ≥90% | Real-time |
| **DQCS** | Quality | Σ(matches×score)/Σmatches | ≥0.80 | Hourly |
| **REI** | Efficiency | (Success×Util×Speed)/100 | ≥40 | 6-hourly |

---

## 📊 KPI 1: Reconciliation Coverage Rate (RCR)

### What It Measures
Percentage of source records successfully matched to target records.

### Why It Matters
- Identifies data gaps
- Tracks reconciliation completeness
- Enables SLA monitoring
- Supports compliance

### Calculation
```
RCR = (Matched Records / Total Source Records) × 100

Example:
- Matched: 1,247
- Total: 1,300
- RCR = 95.92%
```

### Automation
- **Trigger**: After each execution
- **Data Source**: Execution results + source schema
- **Storage**: `kpi_reconciliation_coverage` collection
- **Alert**: If RCR < 90%

### MongoDB Schema
```json
{
  "kpi_type": "RECONCILIATION_COVERAGE_RATE",
  "ruleset_id": "RECON_23B2B063",
  "timestamp": "2025-10-23T14:30:22Z",
  "metrics": {
    "matched_records": 1247,
    "total_source_records": 1300,
    "coverage_rate": 95.92
  },
  "data_lineage": {
    "source_kg": "Test_New_321",
    "source_schemas": ["orderMgmt-catalog", "qinspect-designcode"]
  }
}
```

---

## 📊 KPI 2: Data Quality Confidence Score (DQCS)

### What It Measures
Weighted average confidence of all matched records.

### Why It Matters
- Measures data reliability
- Identifies high-quality rules
- Supports decision-making
- Enables quality-based filtering

### Calculation
```
DQCS = Σ(matched_count × confidence_score) / Σ matched_count

Example:
- Rule 1: 500 matches × 0.95 = 475
- Rule 2: 400 matches × 0.85 = 340
- Rule 3: 347 matches × 0.75 = 260.25
- DQCS = 1,075.25 / 1,247 = 0.862 (86.2%)
```

### Automation
- **Trigger**: After each execution
- **Data Source**: Matched records + rule confidence
- **Storage**: `kpi_data_quality_confidence` collection
- **Alert**: If DQCS < 0.80

### MongoDB Schema
```json
{
  "kpi_type": "DATA_QUALITY_CONFIDENCE_SCORE",
  "ruleset_id": "RECON_23B2B063",
  "timestamp": "2025-10-23T14:30:22Z",
  "metrics": {
    "overall_confidence_score": 0.862,
    "total_matched_records": 1247,
    "high_confidence_matches": 1100
  },
  "rule_quality_breakdown": [
    {
      "rule_id": "RULE_57DFE374",
      "matched_count": 500,
      "confidence_score": 0.95
    }
  ]
}
```

---

## 📊 KPI 3: Reconciliation Efficiency Index (REI)

### What It Measures
Combined score of match success, rule utilization, and execution speed.

### Why It Matters
- Identifies performance bottlenecks
- Optimizes resource utilization
- Predicts system capacity
- Supports cost optimization

### Calculation
```
REI = (Match Success Rate × Rule Utilization × Speed Factor) / 100

Where:
- Match Success Rate = (Matched / Total) × 100
- Rule Utilization = (Active Rules / Total Rules) × 100
- Speed Factor = (Target Time / Actual Time) × 100

Example:
- Success Rate: 95.92%
- Rule Utilization: 81.82%
- Speed Factor: 52%
- REI = (95.92 × 81.82 × 52) / 100 = 40.8
```

### Automation
- **Trigger**: After each execution
- **Data Source**: Execution metrics + performance data
- **Storage**: `kpi_reconciliation_efficiency` collection
- **Alert**: If REI < 30

### MongoDB Schema
```json
{
  "kpi_type": "RECONCILIATION_EFFICIENCY_INDEX",
  "ruleset_id": "RECON_23B2B063",
  "timestamp": "2025-10-23T14:30:22Z",
  "metrics": {
    "efficiency_index": 40.8,
    "match_success_rate": 95.92,
    "rule_utilization": 81.82,
    "speed_factor": 52.0
  },
  "performance_details": {
    "total_records_processed": 1300,
    "execution_time_ms": 2500,
    "records_per_second": 520
  }
}
```

---

## 🗄️ MongoDB Collections

### Collection 1: kpi_reconciliation_coverage
- **Purpose**: Store RCR metrics
- **Indexes**: ruleset_id, timestamp, coverage_rate
- **Retention**: 30 days (real-time), 90 days (hourly), 1 year (daily)

### Collection 2: kpi_data_quality_confidence
- **Purpose**: Store DQCS metrics
- **Indexes**: ruleset_id, timestamp, overall_confidence_score
- **Retention**: 30 days (real-time), 90 days (hourly), 1 year (daily)

### Collection 3: kpi_reconciliation_efficiency
- **Purpose**: Store REI metrics
- **Indexes**: ruleset_id, timestamp, efficiency_index
- **Retention**: 30 days (real-time), 90 days (6-hourly), 1 year (daily)

### Collection 4: kpi_knowledge_graph_metadata
- **Purpose**: Store KG metadata for lineage
- **Indexes**: kg_name, created_at, relationships_detected
- **Retention**: Permanent (reference data)

### Collection 5: kpi_ruleset_relationships
- **Purpose**: Store ruleset-relationship mappings
- **Indexes**: ruleset_id, source_kg, confidence
- **Retention**: Permanent (reference data)

---

## 🔗 Data Lineage Mapping

### RCR Lineage
```
Source Schemas (1,300 records)
    ↓
Knowledge Graph (22 relationships)
    ↓
Ruleset (22 rules)
    ↓
Execution (1,247 matched)
    ↓
RCR = 95.92%
```

### DQCS Lineage
```
Ruleset Rules (confidence scores)
    ↓
Matched Records (1,247 total)
    ↓
Weighted Average Calculation
    ↓
DQCS = 86.2%
```

### REI Lineage
```
Execution Metrics (time, records, rules)
    ↓
Performance Factors (success, utilization, speed)
    ↓
Combined Calculation
    ↓
REI = 40.8
```

---

## 🚨 Alert Configuration

### RCR Alerts
```
CRITICAL: RCR < 80%  → Immediate escalation
WARNING:  RCR < 90%  → Daily review
HEALTHY:  RCR ≥ 90%  → Normal operation
```

### DQCS Alerts
```
CRITICAL: DQCS < 0.70  → Immediate escalation
WARNING:  DQCS < 0.80  → Daily review
HEALTHY:  DQCS ≥ 0.80  → Normal operation
```

### REI Alerts
```
CRITICAL: REI < 20   → Immediate escalation
WARNING:  REI < 30   → Daily review
ACCEPTABLE: 30-40    → Monitor
GOOD: 40-50          → Normal
EXCELLENT: > 50      → Optimal
```

---

## 📈 Monitoring Dashboard

### Real-time Metrics
- Current RCR, DQCS, REI values
- Status indicators (HEALTHY/WARNING/CRITICAL)
- Trend arrows (UP/DOWN/STABLE)

### Historical Trends
- 24-hour trend charts
- 7-day comparison
- 30-day trend analysis

### Breakdown Views
- RCR by ruleset
- DQCS by rule quality
- REI by performance factor

### Alerts & Notifications
- Real-time alerts
- Email notifications
- Slack integration

---

## 🔧 Implementation Checklist

- [ ] Create MongoDB collections
- [ ] Create indexes on collections
- [ ] Implement RCR calculation logic
- [ ] Implement DQCS calculation logic
- [ ] Implement REI calculation logic
- [ ] Setup event-based triggers
- [ ] Setup scheduled jobs
- [ ] Configure alert thresholds
- [ ] Create dashboard
- [ ] Setup notifications
- [ ] Test with sample data
- [ ] Deploy to production
- [ ] Monitor for 1 week
- [ ] Adjust thresholds based on data

---

## 📚 Related Documents

- **KPI_DESIGN_AND_ANALYSIS.md** - Detailed KPI specifications
- **MONGODB_RECONCILIATION_GUIDE.md** - MongoDB setup guide
- **RECONCILIATION_EXECUTION_GUIDE.md** - Execution details

---

**Version**: 1.0
**Last Updated**: 2025-10-23
**Status**: Ready for Implementation

