# KPI Dashboard Vega-Lite - Data Transformation Guide

## 🎯 Overview

The KPI Dashboard automatically transforms API data into Vega-Lite compatible format. This guide explains how the data flows from the API to the visualization.

---

## 📊 Data Flow

```
API Response
    ↓
Data Validation & Transformation
    ↓
Group Organization
    ↓
Vega-Lite Spec Generation
    ↓
Chart Rendering
```

---

## 🔄 API Response Handling

### Expected API Response Format

The dashboard expects one of two formats:

#### Format 1: Grouped Response (Preferred)
```json
{
  "groups": [
    {
      "group_name": "Data Quality",
      "kpis": [
        {
          "id": "kpi_123",
          "name": "Product Count",
          "description": "Total products",
          "group": "Data Quality",
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

#### Format 2: Flat Response (Auto-converted)
```json
{
  "kpis": [
    {
      "id": "kpi_123",
      "name": "Product Count",
      "description": "Total products",
      "group": "Data Quality",
      "latest_execution": {
        "status": "success",
        "record_count": 1500
      }
    }
  ]
}
```

---

## 🔧 Data Transformation Logic

### Step 1: Fetch Dashboard Data
```javascript
const response = await fetch(`${API_BASE_URL}/landing-kpi/dashboard`);
const data = await response.json();
```

### Step 2: Validate & Transform
```javascript
let transformedData = data;

// If API returns flat list, group by group_name
if (data.kpis && !data.groups) {
  const groupedByName = {};
  
  data.kpis.forEach(kpi => {
    const groupName = kpi.group || 'Ungrouped';
    if (!groupedByName[groupName]) {
      groupedByName[groupName] = [];
    }
    groupedByName[groupName].push(kpi);
  });
  
  transformedData = {
    groups: Object.entries(groupedByName).map(([name, kpis]) => ({
      group_name: name,
      kpis: kpis,
    })),
  };
}
```

### Step 3: Extract Groups
```javascript
const groups = transformedData?.groups || [];
```

---

## 📈 Vega-Lite Data Transformation

### Per-Group Data Transformation

For each group, KPI data is transformed into Vega-Lite format:

```javascript
group.kpis.map(kpi => ({
  name: kpi.name,                                    // KPI name
  records: kpi.latest_execution?.record_count || 0, // Y-axis value
  id: kpi.id,                                        // KPI ID
  status: kpi.latest_execution?.status || 'pending', // Color encoding
}))
```

### Example Transformation

**Input KPI:**
```javascript
{
  id: "kpi_123",
  name: "Product Count",
  latest_execution: {
    status: "success",
    record_count: 1500
  }
}
```

**Output for Vega-Lite:**
```javascript
{
  name: "Product Count",
  records: 1500,
  id: "kpi_123",
  status: "success"
}
```

---

## 📊 Vega-Lite Specification

### Complete Chart Spec

```javascript
{
  $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
  description: `KPI metrics for ${group.group_name}`,
  
  // Data: Transformed KPI array
  data: {
    values: [
      { name: "KPI1", records: 1500, id: "kpi_123", status: "success" },
      { name: "KPI2", records: 2000, id: "kpi_124", status: "failed" },
      { name: "KPI3", records: 800, id: "kpi_125", status: "pending" }
    ]
  },
  
  // Mark: Bar chart
  mark: { type: 'bar', cursor: 'pointer', tooltip: true },
  
  // Encoding: Map data fields to visual properties
  encoding: {
    x: {
      field: 'name',
      type: 'nominal',
      axis: { labelAngle: -45, labelBound: true },
      title: 'KPI Name'
    },
    y: {
      field: 'records',
      type: 'quantitative',
      title: 'Record Count'
    },
    color: {
      field: 'status',
      type: 'nominal',
      scale: {
        domain: ['success', 'failed', 'pending'],
        range: ['#4caf50', '#f44336', '#ff9800']
      },
      title: 'Status'
    },
    tooltip: [
      { field: 'name', type: 'nominal', title: 'KPI' },
      { field: 'records', type: 'quantitative', title: 'Records' },
      { field: 'status', type: 'nominal', title: 'Status' },
      { field: 'id', type: 'nominal', title: 'ID' }
    ]
  },
  
  // Sizing
  width: 'container',
  height: 300,
  
  // Configuration
  config: {
    mark: { tooltip: true },
    axis: { minExtent: 30 }
  }
}
```

---

## 🎨 Visual Encoding

### X-Axis (Horizontal)
- **Field**: `name` (KPI name)
- **Type**: Nominal (categorical)
- **Display**: KPI names with -45° angle

### Y-Axis (Vertical)
- **Field**: `records` (record count)
- **Type**: Quantitative (numerical)
- **Display**: Record count values

### Color
- **Field**: `status` (execution status)
- **Type**: Nominal (categorical)
- **Mapping**:
  - `success` → Green (#4caf50)
  - `failed` → Red (#f44336)
  - `pending` → Orange (#ff9800)

### Tooltip
- Shows on hover
- Displays: KPI name, records, status, ID

---

## 🔍 Data Validation

### Null/Undefined Handling

```javascript
// Record count defaults to 0
records: kpi.latest_execution?.record_count || 0

