import pytest
from datetime import datetime
from app.schemas import AnalysisResponse

def test_naive_datetime_serialization():
    # Simulate data retrieved from the DB which is naive but implicitly UTC
    naive_dt = datetime(2026, 9, 24, 12, 0, 0)
    
    response = AnalysisResponse(
        id="123",
        user_id="user1",
        created_at=naive_dt,
        disclaimer="Test"
    )
    
    # Assert that the validator added timezone info
    assert response.created_at.tzinfo is not None
    
    # Dump to JSON to ensure the string ends with Z (since it's UTC)
    json_str = response.model_dump_json()
    assert '"created_at":"2026-09-24T12:00:00Z"' in json_str

def test_aware_datetime_serialization():
    from datetime import timezone
    aware_dt = datetime(2026, 9, 24, 12, 0, 0, tzinfo=timezone.utc)
    
    response = AnalysisResponse(
        id="123",
        user_id="user1",
        created_at=aware_dt,
        disclaimer="Test"
    )
    
    json_str = response.model_dump_json()
    assert '"created_at":"2026-09-24T12:00:00Z"' in json_str
