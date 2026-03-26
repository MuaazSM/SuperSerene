"""Authentication service.

Provides signup and login flows with password hashing and JWT issuance.
"""

from datetime import datetime, timezone
from typing import Dict
import bcrypt

from services.base_service import BaseService
from db.repositories.user_repository import UserRepository
from auth import create_jwt_token


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Truncate password to 72 bytes for bcrypt compatibility
    password_bytes = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash."""
    password_bytes = password[:72].encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


class AuthService(BaseService):
    """Service handling user authentication and registration."""

    async def login(self, email: str, password: str) -> Dict[str, str]:
        """Validate credentials and return JWT + profile."""
        users = UserRepository(self.db)
        user = await users.find_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(password, user.get("hashed_password", "")):
            raise ValueError("Invalid email or password")

        await users.update_last_login(str(user["_id"]))

        token = create_jwt_token(user)
        self.log_info("User login", email=email)

        return {
            "token": token,
            "user_id": str(user["_id"]),
            "email": user["email"],
            "name": user.get("name", ""),
        }

    async def signup(self, name: str, email: str, password: str, age: int | None = None) -> Dict[str, str]:
        """Register a new user and return JWT + profile."""
        users = UserRepository(self.db)

        if not email or not password or not name:
            raise ValueError("Email, password, and name are required")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        # Truncate password if needed for bcrypt (max 72 bytes)
        password_truncated = password[:72]

        existing = await users.find_by_email(email)
        if existing:
            # Treat existing users as idempotent signup: return a fresh token when password matches
            if verify_password(password_truncated, existing.get("hashed_password", "")):
                token = create_jwt_token(existing)
                self.log_info("User signup (idempotent)", email=email)
                return {
                    "token": token,
                    "user_id": str(existing["_id"]),
                    "email": existing["email"],
                    "name": existing.get("name", ""),
                }
            raise ValueError("Email already registered")
        
        doc = await users.create_user(
            name=name,
            email=email,
            hashed_password=hash_password(password_truncated),
        )

        # Store age if provided
        if age is not None:
            try:
                from db.mongo import get_mongo
                get_mongo().db.users.update_one(
                    {"user_id": doc.get("user_id")},
                    {"$set": {"age": age}},
                )
            except Exception:
                pass

        token = create_jwt_token(doc)
        self.log_info("User signup", email=email)

        return {
            "token": token,
            "user_id": str(doc["_id"]),
            "email": doc["email"],
            "name": doc["name"],
        }
