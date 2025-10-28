# KPI Dashboard with Vega-Lite - Advanced Guide

## 🔧 Customization & Extension

### 1. Modify Chart Colors

**File**: `web-app/src/components/KPIDashboardVega.js` (Line ~280)

```javascript
// Current color scheme
scale: {
  domain: ['success', 'failed', 'pending'],
  range: ['#4caf50', '#f44336', '#ff9800'],
}

// Custom colors
scale: {
  domain: ['success', 'failed', 'pending'],
  range: ['#2196F3', '#FF5722', '#FFC107'],  // Blue, Deep Orange, Amber
}
```

### 2. Change Chart Height

**File**: `web-app/src/components/KPIDashboardVega.js` (Line ~300)

```javascript
// Current
height: 300,

// Larger chart
height: 400,

// Smaller chart
height: 250,
```

### 3. Modify Pagination Options

**File**: `web-app/src/components/KPIDashboardVega.js` (Line ~425)

```javascript
// Current
rowsPerPageOptions={[5, 10, 25, 50]}

// Custom options
rowsPerPageOptions={[10, 20, 50, 100]}
```

### 4. Change Default Rows Per Page

**File**: `web-app/src/components/KPIDashboardVega.js` (Line ~44)

```javascript
// Current
const [rowsPerPage, setRowsPerPage] = useState(10);

// Show 25 rows by default
const [rowsPerPage, setRowsPerPage] = useState(25);
```

## 📊 Advanced Vega-Lite Customization

### Add Data Labels on Bars

```javascript
// In the Vega-Lite spec, add text mark
{
  mark: { type: 'bar', cursor: 'pointer', tooltip: true },
  // Add this:
  layer: [
    {
      mark: 'bar',
      encoding: { /* existing encoding */ }
    },
    {
      mark: { type: 'text', align: 'center', baseline: 'bottom' },
      encoding: {
        text: { field: 'records', type: 'quantitative' },
        y: { field: 'records', type: 'quantitative' }
      }
    }
  ]
}
```

### Add Sorting to Chart

```javascript
// In x encoding
x: {
  field: 'name',
  type: 'nominal',
  sort: { field: 'records', order: 'descending' },  // Sort by records
  axis: { labelAngle: -45, labelBound: true },
  title: 'KPI Name',
}
```

### Add Trend Line

```javascript
// Add to layer
{
  mark: { type: 'line', point: true, color: 'red' },
  transform: [
    { regression: 'records', on: 'name' }
  ],
  encoding: {
    x: { field: 'name', type: 'nominal' },
    y: { field: 'records', type: 'quantitative' }
  }
}
```

## 🎨 Styling Customization

### Change Dialog Width

**File**: `web-app/src/components/KPIDashboardVega.js` (Line ~340)

```javascript
// Current
<Dialog open={drilldownOpen} onClose={handleCloseDrilldown} maxWidth="lg" fullWidth>

// Smaller dialog
<Dialog open={drilldownOpen} onClose={handleCloseDrilldown} maxWidth="md" fullWidth>

// Larger dialog
<Dialog open={drilldownOpen} onClose={handleCloseDrilldown} maxWidth="xl" fullWidth>
```

### Customize Table Styling

```javascript
// Add to Table component
<Table size="small" sx={{ 
  '& thead': { backgroundColor: '#e3f2fd' },
  '& tbody tr:hover': { backgroundColor: '#f5f5f5' },
  '& th': { fontWeight: 'bold', color: '#1976d2' }
}}>
```

### Change Paper Background

```javascript
// Current
<Paper key={group.group_name} sx={{ p: 3, backgroundColor: '#fafafa' }}>

// White background
<Paper key={group.group_name} sx={{ p: 3, backgroundColor: '#ffffff' }}>

// Light blue
<Paper key={group.group_name} sx={{ p: 3, backgroundColor: '#e3f2fd' }}>
```

## 🔌 API Integration Customization

### Add Custom Headers to API Calls

```javascript
const fetchDashboardData = async () => {
  try {
    setLoading(true);
    setError(null);
    const response = await fetch(`${API_BASE_URL}/v1/landing-kpi/dashboard`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'X-Custom-Header': 'value'
      }
    });
    // ... rest of code
  }
}
```

### Add Request Timeout

```javascript
const fetchWithTimeout = (url, timeout = 5000) => {
  return Promise.race([
    fetch(url),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Request timeout')), timeout)
    )
  ]);
};
```

### Add Retry Logic

```javascript
const fetchWithRetry = async (url, retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      return await fetch(url);
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
};
```

## 🧪 Testing Examples

### Unit Test - Component Rendering

