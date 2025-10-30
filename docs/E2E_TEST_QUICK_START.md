# End-to-End Test - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Verify Prerequisites

```bash
# Check Python
python --version

# Check dependencies
pip list | findstr "jaydebeapi pymongo openai"

# Check services running
# - FalkorDB: redis-cli ping
# - MongoDB: mongosh --eval "db.adminCommand('ping')"
# - MySQL: mysql -u root -p -e "SELECT 1"
```

### 2. Verify Configuration

```bash
# Check .env file exists
type .env

# Verify key settings
# - OPENAI_API_KEY is set
# - SOURCE_DB_HOST, SOURCE_DB_PORT, SOURCE_DB_DATABASE
# - TARGET_DB_HOST, TARGET_DB_PORT, TARGET_DB_DATABASE
# - MONGODB_CONNECTION_STRING
```

### 3. Run the Test

```bash
cd d:\learning\dq-poc
python test_end_to_end_reconciliation.py
```

### 4. Monitor Progress

```bash
# In another terminal, watch the log file
Get-Content e2e_reconciliation.log -Wait
```

### 5. Check Results

```bash
# View summary report
Get-ChildItem e2e_reconciliation_report_*.txt | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content

# View MongoDB results
mongosh --eval "db.kpi_reconciliation_coverage.findOne()"
```

---

## 📊 Expected Output

### Console Output
```
================================================================================
STARTING END-TO-END RECONCILIATION WORKFLOW
================================================================================

================================================================================
STEP 1: SCHEMA LOADING
================================================================================
Found 2 schemas: ['orderMgmt-catalog', 'qinspect-designcode']
✓ Loaded schema: orderMgmt-catalog
  - Tables: 5
✓ Loaded schema: qinspect-designcode
  - Tables: 3
✓ Successfully loaded 2 schemas

================================================================================
STEP 2: KNOWLEDGE GRAPH CREATION
================================================================================
Creating KG 'kg_20251023_143045' from schemas: ['orderMgmt-catalog', 'qinspect-designcode']
✓ KG created: kg_20251023_143045
  - Nodes: 45
  - Relationships: 78

[... more steps ...]

================================================================================
✓ END-TO-END RECONCILIATION WORKFLOW COMPLETED SUCCESSFULLY
================================================================================
```

### Output Files
```
e2e_reconciliation.log                          # Execution log
e2e_reconciliation_report_20251023_143045.txt   # Summary report
```

---

## 🔍 Workflow Steps (What Happens)

```
1. SCHEMA LOADING
   └─ Loads: orderMgmt-catalog.json, qinspect-designcode.json
   └─ Output: 2 schemas with tables and columns

2. KNOWLEDGE GRAPH CREATION
   └─ Creates unified KG from 2 schemas
   └─ Output: KG with ~45 nodes, ~78 relationships

3. RELATIONSHIP GENERATION (LLM)
   └─ Uses OpenAI GPT-3.5-turbo
   └─ Enhances relationships with semantic analysis
   └─ Output: Enhanced KG with more relationships

4. RECONCILIATION RULES GENERATION (LLM)
   └─ Uses OpenAI GPT-3.5-turbo
   └─ Generates matching rules from KG
   └─ Output: ~20 reconciliation rules

5. DATABASE CONNECTION VERIFICATION
   └─ Verifies connection to ordermgmt (source)
   └─ Verifies connection to newamazon (target)
   └─ Output: Connection configs

6. RULE EXECUTION
   └─ Executes rules against real databases
   └─ Finds matched and unmatched records
   └─ Output: Matched count, unmatched counts

7. KPI CALCULATION
   └─ Calculates RCR, DQCS, REI
   └─ Stores in MongoDB
   └─ Output: KPI values and MongoDB IDs
```

---

## ⏱️ Typical Execution Time

```
Step 1: Schema Loading          ~2 seconds
Step 2: KG Creation             ~3 seconds
Step 3: LLM Relationships       ~15 seconds (API calls)
Step 4: LLM Rules Generation    ~20 seconds (API calls)
Step 5: DB Connection           ~1 second
Step 6: Rule Execution          ~10 seconds (database queries)
Step 7: KPI Calculation         ~2 seconds

Total: ~50-60 seconds
```

---

## 📋 Checklist Before Running

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with credentials
- [ ] FalkorDB running (port 6379)
- [ ] MongoDB running (port 27017)
- [ ] MySQL running with ordermgmt and newamazon databases
- [ ] OpenAI API key valid and set in `.env`
- [ ] Schemas exist in `schemas/` folder
- [ ] Network connectivity to all services

---

## 🎯 Key Results to Check

### 1. Log File
```bash
# Should show all 7 steps completed
Get-Content e2e_reconciliation.log | Select-String "STEP"
```

### 2. Summary Report
```bash
# Should show KPI values
Get-Content e2e_reconciliation_report_*.txt | Select-String "KPI"
```

### 3. MongoDB
```bash
# Should have 3 new KPI documents
mongosh --eval "db.kpi_reconciliation_coverage.countDocuments()"
mongosh --eval "db.kpi_data_quality_confidence.countDocuments()"
mongosh --eval "db.kpi_reconciliation_efficiency.countDocuments()"
```

---

## 🔄 Running Multiple Times

The script is **idempotent** - safe to run multiple times:

```bash
# First run
python test_end_to_end_reconciliation.py

# Second run (creates new KG, ruleset, execution)
python test_end_to_end_reconciliation.py

# Third run (creates new KG, ruleset, execution)
python test_end_to_end_reconciliation.py
```

Each run:
- Creates new KG with timestamp
- Generates new ruleset
- Creates new execution record
- Stores new KPI documents in MongoDB
- Appends to log file
- Creates new summary report

---

## 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| "Schema directory not found" | Verify `schemas/` folder exists |
| "Failed to connect to database" | Check MySQL is running, verify `.env` credentials |
| "OpenAI API error" | Verify `OPENAI_API_KEY` in `.env` is valid |
| "MongoDB connection failed" | Check MongoDB is running on port 27017 |
| "FalkorDB connection failed" | Check FalkorDB is running on port 6379 |

---

## 📚 Full Documentation

See `docs/E2E_TEST_GUIDE.md` for comprehensive documentation

---

## 🎉 Success!

When you see this message, the test completed successfully:

```
================================================================================
✓ END-TO-END RECONCILIATION WORKFLOW COMPLETED SUCCESSFULLY
================================================================================
```

Check the summary report for detailed results:
```bash
Get-ChildItem e2e_reconciliation_report_*.txt | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

---

**Ready to run?**
```bash
python test_end_to_end_reconciliation.py
```

