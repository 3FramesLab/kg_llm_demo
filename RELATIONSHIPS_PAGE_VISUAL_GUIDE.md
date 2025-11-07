# Relationships Page - Visual Guide

## Page Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Table Relationships                                            │
│  Create and manage relationships between database tables        │
│  with column mappings                                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  [Create Relationship] [View Relationships]                     │
└─────────────────────────────────────────────────────────────────┘
```

## Tab 1: Create Relationship

```
┌─────────────────────────────────────────────────────────────────┐
│  Create New Relationship                                        │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Relationship Name *                                       │ │
│  │ [Product to Supplier Relationship________________]        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────┐    ┌──────┐    ┌─────────────────┐      │
│  │ Source Table *  │    │  →   │    │ Target Table *  │      │
│  │ [products    ▼] │    │      │    │ [suppliers   ▼] │      │
│  └─────────────────┘    └──────┘    └─────────────────┘      │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Relationship Type                                         │ │
│  │ [REFERENCES                                            ▼] │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  Column Mappings                          [+ Add Mapping]      │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ ┌──────────────┐  🔗  ┌──────────────┐         [🗑️]     │ │
│  │ │ Source Col   │      │ Target Col   │                   │ │
│  │ │ [supplier_id▼]│      │ [id        ▼]│                   │ │
│  │ └──────────────┘      └──────────────┘                   │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ ┌──────────────┐  🔗  ┌──────────────┐         [🗑️]     │ │
│  │ │ Source Col   │      │ Target Col   │                   │ │
│  │ │ [supplier_name▼]│    │ [name      ▼]│                   │ │
│  │ └──────────────┘      └──────────────┘                   │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│                                    [Clear] [Save Relationship]  │
└─────────────────────────────────────────────────────────────────┘
```

## Tab 2: View Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│  All Relationships (3)                          [🔄 Refresh]    │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Product to Supplier Relationship              [✏️] [🗑️]   │ │
│  │                                                           │ │
│  │ [products] → [suppliers]  [REFERENCES]                   │ │
│  │                                                           │ │
│  │ ─────────────────────────────────────────────────────────  │ │
│  │                                                           │ │
│  │ Column Mappings (2)                                       │ │
│  │                                                           │ │
│  │ ┌─────────────────────────────────────────────────────┐  │ │
│  │ │ Source Column    →    Target Column                │  │ │
│  │ ├─────────────────────────────────────────────────────┤  │ │
│  │ │ [supplier_id]    🔗    [id]                        │  │ │
│  │ │ [supplier_name]  🔗    [name]                      │  │ │
│  │ └─────────────────────────────────────────────────────┘  │ │
│  │                                                           │ │
│  │ Created: 11/7/2025, 10:30:00 AM                          │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Order to Customer Relationship                [✏️] [🗑️]   │ │
│  │                                                           │ │
│  │ [orders] → [customers]  [FOREIGN_KEY]                    │ │
│  │                                                           │ │
│  │ ─────────────────────────────────────────────────────────  │ │
│  │                                                           │ │
│  │ Column Mappings (1)                                       │ │
│  │                                                           │ │
│  │ ┌─────────────────────────────────────────────────────┐  │ │
│  │ │ Source Column    →    Target Column                │  │ │
│  │ ├─────────────────────────────────────────────────────┤  │ │
│  │ │ [customer_id]    🔗    [id]                        │  │ │
│  │ └─────────────────────────────────────────────────────┘  │ │
│  │                                                           │ │
│  │ Created: 11/7/2025, 9:15:00 AM                           │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Navigation Menu

```
┌──────────────────────┐
│ DQ-Reconciliation    │
├──────────────────────┤
│ 📊 Overview          │
│ 📄 Schemas           │
│ 🌳 Knowledge Graph   │
│ 🔗 Relationships     │  ← NEW!
│ 🏷️  Column Hints     │
│ 💬 Natural Language  │
│ 📈 NL KPI Management │
│ 📊 Dashboard         │
└──────────────────────┘
```

## Color Scheme

- **Primary Color**: Blue (#1976d2) - Used for buttons, icons, chips
- **Secondary Color**: Pink (#dc004e) - Used for target table chips
- **Success**: Green - Success messages
- **Error**: Red - Error messages, delete buttons
- **Background**: Light gray (#f5f5f5)
- **Paper**: White with subtle shadow

## Icons Used

- **🔗 Link Icon**: Relationships menu item, column mapping connections
- **➕ Add Icon**: Create relationship tab, add mapping button
- **📊 TableChart Icon**: View relationships tab
- **➡️ ArrowForward Icon**: Visual flow between source and target
- **✏️ Edit Icon**: Edit relationship button
- **🗑️ Delete Icon**: Delete relationship/mapping buttons
- **💾 Save Icon**: Save relationship button
- **❌ Cancel Icon**: Clear form button
- **🔄 Refresh Icon**: Refresh relationships list

## Responsive Design

### Desktop (>960px)
- Source and target tables side by side
- Column mappings displayed in full width cards
- All actions visible

### Tablet (600-960px)
- Source and target tables stack vertically
- Column mappings remain side by side
- Compact spacing

### Mobile (<600px)
- All elements stack vertically
- Dropdowns full width
- Touch-friendly button sizes
- Simplified card layout

## User Interactions

### Creating a Relationship
1. User clicks "Create Relationship" tab
2. Fills in relationship name
3. Selects source table → columns load automatically
4. Selects target table → columns load automatically
5. Clicks "Add Mapping" for each column pair
6. Selects source and target columns from dropdowns
7. Clicks "Save Relationship"
8. Success message appears
9. Automatically switches to "View Relationships" tab

### Editing a Relationship
1. User clicks edit icon on a relationship card
2. Form populates with existing data
3. User makes changes
4. Clicks "Update Relationship"
5. Success message appears
6. Relationship updates in the list

### Deleting a Relationship
1. User clicks delete icon
2. Confirmation dialog appears
3. User confirms deletion
4. Relationship removed from list
5. Success message appears

## Validation Messages

### Error Messages
- ❌ "Please fill in all required fields"
- ❌ "Please add at least one column mapping"
- ❌ "Please complete all column mappings"
- ❌ "Failed to save relationship"
- ❌ "Failed to load relationships"

### Success Messages
- ✅ "Relationship created successfully"
- ✅ "Relationship updated successfully"
- ✅ "Relationship deleted successfully"

### Info Messages
- ℹ️ "Click 'Add Mapping' to create column mappings between the source and target tables."
- ℹ️ "No relationships found. Create your first relationship using the 'Create Relationship' tab."

## Loading States

- Circular progress spinner during API calls
- Disabled buttons during loading
- Skeleton loaders for relationship cards (optional enhancement)

## Accessibility Features

- Proper ARIA labels on all interactive elements
- Keyboard navigation support
- Focus indicators on form fields
- Screen reader friendly
- High contrast text
- Touch-friendly tap targets (48px minimum)

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Considerations

- Lazy loading of columns when tables selected
- Debounced search (future enhancement)
- Pagination for large relationship lists (future enhancement)
- Optimistic UI updates
- Efficient re-rendering with React hooks

