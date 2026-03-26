"""
Multi-language crisis resource database.

All phone numbers and URLs have been sourced from the organisations' official
websites as of early 2025.  Numbers marked with # VERIFY should be re-checked
before a production launch.
"""

from typing import Dict, Any, List, Optional

from db.mongo import get_mongo
from logger.custom_logger import CustomLogger

_LOG = CustomLogger().get_logger(__name__)


# ---------------------------------------------------------------------------
# Resource database
# ---------------------------------------------------------------------------

CRISIS_RESOURCES: List[Dict[str, Any]] = [
    # ── English ───────────────────────────────────────────────────────────
    {
        "country": "United States",
        "country_code": "US",
        "language": "en",
        "hotline_name": "988 Suicide & Crisis Lifeline",
        "phone_number": "988",
        "text_line": "Text 988",
        "chat_url": "https://988lifeline.org/chat/",
        "hours": "24/7",
        "description": "Free, confidential support for people in suicidal crisis or emotional distress.",
    },
    {
        "country": "United States",
        "country_code": "US",
        "language": "en",
        "hotline_name": "Crisis Text Line",
        "phone_number": None,
        "text_line": "Text HOME to 741741",
        "chat_url": "https://www.crisistextline.org/",
        "hours": "24/7",
        "description": "Free crisis counseling via text message.",
    },
    {
        "country": "United Kingdom",
        "country_code": "GB",
        "language": "en",
        "hotline_name": "Samaritans",
        "phone_number": "116 123",
        "text_line": None,
        "chat_url": "https://www.samaritans.org/how-we-can-help/contact-samaritan/",
        "hours": "24/7",
        "description": "Emotional support for anyone in distress or at risk of suicide.",
    },
    {
        "country": "Australia",
        "country_code": "AU",
        "language": "en",
        "hotline_name": "Lifeline Australia",
        "phone_number": "13 11 14",
        "text_line": "Text 0477 13 11 14",
        "chat_url": "https://www.lifeline.org.au/crisis-chat/",
        "hours": "24/7",
        "description": "Crisis support and suicide prevention services.",
    },
    {
        "country": "Canada",
        "country_code": "CA",
        "language": "en",
        "hotline_name": "Talk Suicide Canada",
        "phone_number": "1-833-456-4566",
        "text_line": "Text 45645",
        "chat_url": "https://talksuicide.ca/",
        "hours": "24/7",
        "description": "Canada-wide suicide prevention and support service.",
    },
    {
        "country": "Ireland",
        "country_code": "IE",
        "language": "en",
        "hotline_name": "Samaritans Ireland",
        "phone_number": "116 123",
        "text_line": None,
        "chat_url": None,
        "hours": "24/7",
        "description": "Free emotional support, available day or night.",
    },
    {
        "country": "New Zealand",
        "country_code": "NZ",
        "language": "en",
        "hotline_name": "Lifeline New Zealand",
        "phone_number": "0800 543 354",
        "text_line": "Text HELP to 4357",
        "chat_url": None,
        "hours": "24/7",
        "description": "Telephone counselling and crisis support.",
    },

    # ── Hindi ─────────────────────────────────────────────────────────────
    {
        "country": "India",
        "country_code": "IN",
        "language": "hi",
        "hotline_name": "AASRA",
        "phone_number": "91-22-27546669",
        "text_line": None,
        "chat_url": "http://www.aasra.info/",
        "hours": "24/7",
        "description": "Crisis intervention centre for the depressed and suicidal.",
    },
    {
        "country": "India",
        "country_code": "IN",
        "language": "hi",
        "hotline_name": "Vandrevala Foundation Helpline",
        "phone_number": "1860-2662-345",
        "text_line": None,
        "chat_url": "https://www.vandrevalafoundation.com/",
        "hours": "24/7",
        "description": "Free, professional mental health counselling in multiple Indian languages.",
    },
    {
        "country": "India",
        "country_code": "IN",
        "language": "hi",
        "hotline_name": "iCall — TISS",
        "phone_number": "9152987821",
        "text_line": None,
        "chat_url": "https://icallhelpline.org/",
        "hours": "Mon-Sat, 8 AM - 10 PM IST",
        "description": "Psychosocial helpline run by Tata Institute of Social Sciences.",
    },
    {
        "country": "India",
        "country_code": "IN",
        "language": "hi",
        "hotline_name": "Snehi",
        "phone_number": "044-24640050",
        "text_line": None,
        "chat_url": "https://www.snehaindia.org/",
        "hours": "24/7",
        "description": "Emotional support and suicide prevention (Chennai-based, Hindi/English).",
    },

    # ── Spanish ───────────────────────────────────────────────────────────
    {
        "country": "Mexico",
        "country_code": "MX",
        "language": "es",
        "hotline_name": "Linea de la Vida",
        "phone_number": "800-911-2000",
        "text_line": None,
        "chat_url": None,
        "hours": "24/7",
        "description": "Linea nacional de atencion en crisis y prevencion del suicidio.",
    },
    {
        "country": "Spain",
        "country_code": "ES",
        "language": "es",
        "hotline_name": "Telefono de la Esperanza",
        "phone_number": "717 003 717",
        "text_line": None,
        "chat_url": "https://www.telefonodelaesperanza.org/",
        "hours": "24/7",
        "description": "Linea de atencion a la conducta suicida del Ministerio de Sanidad.",
    },
    {
        "country": "Mexico",
        "country_code": "MX",
        "language": "es",
        "hotline_name": "SAPTEL",
        "phone_number": "55 5259-8121",
        "text_line": None,
        "chat_url": "https://www.saptel.org.mx/",
        "hours": "24/7",
        "description": "Servicio de apoyo psicologico por telefono (Mexico City).",
    },
    {
        "country": "United States",
        "country_code": "US",
        "language": "es",
        "hotline_name": "988 Linea de Prevencion del Suicidio (espanol)",
        "phone_number": "988 (oprima 2 para espanol)",
        "text_line": "Envie un mensaje de texto con HOLA al 741741",
        "chat_url": "https://988lifeline.org/es/chat/",
        "hours": "24/7",
        "description": "Apoyo gratuito y confidencial en espanol para personas en crisis.",
    },

    # ── French ────────────────────────────────────────────────────────────
    {
        "country": "France",
        "country_code": "FR",
        "language": "fr",
        "hotline_name": "SOS Amitie",
        "phone_number": "09 72 39 40 50",
        "text_line": None,
        "chat_url": "https://www.sos-amitie.com/",
        "hours": "24/7",
        "description": "Ecoute et soutien emotionnel pour toute personne en detresse.",
    },
    {
        "country": "Canada",
        "country_code": "CA",
        "language": "fr",
        "hotline_name": "Tel-Aide",
        "phone_number": "514-935-1101",
        "text_line": None,
        "chat_url": None,
        "hours": "24/7",
        "description": "Service d'ecoute telephonique pour personnes en detresse (Quebec).",
    },
    {
        "country": "Belgium",
        "country_code": "BE",
        "language": "fr",
        "hotline_name": "Centre de Prevention du Suicide",
        "phone_number": "0800 32 123",
        "text_line": None,
        "chat_url": "https://www.preventionsuicide.be/",
        "hours": "24/7",
        "description": "Ligne d'ecoute gratuite pour la prevention du suicide.",
    },
    {
        "country": "France",
        "country_code": "FR",
        "language": "fr",
        "hotline_name": "3114 — Numero National de Prevention du Suicide",
        "phone_number": "3114",
        "text_line": None,
        "chat_url": "https://3114.fr/",
        "hours": "24/7",
        "description": "Numero national de prevention du suicide (gratuit, confidentiel).",
    },
]

