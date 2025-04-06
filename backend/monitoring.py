# backend/monitoring.py

from fastapi import APIRouter
from prometheus_client import Counter, generate_latest, CollectorRegistry
from starlette.responses import Response

router = APIRouter()

# Create a registry and metrics counters
REQUEST_COUNT = Counter(
    "request_count", "App Request Count", ["method", "endpoint", "http_status"]
)

@router.get("/metrics")
def metrics():
    """
    Expose Prometheus metrics.
    """
    content = generate_latest()
    return Response(content=content, media_type="text/plain")
