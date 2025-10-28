# KPI Dashboard with Vega-Lite - Visual Guide

## 🎨 Dashboard Layout Visualization

### Full Dashboard View
```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ KPI Dashboard                                  [Refresh]    │   │
│  │ 15 KPIs across 3 groups                                    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 📊 Data Quality                                             │   │
│  │ 5 KPIs • Total Records: 15,000                             │   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │                                                        │  │   │
│  │  │  [Bar Chart - Vega-Lite]                             │  │   │
│  │  │  ▓▓▓▓▓  ▓▓▓▓  ▓▓▓▓▓▓  ▓▓▓  ▓▓▓▓▓▓▓                  │  │   │
│  │  │  KPI1  KPI2  KPI3   KPI4 KPI5                        │  │   │
│  │  │                                                        │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                                                              │   │
│  │  [KPI1] [KPI2] [KPI3] [KPI4] [KPI5]                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 📊 Reconciliation                                           │   │
│  │ 5 KPIs • Total Records: 8,500                              │   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │                                                        │  │   │
│  │  │  [Bar Chart - Vega-Lite]                             │  │   │
│  │  │  ▓▓▓▓  ▓▓▓▓▓▓  ▓▓▓  ▓▓▓▓▓  ▓▓▓▓▓▓▓                  │  │   │
│  │  │  KPI6  KPI7   KPI8 KPI9  KPI10                       │  │   │
│  │  │                                                        │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                                                              │   │
│  │  [KPI6] [KPI7] [KPI8] [KPI9] [KPI10]                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ... more groups ...                                                 │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## 📊 Bar Chart Details

### Chart Components
```
Record Count (Y-axis)
    │
 5K │     ┌─────┐
    │     │     │
 4K │     │     │  ┌─────┐
    │     │     │  │     │
 3K │  ┌──┤     ├──┤     ├──┐
    │  │  │     │  │     │  │
 2K │  │  │     │  │     │  │  ┌─────┐
    │  │  │     │  │     │  │  │     │
 1K │  │  │     │  │     │  │  │     │
    │  │  │     │  │     │  │  │     │
  0 └──┴──┴─────┴──┴─────┴──┴──┴─────┴──
    KPI1 KPI2  KPI3 KPI4  KPI5 KPI6

    🟢 Success  🔴 Failed  🟠 Pending
```

### Hover Tooltip
```
┌──────────────────┐
│ KPI: Product     │
│ Records: 1,500   │
│ Status: Success  │
│ ID: kpi_123      │
└──────────────────┘
```

## 🔍 Drill-down Dialog

### Dialog Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Product Count                                          [X]   │
│ Total products in system                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ SQL Query:                                                  │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ SELECT * FROM products WHERE status = 'active'      │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ ┌──────────────────────┐  ┌──────────────────────┐         │
│ │ Total Records: 1,500 │  │ Columns: 8           │         │
│ └──────────────────────┘  └──────────────────────┘         │
│                                                              │
│ [Search records...]                                         │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ ID  │ Name      │ Category │ Price │ Status │ Date  │   │
│ ├─────┼───────────┼──────────┼───────┼────────┼───────┤   │
│ │ 1   │ Product A │ Tech     │ $99   │ Active │ 2025  │   │
│ │ 2   │ Product B │ Home     │ $49   │ Active │ 2025  │   │
│ │ 3   │ Product C │ Tech     │ $199  │ Active │ 2025  │   │
│ │ ... │ ...       │ ...      │ ...   │ ...    │ ...   │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ Rows per page: [10 ▼]  1-10 of 1,500  [< 1 2 3 ... >]    │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│ [Export CSV]  [Close]                                       │
└─────────────────────────────────────────────────────────────┘
```

## 🎨 Color Scheme

### Status Colors
```
Success  ████████████  #4caf50  (Green)
Failed   ████████████  #f44336  (Red)
Pending  ████████████  #ff9800  (Orange)
Primary  ████████████  #1976d2  (Blue)
```

### Material-UI Palette
```
Background: #f5f5f5  (Light Gray)
Paper:      #ffffff  (White)
Text:       #212121  (Dark Gray)
Divider:    #e0e0e0  (Light Gray)
```

## 📱 Responsive Breakpoints

### Mobile (< 600px)
```
┌─────────────────┐
│ KPI Dashboard   │
│ 15 KPIs         │
│ [Refresh]       │
├─────────────────┤
│ Data Quality    │
│ 5 KPIs          │
│ [Chart]         │
│ [KPI1]          │
│ [KPI2]          │
│ [KPI3]          │
│ [KPI4]          │
│ [KPI5]          │
├─────────────────┤
│ Reconciliation  │
│ 5 KPIs          │
│ [Chart]         │
│ [KPI6]          │
│ [KPI7]          │
│ [KPI8]          │
│ [KPI9]          │
│ [KPI10]         │
└─────────────────┘
```

