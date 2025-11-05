# End-to-End Test - Technical Specification

## 📋 Document Overview

This document provides technical details about the end-to-end reconciliation test script implementation.

**Script**: `test_end_to_end_reconciliation.py`
**Location**: `d:\learning\dq-poc/`
**Language**: Python 3.8+
**Lines of Code**: ~600

---

## 🏗️ Architecture

### Module Structure

```
test_end_to_end_reconciliation.py
├── Imports & Configuration
├── Logging Setup
├── Step 1: Schema Loading
├── Step 2: KG Creation
├── Step 3: Relationship Generation (LLM)
├── Step 4: Rules Generation (LLM)
├── Step 5: Database Connection
├── Step 6: Rule Execution
├── Step 7: KPI Calculation
├── Summary Report Generation
└── Main Execution
```

### Dependencies

```python
# Core
import os, sys, json, logging, time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Project
from kg_builder.services.schema_parser import SchemaParser
from kg_builder.services.reconciliation_service import get_reconciliation_service
from kg_builder.services.reconciliation_executor import get_reconciliation_executor
from kg_builder.services.kpi_service import KPIService
from kg_builder.services.mongodb_storage import get_mongodb_storage
from kg_builder.models import DatabaseConnectionInfo
from kg_builder.config import (
    SOURCE_DB_TYPE, SOURCE_DB_HOST, SOURCE_DB_PORT, SOURCE_DB_DATABASE,
    SOURCE_DB_USERNAME, SOURCE_DB_PASSWORD, SOURCE_DB_SERVICE_NAME,
    TARGET_DB_TYPE, TARGET_DB_HOST, TARGET_DB_PORT, TARGET_DB_DATABASE,
    TARGET_DB_USERNAME, TARGET_DB_PASSWORD, TARGET_DB_SERVICE_NAME
)
```

---

## 🔄 Workflow Implementation

### Step 1: Schema Loading

**Function**: `load_schemas(schema_dir: str = "schemas")`

**Implementation**:
```python
1. Scan schemas/ directory for *.json files
2. Extract schema names from filenames
3. Load each schema using SchemaParser.load_schema()
4. Validate schema structure
5. Return list of schema names and loaded schemas
```

**Error Handling**:
- FileNotFoundError: If schemas/ directory doesn't exist
- FileNotFoundError: If no JSON files found
- Exception: If schema loading fails

**Logging**:
- Schema count
- Schema names
- Table count per schema
- Success/failure status

---

### Step 2: Knowledge Graph Creation

**Function**: `create_knowledge_graph(schema_names: List[str], kg_name: str)`

**Implementation**:
```python
1. Always use SchemaParser.build_merged_knowledge_graph() (UNIFIED APPROACH)
2. Single schema is just a special case of multiple schemas (count = 1)
3. Extract nodes and relationships
4. Return KG metadata
```

**Data Structures**:
```python
{
    "kg_name": str,
    "nodes_count": int,
    "relationships_count": int,
    "kg_object": KnowledgeGraph
}
```

**Logging**:
- KG name
- Node count
- Relationship count

---

### Step 3: Relationship Generation (LLM)

**Function**: `generate_relationships_with_llm(kg_data, schema_names)`

**Implementation**:
```python
1. Check if multiple schemas
2. If yes: rebuild KG with use_llm=True
3. LLM analyzes schemas for semantic relationships
4. Adds new relationships to KG
5. Return updated KG metadata
```

**LLM Configuration**:
- Model: gpt-3.5-turbo
- Temperature: 0.7
- Max tokens: 2000

**Logging**:
- Initial relationship count
- New relationships added
- Total relationships after LLM

---

### Step 4: Reconciliation Rules Generation (LLM)

**Function**: `generate_reconciliation_rules(kg_data, schema_names)`

**Implementation**:
```python
1. Get reconciliation service
2. Call generate_from_knowledge_graph()
3. LLM generates semantic rules
4. Filter by confidence >= 0.7
5. Deduplicate rules
6. Return ruleset metadata
```

**Rule Generation Process**:
```
KG Relationships
    ↓
Pattern-based rules (basic)
    ↓
LLM-based rules (semantic)
    ↓
Merge and deduplicate
    ↓
Filter by confidence
    ↓
ReconciliationRuleSet
```

**Logging**:
- Ruleset ID
- Ruleset name
- Total rules
- First 5 rules with confidence scores

---

### Step 5: Database Connection Verification

**Function**: `verify_database_connections()`

**Implementation**:
```python
1. Read database config from environment
2. Create DatabaseConnectionInfo objects
3. Log connection details
4. Return source and target configs
```

**Configuration Source**: `.env` file

**Logging**:
- Source DB type, host, port, database, user
- Target DB type, host, port, database, user

---

### Step 6: Rule Execution

**Function**: `execute_reconciliation_rules(ruleset_data, source_config, target_config, limit)`

**Implementation**:
```python
1. Get reconciliation executor
2. Call execute_ruleset()
3. Executor connects to databases
4. Executes each rule
5. Collects matched/unmatched records
6. Stores results in MongoDB
7. Return execution metadata
```

**Execution Process**:
```
Ruleset
    ↓
For each rule:
  - Execute matched query
  - Execute unmatched source query
  - Execute unmatched target query
    ↓
Aggregate results
    ↓
Store in MongoDB
    ↓
Return execution response
```

**Logging**:
- Execution ID
- Matched count
- Unmatched source count
- Unmatched target count
- Total source count
- Coverage rate
- Execution time
- MongoDB document ID

