# Running the Server with Logging on Windows

## Features
- **Console Logging**: All logs appear in your Windows terminal in real-time
- **File Logging**: Logs automatically saved to `logs/` folder with daily rotation
- **30 Day Retention**: Old logs automatically deleted after 30 days
- **Organized Logs**: Separate files for app, error, SQL, and access logs
- **Async-Safe**: Non-blocking file writes for optimal performance

## How to Run the Server

### Option 1: Using the Run Script (RECOMMENDED)
```bash
python run_server.py
```

### Option 2: Using uvicorn with logging config file
```bash
uvicorn kg_builder.main:app --reload --host 0.0.0.0 --port 8000 --log-config logging_config.json
```

### Option 3: Using uv with logging config file
```bash
uv run uvicorn kg_builder.main:app --reload --host 0.0.0.0 --port 8000 --log-config logging_config.json
```

### Option 4: Using python -m
```bash
python -m kg_builder.main
```

## What You'll See

### Console Output
When the server starts successfully, you'll see logs in your terminal:

```
[STARTUP] Starting Knowledge Graph Builder API server...
[STARTUP] Log level: INFO
[STARTUP] Logs will appear in this console
============================================================
2025-10-28 00:11:16 - uvicorn.error - INFO - Uvicorn running on http://0.0.0.0:8000
2025-10-28 00:11:18 - kg_builder.main - INFO - Starting Knowledge Graph Builder v1.0.0
2025-10-28 00:11:22 - kg_builder.main - INFO - FalkorDB connected: False
2025-10-28 00:11:22 - kg_builder.main - INFO - Graphiti available: True
2025-10-28 00:11:22 - uvicorn.error - INFO - Application startup complete.
```

### Log Files
All logs are also saved to the `logs/` folder:

- **`logs/app.log`** - All application logs with detailed file/line info
- **`logs/error.log`** - Only ERROR and CRITICAL logs with stack traces
- **`logs/sql.log`** - SQL queries and database operations
- **`logs/access.log`** - HTTP access logs

Logs include:
- SQL queries from nl_query_executor
- Service-level operations
- API request/response logs
- Error messages and full stack traces
- Filename and line number for debugging

### Daily Rotation
- Logs rotate automatically at midnight
- Old logs renamed: `app.log.2025-10-27`
- Kept for 30 days, then auto-deleted
- No manual maintenance required

## Viewing Logs

### Real-time Console
Just watch your terminal - all logs appear there immediately

### View Log Files

**Windows Command Prompt:**
```bash
type logs\app.log
type logs\error.log
```

**Windows PowerShell:**
```powershell
Get-Content logs/app.log -Tail 50
Get-Content logs/error.log -Wait -Tail 50  # Real-time monitoring
```

**Git Bash / Linux-style:**
```bash
tail -f logs/app.log
grep "ERROR" logs/app.log
```

### Search Logs
```bash
# Find all errors
grep "ERROR" logs/app.log

# Find SQL queries
grep "SELECT" logs/sql.log

# Search all logs
grep -r "keyword" logs/
```

## Files Created

1. **`run_server.py`** - Recommended startup script with logging configured
2. **`logging_config.json`** - JSON logging configuration for uvicorn CLI
3. **`kg_builder/logging_config.py`** - Python logging configuration module
4. **`test_logging.py`** - Quick test script to verify logging works
5. **`logs/`** - Log files directory (auto-created, git-ignored)
6. **`logs/README.md`** - Detailed documentation about log files

## Troubleshooting

If logs still don't appear:
1. Make sure you're using one of the methods above
2. Check that `LOG_LEVEL` in your `.env` or `kg_builder/config.py` is set to `INFO` or `DEBUG`
3. Try running `python test_logging.py` to verify basic logging works

## Log Levels

You can control log verbosity by setting `LOG_LEVEL` in your environment or config:
- `DEBUG` - Very verbose, shows everything
- `INFO` - Standard logging (recommended)
- `WARNING` - Only warnings and errors
- `ERROR` - Only errors
