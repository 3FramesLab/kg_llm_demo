"""
Startup script to run uvicorn with proper logging configuration on Windows.
Use this instead of running uvicorn directly for consistent logging.
"""
import sys
import uvicorn
from kg_builder.logging_config import LOGGING_CONFIG
from kg_builder.config import LOG_LEVEL

if __name__ == "__main__":
    print("[STARTUP] Starting Knowledge Graph Builder API server...", flush=True)
    print(f"[STARTUP] Log level: {LOG_LEVEL}", flush=True)
    print("[STARTUP] Logs will appear in this console", flush=True)
    print("=" * 60, flush=True)

    uvicorn.run(
        "kg_builder.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=LOG_LEVEL.lower(),
        log_config=LOGGING_CONFIG,
        use_colors=True
    )
