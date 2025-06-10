# test for BookingRequest model
from src.domain.models import BookingRequest
def test_booking_request_model():
    booking = BookingRequest(class_id=1, client_name="Test", client_email="test@example.com")
    assert booking.class_id == 1
    assert booking.client_name == "Test"
    assert booking.client_email == "test@example.com"