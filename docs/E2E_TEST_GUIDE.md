# End-to-End Reconciliation Test Script Guide

## 📋 Overview

The `test_end_to_end_reconciliation.py` script automates the complete data reconciliation workflow from schema loading through KPI calculation and MongoDB storage.

**File Location**: `d:\learning\dq-poc/test_end_to_end_reconciliation.py`

---

## 🎯 Workflow Steps

### Step 1: Schema Loading
- **What**: Loads JSON schemas from `schemas/` folder
- **Schemas Used**: 
  - `orderMgmt-catalog.json`
  - `qinspect-designcode.json`
- **Output**: Loaded schema objects with table and column information
- **Logging**: Schema count, table count per schema

### Step 2: Knowledge Graph Creation
- **What**: Creates a unified KG from loaded schemas
- **Method**: `SchemaParser.build_merged_knowledge_graph()` for multiple schemas
- **Output**: KG with nodes and relationships
- **Logging**: Node count, relationship count

### Step 3: Relationship Generation (LLM)
- **What**: Enhances KG with LLM-based relationship inference
- **LLM Usage**: OpenAI GPT-3.5-turbo for semantic analysis
- **Output**: Enhanced KG with additional relationships
- **Logging**: New relationships added, total relationships

### Step 4: Reconciliation Rules Generation (LLM)
- **What**: Generates reconciliation rules from KG relationships
- **LLM Usage**: OpenAI for semantic rule generation
- **Output**: ReconciliationRuleSet with rules
- **Logging**: Ruleset ID, rule count, confidence scores

### Step 5: Database Connection Verification
- **What**: Verifies connections to source and target databases
- **Source DB**: `ordermgmt` (MySQL)
- **Target DB**: `newamazon` (MySQL)
- **Output**: DatabaseConnectionInfo objects
- **Logging**: Connection details (host, port, database, user)

### Step 6: Rule Execution
- **What**: Executes reconciliation rules against real databases
- **Method**: `ReconciliationExecutor.execute_ruleset()`
- **Output**: Matched and unmatched records
- **Logging**: Matched count, unmatched counts, coverage rate, execution time

### Step 7: KPI Calculation
- **What**: Calculates three KPIs from execution results
- **KPIs**:
  - **RCR**: Reconciliation Coverage Rate (%)
  - **DQCS**: Data Quality Confidence Score (0.0-1.0)
  - **REI**: Reconciliation Efficiency Index
- **Storage**: MongoDB collections
- **Logging**: KPI values, status, MongoDB IDs

---

## 🚀 Running the Script

### Prerequisites

1. **Python Environment**
   ```bash
   python --version  # Python 3.8+
   ```

2. **Dependencies Installed**
   ```bash
   pip install -r requirements.txt
   ```

3. **Services Running**
   - FalkorDB (for KG storage)
   - MongoDB (for KPI storage)
   - Source Database (MySQL: ordermgmt)
   - Target Database (MySQL: newamazon)

4. **Environment Variables**
   - `.env` file configured with database credentials
   - OpenAI API key set in `.env`

### Running the Script

**Option 1: Direct Execution**
```bash
cd d:\learning\dq-poc
python test_end_to_end_reconciliation.py
```

**Option 2: With Python Module**
```bash
python -m test_end_to_end_reconciliation
```

**Option 3: From PowerShell**
```powershell
cd d:\learning\dq-poc
python test_end_to_end_reconciliation.py
```

---

## 📊 Output Files

### 1. Execution Log
**File**: `e2e_reconciliation.log`

Contains:
- Timestamp for each step
- INFO level logs for all operations
- Error details if any step fails
- Summary of results

**Example**:
```
2025-10-23 14:30:45 - E2E_Reconciliation - INFO - ================================================================================
2025-10-23 14:30:45 - E2E_Reconciliation - INFO - STEP 1: SCHEMA LOADING
2025-10-23 14:30:45 - E2E_Reconciliation - INFO - Found 2 schemas: ['orderMgmt-catalog', 'qinspect-designcode']
2025-10-23 14:30:46 - E2E_Reconciliation - INFO - ✓ Loaded schema: orderMgmt-catalog
2025-10-23 14:30:46 - E2E_Reconciliation - INFO -   - Tables: 5
```

### 2. Summary Report
**File**: `e2e_reconciliation_report_YYYYMMDD_HHMMSS.txt`

Contains:
- Execution timestamp
- Total execution time
- Schema information
- KG statistics
- Ruleset details
- Execution results
- KPI values and statuses
- MongoDB document IDs

**Example**:
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

================================================================================
6. KPI RESULTS
================================================================================
   RCR (Reconciliation Coverage Rate):
      Value: 95.92%
      Status: HEALTHY
      MongoDB ID: 507f1f77bcf86cd799439011
```

---

## 🔄 Idempotent Execution

The script is designed to be **idempotent** - it can be run multiple times safely:

### How It Works

1. **New KG Names**: Each execution creates a new KG with timestamp
   ```
   kg_20251023_143045
   kg_20251023_143100
   ```

2. **New Rulesets**: Each execution generates a new ruleset
   ```
   RECON_ABC123
   RECON_DEF456
   ```

3. **New Executions**: Each execution creates a new execution record
   ```
   EXEC_001
   EXEC_002
   ```

4. **New KPI Records**: Each execution stores new KPI documents in MongoDB
   - No overwriting of previous results
   - Full history maintained

### Running Multiple Times

```bash
# First run
python test_end_to_end_reconciliation.py

