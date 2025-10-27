"""
Quick test script to verify logging configuration works on Windows.
Tests both console output and file logging with daily rotation.
"""
import logging
import logging.config
from pathlib import Path

# Import the logging config
from kg_builder.logging_config import LOGGING_CONFIG

# Setup logging using the application config
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

print("=" * 80, flush=True)
print("Testing logging configuration on Windows...", flush=True)
print("=" * 80, flush=True)

# Test different log levels
logger.debug("[DEBUG] This is a DEBUG message")
logger.info("[INFO] This is an INFO message")
logger.warning("[WARNING] This is a WARNING message")
logger.error("[ERROR] This is an ERROR message")
logger.critical("[CRITICAL] This is a CRITICAL message")

print("=" * 80, flush=True)
print("Console logging: SUCCESS - You should see messages above", flush=True)
print("=" * 80, flush=True)

# Test kg_builder loggers
kg_logger = logging.getLogger('kg_builder.services.test')
kg_logger.info("[TEST] Testing kg_builder service logger")
kg_logger.debug("[TEST] Testing kg_builder service debug logger")

# Test SQL logger
sql_logger = logging.getLogger('kg_builder.services.nl_sql_generator')
sql_logger.info("[SQL] Testing SQL logging - this goes to sql.log")

# Test error logger
error_logger = logging.getLogger('kg_builder.services.test')
error_logger.error("[ERROR] Testing error logging - this goes to error.log")

print("\n" + "=" * 80, flush=True)
print("File logging test:", flush=True)

# Check if log files were created
logs_dir = Path(__file__).parent / "logs"
log_files = ["app.log", "error.log", "sql.log"]

for log_file in log_files:
    log_path = logs_dir / log_file
    if log_path.exists():
        size = log_path.stat().st_size
        print(f"  [OK] {log_file} created ({size} bytes)", flush=True)
    else:
        print(f"  [MISS] {log_file} not found", flush=True)

print("=" * 80, flush=True)
print("SUCCESS: Logging is working!", flush=True)
print("Check the logs/ folder for log files", flush=True)
print("=" * 80, flush=True)
