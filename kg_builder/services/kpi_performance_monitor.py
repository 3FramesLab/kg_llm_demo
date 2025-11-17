"""
KPI Performance Monitor

Provides detailed performance monitoring and logging for KPI execution processes.
Tracks execution times, memory usage, and provides performance insights.
"""

import logging
import time
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

# Optional import for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance metrics during KPI execution."""
    
    # Timing metrics
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    total_duration_ms: Optional[float] = None
    
    # Step-by-step timing
    step_timings: Dict[str, float] = field(default_factory=dict)
    step_start_times: Dict[str, float] = field(default_factory=dict)
    
    # Memory metrics
    initial_memory_mb: Optional[float] = None
    peak_memory_mb: Optional[float] = None
    final_memory_mb: Optional[float] = None
    memory_samples: List[float] = field(default_factory=list)
    
    # Database metrics
    db_connection_time_ms: Optional[float] = None
    query_execution_time_ms: Optional[float] = None
    result_fetch_time_ms: Optional[float] = None
    
    # KPI-specific metrics
    records_processed: int = 0
    records_per_second: Optional[float] = None
    
    # Resource utilization
    cpu_usage_percent: Optional[float] = None
    thread_count: Optional[int] = None
    
    # Context information
    kpi_id: Optional[str] = None
    kpi_type: Optional[str] = None
    execution_id: Optional[str] = None


