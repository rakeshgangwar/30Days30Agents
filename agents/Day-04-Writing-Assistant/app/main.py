"""
Writing Assistant API
Main application entry point for the FastAPI server.
"""
import logging
import sys
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, parent_dir)

# Use absolute imports which work in both cases
from app.core.config import settings
from app.utils.logging_config import setup_logging
from app.db.database import engine
from app.models.preferences import UserPreference
from app.models import preferences

# Initialize database tables
preferences.Base.metadata.create_all(bind=engine)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url=settings.DOCS_URL,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.routers import drafting, grammar, summarization, tone, preferences, models

app.include_router(drafting.router, prefix="/api/v1", tags=["drafting"])
app.include_router(grammar.router, prefix="/api/v1", tags=["grammar"])
app.include_router(summarization.router, prefix="/api/v1", tags=["summarization"])
app.include_router(tone.router, prefix="/api/v1", tags=["tone"])
app.include_router(preferences.router, prefix="/api/v1", tags=["preferences"])
app.include_router(models.router, prefix="/api/v1", tags=["models"])

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting {settings.APP_NAME} API")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )