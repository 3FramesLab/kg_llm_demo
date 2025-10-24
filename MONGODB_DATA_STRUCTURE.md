# MongoDB Data Structure - Complete Reference

## 📊 Overview

MongoDB stores reconciliation results and KPIs in the `reconciliation` database with multiple collections:

1. **reconciliation_results** - Main reconciliation execution results
2. **kpi_reconciliation_coverage** - RCR (Reconciliation Coverage Rate) metrics
3. **kpi_data_quality_confidence** - DQCS (Data Quality Confidence Score) metrics
4. **kpi_reconciliation_efficiency** - REI (Reconciliation Efficiency Index) metrics
5. **kpi_knowledge_graph_metadata** - Knowledge graph metadata
6. **kpi_ruleset_relationships** - Ruleset and KG relationships

---

## 1️⃣ Reconciliation Results Collection

**Collection Name**: `reconciliation_results`

### Document Structure

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "ruleset_id": "RECON_07C55A55",
  "execution_timestamp": ISODate("2025-10-24T00:48:35.780Z"),
  "matched_count": 0,
  "unmatched_source_count": 100,
  "unmatched_target_count": 1900,
  "matched_records": [
    {
      "source_record": { "id": 1, "name": "Product A", "code": "PA001" },
      "target_record": { "id": 101, "name": "Product A", "code": "PA001" },
      "match_confidence": 0.95,
      "rule_used": "RULE_001",
      "rule_name": "Name_Match_catalog_id"
    }
  ],
  "unmatched_source": [
    {
      "id": 2,
      "name": "Product B",
      "code": "PB001",
      "rule_id": "RULE_001",
      "rule_name": "Name_Match_catalog_id"
    }
  ],
  "unmatched_target": [
    {
      "id": 102,
      "name": "Product C",
      "code": "PC001",
      "rule_id": "RULE_001",
      "rule_name": "Name_Match_catalog_id"
    }
  ],
  "metadata": {
    "execution_time_ms": 16210,
    "limit": 100,
    "source_db_type": "mysql",
    "target_db_type": "mysql",
    "include_matched": true,
    "include_unmatched": true
  }
}
```

### Fields Description

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | MongoDB unique identifier |
| `ruleset_id` | String | ID of the ruleset executed (e.g., RECON_07C55A55) |
| `execution_timestamp` | Date | When the reconciliation was executed |
| `matched_count` | Integer | Number of matched records |
| `unmatched_source_count` | Integer | Number of unmatched source records |
| `unmatched_target_count` | Integer | Number of unmatched target records |
| `matched_records` | Array | List of matched record pairs |
| `unmatched_source` | Array | Source records with no match in target |
| `unmatched_target` | Array | Target records with no match in source |
| `metadata` | Object | Execution metadata (time, DB types, etc.) |

---

## 2️⃣ RCR (Reconciliation Coverage Rate) Collection

**Collection Name**: `kpi_reconciliation_coverage`

### Document Structure

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439012"),
  "kpi_type": "RECONCILIATION_COVERAGE_RATE",
  "ruleset_id": "RECON_07C55A55",
  "ruleset_name": "Reconciliation_kg_20251024_005324",
  "execution_id": "EXEC_20251024_005324",
  "timestamp": ISODate("2025-10-24T00:48:35.778Z"),
  "period": "execution",
  "metrics": {
    "matched_records": 0,
    "unmatched_source": 100,
    "total_source_records": 100,
    "coverage_rate": 0.0,
    "coverage_percentage": 0.0
  },
  "breakdown_by_rule": [
    {
      "rule_id": "RULE_001",
      "rule_name": "Name_Match_catalog_id",
      "matched": 0,
      "coverage": 0.0
    }
  ],
  "thresholds": {
    "warning_level": 90,
    "critical_level": 80,
    "status": "CRITICAL"
  },
  "data_lineage": {
    "source_kg": "kg_20251024_005324",
    "source_schemas": ["orderMgmt-catalog", "qinspect-designcode"],
    "generated_from_kg": "kg_20251024_005324"
  },
  "created_at": ISODate("2025-10-24T00:48:35.778Z"),
  "updated_at": ISODate("2025-10-24T00:48:35.778Z")
}
```

### Status Levels

- **HEALTHY**: Coverage ≥ 90%
- **WARNING**: Coverage 80-89%
- **CRITICAL**: Coverage < 80%

---

## 3️⃣ DQCS (Data Quality Confidence Score) Collection

**Collection Name**: `kpi_data_quality_confidence`

