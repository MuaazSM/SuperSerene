"""Age-related utilities for SuperSerene."""


def get_age_band(user_id: str) -> str:
    """Return the age band for a user.

    Returns:
        'minor'       — age 13-17
        'young_adult' — age 18-25
        'adult'       — age 26+
        'unknown'     — age not stored or any error (fail-open)
    """
    try:
        from db.mongo import get_mongo

        mongo = get_mongo()
        user = mongo.db.users.find_one({"user_id": user_id}) or mongo.db.users.find_one({"_id": user_id})
        if not user:
            return "unknown"
        age = user.get("age")
        if age is None:
            return "unknown"
        age = int(age)
        if 13 <= age <= 17:
            return "minor"
        if 18 <= age <= 25:
            return "young_adult"
        return "adult"
    except Exception:
        return "unknown"
