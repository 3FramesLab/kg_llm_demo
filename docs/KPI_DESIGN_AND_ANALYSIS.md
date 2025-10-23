# KPI Design and Analysis: Data Quality & Reconciliation Effectiveness

## Executive Summary

This document presents **3 strategic KPIs** designed to monitor data quality and reconciliation effectiveness in the DQ-POC system. These KPIs provide actionable insights into:

1. **Reconciliation Coverage Rate (RCR)** - Measures how much data is successfully matched
2. **Data Quality Confidence Score (DQCS)** - Measures overall quality of matched data
3. **Reconciliation Efficiency Index (REI)** - Measures system performance and rule effectiveness

---

## 🎯 KPI 1: Reconciliation Coverage Rate (RCR)

### Definition
**Reconciliation Coverage Rate** measures the percentage of source records that have been successfully matched to target records through active reconciliation rules.

### Why It Matters
- **Business Impact**: Identifies data gaps and unmatched records that need manual intervention
- **Quality Assurance**: High coverage indicates comprehensive data alignment
- **Risk Indicator**: Low coverage suggests missing rules or data quality issues
- **Compliance**: Ensures all critical data is accounted for

### Calculation Formula
```
RCR = (Matched Records / Total Source Records) × 100

Where:
- Matched Records = Sum of matched_count across all rule executions
- Total Source Records = Count of all records in source schema
```

### Example Calculation
```
Matched Records: 1,247
Total Source Records: 1,300
RCR = (1,247 / 1,300) × 100 = 95.92%
```

### Automation Design

#### Trigger
- **Event-based**: When reconciliation execution completes
- **Scheduled**: Daily at 2 AM (off-peak hours)
- **Manual**: On-demand via API endpoint

#### Data Sources
- Reconciliation execution results (MongoDB)
- Source schema metadata
- Ruleset definitions

#### Calculation Process
```
1. Fetch latest execution results for ruleset
2. Sum matched_count from all rules
3. Query source database for total record count
4. Calculate: RCR = (matched / total) × 100
5. Store result in MongoDB KPI collection
6. Trigger alerts if RCR < threshold (e.g., 90%)
```

#### Update Frequency
- **Real-time**: Immediately after execution
- **Aggregated**: Hourly summary
- **Historical**: Daily trend analysis

---

## 🎯 KPI 2: Data Quality Confidence Score (DQCS)

### Definition
**Data Quality Confidence Score** is a weighted average of confidence scores from all matched records, reflecting the overall quality and reliability of the reconciliation.

### Why It Matters
- **Trust Indicator**: Shows how confident the system is in the matches
- **Rule Quality**: Identifies which rules produce high-quality matches
- **Trend Analysis**: Tracks improvement/degradation over time
- **Decision Support**: Helps prioritize which data to use

### Calculation Formula
```
DQCS = (Σ(matched_count × confidence_score) / Σ matched_count)

Where:
- confidence_score = Rule's confidence score (0.0-1.0)
- matched_count = Number of records matched by that rule
- Weighted average across all rules
```

### Example Calculation
```
Rule 1: 500 matches × 0.95 confidence = 475
Rule 2: 400 matches × 0.85 confidence = 340
Rule 3: 347 matches × 0.75 confidence = 260.25

DQCS = (475 + 340 + 260.25) / (500 + 400 + 347)
     = 1,075.25 / 1,247
     = 0.862 (86.2%)
```

### Automation Design

#### Trigger
- **Event-based**: After each rule execution
- **Scheduled**: Hourly aggregation
- **Real-time**: Streaming calculation

#### Data Sources
- Matched records from execution results
- Rule confidence scores from ruleset
- Historical DQCS values

#### Calculation Process
```
1. Fetch execution results with matched records
2. For each matched record, get rule confidence
3. Calculate weighted average
4. Compare with previous DQCS
5. Calculate trend (improving/degrading)
6. Store in MongoDB with trend metadata
7. Alert if DQCS drops > 5% from baseline
```

