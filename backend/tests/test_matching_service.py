"""
Tests for the teletherapy matching service — scoring and ranking logic.
"""

import pytest
from services.matching_service import (
    _score_provider,
    _today_and_next,
    _next_slot_text,
)


class TestScoreProvider:
    """Test the provider scoring algorithm weights."""

    def _make_provider(self, **overrides):
        base = {
            "specialties": ["anxiety", "depression"],
            "availability_slots": [
                {"day": "monday", "start_time": "10:00", "end_time": "11:00", "timezone": "UTC"},
            ],
            "languages": ["English"],
            "rating": 4.0,
        }
        base.update(overrides)
        return base

    def test_perfect_match(self):
        provider = self._make_provider(
            specialties=["anxiety", "depression"],
            languages=["English"],
            rating=5.0,
        )
        score = _score_provider(
            provider,
            concerns=["anxiety", "depression"],
            upcoming_days=["monday"],
            user_lang="English",
        )
        # All components should be high
        assert score > 0.8

    def test_no_specialty_match(self):
        provider = self._make_provider(specialties=["substance_use", "trauma"])
        score = _score_provider(
            provider,
            concerns=["anxiety"],
            upcoming_days=["monday"],
            user_lang="English",
        )
        # Specialty component is 0, but availability + language + rating still contribute
        assert score < 0.7

    def test_no_availability_match(self):
        provider = self._make_provider(
            availability_slots=[{"day": "friday", "start_time": "10:00", "end_time": "11:00", "timezone": "UTC"}]
        )
        score = _score_provider(
            provider,
            concerns=["anxiety"],
            upcoming_days=["monday", "tuesday", "wednesday"],
            user_lang="English",
        )
        # Availability component is 0
        assert score < 0.7

    def test_language_mismatch(self):
        provider = self._make_provider(languages=["Hindi"])
        score_matched = _score_provider(
            provider,
            concerns=["anxiety"],
            upcoming_days=["monday"],
            user_lang="Hindi",
        )
        score_mismatched = _score_provider(
            provider,
            concerns=["anxiety"],
            upcoming_days=["monday"],
            user_lang="English",
        )
        # Language match adds 0.2
        assert score_matched > score_mismatched

    def test_higher_rating_scores_better(self):
        high = self._make_provider(rating=5.0)
        low = self._make_provider(rating=2.0)
        score_high = _score_provider(high, ["anxiety"], ["monday"], "English")
        score_low = _score_provider(low, ["anxiety"], ["monday"], "English")
        assert score_high > score_low

    def test_empty_specialties(self):
        provider = self._make_provider(specialties=[])
        score = _score_provider(provider, ["anxiety"], ["monday"], "English")
        assert 0 <= score <= 1

    def test_empty_concerns(self):
        provider = self._make_provider()
        score = _score_provider(provider, [], ["monday"], "English")
        assert 0 <= score <= 1

    def test_score_bounded_0_1(self):
        provider = self._make_provider()
        score = _score_provider(provider, ["anxiety"], ["monday"], "English")
        assert 0 <= score <= 1


class TestTodayAndNext:
    def test_returns_correct_count(self):
        days = _today_and_next(2)
        assert len(days) == 3  # today + 2

    def test_returns_lowercase_day_names(self):
        days = _today_and_next(2)
        valid = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
        for d in days:
            assert d in valid


class TestNextSlotText:
    def test_matching_day(self):
        slots = [{"day": "monday", "start_time": "10:00", "end_time": "11:00", "timezone": "UTC"}]
        result = _next_slot_text(slots, ["monday", "tuesday"])
        assert "Monday" in result
        assert "10:00" in result

    def test_no_matching_day_falls_back(self):
        slots = [{"day": "friday", "start_time": "14:00", "end_time": "15:00", "timezone": "UTC"}]
        result = _next_slot_text(slots, ["monday", "tuesday"])
        assert "Friday" in result

    def test_empty_slots(self):
        result = _next_slot_text([], ["monday"])
        assert "Contact" in result
