"""
Domain models and Pydantic schemas.
Defines the core business entities and data validation models.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator, Field
import pytz

class ClassBase(BaseModel):
    """Base class model."""
    name: str = Field(..., min_length=1, max_length=100, description="Class name")
    instructor: str = Field(..., min_length=1, max_length=100, description="Instructor name")
    datetime_utc: str = Field(..., description="Class datetime in UTC ISO format")
    timezone: str = Field(default="Asia/Kolkata", description="Original timezone")
    total_slots: int = Field(..., gt=0, le=100, description="Total available slots")
    available_slots: int = Field(..., ge=0, description="Currently available slots")

class Class(ClassBase):
    """Class model with ID."""
    id: int = Field(..., description="Unique class identifier")
    
    @validator('available_slots')
    def validate_available_slots(cls, v, values):
        """Validate that available slots don't exceed total slots."""
        if 'total_slots' in values and v > values['total_slots']:
            raise ValueError('Available slots cannot exceed total slots')
        return v

class ClassResponse(BaseModel):
    """Class response model with timezone conversion."""
    id: int
    name: str
    instructor: str
    datetime_local: str = Field(..., description="Class datetime in requested timezone")
    timezone: str
    total_slots: int
    available_slots: int
    
    @classmethod
    def from_class(cls, class_obj: Class, target_timezone: str = "Asia/Kolkata"):
        """Create response from Class object with timezone conversion."""
        # Parse UTC datetime
        utc_dt = datetime.fromisoformat(class_obj.datetime_utc.replace('Z', '+00:00'))
        utc_dt = utc_dt.replace(tzinfo=pytz.UTC)
        
        # Convert to target timezone
        target_tz = pytz.timezone(target_timezone)
        local_dt = utc_dt.astimezone(target_tz)
        
        return cls(
            id=class_obj.id,
            name=class_obj.name,
            instructor=class_obj.instructor,
            datetime_local=local_dt.isoformat(),
            timezone=target_timezone,
            total_slots=class_obj.total_slots,
            available_slots=class_obj.available_slots
        )

class BookingRequest(BaseModel):
    """Booking request model."""
    class_id: int = Field(..., gt=0, description="ID of the class to book")
    client_name: str = Field(..., min_length=1, max_length=100, description="Client name")
    client_email: EmailStr = Field(..., description="Client email address")
    
    @validator('client_name')
    def validate_client_name(cls, v):
        """Validate client name contains only allowed characters."""
        if not v.strip():
            raise ValueError('Client name cannot be empty')
        return v.strip()

class BookingBase(BaseModel):
    """Base booking model."""
    class_id: int
    client_name: str
    client_email: EmailStr
    booking_time: str
    status: str = "confirmed"

class Booking(BookingBase):
    """Booking model with ID."""
    id: int

class BookingResponse(BaseModel):
    """Booking response model with class details."""
    id: int
    class_id: int
    client_name: str
    client_email: EmailStr
    booking_time: str
    status: str
    class_name: str
    instructor: str
    class_datetime_local: str
    class_timezone: str
    
    @classmethod
    def from_booking_with_class(cls, booking_data: dict, target_timezone: str = "Asia/Kolkata"):
        """Create response from booking data with class information."""
        # Parse UTC datetime
        utc_dt = datetime.fromisoformat(booking_data['datetime_utc'].replace('Z', '+00:00'))
        utc_dt = utc_dt.replace(tzinfo=pytz.UTC)
        
        # Convert to target timezone
        target_tz = pytz.timezone(target_timezone)
        local_dt = utc_dt.astimezone(target_tz)
        
        return cls(
            id=booking_data['id'],
            class_id=booking_data['class_id'],
            client_name=booking_data['client_name'],
            client_email=booking_data['client_email'],
            booking_time=booking_data['booking_time'],
            status=booking_data['status'],
            class_name=booking_data['class_name'],
            instructor=booking_data['instructor'],
            class_datetime_local=local_dt.isoformat(),
            class_timezone=target_timezone
        )

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    error_code: Optional[str] = Field(None, description="Error code for client handling")

class SuccessResponse(BaseModel):
    """Success response model."""
    message: str = Field(..., description="Success message")
    data: Optional[dict] = Field(None, description="Additional response data")

# Query parameter models
class TimezoneQuery(BaseModel):
    """Timezone query parameter model."""
    timezone: str = Field(default="Asia/Kolkata", description="Target timezone for datetime conversion")
    
    @validator('timezone')
    def validate_timezone(cls, v):
        """Validate timezone string."""
        try:
            pytz.timezone(v)
            return v
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f'Unknown timezone: {v}')
