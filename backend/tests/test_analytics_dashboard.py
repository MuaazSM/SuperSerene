"""
Tests for the analytics dashboard service.

Tests the pure computation functions that don't require a database.
"""

import pytest
from services.analytics_dashboard import (
    _ema_series,
    PERIOD_DAYS,
)


class TestEMASeries:
    def test_empty(self):
        assert _ema_series([], 7) == []

    def test_single_value(self):
        result = _ema_series([50.0], 7)
        assert result == [50.0]

    def test_constant_series(self):
        result = _ema_series([60.0, 60.0, 60.0], 7)
        assert all(v == 60.0 for v in result)

    def test_length_matches_input(self):
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        result = _ema_series(values, 7)
        assert len(result) == len(values)

    def test_first_value_preserved(self):
        values = [42.0, 50.0, 60.0]
        result = _ema_series(values, 7)
        assert result[0] == 42.0

    def test_shorter_window_more_responsive(self):
        values = [10.0, 10.0, 10.0, 10.0, 90.0]
        ema3 = _ema_series(values, 3)
        ema14 = _ema_series(values, 14)
        # Shorter window reacts more to the spike
        assert ema3[-1] > ema14[-1]


class TestPeriodDays:
    def test_week(self):
        assert PERIOD_DAYS["week"] == 7

    def test_month(self):
        assert PERIOD_DAYS["month"] == 30

    def test_3months(self):
        assert PERIOD_DAYS["3months"] == 90
