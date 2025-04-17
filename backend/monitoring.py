# backend/monitoring.py

import logging
import time
import threading
import psutil
from fastapi import APIRouter
from prometheus_client import (
    Counter, Gauge, Histogram, Summary, generate_latest, 
    CollectorRegistry, CONTENT_TYPE_LATEST
)
from starlette.responses import Response
from backend.config import MONITORING_INTERVAL, MONITORING_THRESHOLD

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Create metrics
REQUEST_COUNT = Counter(
    "request_count", "App Request Count", ["method", "endpoint", "http_status"]
)

INPROGRESS_REQUESTS = Gauge(
    "inprogress_requests", "Number of in-progress requests"
)

RESPONSE_TIME = Histogram(
    "response_time", "Response Time in seconds", ["endpoint"]
)

QUERY_LATENCY = Summary(
    "query_processing_seconds", "Time spent processing queries"
)

SYSTEM_MEMORY = Gauge(
    "system_memory_usage_percent", "System memory usage in percent"
)

SYSTEM_CPU = Gauge(
    "system_cpu_usage_percent", "System CPU usage in percent"
)

SYSTEM_DISK = Gauge(
    "system_disk_usage_percent", "System disk usage in percent"
)

DOCUMENT_COUNT = Gauge(
    "document_count", "Number of documents in the system"
)

CHUNK_COUNT = Gauge(
    "chunk_count", "Number of document chunks in the system"
)

EMBEDDING_TIME = Histogram(
    "embedding_generation_seconds", "Time spent generating embeddings"
)

LLM_GENERATION_TIME = Histogram(
    "llm_generation_seconds", "Time spent generating LLM responses"
)

# Monitoring thread stop flag
stop_monitoring = threading.Event()

def collect_system_metrics():
    """Collect system metrics like CPU, memory, and disk usage."""
    try:
        # Memory usage
        memory_percent = psutil.virtual_memory().percent
        SYSTEM_MEMORY.set(memory_percent)
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        SYSTEM_CPU.set(cpu_percent)
        
        # Disk usage
        disk_percent = psutil.disk_usage('/').percent
        SYSTEM_DISK.set(disk_percent)
        
        # Log warning if any metrics exceed threshold
        if (memory_percent > MONITORING_THRESHOLD * 100 or 
            cpu_percent > MONITORING_THRESHOLD * 100 or 
            disk_percent > MONITORING_THRESHOLD * 100):
            logger.warning(
                f"System resources near capacity: Memory={memory_percent}%, "
                f"CPU={cpu_percent}%, Disk={disk_percent}%"
            )
    except Exception as e:
        logger.error(f"Error collecting system metrics: {e}")

def monitoring_loop():
    """Background thread for periodic system metrics collection."""
    logger.info("Starting system metrics monitoring")
    while not stop_monitoring.is_set():
        try:
            collect_system_metrics()
            time.sleep(MONITORING_INTERVAL)
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            time.sleep(MONITORING_INTERVAL)

# Start monitoring thread
monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
monitoring_thread.start()

@router.get("/metrics")
def metrics():
    """
    Expose Prometheus metrics endpoint.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Custom metrics context managers for timing operations
class TimerContextManager:
    """Context manager for timing operations and recording in Prometheus metrics."""
    
    def __init__(self, metric, labels=None):
        self.metric = metric
        self.labels = labels or {}
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            if self.labels:
                self.metric.labels(**self.labels).observe(duration)
            else:
                self.metric.observe(duration)

# Convenient timer functions
def time_embedding_generation():
    """Time the embedding generation process."""
    return TimerContextManager(EMBEDDING_TIME)

def time_llm_generation():
    """Time the LLM response generation process."""
    return TimerContextManager(LLM_GENERATION_TIME)

def time_query_processing():
    """Time the overall query processing."""
    return TimerContextManager(QUERY_LATENCY)

# Function to update document counts
def update_document_counts(doc_count, chunk_count):
    """Update the document and chunk count metrics."""
    DOCUMENT_COUNT.set(doc_count)
    CHUNK_COUNT.set(chunk_count)

# Cleanup function to stop the monitoring thread
def stop_monitoring_thread():
    """Stop the background monitoring thread."""
    stop_monitoring.set()
    if monitoring_thread.is_alive():
        monitoring_thread.join(timeout=5)
    logger.info("Monitoring thread stopped")