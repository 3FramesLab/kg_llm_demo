# Column Hints UX - Quick Start Guide

## Overview

A complete React + Material-UI interface for managing column hints in your data quality reconciliation system.

## What Was Created

### 1. **Main Pages**
- `src/pages/HintsManagement.js` - Main hints management page with tabs for overview, editing, and search

### 2. **Components**
- `src/components/TableHintsView.js` - Table-level hints display and column list
- `src/components/ColumnHintEditor.js` - Detailed column hint editor with full CRUD
- `src/components/HintsSearch.js` - Search results display
- `src/components/HintsStatistics.js` - Statistics dashboard

### 3. **Services**
- `src/services/api.js` - Updated with 14 new API endpoints for hints management

### 4. **Routing**
- `src/App.js` - Added route `/hints-management`
- `src/components/Layout.js` - Added "Column Hints" menu item

## Features

### ✅ Tables Overview
- Grid view of all tables
- Shows column counts
- Business names and descriptions
- Click to edit

### ✅ Hint Editor
- Edit table-level hints (name, description, aliases, category)
- Expandable column rows
- Inline editing of all hint fields
- Add/remove aliases, terms, examples, business rules
- Toggle searchable/filterable/aggregatable flags

### ✅ AI Generation
- Auto-generate hints for individual columns
- Bulk generate for entire table
- One-click regeneration

### ✅ Search
- Real-time search across all hints
- Match by business name, aliases, or common terms
- Navigate directly to table editor from results

### ✅ Version Control
- Create version snapshots
- Export hints to JSON
- Track who updated what and when

### ✅ Statistics
- Total tables and columns
- Auto-generated vs manual count
- Verification progress
- Last updated info

## Getting Started

### Prerequisites
1. Backend API running on `http://localhost:8000`
2. Hints initialized (run the initialization script)
3. Node.js and npm installed

### Installation
```bash
cd web-app
npm install  # If not already done
npm start
```

### First Time Setup

1. **Initialize Hints (Backend)**
   ```bash
   # From project root
   python scripts/initialize_hints_from_schema.py --schema schemas/newdqschemanov.json --use-llm
   ```

2. **Start Backend**
   ```bash
   # Make sure your FastAPI backend is running
   # The hints API should be available at /api/kg/hints/
   ```

3. **Start Frontend**
   ```bash
   cd web-app
   npm start
   ```

4. **Access the UI**
   - Navigate to `http://localhost:3000/hints-management`
   - Or click "Column Hints" in the sidebar

## Usage Workflow

### View Tables
1. Click "Column Hints" in sidebar
2. See all tables in grid view
3. Statistics show at the top

### Edit Table Hints
1. Click on a table card
2. Click edit icon (✏️) next to "Table Information"
3. Update business name, description, aliases, category
4. Click save ✓

### Edit Column Hints
1. Select a table
2. Click expand icon (▼) on any column row
3. Click "Edit" button
4. Update all fields:
   - Business name
   - Description
   - Semantic type (dropdown)
   - Role (dropdown)
   - Priority (dropdown)
   - Aliases (add/remove chips)
   - Common terms
   - Examples
   - Business rules
   - Flags (searchable, filterable, aggregatable)
   - User notes
5. Click "Save"

### Generate Hints with AI
1. **Single Column**: Click sparkle icon (✨) in column row
2. **Bulk Generation**:
   - Select a table
   - Click "Generate Hints" button at top
   - Confirm prompt
   - Wait for completion

### Search Hints
1. Type search term in top search bar
2. Press Enter or click "Search"
3. View results in "Search Results" tab
4. Click "View" to navigate to that table

### Version Control
1. Click "Save Version" button
2. Enter version name (e.g., "v1.0")
3. Add optional comment
4. Click OK

## UI Components Breakdown

### Main Layout
```
┌─────────────────────────────────────────────────────────┐
│  Header: "Column Hints Management"                      │
├─────────────────────────────────────────────────────────┤
│  Search Bar | Refresh | Save Version | Generate | Export│
├─────────────────────────────────────────────────────────┤
│  Statistics Cards (4 cards)                             │
│  - Total Tables | Total Columns | Auto-Gen | Verified   │
├─────────────────────────────────────────────────────────┤
│  Tabs: [Tables Overview] [Edit Hints] [Search Results]  │
├─────────────────────────────────────────────────────────┤
│  Tab Content Area                                        │
│                                                          │
│  [Tables Overview]:                                      │
│    ┌──────┐ ┌──────┐ ┌──────┐                          │
│    │Table │ │Table │ │Table │ (Grid of cards)           │
│    │ Card │ │ Card │ │ Card │                           │
│    └──────┘ └──────┘ └──────┘                          │
│                                                          │
│  [Edit Hints]:                                           │
│    Table Information (editable)                          │
│    Column List (expandable rows)                         │
│    - Click row to expand editor                          │
│                                                          │
│  [Search Results]:                                       │
│    List of matching columns                              │
│    - Click to navigate to table                          │
└─────────────────────────────────────────────────────────┘
```

