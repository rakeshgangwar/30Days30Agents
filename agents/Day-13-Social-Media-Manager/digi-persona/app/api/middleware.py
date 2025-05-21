from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.personas.context import persona_context

async def persona_middleware(request: Request, call_next):
    """
    Middleware to set persona context from request.
    
    Args:
        request: The incoming request.
        call_next: The next middleware or route handler.
        
    Returns:
        Response: The response from the next middleware or route handler.
    """
    # Extract persona ID from header
    persona_id_header = request.headers.get("X-Persona-ID")
    
    # Set persona ID in context if present
    if persona_id_header and persona_id_header.isdigit():
        persona_context.set_persona(int(persona_id_header))
    
    # Process the request
    response = await call_next(request)
    
    return response
