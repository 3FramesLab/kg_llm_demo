# Reconciliation Execution UI - Updated

## Overview

The Reconciliation Execution screen has been updated to include all latest backend features and provide a better user experience.

---

## What's New

### 1. **Execution Options Section**

Added three new checkboxes to control execution behavior:

- **Include Matched Records** (default: ✅ checked)
  - Include records that exist in both source and target
  - Useful for validation and reconciliation analysis

- **Include Unmatched Records** (default: ✅ checked)
  - Include records that only exist in source or target
  - Helps identify data gaps and discrepancies

- **Store Results in MongoDB** (default: ✅ checked)
  - Automatically store execution results in MongoDB
  - Enables result retrieval and historical tracking
  - Only applies to Direct Execution Mode

### 2. **Database Type Selection**

Added database type selector for both source and target databases:

- **Oracle** (default)
- **SQL Server**
- **PostgreSQL**
- **MySQL**

Allows users to specify different database types for source and target.

### 3. **Oracle Service Name Field**

Added conditional field for Oracle databases:

- **Service Name** (optional)
- Only appears when database type is set to "Oracle"
- Example: `ORCLPDB`, `ORCL`, etc.
- Helps with Oracle-specific connection configurations

### 4. **Improved Form Organization**

- **Execution Options** section with checkboxes
- **Source Database Configuration** accordion (expanded by default)
- **Target Database Configuration** accordion (expanded by default)
- Clear visual separation with dividers

### 5. **Request/Response Preview**

Updated the right panel to show:

- **Request Payload**: Live preview of the API request being sent
  - Shows all form values in JSON format
  - Includes all new fields (include_matched, include_unmatched, store_in_mongodb)
  - Shows database type and service name

- **Response Placeholder**: Example response structure
  - Shows success status
  - Includes execution metrics (matched, unmatched counts)
  - Shows MongoDB document ID if stored
  - Displays storage location

---

## Form Fields

### Basic Configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| Ruleset | Select | - | Choose ruleset to execute |
| Limit | Number | 1000 | Max records per query |

### Execution Options

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| Include Matched Records | Checkbox | ✅ | Include matched records |
| Include Unmatched Records | Checkbox | ✅ | Include unmatched records |
| Store Results in MongoDB | Checkbox | ✅ | Store in MongoDB |

### Source Database Configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| Database Type | Select | oracle | oracle, sqlserver, postgresql, mysql |
| Host | Text | localhost | Database host/IP |
| Port | Number | 1521 | Database port |
| Database | Text | ORCL | Database name |
| Username | Text | - | Database username |
| Password | Password | - | Database password |
| Service Name | Text | - | Oracle service name (Oracle only) |

### Target Database Configuration

Same as Source Database Configuration

---

## API Request Structure

```json
{
  "ruleset_id": "RECON_ABC12345",
  "limit": 1000,
  "include_matched": true,
  "include_unmatched": true,
  "store_in_mongodb": true,
  "source_db_config": {
    "db_type": "oracle",
    "host": "localhost",
    "port": 1521,
    "database": "ORCL",
    "username": "user1",
    "password": "pass1",
    "service_name": "ORCLPDB"
  },
  "target_db_config": {
    "db_type": "oracle",
    "host": "localhost",
    "port": 1521,
    "database": "ORCL",
    "username": "user2",
    "password": "pass2",
    "service_name": "ORCLPDB"
  }
}
```

---

## API Response Structure

```json
{
  "success": true,
  "mode": "direct_execution",
  "ruleset_id": "RECON_ABC12345",
  "matched_count": 1247,
  "unmatched_source_count": 53,
  "unmatched_target_count": 28,
  "execution_time_ms": 2500,
  "mongodb_document_id": "ObjectId(...)",
  "storage_location": "mongodb",
  "summary": {
    "total_rules_executed": 12,
    "total_matched": 8934,
    "total_unmatched_source": 412,
    "total_unmatched_target": 287,
    "overall_match_rate": 0.78
  }
}
```

---

## Files Modified

**web-app/src/pages/Execution.js**

### Changes:
1. Added `FormControlLabel` and `Checkbox` imports from MUI
2. Updated `execFormData` state to include:
   - `include_matched` (boolean, default: true)
   - `include_unmatched` (boolean, default: true)
   - `store_in_mongodb` (boolean, default: true)
3. Added Execution Options section with 3 checkboxes
4. Added Database Type selector for source and target
5. Added conditional Service Name field for Oracle
6. Updated Request Payload preview to show all new fields
7. Updated Response Placeholder to show new response fields

---

## User Experience Improvements

✅ **Better Organization**: Logical grouping of related fields
✅ **Conditional Fields**: Service Name only shows for Oracle
✅ **Live Preview**: Request/Response preview updates in real-time
✅ **Expanded Accordions**: Database configs expanded by default
✅ **Clear Labels**: All fields have descriptive labels and helper text
✅ **Multiple DB Types**: Support for Oracle, SQL Server, PostgreSQL, MySQL
✅ **Execution Control**: Fine-grained control over what to include in results

---

## Testing Checklist

- [ ] Select a ruleset and verify it loads
- [ ] Change database type and verify Service Name field appears/disappears
- [ ] Toggle execution options and verify request payload updates
- [ ] Fill in database credentials and verify request payload
- [ ] Execute reconciliation and verify response displays correctly
- [ ] Check MongoDB storage when enabled
- [ ] Verify results tab shows execution results

---

## Summary

The Reconciliation Execution screen now fully supports all backend features including:
- Multiple database types
- Execution options (matched/unmatched/MongoDB storage)
- Oracle service name configuration
- Live request/response preview
- Better form organization and UX


