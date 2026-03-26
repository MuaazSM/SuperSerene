"""
Provider schema for teletherapy matching.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class AvailabilitySlot(BaseModel):
    day: str                    # "monday", "tuesday", etc.
    start_time: str             # "09:00"
    end_time: str               # "10:00"
    timezone: str = "UTC"       # "America/New_York", "Asia/Kolkata", etc.


class Provider(BaseModel):
    provider_id: str
    name: str
    credentials: str            # e.g. "Licensed Clinical Psychologist"
    specialties: List[str]      # ["anxiety", "depression", "trauma", ...]
    age_range_min: int = 13
    age_range_max: int = 100
    languages: List[str] = ["English"]
    availability_slots: List[AvailabilitySlot] = []
    accepts_insurance: bool = False
    session_cost: float = 0.0   # in USD
    teletherapy_platform: str = "zoom"  # zoom / meet / custom
    rating: float = 4.0         # 0-5
    active: bool = True
    bio: str = ""
    image_url: str = ""

    def to_doc(self) -> Dict[str, Any]:
        d = self.model_dump()
        d["created_at"] = datetime.now(timezone.utc)
        return d
