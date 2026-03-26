"""
Clinically validated screening instruments for mental health triage.

Implements PHQ-A (Patient Health Questionnaire — Adolescent), GAD-7 (Generalized
Anxiety Disorder 7-item), and CRAFFT (substance use screening).  Scoring cutoffs
are aligned with published DSM-5 thresholds — do NOT modify them.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Any


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

LIKERT_4 = [
    {"value": 0, "label": "Not at all"},
    {"value": 1, "label": "Several days"},
    {"value": 2, "label": "More than half the days"},
    {"value": 3, "label": "Nearly every day"},
]

YES_NO = [
    {"value": 0, "label": "No"},
    {"value": 1, "label": "Yes"},
]

CARE_LEVELS = {
    "self_help":        "Self-help resources and psychoeducation",
    "peer_support":     "Peer support and guided exercises",
    "licensed_counselor": "Licensed counselor session recommended",
    "teletherapy":      "Teletherapy / clinical follow-up recommended",
    "crisis_line":      "Immediate crisis support — contact 988 / AASRA",
}

SEVERITY_BAND_MAP = {
    "minimal": "green",
    "mild": "yellow",
    "moderate": "orange",
    "moderately_severe": "red",
    "severe": "red",
    "positive": "orange",
    "negative": "green",
}


@dataclass
class ScoringResult:
    instrument: str
    raw_score: int
    max_score: int
    severity_label: str
    severity_band: str          # green / yellow / orange / red
    care_level: str             # key into CARE_LEVELS
    care_description: str       # human-readable recommendation
    interpretation: str         # one-liner explaining the score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instrument": self.instrument,
            "raw_score": self.raw_score,
            "max_score": self.max_score,
            "severity_label": self.severity_label,
            "severity_band": self.severity_band,
            "care_level": self.care_level,
            "care_description": self.care_description,
            "interpretation": self.interpretation,
        }


# ---------------------------------------------------------------------------
# PHQ-A  (Patient Health Questionnaire for Adolescents — 9 items)
# ---------------------------------------------------------------------------

class PHQ_A:
    """PHQ-A: 9-item depression screening scored 0-27."""

    NAME = "PHQ_A"
    FULL_NAME = "Patient Health Questionnaire for Adolescents"
    DESCRIPTION = "Screens for depression severity over the past two weeks."
    NUM_QUESTIONS = 9

    QUESTIONS: List[str] = [
        "Little interest or pleasure in doing things",
        "Feeling down, depressed, or hopeless",
        "Trouble falling or staying asleep, or sleeping too much",
        "Feeling tired or having little energy",
        "Poor appetite or overeating",
        "Feeling bad about yourself — or that you are a failure or have let yourself or your family down",
        "Trouble concentrating on things, such as reading or watching videos",
        "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual",
        "Thoughts that you would be better off dead, or of hurting yourself in some way",
    ]

    # DSM-5 aligned cutoffs
    CUTOFFS = [
        (0,  4,  "minimal",           "green",  "self_help"),
        (5,  9,  "mild",              "yellow", "peer_support"),
        (10, 14, "moderate",          "orange", "licensed_counselor"),
        (15, 19, "moderately_severe", "red",    "teletherapy"),
        (20, 27, "severe",            "red",    "crisis_line"),
    ]

    @classmethod
    def get_questions(cls) -> Dict[str, Any]:
        return {
            "instrument": cls.NAME,
            "full_name": cls.FULL_NAME,
            "description": cls.DESCRIPTION,
            "instructions": "Over the past 2 weeks, how often have you been bothered by any of the following problems?",
            "questions": [
                {"index": i, "text": q, "options": LIKERT_4}
                for i, q in enumerate(cls.QUESTIONS)
            ],
        }

    @classmethod
    def score(cls, answers: List[int]) -> ScoringResult:
        if len(answers) != cls.NUM_QUESTIONS:
            raise ValueError(f"PHQ-A requires exactly {cls.NUM_QUESTIONS} answers, got {len(answers)}")
        for i, a in enumerate(answers):
            if a not in (0, 1, 2, 3):
                raise ValueError(f"Answer at index {i} must be 0-3, got {a}")

        raw = sum(answers)
        for lo, hi, label, band, care in cls.CUTOFFS:
            if lo <= raw <= hi:
                return ScoringResult(
                    instrument=cls.NAME,
                    raw_score=raw,
                    max_score=27,
                    severity_label=label,
                    severity_band=band,
                    care_level=care,
                    care_description=CARE_LEVELS[care],
                    interpretation=f"PHQ-A score {raw}/27 indicates {label.replace('_', ' ')} depression severity.",
                )
        # Fallback (should not happen with valid input)
        return ScoringResult(
            instrument=cls.NAME, raw_score=raw, max_score=27,
            severity_label="unknown", severity_band="yellow",
            care_level="peer_support", care_description=CARE_LEVELS["peer_support"],
            interpretation=f"PHQ-A score {raw}/27.",
        )


# ---------------------------------------------------------------------------
# GAD-7  (Generalized Anxiety Disorder 7-item)
# ---------------------------------------------------------------------------

class GAD_7:
    """GAD-7: 7-item anxiety screening scored 0-21."""

    NAME = "GAD_7"
    FULL_NAME = "Generalized Anxiety Disorder 7-item Scale"
    DESCRIPTION = "Screens for anxiety severity over the past two weeks."
    NUM_QUESTIONS = 7

    QUESTIONS: List[str] = [
        "Feeling nervous, anxious, or on edge",
        "Not being able to stop or control worrying",
        "Worrying too much about different things",
        "Trouble relaxing",
        "Being so restless that it is hard to sit still",
        "Becoming easily annoyed or irritable",
        "Feeling afraid, as if something awful might happen",
    ]

    CUTOFFS = [
        (0,  4,  "minimal",  "green",  "self_help"),
        (5,  9,  "mild",     "yellow", "peer_support"),
        (10, 14, "moderate", "orange", "licensed_counselor"),
        (15, 21, "severe",   "red",    "teletherapy"),
    ]

    @classmethod
    def get_questions(cls) -> Dict[str, Any]:
        return {
            "instrument": cls.NAME,
            "full_name": cls.FULL_NAME,
            "description": cls.DESCRIPTION,
            "instructions": "Over the past 2 weeks, how often have you been bothered by the following problems?",
            "questions": [
                {"index": i, "text": q, "options": LIKERT_4}
                for i, q in enumerate(cls.QUESTIONS)
            ],
        }

    @classmethod
    def score(cls, answers: List[int]) -> ScoringResult:
        if len(answers) != cls.NUM_QUESTIONS:
            raise ValueError(f"GAD-7 requires exactly {cls.NUM_QUESTIONS} answers, got {len(answers)}")
        for i, a in enumerate(answers):
            if a not in (0, 1, 2, 3):
                raise ValueError(f"Answer at index {i} must be 0-3, got {a}")

        raw = sum(answers)
        for lo, hi, label, band, care in cls.CUTOFFS:
            if lo <= raw <= hi:
                return ScoringResult(
                    instrument=cls.NAME,
                    raw_score=raw,
                    max_score=21,
                    severity_label=label,
                    severity_band=band,
                    care_level=care,
                    care_description=CARE_LEVELS[care],
                    interpretation=f"GAD-7 score {raw}/21 indicates {label} anxiety severity.",
                )
        return ScoringResult(
            instrument=cls.NAME, raw_score=raw, max_score=21,
            severity_label="unknown", severity_band="yellow",
            care_level="peer_support", care_description=CARE_LEVELS["peer_support"],
            interpretation=f"GAD-7 score {raw}/21.",
        )


# ---------------------------------------------------------------------------
# CRAFFT  (Substance use screening — 6 items)
# ---------------------------------------------------------------------------

class CRAFFT:
    """CRAFFT 2.1: 6-item substance use risk screening scored 0-6."""

    NAME = "CRAFFT"
    FULL_NAME = "CRAFFT Substance Use Screening Tool"
    DESCRIPTION = "Screens for substance use risk in adolescents and young adults."
    NUM_QUESTIONS = 6

    QUESTIONS: List[str] = [
        "Have you ever ridden in a CAR driven by someone (including yourself) who was high or had been using alcohol or drugs?",
        "Do you ever use alcohol or drugs to RELAX, feel better about yourself, or fit in?",
        "Do you ever use alcohol or drugs while you are by yourself, or ALONE?",
        "Do you ever FORGET things you did while using alcohol or drugs?",
        "Do your FAMILY or FRIENDS ever tell you that you should cut down on your drinking or drug use?",
        "Have you ever gotten into TROUBLE while you were using alcohol or drugs?",
    ]

    CUTOFFS = [
        (0, 1, "negative", "green",  "self_help"),
        (2, 6, "positive", "orange", "licensed_counselor"),
    ]

    @classmethod
    def get_questions(cls) -> Dict[str, Any]:
        return {
            "instrument": cls.NAME,
            "full_name": cls.FULL_NAME,
            "description": cls.DESCRIPTION,
            "instructions": "Please answer Yes or No to each of the following questions.",
            "questions": [
                {"index": i, "text": q, "options": YES_NO}
                for i, q in enumerate(cls.QUESTIONS)
            ],
        }

    @classmethod
    def score(cls, answers: List[int]) -> ScoringResult:
        if len(answers) != cls.NUM_QUESTIONS:
            raise ValueError(f"CRAFFT requires exactly {cls.NUM_QUESTIONS} answers, got {len(answers)}")
        for i, a in enumerate(answers):
            if a not in (0, 1):
                raise ValueError(f"Answer at index {i} must be 0 or 1, got {a}")

        raw = sum(answers)
        for lo, hi, label, band, care in cls.CUTOFFS:
            if lo <= raw <= hi:
                return ScoringResult(
                    instrument=cls.NAME,
                    raw_score=raw,
                    max_score=6,
                    severity_label=label,
                    severity_band=band,
                    care_level=care,
                    care_description=CARE_LEVELS[care],
                    interpretation=(
                        f"CRAFFT score {raw}/6 — {'positive screen; further assessment recommended' if label == 'positive' else 'negative screen'}."
                    ),
                )
        return ScoringResult(
            instrument=cls.NAME, raw_score=raw, max_score=6,
            severity_label="unknown", severity_band="yellow",
            care_level="peer_support", care_description=CARE_LEVELS["peer_support"],
            interpretation=f"CRAFFT score {raw}/6.",
        )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

INSTRUMENTS = {
    "PHQ_A": PHQ_A,
    "GAD_7": GAD_7,
    "CRAFFT": CRAFFT,
}


def get_instrument(name: str):
    """Lookup instrument by name (case-insensitive, dashes/underscores accepted)."""
    key = name.upper().replace("-", "_")
    inst = INSTRUMENTS.get(key)
    if inst is None:
        raise ValueError(f"Unknown instrument '{name}'. Available: {list(INSTRUMENTS.keys())}")
    return inst


# ---------------------------------------------------------------------------
# Composite triage
# ---------------------------------------------------------------------------

_BAND_SEVERITY = {"green": 0, "yellow": 1, "orange": 2, "red": 3}
_CARE_SEVERITY = {
    "self_help": 0,
    "peer_support": 1,
    "licensed_counselor": 2,
    "teletherapy": 3,
    "crisis_line": 4,
}


def composite_triage(results: List[ScoringResult]) -> Dict[str, Any]:
    """
    Given scored results from multiple instruments, return the highest
    severity band, care level, and per-instrument breakdown.
    """
    if not results:
        raise ValueError("At least one scored result is required")

    worst_band = max(results, key=lambda r: _BAND_SEVERITY.get(r.severity_band, 0))
    worst_care = max(results, key=lambda r: _CARE_SEVERITY.get(r.care_level, 0))

    return {
        "overall_severity_band": worst_band.severity_band,
        "overall_severity_label": worst_band.severity_label,
        "overall_care_level": worst_care.care_level,
        "overall_care_description": worst_care.care_description,
        "instruments": [r.to_dict() for r in results],
    }
