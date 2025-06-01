"""Meeting Assistant - Entry Point"""

import uvicorn
from config.settings import settings
from config.logging import logger


def main():
    """Run the Meeting Assistant API server"""
    logger.info(f"Starting Meeting Assistant API in {settings.ENVIRONMENT} environment")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    logger.info(f"Allowed origins: {settings.ALLOWED_ORIGINS}")
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
