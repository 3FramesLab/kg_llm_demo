# Relationships Page - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Backend server running on `http://localhost:8000`
- Frontend development server running on `http://localhost:3000`
- At least one schema loaded in the system

### Starting the Application

#### 1. Start Backend Server
```bash
# From project root
python -m uvicorn kg_builder.main:app --reload --port 8000
```

#### 2. Start Frontend Server
```bash
# From web-app directory
cd web-app
npm start
```

#### 3. Access the Application
Open browser to: `http://localhost:3000`

## 📋 Quick Test Checklist

### ✅ Test 1: Navigation
1. Open the application
2. Look for "Relationships" in the sidebar menu (with 🔗 icon)
3. Click on "Relationships"
4. Verify page loads with two tabs: "Create Relationship" and "View Relationships"

### ✅ Test 2: Create a Simple Relationship
1. Go to "Create Relationship" tab
2. Enter name: `Test Product Supplier`
3. Select source table: `products` (or any available schema)
4. Select target table: `suppliers` (or any available schema)
5. Select relationship type: `REFERENCES`
6. Click "Add Mapping"
7. Select source column: `supplier_id`
8. Select target column: `id`
9. Click "Save Relationship"
10. Verify success message appears
11. Verify page switches to "View Relationships" tab
12. Verify new relationship appears in the list

### ✅ Test 3: View Relationships
1. Go to "View Relationships" tab
2. Verify relationship card shows:
   - Relationship name
   - Source and target tables with chips
   - Relationship type badge
   - Column mappings table
   - Edit and delete buttons
   - Timestamp

### ✅ Test 4: Edit Relationship
1. Click edit icon (✏️) on a relationship
2. Verify form populates with existing data
3. Change relationship name to: `Updated Test Relationship`
4. Add another column mapping
5. Click "Update Relationship"
6. Verify success message
7. Go to "View Relationships" tab
8. Verify changes are reflected

### ✅ Test 5: Delete Relationship
1. Go to "View Relationships" tab
2. Click delete icon (🗑️) on a relationship
3. Verify confirmation dialog appears
4. Click "OK" to confirm
5. Verify success message
6. Verify relationship is removed from list

### ✅ Test 6: Form Validation
1. Go to "Create Relationship" tab
2. Try clicking "Save Relationship" without filling any fields
3. Verify error message: "Please fill in all required fields"
4. Fill in name and tables but don't add mappings
5. Try saving
6. Verify error message: "Please add at least one column mapping"
7. Add a mapping but leave columns empty
8. Try saving
9. Verify error message: "Please complete all column mappings"

### ✅ Test 7: Clear Form
1. Fill in some form fields
2. Add a few column mappings
3. Click "Clear" button
4. Verify all fields are reset
5. Verify column mappings are cleared

### ✅ Test 8: Multiple Column Mappings
1. Create a new relationship
2. Click "Add Mapping" 5 times
3. Fill in all 5 mappings with different columns
4. Save the relationship
5. View the relationship
6. Verify all 5 mappings are displayed correctly

## 🧪 API Testing with cURL

### Create Relationship
```bash
curl -X POST "http://localhost:8000/v1/relationships" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Product to Supplier",
    "source_table": "products",
    "target_table": "suppliers",
    "column_mappings": [
      {"source_column": "supplier_id", "target_column": "id"},
      {"source_column": "supplier_name", "target_column": "name"}
    ],
    "relationship_type": "REFERENCES"
  }'
```

### List All Relationships
```bash
curl -X GET "http://localhost:8000/v1/relationships"
```

### Get Specific Relationship
```bash
curl -X GET "http://localhost:8000/v1/relationships/{relationship_id}"
```

### Update Relationship
```bash
curl -X PUT "http://localhost:8000/v1/relationships/{relationship_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Product to Supplier",
    "column_mappings": [
      {"source_column": "supplier_id", "target_column": "id"}
    ]
  }'
```

### Delete Relationship
```bash
curl -X DELETE "http://localhost:8000/v1/relationships/{relationship_id}"
```

## 🐛 Troubleshooting

### Issue: "Failed to load schemas"
**Solution**: 
- Verify backend server is running
- Check that schema files exist in `schemas/` directory
- Check browser console for API errors

