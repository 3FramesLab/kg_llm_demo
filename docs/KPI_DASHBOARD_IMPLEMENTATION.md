# KPI Dashboard Implementation Guide

## Overview

A comprehensive KPI Dashboard has been implemented for the Landing KPI system, providing a visual overview of all KPIs grouped by Knowledge Graph (KG) with their latest execution status and results.

## Features

### 1. Dashboard Display
- **KPI Grouping**: All KPIs are grouped by Knowledge Graph name
- **Visual Organization**: Each KG group is displayed as an expandable accordion
- **KPI Cards**: Individual KPIs shown as cards within each group with:
  - KPI Name
  - Description
  - Latest execution status (success/failed/pending)
  - Record count from latest execution
  - Execution time
  - Last execution timestamp
  - Error messages (if any)

### 2. Results Viewing
- **View Results Button**: Click to see detailed results from the latest execution
- **Results Dialog**: Shows:
  - Execution metadata (status, record count, execution time, confidence score)
  - Generated SQL query (with copy-to-clipboard functionality)
  - Query results in a paginated table
  - Column names and data types
  - Download results as CSV

### 3. User Experience
- **Loading States**: Skeleton loaders while fetching data
- **Error Handling**: User-friendly error messages with retry option
- **Empty State**: Message when no KPIs exist
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Refresh Button**: Manually refresh dashboard data

## Backend Implementation

### New API Endpoints

#### 1. GET `/v1/landing-kpi/dashboard`
Returns all KPIs grouped by KG name with latest execution summary.

**Response Format:**
```json
{
  "success": true,
  "kgs": [
    {
      "kg_name": "KG_102",
      "kpis": [
        {
          "id": 1,
          "name": "Inactive Products in RBP",
          "definition": "Show me all...",
          "description": "...",
          "group_name": "...",
          "latest_execution": {
            "executed_at": "2025-10-28T13:50:55",
            "record_count": 42,
            "status": "success",
            "execution_time_ms": 1234.56,
            "error_message": null
          }
        }
      ]
    }
  ]
}
```

**Implementation:**
- File: `kg_builder/routes.py` (lines 2810-2850)
- Service Method: `LandingKPIService.get_dashboard_data()`

#### 2. GET `/v1/landing-kpi/{kpi_id}/latest-results`
Returns SQL results from the most recent execution for a specific KPI.

**Response Format:**
```json
{
  "success": true,
  "results": {
    "execution_id": 123,
    "kpi_id": 1,
    "sql_query": "SELECT * FROM ...",
    "result_data": [...],
    "column_names": ["col1", "col2", ...],
    "record_count": 42,
    "execution_status": "success",
    "execution_timestamp": "2025-10-28T13:50:55",
    "execution_time_ms": 1234.56,
    "confidence_score": 0.85,
    "error_message": null,
    "source_table": "brz_lnd_RBP_GPU",
    "target_table": "brz_lnd_OPS_EXCEL_GPU",
    "operation": "NOT_IN"
  }
}
```

**Implementation:**
- File: `kg_builder/routes.py` (lines 2853-2907)
- Service Method: `LandingKPIService.get_latest_results(kpi_id)`

### Service Layer Updates

**File:** `kg_builder/services/landing_kpi_service.py`

#### New Methods:

1. **`get_dashboard_data()`** (lines 335-420)
   - Fetches all active KPIs with their latest execution
   - Groups by KG name
   - Returns structured data for dashboard display
   - Handles NULL executions (KPIs never executed)

2. **`get_latest_results(kpi_id)`** (lines 422-495)
   - Fetches the most recent execution for a KPI
   - Parses JSON fields (result_data, joined_columns)
   - Extracts column names from result data
   - Returns comprehensive execution metadata

## Frontend Implementation

### Components

#### 1. KPIDashboard Component
**File:** `web-app/src/components/KPIDashboard.js`

**Features:**
- Fetches dashboard data on mount
- Groups KPIs by KG using Accordion components
- Displays KPI cards with status indicators
- Handles loading, error, and empty states
- Refresh functionality
- Opens results dialog on "View Results" click

**Key Functions:**
- `fetchDashboardData()`: Fetches from `/v1/landing-kpi/dashboard`
- `handleViewResults()`: Opens results dialog for selected KPI
- `getStatusIcon()`: Returns appropriate icon based on execution status
- `formatTimestamp()`: Formats execution timestamps
- `formatExecutionTime()`: Formats execution time in milliseconds

#### 2. KPIResultsViewDialog Component
**File:** `web-app/src/components/KPIResultsViewDialog.js`

**Features:**
- Modal dialog displaying detailed execution results
- Execution metadata section with status, record count, execution time, confidence score
- SQL query display with copy-to-clipboard
- Paginated results table
- CSV download functionality
- Error message display