### Tablet (600-960px)
```
┌──────────────────────────────────────┐
│ KPI Dashboard          [Refresh]     │
│ 15 KPIs across 3 groups              │
├──────────────────────────────────────┤
│ Data Quality                          │
│ 5 KPIs • Total: 15,000               │
│ [Chart - 2 columns]                  │
│ [KPI1] [KPI2] [KPI3] [KPI4] [KPI5]  │
├──────────────────────────────────────┤
│ Reconciliation                        │
│ 5 KPIs • Total: 8,500                │
│ [Chart - 2 columns]                  │
│ [KPI6] [KPI7] [KPI8] [KPI9] [KPI10] │
└──────────────────────────────────────┘
```

### Desktop (> 960px)
```
┌────────────────────────────────────────────────────────────┐
│ KPI Dashboard                              [Refresh]       │
│ 15 KPIs across 3 groups                                    │
├────────────────────────────────────────────────────────────┤
│ Data Quality                                                │
│ 5 KPIs • Total: 15,000                                     │
│ [Chart - Full Width]                                       │
│ [KPI1] [KPI2] [KPI3] [KPI4] [KPI5]                        │
├────────────────────────────────────────────────────────────┤
│ Reconciliation                                              │
│ 5 KPIs • Total: 8,500                                      │
│ [Chart - Full Width]                                       │
│ [KPI6] [KPI7] [KPI8] [KPI9] [KPI10]                       │
└────────────────────────────────────────────────────────────┘
```

## 🔄 User Interaction Flow

### Flow Diagram
```
┌─────────────────┐
│  Load Dashboard │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ Fetch Dashboard Data    │
│ GET /v1/landing-kpi/... │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Display Groups & Charts │
└────────┬────────────────┘
         │
         ├─────────────────────────┐
         │                         │
         ▼                         ▼
    ┌─────────┐          ┌──────────────┐
    │ Refresh │          │ Click KPI    │
    └────┬────┘          └────┬─────────┘
         │                    │
         │                    ▼
         │            ┌──────────────────┐
         │            │ Open Drill-down  │
         │            │ Dialog           │
         │            └────┬─────────────┘
         │                 │
         │                 ▼
         │        ┌──────────────────────┐
         │        │ Fetch Drill-down Data│
         │        │ GET /v1/landing-kpi/ │
         │        │ {kpi_id}/latest-...  │
         │        └────┬─────────────────┘
         │             │
         │             ▼
         │        ┌──────────────────────┐
         │        │ Display Data Table   │
         │        │ with Pagination      │
         │        └────┬─────────────────┘
         │             │
         │             ├──────────────┐
         │             │              │
         │             ▼              ▼
         │        ┌────────┐    ┌──────────┐
         │        │ Search │    │ Export   │
         │        │ Filter │    │ CSV      │
         │        └────────┘    └──────────┘
         │
         └─────────────────────────┘
```

## 📊 Data Flow

### API Response Structure
```
Dashboard API Response:
{
  "groups": [
    {
      "group_name": "Data Quality",
      "kpis": [
        {
          "id": "kpi_123",
          "name": "Product Count",
          "description": "Total products",
          "latest_execution": {
            "status": "success",
            "record_count": 1500
          }
        }
      ]
    }
  ]
}

Drill-down API Response:
{
  "sql": "SELECT * FROM products WHERE...",
  "records": [
    { "id": 1, "name": "Product A", "count": 100 },
    { "id": 2, "name": "Product B", "count": 200 }
  ]
}
```

## 🎯 Component Hierarchy

```
KPIDashboardVega
├── Header
│   ├── Title
│   ├── Summary Stats
│   └── Refresh Button
├── Group Sections (Map)
│   ├── Group Header
│   ├── Vega-Lite Chart
│   └── KPI Chips (Map)
│       └── Chip (Clickable)
└── Drill-down Dialog
    ├── Dialog Title
    ├── Dialog Content
    │   ├── SQL Display
    │   ├── Summary Stats
    │   ├── Search Filter
    │   └── Data Table
    │       ├── Table Head
    │       ├── Table Body
    │       └── Pagination
    └── Dialog Actions
        ├── Export Button
        └── Close Button
```

## 🎨 Styling Hierarchy

```
Container (maxWidth="xl")
├── Box (Header)
│   ├── Typography (h4)
│   ├── Typography (body2)
│   └── Button
├── Box (Groups)
│   └── Paper (Group Section)
│       ├── Box (Group Header)
│       │   ├── Typography (h6)
│       │   └── Typography (body2)
│       ├── Box (Chart Container)
│       │   ├── VegaLite (Chart)
│       │   └── Box (Chips)
│       │       └── Chip (KPI)
│       └── Box (Drill-down Dialog)
│           ├── DialogTitle
│           ├── DialogContent
│           │   ├── Paper (SQL)
│           │   ├── Grid (Stats)
│           │   ├── TextField (Search)
│           │   └── TableContainer
│           │       └── Table
│           └── DialogActions
└── ...
```

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-28


