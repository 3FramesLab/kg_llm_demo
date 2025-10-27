# Table Aliases UI Guide - Visual Reference

## 🎨 Web UI Layout

### Knowledge Graph View Page

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Knowledge Graph                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────┐  ┌──────────────────────┐ │
│  │                                          │  │  📊 Table Aliases    │ │
│  │                                          │  ├──────────────────────┤ │
│  │                                          │  │ LLM-Learned Business │ │
│  │                                          │  │ Names                │ │
│  │                                          │  │                      │ │
│  │     Force-Directed Graph                │  │ brz_lnd_RBP_GPU      │ │
│  │     (Nodes & Relationships)             │  │ [RBP] [RBP GPU]      │ │
│  │                                          │  │ [GPU]                │ │
│  │                                          │  │                      │ │
│  │                                          │  │ brz_lnd_OPS_EXCEL_GPU│ │
│  │                                          │  │ [OPS] [OPS Excel]    │ │
│  │                                          │  │                      │ │
│  │                                          │  │ brz_lnd_SKU_LIFNR    │ │
│  │                                          │  │ [SKU] [SKU LIFNR]    │ │
│  │                                          │  │                      │ │
│  │                                          │  │ hana_material_master │ │
│  │                                          │  │ [Material]           │ │
│  │                                          │  │ [Material Master]    │ │
│  │                                          │  │ [HANA]               │ │
│  │                                          │  │                      │ │
│  └──────────────────────────────────────────┘  └──────────────────────┘ │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📱 Responsive Design

### Desktop (Wide Screen)
```
┌─────────────────────────────────────────────────────────────┐
│ Graph (60%)              │ Details Panel (40%)              │
│                          │ ┌──────────────────────────────┐ │
│                          │ │ 📊 Table Aliases             │ │
│                          │ │ ┌──────────────────────────┐ │ │
│                          │ │ │ brz_lnd_RBP_GPU          │ │ │
│                          │ │ │ [RBP] [RBP GPU] [GPU]    │ │ │
│                          │ │ │                          │ │ │
│                          │ │ │ brz_lnd_OPS_EXCEL_GPU    │ │ │
│                          │ │ │ [OPS] [OPS Excel]        │ │ │
│                          │ │ └──────────────────────────┘ │ │
│                          │ └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Mobile (Narrow Screen)
```
┌──────────────────────────┐
│ Graph                    │
│ (Full Width)             │
│                          │
│                          │
└──────────────────────────┘
┌──────────────────────────┐
│ 📊 Table Aliases         │
│ ┌──────────────────────┐ │
│ │ brz_lnd_RBP_GPU      │ │
│ │ [RBP] [RBP GPU]      │ │
│ │ [GPU]                │ │
│ │                      │ │
│ │ brz_lnd_OPS_EXCEL_GPU│ │
│ │ [OPS] [OPS Excel]    │ │
│ └──────────────────────┘ │
└──────────────────────────┘
```

---

## 🎯 Panel States

### State 1: No Selection (Aliases Visible)
```
┌──────────────────────────┐
│ 📊 Table Aliases         │ ← Green header
├──────────────────────────┤
│ LLM-Learned Business     │
│ Names                    │
│                          │
│ brz_lnd_RBP_GPU          │ ← Table name
│ [RBP] [RBP GPU] [GPU]    │ ← Alias chips
│                          │
│ brz_lnd_OPS_EXCEL_GPU    │
│ [OPS] [OPS Excel]        │
│                          │
│ (Scrollable if many)     │
└──────────────────────────┘
```

### State 2: Node Selected (Node Details)
```
┌──────────────────────────┐
│ Entity Details           │ ← Purple header
├──────────────────────────┤
│ ID                       │
│ [table_brz_lnd_RBP_GPU]  │
│                          │
│ Label                    │
│ brz_lnd_RBP_GPU          │
│                          │
│ Type                     │
│ [Table]                  │
│                          │
│ [Edit Entity]            │
│ [Delete Entity]          │
└──────────────────────────┘
```

### State 3: Link Selected (Relationship Details)
```
┌──────────────────────────┐
│ Relationship Details     │ ← Purple header
├──────────────────────────┤
│ Source                   │
│ [table_brz_lnd_RBP_GPU]  │
│                          │
│ Target                   │
│ [table_brz_lnd_OPS_...]  │
│                          │
│ Relationship Type        │
│ [CONTAINS]               │
│                          │
│ [Delete Relationship]    │
└──────────────────────────┘
```

---

## 🎨 Color Scheme

### Table Aliases Panel
- **Header Background**: Green gradient (#43e97b → #38f9d7)
- **Header Text**: White
- **Alias Chips**: Light teal background (#e0f7f4)
- **Alias Text**: Dark teal (#00897b)
- **Table Names**: Secondary text color

### Chip Styling
```
┌─────────────────┐
│ [RBP]           │  ← Light teal background
│ [RBP GPU]       │  ← Dark teal text
│ [GPU]           │  ← Small font (0.7rem)
└─────────────────┘
```

---

## 🔄 User Interactions

### Viewing Aliases
1. **Load KG** → Click "View" button
2. **Navigate to View Tab** → See graph visualization
3. **Check Right Panel** → See table aliases automatically
4. **Scroll** → If many aliases, scroll to see all

### Switching Between Views
```
Click Node
  ↓
Show Node Details
  ↓
Click Empty Space
  ↓
Show Table Aliases
  ↓
Click Link
  ↓
Show Link Details
  ↓
Click Empty Space
  ↓
Show Table Aliases (again)
```

---

## 📊 Example Data Display

### Real Example
```
📊 Table Aliases
─────────────────────────────────────────

LLM-Learned Business Names

brz_lnd_RBP_GPU
  [RBP] [RBP GPU] [GPU]

brz_lnd_OPS_EXCEL_GPU
  [OPS] [OPS Excel] [Excel GPU]

brz_lnd_SKU_LIFNR_Excel
  [SKU] [SKU LIFNR] [Excel]

hana_material_master
  [Material] [Material Master] [HANA]

brz_lnd_VENDOR_MASTER
  [Vendor] [Vendor Master] [VENDOR]
```

---

## 🎯 Key Features

✅ **Always Visible**: Shows when no element selected
✅ **Organized**: Grouped by table name
✅ **Scrollable**: Handles many aliases
✅ **Color-Coded**: Green header distinguishes from other panels
✅ **Responsive**: Works on all screen sizes
✅ **Non-Intrusive**: Doesn't interfere with graph interaction

---

## 🚀 How to Use

### For End Users
1. Generate a KG with LLM enhancement
2. Click "View" on the KG
3. Go to "View" tab
4. Look at right panel to see all table aliases
5. Use these names when writing NL queries

### Example Query
```
User sees in UI:
  brz_lnd_RBP_GPU → [RBP] [RBP GPU] [GPU]
  brz_lnd_OPS_EXCEL_GPU → [OPS] [OPS Excel]

User writes query:
  "Show me products in RBP not in OPS Excel"

System resolves:
  "RBP" → brz_lnd_RBP_GPU ✓
  "OPS Excel" → brz_lnd_OPS_EXCEL_GPU ✓
```

---

## 🎉 Benefits

✨ **Transparency**: Users see what aliases are available
✨ **Discoverability**: Easy to find correct table names
✨ **Accuracy**: Reduces query errors
✨ **Learning**: Users learn the business terminology
✨ **Debugging**: Easy to verify alias mappings

---

**Status**: ✅ COMPLETE AND READY TO USE!

