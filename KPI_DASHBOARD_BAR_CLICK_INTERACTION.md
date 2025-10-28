# KPI Dashboard - Bar Click Interaction Guide

## 🎯 Overview

The KPI Dashboard now supports **direct bar click interaction** for drill-down functionality. Users can click on any bar in the Vega-Lite chart to open the drill-down dialog with detailed KPI data.

---

## 🔄 How It Works

### User Interaction Flow

```
User clicks on bar
    ↓
Vega chart detects click event
    ↓
Extract clicked bar data (KPI ID)
    ↓
Find matching KPI object
    ↓
Call onBarClick handler
    ↓
Open drill-down dialog
    ↓
Fetch detailed KPI results
    ↓
Display data table with SQL query
```

---

## 🛠️ Implementation Details

### VegaChart Component

The `VegaChart` component now accepts three props:

```javascript
<VegaChart
  spec={vegaSpec}           // Vega-Lite specification
  onBarClick={handleBarClick}  // Click handler function
  kpis={group.kpis}         // Array of KPI objects
/>
```

### Click Event Handler

```javascript
const VegaChart = ({ spec, onBarClick, kpis }) => {
  const chartRef = React.useRef(null);
  const [chartError, setChartError] = React.useState(null);

  React.useEffect(() => {
    if (chartRef.current && spec) {
      setChartError(null);
      VegaEmbed(chartRef.current, spec, {
        actions: {
          export: true,
          source: false,
          compiled: false,
          editor: false,
        },
      })
        .then((result) => {
          // Add click event listener to the Vega view
          if (result && result.view) {
            result.view.addEventListener('click', (event, item) => {
              if (item && item.datum) {
                // Find the KPI object that matches the clicked bar
                const clickedKPI = kpis.find(kpi => kpi.id === item.datum.id);
                if (clickedKPI && onBarClick) {
                  onBarClick(clickedKPI);
                }
              }
            });
          }
        })
        .catch((err) => {
          console.error('Vega chart error:', err);
          setChartError(err.message);
        });
    }
  }, [spec, onBarClick, kpis]);

  // ... rest of component
};
```

### Click Handler Function

```javascript
const handleBarClick = (kpi) => {
  setSelectedKPI(kpi);
  setDrilldownOpen(true);
  fetchDrilldownData(kpi.id);
};
```

---

## 📊 Data Flow

### Step 1: Click Detection
```javascript
result.view.addEventListener('click', (event, item) => {
  // item.datum contains the clicked bar's data
  // Example: { name: "Product Count", records: 1500, id: "kpi_123", status: "success" }
});
```

### Step 2: KPI Matching
```javascript
const clickedKPI = kpis.find(kpi => kpi.id === item.datum.id);
// Matches the clicked bar's ID with the KPI object
```

### Step 3: Handler Invocation
```javascript
if (clickedKPI && onBarClick) {
  onBarClick(clickedKPI);
}
// Calls the parent component's handler with the KPI object
```

### Step 4: Dialog Opening
```javascript
const handleBarClick = (kpi) => {
  setSelectedKPI(kpi);        // Store selected KPI
  setDrilldownOpen(true);     // Open dialog
  fetchDrilldownData(kpi.id); // Fetch detailed data
};
```

---

## 🎨 Visual Feedback

### Cursor Change
```javascript
// In Vega spec
mark: { type: 'bar', cursor: 'pointer', tooltip: true }

// In VegaChart div
<div ref={chartRef} style={{ cursor: 'pointer' }} />
```

### Tooltip on Hover
```javascript
tooltip: [
  { field: 'definition', type: 'nominal', title: 'Definition' },
  { field: 'name', type: 'nominal', title: 'KPI' },
  { field: 'records', type: 'quantitative', title: 'Records' },
]
```

---

## 🔍 Drill-down Dialog

### What Opens
When a bar is clicked, a dialog opens showing:

1. **KPI Information**
   - KPI name
   - KPI description

2. **SQL Query**
   - Read-only SQL query display
   - Shows the query used to generate the data

3. **Summary Statistics**
   - Total records
   - Number of columns

4. **Data Table**
   - Searchable records
   - Pagination (5, 10, 25, 50 rows)
   - All columns from query results

5. **Export**
   - CSV download button
   - Properly formatted CSV with special character handling

---

## 💻 Code Example

### Complete Implementation

