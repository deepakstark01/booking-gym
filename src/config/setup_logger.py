"""
Logging configuration setup.
Configures application-wide logging with appropriate formatters and handlers.
"""

import logging
import sys
from datetime import datetime

def setup_logger() -> None:
    """Setup application logging configuration."""
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Create file handler
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Setup specific loggers
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)
    
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.setLevel(logging.INFO)
    
    # Application logger
    app_logger = logging.getLogger("src")
    app_logger.setLevel(logging.DEBUG)
    
    logging.info("Logging configuration setup completed")