# Second run (safe - creates new KG, ruleset, execution)
python test_end_to_end_reconciliation.py

# Third run (safe - creates new KG, ruleset, execution)
python test_end_to_end_reconciliation.py
```

Each run produces:
- New log file: `e2e_reconciliation.log` (appended)
- New report file: `e2e_reconciliation_report_YYYYMMDD_HHMMSS.txt`
- New MongoDB documents for KPIs

---

## 📝 Logging Details

### Log Levels

- **INFO**: All major steps, results, and statistics
- **ERROR**: Failures with detailed error messages and stack traces

### Log Format

```
YYYY-MM-DD HH:MM:SS - E2E_Reconciliation - LEVEL - Message
```

### Example Log Output

```
2025-10-23 14:30:45 - E2E_Reconciliation - INFO - ================================================================================
2025-10-23 14:30:45 - E2E_Reconciliation - INFO - STEP 1: SCHEMA LOADING
2025-10-23 14:30:45 - E2E_Reconciliation - INFO - ================================================================================
2025-10-23 14:30:45 - E2E_Reconciliation - INFO - Found 2 schemas: ['orderMgmt-catalog', 'qinspect-designcode']
2025-10-23 14:30:46 - E2E_Reconciliation - INFO - ✓ Loaded schema: orderMgmt-catalog
2025-10-23 14:30:46 - E2E_Reconciliation - INFO -   - Tables: 5
2025-10-23 14:30:46 - E2E_Reconciliation - INFO - ✓ Loaded schema: qinspect-designcode
2025-10-23 14:30:46 - E2E_Reconciliation - INFO -   - Tables: 3
2025-10-23 14:30:46 - E2E_Reconciliation - INFO - ✓ Successfully loaded 2 schemas
```

---

## 🔧 Configuration

### Environment Variables (.env)

**Schema Loading**
- Schemas are loaded from `schemas/` folder
- No configuration needed

**LLM Configuration**
```
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000
```

**Database Configuration**
```
SOURCE_DB_TYPE=mysql
SOURCE_DB_HOST=localhost
SOURCE_DB_PORT=3306
SOURCE_DB_DATABASE=ordermgmt
SOURCE_DB_USERNAME=root
SOURCE_DB_PASSWORD=Baps@1234

TARGET_DB_TYPE=mysql
TARGET_DB_HOST=localhost
TARGET_DB_PORT=3306
TARGET_DB_DATABASE=newamazon
TARGET_DB_USERNAME=root
TARGET_DB_PASSWORD=Baps@1234
```

**MongoDB Configuration**
```
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE=dq_poc
```

---

## ✅ Success Indicators

### Successful Execution

1. **Log Output**
   - All 7 steps complete without errors
   - ✓ checkmarks for each step
   - Final message: "✓ END-TO-END RECONCILIATION WORKFLOW COMPLETED SUCCESSFULLY"

2. **Output Files**
   - `e2e_reconciliation.log` created/updated
   - `e2e_reconciliation_report_*.txt` created

3. **MongoDB**
   - 3 new KPI documents created
   - RCR, DQCS, REI values stored

### Example Success Output

```
================================================================================
STEP 1: SCHEMA LOADING
================================================================================
✓ Successfully loaded 2 schemas

================================================================================
STEP 2: KNOWLEDGE GRAPH CREATION
================================================================================
✓ KG created: kg_20251023_143045
  - Nodes: 45
  - Relationships: 78

================================================================================
STEP 7: KPI CALCULATION
================================================================================
✓ RCR calculated: 95.92%
✓ DQCS calculated: 0.862
✓ REI calculated: 40.8

================================================================================
✓ END-TO-END RECONCILIATION WORKFLOW COMPLETED SUCCESSFULLY
================================================================================
```

---

## 🐛 Troubleshooting

### Issue: "Schema directory not found"
**Solution**: Ensure `schemas/` folder exists with JSON files

### Issue: "Failed to connect to database"
**Solution**: 
- Verify database is running
- Check `.env` credentials
- Verify host/port are correct

### Issue: "OpenAI API error"
**Solution**:
- Verify `OPENAI_API_KEY` in `.env`
- Check API key is valid
- Verify rate limits not exceeded

### Issue: "MongoDB connection failed"
**Solution**:
- Verify MongoDB is running
- Check `MONGODB_CONNECTION_STRING` in `.env`
- Verify MongoDB port (default: 27017)

---

## 📚 Related Documentation

- `docs/KPI_DESIGN_AND_ANALYSIS.md` - KPI specifications
- `docs/KPI_EXECUTION_FLOW.md` - KPI execution details
- `LOCAL_DEVELOPMENT_GUIDE.md` - Local setup guide
- `MONGODB_RECONCILIATION_GUIDE.md` - MongoDB setup

---

**Version**: 1.0
**Date**: 2025-10-23
**Status**: Complete