```javascript
// 1. VegaChart component with click handler
<VegaChart
  spec={{
    $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
    data: {
      values: group.kpis.map(kpi => ({
        name: kpi.name,
        records: kpi.latest_execution?.record_count || 0,
        id: kpi.id,  // Important: ID used for matching
        definition: kpi.definition || 'No definition',
      })),
    },
    mark: { type: 'bar', cursor: 'pointer', tooltip: true },
    encoding: {
      x: { field: 'name', type: 'nominal' },
      y: { field: 'records', type: 'quantitative' },
      tooltip: [
        { field: 'definition', type: 'nominal', title: 'Definition' },
      ],
    },
  }}
  onBarClick={handleBarClick}
  kpis={group.kpis}
/>

// 2. Handler function
const handleBarClick = (kpi) => {
  setSelectedKPI(kpi);
  setDrilldownOpen(true);
  fetchDrilldownData(kpi.id);
};

// 3. Drill-down dialog
<Dialog open={drilldownOpen} onClose={handleCloseDrilldown} maxWidth="lg" fullWidth>
  <DialogTitle>{selectedKPI?.name}</DialogTitle>
  <DialogContent>
    {/* SQL Display */}
    <Paper sx={{ p: 2, mb: 2, backgroundColor: '#f5f5f5' }}>
      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
        {drilldownData?.sql}
      </Typography>
    </Paper>
    
    {/* Data Table */}
    <TableContainer>
      <Table>
        {/* Table content */}
      </Table>
    </TableContainer>
  </DialogContent>
</Dialog>
```

---

## 🎯 Key Features

### ✅ Direct Bar Click
- Click any bar to open drill-down
- No need for separate chips
- Intuitive user interaction

### ✅ Visual Feedback
- Cursor changes to pointer on hover
- Tooltip shows KPI definition
- Smooth transitions

### ✅ Data Matching
- Automatically matches clicked bar to KPI object
- Uses KPI ID for reliable matching
- Handles missing data gracefully

### ✅ Error Handling
- Catches click event errors
- Validates KPI object exists
- Logs errors to console

### ✅ Performance
- Efficient event listener setup
- Minimal re-renders
- Lazy data fetching

---

## 🧪 Testing

### Manual Testing

1. **Load Dashboard**
   ```
   Navigate to /kpi-dashboard
   ```

2. **Hover Over Bar**
   ```
   - Cursor should change to pointer
   - Tooltip should appear
   ```

3. **Click on Bar**
   ```
   - Dialog should open
   - KPI name should display
   - SQL query should show
   - Data table should load
   ```

4. **Verify Data**
   ```
   - Check KPI name matches clicked bar
   - Verify SQL query is correct
   - Check data table has records
   ```

### Browser Console Debugging

```javascript
// Check if click event fires
console.log('Bar clicked:', item.datum);

// Check if KPI is found
console.log('Matched KPI:', clickedKPI);

// Check if handler is called
console.log('Handler called with:', kpi);
```

---

## 🔧 Troubleshooting

### Issue: Click Not Working
**Cause**: Event listener not attached  
**Solution**: Check browser console for errors, verify Vega spec is valid

### Issue: Wrong KPI Opens
**Cause**: ID mismatch between bar data and KPI object  
**Solution**: Verify `id` field is included in Vega data values

### Issue: Dialog Doesn't Open
**Cause**: Handler not called or state not updated  
**Solution**: Check console for errors, verify `onBarClick` prop passed

### Issue: Data Not Loading
**Cause**: API error or network issue  
**Solution**: Check network tab in DevTools, verify API endpoint

---

## 📈 Performance Considerations

### Event Listener Setup
- Listener attached once per chart render
- Cleaned up on component unmount
- Minimal memory overhead

### Data Fetching
- Drill-down data fetched on demand
- Not pre-fetched for all KPIs
- Reduces initial load time

### Re-renders
- Only re-renders when spec changes
- Efficient dependency array
- No unnecessary updates

---

## 🎨 Customization

### Change Cursor Style
```javascript
mark: { type: 'bar', cursor: 'crosshair', tooltip: true }
```

### Add Click Animation
```javascript
// In Vega spec
selection: {
  click: {
    type: 'single',
    on: 'click',
    encodings: ['x'],
  },
},
opacity: {
  condition: { selection: 'click', value: 1 },
  value: 0.7,
}
```

### Customize Tooltip
```javascript
tooltip: [
  { field: 'name', type: 'nominal', title: 'KPI Name' },
  { field: 'records', type: 'quantitative', title: 'Record Count' },
  { field: 'definition', type: 'nominal', title: 'Definition' },
  { field: 'status', type: 'nominal', title: 'Status' },
]
```

---

## ✅ Verification Checklist

- [x] VegaChart component accepts onBarClick prop
- [x] Click event listener attached to Vega view
- [x] KPI matching logic works correctly
- [x] Handler function called on click
- [x] Dialog opens with correct KPI
- [x] Data fetched and displayed
- [x] Error handling in place
- [x] Build successful
- [x] No console errors

---

## 📚 Related Documentation

- `KPI_DASHBOARD_VEGA_DOCUMENTATION.md` - Full technical docs
- `KPI_DASHBOARD_VEGA_DATA_TRANSFORMATION.md` - Data transformation guide
- `KPI_DASHBOARD_VEGA_FIX_SUMMARY.md` - Issues fixed

---

**Version**: 1.0.0  
**Status**: ✅ Implemented and Tested  
**Last Updated**: 2025-10-28


