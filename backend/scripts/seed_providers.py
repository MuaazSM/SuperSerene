#!/usr/bin/env python3
"""
Seed the providers collection with 10 sample teletherapy providers.

Usage:
    cd backend && python -m scripts.seed_providers
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from db.mongo import get_mongo


PROVIDERS = [
    {
        "provider_id": "prov_001",
        "name": "Dr. Ananya Sharma",
        "credentials": "Licensed Clinical Psychologist (PsyD)",
        "specialties": ["anxiety", "depression", "trauma"],
        "age_range_min": 13, "age_range_max": 24,
        "languages": ["English", "Hindi"],
        "availability_slots": [
            {"day": "monday", "start_time": "10:00", "end_time": "11:00", "timezone": "Asia/Kolkata"},
            {"day": "wednesday", "start_time": "14:00", "end_time": "15:00", "timezone": "Asia/Kolkata"},
            {"day": "friday", "start_time": "10:00", "end_time": "11:00", "timezone": "Asia/Kolkata"},
        ],
        "accepts_insurance": True,
        "session_cost": 40.0,
        "teletherapy_platform": "zoom",
        "rating": 4.8,
        "active": True,
        "bio": "Specialises in adolescent anxiety and depression with 8 years of clinical experience.",
    },
    {
        "provider_id": "prov_002",
        "name": "Dr. Marcus Rivera",
        "credentials": "Licensed Professional Counselor (LPC)",
        "specialties": ["depression", "substance_use", "stress"],
        "age_range_min": 13, "age_range_max": 30,
        "languages": ["English", "Spanish"],
        "availability_slots": [
            {"day": "tuesday", "start_time": "09:00", "end_time": "10:00", "timezone": "America/New_York"},
            {"day": "thursday", "start_time": "13:00", "end_time": "14:00", "timezone": "America/New_York"},
            {"day": "saturday", "start_time": "10:00", "end_time": "11:00", "timezone": "America/New_York"},
        ],
        "accepts_insurance": True,
        "session_cost": 60.0,
        "teletherapy_platform": "zoom",
        "rating": 4.6,
        "active": True,
        "bio": "Bilingual counselor focusing on substance use prevention and stress management in youth.",
    },
    {
        "provider_id": "prov_003",
        "name": "Dr. Emily Chen",
        "credentials": "Licensed Clinical Social Worker (LCSW)",
        "specialties": ["anxiety", "self_harm", "eating_disorders"],
        "age_range_min": 13, "age_range_max": 21,
        "languages": ["English"],
        "availability_slots": [
            {"day": "monday", "start_time": "15:00", "end_time": "16:00", "timezone": "America/Los_Angeles"},
            {"day": "wednesday", "start_time": "15:00", "end_time": "16:00", "timezone": "America/Los_Angeles"},
            {"day": "friday", "start_time": "11:00", "end_time": "12:00", "timezone": "America/Los_Angeles"},
        ],
        "accepts_insurance": False,
        "session_cost": 55.0,
        "teletherapy_platform": "meet",
        "rating": 4.9,
        "active": True,
        "bio": "Works with teens navigating anxiety, self-harm recovery, and body image challenges.",
    },
    {
        "provider_id": "prov_004",
        "name": "Dr. Raj Patel",
        "credentials": "Psychiatrist (MD)",
        "specialties": ["depression", "bipolar", "medication_management"],
        "age_range_min": 16, "age_range_max": 30,
        "languages": ["English", "Hindi"],
        "availability_slots": [
            {"day": "tuesday", "start_time": "11:00", "end_time": "12:00", "timezone": "Asia/Kolkata"},
            {"day": "thursday", "start_time": "11:00", "end_time": "12:00", "timezone": "Asia/Kolkata"},
        ],
        "accepts_insurance": True,
        "session_cost": 75.0,
        "teletherapy_platform": "zoom",
        "rating": 4.7,
        "active": True,
        "bio": "Board-certified psychiatrist specialising in mood disorders and medication management for young adults.",
    },
    {
        "provider_id": "prov_005",
        "name": "Sofia Morales, LMFT",
        "credentials": "Licensed Marriage & Family Therapist",
        "specialties": ["relationships", "family_conflict", "anxiety", "stress"],
        "age_range_min": 13, "age_range_max": 25,
        "languages": ["English", "Spanish"],
        "availability_slots": [
            {"day": "monday", "start_time": "09:00", "end_time": "10:00", "timezone": "America/Chicago"},
            {"day": "wednesday", "start_time": "09:00", "end_time": "10:00", "timezone": "America/Chicago"},
            {"day": "friday", "start_time": "14:00", "end_time": "15:00", "timezone": "America/Chicago"},
        ],
        "accepts_insurance": True,
        "session_cost": 45.0,
        "teletherapy_platform": "zoom",
        "rating": 4.5,
        "active": True,
        "bio": "Family therapist experienced in adolescent communication and relationship skills.",
    },
    {
        "provider_id": "prov_006",
        "name": "Dr. James Okonkwo",
        "credentials": "Licensed Clinical Psychologist (PhD)",
        "specialties": ["trauma", "grief", "depression", "cultural_identity"],
        "age_range_min": 13, "age_range_max": 30,
        "languages": ["English"],
        "availability_slots": [
            {"day": "tuesday", "start_time": "16:00", "end_time": "17:00", "timezone": "America/New_York"},
            {"day": "thursday", "start_time": "16:00", "end_time": "17:00", "timezone": "America/New_York"},
            {"day": "saturday", "start_time": "09:00", "end_time": "10:00", "timezone": "America/New_York"},
        ],
        "accepts_insurance": False,
        "session_cost": 70.0,
        "teletherapy_platform": "meet",
        "rating": 4.8,
        "active": True,
        "bio": "Trauma-focused therapist with expertise in grief, loss, and cultural identity work.",
    },
    {
        "provider_id": "prov_007",
        "name": "Priya Desai, LPC",
        "credentials": "Licensed Professional Counselor",
        "specialties": ["anxiety", "academic_stress", "self_esteem"],
        "age_range_min": 13, "age_range_max": 22,
        "languages": ["English", "Hindi"],
        "availability_slots": [
            {"day": "monday", "start_time": "17:00", "end_time": "18:00", "timezone": "Asia/Kolkata"},
            {"day": "thursday", "start_time": "17:00", "end_time": "18:00", "timezone": "Asia/Kolkata"},
        ],
        "accepts_insurance": False,
        "session_cost": 35.0,
        "teletherapy_platform": "zoom",
        "rating": 4.4,
        "active": True,
        "bio": "Specialises in academic stress and self-esteem building for teens and college students.",
    },
    {
        "provider_id": "prov_008",
        "name": "Dr. Sarah Kim",
        "credentials": "Licensed Clinical Psychologist (PsyD)",
        "specialties": ["substance_use", "impulse_control", "anger_management"],
        "age_range_min": 14, "age_range_max": 24,
        "languages": ["English"],
        "availability_slots": [
            {"day": "wednesday", "start_time": "10:00", "end_time": "11:00", "timezone": "America/Los_Angeles"},
            {"day": "friday", "start_time": "14:00", "end_time": "15:00", "timezone": "America/Los_Angeles"},
        ],
        "accepts_insurance": True,
        "session_cost": 65.0,
        "teletherapy_platform": "zoom",
        "rating": 4.6,
        "active": True,
        "bio": "Focuses on substance use intervention and impulse control strategies for adolescents.",
    },
    {
        "provider_id": "prov_009",
        "name": "Carlos Mendez, LCSW",
        "credentials": "Licensed Clinical Social Worker",
        "specialties": ["depression", "anxiety", "lgbtq_support"],
        "age_range_min": 13, "age_range_max": 25,
        "languages": ["English", "Spanish"],
        "availability_slots": [
            {"day": "tuesday", "start_time": "10:00", "end_time": "11:00", "timezone": "America/Chicago"},
            {"day": "thursday", "start_time": "10:00", "end_time": "11:00", "timezone": "America/Chicago"},
            {"day": "saturday", "start_time": "11:00", "end_time": "12:00", "timezone": "America/Chicago"},
        ],
        "accepts_insurance": True,
        "session_cost": 50.0,
        "teletherapy_platform": "meet",
        "rating": 4.7,
        "active": True,
        "bio": "Affirming therapist supporting LGBTQ+ youth with depression and anxiety.",
    },
    {
        "provider_id": "prov_010",
        "name": "Dr. Meera Iyer",
        "credentials": "Clinical Psychologist (MPhil)",
        "specialties": ["anxiety", "depression", "stress", "mindfulness"],
        "age_range_min": 13, "age_range_max": 30,
        "languages": ["English", "Hindi"],
        "availability_slots": [
            {"day": "monday", "start_time": "09:00", "end_time": "10:00", "timezone": "Asia/Kolkata"},
            {"day": "wednesday", "start_time": "09:00", "end_time": "10:00", "timezone": "Asia/Kolkata"},
            {"day": "friday", "start_time": "16:00", "end_time": "17:00", "timezone": "Asia/Kolkata"},
        ],
        "accepts_insurance": False,
        "session_cost": 30.0,
        "teletherapy_platform": "zoom",
        "rating": 4.5,
        "active": True,
        "bio": "Integrates mindfulness-based therapy for adolescent anxiety and depression.",
    },
]


def seed():
    mongo = get_mongo()
    coll = mongo.db.providers

    # Create indexes
    coll.create_index("provider_id", unique=True, name="provider_id_unique")
    coll.create_index("active", name="active_idx")
    coll.create_index("specialties", name="specialties_idx")

    inserted = 0
    for p in PROVIDERS:
        p["created_at"] = datetime.now(timezone.utc)
        try:
            coll.update_one(
                {"provider_id": p["provider_id"]},
                {"$set": p},
                upsert=True,
            )
            inserted += 1
        except Exception as e:
            print(f"  Skipped {p['provider_id']}: {e}")

    print(f"Seeded {inserted} providers into '{mongo.db_name}.providers'")


if __name__ == "__main__":
    seed()
