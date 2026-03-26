"""
Tests for clinically validated screening instruments.

Verifies scoring logic, severity bands, and care level mapping
for PHQ-A, GAD-7, and CRAFFT.
"""

import pytest
from screening.instruments import (
    PHQ_A, GAD_7, CRAFFT,
    get_instrument, composite_triage,
    INSTRUMENTS, ScoringResult,
)


# ── PHQ-A Tests ───────────────────────────────────────────────────────────

class TestPHQA:
    def test_question_count(self):
        assert len(PHQ_A.QUESTIONS) == 9

    def test_get_questions_structure(self):
        q = PHQ_A.get_questions()
        assert q["instrument"] == "PHQ_A"
        assert len(q["questions"]) == 9
        assert all("text" in item and "options" in item for item in q["questions"])
        assert all(len(item["options"]) == 4 for item in q["questions"])

    def test_score_minimal(self):
        result = PHQ_A.score([0, 0, 0, 0, 0, 0, 0, 0, 0])
        assert result.raw_score == 0
        assert result.severity_band == "green"
        assert result.severity_label == "minimal"
        assert result.care_level == "self_help"

    def test_score_mild(self):
        result = PHQ_A.score([1, 1, 1, 1, 1, 0, 0, 0, 0])
        assert result.raw_score == 5
        assert result.severity_band == "yellow"
        assert result.severity_label == "mild"

    def test_score_moderate(self):
        result = PHQ_A.score([2, 2, 1, 1, 1, 1, 1, 1, 0])
        assert result.raw_score == 10
        assert result.severity_band == "orange"
        assert result.severity_label == "moderate"
        assert result.care_level == "licensed_counselor"

    def test_score_moderately_severe(self):
        result = PHQ_A.score([2, 2, 2, 2, 2, 2, 1, 1, 1])
        assert result.raw_score == 15
        assert result.severity_band == "red"
        assert result.severity_label == "moderately_severe"

    def test_score_severe(self):
        result = PHQ_A.score([3, 3, 3, 3, 3, 2, 2, 2, 2])
        assert result.raw_score == 23
        assert result.severity_band == "red"
        assert result.severity_label == "severe"
        assert result.care_level == "crisis_line"

    def test_score_max(self):
        result = PHQ_A.score([3, 3, 3, 3, 3, 3, 3, 3, 3])
        assert result.raw_score == 27
        assert result.severity_band == "red"

    def test_wrong_answer_count_raises(self):
        with pytest.raises(ValueError, match="exactly 9"):
            PHQ_A.score([1, 2, 3])

    def test_invalid_answer_value_raises(self):
        with pytest.raises(ValueError, match="must be 0-3"):
            PHQ_A.score([0, 0, 0, 0, 0, 0, 0, 0, 5])

    def test_boundary_4_is_minimal(self):
        result = PHQ_A.score([1, 1, 1, 1, 0, 0, 0, 0, 0])
        assert result.raw_score == 4
        assert result.severity_label == "minimal"

    def test_boundary_9_is_mild(self):
        result = PHQ_A.score([1, 1, 1, 1, 1, 1, 1, 1, 1])
        assert result.raw_score == 9
        assert result.severity_label == "mild"

    def test_to_dict(self):
        result = PHQ_A.score([0] * 9)
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["instrument"] == "PHQ_A"
        assert "raw_score" in d
        assert "severity_band" in d


# ── GAD-7 Tests ───────────────────────────────────────────────────────────

class TestGAD7:
    def test_question_count(self):
        assert len(GAD_7.QUESTIONS) == 7

    def test_score_minimal(self):
        result = GAD_7.score([0, 0, 0, 0, 0, 0, 0])
        assert result.severity_band == "green"
        assert result.severity_label == "minimal"

    def test_score_mild(self):
        result = GAD_7.score([1, 1, 1, 1, 1, 0, 0])
        assert result.raw_score == 5
        assert result.severity_band == "yellow"

    def test_score_moderate(self):
        result = GAD_7.score([2, 2, 2, 2, 1, 1, 0])
        assert result.raw_score == 10
        assert result.severity_band == "orange"

    def test_score_severe(self):
        result = GAD_7.score([3, 3, 3, 2, 2, 1, 1])
        assert result.raw_score == 15
        assert result.severity_band == "red"
        assert result.severity_label == "severe"

    def test_max_score(self):
        result = GAD_7.score([3] * 7)
        assert result.raw_score == 21
        assert result.severity_band == "red"

    def test_wrong_count_raises(self):
        with pytest.raises(ValueError):
            GAD_7.score([1, 2])

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            GAD_7.score([0, 0, 0, 0, 0, 0, 4])


