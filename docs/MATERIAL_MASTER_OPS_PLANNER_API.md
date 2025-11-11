# Material Master OPS_PLANNER API

## Overview
This API endpoint retrieves unique OPS_PLANNER values from the `hana_material_master` table in the NewDQ database.

## Endpoint Details

### Get Unique OPS Planners

**URL**: `/v1/material-master/ops-planners`

**Method**: `GET`

**Tags**: Material Master

**Description**: Returns a list of distinct planner names from the material master table. Useful for filtering, dropdowns, and analytics.

---

## Request

### URL
```
GET http://localhost:8000/v1/material-master/ops-planners
```

### Headers
```
Content-Type: application/json
```

### Query Parameters
None

---

## Response

### Success Response (200 OK)

```json
{
  "success": true,
  "data": [
    "David Kim",
    "Emily Rodriguez",
    "James Anderson",
    "John Smith",
    "Lisa Wang",
    "Maria Garcia",
    "Michael Chen",
    "Sarah Johnson"
  ],
  "count": 8,
  "source_table": "hana_material_master",
  "source_database": "NewDQ"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Indicates if the request was successful |
| `data` | array | List of unique OPS_PLANNER names (sorted alphabetically) |
| `count` | integer | Number of unique planners found |
| `source_table` | string | Source table name (hana_material_master) |
| `source_database` | string | Source database name (NewDQ) |

### Error Response (500 Internal Server Error)

```json
{
  "detail": "Failed to fetch OPS_PLANNER values: Connection error"
}
```

---

## Usage Examples

### JavaScript/React (using Axios)

```javascript
import { getUniqueOpsPlanner } from './services/api';

// Fetch unique planners
const fetchPlanners = async () => {
  try {
    const response = await getUniqueOpsPlanner();
    const planners = response.data.data;
    console.log('Planners:', planners);
    console.log('Count:', response.data.count);
  } catch (error) {
    console.error('Error fetching planners:', error);
  }
};
```

### Python (using requests)

```python
import requests

url = "http://localhost:8000/v1/material-master/ops-planners"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    planners = data['data']
    print(f"Found {data['count']} planners:")
    for planner in planners:
        print(f"  - {planner}")
else:
    print(f"Error: {response.status_code}")
```

### cURL

```bash
curl -X GET "http://localhost:8000/v1/material-master/ops-planners" \
     -H "Content-Type: application/json"
```

---

## Use Cases

### 1. Dropdown Filter in UI
Use this API to populate a dropdown filter for selecting planners:

```javascript
import React, { useEffect, useState } from 'react';
import { getUniqueOpsPlanner } from './services/api';

function PlannerFilter({ onPlannerChange }) {
  const [planners, setPlanners] = useState([]);

  useEffect(() => {
    const loadPlanners = async () => {
      const response = await getUniqueOpsPlanner();
      setPlanners(response.data.data);
    };
    loadPlanners();
  }, []);

  return (
    <select onChange={(e) => onPlannerChange(e.target.value)}>
      <option value="">All Planners</option>
      {planners.map(planner => (
        <option key={planner} value={planner}>
          {planner}
        </option>
      ))}
    </select>
  );
}
```

### 2. Analytics Dashboard
Display planner statistics:

```javascript
const loadPlannerStats = async () => {
  const response = await getUniqueOpsPlanner();
  const plannerCount = response.data.count;

  // Display in dashboard
  console.log(`Total Active Planners: ${plannerCount}`);
};
```

### 3. Data Validation
Validate planner names in forms:

```javascript
const validatePlanner = async (plannerName) => {
  const response = await getUniqueOpsPlanner();
  const validPlanners = response.data.data;

  return validPlanners.includes(plannerName);
};
```

---

## Database Query

The API executes the following SQL query against the NewDQ database:

```sql
SELECT DISTINCT OPS_PLANNER
FROM hana_material_master
WHERE OPS_PLANNER IS NOT NULL
ORDER BY OPS_PLANNER
```

### Query Details
- **Filters**: Only returns non-NULL planner names
- **Sorting**: Results are sorted alphabetically
- **Uniqueness**: Uses DISTINCT to ensure no duplicates

---

## Notes

1. **Database Connection**: This endpoint connects to the SOURCE database (NewDQ) configured in your `.env` file
2. **Performance**: The query is optimized with DISTINCT and filters NULL values
3. **Caching**: Consider caching the results in the frontend as planner names don't change frequently
4. **NULL Handling**: NULL planner values are automatically excluded from results
5. **Case Sensitivity**: Planner names are returned exactly as stored in the database

---

## Troubleshooting

### Issue: Empty results (count: 0)

**Possible Causes**:
1. No data in `hana_material_master` table
2. All OPS_PLANNER values are NULL
3. Database connection issue

**Solution**:
- Run the seed data script to populate the table
- Check database connection in `.env` file

### Issue: Connection Error

**Possible Causes**:
1. Source database (NewDQ) is not running
2. JDBC driver not found
3. Invalid credentials in `.env`

**Solution**:
- Verify SQL Server is running
- Check SOURCE_DB_* configuration in `.env`
- Ensure JDBC driver exists in `jdbc_drivers/` folder

### Issue: 500 Internal Server Error

**Check**:
- Backend logs for detailed error messages
- Database connectivity
- SQL Server permissions for the user

---

## Related APIs

- **KPI Execution**: `/v1/landing-kpi-mssql/kpis/{kpi_id}/execute`
- **Dashboard Data**: `/v1/landing-kpi-mssql/dashboard`
- **Table Aliases**: `/v1/kg/{kg_name}/table-aliases`

---

## Changelog

### 2025-11-08
- Initial API creation
- Added endpoint to get unique OPS_PLANNER values
- Added frontend API client function
- Created documentation
