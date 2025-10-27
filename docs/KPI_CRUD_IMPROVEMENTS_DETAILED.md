# KPI CRUD Implementation - Detailed Improvement Guide

**Document Version**: 1.0  
**Date**: 2025-10-27

---

## Implementation Examples

### 1. Separate Result Storage - Complete Implementation

#### Database Schema

```sql
-- Modify kpi_execution_results table
ALTER TABLE kpi_execution_results 
DROP COLUMN result_data;

ALTER TABLE kpi_execution_results 
ADD COLUMN first_row_sample TEXT;

-- Create new result rows table
CREATE TABLE kpi_execution_result_rows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id INTEGER NOT NULL,
    row_number INTEGER NOT NULL,
    row_data TEXT NOT NULL,  -- JSON
    FOREIGN KEY (execution_id) REFERENCES kpi_execution_results(id) ON DELETE CASCADE,
    UNIQUE(execution_id, row_number)
);

CREATE INDEX idx_execution_result_rows ON kpi_execution_result_rows(execution_id);
```

#### Service Implementation

```python
def store_execution_results(self, execution_id: int, result_rows: List[Dict]):
    """Store execution results row by row"""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    try:
        for row_num, row_data in enumerate(result_rows, 1):
            cursor.execute("""
                INSERT INTO kpi_execution_result_rows 
                (execution_id, row_number, row_data)
                VALUES (?, ?, ?)
            """, (execution_id, row_num, json.dumps(row_data)))
        
        # Store first row as sample
        if result_rows:
            cursor.execute("""
                UPDATE kpi_execution_results 
                SET first_row_sample = ?
                WHERE id = ?
            """, (json.dumps(result_rows[0]), execution_id))
        
        conn.commit()
    finally:
        conn.close()

def get_drilldown_data_paginated(self, execution_id: int, page: int = 1, page_size: int = 50):
    """Get paginated drill-down data"""
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    offset = (page - 1) * page_size
    
    # Get total count
    cursor.execute("""
        SELECT COUNT(*) as total FROM kpi_execution_result_rows 
        WHERE execution_id = ?
    """, (execution_id,))
    total = cursor.fetchone()['total']
    
    # Get paginated data
    cursor.execute("""
        SELECT row_data FROM kpi_execution_result_rows 
        WHERE execution_id = ?
        ORDER BY row_number
        LIMIT ? OFFSET ?
    """, (execution_id, page_size, offset))
    
    rows = [json.loads(row['row_data']) for row in cursor.fetchall()]
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "data": rows
    }
```

---

### 2. Retry Logic - Complete Implementation

```python
import time
from functools import wraps
from typing import Callable, Any

def retry_on_failure(max_retries: int = 3, retry_delay: int = 5, backoff: float = 1.0):
    """Decorator for retry logic with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (backoff ** attempt)
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. "
                            f"Retrying in {wait_time}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries} attempts failed")
            
            raise last_exception
        return wrapper
    return decorator

# Usage in service
@retry_on_failure(max_retries=3, retry_delay=5, backoff=1.5)
def execute_kpi(self, kpi_id: int, execution_params: KPIExecutionRequest):
    """Execute KPI with automatic retry"""
    # Implementation
    pass
```

---

### 3. Execution Timeout - Complete Implementation

```python
import signal
from contextlib import contextmanager

class TimeoutException(Exception):
    pass

@contextmanager
def timeout(seconds: int):
    """Context manager for timeout"""
    def signal_handler(signum, frame):
        raise TimeoutException(f"Operation timed out after {seconds} seconds")
    
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

def execute_kpi_with_timeout(
    self, 
    kpi_id: int, 
    execution_params: KPIExecutionRequest,
    timeout_seconds: int = 300
):
    """Execute KPI with timeout protection"""
    start_time = time.time()
    
    try:
        with timeout(timeout_seconds):
            result = self.execute_kpi(kpi_id, execution_params)
        
        execution_time = (time.time() - start_time) * 1000
        return result
        
    except TimeoutException as e:
        execution_time = (time.time() - start_time) * 1000
        self._store_execution_result(
            kpi_id=kpi_id,
            execution_params=execution_params,
            status="timeout",
            error_message=str(e),
            execution_time_ms=execution_time
        )
        raise
```

---

### 4. Async Execution - Complete Implementation

