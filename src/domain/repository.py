"""
Repository interfaces and implementations.
Handles data access layer with clean architecture principles.
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

from src.domain.models import Class, Booking, BookingRequest
from src.db_schema import Queries

logger = logging.getLogger(__name__)

class BookingRepositoryInterface(ABC):
    """Abstract repository interface for booking operations."""
    
    @abstractmethod
    def get_all_upcoming_classes(self) -> List[Class]:
        """Get all upcoming fitness classes."""
        pass
    
    @abstractmethod
    def get_class_by_id(self, class_id: int) -> Optional[Class]:
        """Get a specific class by ID."""
        pass
    
    @abstractmethod
    def create_booking(self, booking_request: BookingRequest) -> Optional[Booking]:
        """Create a new booking."""
        pass
    
    @abstractmethod
    def get_bookings_by_email(self, email: str) -> List[Dict[str, Any]]:
        """Get all bookings for a specific email."""
        pass
    
    @abstractmethod
    def check_existing_booking(self, class_id: int, email: str) -> bool:
        """Check if user already has a booking for this class."""
        pass
    
    @abstractmethod
    def update_class_slots(self, class_id: int) -> bool:
        """Reduce available slots for a class."""
        pass

class BookingRepository(BookingRepositoryInterface):
    """SQLite implementation of booking repository."""
    
    def __init__(self, db_context):
        """Initialize repository with database context."""
        self.db_context = db_context
    
    def get_all_upcoming_classes(self) -> List[Class]:
        """Get all upcoming fitness classes."""
        try:
            with self.db_context as conn:
                cursor = conn.cursor()
                cursor.execute(Queries.GET_ALL_UPCOMING_CLASSES)
                rows = cursor.fetchall()
                
                classes = []
                for row in rows:
                    class_obj = Class(
                        id=row['id'],
                        name=row['name'],
                        instructor=row['instructor'],
                        datetime_utc=row['datetime_utc'],
                        timezone=row['timezone'],
                        total_slots=row['total_slots'],
                        available_slots=row['available_slots']
                    )
                    classes.append(class_obj)
                
                logger.info(f"Retrieved {len(classes)} upcoming classes")
                return classes
                
        except Exception as e:
            logger.error(f"Error retrieving classes: {e}")
            raise
    
    def get_class_by_id(self, class_id: int) -> Optional[Class]:
        """Get a specific class by ID."""
        try:
            with self.db_context as conn:
                cursor = conn.cursor()
                cursor.execute(Queries.GET_CLASS_BY_ID, (class_id,))
                row = cursor.fetchone()
                
                if row:
                    class_obj = Class(
                        id=row['id'],
                        name=row['name'],
                        instructor=row['instructor'],
                        datetime_utc=row['datetime_utc'],
                        timezone=row['timezone'],
                        total_slots=row['total_slots'],
                        available_slots=row['available_slots']
                    )
                    logger.info(f"Retrieved class {class_id}")
                    return class_obj
                else:
                    logger.warning(f"Class {class_id} not found")
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving class {class_id}: {e}")
            raise
    
    def create_booking(self, booking_request: BookingRequest) -> Optional[Booking]:
        """Create a new booking with transaction support."""
        try:
            with self.db_context as conn:
                cursor = conn.cursor()
                
                # Start transaction
                conn.execute("BEGIN")
                
                try:
                    # Check if class exists and has available slots
                    cursor.execute(Queries.GET_CLASS_BY_ID, (booking_request.class_id,))
                    class_row = cursor.fetchone()
                    
                    if not class_row:
                        logger.warning(f"Class {booking_request.class_id} not found")
                        return None
                    
                    if class_row['available_slots'] <= 0:
                        logger.warning(f"No available slots for class {booking_request.class_id}")
                        return None
                    
                    # Check for existing booking
                    cursor.execute(Queries.CHECK_EXISTING_BOOKING, 
                                 (booking_request.class_id, booking_request.client_email))
                    existing_count = cursor.fetchone()['count']
                    
                    if existing_count > 0:
                        logger.warning(f"User {booking_request.client_email} already has booking for class {booking_request.class_id}")
                        return None
                    
                    # Create booking
                    booking_time = datetime.utcnow().isoformat()
                    cursor.execute(Queries.INSERT_BOOKING, (
                        booking_request.class_id,
                        booking_request.client_name,
                        booking_request.client_email,
                        booking_time
                    ))
                    
                    booking_id = cursor.lastrowid
                    
                    # Update available slots
                    cursor.execute(Queries.UPDATE_CLASS_SLOTS, (booking_request.class_id,))
                    
                    if cursor.rowcount == 0:
                        logger.warning(f"Could not update slots for class {booking_request.class_id}")
                        conn.rollback()
                        return None
                    
                    # Commit transaction
                    conn.commit()
                    
                    booking = Booking(
                        id=booking_id,
                        class_id=booking_request.class_id,
                        client_name=booking_request.client_name,
                        client_email=booking_request.client_email,
                        booking_time=booking_time,
                        status="confirmed"
                    )
                    
                    logger.info(f"Created booking {booking_id} for class {booking_request.class_id}")
                    return booking
                    
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error in booking transaction: {e}")
                    raise
                    
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            raise
    
    def get_bookings_by_email(self, email: str) -> List[Dict[str, Any]]:
        """Get all bookings for a specific email."""
        try:
            with self.db_context as conn:
                cursor = conn.cursor()
                cursor.execute(Queries.GET_BOOKINGS_BY_EMAIL, (email,))
                rows = cursor.fetchall()
                
                bookings = []
                for row in rows:
                    booking_data = {
                        'id': row['id'],
                        'class_id': row['class_id'],
                        'client_name': row['client_name'],
                        'client_email': row['client_email'],
                        'booking_time': row['booking_time'],
                        'status': row['status'],
                        'class_name': row['class_name'],
                        'instructor': row['instructor'],
                        'datetime_utc': row['datetime_utc'],
                        'timezone': row['timezone']
                    }
                    bookings.append(booking_data)
                
                logger.info(f"Retrieved {len(bookings)} bookings for {email}")
                return bookings
                
        except Exception as e:
            logger.error(f"Error retrieving bookings for {email}: {e}")
            raise
    
    def check_existing_booking(self, class_id: int, email: str) -> bool:
        """Check if user already has a booking for this class."""
        try:
            with self.db_context as conn:
                cursor = conn.cursor()
                cursor.execute(Queries.CHECK_EXISTING_BOOKING, (class_id, email))
                count = cursor.fetchone()['count']
                return count > 0
                
        except Exception as e:
            logger.error(f"Error checking existing booking: {e}")
            raise
    
    def update_class_slots(self, class_id: int) -> bool:
        """Reduce available slots for a class."""
        try:
            with self.db_context as conn:
                cursor = conn.cursor()
                cursor.execute(Queries.UPDATE_CLASS_SLOTS, (class_id,))
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error updating class slots: {e}")
            raise
