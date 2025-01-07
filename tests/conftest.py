import os
import tempfile

import pytest
from personal_mcp.database import Database
from personal_mcp.server import PersonalMCP


@pytest.fixture
def temp_db_path():
    """Create a temporary database file."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def db(temp_db_path):
    """Create a test database instance."""
    return Database(temp_db_path)


@pytest.fixture
def server(temp_db_path):
    """Create a test server instance."""
    return PersonalMCP(name="Test Server", db_path=temp_db_path)


@pytest.fixture
def sample_workout():
    """Create a sample workout data."""
    return {
        "date": "2024-01-07",
        "exercises": [
            {
                "name": "Bench Press",
                "sets": [{"weight": 135, "reps": 10, "rpe": 7, "notes": "Felt good"}],
            },
            {"name": "Squats", "sets": [{"weight": 185, "reps": 8, "rpe": 8, "notes": None}]},
        ],
        "perceived_effort": 8,
        "post_workout_feeling": "Strong",
        "notes": "Great session",
    }


@pytest.fixture
def sample_meal():
    """Create a sample meal data."""
    return {
        "meal_type": "lunch",
        "foods": [
            {"name": "Chicken Breast", "amount": 200, "unit": "g", "protein": 46, "calories": 330},
            {"name": "Brown Rice", "amount": 100, "unit": "g", "protein": 7, "calories": 111},
        ],
        "time": "12:30",
        "hunger_level": 7,
        "satisfaction_level": 8,
        "notes": "Good balanced meal",
    }


@pytest.fixture
def sample_journal_entry():
    """Create a sample journal entry data."""
    return {
        "entry_type": "daily",
        "content": "Had a productive day with good energy levels.",
        "mood": 8,
        "energy": 7,
        "sleep_quality": 8,
        "stress_level": 3,
        "tags": ["productive", "energetic"],
    }
