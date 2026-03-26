"""
Tests for the guided meditation service.
"""

import pytest
from services.meditation_service import (
    MEDITATIONS,
    get_library,
    get_meditation,
    recommend_meditations,
)


class TestMeditationLibrary:
    def test_has_9_meditations(self):
        assert len(MEDITATIONS) == 9

    def test_three_per_duration(self):
        by_dur = {}
        for m in MEDITATIONS:
            d = m["duration_minutes"]
            by_dur.setdefault(d, []).append(m)
        assert len(by_dur[5]) == 3
        assert len(by_dur[10]) == 3
        assert len(by_dur[15]) == 3

    def test_all_have_required_fields(self):
        required = {"id", "title", "duration_minutes", "category", "description", "mood_tags", "steps"}
        for m in MEDITATIONS:
            for f in required:
                assert f in m, f"Missing {f} in {m['id']}"

    def test_all_have_steps(self):
        for m in MEDITATIONS:
            assert len(m["steps"]) >= 5, f"{m['id']} has too few steps"

    def test_steps_have_timestamps(self):
        for m in MEDITATIONS:
            for step in m["steps"]:
                assert "timestamp_seconds" in step
                assert "instruction_text" in step
                assert isinstance(step["timestamp_seconds"], int)

    def test_steps_sorted_by_timestamp(self):
        for m in MEDITATIONS:
            timestamps = [s["timestamp_seconds"] for s in m["steps"]]
            assert timestamps == sorted(timestamps), f"{m['id']} steps not sorted"

    def test_unique_ids(self):
        ids = [m["id"] for m in MEDITATIONS]
        assert len(ids) == len(set(ids))

    def test_mood_tags_not_empty(self):
        for m in MEDITATIONS:
            assert len(m["mood_tags"]) > 0, f"{m['id']} has no mood tags"


class TestGetLibrary:
    def test_returns_grouped(self):
        lib = get_library()
        assert "groups" in lib
        assert "5" in lib["groups"]
        assert "10" in lib["groups"]
        assert "15" in lib["groups"]

    def test_total_count(self):
        lib = get_library()
        assert lib["total"] == 9

    def test_steps_excluded_from_summary(self):
        lib = get_library()
        for group in lib["groups"].values():
            for m in group:
                assert "steps" not in m


class TestGetMeditation:
    def test_valid_id(self):
        m = get_meditation("quick_calm")
        assert m is not None
        assert m["title"] == "Quick Calm"
        assert "steps" in m

    def test_invalid_id(self):
        m = get_meditation("nonexistent")
        assert m is None

    def test_all_ids_retrievable(self):
        for m in MEDITATIONS:
            result = get_meditation(m["id"])
            assert result is not None
            assert result["id"] == m["id"]


class TestRecommendMeditations:
    def test_returns_list(self):
        # Without a real DB, this tests the fallback path
        result = recommend_meditations("fake_user_123")
        assert isinstance(result, list)
        assert len(result) <= 3

    def test_no_steps_in_recommendations(self):
        result = recommend_meditations("fake_user_123")
        for m in result:
            assert "steps" not in m

    def test_recommendations_have_required_fields(self):
        result = recommend_meditations("fake_user_123")
        for m in result:
            assert "id" in m
            assert "title" in m
            assert "duration_minutes" in m
            assert "mood_tags" in m
