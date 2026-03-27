"""
Tests for the backend minimum age gate in AuthService.signup().

Gap 1: POST /api/v1/auth/signup must reject age < 13 with ValueError
before any DB write.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
class TestAgeGate:
    """AuthService.signup() age validation."""

    async def _make_service(self):
        """Return an AuthService with a mocked DB."""
        with patch("services.auth_service.UserRepository"):
            from services.auth_service import AuthService
            svc = AuthService.__new__(AuthService)
            svc.db = MagicMock()
            svc.log_info = lambda *a, **kw: None
            return svc

    @patch("services.auth_service.UserRepository")
    @pytest.mark.asyncio
    async def test_rejects_age_below_13(self, mock_repo_cls):
        """signup() raises ValueError for age < 13 before any DB write."""
        mock_repo = AsyncMock()
        mock_repo.find_by_email = AsyncMock(return_value=None)
        mock_repo_cls.return_value = mock_repo

        from services.auth_service import AuthService
        svc = AuthService.__new__(AuthService)
        svc.db = MagicMock()
        svc.log_info = lambda *a, **kw: None

        with pytest.raises(ValueError, match="13"):
            await svc.signup(name="Kid", email="kid@test.com", password="secure123", age=12)

        # DB write must NOT have been called
        mock_repo.create_user.assert_not_called()

    @patch("services.auth_service.UserRepository")
    @pytest.mark.asyncio
    async def test_rejects_age_0(self, mock_repo_cls):
        mock_repo = AsyncMock()
        mock_repo.find_by_email = AsyncMock(return_value=None)
        mock_repo_cls.return_value = mock_repo

        from services.auth_service import AuthService
        svc = AuthService.__new__(AuthService)
        svc.db = MagicMock()
        svc.log_info = lambda *a, **kw: None

        with pytest.raises(ValueError, match="13"):
            await svc.signup(name="Baby", email="baby@test.com", password="secure123", age=0)

    @patch("services.auth_service.UserRepository")
    @patch("services.auth_service.hash_password", return_value="hashed")
    @patch("services.auth_service.create_jwt_token", return_value="tok")
    @pytest.mark.asyncio
    async def test_allows_age_13(self, mock_jwt, mock_hash, mock_repo_cls):
        """signup() succeeds for age == 13 (boundary)."""
        mock_repo = AsyncMock()
        mock_repo.find_by_email = AsyncMock(return_value=None)
        mock_repo.create_user = AsyncMock(return_value={
            "_id": "abc", "user_id": "abc", "email": "teen@test.com", "name": "Teen"
        })
        mock_repo_cls.return_value = mock_repo

        from services.auth_service import AuthService
        svc = AuthService.__new__(AuthService)
        svc.db = MagicMock()
        svc.log_info = lambda *a, **kw: None

        with patch("services.auth_service.get_mongo") as mock_get_mongo:
            mock_get_mongo.return_value.db.users.update_one = MagicMock()
            result = await svc.signup(name="Teen", email="teen@test.com", password="secure123", age=13)

        assert result["token"] == "tok"

    @patch("services.auth_service.UserRepository")
    @patch("services.auth_service.hash_password", return_value="hashed")
    @patch("services.auth_service.create_jwt_token", return_value="tok")
    @pytest.mark.asyncio
    async def test_allows_no_age(self, mock_jwt, mock_hash, mock_repo_cls):
        """signup() succeeds when age is not provided."""
        mock_repo = AsyncMock()
        mock_repo.find_by_email = AsyncMock(return_value=None)
        mock_repo.create_user = AsyncMock(return_value={
            "_id": "abc", "user_id": "abc", "email": "anon@test.com", "name": "Anon"
        })
        mock_repo_cls.return_value = mock_repo

        from services.auth_service import AuthService
        svc = AuthService.__new__(AuthService)
        svc.db = MagicMock()
        svc.log_info = lambda *a, **kw: None

        result = await svc.signup(name="Anon", email="anon@test.com", password="secure123")
        assert result["token"] == "tok"