```python
import asyncio
import uuid
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

# In-memory job store (use Redis for production)
job_store = {}

@app.post("/v1/landing-kpi/kpis/{kpi_id}/execute-async")
async def execute_kpi_async(kpi_id: int, request: KPIExecutionRequest):
    """Execute KPI asynchronously"""
    job_id = str(uuid.uuid4())
    
    job_store[job_id] = {
        "status": JobStatus.PENDING,
        "kpi_id": kpi_id,
        "created_at": datetime.now(),
        "result": None,
        "error": None
    }
    
    # Start background task
    asyncio.create_task(
        _execute_kpi_background(job_id, kpi_id, request)
    )
    
    return {
        "success": True,
        "job_id": job_id,
        "status_url": f"/v1/landing-kpi/jobs/{job_id}"
    }

async def _execute_kpi_background(job_id: str, kpi_id: int, request: KPIExecutionRequest):
    """Background task for KPI execution"""
    try:
        job_store[job_id]["status"] = JobStatus.RUNNING
        result = landing_kpi_service.execute_kpi(kpi_id, request)
        job_store[job_id]["status"] = JobStatus.SUCCESS
        job_store[job_id]["result"] = result
    except Exception as e:
        job_store[job_id]["status"] = JobStatus.FAILED
        job_store[job_id]["error"] = str(e)

@app.get("/v1/landing-kpi/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status of async execution job"""
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = job_store[job_id]
    return {
        "success": True,
        "job_id": job_id,
        "status": job["status"],
        "result": job["result"],
        "error": job["error"],
        "created_at": job["created_at"]
    }
```

---

### 5. Audit Trail - Complete Implementation

```python
def log_audit(
    self, 
    kpi_id: int, 
    action: str, 
    performed_by: str,
    changes: Dict = None
):
    """Log audit trail entry"""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO kpi_audit_log 
            (kpi_id, action, performed_by, changes)
            VALUES (?, ?, ?, ?)
        """, (
            kpi_id,
            action,
            performed_by,
            json.dumps(changes) if changes else None
        ))
        conn.commit()
    finally:
        conn.close()

def get_audit_log(self, kpi_id: int, limit: int = 100):
    """Get audit log for KPI"""
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM kpi_audit_log 
        WHERE kpi_id = ?
        ORDER BY performed_at DESC
        LIMIT ?
    """, (kpi_id, limit))
    
    return [dict(row) for row in cursor.fetchall()]

# Usage in CRUD operations
def create_kpi(self, kpi_data: KPICreateRequest, created_by: str):
    """Create KPI with audit logging"""
    kpi = self._create_kpi_db(kpi_data)
    self.log_audit(
        kpi_id=kpi.id,
        action="CREATE",
        performed_by=created_by,
        changes=kpi_data.dict()
    )
    return kpi
```

---

### 6. KPI Versioning - Complete Implementation

```python
def update_kpi(self, kpi_id: int, kpi_data: KPIUpdateRequest, updated_by: str):
    """Update KPI with versioning"""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    try:
        # Get current KPI
        cursor.execute("SELECT * FROM kpi_definitions WHERE id = ?", (kpi_id,))
        current = cursor.fetchone()
        
        # Increment version
        new_version = current['version'] + 1
        
        # Store in history
        cursor.execute("""
            INSERT INTO kpi_definition_history 
            (kpi_id, version, name, nl_definition, changed_by)
            VALUES (?, ?, ?, ?, ?)
        """, (
            kpi_id,
            current['version'],
            current['name'],
            current['nl_definition'],
            updated_by
        ))
        
        # Update main table
        cursor.execute("""
            UPDATE kpi_definitions 
            SET version = ?, updated_at = CURRENT_TIMESTAMP, ...
            WHERE id = ?
        """, (new_version, kpi_id))
        
        conn.commit()
    finally:
        conn.close()

def get_kpi_history(self, kpi_id: int):
    """Get version history for KPI"""
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM kpi_definition_history 
        WHERE kpi_id = ?
        ORDER BY version DESC
    """, (kpi_id,))
    
    return [dict(row) for row in cursor.fetchall()]
```

---

### 7. Batch Execution - Complete Implementation

```python
class BatchExecutionRequest(BaseModel):
    kpi_ids: List[int]
    execution_params: KPIExecutionRequest

@app.post("/v1/landing-kpi/batch-execute")
async def batch_execute_kpis(request: BatchExecutionRequest):
    """Execute multiple KPIs"""
    results = []
    errors = []
    
    for kpi_id in request.kpi_ids:
        try:
            result = landing_kpi_service.execute_kpi(
                kpi_id, 
                request.execution_params
            )
            results.append(result)
        except Exception as e:
            errors.append({
                "kpi_id": kpi_id,
                "error": str(e)
            })
    
    return {
        "success": len(errors) == 0,
        "total": len(request.kpi_ids),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }
```

---

## Testing Examples

### Unit Test for Retry Logic

```python
def test_retry_logic():
    """Test retry decorator"""
    call_count = 0
    
    @retry_on_failure(max_retries=3, retry_delay=0.1)
    def failing_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Temporary failure")
        return "Success"
    
    result = failing_function()
    assert result == "Success"
    assert call_count == 3
```

---

**End of Document**

