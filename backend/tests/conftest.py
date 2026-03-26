"""
Shared test fixtures for the SuperSerene backend test suite.
"""

import os
import sys
import pytest

# Ensure the backend directory is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_phq_answers():
    """Valid PHQ-A answers (9 items, 0-3 each)."""
    return [2, 1, 3, 2, 0, 1, 2, 1, 0]


@pytest.fixture
def sample_gad_answers():
    """Valid GAD-7 answers (7 items, 0-3 each)."""
    return [3, 2, 2, 1, 1, 2, 3]


@pytest.fixture
def sample_crafft_answers():
    """Valid CRAFFT answers (6 items, 0/1 each)."""
    return [1, 1, 0, 1, 0, 0]


@pytest.fixture
def sample_checkin_payload():
    """Sample daily check-in payload."""
    return {
        "user_id": "test_user_001",
        "mood": 3,
        "stress": 4,
        "energy": 2,
        "connection": 3,
        "motivation": 2,
    }


@pytest.fixture
def sample_user_id():
    return "test_user_001"
