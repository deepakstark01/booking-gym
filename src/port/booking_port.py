"""
FastAPI port layer for booking operations.
Handles HTTP requests and responses with proper error handling.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from src.domain.models import (
    ClassResponse, BookingRequest, BookingResponse, 
    ErrorResponse, SuccessResponse, TimezoneQuery
)
from src.service.booking_service import BookingService
from src.config.database import get_database
from src.domain.repository import BookingRepository

logger = logging.getLogger(__name__)

class BookingRouter:
    """FastAPI router for booking operations."""
    
    def __init__(self):
        """Initialize booking router."""
        self.router = APIRouter(
            prefix="/api/v1",
            tags=["fitness-booking"],
            responses={
                400: {"model": ErrorResponse, "description": "Bad Request"},
                404: {"model": ErrorResponse, "description": "Not Found"},
                500: {"model": ErrorResponse, "description": "Internal Server Error"}
            }
        )
        self._setup_routes()
    
    def get_router(self) -> APIRouter:
        """Get the configured router."""
        return self.router
    
    def _get_booking_service(self) -> BookingService:
        """Dependency injection for BookingService."""
        # Pass the function, not the context manager instance
        repository = BookingRepository(get_database)
        return BookingService(repository)
    
    def _setup_routes(self):
        """Setup all route handlers."""
        
        @self.router.get(
            "/classes",
            response_model=List[ClassResponse],
            summary="Get all upcoming fitness classes",
            description="Retrieve all upcoming fitness classes with timezone conversion"
        )
        async def get_classes(
            timezone: str = Query(
                default="Asia/Kolkata",
                description="Target timezone for datetime conversion (e.g., 'Asia/Kolkata', 'America/New_York')"
            ),
            booking_service: BookingService = Depends(self._get_booking_service)
        ):
            """Get all upcoming fitness classes."""
            try:
                logger.info(f"Getting classes for timezone: {timezone}")
                
                # Validate timezone
                try:
                    timezone_query = TimezoneQuery(timezone=timezone)
                    validated_timezone = timezone_query.timezone
                except ValueError as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid timezone: {str(e)}"
                    )
                
                classes = booking_service.get_upcoming_classes(validated_timezone)
                logger.info(f"Returning {len(classes)} classes")
                return classes
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting classes: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="Internal server error while retrieving classes"
                )
        
        @self.router.post(
            "/book",
            response_model=SuccessResponse,
            summary="Book a fitness class",
            description="Create a booking for a fitness class with validation"
        )
        async def book_class(
            booking_request: BookingRequest,
            booking_service: BookingService = Depends(self._get_booking_service)
        ):
            """Book a fitness class."""
            try:
                logger.info(f"Booking request for class {booking_request.class_id} by {booking_request.client_email}")
                
                result = booking_service.create_booking(booking_request)
                
                if result.success:
                    logger.info(f"Booking successful: {result.message}")
                    return SuccessResponse(
                        message=result.message,
                        data={"booking_id": result.data.get("booking_id") if result.data else None}
                    )
                else:
                    logger.warning(f"Booking failed: {result.message}")
                    
                    # Determine appropriate HTTP status code based on error
                    if "not found" in result.message.lower():
                        status_code = 404
                    elif any(phrase in result.message.lower() for phrase in 
                           ["no slots", "already booked", "fully booked"]):
                        status_code = 400
                    else:
                        status_code = 400
                    
                    raise HTTPException(
                        status_code=status_code,
                        detail=result.message
                    )
                    
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error creating booking: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="Internal server error while creating booking"
                )
        
        @self.router.get(
            "/bookings",
            response_model=List[BookingResponse],
            summary="Get bookings by email",
            description="Retrieve all bookings for a specific email address with timezone conversion"
        )
        async def get_bookings(
            email: str = Query(..., description="Client email address"),
            timezone: str = Query(
                default="Asia/Kolkata",
                description="Target timezone for datetime conversion"
            ),
            booking_service: BookingService = Depends(self._get_booking_service)
        ):
            """Get all bookings for a specific email."""
            try:
                logger.info(f"Getting bookings for email: {email}, timezone: {timezone}")
                
                # Validate email format
                if not email or "@" not in email:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid email address"
                    )
                
                # Validate timezone
                try:
                    timezone_query = TimezoneQuery(timezone=timezone)
                    validated_timezone = timezone_query.timezone
                except ValueError as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid timezone: {str(e)}"
                    )
                
                bookings = booking_service.get_bookings_by_email(email, validated_timezone)
                logger.info(f"Returning {len(bookings)} bookings for {email}")
                return bookings
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting bookings for {email}: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="Internal server error while retrieving bookings"
                )
        
        @self.router.get(
            "/classes/{class_id}",
            response_model=ClassResponse,
            summary="Get a specific class by ID",
            description="Retrieve details of a specific fitness class"
        )
        async def get_class(
            class_id: int,
            timezone: str = Query(
                default="Asia/Kolkata",
                description="Target timezone for datetime conversion"
            ),
            booking_service: BookingService = Depends(self._get_booking_service)
        ):
            """Get a specific class by ID."""
            try:
                logger.info(f"Getting class {class_id} for timezone: {timezone}")
                
                # Validate timezone
                try:
                    timezone_query = TimezoneQuery(timezone=timezone)
                    validated_timezone = timezone_query.timezone
                except ValueError as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid timezone: {str(e)}"
                    )
                
                class_obj = booking_service.get_class_by_id(class_id, validated_timezone)
                
                if not class_obj:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Class with ID {class_id} not found"
                    )
                
                logger.info(f"Returning class {class_id}")
                return class_obj
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting class {class_id}: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="Internal server error while retrieving class"
                )