### Document Structure

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439013"),
  "kpi_type": "DATA_QUALITY_CONFIDENCE_SCORE",
  "ruleset_id": "RECON_07C55A55",
  "ruleset_name": "Reconciliation_kg_20251024_005324",
  "execution_id": "EXEC_20251024_005324",
  "timestamp": ISODate("2025-10-24T00:48:35.779Z"),
  "period": "execution",
  "metrics": {
    "overall_confidence_score": 0.0,
    "confidence_percentage": 0.0,
    "total_matched_records": 0,
    "high_confidence_matches": 0,
    "medium_confidence_matches": 0,
    "low_confidence_matches": 0
  },
  "quality_breakdown": [
    {
      "rule_id": "RULE_001",
      "rule_name": "Name_Match_catalog_id",
      "avg_confidence": 0.75,
      "matched_count": 0
    }
  ],
  "thresholds": {
    "good_level": 0.8,
    "acceptable_level": 0.7,
    "status": "POOR"
  },
  "data_lineage": {
    "source_kg": "kg_20251024_005324",
    "source_schemas": ["orderMgmt-catalog", "qinspect-designcode"]
  },
  "created_at": ISODate("2025-10-24T00:48:35.779Z"),
  "updated_at": ISODate("2025-10-24T00:48:35.779Z")
}
```

### Status Levels

- **GOOD**: Score ≥ 0.8
- **ACCEPTABLE**: Score 0.7-0.79
- **POOR**: Score < 0.7

---

## 4️⃣ REI (Reconciliation Efficiency Index) Collection

**Collection Name**: `kpi_reconciliation_efficiency`

### Document Structure

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439014"),
  "kpi_type": "RECONCILIATION_EFFICIENCY_INDEX",
  "ruleset_id": "RECON_07C55A55",
  "ruleset_name": "Reconciliation_kg_20251024_005324",
  "execution_id": "EXEC_20251024_005324",
  "timestamp": ISODate("2025-10-24T00:48:35.780Z"),
  "period": "execution",
  "metrics": {
    "efficiency_index": 0.0,
    "execution_time_ms": 16210,
    "records_processed": 100,
    "throughput_records_per_sec": 6.17,
    "success_rate": 100.0
  },
  "efficiency_breakdown": {
    "success_factor": 1.0,
    "utilization_factor": 0.5,
    "speed_factor": 0.5
  },
  "data_lineage": {
    "source_kg": "kg_20251024_005324",
    "source_schemas": ["orderMgmt-catalog", "qinspect-designcode"]
  },
  "created_at": ISODate("2025-10-24T00:48:35.780Z"),
  "updated_at": ISODate("2025-10-24T00:48:35.780Z")
}
```

---

## 📑 MongoDB Indexes

The following indexes are automatically created for performance:

### RCR Collection
```
- ruleset_id (ascending), timestamp (descending)
- metrics.coverage_rate (ascending)
```

### DQCS Collection
```
- ruleset_id (ascending), timestamp (descending)
- metrics.overall_confidence_score (ascending)
```

### REI Collection
```
- ruleset_id (ascending), timestamp (descending)
- metrics.efficiency_index (ascending)
```

---

## 🔍 Query Examples

### Get Latest RCR for a Ruleset
```javascript
db.kpi_reconciliation_coverage.findOne(
  { ruleset_id: "RECON_07C55A55" },
  { sort: { timestamp: -1 } }
)
```

### Get All Reconciliation Results
```javascript
db.reconciliation_results.find({ ruleset_id: "RECON_07C55A55" })
```

### Get DQCS Metrics
```javascript
db.kpi_data_quality_confidence.findOne(
  { ruleset_id: "RECON_07C55A55" },
  { sort: { timestamp: -1 } }
)
```

---

## 📊 Data Flow

```
Reconciliation Execution
    ↓
Matched/Unmatched Records
    ↓
MongoDB Storage (reconciliation_results)
    ↓
KPI Calculation
    ├→ RCR (kpi_reconciliation_coverage)
    ├→ DQCS (kpi_data_quality_confidence)
    └→ REI (kpi_reconciliation_efficiency)
```

---

## 💾 Storage Size Estimation

For 100 records per execution:
- **reconciliation_results**: ~50-100 KB per document
- **KPI documents**: ~5-10 KB each (3 documents per execution)
- **Total per execution**: ~70-130 KB

---

**Version**: 1.0  
**Date**: 2025-10-24  
**Status**: ✅ Complete

