from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import logging
from datetime import datetime, timezone

from .agent import TravelAgent

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend's URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler('travel_agent.log')  # Log to file
    ]
)
logger = logging.getLogger(__name__)


class Interest(BaseModel):
    """Interest model for travel preferences."""
    name: str
    importance: Optional[int] = Field(None, ge=1, le=5, description="Importance from 1-5")


class Preferences(BaseModel):
    """Preferences model for travel requests."""
    budget: str = Field(..., description="Budget level (budget, medium, luxury)")
    interests: List[str] = Field(..., description="List of interests")
    transportation: str = Field(..., description="Preferred transportation mode")
    accommodation_type: str = Field(..., description="Type of accommodation")
    pace: str = Field(..., description="Travel pace (relaxed, moderate, busy)")


class TravelRequest(BaseModel):
    """Travel request model for itinerary generation."""
    from_location: str = Field(..., description="Starting location")
    to_location: str = Field(..., description="Destination location")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    preferences: Preferences = Field(..., description="Travel preferences")
    number_of_travelers: int = Field(..., ge=1, description="Number of travelers")
    include_weather: bool = Field(True, description="Include weather information")
    include_local_tips: bool = Field(True, description="Include local tips")


# Initialize the travel agent with the OpenAI API key
logger.info("Environment Variables:")
logger.info(f"OPENAI_API_KEY present: {'OPENAI_API_KEY' in os.environ}")
logger.info(f"GOOGLE_MAPS_API_KEY present: {'GOOGLE_MAPS_API_KEY' in os.environ}")
logger.info(f"TAVILY_API_KEY present: {'TAVILY_API_KEY' in os.environ}")
logger.info(f"OPENWEATHERMAP_API_KEY present: {'OPENWEATHERMAP_API_KEY' in os.environ}")

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.error("OPENAI_API_KEY environment variable is not set!")
    raise ValueError("OPENAI_API_KEY environment variable is not set!")

agent = TravelAgent(openai_api_key=openai_api_key)


@app.get("/")
async def root():
    """Root endpoint to check if the API is running."""
    return {"message": "Travel Planning Agent API is running"}


@app.post("/api/v1/generate-itinerary")
async def generate_itinerary(request: TravelRequest):
    """Generate a travel itinerary based on the provided request."""
    logger.info(f"Received itinerary request for {request.from_location} to {request.to_location}")
    try:
        itinerary = await agent.generate_itinerary(request.model_dump())
        logger.info("Itinerary generated successfully")
        return itinerary
    except Exception as e:
        error_msg = f"Error generating itinerary: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("agent.api:app", host="0.0.0.0", port=8000, reload=True)