### Column Editor (Expanded)
```
┌─────────────────────────────────────────────────────────┐
│  Edit Column Hints                      [Save] [Cancel]  │
├─────────────────────────────────────────────────────────┤
│  Business Name: [___________]  Data Type: [NVARCHAR(18)]│
│  Description: [________________________________]          │
│  Semantic Type: [dropdown] Role: [dropdown]              │
│  Priority: [dropdown]                                    │
│                                                          │
│  Aliases:                                                │
│  [Add alias...] [Add]                                    │
│  [product × ] [item × ] [sku × ]                        │
│                                                          │
│  Common Terms:                                           │
│  [Add term...] [Add]                                     │
│  [material × ] [product × ]                             │
│                                                          │
│  Examples: [MAT001, PRD-567]                            │
│  Business Rules: [• Rule 1 × ] [• Rule 2 × ]            │
│                                                          │
│  ☑ Searchable  ☑ Filterable  ☐ Aggregatable            │
│  User Notes: [___________]                               │
└─────────────────────────────────────────────────────────┘
```

## API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/kg/hints/` | GET | Get all hints |
| `/api/kg/hints/statistics` | GET | Get statistics |
| `/api/kg/hints/table/{table}` | GET | Get table hints |
| `/api/kg/hints/column/{table}/{col}` | GET | Get column hints |
| `/api/kg/hints/table` | POST | Update table hints |
| `/api/kg/hints/column` | POST | Update column hints |
| `/api/kg/hints/search` | POST | Search hints |
| `/api/kg/hints/version` | POST | Create version |
| `/api/kg/hints/generate` | POST | Generate single column |
| `/api/kg/hints/generate/bulk` | POST | Bulk generate |
| `/api/kg/hints/export` | GET | Export to file |

## Keyboard Shortcuts

- **Enter** in search box → Search
- **Enter** when adding alias/term → Add to list
- **Escape** → Cancel edit (planned)

## Tips & Best Practices

### For End Users
1. **Start with Overview**: Browse all tables to understand the schema
2. **Use Search**: Find columns by business terms quickly
3. **Verify AI Hints**: Review auto-generated hints before marking verified
4. **Add Context**: Include user notes for future reference
5. **Save Versions**: Create snapshots before major changes

### For Admins
1. **Bulk Generate First**: Use AI to create initial hints
2. **Review & Refine**: Domain experts should verify and enhance
3. **Regular Backups**: Use "Export" feature weekly
4. **Track Progress**: Monitor statistics dashboard
5. **Document Changes**: Use version comments to track what changed

## Troubleshooting

### UI doesn't load
- Check that backend is running on port 8000
- Verify API endpoints are accessible
- Check browser console for errors

### Search returns no results
- Ensure hints are initialized
- Check that `searchable: true` for columns
- Verify backend API is responding

### Can't save changes
- Check browser console for API errors
- Verify user has write permissions
- Ensure backend is not in read-only mode

### Bulk generation fails
- Check that OpenAI API key is configured in backend
- Verify schema file path is correct
- Check backend logs for rate limiting

## Advanced Features

### Custom Semantic Types
Add new types by editing `ColumnHintEditor.js`:
```javascript
const SEMANTIC_TYPES = [
  'identifier', 'measure', 'dimension',
  'date', 'flag', 'description', 'attribute',
  'your_custom_type'  // Add here
];
```

### Bulk Operations
Select multiple tables (planned feature):
- Bulk generate for selected tables
- Bulk export
- Bulk verify

### Integration with NL-to-SQL
The hints are used by:
1. Natural language query parser
2. SQL generation engine
3. Query suggestion system

## Future Enhancements

- [ ] Bulk select for tables
- [ ] Import hints from file (UI)
- [ ] Undo/redo functionality
- [ ] Hint diff viewer (compare versions)
- [ ] Collaboration features (comments, approvals)
- [ ] Column usage statistics
- [ ] Smart suggestions based on column name patterns

## Support

For issues or questions:
- Check backend logs for API errors
- Review browser console for frontend errors
- Consult `docs/COLUMN_HINTS_GUIDE.md` for detailed API docs

## Screenshots Reference

### Tables Overview
Grid of table cards showing:
- Business name (large text)
- Technical name (gray text)
- Description
- Column count chip
- Category chip (if set)

### Column List
Table with columns:
- Expand icon
- Column name (monospace)
- Business name
- Semantic type chip
- Priority chip (colored)
- Status icons (verified/auto-generated/warning)
- Actions (generate button)

### Column Editor
Full-width form with:
- Text fields (business name, description)
- Dropdowns (semantic type, role, priority)
- Chip input fields (aliases, terms, examples)
- List with delete (business rules)
- Toggles (flags)
- Multiline text (user notes)

---

**Ready to use!** Access at `http://localhost:3000/hints-management`
