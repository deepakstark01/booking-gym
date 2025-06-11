# test for BookingRepository
import pytest
import json
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_classes():
    with open("test/data/classes.json", encoding="utf-8") as f:
        return json.load(f)

def test_get_all_upcoming_classes(mock_classes):
    with patch("src.domain.repository.BookingRepository.get_all_upcoming_classes", return_value=mock_classes):
        from src.domain.repository import BookingRepository
        repo = BookingRepository(db_context=MagicMock())
        classes = repo.get_all_upcoming_classes()
        assert isinstance(classes, list)
        assert classes[0]["name"] == "Yoga"