# ── CRAFFT Tests ──────────────────────────────────────────────────────────

class TestCRAFFT:
    def test_question_count(self):
        assert len(CRAFFT.QUESTIONS) == 6

    def test_score_negative(self):
        result = CRAFFT.score([0, 0, 0, 0, 0, 0])
        assert result.raw_score == 0
        assert result.severity_label == "negative"
        assert result.severity_band == "green"

    def test_score_one_is_negative(self):
        result = CRAFFT.score([1, 0, 0, 0, 0, 0])
        assert result.raw_score == 1
        assert result.severity_label == "negative"

    def test_score_two_is_positive(self):
        result = CRAFFT.score([1, 1, 0, 0, 0, 0])
        assert result.raw_score == 2
        assert result.severity_label == "positive"
        assert result.severity_band == "orange"
        assert result.care_level == "licensed_counselor"

    def test_score_all_yes(self):
        result = CRAFFT.score([1, 1, 1, 1, 1, 1])
        assert result.raw_score == 6
        assert result.severity_label == "positive"

    def test_wrong_count_raises(self):
        with pytest.raises(ValueError):
            CRAFFT.score([1, 0])

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            CRAFFT.score([0, 0, 0, 0, 0, 2])

    def test_yes_no_options(self):
        q = CRAFFT.get_questions()
        for item in q["questions"]:
            assert len(item["options"]) == 2
            values = [o["value"] for o in item["options"]]
            assert 0 in values and 1 in values


# ── Registry & Composite Tests ────────────────────────────────────────────

class TestRegistry:
    def test_all_instruments_registered(self):
        assert "PHQ_A" in INSTRUMENTS
        assert "GAD_7" in INSTRUMENTS
        assert "CRAFFT" in INSTRUMENTS

    def test_get_instrument_case_insensitive(self):
        assert get_instrument("phq_a") == PHQ_A
        assert get_instrument("GAD-7") == GAD_7
        assert get_instrument("crafft") == CRAFFT

    def test_get_instrument_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown instrument"):
            get_instrument("INVALID")


class TestCompositeTriage:
    def test_composite_takes_worst_band(self):
        r1 = PHQ_A.score([0] * 9)      # green
        r2 = GAD_7.score([3] * 7)       # red
        r3 = CRAFFT.score([0] * 6)      # green
        result = composite_triage([r1, r2, r3])
        assert result["overall_severity_band"] == "red"

    def test_composite_takes_worst_care(self):
        r1 = PHQ_A.score([3, 3, 3, 3, 3, 3, 3, 3, 3])  # crisis_line
        r2 = GAD_7.score([0] * 7)                         # self_help
        result = composite_triage([r1, r2])
        assert result["overall_care_level"] == "crisis_line"

    def test_composite_single_instrument(self):
        r = PHQ_A.score([1, 1, 1, 1, 1, 0, 0, 0, 0])
        result = composite_triage([r])
        assert result["overall_severity_band"] == "yellow"
        assert len(result["instruments"]) == 1

    def test_composite_empty_raises(self):
        with pytest.raises(ValueError):
            composite_triage([])

    def test_composite_instruments_list(self):
        r1 = PHQ_A.score([0] * 9)
        r2 = GAD_7.score([0] * 7)
        result = composite_triage([r1, r2])
        assert len(result["instruments"]) == 2
        assert result["instruments"][0]["instrument"] == "PHQ_A"
        assert result["instruments"][1]["instrument"] == "GAD_7"