---

### Step 7: KPI Calculation

**Function**: `calculate_kpis(execution_data, ruleset_data, schema_names)`

**Implementation**:
```python
1. Initialize KPI service
2. Ensure MongoDB indexes
3. Calculate RCR: (matched / total) × 100
4. Calculate DQCS: mean(confidence_scores)
5. Calculate REI: (success × util × speed) / 10000
6. Store each KPI in MongoDB
7. Return KPI metadata
```

**KPI Formulas**:

**RCR**:
```
RCR = (Matched Records / Total Source Records) × 100
Status: HEALTHY (≥90%), WARNING (≥80%), CRITICAL (<80%)
```

**DQCS**:
```
DQCS = mean(confidence_scores)
Status: EXCELLENT (≥0.9), GOOD (≥0.8), ACCEPTABLE (≥0.7), POOR (<0.7)
```

**REI**:
```
REI = (Success Rate × Rule Utilization × Speed Factor) / 10000
Status: EXCELLENT (≥50), GOOD (≥40), ACCEPTABLE (≥30), WARNING (≥20), CRITICAL (<20)
```

**Logging**:
- RCR value, status, MongoDB ID
- DQCS value, status, MongoDB ID
- REI value, status, MongoDB ID

---

## 📊 Data Flow

```
Schemas (JSON files)
    ↓
SchemaParser.load_schema()
    ↓
DatabaseSchema objects
    ↓
SchemaParser.build_merged_knowledge_graph()
    ↓
KnowledgeGraph (nodes + relationships)
    ↓
LLM Enhancement (relationships)
    ↓
Enhanced KnowledgeGraph
    ↓
ReconciliationService.generate_from_knowledge_graph()
    ↓
ReconciliationRuleSet
    ↓
ReconciliationExecutor.execute_ruleset()
    ↓
Execution Results (matched/unmatched)
    ↓
KPIService.calculate_*()
    ↓
KPI Documents
    ↓
MongoDB Storage
```

---

## 🔐 Error Handling

### Try-Catch Blocks

Each step wrapped in try-except:

```python
try:
    # Step implementation
    logger.info("Step completed")
    return result
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    raise
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    raise
```

### Error Propagation

- Errors logged with full stack trace
- Execution stops at first error
- Main function catches and returns exit code 1

---

## 📝 Logging Implementation

### Logger Setup

```python
def setup_logging(log_file: str = "e2e_reconciliation.log"):
    logger = logging.getLogger("E2E_Reconciliation")
    logger.setLevel(logging.INFO)
    
    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger
```

### Log Output

- **File**: `e2e_reconciliation.log` (appended)
- **Console**: Real-time output
- **Format**: `YYYY-MM-DD HH:MM:SS - E2E_Reconciliation - LEVEL - Message`

---

## 🔄 Idempotency

### Design Principles

1. **Unique KG Names**: Each execution creates new KG with timestamp
   ```python
   kg_name = f"kg_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
   ```

2. **New Rulesets**: Each execution generates new ruleset
   ```python
   ruleset_id = f"RECON_{generate_uid()}"
   ```

3. **New Executions**: Each execution creates new execution record
   ```python
   execution_id = f"EXEC_{generate_uid()}"
   ```

4. **Append-Only Logs**: Log file appended, not overwritten
   ```python
   fh = logging.FileHandler(log_file)  # Appends by default
   ```

5. **New Reports**: Each execution creates new report file
   ```python
   report_file = f"e2e_reconciliation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
   ```

### Safe to Run Multiple Times

- No data deleted
- No data overwritten
- Full history maintained
- Each run independent

---

## 📊 Output Formats

### Log File Format

```
2025-10-23 14:30:45 - E2E_Reconciliation - INFO - ================================================================================
2025-10-23 14:30:45 - E2E_Reconciliation - INFO - STEP 1: SCHEMA LOADING
2025-10-23 14:30:45 - E2E_Reconciliation - INFO - ================================================================================
```

### Report File Format

```
================================================================================
END-TO-END RECONCILIATION WORKFLOW - SUMMARY REPORT
================================================================================

Execution Timestamp: 2025-10-23 14:30:45
Total Execution Time: 45.23 seconds

================================================================================
1. SCHEMA LOADING
================================================================================
   Schemas Processed: 2
   Schema Names: orderMgmt-catalog, qinspect-designcode
```

### MongoDB Document Format

```json
{
  "_id": ObjectId("..."),
  "kpi_type": "RECONCILIATION_COVERAGE_RATE",
  "ruleset_id": "RECON_ABC123",
  "ruleset_name": "Reconciliation_kg_20251023_143045",
  "execution_id": "EXEC_001",
  "timestamp": ISODate("2025-10-23T14:30:45Z"),
  "metrics": {
    "coverage_rate": 95.92,
    "matched_records": 1247,
    "total_source_records": 1300
  },
  "status": "HEALTHY"
}
```

---

## 🎯 Exit Codes

- **0**: Success - all steps completed
- **1**: Failure - error occurred, check logs

---

## 📚 Related Files

- `test_end_to_end_reconciliation.py` - Main script
- `docs/E2E_TEST_GUIDE.md` - Comprehensive guide
- `E2E_TEST_QUICK_START.md` - Quick start
- `e2e_reconciliation.log` - Execution log
- `e2e_reconciliation_report_*.txt` - Summary report

---

**Version**: 1.0
**Date**: 2025-10-23
**Status**: Complete

