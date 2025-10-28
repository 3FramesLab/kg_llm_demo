# KPI Dashboard - Quick Start Guide

## What is the KPI Dashboard?

The KPI Dashboard is a visual overview of all your Landing KPIs, organized by Knowledge Graph. It shows:
- All KPIs grouped by KG name
- Latest execution status for each KPI
- Record counts and execution times
- Quick access to detailed results

## Accessing the Dashboard

### Option 1: Via Navigation Menu
1. Open the application
2. Look for "KPI Dashboard" in the left sidebar
3. Click it to navigate to the dashboard

### Option 2: Direct URL
Navigate to: `http://localhost:3000/kpi-dashboard`

## Dashboard Layout

### Top Section
- **Title**: "KPI Dashboard"
- **Summary**: Shows total number of KPIs and Knowledge Graphs
- **Refresh Button**: Click to reload dashboard data

### KG Groups (Accordions)
Each Knowledge Graph is displayed as an expandable section:
- Click the arrow to expand/collapse
- Shows count of KPIs in that group

### KPI Cards
Within each KG group, KPIs are displayed as cards showing:

| Field | Description |
|-------|-------------|
| **KPI Name** | The name of the KPI |
| **Description** | Optional description of what the KPI does |
| **Status Badge** | ✅ Success, ❌ Failed, ⏱️ Pending |
| **Records** | Number of records returned by latest execution |
| **Execution Time** | How long the query took to execute |
| **Last Run** | When the KPI was last executed |
| **View Results** | Button to see detailed results |

## Viewing KPI Results

### Step 1: Find Your KPI
1. Expand the KG group containing your KPI
2. Locate the KPI card

### Step 2: Click "View Results"
- Button is in the bottom-right of the KPI card
- Only enabled if the KPI has been executed at least once

### Step 3: Results Dialog Opens
The dialog shows:

#### Execution Metadata
- **Status**: success/failed/pending
- **Record Count**: Total records returned
- **Execution Time**: Query duration in milliseconds
- **Confidence Score**: LLM confidence percentage
- **Source/Target Tables**: Tables involved in the query

#### Generated SQL Query
- Shows the exact SQL that was executed
- **Copy Button**: Click to copy SQL to clipboard
- Useful for debugging or running manually

#### Query Results Table
- Displays the actual data returned by the query
- **Pagination**: Navigate through results (5, 10, 25, or 50 rows per page)
- **Column Headers**: Shows all columns returned by the query
- **Data Rows**: Shows the actual data

#### Download Option
- **Download CSV Button**: Exports results as CSV file
- Filename: `{kpi_name}-results.csv`
- Opens in your default spreadsheet application

## Common Tasks

### Refresh Dashboard Data
1. Click the "Refresh" button in the top-right
2. Dashboard will reload with latest KPI data

### Copy SQL Query
1. Open results dialog for a KPI
2. Click "Copy" button next to "Generated SQL Query"
3. SQL is copied to clipboard
4. Paste it anywhere (text editor, database tool, etc.)

### Download Results as CSV
1. Open results dialog for a KPI
2. Scroll to "Query Results" section
3. Click "Download CSV" button
4. File downloads to your computer

### Check Execution Errors
1. If a KPI shows ❌ Failed status
2. Open results dialog
3. Scroll to bottom to see error message
4. Error message explains what went wrong

## Status Indicators

### ✅ Success (Green)
- KPI executed successfully
- Results are available
- View Results button is enabled

### ❌ Failed (Red)
- KPI execution failed
- Error message is shown on the card
- Check error details in results dialog

### ⏱️ Pending (Orange)
- KPI has never been executed
- View Results button is disabled
- Execute the KPI from Landing KPI Management page

## Tips & Tricks

### 1. Organize by KG
KPIs are automatically grouped by Knowledge Graph. If you have many KPIs, they're easier to find when organized by KG.

### 2. Use Pagination
If a KPI returns many records, use the pagination controls to navigate through results without loading everything at once.

### 3. Export for Analysis
Download results as CSV and open in Excel or Google Sheets for further analysis.

### 4. Monitor Execution Times
Check execution times to identify slow-running KPIs that might need optimization.

### 5. Track Confidence Scores
Higher confidence scores (closer to 100%) indicate the LLM was more confident in its interpretation of the natural language definition.

## Troubleshooting

### Dashboard Won't Load
- **Problem**: Dashboard shows loading spinner indefinitely
- **Solution**: 
  1. Click Refresh button
  2. Check browser console for errors (F12)
  3. Verify backend API is running

### No KPIs Showing
- **Problem**: Dashboard shows "No KPIs found"
- **Solution**:
  1. Go to Landing KPI Management page
  2. Create at least one KPI
  3. Execute the KPI
  4. Return to dashboard

### Results Dialog Won't Open
- **Problem**: View Results button is disabled
- **Solution**:
  1. KPI must have been executed at least once
  2. Go to Landing KPI Management
  3. Execute the KPI
  4. Return to dashboard and try again

### CSV Download Not Working
- **Problem**: Download button doesn't work
- **Solution**:
  1. Check browser download settings
  2. Ensure pop-ups aren't blocked
  3. Try a different browser
  4. Check browser console for errors

### SQL Query Not Showing
- **Problem**: Generated SQL Query section is empty
- **Solution**:
  1. This can happen if execution failed
  2. Check error message at bottom of dialog
  3. Re-execute the KPI from Landing KPI Management

## API Endpoints (For Developers)

### Get Dashboard Data
```
GET /v1/landing-kpi/dashboard
```
Returns all KPIs grouped by KG with latest execution summary.

### Get Latest Results for KPI
```
GET /v1/landing-kpi/{kpi_id}/latest-results
```
Returns detailed results from the most recent execution of a specific KPI.

## Next Steps

1. **Create KPIs**: Go to Landing KPI Management to create new KPIs
2. **Execute KPIs**: Execute KPIs to generate results
3. **View Dashboard**: Return to KPI Dashboard to see results
4. **Analyze Results**: Use the dashboard to monitor KPI performance

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the full implementation guide: `docs/KPI_DASHBOARD_IMPLEMENTATION.md`
3. Check backend logs for API errors
4. Check browser console (F12) for frontend errors