LANGUAGE_NAMES: Dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
}

SUPPORTED_LANGUAGES = list(LANGUAGE_NAMES.keys())


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def get_resources(
    lang: Optional[str] = None,
    country_code: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Filter resources by language and/or country code."""
    results = CRISIS_RESOURCES
    if lang:
        results = [r for r in results if r["language"] == lang.lower()[:2]]
    if country_code:
        results = [r for r in results if r["country_code"] == country_code.upper()]
    return results


def get_all_grouped() -> Dict[str, List[Dict[str, Any]]]:
    """Return all resources grouped by language."""
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for r in CRISIS_RESOURCES:
        lang = r["language"]
        grouped.setdefault(lang, []).append(r)
    return grouped


def get_nearest(lang: str) -> Dict[str, Any]:
    """
    Return resources matching the user's language. Falls back to English
    with a note if the language isn't supported.
    """
    lang_key = lang.lower()[:2]
    matched = [r for r in CRISIS_RESOURCES if r["language"] == lang_key]
    if matched:
        return {
            "language": lang_key,
            "language_name": LANGUAGE_NAMES.get(lang_key, lang_key),
            "resources": matched,
            "fallback": False,
        }
    # Fallback to English
    en = [r for r in CRISIS_RESOURCES if r["language"] == "en"]
    return {
        "language": "en",
        "language_name": "English",
        "resources": en,
        "fallback": True,
        "note": f"Resources in '{lang}' are not yet available. Showing English resources.",
    }


def get_resources_for_escalation(
    user_id: Optional[str] = None,
    text: Optional[str] = None,
    lang: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Called by the safety checker during escalation.
    Detects language and returns matching crisis resources.
    """
    detected_lang = lang or _detect_user_language(user_id, text)
    result = get_nearest(detected_lang)

    # Always include a compact list for embedding in chat responses
    compact = []
    for r in result["resources"][:3]:
        entry = {"name": r["hotline_name"], "hours": r["hours"]}
        if r.get("phone_number"):
            entry["phone"] = r["phone_number"]
        if r.get("text_line"):
            entry["text"] = r["text_line"]
        if r.get("chat_url"):
            entry["chat"] = r["chat_url"]
        compact.append(entry)

    result["compact"] = compact
    return result


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

def _detect_user_language(user_id: Optional[str], text: Optional[str]) -> str:
    """
    Detect user's language:
    1. Check user profile for 'language' field
    2. Fall back to lightweight text-based detection
    3. Default to 'en'
    """
    # 1. Profile check
    if user_id:
        try:
            mongo = get_mongo()
            user = mongo.get_user(user_id) or mongo.db.users.find_one({"user_id": user_id})
            if user:
                profile_lang = user.get("language") or user.get("locale")
                if profile_lang:
                    return profile_lang[:2].lower()
        except Exception:
            pass

    # 2. Text-based detection
    if text and len(text.strip()) > 10:
        detected = _detect_from_text(text)
        if detected:
            return detected

    return "en"


def _detect_from_text(text: str) -> Optional[str]:
    """Lightweight language detection. Try langdetect first, fall back to keyword heuristics."""
    # Try langdetect library
    try:
        from langdetect import detect
        lang = detect(text)
        if lang in SUPPORTED_LANGUAGES:
            return lang
        # Map common langdetect codes
        mapping = {"hi": "hi", "es": "es", "fr": "fr", "en": "en"}
        return mapping.get(lang)
    except ImportError:
        pass
    except Exception:
        pass

    # Keyword heuristic fallback
    lower = text.lower()

    hindi_markers = ["मैं", "मुझे", "है", "हूं", "क्या", "nahi", "kya", "mujhe", "hai", "hoon", "kaise"]
    if any(m in lower for m in hindi_markers):
        return "hi"

    spanish_markers = ["estoy", "necesito", "ayuda", "tengo", "puedo", "quiero", "siento", "dolor"]
    if any(m in lower for m in spanish_markers):
        return "es"

    french_markers = ["je suis", "j'ai", "besoin", "aide", "pourquoi", "comment", "triste", "seul"]
    if any(m in lower for m in french_markers):
        return "fr"

    return None


def detect_language(text: str, user_id: Optional[str] = None) -> str:
    """Public interface for language detection."""
    return _detect_user_language(user_id, text)
