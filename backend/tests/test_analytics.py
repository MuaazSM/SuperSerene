"""
Tests for core analytics functions.

Verifies mood index computation, EMA, z-score, trend detection,
and check-in scoring.
"""

import pytest
import math
from core.analytics import (
    score_checkin,
    compute_mood_index,
    ema,
    zscore,
    flag_from_trend,
    compute_series_stats,
)


class TestScoreCheckin:
    def test_neutral_checkin(self):
        payload = {"mood": 3, "stress": 3, "energy": 3, "connection": 3, "motivation": 3}
        result = score_checkin(payload)
        assert "mood_index" in result
        assert 0 <= result["mood_index"] <= 100

    def test_best_case(self):
        payload = {"mood": 5, "stress": 1, "energy": 5, "connection": 5, "motivation": 5}
        result = score_checkin(payload)
        assert result["mood_index"] == 100.0

    def test_worst_case(self):
        payload = {"mood": 1, "stress": 5, "energy": 1, "connection": 1, "motivation": 1}
        result = score_checkin(payload)
        assert result["mood_index"] == 0.0

    def test_missing_fields_default(self):
        payload = {"mood": 4}
        result = score_checkin(payload)
        assert "mood_index" in result
        assert 0 <= result["mood_index"] <= 100

    def test_preserves_original_payload(self):
        payload = {"mood": 3, "stress": 2, "energy": 4, "connection": 3, "motivation": 3, "user_id": "abc"}
        result = score_checkin(payload)
        assert result["user_id"] == "abc"

    def test_stress_is_inverted(self):
        """Higher stress should lower the mood index."""
        low_stress = score_checkin({"mood": 3, "stress": 1, "energy": 3, "connection": 3, "motivation": 3})
        high_stress = score_checkin({"mood": 3, "stress": 5, "energy": 3, "connection": 3, "motivation": 3})
        assert low_stress["mood_index"] > high_stress["mood_index"]


class TestComputeMoodIndex:
    def test_returns_float(self):
        result = compute_mood_index({"mood": 3, "stress": 3, "energy": 3, "connection": 3, "motivation": 3})
        assert isinstance(result, float)


class TestEMA:
    def test_empty_series(self):
        assert ema([], 7) == 0.0

    def test_single_value(self):
        assert ema([50.0], 7) == 50.0

    def test_constant_series(self):
        result = ema([50.0, 50.0, 50.0, 50.0, 50.0], 7)
        assert result == 50.0

    def test_increasing_series(self):
        series = [10.0, 20.0, 30.0, 40.0, 50.0]
        result = ema(series, 3)
        assert result > 30.0  # EMA with recent weighting

    def test_k_parameter_affects_smoothing(self):
        series = [10.0, 50.0, 10.0, 50.0, 10.0]
        ema3 = ema(series, 3)
        ema14 = ema(series, 14)
        # Shorter window = more responsive to recent values
        assert ema3 != ema14


class TestZScore:
    def test_insufficient_data(self):
        assert zscore([]) == 0.0
        assert zscore([50.0]) == 0.0

    def test_constant_series_zero_std(self):
        assert zscore([50.0, 50.0, 50.0]) == 0.0

    def test_positive_zscore(self):
        series = [50.0, 50.0, 50.0, 50.0, 80.0]
        z = zscore(series)
        assert z > 0

    def test_negative_zscore(self):
        series = [50.0, 50.0, 50.0, 50.0, 20.0]
        z = zscore(series)
        assert z < 0


class TestFlagFromTrend:
    def test_insufficient_data(self):
        assert flag_from_trend([]) == "SAFE"
        assert flag_from_trend([50.0]) == "SAFE"
        assert flag_from_trend([50.0, 50.0]) == "SAFE"

    def test_stable_series(self):
        assert flag_from_trend([50.0, 51.0, 49.0, 50.0, 50.0]) == "SAFE"

    def test_declining_series(self):
        series = [80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 10.0]
        assert flag_from_trend(series) == "WATCH"


class TestComputeSeriesStats:
    def test_empty_series(self):
        stats = compute_series_stats([])
        assert stats["ema7"] == 0.0
        assert stats["flag"] == "SAFE"

    def test_full_series(self):
        stats = compute_series_stats([50.0, 55.0, 60.0, 45.0, 50.0, 55.0, 60.0])
        assert "ema7" in stats
        assert "ema14" in stats
        assert "zscore" in stats
        assert stats["flag"] in ("SAFE", "WATCH")