```javascript
import { render, screen } from '@testing-library/react';
import KPIDashboardVega from './KPIDashboardVega';

test('renders dashboard title', () => {
  render(<KPIDashboardVega />);
  expect(screen.getByText('KPI Dashboard')).toBeInTheDocument();
});
```

### Integration Test - API Call

```javascript
test('fetches and displays dashboard data', async () => {
  const mockData = {
    groups: [{
      group_name: 'Test Group',
      kpis: [{
        id: '1',
        name: 'Test KPI',
        latest_execution: { status: 'success', record_count: 100 }
      }]
    }]
  };

  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve(mockData)
    })
  );

  render(<KPIDashboardVega />);
  await waitFor(() => {
    expect(screen.getByText('Test Group')).toBeInTheDocument();
  });
});
```

### Test - CSV Export

```javascript
test('exports data to CSV', async () => {
  const mockData = {
    records: [
      { id: 1, name: 'Item 1' },
      { id: 2, name: 'Item 2' }
    ]
  };

  // Mock the download
  const mockBlob = new Blob(['csv content']);
  global.URL.createObjectURL = jest.fn(() => 'blob:mock');

  // Test export function
  // Verify CSV content and download triggered
});
```

## 📈 Performance Optimization

### Memoize Group Sections

```javascript
const GroupSection = React.memo(({ group, onKPIClick }) => (
  <Paper key={group.group_name} sx={{ p: 3 }}>
    {/* Group content */}
  </Paper>
));
```

### Lazy Load Drill-down Data

```javascript
const [drilldownData, setDrilldownData] = useState(null);

// Only fetch when dialog opens
useEffect(() => {
  if (drilldownOpen && selectedKPI) {
    fetchDrilldownData(selectedKPI.id);
  }
}, [drilldownOpen, selectedKPI]);
```

### Debounce Search

```javascript
import { useCallback } from 'react';

const handleSearchChange = useCallback(
  debounce((value) => {
    setSearchFilter(value);
    setPage(0);
  }, 300),
  []
);
```

## 🔐 Security Enhancements

### Sanitize User Input

```javascript
import DOMPurify from 'dompurify';

const sanitizedSearch = DOMPurify.sanitize(searchFilter);
```

### Validate API Response

```javascript
const validateDashboardData = (data) => {
  if (!data.groups || !Array.isArray(data.groups)) {
    throw new Error('Invalid dashboard data format');
  }
  return data;
};
```

### Escape HTML in Records

```javascript
const escapeHtml = (text) => {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
};
```

## 🚀 Advanced Features

### Add Real-time Updates

```javascript
useEffect(() => {
  const interval = setInterval(() => {
    fetchDashboardData();
  }, 30000); // Refresh every 30 seconds

  return () => clearInterval(interval);
}, []);
```

### Add WebSocket Support

```javascript
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8000/kpi-updates');
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    setDashboardData(data);
  };

  return () => ws.close();
}, []);
```

### Add Caching

```javascript
const cache = new Map();

const fetchWithCache = async (url) => {
  if (cache.has(url)) {
    return cache.get(url);
  }
  
  const response = await fetch(url);
  const data = await response.json();
  cache.set(url, data);
  return data;
};
```

## 📊 Custom Metrics

### Add Custom Y-axis Metric

```javascript
// Allow user to select metric
const [metric, setMetric] = useState('records');

// Update chart encoding
y: {
  field: metric,  // 'records', 'execution_count', 'avg_time', etc.
  type: 'quantitative',
  title: metric.charAt(0).toUpperCase() + metric.slice(1),
}
```

### Add Comparison View

```javascript
// Show two metrics side by side
const [compareMetric, setCompareMetric] = useState(null);

// Create two charts
<Box sx={{ display: 'flex', gap: 2 }}>
  <Box sx={{ flex: 1 }}>{/* Chart 1 */}</Box>
  <Box sx={{ flex: 1 }}>{/* Chart 2 */}</Box>
</Box>
```

## 🎯 Accessibility Improvements

### Add ARIA Labels

```javascript
<Dialog
  open={drilldownOpen}
  onClose={handleCloseDrilldown}
  aria-labelledby="drill-down-title"
  aria-describedby="drill-down-description"
>
  <DialogTitle id="drill-down-title">
    {selectedKPI?.name}
  </DialogTitle>
</Dialog>
```

### Add Keyboard Navigation

```javascript
const handleKeyDown = (e) => {
  if (e.key === 'Escape') {
    handleCloseDrilldown();
  }
};

useEffect(() => {
  window.addEventListener('keydown', handleKeyDown);
  return () => window.removeEventListener('keydown', handleKeyDown);
}, []);
```

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-28


