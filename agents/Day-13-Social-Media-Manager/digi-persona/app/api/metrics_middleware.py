"""
Metrics middleware module.

This module provides middleware for tracking metrics.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.endpoints.metrics import track_request_start, track_request_end

class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track request metrics.
    
    This middleware tracks the number of requests, request latency, and active requests.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and track metrics.
        
        Args:
            request: The incoming request.
            call_next: The next middleware or route handler.
            
        Returns:
            Response: The response from the next middleware or route handler.
        """
        # Track request start
        track_request_start(request)
        
        # Process the request
        response = await call_next(request)
        
        # Track request end
        track_request_end(request, response)
        
        return response
