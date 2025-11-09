# Schedule Trigger Cached SQL Fix

## 🔍 **Problem Identified**

When calling `/v1/kpi-schedules/1/trigger`, the system was **NOT using cached SQL** for execution. Instead, it was:

1. ❌ Using `LandingKPIServiceJDBC.execute_kpi()` directly
2. ❌ This method always generates new SQL via LLM
3. ❌ Ignoring `isSQLCached` flag and `cached_sql` field
4. ❌ Inconsistent behavior compared to manual KPI execution

## ✅ **Solution Implemented**

### **1. Fixed Manual Trigger Method**

Updated `KPIScheduleService.manual_trigger_schedule()` to use the **LandingKPIExecutor** which supports cached SQL:

**Before (❌ Wrong):**
```python
# Used direct service execution (no cached SQL support)
kpi_service = get_landing_kpi_service_jdbc()
kpi_execution = kpi_service.execute_kpi(schedule['kpi_id'], execution_params)
```

**After (✅ Correct):**
```python
# Uses LandingKPIExecutor which supports cached SQL
kpi_service = get_landing_kpi_service_jdbc()
executor = get_landing_kpi_executor()

# Create execution record first
kpi_execution_record = kpi_service.create_execution_record(schedule['kpi_id'], execution_params)

# Execute using executor (supports cached SQL)
executor.execute_kpi_async(
    kpi_id=schedule['kpi_id'],
    execution_id=kpi_execution_id,
    execution_params=execution_params
)
```

### **2. Added Missing Method**

Added `create_execution_record()` method to `LandingKPIServiceJDBC` to support the new flow:

```python
def create_execution_record(self, kpi_id: int, execution_params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new execution record for a KPI without executing it."""
    # Creates pending execution record
    # Returns execution details for further processing
```

## 🎯 **How Cached SQL Now Works**

### **Execution Flow:**
```
1. POST /v1/kpi-schedules/1/trigger
   ↓
2. KPIScheduleService.manual_trigger_schedule()
   ↓
3. Create schedule execution record (pending)
   ↓
4. Create KPI execution record (pending)
   ↓
5. LandingKPIExecutor.execute_kpi_async()
   ↓
6. Check KPI cache flags:
   - isSQLCached = True?
   - cached_sql exists?
   ↓
7a. IF CACHED: Execute cached SQL directly ✅
7b. IF NOT CACHED: Generate new SQL via LLM
   ↓
8. Update execution records with results
```

### **Cache Decision Logic:**
```python
is_cached = kpi.get('isSQLCached', False)
has_cached_sql = bool(kpi.get('cached_sql', '').strip())

if is_cached and has_cached_sql:
    # 🔄 USING CACHED SQL
    query_result = self._execute_cached_sql(kpi['cached_sql'], connection, limit, intent.definition)
else:
    # 🤖 USING LLM GENERATION
    executor = get_nl_query_executor(db_type, kg=kg, use_llm=True)
    query_result = executor.execute(intent, connection, limit=limit)
```

## 🚀 **Benefits**

1. **✅ Consistent Behavior**: Schedule triggers now behave the same as manual KPI execution
2. **✅ Reliable Execution**: Uses pre-approved, tested SQL queries
3. **✅ Performance**: Cached SQL executes faster than LLM generation
4. **✅ Cost Effective**: Reduces LLM API calls for scheduled executions
5. **✅ Predictable Results**: Same SQL = same results every time

## 🔧 **Files Modified**

1. **`kg_builder/services/kpi_schedule_service.py`**
   - Updated `manual_trigger_schedule()` method
   - Now uses `LandingKPIExecutor` instead of direct service call

2. **`kg_builder/services/landing_kpi_service_jdbc.py`**
   - Added `create_execution_record()` method
   - Added singleton function `get_landing_kpi_service_jdbc()`

## ✅ **Verification**

To verify the fix works:

1. **Set up a KPI with cached SQL:**
   ```sql
   UPDATE kpi_definitions 
   SET isSQLCached = 1, cached_sql = 'SELECT * FROM your_table LIMIT 100'
   WHERE id = 1;
   ```

2. **Trigger the schedule:**
   ```bash
   POST /v1/kpi-schedules/1/trigger
   ```

3. **Check logs for:**
   ```
   🔄 USING CACHED SQL instead of LLM generation
   🔹 CACHED SQL TO BE EXECUTED:
   SELECT * FROM your_table LIMIT 100
   ✅ Cached SQL executed successfully
   ```

## 🎯 **Expected Response**

```json
{
  "success": true,
  "message": "Schedule 1 triggered manually",
  "execution_id": 123,
  "schedule_id": 1,
  "kpi_id": 5,
  "kpi_name": "Product Match Rate",
  "execution_status": "running",
  "triggered_at": "2025-11-09T19:30:00.123456"
}
```

The execution will now **automatically use cached SQL** if available, ensuring consistent and reliable scheduled KPI execution! 🎉