#### Update Frequency
- **Real-time**: Per execution
- **Aggregated**: Hourly rolling average
- **Trend**: Daily comparison

---

## 🎯 KPI 3: Reconciliation Efficiency Index (REI)

### Definition
**Reconciliation Efficiency Index** measures how effectively the system processes data, combining execution speed, rule utilization, and match success rate.

### Why It Matters
- **Performance**: Identifies bottlenecks in reconciliation process
- **Resource Optimization**: Shows which rules are most efficient
- **Scalability**: Helps predict system capacity
- **Cost Efficiency**: Correlates with infrastructure costs

### Calculation Formula
```
REI = (Match Success Rate × Rule Utilization × Speed Factor) / 100

Where:
- Match Success Rate = (Matched / Total) × 100
- Rule Utilization = (Active Rules / Total Rules) × 100
- Speed Factor = (Target Time / Actual Time) × 100
  (Target Time = 1000ms per 1000 records)
```

### Example Calculation
```
Match Success Rate = (1,247 / 1,300) × 100 = 95.92%
Rule Utilization = (18 / 22) × 100 = 81.82%
Execution Time = 2,500ms for 1,300 records
Speed Factor = (1,300ms / 2,500ms) × 100 = 52%

REI = (95.92 × 81.82 × 52) / 100 = 40.8
```

### Automation Design

#### Trigger
- **Event-based**: After execution completes
- **Scheduled**: Every 6 hours
- **Continuous**: Real-time monitoring

#### Data Sources
- Execution results (matched/unmatched counts)
- Ruleset metadata (active rules)
- Performance metrics (execution time)
- Historical baseline data

#### Calculation Process
```
1. Get execution metrics (time, matches, rules used)
2. Calculate match success rate
3. Calculate rule utilization
4. Calculate speed factor
5. Combine into REI score
6. Compare with baseline
7. Store with performance breakdown
8. Alert if REI < 30 (poor efficiency)
```

#### Update Frequency
- **Real-time**: Per execution
- **Aggregated**: 6-hourly summary
- **Baseline**: Weekly recalibration

---

## 📊 MongoDB Storage Schemas

### Collection 1: kpi_reconciliation_coverage

```json
{
  "_id": ObjectId,
  "kpi_type": "RECONCILIATION_COVERAGE_RATE",
  "ruleset_id": "RECON_23B2B063",
  "ruleset_name": "Reconciliation_Test_New_321",
  "execution_id": "EXEC_20251023_143022",
  "timestamp": "2025-10-23T14:30:22Z",
  "period": "daily",
  "metrics": {
    "matched_records": 1247,
    "unmatched_source": 53,
    "total_source_records": 1300,
    "coverage_rate": 95.92,
    "coverage_percentage": 95.92
  },
  "breakdown_by_rule": [
    {
      "rule_id": "RULE_57DFE374",
      "rule_name": "Brand_UID_Match",
      "matched_count": 1200,
      "coverage_contribution": 96.25
    }
  ],
  "thresholds": {
    "warning_level": 90,
    "critical_level": 80,
    "status": "HEALTHY"
  },
  "trend": {
    "previous_value": 94.5,
    "change_percentage": 1.42,
    "direction": "UP"
  },
  "data_lineage": {
    "source_kg": "Test_New_321",
    "source_schemas": ["orderMgmt-catalog", "qinspect-designcode"],
    "generated_from_kg": "Test_New_321"
  },
  "created_at": "2025-10-23T14:30:22Z",
  "updated_at": "2025-10-23T14:30:22Z"
}
```

### Collection 2: kpi_data_quality_confidence

