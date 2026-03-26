"""
Tests for the multi-language crisis resource system.
"""

import pytest
from services.crisis_resources import (
    CRISIS_RESOURCES,
    SUPPORTED_LANGUAGES,
    LANGUAGE_NAMES,
    get_resources,
    get_all_grouped,
    get_nearest,
    detect_language,
    _detect_from_text,
)


class TestResourceDatabase:
    def test_has_resources(self):
        assert len(CRISIS_RESOURCES) >= 15

    def test_all_resources_have_required_fields(self):
        required = {"country", "country_code", "language", "hotline_name", "phone_number", "hours", "description"}
        for r in CRISIS_RESOURCES:
            for field in required:
                assert field in r, f"Missing {field} in {r.get('hotline_name', 'unknown')}"

    def test_supported_languages(self):
        assert "en" in SUPPORTED_LANGUAGES
        assert "hi" in SUPPORTED_LANGUAGES
        assert "es" in SUPPORTED_LANGUAGES
        assert "fr" in SUPPORTED_LANGUAGES

    def test_english_resources_exist(self):
        en = [r for r in CRISIS_RESOURCES if r["language"] == "en"]
        assert len(en) >= 5

    def test_hindi_resources_exist(self):
        hi = [r for r in CRISIS_RESOURCES if r["language"] == "hi"]
        assert len(hi) >= 3

    def test_spanish_resources_exist(self):
        es = [r for r in CRISIS_RESOURCES if r["language"] == "es"]
        assert len(es) >= 3

    def test_french_resources_exist(self):
        fr = [r for r in CRISIS_RESOURCES if r["language"] == "fr"]
        assert len(fr) >= 3

    def test_988_lifeline_present(self):
        us_en = [r for r in CRISIS_RESOURCES if r["country_code"] == "US" and r["language"] == "en"]
        names = [r["hotline_name"] for r in us_en]
        assert any("988" in n for n in names)

    def test_aasra_present(self):
        india = [r for r in CRISIS_RESOURCES if r["country_code"] == "IN"]
        names = [r["hotline_name"] for r in india]
        assert any("AASRA" in n for n in names)

    def test_samaritans_present(self):
        uk = [r for r in CRISIS_RESOURCES if r["country_code"] == "GB"]
        names = [r["hotline_name"] for r in uk]
        assert any("Samaritans" in n for n in names)


class TestGetResources:
    def test_filter_by_language(self):
        result = get_resources(lang="en")
        assert all(r["language"] == "en" for r in result)

    def test_filter_by_country(self):
        result = get_resources(country_code="IN")
        assert all(r["country_code"] == "IN" for r in result)

    def test_filter_by_both(self):
        result = get_resources(lang="en", country_code="US")
        assert all(r["language"] == "en" and r["country_code"] == "US" for r in result)

    def test_no_filter_returns_all(self):
        result = get_resources()
        assert len(result) == len(CRISIS_RESOURCES)

    def test_unknown_language_returns_empty(self):
        result = get_resources(lang="zz")
        assert result == []


class TestGetAllGrouped:
    def test_returns_dict(self):
        grouped = get_all_grouped()
        assert isinstance(grouped, dict)

    def test_has_all_languages(self):
        grouped = get_all_grouped()
        for lang in SUPPORTED_LANGUAGES:
            assert lang in grouped

    def test_counts_match(self):
        grouped = get_all_grouped()
        total = sum(len(v) for v in grouped.values())
        assert total == len(CRISIS_RESOURCES)


class TestGetNearest:
    def test_english_match(self):
        result = get_nearest("en")
        assert result["language"] == "en"
        assert result["fallback"] is False
        assert len(result["resources"]) > 0

    def test_hindi_match(self):
        result = get_nearest("hi")
        assert result["language"] == "hi"
        assert result["fallback"] is False

    def test_unsupported_falls_back_to_english(self):
        result = get_nearest("ja")
        assert result["language"] == "en"
        assert result["fallback"] is True
        assert "note" in result

    def test_fallback_note_mentions_language(self):
        result = get_nearest("ko")
        assert "ko" in result.get("note", "")


class TestLanguageDetection:
    def test_default_is_english(self):
        assert detect_language("") == "en"
        assert detect_language("hello") == "en"

    def test_hindi_romanized(self):
        result = _detect_from_text("mujhe bahut tension hai kya karu")
        assert result == "hi"

    def test_spanish_text(self):
        result = _detect_from_text("estoy muy triste y necesito ayuda")
        assert result == "es"

    def test_french_text(self):
        result = _detect_from_text("je suis triste et j'ai besoin d'aide")
        assert result == "fr"

    def test_english_text_no_detection(self):
        result = _detect_from_text("I feel sad today")
        # English text may return None from keyword heuristics (no Hindi/Spanish/French markers)
        assert result is None or result == "en"

    def test_short_text_returns_none(self):
        result = _detect_from_text("hi")
        assert result is None