### Issue: "Failed to save relationship"
**Solution**:
- Check browser console for detailed error
- Verify all required fields are filled
- Ensure at least one column mapping exists
- Check backend logs for server errors

### Issue: Relationships not appearing
**Solution**:
- Click "Refresh" button
- Check browser console for errors
- Verify backend API is responding: `curl http://localhost:8000/v1/relationships`

### Issue: Column dropdowns are empty
**Solution**:
- Currently using mock data for columns
- Verify source and target tables are selected
- Check browser console for errors

### Issue: Page not loading
**Solution**:
- Verify route is added in `App.js`
- Check for JavaScript errors in console
- Verify import statement is correct
- Clear browser cache and reload

## 📊 Sample Test Data

### Sample Relationship 1: Product to Supplier
```json
{
  "name": "Product to Supplier Relationship",
  "source_table": "products",
  "target_table": "suppliers",
  "column_mappings": [
    {"source_column": "supplier_id", "target_column": "id"},
    {"source_column": "supplier_name", "target_column": "name"}
  ],
  "relationship_type": "REFERENCES"
}
```

### Sample Relationship 2: Order to Customer
```json
{
  "name": "Order to Customer Relationship",
  "source_table": "orders",
  "target_table": "customers",
  "column_mappings": [
    {"source_column": "customer_id", "target_column": "id"},
    {"source_column": "customer_email", "target_column": "email"}
  ],
  "relationship_type": "FOREIGN_KEY"
}
```

### Sample Relationship 3: Product to Category
```json
{
  "name": "Product to Category Relationship",
  "source_table": "products",
  "target_table": "categories",
  "column_mappings": [
    {"source_column": "category_id", "target_column": "id"}
  ],
  "relationship_type": "BELONGS_TO"
}
```

## 🎯 Expected Results

### After Creating a Relationship
- ✅ Success message: "Relationship created successfully"
- ✅ Form is cleared
- ✅ Automatically switches to "View Relationships" tab
- ✅ New relationship appears in the list
- ✅ Relationship has a unique ID
- ✅ Timestamps are set

### After Editing a Relationship
- ✅ Success message: "Relationship updated successfully"
- ✅ Changes are reflected in the list
- ✅ Updated timestamp is different from created timestamp
- ✅ Relationship ID remains the same

### After Deleting a Relationship
- ✅ Success message: "Relationship deleted successfully"
- ✅ Relationship is removed from the list
- ✅ Total count decreases by 1

## 📝 Notes

1. **In-Memory Storage**: Relationships are stored in memory and will be lost when the backend server restarts. For production, implement database persistence.

2. **Mock Columns**: Column lists are currently mocked. For production, integrate with actual schema parsing to fetch real columns.

3. **No Authentication**: Current implementation has no authentication. Add authentication for production use.

4. **No Pagination**: All relationships are loaded at once. Implement pagination for large datasets.

5. **No Search**: No search functionality yet. Add search/filter for better UX with many relationships.

## 🔄 Next Steps

After verifying the basic functionality:

1. **Test with Real Schemas**: Load actual schema files and test with real table names
2. **Integrate Column Fetching**: Connect to schema parser to get actual columns
3. **Add Database Persistence**: Replace in-memory storage with SQLite/PostgreSQL
4. **Add Search/Filter**: Implement search and filtering for relationships
5. **Add Validation**: Validate relationships against actual schema structure
6. **Add Export/Import**: Allow exporting and importing relationships
7. **Add Visualization**: Create a graph view of all relationships
8. **Add Tests**: Write unit and integration tests

## 📞 Support

If you encounter any issues:
1. Check browser console for errors
2. Check backend logs for server errors
3. Verify all prerequisites are met
4. Review the implementation documentation
5. Check the API endpoints are responding correctly

## ✨ Success Criteria

The implementation is successful if:
- ✅ All 8 tests pass
- ✅ No console errors
- ✅ UI is responsive and user-friendly
- ✅ All CRUD operations work correctly
- ✅ Validation works as expected
- ✅ Error handling is graceful
- ✅ Success messages appear appropriately