```json
{
  "_id": ObjectId,
  "kpi_type": "DATA_QUALITY_CONFIDENCE_SCORE",
  "ruleset_id": "RECON_23B2B063",
  "ruleset_name": "Reconciliation_Test_New_321",
  "execution_id": "EXEC_20251023_143022",
  "timestamp": "2025-10-23T14:30:22Z",
  "period": "hourly",
  "metrics": {
    "overall_confidence_score": 0.862,
    "confidence_percentage": 86.2,
    "total_matched_records": 1247,
    "high_confidence_matches": 1100,
    "medium_confidence_matches": 120,
    "low_confidence_matches": 27
  },
  "confidence_distribution": {
    "0.9_to_1.0": 850,
    "0.8_to_0.9": 250,
    "0.7_to_0.8": 120,
    "below_0.7": 27
  },
  "rule_quality_breakdown": [
    {
      "rule_id": "RULE_57DFE374",
      "rule_name": "Brand_UID_Match",
      "matched_count": 500,
      "confidence_score": 0.95,
      "weighted_contribution": 0.381
    },
    {
      "rule_id": "RULE_538D152A",
      "rule_name": "Product_Type_Match",
      "matched_count": 400,
      "confidence_score": 0.85,
      "weighted_contribution": 0.272
    }
  ],
  "quality_assessment": {
    "llm_generated_rules": {
      "count": 3,
      "avg_confidence": 0.883
    },
    "name_similarity_rules": {
      "count": 19,
      "avg_confidence": 0.75
    }
  },
  "thresholds": {
    "excellent": 0.9,
    "good": 0.8,
    "acceptable": 0.7,
    "current_status": "GOOD"
  },
  "trend": {
    "previous_score": 0.845,
    "change": 0.017,
    "direction": "UP"
  },
  "data_lineage": {
    "source_kg": "Test_New_321",
    "relationships_used": 22,
    "high_confidence_relationships": 18
  },
  "created_at": "2025-10-23T14:30:22Z",
  "updated_at": "2025-10-23T14:30:22Z"
}
```

### Collection 3: kpi_reconciliation_efficiency

```json
{
  "_id": ObjectId,
  "kpi_type": "RECONCILIATION_EFFICIENCY_INDEX",
  "ruleset_id": "RECON_23B2B063",
  "ruleset_name": "Reconciliation_Test_New_321",
  "execution_id": "EXEC_20251023_143022",
  "timestamp": "2025-10-23T14:30:22Z",
  "period": "6hourly",
  "metrics": {
    "efficiency_index": 40.8,
    "match_success_rate": 95.92,
    "rule_utilization": 81.82,
    "speed_factor": 52.0
  },
  "performance_details": {
    "total_records_processed": 1300,
    "execution_time_ms": 2500,
    "records_per_second": 520,
    "target_time_ms": 1300,
    "actual_time_ms": 2500,
    "time_efficiency": 52.0
  },
  "rule_efficiency": {
    "total_rules": 22,
    "active_rules": 18,
    "rules_with_matches": 18,
    "avg_matches_per_rule": 69.28,
    "most_efficient_rule": {
      "rule_id": "RULE_57DFE374",
      "rule_name": "Brand_UID_Match",
      "matches": 500,
      "efficiency_score": 0.95
    }
  },
  "resource_utilization": {
    "cpu_usage_percent": 45,
    "memory_usage_mb": 256,
    "database_query_time_ms": 1200,
    "network_latency_ms": 50
  },
  "efficiency_assessment": {
    "status": "ACCEPTABLE",
    "bottleneck": "database_queries",
    "optimization_potential": "HIGH"
  },
  "thresholds": {
    "excellent": 50,
    "good": 40,
    "acceptable": 30,
    "poor": 20,
    "current_status": "ACCEPTABLE"
  },
  "trend": {
    "previous_index": 38.5,
    "change": 2.3,
    "direction": "UP"
  },
  "data_lineage": {
    "source_kg": "Test_New_321",
    "ruleset_version": 1,
    "schema_count": 2
  },
  "created_at": "2025-10-23T14:30:22Z",
  "updated_at": "2025-10-23T14:30:22Z"
}
```

### Collection 4: kpi_knowledge_graph_metadata

