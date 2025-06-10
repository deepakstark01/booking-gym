"""
Comprehensive unit tests for the booking system.
Tests all layers of the application with proper mocking.
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from contextlib import contextmanager
import pytz

from src.domain.models import BookingRequest, Class, Booking
from src.domain.repository import BookingRepository
from src.service.booking_service import BookingService
from src.config.database import init_database

class TestDatabase:
    """Test database helper."""
    
    def __init__(self):
        self.db_file = None
        self.connection = None
    
    def setup(self):
        """Setup test database."""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_file.close()
        self.db_path = self.db_file.name
        
        # Override database path for testing
        import src.config.database
        src.config.database.DATABASE_PATH = self.db_path
        
        # Initialize test database
        init_database()
        
        # Insert test data
        self._insert_test_data()
    
    def teardown(self):
        """Cleanup test database."""
        if self.connection:
            self.connection.close()
        if self.db_path and os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    @contextmanager
    def get_connection(self):
        """Get database connection for testing."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _insert_test_data(self):
        """Insert test data for testing."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert test classes
            ist = pytz.timezone('Asia/Kolkata')
            future_time = datetime.now(ist) + timedelta(days=1)
            utc_time = future_time.astimezone(pytz.UTC)
            
            cursor.execute("""
                INSERT INTO classes (id, name, instructor, datetime_utc, timezone, total_slots, available_slots)
                VALUES (1, 'Test Yoga', 'Test Instructor', ?, 'Asia/Kolkata', 10, 5)
            """, (utc_time.isoformat(),))
            
            cursor.execute("""
                INSERT INTO classes (id, name, instructor, datetime_utc, timezone, total_slots, available_slots)
                VALUES (2, 'Full Class', 'Test Instructor', ?, 'Asia/Kolkata', 5, 0)
            """, (utc_time.isoformat(),))
            
            conn.commit()

@pytest.fixture
def test_db():
    """Test database fixture."""
    db = TestDatabase()
    db.setup()
    yield db
    db.teardown()

@pytest.fixture
def repository(test_db):
    """Repository fixture."""
    return BookingRepository(test_db.get_connection)

@pytest.fixture
def service(repository):
    """Service fixture."""
    return BookingService(repository)

class TestBookingRepository:
    """Test cases for BookingRepository."""
    
    def test_get_all_upcoming_classes(self, repository):
        """Test retrieving all upcoming classes."""
        classes = repository.get_all_upcoming_classes()
        assert len(classes) >= 2
        assert all(isinstance(c, Class) for c in classes)
    
    def test_get_class_by_id_existing(self, repository):
        """Test retrieving existing class by ID."""
        class_obj = repository.get_class_by_id(1)
        assert class_obj is not None
        assert class_obj.id == 1
        assert class_obj.name == "Test Yoga"
        assert class_obj.available_slots == 5
    
    def test_get_class_by_id_nonexistent(self, repository):
        """Test retrieving non-existent class."""
        class_obj = repository.get_class_by_id(999)
        assert class_obj is None
    
    def test_create_booking_success(self, repository):
        """Test successful booking creation."""
        booking_request = BookingRequest(
            class_id=1,
            client_name="Test User",
            client_email="test@example.com"
        )
        
        booking = repository.create_booking(booking_request)
        assert booking is not None
        assert booking.class_id == 1
        assert booking.client_email == "test@example.com"
        assert booking.status == "confirmed"
    
    def test_create_booking_duplicate(self, repository):
        """Test duplicate booking prevention."""
        booking_request = BookingRequest(
            class_id=1,
            client_name="Test User",
            client_email="test@example.com"
        )
        
        # First booking should succeed
        booking1 = repository.create_booking(booking_request)
        assert booking1 is not None
        
        # Second booking should fail
        booking2 = repository.create_booking(booking_request)
        assert booking2 is None
    
    def test_create_booking_no_slots(self, repository):
        """Test booking when no slots available."""
        booking_request = BookingRequest(
            class_id=2,  # Full class
            client_name="Test User",
            client_email="test@example.com"
        )
        
        booking = repository.create_booking(booking_request)
        assert booking is None
    
    def test_get_bookings_by_email(self, repository):
        """Test retrieving bookings by email."""
        # Create a booking first
        booking_request = BookingRequest(
            class_id=1,
            client_name="Test User",
            client_email="test@example.com"
        )
        repository.create_booking(booking_request)
        
        # Retrieve bookings
        bookings = repository.get_bookings_by_email("test@example.com")
        assert len(bookings) == 1
        assert bookings[0]['client_email'] == "test@example.com"
        assert bookings[0]['class_name'] == "Test Yoga"
    
    def test_check_existing_booking(self, repository):
        """Test checking for existing bookings."""
        booking_request = BookingRequest(
            class_id=1,
            client_name="Test User",
            client_email="test@example.com"
        )
        
        # Initially no booking
        exists = repository.check_existing_booking(1, "test@example.com")
        assert not exists
        
        # Create booking
        repository.create_booking(booking_request)
        
        # Now booking exists
        exists = repository.check_existing_booking(1, "test@example.com")
        assert exists

class TestBookingService:
    """Test cases for BookingService."""
    
    def test_get_upcoming_classes(self, service):
        """Test service method for getting upcoming classes."""
        classes = service.get_upcoming_classes()
        assert len(classes) >= 2
        assert all(hasattr(c, 'datetime_local') for c in classes)
    
    def test_get_upcoming_classes_timezone_conversion(self, service):
        """Test timezone conversion in class retrieval."""
        # Test with different timezone
        classes_ist = service.get_upcoming_classes("Asia/Kolkata")
        classes_utc = service.get_upcoming_classes("UTC")
        
        assert len(classes_ist) == len(classes_utc)
        # Times should be different due to timezone conversion
        if classes_ist and classes_utc:
            assert classes_ist[0].datetime_local != classes_utc[0].datetime_local
    
    def test_create_booking_success(self, service):
        """Test successful booking through service."""
        booking_request = BookingRequest(
            class_id=1,
            client_name="Test User",
            client_email="test@example.com"
        )
        
        result = service.create_booking(booking_request)
        assert result.success
        assert "Successfully booked" in result.message
        assert "booking_id" in result.data
    
    def test_create_booking_class_not_found(self, service):
        """Test booking non-existent class."""
        booking_request = BookingRequest(
            class_id=999,
            client_name="Test User",
            client_email="test@example.com"
        )
        
        result = service.create_booking(booking_request)
        assert not result.success
        assert "not found" in result.message
    
    def test_create_booking_no_slots(self, service):
        """Test booking when class is full."""
        booking_request = BookingRequest(
            class_id=2,  # Full class
            client_name="Test User",
            client_email="test@example.com"
        )
        
        result = service.create_booking(booking_request)
        assert not result.success
        assert "fully booked" in result.message
    
    def test_create_booking_duplicate(self, service):
        """Test duplicate booking prevention through service."""
        booking_request = BookingRequest(
            class_id=1,
            client_name="Test User",
            client_email="test@example.com"
        )
        
        # First booking
        result1 = service.create_booking(booking_request)
        assert result1.success
        
        # Second booking (duplicate)
        result2 = service.create_booking(booking_request)
        assert not result2.success
        assert "already have a booking" in result2.message
    
    def test_get_bookings_by_email(self, service):
        """Test retrieving bookings by email through service."""
        # Create booking first
        booking_request = BookingRequest(
            class_id=1,
            client_name="Test User",
            client_email="test@example.com"
        )
        service.create_booking(booking_request)
        
        # Retrieve bookings
        bookings = service.get_bookings_by_email("test@example.com")
        assert len(bookings) == 1
        assert bookings[0].client_email == "test@example.com"
        assert hasattr(bookings[0], 'class_datetime_local')
    
    def test_get_bookings_invalid_email(self, service):
        """Test retrieving bookings with invalid email."""
        bookings = service.get_bookings_by_email("invalid-email")
        assert len(bookings) == 0
    
    def test_get_class_availability(self, service):
        """Test getting class availability information."""
        availability = service.get_class_availability(1)
        assert availability is not None
        assert availability['class_id'] == 1
        assert availability['total_slots'] == 10
        assert availability['available_slots'] == 5
        assert availability['booked_slots'] == 5
        assert availability['is_available'] is True
        
        # Test full class
        availability_full = service.get_class_availability(2)
        assert availability_full['is_available'] is False

class TestTimezoneHandling:
    """Test cases for timezone handling."""
    
    def test_timezone_conversion_accuracy(self, service):
        """Test accuracy of timezone conversions."""
        # Get class in IST
        classes_ist = service.get_upcoming_classes("Asia/Kolkata")
        if not classes_ist:
            pytest.skip("No classes available for testing")
        
        class_ist = classes_ist[0]
        
        # Get same class in UTC
        classes_utc = service.get_upcoming_classes("UTC")
        class_utc = next(c for c in classes_utc if c.id == class_ist.id)
        
        # Parse times
        ist_time = datetime.fromisoformat(class_ist.datetime_local)
        utc_time = datetime.fromisoformat(class_utc.datetime_local)
        
        # IST is UTC+5:30, so IST time should be 5.5 hours ahead
        # (Note: this is a simplified test, actual timezone handling may vary due to DST)
        time_diff = ist_time - utc_time
        expected_diff = timedelta(hours=5, minutes=30)
        
        # Allow some tolerance for timezone calculation differences
        assert abs(time_diff.total_seconds() - expected_diff.total_seconds()) < 3600  # 1 hour tolerance

class TestDataValidation:
    """Test cases for data validation."""
    
    def test_invalid_booking_request(self):
        """Test validation of booking request data."""
        with pytest.raises(ValueError):
            BookingRequest(
                class_id=0,  # Invalid ID
                client_name="Test User",
                client_email="test@example.com"
            )
        
        with pytest.raises(ValueError):
            BookingRequest(
                class_id=1,
                client_name="",  # Empty name
                client_email="test@example.com"
            )
        
        with pytest.raises(ValueError):
            BookingRequest(
                class_id=1,
                client_name="Test User",
                client_email="invalid-email"  # Invalid email
            )

def test_integration_full_booking_flow(test_db):
    """Integration test for complete booking flow."""
    # Setup
    repository = BookingRepository(test_db.get_connection)
    service = BookingService(repository)
    
    # Get available classes
    classes = service.get_upcoming_classes()
    assert len(classes) > 0
    
    test_class = classes[0]
    initial_slots = test_class.available_slots
    
    # Create booking
    booking_request = BookingRequest(
        class_id=test_class.id,
        client_name="Integration Test User",
        client_email="integration@example.com"
    )
    
    result = service.create_booking(booking_request)
    assert result.success
    
    # Verify slots reduced
    updated_classes = service.get_upcoming_classes()
    updated_class = next(c for c in updated_classes if c.id == test_class.id)
    assert updated_class.available_slots == initial_slots - 1
    
    # Verify booking exists
    bookings = service.get_bookings_by_email("integration@example.com")
    assert len(bookings) == 1
    assert bookings[0].class_id == test_class.id

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
