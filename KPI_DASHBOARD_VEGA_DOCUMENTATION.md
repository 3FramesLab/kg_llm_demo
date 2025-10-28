# KPI Dashboard with Vega-Lite Visualizations

## Overview

The **KPIDashboardVega** component is a comprehensive, interactive data visualization dashboard that displays KPI metrics using Vega-Lite charts. It provides drill-down capabilities, data filtering, and CSV export functionality.

## Features

### 1. **Dynamic Group-Based Sections**
- Automatically creates separate sections for each unique `group_name` from the API
- Each section displays:
  - Group name as header
  - Number of KPIs in the group
  - Total record count across all KPIs in the group

### 2. **Interactive Bar Charts**
- **Vega-Lite bar charts** for each group showing:
  - X-axis: KPI names
  - Y-axis: Record counts
  - Color-coded by execution status (success, failed, pending)
  - Hover tooltips with detailed information
  - Smooth opacity transitions on hover
  - Export functionality (PNG, SVG)

### 3. **Clickable KPI Cards**
- Below each chart, clickable chips for each KPI
- Shows KPI name and record count
- Color-coded by status
- Triggers drill-down dialog on click

### 4. **Drill-down Dialog**
When a user clicks on a KPI:
- Opens a modal dialog with detailed data
- Displays the SQL query that generated the results
- Shows summary statistics (total records, column count)
- Provides interactive data table with:
  - Pagination (5, 10, 25, 50 rows per page)
  - Search/filter functionality
  - Sortable columns
  - Hover effects

### 5. **Data Export**
- CSV export button in drill-down dialog
- Exports all filtered records
- Properly handles special characters and commas

### 6. **Responsive Design**
- Works on desktop, tablet, and mobile
- Flexible grid layout
- Responsive chart sizing
- Mobile-friendly dialogs

## Component Structure

```
KPIDashboardVega
├── Header Section
│   ├── Title
│   ├── Summary (total KPIs and groups)
│   └── Refresh Button
├── Group Sections (Dynamic)
│   ├── Group Header
│   ├── Bar Chart (Vega-Lite)
│   └── KPI Chips (Clickable)
└── Drill-down Dialog
    ├── KPI Title
    ├── SQL Query Display
    ├── Summary Stats
    ├── Search Filter
    ├── Data Table
    ├── Pagination
    └── Export Button
```

## API Integration

### Primary Dashboard API
**Endpoint**: `GET /v1/landing-kpi/dashboard`

**Response Format**:
```json
{
  "groups": [
    {
      "group_name": "Data Quality",
      "kpis": [
        {
          "id": "kpi_123",
          "name": "Product Count",
          "description": "Total products in system",
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

### Drill-down API
**Endpoint**: `GET /v1/landing-kpi/{kpi_id}/latest-results`

**Response Format**:
```json
{
  "sql": "SELECT * FROM products WHERE...",
  "records": [
    { "id": 1, "name": "Product A", "count": 100 },
    { "id": 2, "name": "Product B", "count": 200 }
  ]
}
```

## State Management

### Main States
- `dashboardData`: API response with groups and KPIs
- `loading`: Loading state for dashboard
- `error`: Error message if API fails
- `drilldownOpen`: Dialog visibility
- `selectedKPI`: Currently selected KPI
- `drilldownData`: Drill-down results
- `drilldownLoading`: Loading state for drill-down
- `drilldownError`: Error message for drill-down
- `page`: Current pagination page
- `rowsPerPage`: Rows per page setting
- `searchFilter`: Search filter text

## Key Functions

### `fetchDashboardData()`
- Fetches KPI dashboard data from API
- Sets loading and error states
- Called on component mount and refresh

### `fetchDrilldownData(kpiId)`
- Fetches detailed results for a specific KPI
- Resets pagination
- Sets loading and error states

### `handleBarClick(kpi)`
- Opens drill-down dialog
- Fetches drill-down data

### `handleKPICardClick(kpi)`
- Wrapper for bar click handler
- Triggered by chip click

### `exportToCSV()`
- Generates CSV from drill-down records
- Handles special characters
- Triggers browser download

### `getFilteredRecords()`
- Filters records based on search text
- Case-insensitive search across all fields

## Styling & Design

### Material-UI Components Used
- `Container`: Main layout wrapper
- `Box`: Flexible layout container
- `Paper`: Card-like containers
- `Dialog`: Modal for drill-down
- `Table`: Data display
- `Chip`: Clickable KPI cards
- `TextField`: Search input
- `Button`: Actions
- `Alert`: Error/info messages
- `Skeleton`: Loading placeholders

### Color Scheme
- **Success**: #4caf50 (green)
- **Failed**: #f44336 (red)
- **Pending**: #ff9800 (orange)
- **Primary**: #1976d2 (blue)

### Responsive Breakpoints
- `xs`: Mobile (0px+)
- `sm`: Tablet (600px+)
- `md`: Desktop (960px+)
- `lg`: Large desktop (1280px+)
- `xl`: Extra large (1920px+)

## Usage

### Basic Implementation
```jsx
import KPIDashboardVega from './components/KPIDashboardVega';

function App() {
  return <KPIDashboardVega />;
}
```

### Routing
Already configured in `web-app/src/pages/KPIDashboardPage.js`:
```jsx
import KPIDashboardVega from '../components/KPIDashboardVega';

const KPIDashboardPage = () => {
  return <KPIDashboardVega />;
};
```

Access at: `/kpi-dashboard`

## Error Handling

### Loading States
- Shows skeleton loaders while fetching data
- Displays spinner in drill-down dialog

### Error States
- Shows error alert with message
- Provides retry button
- Logs errors to console

### Empty States
- Shows message if no KPIs found
- Provides link to KPI Management page

## Performance Considerations

1. **Lazy Loading**: Data fetched on demand
2. **Pagination**: Large datasets paginated (10 rows default)
3. **Search Filtering**: Client-side filtering for responsiveness
4. **Memoization**: Consider adding React.memo for group sections
5. **Chart Optimization**: Vega-Lite handles rendering efficiently

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Dependencies

- `react`: ^18.2.0
- `@mui/material`: ^5.14.19
- `@mui/icons-material`: ^5.14.19
- `react-vega`: Latest
- `vega`: Latest
- `vega-lite`: Latest

## Installation

```bash
npm install vega vega-lite react-vega
```

## Future Enhancements

1. **Advanced Filtering**: Multi-column filters
2. **Custom Metrics**: User-defined Y-axis metrics
3. **Time Series**: Historical KPI trends
4. **Alerts**: Threshold-based notifications
5. **Scheduling**: Automated KPI execution
6. **Sharing**: Dashboard sharing/embedding
7. **Customization**: User-defined chart types
8. **Real-time Updates**: WebSocket integration

## Troubleshooting

### Charts Not Rendering
- Check API response format
- Verify Vega-Lite library is installed
- Check browser console for errors

### Drill-down Dialog Not Opening
- Verify KPI has `latest_execution` data
- Check API endpoint is accessible
- Verify KPI ID is correct

### CSV Export Not Working
- Ensure records have data
- Check browser allows downloads
- Verify special characters are handled

## Support

For issues or questions, refer to:
- Vega-Lite Documentation: https://vega.github.io/vega-lite/
- React-Vega: https://github.com/vega/react-vega
- Material-UI: https://mui.com/


