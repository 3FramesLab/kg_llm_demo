# KPI Dashboard with Vega-Lite - Quick Reference Guide

## 🚀 Quick Start

### Access the Dashboard
```
URL: http://localhost:3000/kpi-dashboard
Menu: Click "KPI Dashboard" in sidebar
```

### What You'll See
1. **Dashboard Header** - Title, total KPIs, and refresh button
2. **Group Sections** - One section per group_name from API
3. **Bar Charts** - Visual representation of KPI metrics
4. **KPI Chips** - Clickable cards for each KPI

## 📊 Dashboard Layout

```
┌─────────────────────────────────────────────────────┐
│  KPI Dashboard                          [Refresh]   │
│  15 KPIs across 3 groups                            │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Data Quality                                         │
│ 5 KPIs • Total Records: 15,000                      │
│                                                      │
│  [Bar Chart - Vega-Lite]                            │
│                                                      │
│  [KPI1] [KPI2] [KPI3] [KPI4] [KPI5]                │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Reconciliation                                       │
│ 5 KPIs • Total Records: 8,500                       │
│                                                      │
│  [Bar Chart - Vega-Lite]                            │
│                                                      │
│  [KPI6] [KPI7] [KPI8] [KPI9] [KPI10]               │
└─────────────────────────────────────────────────────┘

... more groups ...
```

## 🎯 User Interactions

### 1. View Dashboard
```
1. Navigate to /kpi-dashboard
2. Wait for data to load
3. See groups with bar charts
```

### 2. Drill-down into KPI
```
1. Click on any KPI chip below a chart
2. Dialog opens with detailed data
3. See SQL query, records, and stats
```

### 3. Search Records
```
1. In drill-down dialog, use search box
2. Type to filter records
3. Results update in real-time
```

### 4. Paginate Data
```
1. Use pagination controls at bottom
2. Select rows per page (5, 10, 25, 50)
3. Navigate through pages
```

### 5. Export Data
```
1. Click "Export CSV" button
2. File downloads to computer
3. Open in Excel or text editor
```

### 6. Refresh Dashboard
```
1. Click "Refresh" button in header
2. Dashboard reloads latest data
3. All sections update
```

## 🎨 Visual Elements

### Status Colors
- 🟢 **Green** (#4caf50): Success
- 🔴 **Red** (#f44336): Failed
- 🟠 **Orange** (#ff9800): Pending

### Chart Elements
- **X-axis**: KPI names
- **Y-axis**: Record counts
- **Bars**: Color-coded by status
- **Hover**: Shows tooltip with details
- **Click**: Opens drill-down dialog

### Data Table
- **Columns**: Dynamic based on data
- **Rows**: Paginated (default 10)
- **Search**: Filter across all columns
- **Hover**: Highlight row

## 📋 Drill-down Dialog

### Components
```
┌─────────────────────────────────────────┐
│ KPI Name                          [X]   │
│ Description                             │
├─────────────────────────────────────────┤
│ SQL Query:                              │
│ SELECT * FROM table WHERE ...           │
│                                         │
│ Total Records: 1,500 | Columns: 8      │
│                                         │
│ [Search Box]                            │
│                                         │
│ [Data Table with Pagination]            │
│                                         │
├─────────────────────────────────────────┤
│ [Export CSV]  [Close]                   │
└─────────────────────────────────────────┘
```

### Features
- Read-only SQL display
- Summary statistics
- Search/filter functionality
- Paginated data table
- CSV export button
- Responsive layout

## 🔧 API Endpoints

### Dashboard Endpoint
```
GET /v1/landing-kpi/dashboard

Response:
{
  "groups": [
    {
      "group_name": "Data Quality",
      "kpis": [
        {
          "id": "kpi_123",
          "name": "Product Count",
          "description": "...",
          "latest_execution": {
            "status": "success",
            "record_count": 1500
          }
        }
      ]
    }
  ]
}
```

### Drill-down Endpoint
```
GET /v1/landing-kpi/{kpi_id}/latest-results

Response:
{
  "sql": "SELECT * FROM products WHERE...",
  "records": [
    { "id": 1, "name": "Product A", "count": 100 },
    { "id": 2, "name": "Product B", "count": 200 }
  ]
}
```

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **Dynamic Groups** | Auto-creates sections for each group |
| **Bar Charts** | Vega-Lite visualizations with hover effects |
| **Drill-down** | Click to see detailed data |
| **Search** | Filter records in real-time |
| **Pagination** | Handle large datasets efficiently |
| **Export** | Download data as CSV |
| **Responsive** | Works on mobile, tablet, desktop |
| **Error Handling** | Graceful error messages |
| **Loading States** | Skeleton loaders while fetching |

## 🚨 Error States

### No Data
```
"No KPIs found. Create your first KPI to get started."
[Go to KPI Management]
```

### API Error
```
"Failed to fetch dashboard data: [error message]"
[Retry]
```

### Drill-down Error
```
"Failed to fetch drill-down data: [error message]"
```

## 💡 Tips & Tricks

1. **Hover over bars** to see tooltip with KPI details
2. **Click KPI chips** to drill-down (not just bars)
3. **Use search** to quickly find specific records
4. **Export CSV** for offline analysis
5. **Refresh** to get latest data
6. **Check status colors** to identify issues
7. **Use pagination** for large datasets
8. **Resize browser** to test responsive design

## 📱 Responsive Breakpoints

| Device | Width | Layout |
|--------|-------|--------|
| Mobile | <600px | Single column, stacked |
| Tablet | 600-960px | 2 columns |
| Desktop | 960-1280px | Full width |
| Large | >1280px | Extra large |

## 🔍 Troubleshooting

### Dashboard Not Loading
- Check API is running
- Check network tab in DevTools
- Verify API_BASE_URL is correct

### Charts Not Showing
- Check browser console for errors
- Verify Vega-Lite library loaded
- Check API response format

### Drill-down Not Opening
- Verify KPI has execution data
- Check KPI ID is correct
- Check API endpoint accessible

### CSV Export Not Working
- Ensure records have data
- Check browser allows downloads
- Try different browser

### Search Not Filtering
- Check search text is entered
- Verify records have data
- Try clearing and re-entering

## 📚 File Locations

```
web-app/
├── src/
│   ├── components/
│   │   └── KPIDashboardVega.js (Main component)
│   ├── pages/
│   │   └── KPIDashboardPage.js (Page wrapper)
│   └── App.js (Routing)
└── package.json (Dependencies)

Root:
├── KPI_DASHBOARD_VEGA_DOCUMENTATION.md
├── KPI_DASHBOARD_VEGA_IMPLEMENTATION_SUMMARY.md
└── KPI_DASHBOARD_QUICK_REFERENCE.md (This file)
```

## 🔗 Related Components

- **KPIManagement**: Create/edit KPIs
- **KPIList**: View all KPIs in table
- **KPIResultsViewDialog**: View results (legacy)
- **Layout**: Navigation menu

## 📞 Support

For issues or questions:
1. Check this quick reference
2. Read full documentation
3. Check browser console for errors
4. Verify API endpoints are working
5. Contact development team

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-28  
**Status**: ✅ Ready for Use