```json
{
  "_id": ObjectId,
  "kg_name": "Test_New_321",
  "kg_id": "KG_20251023_081717",
  "created_at": "2025-10-23T08:17:17Z",
  "schemas": [
    {
      "schema_name": "orderMgmt-catalog",
      "table_count": 1,
      "column_count": 15,
      "record_count": 1300,
      "tables": [
        {
          "table_name": "catalog",
          "columns": ["id", "code", "sub_cat_uid", "tenant_uid", "brand_uid", "subbrand_uid", "designer_code", "fabric_code", "collection_uid", "brand_id", "product_id", "parent_tenant_uid", "subseason_uid", "product_type", "color"]
        }
      ]
    },
    {
      "schema_name": "qinspect-designcode",
      "table_count": 1,
      "column_count": 14,
      "record_count": 1280,
      "tables": [
        {
          "table_name": "design_code_master",
          "columns": ["id", "code", "sub_category_uid", "parent_tenant_uid", "brand_uid", "sub_brand_uid", "design_code", "fabric_code", "collection_uid", "tenant_uid", "product_type_uid", "product_code", "product_uid", "product_type_name", "color"]
        }
      ]
    }
  ],
  "relationships_detected": 22,
  "high_confidence_relationships": 18,
  "relationship_types": {
    "exact_match": 19,
    "semantic_match": 3
  },
  "entities": {
    "total_count": 29,
    "by_type": {
      "table": 2,
      "column": 27
    }
  },
  "quality_metrics": {
    "schema_coverage": 100,
    "relationship_density": 0.76,
    "avg_relationship_confidence": 0.82
  }
}
```

### Collection 5: kpi_ruleset_relationships

```json
{
  "_id": ObjectId,
  "ruleset_id": "RECON_23B2B063",
  "ruleset_name": "Reconciliation_Test_New_321",
  "source_kg": "Test_New_321",
  "relationships": [
    {
      "relationship_id": "REL_001",
      "source_entity": "orderMgmt-catalog.catalog.brand_uid",
      "target_entity": "qinspect-designcode.design_code_master.brand_uid",
      "relationship_type": "EXACT_MATCH",
      "confidence": 0.9,
      "rule_id": "RULE_57DFE374",
      "rule_name": "Brand_UID_Match",
      "match_count": 500,
      "validation_status": "VALID",
      "llm_generated": true,
      "reasoning": "Both fields are UIDs representing brands"
    },
    {
      "relationship_id": "REL_002",
      "source_entity": "orderMgmt-catalog.catalog.product_type",
      "target_entity": "qinspect-designcode.design_code_master.product_type_name",
      "relationship_type": "SEMANTIC_MATCH",
      "confidence": 0.8,
      "rule_id": "RULE_538D152A",
      "rule_name": "Product_Type_Match",
      "match_count": 400,
      "validation_status": "VALID",
      "llm_generated": true,
      "reasoning": "Matching product types between catalog and design code master"
    }
  ],
  "relationship_summary": {
    "total_relationships": 22,
    "by_confidence": {
      "high": 18,
      "medium": 3,
      "low": 1
    },
    "by_type": {
      "exact": 19,
      "semantic": 3
    }
  },
  "created_at": "2025-10-23T08:17:17Z",
  "updated_at": "2025-10-23T14:30:22Z"
}
```

---

## 📈 Data Flow Diagrams

### KPI Calculation Flow

```
Source Schemas          Knowledge Graph         Ruleset
    │                        │                      │
    ├─────────────────────────┼──────────────────────┤
    │                         │                      │
    ▼                         ▼                      ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ orderMgmt    │      │ Test_New_321 │      │ RECON_23B2B0 │
│ qinspect     │      │ (22 rels)    │      │ (22 rules)   │
└──────┬───────┘      └──────┬───────┘      └──────┬───────┘
       │                     │                     │
       └─────────────────────┼─────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Reconciliation  │
                    │ Execution       │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    ┌────────┐          ┌────────┐          ┌────────┐
    │ RCR    │          │ DQCS   │          │ REI    │
    │ 95.92% │          │ 86.2%  │          │ 40.8   │
    └────┬───┘          └────┬───┘          └────┬───┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ MongoDB KPI     │
                    │ Collections     │
                    └─────────────────┘
```

