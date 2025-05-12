"""
Script to run the Learning Coach Agent API.
"""

import logging
import os

import uvicorn
from dotenv import load_dotenv

from app.db.init_db import init_db


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the application."""
    # Load environment variables
    load_dotenv()

    # Log environment variables (without showing actual values)
    logger.info("Environment variables loaded")
    logger.info(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    logger.info(f"OPENAI_MODEL: {os.getenv('OPENAI_MODEL', 'Not set')}")

    # Initialize database
    logger.info("Initializing database")
    init_db()

    # Run the API server
    logger.info("Starting API server")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )


if __name__ == "__main__":
    main()
