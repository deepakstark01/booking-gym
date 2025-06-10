"""
Main entry point for the Fitness Studio Booking API.
Initializes the FastAPI application and starts the server.
"""

import uvicorn
import logging
from src.api import app
from src.config.setup_logger import setup_logger

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Fitness Studio Booking API server...")
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
