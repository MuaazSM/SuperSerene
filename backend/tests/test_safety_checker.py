"""
Tests for the safety checker module.

Verifies keyword detection, risk scoring, recovery pattern handling,
and the dual-layer (keyword + LLM) classification logic.

Note: Uses mock to avoid importing heavy LLM dependencies (langchain).
"""

import sys
import pytest
from unittest.mock import MagicMock

# Mock heavy dependencies before importing safety_checker
_mock_modules = [
    "langchain_google_genai", "langchain_groq", "langchain_openai",
    "langchain_core", "langchain_core.messages", "langchain_core.prompts",
    "langchain_community", "langchain_community.document_loaders",
    "langchain_community.vectorstores", "langchain_community.chat_message_histories",
    "langchain_community.retrievers",
    "langchain_text_splitters", "langchain_core.chat_history",
    "langchain_core.runnables.history", "langchain_core.documents",
    "sentence_transformers",
]
for mod in _mock_modules:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

from core.safety_checker import (
    _keyword_risk,
    _compute_risk_score,
    _compute_risk_band,
    classify_risk,
    escalation_message,
    get_crisis_resources,
    SafetyChecker,
    SafetyResult,
)


# ── Keyword Risk Detection ────────────────────────────────────────────────

class TestKeywordRisk:
    def test_safe_text(self):
        result = _keyword_risk("I had a great day at school")
        assert result["flagged"] is False
        assert result["reasons"] == []

    def test_empty_text(self):
        result = _keyword_risk("")
        assert result["flagged"] is False

    def test_strong_intent_detected(self):
        result = _keyword_risk("I want to kill myself")
        assert result["flagged"] is True
        assert "strong_intent" in result["reasons"]

    def test_suicide_keyword(self):
        result = _keyword_risk("I've been thinking about suicide")
        assert result["flagged"] is True
        assert "strong_intent" in result["reasons"]

    def test_method_mention(self):
        result = _keyword_risk("I've been thinking about overdose")
        assert result["flagged"] is True
        assert "method_mention" in result["reasons"]

    def test_despair_detected(self):
        result = _keyword_risk("everything is hopeless and nothing matters")
        assert result["flagged"] is True
        assert "despair" in result["reasons"]

    def test_farewell_detected(self):
        result = _keyword_risk("this is my last message goodbye")
        assert result["flagged"] is True
        assert "farewell" in result["reasons"]

    def test_imminence_detected(self):
        result = _keyword_risk("I feel hopeless right now")
        assert result["flagged"] is True
        assert "imminence" in result["reasons"]

    # Recovery pattern tests
    def test_recovery_narrative_not_flagged(self):
        result = _keyword_risk("I used to feel hopeless but I'm doing better now")
        assert result.get("context") == "recovery_narrative"
        assert result["flagged"] is False

    def test_idiomatic_jump(self):
        result = _keyword_risk("My friend jumped to a conclusion about me")
        assert result.get("context") == "recovery_narrative"
        assert result["flagged"] is False

    def test_hanging_out(self):
        result = _keyword_risk("I was hanging out with friends yesterday")
        assert result.get("context") == "recovery_narrative"
        assert result["flagged"] is False

    def test_cutting_class(self):
        result = _keyword_risk("I've been cutting class too much lately")
        assert result.get("context") == "recovery_narrative"
        assert result["flagged"] is False

    def test_strong_intent_overrides_recovery(self):
        """Strong intent should NOT be downgraded by recovery patterns."""
        result = _keyword_risk("I want to kill myself right now")
        assert result["flagged"] is True
        assert "strong_intent" in result["reasons"]


# ── Risk Score & Band ─────────────────────────────────────────────────────

class TestRiskScoring:
    def test_safe_score(self):
        kw = {"flagged": False, "reasons": []}
        score = _compute_risk_score("SAFE", kw, "normal text")
        assert score < 30

    def test_escalate_score(self):
        kw = {"flagged": True, "reasons": ["strong_intent"]}
        score = _compute_risk_score("ESCALATE", kw, "I want to die")
        assert score >= 70

    def test_band_green(self):
        assert _compute_risk_band(10) == "green"
        assert _compute_risk_band(29) == "green"

    def test_band_yellow(self):
        assert _compute_risk_band(30) == "yellow"
        assert _compute_risk_band(60) == "yellow"

    def test_band_red(self):
        assert _compute_risk_band(61) == "red"
        assert _compute_risk_band(100) == "red"

    def test_score_capped_at_100(self):
        kw = {"flagged": True, "reasons": ["strong_intent", "method_mention", "imminence", "despair", "farewell", "intent_with_method", "despair_with_imminence"]}
        score = _compute_risk_score("ESCALATE", kw, "plan suicide right now")
        assert score <= 100


# ── Classify Risk (no LLM) ───────────────────────────────────────────────

class TestClassifyRisk:
    def test_safe_classification(self):
        result = classify_risk("I had a good day")
        assert result["label"] == "SAFE"
        assert result["risk_band"] == "green"
        assert result["risk_score"] < 30

    def test_escalate_classification(self):
        result = classify_risk("I want to kill myself tonight")
        assert result["label"] == "ESCALATE"
        assert result["risk_band"] == "red"
        assert result["risk_score"] >= 70

    def test_result_has_required_keys(self):
        result = classify_risk("test message")
        assert "label" in result
        assert "risk_score" in result
        assert "risk_band" in result
        assert "signals" in result
        assert "policy_message" in result

    def test_policy_message_present(self):
        result = classify_risk("I feel sad")
        assert len(result["policy_message"]) > 0


# ── Escalation Message ────────────────────────────────────────────────────

class TestEscalationMessage:
    def test_english_message(self):
        msg = escalation_message("en")
        assert "sorry" in msg.lower() or "safety" in msg.lower()

    def test_default_message(self):
        msg = escalation_message()
        assert len(msg) > 20

    def test_other_locale_fallback(self):
        msg = escalation_message("zz")
        assert len(msg) > 20


# ── Crisis Resources ─────────────────────────────────────────────────────

class TestGetCrisisResources:
    def test_us_resources(self):
        r = get_crisis_resources("US")
        assert r["name"] == "988 Suicide & Crisis Lifeline"
        assert r["phone"] == "988"

    def test_uk_resources(self):
        r = get_crisis_resources("UK")
        assert "Samaritans" in r["name"]

    def test_india_resources(self):
        r = get_crisis_resources("IN")
        assert "AASRA" in r["name"]

    def test_unknown_country_fallback(self):
        r = get_crisis_resources("ZZ")
        assert "website" in r


# ── SafetyChecker Class ──────────────────────────────────────────────────

class TestSafetyCheckerClass:
    def test_check_safe_text(self):
        checker = SafetyChecker(llm=None)
        result = checker.check_text("I'm having a good day")
        assert isinstance(result, SafetyResult)
        assert result.is_safe is True
        assert result.label == "SAFE"

    def test_check_unsafe_text(self):
        checker = SafetyChecker(llm=None)
        result = checker.check_text("I want to kill myself")
        assert result.is_safe is False
        assert result.label == "ESCALATE"
        assert result.risk_band == "red"
