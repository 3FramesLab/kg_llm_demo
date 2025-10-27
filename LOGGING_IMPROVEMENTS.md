# Logging System Improvements

## Summary of Changes

Comprehensive logging system implemented with daily file rotation, organized log files, and full Windows terminal support.

## What Was Implemented

### 1. Console Logging (Windows Terminal Support)
- ✅ All logs now appear in Windows terminal in real-time
- ✅ Uses stderr for reliable output on Windows
- ✅ Proper encoding support (UTF-8)
- ✅ Works with: `python run_server.py`, `uvicorn`, and `uv run uvicorn`

### 2. Daily Rotating File Logs
- ✅ Automatic daily rotation at midnight
- ✅ 30-day retention policy (auto-deletes old logs)
- ✅ Async-safe (non-blocking writes)
- ✅ UTF-8 encoding for Windows compatibility

### 3. Organized Log Files

**`logs/app.log`**
- All application logs (INFO+)
- Detailed format with filename and line numbers
- Example: `2025-10-28 00:21:21 - kg_builder.main - INFO - [main.py:35] - Logging configured`

**`logs/error.log`**
- Only ERROR and CRITICAL logs
- Full stack traces
- Faster error investigation without scanning all logs

**`logs/sql.log`**
- SQL queries and database operations
- Services: nl_query_executor, nl_sql_generator, landing_db_connector, kpi_executor
- Dedicated log for database debugging

**`logs/access.log`**
- HTTP access logs from uvicorn
- Format: client_addr, request_line, status_code

### 4. Files Created/Modified

**New Files:**
- `kg_builder/logging_config.py` - Centralized logging configuration
- `logging_config.json` - JSON config for CLI usage
- `run_server.py` - Startup script with logging
- `test_logging.py` - Logging verification script
- `logs/.gitkeep` - Ensures logs directory in git
- `logs/README.md` - Log files documentation
- `RUNNING_SERVER.md` - Server startup guide
- `LOGGING_IMPROVEMENTS.md` - This file

**Modified Files:**
- `kg_builder/main.py` - Updated to use centralized logging config
- `.gitignore` - Added logs/*.log exclusion rules

## How to Use

### Run the Server
```bash
# Option 1: Recommended
python run_server.py

# Option 2: With uvicorn CLI
uvicorn kg_builder.main:app --reload --host 0.0.0.0 --port 8000 --log-config logging_config.json

# Option 3: With uv
uv run uvicorn kg_builder.main:app --reload --host 0.0.0.0 --port 8000 --log-config logging_config.json
```

### View Logs

**Console**: Logs appear in terminal automatically

**Files**:
```bash
# View logs
cat logs/app.log
cat logs/error.log

# Watch in real-time
tail -f logs/app.log

# Search logs
grep "ERROR" logs/app.log
grep "SELECT" logs/sql.log
```

**Windows PowerShell**:
```powershell
Get-Content logs/app.log -Tail 50
Get-Content logs/app.log -Wait -Tail 50  # Real-time
```

## Benefits

### For Development
- ✅ Immediate feedback in console
- ✅ Detailed file/line info for debugging
- ✅ Separate SQL log for query optimization
- ✅ Color-coded output (with uvicorn colors)

### For Production
- ✅ 30 days of historical logs
- ✅ Automatic rotation and cleanup
- ✅ Async-safe (no performance impact)
- ✅ Organized by type for faster troubleshooting

### For Windows Users
- ✅ Works reliably on Windows terminal
- ✅ UTF-8 encoding prevents character errors
- ✅ Compatible with PowerShell, CMD, and Git Bash

## Technical Details

### Log Rotation
- **When**: Midnight every day
- **Format**: `filename.log.YYYY-MM-DD`
- **Handler**: `TimedRotatingFileHandler`
- **Backup Count**: 30 days
- **Automatic Cleanup**: Yes

### Formatters
- **Console**: Simple format for readability
- **Files**: Detailed format with filename:line_number
- **Access**: Special format for HTTP logs

### Performance
- **Non-blocking**: Uses buffered I/O
- **Async-safe**: Works with FastAPI/uvicorn
- **Efficient**: Minimal overhead on application

## Testing

Run the test script to verify everything works:
```bash
python test_logging.py
```

Expected output:
- Console logs appear
- 4 log files created in logs/
- Confirmation messages

## Log Levels

Control verbosity via `LOG_LEVEL` environment variable or `kg_builder/config.py`:
- `DEBUG` - Very verbose (development)
- `INFO` - Standard (recommended)
- `WARNING` - Only warnings and errors
- `ERROR` - Only errors

## Maintenance

### Automatic
- Logs rotate daily
- Old logs deleted after 30 days
- No manual intervention needed

### Manual (if needed)
```bash
# Delete all logs (fresh start)
rm logs/*.log

# Archive old logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/*.log.*

# Clean up old rotated logs manually
find logs -name "*.log.*" -mtime +30 -delete
```

## Troubleshooting

### Logs don't appear in console
1. Check you're using one of the recommended run methods
2. Verify `LOG_LEVEL` is set to `INFO` or `DEBUG`
3. Run `python test_logging.py` to verify

### Log files not created
1. Check write permissions on `logs/` directory
2. Verify application is running
3. Check for disk space

### Too many/few logs
Adjust `LOG_LEVEL`:
- More logs: Set to `DEBUG`
- Fewer logs: Set to `WARNING` or `ERROR`

## Future Enhancements (Optional)

- [ ] Structured JSON logging for log aggregation tools
- [ ] Log shipping to external services (e.g., CloudWatch, ELK)
- [ ] Per-service log level configuration
- [ ] Log compression for archived files
- [ ] Separate log files per service/module
- [ ] Request ID tracking across logs
- [ ] Performance metrics logging

## References

- Python logging: https://docs.python.org/3/library/logging.html
- TimedRotatingFileHandler: https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler
- Uvicorn logging: https://www.uvicorn.org/settings/#logging