class KPIPerformanceMonitor:
    """Performance monitor for KPI execution processes."""
    
    def __init__(self, kpi_id: str = None, kpi_type: str = None, execution_id: str = None):
        """Initialize performance monitor."""
        self.metrics = PerformanceMetrics(
            kpi_id=kpi_id,
            kpi_type=kpi_type,
            execution_id=execution_id
        )
        self._monitoring_active = False
        self._memory_monitor_thread = None
        
        # Initialize memory tracking
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                self.metrics.initial_memory_mb = process.memory_info().rss / 1024 / 1024
                self.metrics.peak_memory_mb = self.metrics.initial_memory_mb
                logger.info(f"📊 Performance monitoring initialized")
                logger.info(f"   KPI ID: {kpi_id}")
                logger.info(f"   Initial Memory: {self.metrics.initial_memory_mb:.2f} MB")
            except Exception as e:
                logger.warning(f"Could not initialize memory monitoring: {e}")
        else:
            logger.info(f"📊 Performance monitoring initialized (memory tracking disabled - psutil not available)")
            logger.info(f"   KPI ID: {kpi_id}")
            self.metrics.initial_memory_mb = 0.0
            self.metrics.peak_memory_mb = 0.0
    
    def start_step(self, step_name: str) -> None:
        """Start timing a specific step."""
        step_start = time.time()
        self.metrics.step_start_times[step_name] = step_start
        logger.info(f"⏱️ STEP STARTED: {step_name}")
        logger.info(f"   Start Time: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    
    def end_step(self, step_name: str) -> float:
        """End timing a specific step and return duration in ms."""
        if step_name not in self.metrics.step_start_times:
            logger.warning(f"Step '{step_name}' was not started")
            return 0.0
            
        step_end = time.time()
        step_duration = (step_end - self.metrics.step_start_times[step_name]) * 1000
        self.metrics.step_timings[step_name] = step_duration
        
        logger.info(f"✅ STEP COMPLETED: {step_name}")
        logger.info(f"   Duration: {step_duration:.2f}ms")
        logger.info(f"   End Time: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        
        return step_duration
    
    def start_memory_monitoring(self) -> None:
        """Start continuous memory monitoring in background thread."""
        if self._monitoring_active:
            return
            
        self._monitoring_active = True
        self._memory_monitor_thread = threading.Thread(
            target=self._monitor_memory,
            daemon=True
        )
        self._memory_monitor_thread.start()
        logger.info(f"🔍 Memory monitoring started")
    
    def stop_memory_monitoring(self) -> None:
        """Stop continuous memory monitoring."""
        self._monitoring_active = False
        if self._memory_monitor_thread:
            self._memory_monitor_thread.join(timeout=1.0)
        logger.info(f"🔍 Memory monitoring stopped")
    
    def _monitor_memory(self) -> None:
        """Background memory monitoring loop."""
        if not PSUTIL_AVAILABLE:
            logger.warning("Memory monitoring disabled - psutil not available")
            return

        try:
            process = psutil.Process()
            while self._monitoring_active:
                memory_mb = process.memory_info().rss / 1024 / 1024
                self.metrics.memory_samples.append(memory_mb)

                if memory_mb > self.metrics.peak_memory_mb:
                    self.metrics.peak_memory_mb = memory_mb

                time.sleep(0.1)  # Sample every 100ms
        except Exception as e:
            logger.warning(f"Memory monitoring error: {e}")
    
    def record_database_timing(self, connection_ms: float = None, 
                             execution_ms: float = None, fetch_ms: float = None) -> None:
        """Record database operation timings."""
        if connection_ms is not None:
            self.metrics.db_connection_time_ms = connection_ms
            logger.info(f"📊 DB Connection Time: {connection_ms:.2f}ms")
            
        if execution_ms is not None:
            self.metrics.query_execution_time_ms = execution_ms
            logger.info(f"📊 Query Execution Time: {execution_ms:.2f}ms")
            
        if fetch_ms is not None:
            self.metrics.result_fetch_time_ms = fetch_ms
            logger.info(f"📊 Result Fetch Time: {fetch_ms:.2f}ms")
    
    def record_processing_stats(self, records_count: int) -> None:
        """Record processing statistics."""
        self.metrics.records_processed = records_count

        if self.metrics.total_duration_ms and self.metrics.total_duration_ms > 0:
            self.metrics.records_per_second = (records_count / self.metrics.total_duration_ms) * 1000

        logger.info(f"📊 Processing Stats:")
        logger.info(f"   Records Processed: {records_count}")
        if self.metrics.records_per_second:
            logger.info(f"   Records/Second: {self.metrics.records_per_second:.2f}")

    def finalize(self) -> PerformanceMetrics:
        """Finalize monitoring and return complete metrics."""
        self.metrics.end_time = time.time()
        self.metrics.total_duration_ms = (self.metrics.end_time - self.metrics.start_time) * 1000

        # Stop memory monitoring
        self.stop_memory_monitoring()

        # Record final memory usage
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                self.metrics.final_memory_mb = process.memory_info().rss / 1024 / 1024
                self.metrics.cpu_usage_percent = process.cpu_percent()
                self.metrics.thread_count = process.num_threads()
            except Exception as e:
                logger.warning(f"Could not capture final system metrics: {e}")
        else:
            self.metrics.final_memory_mb = 0.0
            self.metrics.cpu_usage_percent = 0.0
            self.metrics.thread_count = 0

        # Calculate records per second if not already done
        if self.metrics.records_processed > 0 and not self.metrics.records_per_second:
            self.metrics.records_per_second = (self.metrics.records_processed / self.metrics.total_duration_ms) * 1000

        return self.metrics

    def log_performance_summary(self) -> None:
        """Log comprehensive performance summary."""
        logger.info("="*120)
        logger.info(f"📊 PERFORMANCE SUMMARY")
        logger.info(f"   KPI ID: {self.metrics.kpi_id}")
        logger.info(f"   KPI Type: {self.metrics.kpi_type}")
        logger.info(f"   Execution ID: {self.metrics.execution_id}")
        logger.info(f"   Total Duration: {self.metrics.total_duration_ms:.2f}ms")
        logger.info("="*120)

        # Timing breakdown
        if self.metrics.step_timings:
            logger.info(f"⏱️ TIMING BREAKDOWN:")
            total_step_time = 0
            for step_name, duration in self.metrics.step_timings.items():
                percentage = (duration / self.metrics.total_duration_ms) * 100 if self.metrics.total_duration_ms > 0 else 0
                logger.info(f"   {step_name}: {duration:.2f}ms ({percentage:.1f}%)")
                total_step_time += duration

            unaccounted_time = self.metrics.total_duration_ms - total_step_time
            if unaccounted_time > 0:
                unaccounted_percentage = (unaccounted_time / self.metrics.total_duration_ms) * 100
                logger.info(f"   Unaccounted Time: {unaccounted_time:.2f}ms ({unaccounted_percentage:.1f}%)")

        # Memory usage
        logger.info(f"💾 MEMORY USAGE:")
        logger.info(f"   Initial: {self.metrics.initial_memory_mb:.2f} MB")
        logger.info(f"   Peak: {self.metrics.peak_memory_mb:.2f} MB")
        logger.info(f"   Final: {self.metrics.final_memory_mb:.2f} MB")

        if self.metrics.initial_memory_mb and self.metrics.final_memory_mb:
            memory_delta = self.metrics.final_memory_mb - self.metrics.initial_memory_mb
            logger.info(f"   Delta: {memory_delta:+.2f} MB")

        # Database performance
        if any([self.metrics.db_connection_time_ms, self.metrics.query_execution_time_ms, self.metrics.result_fetch_time_ms]):
            logger.info(f"🗄️ DATABASE PERFORMANCE:")
            if self.metrics.db_connection_time_ms:
                logger.info(f"   Connection: {self.metrics.db_connection_time_ms:.2f}ms")
            if self.metrics.query_execution_time_ms:
                logger.info(f"   Query Execution: {self.metrics.query_execution_time_ms:.2f}ms")
            if self.metrics.result_fetch_time_ms:
                logger.info(f"   Result Fetch: {self.metrics.result_fetch_time_ms:.2f}ms")

        # Processing statistics
        logger.info(f"📈 PROCESSING STATISTICS:")
        logger.info(f"   Records Processed: {self.metrics.records_processed}")
        if self.metrics.records_per_second:
            logger.info(f"   Records/Second: {self.metrics.records_per_second:.2f}")

        # System resources
        if self.metrics.cpu_usage_percent is not None:
            logger.info(f"🖥️ SYSTEM RESOURCES:")
            logger.info(f"   CPU Usage: {self.metrics.cpu_usage_percent:.1f}%")
            logger.info(f"   Thread Count: {self.metrics.thread_count}")

        # Performance insights
        self._log_performance_insights()

        logger.info("="*120)

    def _log_performance_insights(self) -> None:
        """Log performance insights and recommendations."""
        logger.info(f"💡 PERFORMANCE INSIGHTS:")

        # Timing insights
        if self.metrics.total_duration_ms:
            if self.metrics.total_duration_ms < 1000:
                logger.info(f"   ✅ Excellent response time: {self.metrics.total_duration_ms:.0f}ms")
            elif self.metrics.total_duration_ms < 5000:
                logger.info(f"   ✅ Good response time: {self.metrics.total_duration_ms:.0f}ms")
            elif self.metrics.total_duration_ms < 10000:
                logger.info(f"   ⚠️ Moderate response time: {self.metrics.total_duration_ms:.0f}ms")
            else:
                logger.info(f"   ❌ Slow response time: {self.metrics.total_duration_ms:.0f}ms")

        # Memory insights
        if self.metrics.initial_memory_mb and self.metrics.peak_memory_mb:
            memory_increase = self.metrics.peak_memory_mb - self.metrics.initial_memory_mb
            if memory_increase > 100:
                logger.info(f"   ⚠️ High memory usage increase: {memory_increase:.1f}MB")
            elif memory_increase > 50:
                logger.info(f"   ⚠️ Moderate memory usage increase: {memory_increase:.1f}MB")
            else:
                logger.info(f"   ✅ Low memory usage increase: {memory_increase:.1f}MB")

        # Processing efficiency
        if self.metrics.records_per_second:
            if self.metrics.records_per_second > 1000:
                logger.info(f"   ✅ High processing throughput: {self.metrics.records_per_second:.0f} records/sec")
            elif self.metrics.records_per_second > 100:
                logger.info(f"   ✅ Good processing throughput: {self.metrics.records_per_second:.0f} records/sec")
            else:
                logger.info(f"   ⚠️ Low processing throughput: {self.metrics.records_per_second:.0f} records/sec")


def create_performance_monitor(kpi_id: str = None, kpi_type: str = None, execution_id: str = None) -> KPIPerformanceMonitor:
    """Factory function to create a performance monitor."""
    return KPIPerformanceMonitor(kpi_id=kpi_id, kpi_type=kpi_type, execution_id=execution_id)
