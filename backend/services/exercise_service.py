"""Exercise recommendation service."""

from typing import Dict, Any, Optional
from datetime import datetime, timezone

from services.base_service import BaseService


class ExerciseService(BaseService):
    """Service for exercise recommendations and feedback."""

    async def recommend(
        self,
        user_id: str,
        mood: int,
        context: str,
        energy_level: int,
        count: int,
    ) -> Dict[str, Any]:
        if not 1 <= mood <= 5:
            raise ValueError("Mood must be between 1 and 5")
        if not 1 <= energy_level <= 5:
            raise ValueError("Energy level must be between 1 and 5")

        try:
            try:
                exercises = await self.orchestrator.get_exercise_recommendations(
                    user_id=user_id,
                    mood=mood,
                    context=context,
                    energy_level=energy_level,
                    count=count,
                )
            except Exception as e:
                self.log_warning("Exercise recommendations failed", error=str(e))
                exercises = []

            event = {
                "user_id": user_id,
                "type": "recommendation_requested",
                "mood": mood,
                "energy_level": energy_level,
                "context": context,
                "recommendations": exercises,
                "created_at": datetime.now(timezone.utc),
            }
            result = self.db.exercise_events.insert_one(event)
            return {"exercises": exercises, "count": len(exercises), "request_id": str(result.inserted_id)}
        except Exception as e:
            self.log_warning("Exercise recommendation recording failed", error=str(e))
            return {"exercises": [], "count": 0, "request_id": None, "error": "recommendations_unavailable"}

    async def list_recommendations(self, user_id: str, limit: int, skip: int) -> Dict[str, Any]:
        try:
            recs = list(
                self.db.exercise_events.find({
                    "user_id": user_id,
                    "type": "recommendation_requested",
                }).sort("created_at", -1).skip(skip).limit(limit)
            )
        except Exception as e:
            self.log_warning("List recommendations failed", error=str(e))
            recs = []
        return {"recommendations": recs, "count": len(recs)}

    async def rate(
        self,
        user_id: str,
        exercise_id: str,
        rating: int,
        feedback: str = "",
    ) -> Dict[str, Any]:
        if not exercise_id:
            raise ValueError("exercise_id required")
        if not isinstance(rating, int) or not 1 <= rating <= 5:
            raise ValueError("Rating must be integer between 1 and 5")

        try:
            record = {
                "user_id": user_id,
                "exercise_id": exercise_id,
                "rating": rating,
                "feedback": feedback,
                "created_at": datetime.now(timezone.utc),
            }
            res = self.db.exercise_ratings.insert_one(record)
            return {"id": str(res.inserted_id), "rating": rating, "feedback": feedback}
        except Exception as e:
            self.log_warning("Rate exercise failed", error=str(e))
            return {"id": None, "rating": rating, "feedback": feedback, "error": "rating_failed"}

    async def history(self, user_id: str, limit: int, skip: int) -> Dict[str, Any]:
        try:
            events = list(
                self.db.exercise_events.find({"user_id": user_id})
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit)
            )
            ratings = list(self.db.exercise_ratings.find({"user_id": user_id}))
        except Exception as e:
            self.log_warning("Exercise history failed", error=str(e))
            events, ratings = [], []

        rating_map = {r.get("exercise_id"): r.get("rating") for r in ratings}

        enriched = []
        for event in events:
            item = event.copy()
            if "recommendations" in item:
                for rec in item.get("recommendations", []):
                    if isinstance(rec, dict) and "id" in rec:
                        rec["user_rating"] = rating_map.get(rec.get("id"))
            enriched.append(item)

        return {"history": enriched, "count": len(enriched), "total_ratings": len(ratings)}