### Data Lineage for Each KPI

```
KPI 1: Reconciliation Coverage Rate
├── Source: Execution Results (matched_count, unmatched_count)
├── Depends on: Source schema record count
├── Links to: Ruleset → Knowledge Graph → Relationships
└── Output: Coverage percentage, trend, status

KPI 2: Data Quality Confidence Score
├── Source: Matched records with confidence scores
├── Depends on: Rule confidence scores
├── Links to: Ruleset → Rules → LLM Enhancement
└── Output: Weighted confidence, distribution, quality assessment

KPI 3: Reconciliation Efficiency Index
├── Source: Execution metrics (time, records, rules)
├── Depends on: Performance baseline, rule utilization
├── Links to: Ruleset → Execution → Resource metrics
└── Output: Efficiency score, bottleneck analysis, optimization potential
```

---

## 🔗 Data Lineage Details

### KPI 1: RCR Data Lineage

```
Knowledge Graph (Test_New_321)
    ├── Entities: 29 (2 tables, 27 columns)
    ├── Relationships: 22 detected
    └── High-confidence: 18
         │
         ▼
    Ruleset (RECON_23B2B063)
    ├── Rules: 22 total
    ├── LLM-generated: 3 (high confidence)
    └── Name-similarity: 19 (medium confidence)
         │
         ▼
    Execution Results
    ├── Matched: 1,247 records
    ├── Unmatched Source: 53 records
    └── Total Source: 1,300 records
         │
         ▼
    RCR Calculation
    └── Coverage: 95.92%
```

### KPI 2: DQCS Data Lineage

```
Ruleset Rules
├── Rule 1: Brand_UID_Match (confidence: 0.9, matches: 500)
├── Rule 2: Product_Type_Match (confidence: 0.8, matches: 400)
└── Rule 3: Color_Match (confidence: 0.75, matches: 347)
     │
     ▼
Matched Records
├── High confidence (0.9-1.0): 850 records
├── Medium confidence (0.8-0.9): 250 records
└── Low confidence (0.7-0.8): 147 records
     │
     ▼
DQCS Calculation
└── Weighted Average: 86.2%
```

### KPI 3: REI Data Lineage

```
Execution Metrics
├── Records processed: 1,300
├── Execution time: 2,500ms
├── Rules used: 18 of 22
└── Matches: 1,247
     │
     ▼
Performance Factors
├── Match Success Rate: 95.92%
├── Rule Utilization: 81.82%
└── Speed Factor: 52%
     │
     ▼
REI Calculation
└── Efficiency Index: 40.8
```

---

## 🏗️ MongoDB Indexing Strategy

### Collection: kpi_reconciliation_coverage
```javascript
db.kpi_reconciliation_coverage.createIndex({ ruleset_id: 1, timestamp: -1 })
db.kpi_reconciliation_coverage.createIndex({ "metrics.coverage_rate": 1 })
db.kpi_reconciliation_coverage.createIndex({ timestamp: -1 })
db.kpi_reconciliation_coverage.createIndex({ "data_lineage.source_kg": 1 })
```

### Collection: kpi_data_quality_confidence
```javascript
db.kpi_data_quality_confidence.createIndex({ ruleset_id: 1, timestamp: -1 })
db.kpi_data_quality_confidence.createIndex({ "metrics.overall_confidence_score": 1 })
db.kpi_data_quality_confidence.createIndex({ timestamp: -1 })
db.kpi_data_quality_confidence.createIndex({ "rule_quality_breakdown.rule_id": 1 })
```

