"""
Business logic layer for booking operations.
Handles business rules, validation, and orchestrates domain operations.
"""

import logging
from typing import List, Optional
from datetime import datetime
import pytz

from src.domain.models import (
    Class, ClassResponse, BookingRequest, BookingResponse, Booking
)
from src.domain.repository import BookingRepositoryInterface

logger = logging.getLogger(__name__)

class BookingResult:
    """Result class for booking operations."""
    
    def __init__(self, success: bool, message: str, data: Optional[dict] = None):
        self.success = success
        self.message = message
        self.data = data or {}

class BookingService:
    """Service layer for booking business logic."""
    
    def __init__(self, repository: BookingRepositoryInterface):
        """Initialize service with repository dependency."""
        self.repository = repository
        self.logger = logging.getLogger(__name__)
    
    def get_upcoming_classes(self, timezone: str = "Asia/Kolkata") -> List[ClassResponse]:
        """Get all upcoming fitness classes with timezone conversion."""
        try:
            self.logger.info(f"Retrieving upcoming classes for timezone: {timezone}")
            
            # Get classes from repository
            classes = self.repository.get_all_upcoming_classes()
            
            # Convert to response models with timezone conversion
            class_responses = []
            for class_obj in classes:
                try:
                    response = ClassResponse.from_class(class_obj, timezone)
                    class_responses.append(response)
                except Exception as e:
                    self.logger.warning(f"Error converting class {class_obj.id} to response: {e}")
                    continue
            
            self.logger.info(f"Successfully converted {len(class_responses)} classes")
            return class_responses
            
        except Exception as e:
            self.logger.error(f"Error retrieving upcoming classes: {e}")
            raise
    
    def get_class_by_id(self, class_id: int, timezone: str = "Asia/Kolkata") -> Optional[ClassResponse]:
        """Get a specific class by ID with timezone conversion."""
        try:
            self.logger.info(f"Retrieving class {class_id} for timezone: {timezone}")
            
            class_obj = self.repository.get_class_by_id(class_id)
            
            if not class_obj:
                self.logger.warning(f"Class {class_id} not found")
                return None
            
            response = ClassResponse.from_class(class_obj, timezone)
            self.logger.info(f"Successfully retrieved class {class_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error retrieving class {class_id}: {e}")
            raise
    
    def create_booking(self, booking_request: BookingRequest) -> BookingResult:
        """Create a new booking with comprehensive validation."""
        try:
            self.logger.info(f"Processing booking request for class {booking_request.class_id}")
            
            # Validate class exists and is upcoming
            class_obj = self.repository.get_class_by_id(booking_request.class_id)
            if not class_obj:
                return BookingResult(
                    success=False,
                    message=f"Class with ID {booking_request.class_id} not found"
                )
            
            # Check if class is in the future
            try:
                class_datetime = datetime.fromisoformat(class_obj.datetime_utc.replace('Z', '+00:00'))
                class_datetime = class_datetime.replace(tzinfo=pytz.UTC)
                now_utc = datetime.now(pytz.UTC)
                
                if class_datetime <= now_utc:
                    return BookingResult(
                        success=False,
                        message="Cannot book past or ongoing classes"
                    )
            except Exception as e:
                self.logger.error(f"Error parsing class datetime: {e}")
                return BookingResult(
                    success=False,
                    message="Invalid class datetime"
                )
            
            # Check available slots
            if class_obj.available_slots <= 0:
                return BookingResult(
                    success=False,
                    message=f"Class '{class_obj.name}' is fully booked"
                )
            
            # Check for existing booking
            existing_booking = self.repository.check_existing_booking(
                booking_request.class_id,
                booking_request.client_email
            )
            
            if existing_booking:
                return BookingResult(
                    success=False,
                    message=f"You already have a booking for this class"
                )
            
            # Create the booking
            booking = self.repository.create_booking(booking_request)
            
            if not booking:
                return BookingResult(
                    success=False,
                    message="Failed to create booking. Please try again."
                )
            
            self.logger.info(f"Successfully created booking {booking.id}")
            return BookingResult(
                success=True,
                message=f"Successfully booked '{class_obj.name}' class with {class_obj.instructor}",
                data={"booking_id": booking.id}
            )
            
        except Exception as e:
            self.logger.error(f"Error creating booking: {e}")
            return BookingResult(
                success=False,
                message="Internal error occurred while processing booking"
            )
    
    def get_bookings_by_email(self, email: str, timezone: str = "Asia/Kolkata") -> List[BookingResponse]:
        """Get all bookings for a specific email with timezone conversion."""
        try:
            self.logger.info(f"Retrieving bookings for {email} in timezone: {timezone}")
            
            # Validate email format (basic validation)
            if not email or "@" not in email:
                self.logger.warning(f"Invalid email format: {email}")
                return []
            
            # Get bookings from repository
            booking_data_list = self.repository.get_bookings_by_email(email)
            
            # Convert to response models with timezone conversion
            booking_responses = []
            for booking_data in booking_data_list:
                try:
                    response = BookingResponse.from_booking_with_class(booking_data, timezone)
                    booking_responses.append(response)
                except Exception as e:
                    self.logger.warning(f"Error converting booking {booking_data.get('id')} to response: {e}")
                    continue
            
            self.logger.info(f"Successfully retrieved {len(booking_responses)} bookings for {email}")
            return booking_responses
            
        except Exception as e:
            self.logger.error(f"Error retrieving bookings for {email}: {e}")
            raise
    
    def cancel_booking(self, booking_id: int, client_email: str) -> BookingResult:
        """Cancel a booking if it exists and belongs to the client."""
        self.logger.info(f"Attempting to cancel booking {booking_id} for {client_email}")
        self.logger.debug(f"Booking ID: {booking_id}, Client Email: {client_email}")
        try:
            result = self.repository.cancel_booking(booking_id, client_email)
            if result:
                self.logger.info(f"Successfully cancelled booking {booking_id}")
                return BookingResult(
                    success=True,
                    message="Booking cancelled successfully"
                )
            else:
                self.logger.warning(f"Booking {booking_id} not found or not owned by {client_email}")
                return BookingResult(
                    success=False,
                    message="Booking not found or not owned by this email"
                )
        except Exception as e:
            self.logger.error(f"Error cancelling booking {booking_id}: {e}")
            return BookingResult(
                success=False,
                message="Internal error occurred while cancelling booking"
            )
    
    def get_class_availability(self, class_id: int) -> Optional[dict]:
        """Get detailed availability information for a class."""
        try:
            class_obj = self.repository.get_class_by_id(class_id)
            if not class_obj:
                return None
            
            availability_info = {
                "class_id": class_obj.id,
                "class_name": class_obj.name,
                "total_slots": class_obj.total_slots,
                "available_slots": class_obj.available_slots,
                "booked_slots": class_obj.total_slots - class_obj.available_slots,
                "is_available": class_obj.available_slots > 0
            }
            
            return availability_info
            
        except Exception as e:
            self.logger.error(f"Error getting availability for class {class_id}: {e}")
            raise
