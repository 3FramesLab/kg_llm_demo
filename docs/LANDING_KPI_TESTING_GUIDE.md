# Landing KPI Testing Guide

## Quick Start Testing

### 1. Start the Backend Server
```bash
cd d:\learning\dq-poc
python -m uvicorn kg_builder.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend
```bash
cd web-app
npm start
```

### 3. Access the Application
- Open browser: `http://localhost:3000`
- Navigate to: **Landing KPI** (in left sidebar)

---

## Manual Testing Workflow

### Test 1: Create a KPI

**Steps**:
1. Click "Create New KPI" button
2. Fill in form:
   - **Name**: "Product Match Rate"
   - **Alias**: "PMR"
   - **Group**: "Data Quality"
   - **Description**: "Percentage of products matched between systems"
   - **NL Definition**: "Show me all products in RBP GPU which are not in OPS Excel"
3. Click "Create"

**Expected Result**:
- Success message appears
- KPI appears in list
- Form closes

---

### Test 2: Execute a KPI

**Prerequisites**: At least one KPI created

**Steps**:
1. Find the KPI in the list
2. Click "Execute" button (play icon)
3. Fill in execution parameters:
   - **Knowledge Graph**: "KG_098" (or available KG)
   - **Schema**: "newdqschema"
   - **Database Type**: "mysql"
   - **Limit Records**: 1000
   - **Use LLM**: Checked
4. Click "Execute"

**Expected Result**:
- Success message: "KPI execution started (ID: XXX)"
- Execution record created with status "pending"
- Background execution begins

**Monitoring**:
- Check backend logs for execution progress
- Look for messages like:
  - "Starting KPI execution: KPI ID=1, Execution ID=1"
  - "Executing KPI: Product Match Rate"
  - "Query Type: comparison"
  - "KPI execution successful: 245 records in 1234.56ms"

---

### Test 3: View Execution History

**Prerequisites**: At least one KPI executed

**Steps**:
1. Find the KPI in the list
2. Click "History" button (clock icon)
3. View execution history table

**Expected Result**:
- Dialog opens showing execution history
- Displays: ID, Status, Records, Time, Confidence, Timestamp
- Status shows as "pending" or "success" or "failed"

---

### Test 4: View Drill-down Results

**Prerequisites**: Successful KPI execution with results

**Steps**:
1. Open execution history (see Test 3)
2. Find successful execution with records > 0
3. Click "View Results" button (eye icon)
4. Browse paginated results

**Expected Result**:
- Drill-down dialog opens
- Shows summary: Total Records, Page, Page Size
- Displays paginated table with results
- Can navigate between pages

---

### Test 5: Edit a KPI

**Steps**:
1. Find the KPI in the list
2. Click "Edit" button (pencil icon)
3. Modify fields (except Name):
   - Change Alias to "PMR_v2"
   - Update Description
4. Click "Update"

**Expected Result**:
- Success message appears
- KPI list refreshes with updated values

---

### Test 6: Delete a KPI

**Steps**:
1. Find the KPI in the list
2. Click "Delete" button (trash icon)
3. Confirm deletion in dialog

**Expected Result**:
- Confirmation dialog appears
- After confirmation, KPI is removed from list
- Success message appears

---

### Test 7: Search and Filter

**Steps**:
1. Enter search term: "Product"
2. Click "Apply Filters"

**Expected Result**:
- List filters to show only matching KPIs

**Steps**:
1. Select Group: "Data Quality"
2. Click "Apply Filters"

**Expected Result**:
- List filters to show only KPIs in that group

---

## API Testing with cURL

### Create KPI
```bash
curl -X POST http://localhost:8000/v1/landing-kpi/kpis \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test KPI",
    "alias_name": "TKPI",
    "group_name": "Data Quality",
    "description": "Test KPI",
    "nl_definition": "Show me all products in RBP GPU which are not in OPS Excel"
  }'
```

### List KPIs
```bash
curl http://localhost:8000/v1/landing-kpi/kpis
```

### Execute KPI
```bash
curl -X POST http://localhost:8000/v1/landing-kpi/kpis/1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "KG_098",
    "select_schema": "newdqschema",
    "db_type": "mysql",
    "limit_records": 1000,
    "use_llm": true
  }'
```

### Get Execution Result
```bash
curl http://localhost:8000/v1/landing-kpi/executions/1
```

### Get Drill-down Data
```bash
curl "http://localhost:8000/v1/landing-kpi/executions/1/drilldown?page=1&page_size=50"
```

---

## Troubleshooting

### Issue: "Could not establish database connection"
**Solution**: 
- Verify database credentials in `.env`
- Check database is running and accessible
- Verify schema exists in database

### Issue: "KPI ID not found"
**Solution**:
- Verify KPI was created successfully
- Check KPI ID in database

### Issue: Execution stays "pending"
**Solution**:
- Check backend logs for errors
- Verify NL Query Executor is working
- Check database connection

### Issue: No results returned
**Solution**:
- Verify NL definition is correct
- Check if data exists in source tables
- Verify schema and table names

---

## Performance Testing

### Test Large Result Sets
1. Create KPI with query returning many records
2. Execute with `limit_records: 10000`
3. Monitor:
   - Execution time
   - Memory usage
   - Pagination performance

### Test Concurrent Executions
1. Execute multiple KPIs simultaneously
2. Monitor:
   - Thread creation
   - Database connection pooling
   - Response times

---

## Expected Behavior

### Successful Execution Flow:
1. User clicks "Execute"
2. Execution record created (status: pending)
3. API returns immediately with execution_id
4. Background thread starts
5. NL Query pipeline executes
6. Results stored in database
7. Execution record updated (status: success)
8. User can view results

### Error Handling:
- Invalid parameters → HTTP 400
- KPI not found → HTTP 404
- Database error → HTTP 500 + error message
- Execution error → Execution record updated with error_message

---

## Checklist

- [ ] Backend server running
- [ ] Frontend server running
- [ ] Can navigate to Landing KPI page
- [ ] Can create KPI
- [ ] Can execute KPI
- [ ] Can view execution history
- [ ] Can view drill-down results
- [ ] Can edit KPI
- [ ] Can delete KPI
- [ ] Can search/filter KPIs
- [ ] API endpoints working with cURL
- [ ] Error handling working correctly

