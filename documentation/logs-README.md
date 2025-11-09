# Logs Directory

This directory contains application logs organized by type and automatically rotated daily.

## Log Files

### `app.log`
- **Contains**: All application logs (INFO, WARNING, ERROR, CRITICAL)
- **Format**: Detailed with filename and line numbers
- **Rotation**: Daily at midnight
- **Retention**: 30 days

Example:
```
2025-10-28 00:21:21 - kg_builder.main - INFO - [main.py:35] - Logging configured at INFO level
```

### `error.log`
- **Contains**: Only ERROR and CRITICAL level logs
- **Format**: Detailed with full stack traces
- **Rotation**: Daily at midnight
- **Retention**: 30 days
- **Use**: Quick access to errors without scanning all logs

Example:
```
2025-10-28 00:21:34 - kg_builder.services.falkordb_backend - ERROR - [falkordb_backend.py:38] - Failed to connect to FalkorDB
```

### `sql.log`
- **Contains**: SQL queries and database operations
- **Services**: nl_query_executor, nl_sql_generator, landing_db_connector, kpi_executor
- **Format**: Detailed with filename and line numbers
- **Rotation**: Daily at midnight
- **Retention**: 30 days
- **Use**: Debug SQL queries without application noise

### `access.log`
- **Contains**: HTTP access logs from uvicorn
- **Format**: Client address, request line, status code
- **Rotation**: Daily at midnight
- **Retention**: 30 days

Example:
```
2025-10-28 00:21:21 - INFO - 127.0.0.1:12345 - GET /v1/health HTTP/1.1 - 200
```

## Rotation Details

- **When**: Midnight every day
- **Format**: Original filename + timestamp (e.g., `app.log.2025-10-27`)
- **Backup Count**: 30 files (30 days of history)
- **Old Files**: Automatically deleted after 30 days
- **Encoding**: UTF-8 (works properly on Windows)

## Performance

- **Async-Safe**: Uses buffered writes, doesn't block application
- **Automatic**: No manual intervention needed
- **Reliable**: Logs continue even if rotation fails

## Viewing Logs

### View latest logs
```bash
# Last 50 lines of app log
tail -50 logs/app.log

# Last 50 lines of error log
tail -50 logs/error.log

# Watch logs in real-time
tail -f logs/app.log
```

### Search logs
```bash
# Find specific errors
grep "ERROR" logs/app.log

# Find SQL queries
grep "SELECT" logs/sql.log

# Search across all logs
grep -r "keyword" logs/
```

### Windows PowerShell
```powershell
# View last 50 lines
Get-Content logs/app.log -Tail 50

# Watch in real-time
Get-Content logs/app.log -Wait -Tail 50
```

## Troubleshooting

If logs aren't being created:
1. Check that the application has write permissions
2. Verify the logs directory exists
3. Check LOG_LEVEL in your .env or config.py
4. Look for errors in console output during startup

## Console Output

Note: All logs also appear in the console (terminal) in real-time for immediate feedback. File logs provide permanent historical records.