### Collection: kpi_reconciliation_efficiency
```javascript
db.kpi_reconciliation_efficiency.createIndex({ ruleset_id: 1, timestamp: -1 })
db.kpi_reconciliation_efficiency.createIndex({ "metrics.efficiency_index": 1 })
db.kpi_reconciliation_efficiency.createIndex({ timestamp: -1 })
db.kpi_reconciliation_efficiency.createIndex({ "performance_details.execution_time_ms": 1 })
```

### Collection: kpi_knowledge_graph_metadata
```javascript
db.kpi_knowledge_graph_metadata.createIndex({ kg_name: 1 })
db.kpi_knowledge_graph_metadata.createIndex({ created_at: -1 })
db.kpi_knowledge_graph_metadata.createIndex({ "relationships_detected": 1 })
```

### Collection: kpi_ruleset_relationships
```javascript
db.kpi_ruleset_relationships.createIndex({ ruleset_id: 1 })
db.kpi_ruleset_relationships.createIndex({ source_kg: 1 })
db.kpi_ruleset_relationships.createIndex({ "relationships.confidence": 1 })
db.kpi_ruleset_relationships.createIndex({ "relationships.rule_id": 1 })
```

---

## 💡 Benefits and Use Cases

### KPI 1: Reconciliation Coverage Rate

**Benefits**:
- Identifies data gaps requiring attention
- Tracks reconciliation completeness
- Enables SLA monitoring
- Supports compliance reporting

**Use Cases**:
1. **Daily Monitoring**: Track coverage trends
2. **Incident Response**: Alert when coverage drops below 90%
3. **Capacity Planning**: Identify schemas needing more rules
4. **Audit Trail**: Historical coverage records

### KPI 2: Data Quality Confidence Score

**Benefits**:
- Measures data reliability
- Identifies high-quality rules
- Supports decision-making
- Enables quality-based filtering

**Use Cases**:
1. **Quality Assurance**: Validate matched data quality
2. **Rule Optimization**: Identify underperforming rules
3. **Risk Assessment**: Flag low-confidence matches
4. **Trend Analysis**: Monitor quality improvements

### KPI 3: Reconciliation Efficiency Index

**Benefits**:
- Identifies performance bottlenecks
- Optimizes resource utilization
- Predicts system capacity
- Supports cost optimization

**Use Cases**:
1. **Performance Tuning**: Identify slow rules
2. **Capacity Planning**: Predict scalability needs
3. **Cost Analysis**: Correlate efficiency with infrastructure costs
4. **Optimization**: Prioritize rule improvements

---

## 🔧 Implementation Considerations

### Automation Triggers

| KPI | Trigger Type | Frequency | Latency |
|-----|--------------|-----------|---------|
| RCR | Event-based | Per execution | Real-time |
| RCR | Scheduled | Daily 2 AM | 24 hours |
| DQCS | Event-based | Per execution | Real-time |
| DQCS | Scheduled | Hourly | 1 hour |
| REI | Event-based | Per execution | Real-time |
| REI | Scheduled | Every 6 hours | 6 hours |

### Data Retention Policy

```
- Real-time KPI data: 30 days
- Hourly aggregates: 90 days
- Daily summaries: 1 year
- Monthly reports: 3 years
- Archived data: S3/cold storage
```

### Alert Thresholds

```
RCR:
- Critical: < 80%
- Warning: < 90%
- Healthy: >= 90%

DQCS:
- Critical: < 0.70
- Warning: < 0.80
- Healthy: >= 0.80

REI:
- Critical: < 20
- Warning: < 30
- Acceptable: 30-40
- Good: 40-50
- Excellent: > 50
```

---

## 📋 Summary Table

| KPI | Metric | Formula | Frequency | Alert |
|-----|--------|---------|-----------|-------|
| **RCR** | Coverage % | (Matched/Total)×100 | Real-time | <90% |
| **DQCS** | Confidence | Σ(matches×score)/Σmatches | Hourly | <0.80 |
| **REI** | Efficiency | (Success×Util×Speed)/100 | 6-hourly | <30 |

---

**Document Version**: 1.0
**Last Updated**: 2025-10-23
**Status**: Ready for Implementation

