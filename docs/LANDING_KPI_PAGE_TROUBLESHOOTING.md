# Landing KPI Page Not Loading - Troubleshooting Guide ✅

## 🔍 **Root Cause Identified and Fixed**

The landing-kpi web page was not loading because of **API response format mismatch** after migrating from SQLite to MS SQL Server API.

---

## 🛠️ **Issues Found and Fixed**

### **1. API Response Format Mismatch** ❌→✅

#### **Problem**:
- **Old SQLite API** returned: `{success: true, kpis: [...], total: 5}`
- **New MS SQL API** returns: `{success: true, data: [...], count: 5}`
- **Frontend components** expected the old format

#### **Solution Applied**:
Updated frontend components to handle both formats:

**File**: `web-app/src/components/KPIList.js`
```javascript
// OLD: Only handled old format
setKpis(response.data.kpis || []);

// NEW: Handles both formats
const kpisData = response.data.kpis || response.data.data || response.data || [];
setKpis(Array.isArray(kpisData) ? kpisData : []);
```

**File**: `web-app/src/components/KPIExecutionHistory.js`
```javascript
// OLD: Only handled old format
setExecutions(response.data.executions || []);

// NEW: Handles both formats
const executionsData = response.data.executions || response.data.data || response.data || [];
setExecutions(Array.isArray(executionsData) ? executionsData : []);
```

### **2. Missing Dashboard Endpoints** ❌→✅

#### **Problem**:
- **Dashboard components** were calling `/landing-kpi-mssql/dashboard`
- **New MS SQL API** didn't have dashboard endpoints implemented

#### **Solution Applied**:
Added missing dashboard endpoints to the new API:

**File**: `api/routes/landing_kpi_mssql.py`
```python
@landing_kpi_mssql_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get dashboard data with KPIs grouped by group name."""
    dashboard_data = kpi_service.get_dashboard_data()
    return jsonify({'success': True, **dashboard_data, 'storage_type': 'mssql'})

@landing_kpi_mssql_bp.route('/<int:kpi_id>/latest-results', methods=['GET'])
def get_latest_results(kpi_id):
    """Get the latest execution results for a specific KPI."""
    results = kpi_service.get_latest_results(kpi_id)
    return jsonify({'success': True, 'results': results, 'storage_type': 'mssql'})
```

**File**: `kg_builder/services/landing_kpi_service_mssql.py`
```python
def get_dashboard_data(self) -> Dict[str, Any]:
    """Get all KPIs grouped by group name with their latest execution summary."""
    # Implementation added with proper MS SQL queries

def get_latest_results(self, kpi_id: int) -> Optional[Dict[str, Any]]:
    """Get the latest execution results for a specific KPI."""
    # Implementation added with proper MS SQL queries
```

### **3. API Endpoint Migration** ❌→✅

#### **Problem**:
- **Frontend components** were still calling old SQLite endpoints
- **API service** was updated but some components weren't using it correctly

#### **Solution Applied**:
Updated all API calls to use the new enhanced API:

**File**: `web-app/src/services/api.js`
```javascript
// OLD: SQLite-based endpoints
export const listKPIs = (params) => api.get('/landing-kpi/kpis', { params });
export const getDashboardData = () => api.get('/landing-kpi/dashboard');

// NEW: Enhanced MS SQL endpoints
export const listKPIs = (params) => api.get('/landing-kpi-mssql/kpis', { params });
export const getDashboardData = () => api.get('/landing-kpi-mssql/dashboard');
```

---

## 🧪 **Testing the Fix**

### **1. Test API Endpoints**:
```bash
# Test new enhanced API endpoints
curl http://localhost:8000/v1/landing-kpi-mssql/kpis
curl http://localhost:8000/v1/landing-kpi-mssql/dashboard
curl http://localhost:8000/v1/landing-kpi-mssql/health
```

### **2. Test Frontend**:
1. **Navigate to Landing KPI page**: `http://localhost:3000/landing-kpi`
2. **Verify KPI list loads**: Should show existing KPIs
3. **Test create KPI**: Should work with SQL preview
4. **Test execute KPI**: Should show enhanced SQL with ops_planner
5. **Test dashboard**: Should load KPI groups and latest executions

### **3. Browser Console Check**:
- **No API errors**: Check browser console for 404 or 500 errors
- **Data loading**: Verify API responses are being parsed correctly
- **Component rendering**: Ensure components render without errors

---

## 🎯 **What Should Work Now**

### **✅ Landing KPI Management Page**:
- **KPI List**: Loads all KPIs from MS SQL database
- **Create KPI**: Form works with SQL preview
- **Edit KPI**: Updates work correctly
- **Delete KPI**: Deletion works correctly
- **Execute KPI**: Shows enhanced SQL with ops_planner

### **✅ Enhanced Features**:
- **ops_planner inclusion**: Automatically added to material queries
- **Always-visible SQL**: SQL shown even with 0 records
- **Material master enhancement**: Automatic hana_material_master joins
- **SQL preview**: Live preview in create/edit forms

### **✅ Dashboard Integration**:
- **KPI Dashboard**: Shows KPIs grouped by category
- **Latest Results**: Shows recent execution results
- **Execution History**: Shows all past executions
- **Performance Metrics**: Shows execution times and record counts

---

## 🚨 **If Still Not Working**

### **Check Backend**:
1. **Database Connection**: Ensure MS SQL Server is running and accessible
2. **API Registration**: Verify `landing_kpi_mssql_bp` is registered in Flask app
3. **Service Initialization**: Check `LandingKPIServiceMSSQL` initializes correctly

### **Check Frontend**:
1. **API Base URL**: Verify `API_BASE_URL` points to correct backend
2. **CORS Settings**: Ensure CORS allows frontend domain
3. **Network Tab**: Check browser network tab for failed requests

### **Debug Steps**:
```bash
# 1. Test backend directly
curl -v http://localhost:8000/v1/landing-kpi-mssql/kpis

# 2. Check backend logs
tail -f logs/app.log

# 3. Test database connection
python -c "from kg_builder.services.landing_kpi_service_mssql import LandingKPIServiceMSSQL; service = LandingKPIServiceMSSQL(); print(service.get_all_kpis())"
```

---

## 🎉 **Migration Complete**

The landing-kpi web page should now be working correctly with:

- ✅ **Enhanced MS SQL API** instead of SQLite
- ✅ **ops_planner enhancement** in generated SQL
- ✅ **Always-visible SQL** functionality
- ✅ **Material master enhancement** for better analysis
- ✅ **Improved error handling** and user feedback
- ✅ **Dashboard integration** with latest execution results

**Status**: 🎯 **FIXED - Landing KPI page should now load correctly!**
