"""
FastAPI application setup and routing.
Main API configuration and dependency injection.
"""

import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.config.database import init_database, get_database
from src.config.setup_logger import setup_logger
from src.domain.repository import BookingRepository
from src.service.booking_service import BookingService
from src.port.booking_port import BookingRouter

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Initializing database...")
    init_database()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down application...")

# Create FastAPI application
app = FastAPI(
    title="Fitness Studio Booking API",
    description="A FastAPI-based fitness studio booking system with timezone management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection for services
def get_booking_service() -> BookingService:
    """Dependency injection for BookingService."""
    db = get_database()
    repository = BookingRepository(db)
    return BookingService(repository)

# Initialize and include routers
booking_router = BookingRouter()
app.include_router(
    booking_router.get_router(),
    dependencies=[Depends(get_booking_service)]
)

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "Fitness Studio Booking API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