**Key Functions:**
- `fetchResults()`: Fetches from `/v1/landing-kpi/{kpi_id}/latest-results`
- `handleCopySQL()`: Copies SQL query to clipboard
- `handleDownloadCSV()`: Downloads results as CSV file
- `handleChangePage()`: Handles table pagination

### Routing

**File:** `web-app/src/App.js`
- Added import: `import KPIDashboardPage from './pages/KPIDashboardPage';`
- Added route: `<Route path="/kpi-dashboard" element={<KPIDashboardPage />} />`

**File:** `web-app/src/pages/KPIDashboardPage.js`
- Simple wrapper page that renders KPIDashboard component

### Navigation

**File:** `web-app/src/components/Layout.js`
- Added BarChartIcon import
- Added menu item: `{ text: 'KPI Dashboard', icon: <BarChartIcon />, path: '/kpi-dashboard' }`

## Database Schema

The implementation uses the existing database schema:

### kpi_definitions Table
- `id`: Primary key
- `name`: KPI name
- `nl_definition`: Natural language definition
- `description`: KPI description
- `group_name`: Logical grouping
- `is_active`: Active status flag

### kpi_execution_results Table
- `id`: Primary key
- `kpi_id`: Foreign key to kpi_definitions
- `kg_name`: Knowledge Graph name
- `execution_timestamp`: When execution occurred
- `number_of_records`: Record count from query
- `execution_status`: success/failed/pending
- `execution_time_ms`: Execution duration
- `confidence_score`: LLM confidence
- `error_message`: Error details if failed
- `generated_sql`: The SQL query executed
- `result_data`: JSON array of query results
- `source_table`: Source table name
- `target_table`: Target table name
- `operation`: Query operation type

## Usage

### Accessing the Dashboard

1. **Via Navigation Menu**: Click "KPI Dashboard" in the left sidebar
2. **Direct URL**: Navigate to `http://localhost:3000/kpi-dashboard`

### Viewing KPI Results

1. Click on a KG group to expand it
2. Find the KPI you want to view
3. Click "View Results" button on the KPI card
4. Results dialog opens showing:
   - Execution metadata
   - Generated SQL query
   - Query results in table format
   - Option to download as CSV

### Downloading Results

1. Open results dialog for a KPI
2. Click "Download CSV" button
3. CSV file is downloaded with filename: `{kpi_name}-results.csv`

## Error Handling

### Dashboard Level
- Network errors: Display error message with retry button
- Empty state: Show message when no KPIs exist
- Loading state: Show skeleton loaders while fetching

### Results Dialog Level
- No results: Show info message
- Failed execution: Display error message from execution
- Network errors: Show error alert

## Performance Considerations

1. **Dashboard Query**: Uses efficient SQL with ROW_NUMBER() to get latest execution per KPI
2. **Pagination**: Results table supports pagination (5, 10, 25, 50 rows per page)
3. **Lazy Loading**: Results only fetched when dialog is opened
4. **Caching**: Dashboard data refreshed on demand via refresh button

## Future Enhancements

1. **Auto-refresh**: Add option to auto-refresh dashboard at intervals
2. **Filtering**: Filter KPIs by status, KG, or date range
3. **Sorting**: Sort KPIs by name, status, or last execution time
4. **Favorites**: Mark frequently used KPIs as favorites
5. **Alerts**: Notify when KPI execution fails
6. **Scheduling**: Schedule KPI executions from dashboard
7. **Comparison**: Compare results across multiple executions
8. **Export**: Export dashboard summary as PDF or Excel

## Testing

### Manual Testing Checklist

- [ ] Dashboard loads without errors
- [ ] KPIs are grouped correctly by KG
- [ ] Accordion expand/collapse works
- [ ] View Results button opens dialog
- [ ] Results dialog displays all metadata
- [ ] SQL query copy-to-clipboard works
- [ ] Results table pagination works
- [ ] CSV download works
- [ ] Refresh button updates data
- [ ] Error handling works (test with invalid KPI ID)
- [ ] Empty state displays when no KPIs exist
- [ ] Responsive design works on mobile

### API Testing

```bash
# Get dashboard data
curl http://localhost:8000/v1/landing-kpi/dashboard

# Get latest results for KPI ID 1
curl http://localhost:8000/v1/landing-kpi/1/latest-results
```

## Files Modified/Created

### Backend
- ✅ `kg_builder/services/landing_kpi_service.py` - Added 2 new methods
- ✅ `kg_builder/routes.py` - Added 2 new endpoints

### Frontend
- ✅ `web-app/src/components/KPIDashboard.js` - New component
- ✅ `web-app/src/components/KPIResultsViewDialog.js` - New component
- ✅ `web-app/src/pages/KPIDashboardPage.js` - New page
- ✅ `web-app/src/App.js` - Added route
- ✅ `web-app/src/components/Layout.js` - Added navigation link

## Status

✅ **COMPLETE** - KPI Dashboard fully implemented and ready for use

