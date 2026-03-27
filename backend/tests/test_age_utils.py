"""
Tests for utils.age_utils.get_age_band().

Gap 3: Minor-aware content filtering utility.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestGetAgeBand:
    """get_age_band() returns the correct band or 'unknown' on failure."""

    def _mock_mongo(self, age):
        mock_mongo = MagicMock()
        mock_mongo.db.users.find_one.return_value = {"user_id": "u1", "age": age}
        return mock_mongo

    @patch("utils.age_utils.get_mongo")
    def test_minor_band_lower_boundary(self, mock_get_mongo):
        mock_get_mongo.return_value = self._mock_mongo(13)
        from utils.age_utils import get_age_band
        assert get_age_band("u1") == "minor"

    @patch("utils.age_utils.get_mongo")
    def test_minor_band_upper_boundary(self, mock_get_mongo):
        mock_get_mongo.return_value = self._mock_mongo(17)
        from utils.age_utils import get_age_band
        assert get_age_band("u1") == "minor"

    @patch("utils.age_utils.get_mongo")
    def test_young_adult_band(self, mock_get_mongo):
        mock_get_mongo.return_value = self._mock_mongo(20)
        from utils.age_utils import get_age_band
        assert get_age_band("u1") == "young_adult"

    @patch("utils.age_utils.get_mongo")
    def test_adult_band(self, mock_get_mongo):
        mock_get_mongo.return_value = self._mock_mongo(30)
        from utils.age_utils import get_age_band
        assert get_age_band("u1") == "adult"

    @patch("utils.age_utils.get_mongo")
    def test_unknown_when_age_missing(self, mock_get_mongo):
        mock_mongo = MagicMock()
        mock_mongo.db.users.find_one.return_value = {"user_id": "u1"}
        mock_get_mongo.return_value = mock_mongo
        from utils.age_utils import get_age_band
        assert get_age_band("u1") == "unknown"

    @patch("utils.age_utils.get_mongo")
    def test_unknown_when_user_not_found(self, mock_get_mongo):
        mock_mongo = MagicMock()
        mock_mongo.db.users.find_one.return_value = None
        mock_get_mongo.return_value = mock_mongo
        from utils.age_utils import get_age_band
        assert get_age_band("u1") == "unknown"

    @patch("utils.age_utils.get_mongo")
    def test_fail_open_on_db_error(self, mock_get_mongo):
        mock_get_mongo.side_effect = Exception("DB down")
        from utils.age_utils import get_age_band
        # Must not raise — fail-open returning 'unknown'
        assert get_age_band("u1") == "unknown"

    @patch("utils.age_utils.get_mongo")
    def test_boundary_18_is_young_adult(self, mock_get_mongo):
        mock_get_mongo.return_value = self._mock_mongo(18)
        from utils.age_utils import get_age_band
        assert get_age_band("u1") == "young_adult"

    @patch("utils.age_utils.get_mongo")
    def test_boundary_26_is_adult(self, mock_get_mongo):
        mock_get_mongo.return_value = self._mock_mongo(26)
        from utils.age_utils import get_age_band
        assert get_age_band("u1") == "adult"
