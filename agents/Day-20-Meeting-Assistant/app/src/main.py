"""
Meeting Assistant - Main FastAPI Application
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Import configuration and logging
from config.settings import settings
from config.logging import logger

# Import API routes
from src.api.audio_routes import router as audio_router
from src.api.llm_routes import router as llm_router
from src.api.meeting_routes import router as meeting_router

# No need to configure logging here as it's now in config/logging.py


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info(f"Starting Meeting Assistant API in {settings.ENVIRONMENT} environment...")
    
    # Startup
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.CHUNK_DIR, exist_ok=True)
    os.makedirs(settings.MODEL_DIR, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Initialize database
    from src.database import init_database
    await init_database()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    from src.database import close_database
    await close_database()
    logger.info("Shutting down Meeting Assistant API...")


# Create FastAPI app
app = FastAPI(
    title="Meeting Assistant API",
    description="AI-powered meeting assistant for transcription, speaker diarization, and intelligent summarization",
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Add CORS middleware with settings from configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Meeting Assistant API",
        "version": "0.1.0",
        "status": "running",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Meeting Assistant API is running"}


@app.get("/health/db")
async def database_health_check():
    """Database health check endpoint"""
    try:
        from src.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        try:
            # Simple query to test database connection
            result = db.execute(text("SELECT 1"))
            result.fetchone()
            return {
                "status": "healthy",
                "message": "Database connection successful",
                "database_type": "SQLite" if "sqlite" in str(db.bind.url) else "PostgreSQL"
            }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }


@app.get("/config")
async def get_config():
    """Get non-sensitive configuration settings"""
    # Return only non-sensitive configuration for debugging
    safe_config = {
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "log_level": settings.LOG_LEVEL,
        "chunk_size_minutes": settings.CHUNK_SIZE_MINUTES,
        "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
        "whisper_model": settings.WHISPER_MODEL,
        "enable_gpu": settings.ENABLE_GPU,
        "use_local_llm": settings.USE_LOCAL_LLM,
    }
    return safe_config


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Include API routers
app.include_router(audio_router)
app.include_router(llm_router)
app.include_router(meeting_router)

# Remove the uvicorn.run code since we're now running from main.py