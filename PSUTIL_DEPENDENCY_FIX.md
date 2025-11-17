# psutil Dependency Fix

## 🎯 Problem
The application was failing with the error:
```
"error_message": "No module named 'psutil'"
```

This occurred because the `psutil` package was being imported in `kg_builder/services/kpi_performance_monitor.py` but was not listed in the `requirements.txt` file.

## 🔍 Root Cause
1. **Missing dependency**: `psutil` was not included in `requirements.txt`
2. **Hard import**: The code was using a direct `import psutil` which would fail if the package wasn't installed
3. **Performance monitoring**: The `psutil` package is used for system performance monitoring (memory usage, CPU usage, etc.)

## ✅ Solution Applied

### 1. Added psutil to requirements.txt
**File**: `requirements.txt`  
**Line**: 40

```diff
# Logging and monitoring
structlog>=23.1.0  # Enhanced logging
prometheus-client>=0.17.0  # Metrics and monitoring (optional)
+ psutil>=5.9.0  # System and process utilities for performance monitoring
```

### 2. Made psutil import optional
**File**: `kg_builder/services/kpi_performance_monitor.py`

**Before (Hard import - would fail if psutil not available)**:
```python
import psutil
```

**After (Optional import - graceful fallback)**:
```python
# Optional import for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False
```

### 3. Updated code to handle missing psutil
Modified all functions that use `psutil` to check `PSUTIL_AVAILABLE` first:

- **Memory monitoring initialization**: Falls back to 0.0 values if psutil unavailable
- **Background memory monitoring**: Logs warning and returns early if psutil unavailable  
- **Final system metrics**: Sets default values if psutil unavailable

## 🧪 Benefits of This Fix

1. **Graceful degradation**: Application works even if psutil is not installed
2. **Optional monitoring**: Performance monitoring is enhanced when psutil is available, but not required
3. **Clear logging**: Users are informed when performance monitoring is disabled
4. **Backward compatibility**: Existing functionality is preserved

## 📊 Behavior

### With psutil installed:
- ✅ Full performance monitoring (memory, CPU, threads)
- ✅ Real-time memory tracking
- ✅ Detailed system metrics

### Without psutil installed:
- ✅ Application runs normally
- ⚠️ Performance monitoring disabled (logged as warning)
- ✅ All other functionality works
- 📊 Memory/CPU metrics set to 0.0

## 🚀 Installation

To get full performance monitoring capabilities, install psutil:

```bash
# Install all dependencies including psutil
pip install -r requirements.txt

# Or install psutil specifically
pip install psutil>=5.9.0
```

## 🎉 Result

The application should now start successfully regardless of whether `psutil` is installed, with enhanced performance monitoring when available and graceful fallback when not.
