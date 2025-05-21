from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import personas, content, platforms, interactions, scheduling, auth, analytics, suggestions, metrics
from app.core.config import settings
from app.api.middleware import persona_middleware
from app.api.metrics_middleware import MetricsMiddleware
from app.db.session import create_tables

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifespan events for the application."""
    # Startup: Create tables if they don't exist
    create_tables()
    yield
    # Shutdown: Clean up resources if needed
    pass

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.APP_NAME,
    description="API for managing multiple virtual personas with social media presence",
    version="0.1.0",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middlewares
app.middleware("http")(persona_middleware)
app.add_middleware(MetricsMiddleware)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["auth"])
app.include_router(personas.router, prefix=f"{settings.API_PREFIX}/personas", tags=["personas"])
app.include_router(content.router, prefix=f"{settings.API_PREFIX}/content", tags=["content"])
app.include_router(platforms.router, prefix=f"{settings.API_PREFIX}/platforms", tags=["platforms"])
app.include_router(interactions.router, prefix=f"{settings.API_PREFIX}/interactions", tags=["interactions"])
app.include_router(scheduling.router, prefix=f"{settings.API_PREFIX}/scheduling", tags=["scheduling"])
app.include_router(analytics.router, prefix=f"{settings.API_PREFIX}/analytics", tags=["analytics"])
app.include_router(suggestions.router, prefix=f"{settings.API_PREFIX}/content", tags=["content"])
app.include_router(metrics.router, tags=["metrics"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Digi-Persona API",
        "docs": f"{settings.API_PREFIX}/docs",
    }

@app.get(f"{settings.API_PREFIX}/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
