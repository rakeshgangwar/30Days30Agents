"""
Data Analysis Agent - FastAPI Backend

This is the main entry point for the FastAPI application.
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.schemas import HealthCheckResponse
from app.routers import csv_analysis, sql_analysis
from app.services.llm_service import test_llm_connection

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_TITLE,
    description="API for analyzing and visualizing data using natural language queries",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(csv_analysis.router)
app.include_router(sql_analysis.router)


@app.get("/", response_model=HealthCheckResponse)
async def root():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        HealthCheckResponse: API status information
    """
    return {
        "status": "Welcome to the Data Analysis Agent API!",
        "version": "0.1.0"
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        HealthCheckResponse: API status information
    """
    return {
        "status": "healthy",
        "version": "0.1.0"
    }


@app.get("/test-llm", response_model=dict)
async def test_llm():
    """
    Test the LLM connection.
    
    Returns:
        dict: LLM connection test results
    """
    result = test_llm_connection()
    if not result["success"]:
        return JSONResponse(
            status_code=500,
            content=result
        )
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
