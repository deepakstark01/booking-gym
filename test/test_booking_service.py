# test for BookingService
import pytest
from unittest.mock import MagicMock
from src.service.booking_service import BookingService, BookingResult
from src.domain.models import BookingRequest, Class

@pytest.fixture
def mock_repository():
    return MagicMock()

def test_create_booking_success(mock_repository):
    service = BookingService(mock_repository)
    booking_request = BookingRequest(class_id=1, client_name="Test", client_email="test@example.com")
    mock_class = Class(id=1, name="Yoga", instructor="Priya", datetime_utc="2025-06-11T08:00:00Z", timezone="Asia/Kolkata", total_slots=10, available_slots=5)
    mock_repository.get_class_by_id.return_value = mock_class
    mock_repository.check_existing_booking.return_value = False
    mock_repository.create_booking.return_value = MagicMock(id=42)
    result = service.create_booking(booking_request)
    assert isinstance(result, BookingResult)
    assert result.success is True