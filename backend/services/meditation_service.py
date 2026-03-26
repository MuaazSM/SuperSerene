"""
Guided meditation service.

Provides a curated library of 9 meditation sessions (3 per duration tier),
mood-based recommendations, and completion tracking with pre/post mood deltas.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from db.mongo import get_mongo
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)


# ---------------------------------------------------------------------------
# Meditation library
# ---------------------------------------------------------------------------

MEDITATIONS: List[Dict[str, Any]] = [
    # ── 5-minute sessions ─────────────────────────────────────────────────
    {
        "id": "quick_calm",
        "title": "Quick Calm",
        "duration_minutes": 5,
        "category": "Anxiety Relief",
        "description": "A rapid grounding technique to ease anxiety and bring you back to the present moment.",
        "mood_tags": ["anxious", "stressed", "overwhelmed"],
        "steps": [
            {"timestamp_seconds": 0, "instruction_text": "Find a comfortable position. Close your eyes or soften your gaze.", "breath_pattern": None},
            {"timestamp_seconds": 15, "instruction_text": "Take a deep breath in through your nose... and slowly out through your mouth.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 35, "instruction_text": "Notice five things you can see. Four you can touch. Three you can hear.", "breath_pattern": None},
            {"timestamp_seconds": 70, "instruction_text": "Let your breathing find its natural rhythm. You are safe in this moment.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 120, "instruction_text": "With each exhale, release one worry. Let it dissolve like mist.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 180, "instruction_text": "Place your hand on your chest. Feel the steady beat. You are grounded.", "breath_pattern": None},
            {"timestamp_seconds": 230, "instruction_text": "Slowly bring awareness back to the room. Wiggle your fingers and toes.", "breath_pattern": None},
            {"timestamp_seconds": 270, "instruction_text": "When you're ready, gently open your eyes. Carry this calm with you.", "breath_pattern": None},
        ],
    },
    {
        "id": "morning_reset",
        "title": "Morning Reset",
        "duration_minutes": 5,
        "category": "Energy Boost",
        "description": "Start your day with intention and gentle energy through focused breathing.",
        "mood_tags": ["tired", "unfocused", "low"],
        "steps": [
            {"timestamp_seconds": 0, "instruction_text": "Sit up tall. Roll your shoulders back. Feel your spine lengthen.", "breath_pattern": None},
            {"timestamp_seconds": 15, "instruction_text": "Breathe in energy and light... breathe out stagnation and sleep.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 50, "instruction_text": "Set an intention for today. One word that captures what you need.", "breath_pattern": None},
            {"timestamp_seconds": 90, "instruction_text": "Energising breath: quick inhale through the nose, strong exhale through the mouth.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 140, "instruction_text": "Visualise your day unfolding with clarity and purpose.", "breath_pattern": None},
            {"timestamp_seconds": 200, "instruction_text": "Smile gently. Feel gratitude for this new day.", "breath_pattern": None},
            {"timestamp_seconds": 250, "instruction_text": "Take three final deep breaths. On the last one, open your eyes.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 285, "instruction_text": "You're ready. Go gently, go boldly.", "breath_pattern": None},
        ],
    },
    {
        "id": "stress_release",
        "title": "Stress Release",
        "duration_minutes": 5,
        "category": "Work/School Stress",
        "description": "Decompress after a demanding day with progressive tension release.",
        "mood_tags": ["stressed", "angry", "overwhelmed", "frustrated"],
        "steps": [
            {"timestamp_seconds": 0, "instruction_text": "Close your eyes. Let the weight of the day begin to lift.", "breath_pattern": None},
            {"timestamp_seconds": 15, "instruction_text": "Tense your shoulders up to your ears. Hold... and release.", "breath_pattern": None},
            {"timestamp_seconds": 40, "instruction_text": "Clench your fists tight. Hold for five seconds... and let go.", "breath_pattern": None},
            {"timestamp_seconds": 65, "instruction_text": "Scrunch your face tight. Hold... and relax every muscle.", "breath_pattern": None},
            {"timestamp_seconds": 90, "instruction_text": "Slow breath in... imagine collecting all your stress into a ball.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 140, "instruction_text": "Breathe out... and watch that ball float away from you.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 200, "instruction_text": "Your body is lighter now. Rest here in this stillness.", "breath_pattern": None},
            {"timestamp_seconds": 260, "instruction_text": "Gently return. You've earned this peace. Carry it forward.", "breath_pattern": None},
        ],
    },

    # ── 10-minute sessions ────────────────────────────────────────────────
    {
        "id": "body_scan",
        "title": "Body Scan",
        "duration_minutes": 10,
        "category": "Full Body Relaxation",
        "description": "A systematic journey through your body, releasing tension from head to toe.",
        "mood_tags": ["stressed", "anxious", "tired", "restless"],
        "steps": [
            {"timestamp_seconds": 0, "instruction_text": "Lie down or sit comfortably. Close your eyes and take three deep breaths.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 30, "instruction_text": "Bring attention to the top of your head. Notice any tension. Let it soften.", "breath_pattern": None},
            {"timestamp_seconds": 70, "instruction_text": "Move to your forehead and eyes. Smooth out every crease. Relax your jaw.", "breath_pattern": None},
            {"timestamp_seconds": 120, "instruction_text": "Notice your neck and shoulders. Let them drop away from your ears.", "breath_pattern": None},
            {"timestamp_seconds": 170, "instruction_text": "Feel your arms grow heavy and warm. Fingers uncurl and relax.", "breath_pattern": None},
            {"timestamp_seconds": 220, "instruction_text": "Breathe into your chest and belly. Feel them rise and fall like gentle waves.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 290, "instruction_text": "Bring awareness to your hips and lower back. Release any tightness.", "breath_pattern": None},
            {"timestamp_seconds": 350, "instruction_text": "Travel down through your thighs, knees, calves. Let gravity hold them.", "breath_pattern": None},
            {"timestamp_seconds": 420, "instruction_text": "Finally, your feet and toes. Feel the connection to the ground beneath you.", "breath_pattern": None},
            {"timestamp_seconds": 480, "instruction_text": "Your whole body is at rest. Float in this calm for a moment.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 540, "instruction_text": "Slowly wiggle your fingers and toes. Take a deep, refreshing breath.", "breath_pattern": None},
            {"timestamp_seconds": 580, "instruction_text": "When you're ready, gently open your eyes. Welcome back.", "breath_pattern": None},
        ],
    },
    {
        "id": "loving_kindness",
        "title": "Loving Kindness",
        "duration_minutes": 10,
        "category": "Self-Compassion",
        "description": "Cultivate warmth toward yourself and others with this heart-centred practice.",
        "mood_tags": ["sad", "lonely", "self_critical", "low"],
        "steps": [
            {"timestamp_seconds": 0, "instruction_text": "Settle in. Place your hand on your heart. Feel its warmth.", "breath_pattern": None},
            {"timestamp_seconds": 20, "instruction_text": "Silently repeat: May I be happy. May I be healthy. May I be safe.", "breath_pattern": None},
            {"timestamp_seconds": 70, "instruction_text": "Mean each word. If resistance arises, that's okay. Just notice it.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 130, "instruction_text": "Now think of someone you love. Send them the same wishes: May you be happy...", "breath_pattern": None},
            {"timestamp_seconds": 200, "instruction_text": "Think of someone neutral — a classmate, a stranger. Extend the same warmth.", "breath_pattern": None},
            {"timestamp_seconds": 270, "instruction_text": "Now someone difficult. This is hard — be gentle. May you find peace.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 350, "instruction_text": "Expand outward: May all beings everywhere be happy, healthy, and safe.", "breath_pattern": None},
            {"timestamp_seconds": 420, "instruction_text": "Return to yourself. You deserve this same compassion.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 490, "instruction_text": "Feel the warmth radiating from your chest. You are worthy of love.", "breath_pattern": None},
            {"timestamp_seconds": 550, "instruction_text": "Gently release the practice. Carry this kindness into your day.", "breath_pattern": None},
        ],
    },
    {
        "id": "focus_flow",
        "title": "Focus Flow",
        "duration_minutes": 10,
        "category": "Concentration",
        "description": "Sharpen your attention and enter a state of focused flow.",
        "mood_tags": ["unfocused", "distracted", "scattered", "overwhelmed"],
        "steps": [
            {"timestamp_seconds": 0, "instruction_text": "Sit upright. Eyes half-open, gaze soft on a point ahead.", "breath_pattern": None},
            {"timestamp_seconds": 20, "instruction_text": "Count your breaths: inhale one, exhale two. Up to ten, then restart.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 90, "instruction_text": "When your mind wanders — and it will — gently bring it back. No judgment.", "breath_pattern": None},
            {"timestamp_seconds": 150, "instruction_text": "Narrow your focus to just the sensation at the tip of your nose.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 230, "instruction_text": "Imagine a single candle flame. Steady and unwavering. You are that flame.", "breath_pattern": None},
            {"timestamp_seconds": 310, "instruction_text": "Release the image. Just breathe. Pure awareness, nothing else.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 400, "instruction_text": "Notice how sharp and clear your mind feels. This is your natural state.", "breath_pattern": None},
            {"timestamp_seconds": 470, "instruction_text": "Set an intention: one task you'll carry this focus into.", "breath_pattern": None},
            {"timestamp_seconds": 530, "instruction_text": "Three final breaths. Deep, deliberate, focused.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 580, "instruction_text": "Open your eyes fully. You're ready to flow.", "breath_pattern": None},
        ],
    },

    # ── 15-minute sessions ────────────────────────────────────────────────
    {
        "id": "deep_sleep_prep",
        "title": "Deep Sleep Prep",
        "duration_minutes": 15,
        "category": "Insomnia Support",
        "description": "Gently guide your body and mind toward restful, restorative sleep.",
        "mood_tags": ["tired", "restless", "anxious", "wired"],
        "steps": [
            {"timestamp_seconds": 0, "instruction_text": "Lie in bed. Let your body sink into the mattress.", "breath_pattern": None},
            {"timestamp_seconds": 20, "instruction_text": "Slow your breathing. Inhale for four... exhale for six. Longer exhales calm your nervous system.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 80, "instruction_text": "Starting at your feet, imagine warm golden light melting all tension.", "breath_pattern": None},
            {"timestamp_seconds": 150, "instruction_text": "The warmth rises through your legs... your hips... your belly.", "breath_pattern": None},
            {"timestamp_seconds": 220, "instruction_text": "It fills your chest, your arms, your fingers. Everything softens.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 300, "instruction_text": "The light reaches your neck, your jaw, your eyes. Your face is completely relaxed.", "breath_pattern": None},
            {"timestamp_seconds": 370, "instruction_text": "Your mind is slowing. Thoughts drift by like clouds. Let them pass.", "breath_pattern": None},
            {"timestamp_seconds": 440, "instruction_text": "Count backwards from 10. With each number, sink deeper.", "breath_pattern": None},
            {"timestamp_seconds": 510, "instruction_text": "You are floating. Safe. Warm. Nothing to do, nowhere to be.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 600, "instruction_text": "Let your breath become effortless. Your body knows how to sleep.", "breath_pattern": None},
            {"timestamp_seconds": 700, "instruction_text": "If you're still awake, that's perfectly fine. Just rest here.", "breath_pattern": None},
            {"timestamp_seconds": 800, "instruction_text": "Goodnight. Tomorrow is a new beginning.", "breath_pattern": None},
        ],
    },
    {
        "id": "emotional_processing",
        "title": "Emotional Processing",
        "duration_minutes": 15,
        "category": "After a Difficult Day",
        "description": "Create space to feel, understand, and gently release difficult emotions.",
        "mood_tags": ["sad", "angry", "frustrated", "hurt", "overwhelmed"],
        "steps": [
            {"timestamp_seconds": 0, "instruction_text": "Find a quiet space. This time is just for you.", "breath_pattern": None},
            {"timestamp_seconds": 20, "instruction_text": "Take three deep breaths. Arrive fully in this moment.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 60, "instruction_text": "Ask yourself: What am I feeling right now? Name it without judgment.", "breath_pattern": None},
            {"timestamp_seconds": 120, "instruction_text": "Where do you feel it in your body? Place your hand there gently.", "breath_pattern": None},
            {"timestamp_seconds": 180, "instruction_text": "Say to yourself: It's okay to feel this. This emotion is valid.", "breath_pattern": None},
            {"timestamp_seconds": 240, "instruction_text": "Breathe into that place in your body. Imagine your breath softening it.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 320, "instruction_text": "What does this emotion need? Comfort? Space? Acknowledgment?", "breath_pattern": None},
            {"timestamp_seconds": 400, "instruction_text": "Imagine giving yourself exactly what you need. A hug, a kind word, permission to rest.", "breath_pattern": None},
            {"timestamp_seconds": 470, "instruction_text": "With each exhale, let a small amount of the intensity dissolve.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 550, "instruction_text": "You don't have to fix everything tonight. Feeling it is enough.", "breath_pattern": None},
            {"timestamp_seconds": 650, "instruction_text": "Place both hands on your heart. You showed up for yourself today.", "breath_pattern": None},
            {"timestamp_seconds": 750, "instruction_text": "Take a final deep breath. You are stronger than you think.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 850, "instruction_text": "Gently return. You can come back to this space anytime you need.", "breath_pattern": None},
        ],
    },
    {
        "id": "gratitude_journey",
        "title": "Gratitude Journey",
        "duration_minutes": 15,
        "category": "Mood Boost",
        "description": "A reflective journey through moments of gratitude that naturally lifts your mood.",
        "mood_tags": ["sad", "low", "neutral", "disconnected"],
        "steps": [
            {"timestamp_seconds": 0, "instruction_text": "Close your eyes. Settle into stillness with a few slow breaths.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 30, "instruction_text": "Think of something small that went well today. Even something tiny counts.", "breath_pattern": None},
            {"timestamp_seconds": 90, "instruction_text": "Hold that moment in your mind. Notice the warmth it brings.", "breath_pattern": None},
            {"timestamp_seconds": 150, "instruction_text": "Now think of a person who has shown you kindness. Picture their face.", "breath_pattern": None},
            {"timestamp_seconds": 220, "instruction_text": "Silently say thank you. Let gratitude fill your chest.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 300, "instruction_text": "Think of your body. Thank your lungs for breathing, your heart for beating.", "breath_pattern": None},
            {"timestamp_seconds": 370, "instruction_text": "Think of a challenge you've overcome. You are resilient.", "breath_pattern": None},
            {"timestamp_seconds": 440, "instruction_text": "Breathe in gratitude... breathe out anything that no longer serves you.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 520, "instruction_text": "Think of something you're looking forward to, no matter how small.", "breath_pattern": None},
            {"timestamp_seconds": 600, "instruction_text": "Let all these moments of gratitude blend into a warm glow inside you.", "breath_pattern": None},
            {"timestamp_seconds": 700, "instruction_text": "Smile gently. This feeling is always available to you.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 800, "instruction_text": "Take three final breaths. Let each one seal in this gratitude.", "breath_pattern": "inhale4_hold4_exhale4"},
            {"timestamp_seconds": 870, "instruction_text": "Open your eyes when you're ready. You carry this light with you.", "breath_pattern": None},
        ],
    },
]

_BY_ID = {m["id"]: m for m in MEDITATIONS}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_library() -> Dict[str, Any]:
    """Return all meditations grouped by duration tier."""
    groups: Dict[str, List[Dict[str, Any]]] = {"5": [], "10": [], "15": []}
    for m in MEDITATIONS:
        key = str(m["duration_minutes"])
        summary = {k: v for k, v in m.items() if k != "steps"}
        groups.setdefault(key, []).append(summary)
    return {"groups": groups, "total": len(MEDITATIONS)}


def get_meditation(meditation_id: str) -> Optional[Dict[str, Any]]:
    """Return full session including steps."""
    return _BY_ID.get(meditation_id)


def recommend_meditations(user_id: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Recommend meditations based on the user's latest mood check-in.
    Matches mood keywords to meditation mood_tags.
    """
    mongo = get_mongo()

    # Get latest check-in
    latest = mongo.db.analytics.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)],
    )

    # Derive mood keywords from check-in values
    keywords: List[str] = []
    if latest:
        mood = latest.get("mood", 3)
        stress = latest.get("stress", 3)
        energy = latest.get("energy", 3)
        motivation = latest.get("motivation", 3)

        if mood <= 2:
            keywords.extend(["sad", "low"])
        if stress >= 4:
            keywords.extend(["stressed", "anxious", "overwhelmed"])
        if energy <= 2:
            keywords.extend(["tired", "unfocused"])
        if motivation <= 2:
            keywords.extend(["low", "unfocused"])
        if mood >= 4 and stress <= 2:
            keywords.extend(["neutral"])  # good mood → lighter session

    if not keywords:
        keywords = ["stressed", "anxious"]  # sensible default

    keyword_set = set(keywords)

    # Score each meditation by tag overlap
    scored = []
    for m in MEDITATIONS:
        tags = set(m.get("mood_tags", []))
        overlap = len(tags & keyword_set)
        scored.append((overlap, m))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for _, m in scored[:limit]:
        results.append({k: v for k, v in m.items() if k != "steps"})
    return results


def log_completion(
    user_id: str,
    meditation_id: str,
    pre_mood: int,
    post_mood: int,
) -> Dict[str, Any]:
    """Log meditation completion with before/after mood."""
    mongo = get_mongo()
    delta = post_mood - pre_mood
    doc = {
        "user_id": user_id,
        "meditation_id": meditation_id,
        "pre_mood": pre_mood,
        "post_mood": post_mood,
        "delta": delta,
        "completed_at": datetime.now(timezone.utc),
    }
    mongo.db.meditation_completions.insert_one(doc)
    _LOG.info("Meditation completed", user_id=user_id, meditation_id=meditation_id, delta=delta)

    meditation = _BY_ID.get(meditation_id, {})
    return {
        "meditation_id": meditation_id,
        "title": meditation.get("title", meditation_id),
        "pre_mood": pre_mood,
        "post_mood": post_mood,
        "delta": delta,
        "message": f"You improved by +{delta}!" if delta > 0 else ("Your mood stayed the same." if delta == 0 else f"Your mood shifted by {delta}."),
    }
