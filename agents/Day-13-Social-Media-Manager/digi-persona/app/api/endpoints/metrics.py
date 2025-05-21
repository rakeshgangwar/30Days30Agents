"""
Metrics API Endpoints Module

This module provides API endpoints for Prometheus metrics.
"""

from fastapi import APIRouter, Request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time

# Create router
router = APIRouter()

# Define metrics
REQUEST_COUNT = Counter(
    'digi_persona_request_count', 
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'digi_persona_request_latency_seconds', 
    'Request latency in seconds',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'digi_persona_active_requests',
    'Number of active requests'
)

CONTENT_COUNT = Counter(
    'digi_persona_content_count',
    'Number of content items created',
    ['persona_id', 'platform', 'status']
)

INTERACTION_COUNT = Counter(
    'digi_persona_interaction_count',
    'Number of interactions',
    ['persona_id', 'platform', 'type']
)

PERSONA_COUNT = Gauge(
    'digi_persona_persona_count',
    'Number of personas'
)

PLATFORM_CONNECTION_COUNT = Gauge(
    'digi_persona_platform_connection_count',
    'Number of platform connections',
    ['platform']
)

@router.get("/metrics")
async def metrics():
    """
    Get Prometheus metrics.
    
    Returns:
        Prometheus metrics in the text format.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Helper functions to update metrics
def track_request_start(request: Request):
    """Track the start of a request."""
    ACTIVE_REQUESTS.inc()
    request.state.start_time = time.time()

def track_request_end(request: Request, response):
    """Track the end of a request."""
    ACTIVE_REQUESTS.dec()
    
    # Skip tracking metrics endpoint itself to avoid recursion
    if request.url.path.endswith("/metrics"):
        return
    
    # Get request details
    method = request.method
    endpoint = request.url.path
    status_code = response.status_code
    
    # Update metrics
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    
    # Calculate and record latency
    latency = time.time() - request.state.start_time
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)

def track_content_creation(persona_id: int, platform: str, status: str):
    """Track content creation."""
    CONTENT_COUNT.labels(persona_id=str(persona_id), platform=platform, status=status).inc()

def track_interaction(persona_id: int, platform: str, interaction_type: str):
    """Track interaction."""
    INTERACTION_COUNT.labels(persona_id=str(persona_id), platform=platform, type=interaction_type).inc()

def update_persona_count(count: int):
    """Update persona count."""
    PERSONA_COUNT.set(count)

def update_platform_connection_count(platform: str, count: int):
    """Update platform connection count."""
    PLATFORM_CONNECTION_COUNT.labels(platform=platform).set(count)
