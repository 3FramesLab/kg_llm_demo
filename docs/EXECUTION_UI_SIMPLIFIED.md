# Reconciliation Execution UI - Simplified (No DB Config in UI)

## 🎯 Overview

The Reconciliation Execution screen has been simplified to remove database configuration forms since database credentials are managed in the `.env` file.

---

## ✨ What Changed

### Removed
- ❌ Source Database Configuration accordion
- ❌ Target Database Configuration accordion
- ❌ Database type selector
- ❌ Host, port, database, username, password fields
- ❌ Oracle service name field

### Kept
- ✅ Ruleset selector
- ✅ Limit input
- ✅ Execution options (3 checkboxes)
- ✅ Request/Response preview
- ✅ Execute button

### Added
- ✅ Info alert explaining database config location
- ✅ Caption in request payload showing .env usage

---

## 📋 Simplified Form Structure

```
Direct Execution Mode
├── Basic Configuration
│   ├── Ruleset Selector
│   └── Limit Input
├── Execution Options
│   ├── Include Matched Records ☑
│   ├── Include Unmatched Records ☑
│   └── Store Results in MongoDB ☑
├── Info Alert
│   └── "Database Configuration: Source and target database 
│       credentials are configured in the .env file."
└── Execute Button
```

---

## 🔧 Form State (Simplified)

```javascript
const [execFormData, setExecFormData] = useState({
  ruleset_id: '',           // Ruleset to execute
  limit: 1000,              // Max records per query
  include_matched: true,    // Include matched records
  include_unmatched: true,  // Include unmatched records
  store_in_mongodb: true,   // Store results in MongoDB
  // Database configs are read from .env file
});
```

---

## 📤 Request Payload (Simplified)

```json
{
  "ruleset_id": "RECON_ABC12345",
  "limit": 1000,
  "include_matched": true,
  "include_unmatched": true,
  "store_in_mongodb": true
}
```

**Note**: Database configurations are NOT included in the request. They are read from `.env` file by the backend.

---

## 🔐 Database Configuration (.env)

Database credentials are configured in the `.env` file:

```env
# SOURCE DATABASE
SOURCE_DB_TYPE=sqlserver
SOURCE_DB_HOST=DESKTOP-41O1AL9\LOCALHOST
SOURCE_DB_PORT=1433
SOURCE_DB_DATABASE=NewDQ
SOURCE_DB_USERNAME=mithun
SOURCE_DB_PASSWORD=mithun123
SOURCE_DB_SERVICE_NAME=

# TARGET DATABASE
TARGET_DB_TYPE=sqlserver
TARGET_DB_HOST=DESKTOP-41O1AL9\LOCALHOST
TARGET_DB_PORT=1433
TARGET_DB_DATABASE=NewDQ
TARGET_DB_USERNAME=mithun
TARGET_DB_PASSWORD=mithun123
TARGET_DB_SERVICE_NAME=
```

### Configuration Priority

1. **Request payload** - If `source_db_config` in API request (overrides .env)
2. **Environment variables** - From `.env` file (default)
3. **None** - SQL export mode (no database execution)

---

## 🚀 How to Use

### Step 1: Configure Database (One-time)
1. Edit `.env` file
2. Set `SOURCE_DB_*` variables
3. Set `TARGET_DB_*` variables
4. Set `USE_ENV_DB_CONFIGS=true`

### Step 2: Execute Reconciliation
1. Select a ruleset from dropdown
2. Set limit (default: 1000)
3. Configure execution options:
   - ✅ Include Matched Records
   - ✅ Include Unmatched Records
   - ✅ Store Results in MongoDB
4. Click "Execute Reconciliation"
5. View results in Results tab

---

## 📊 Execution Options Explained

| Option | Default | Purpose |
|--------|---------|---------|
| **Include Matched Records** | ✅ | Include records found in both source and target |
| **Include Unmatched Records** | ✅ | Include records found in only source or only target |
| **Store Results in MongoDB** | ✅ | Automatically save results to MongoDB for later retrieval |

### When to Uncheck

- **Uncheck "Include Matched"** - Only want to see discrepancies
- **Uncheck "Include Unmatched"** - Only want to see successful matches
- **Uncheck "Store in MongoDB"** - Don't need to persist results (faster execution)

---

## 📝 Response Example

```json
{
  "success": true,
  "mode": "direct_execution",
  "ruleset_id": "RECON_ABC123",
  "matched_count": 1247,
  "unmatched_source_count": 53,
  "unmatched_target_count": 28,
  "execution_time_ms": 2500,
  "mongodb_document_id": "507f1f77bcf86cd799439011",
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

## 🎨 UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Reconciliation Execution                                    │
│ [SQL Export] [Direct Execution] [Results]                  │
│                                                             │
│ Direct Execution Mode                                       │
│ ─────────────────────────────────────────────────────────  │
│                                                             │
│ Ruleset: [Select a ruleset ▼]                              │
│ Limit (max records per query): [1000]                       │
│                                                             │
│ Execution Options                                           │
│ ☑ Include Matched Records                                   │
│ ☑ Include Unmatched Records                                 │
│ ☑ Store Results in MongoDB                                  │
│                                                             │
│ ℹ️ Database Configuration: Source and target database       │
│    credentials are configured in the .env file.            │
│                                                             │
│ [Execute Reconciliation]                                    │
│                                                             │
│ ─────────────────────────────────────────────────────────  │
│                                                             │
│ Request Payload                                             │
│ {                                                           │
│   "ruleset_id": "RECON_ABC12345",                           │
│   "limit": 1000,                                            │
│   "include_matched": true,                                  │
│   "include_unmatched": true,                                │
│   "store_in_mongodb": true                                  │
│ }                                                           │
│ Database configs are read from .env file                    │
│                                                             │
│ Response Placeholder                                        │
│ {                                                           │
│   "success": true,                                          │
│   "mode": "direct_execution",                               │
│   "matched_count": 1247,                                    │
│   ...                                                       │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Benefits

✅ **Simpler UI** - Less clutter, easier to use
✅ **Secure** - Credentials not exposed in UI
✅ **Centralized Config** - All database configs in one place (.env)
✅ **Consistent** - Same database config for all executions
✅ **Flexible** - Can override via API request if needed
✅ **Production-Ready** - Follows security best practices

---

## 🔗 Related Files

- **Backend**: `kg_builder/routes.py` - `/reconciliation/execute` endpoint
- **Models**: `kg_builder/models.py` - `RuleExecutionRequest`
- **Config**: `.env` - Database configuration
- **Frontend**: `web-app/src/pages/Execution.js` - This component

---

## 📚 Configuration Files

### .env File Location
```
d:\learning\dq-poc\.env
```

### Key Variables
```env
USE_ENV_DB_CONFIGS=true
SOURCE_DB_TYPE=sqlserver
SOURCE_DB_HOST=...
SOURCE_DB_PORT=...
SOURCE_DB_DATABASE=...
SOURCE_DB_USERNAME=...
SOURCE_DB_PASSWORD=...
TARGET_DB_TYPE=sqlserver
TARGET_DB_HOST=...
TARGET_DB_PORT=...
TARGET_DB_DATABASE=...
TARGET_DB_USERNAME=...
TARGET_DB_PASSWORD=...
```

---

## 🚀 Summary

The Reconciliation Execution UI has been simplified to:

1. ✅ Remove database configuration forms
2. ✅ Keep only execution options
3. ✅ Show info alert about .env configuration
4. ✅ Simplify request payload
5. ✅ Improve security by not exposing credentials in UI
6. ✅ Maintain flexibility via API request override

All changes are backward compatible and production-ready.