// Status defaults to 'pending'
status: kpi.latest_execution?.status || 'pending'

// Group name defaults to 'Ungrouped'
groupName: kpi.group || 'Ungrouped'
```

### Empty Data Handling

```javascript
// If no KPIs exist
if (totalKPIs === 0) {
  // Show empty state message
  // Provide link to KPI Management
}

// If group has no KPIs
if (group.kpis.length === 0) {
  // Skip rendering this group
}
```

---

## 🚨 Error Handling

### API Errors
```javascript
try {
  const response = await fetch(`${API_BASE_URL}/landing-kpi/dashboard`);
  if (!response.ok) {
    throw new Error(`Failed to fetch: ${response.statusText}`);
  }
  const data = await response.json();
} catch (err) {
  console.error('Error fetching dashboard:', err);
  setError(err.message);
}
```

### Chart Rendering Errors
```javascript
VegaEmbed(chartRef.current, spec, options)
  .catch((err) => {
    console.error('Vega chart error:', err);
    setChartError(err.message);
  });
```

---

## 📝 Debugging

### Console Logging

The component logs the API response:
```javascript
console.log('Dashboard API Response:', data);
```

### Check Browser Console

1. Open DevTools (F12)
2. Go to Console tab
3. Look for "Dashboard API Response"
4. Verify data structure matches expected format

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Chart not rendering | Invalid data format | Check API response in console |
| No bars visible | Empty `records` values | Verify `latest_execution.record_count` |
| Wrong colors | Status values don't match | Check status values: success/failed/pending |
| Chart errors | Vega-Lite spec invalid | Check browser console for errors |

---

## 🔄 Data Update Flow

### Initial Load
1. Component mounts
2. `useEffect` calls `fetchDashboardData()`
3. API data fetched and transformed
4. State updated with transformed data
5. Component re-renders with charts

### Refresh Button
1. User clicks "Refresh"
2. `fetchDashboardData()` called again
3. API data fetched and transformed
4. State updated
5. Charts re-render with new data

### Drill-down
1. User clicks KPI chip
2. `fetchDrilldownData(kpiId)` called
3. Detailed data fetched from `/landing-kpi/{kpi_id}/latest-results`
4. Dialog opens with data table

---

## 📊 Example: Complete Data Flow

### Step 1: API Response
```json
{
  "groups": [
    {
      "group_name": "Data Quality",
      "kpis": [
        {
          "id": "kpi_1",
          "name": "Product Count",
          "latest_execution": {
            "status": "success",
            "record_count": 1500
          }
        },
        {
          "id": "kpi_2",
          "name": "Customer Count",
          "latest_execution": {
            "status": "failed",
            "record_count": 0
          }
        }
      ]
    }
  ]
}
```

### Step 2: Transformation
```javascript
// No transformation needed (already grouped)
transformedData = data;
```

### Step 3: Vega Data
```javascript
[
  { name: "Product Count", records: 1500, id: "kpi_1", status: "success" },
  { name: "Customer Count", records: 0, id: "kpi_2", status: "failed" }
]
```

### Step 4: Chart Rendering
- Bar 1: "Product Count" - 1500 records - Green (success)
- Bar 2: "Customer Count" - 0 records - Red (failed)

---

## ✅ Verification Checklist

- [ ] API returns data in expected format
- [ ] Data transformation logic handles both formats
- [ ] Null/undefined values handled correctly
- [ ] Status values are: success, failed, or pending
- [ ] Record counts are numeric
- [ ] Group names are strings
- [ ] KPI names are strings
- [ ] KPI IDs are unique
- [ ] Charts render without errors
- [ ] Tooltips show correct data
- [ ] Colors match status values

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-28


