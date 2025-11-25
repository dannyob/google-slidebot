"""Tests for Google Slides module."""

import json
import pytest
from unittest.mock import patch, MagicMock

from google_slidebot.slides import (
    extract_presentation_id,
    get_stored_token,
    store_token,
    delete_stored_token,
)


class TestExtractPresentationId:
    """Tests for extract_presentation_id function."""

    def test_extracts_id_from_edit_url(self):
        """Should extract ID from standard edit URL."""
        url = "https://docs.google.com/presentation/d/1abc123DEF456_xyz-789/edit"
        assert extract_presentation_id(url) == "1abc123DEF456_xyz-789"

    def test_extracts_id_from_view_url(self):
        """Should extract ID from view URL with query params."""
        url = "https://docs.google.com/presentation/d/1abc123DEF456_xyz-789/view?usp=sharing"
        assert extract_presentation_id(url) == "1abc123DEF456_xyz-789"

    def test_extracts_bare_id(self):
        """Should accept bare presentation ID."""
        bare_id = "1abc123DEF456_xyz-789"
        assert extract_presentation_id(bare_id) == "1abc123DEF456_xyz-789"

    def test_raises_on_invalid_input(self):
        """Should raise ValueError for invalid input."""
        with pytest.raises(ValueError, match="Invalid"):
            extract_presentation_id("not-a-valid-id")

    def test_raises_on_empty_input(self):
        """Should raise ValueError for empty input."""
        with pytest.raises(ValueError):
            extract_presentation_id("")


class TestTokenStorage:
    """Tests for keyring token storage."""

    @patch("google_slidebot.slides.keyring")
    def test_get_stored_token_returns_none_when_missing(self, mock_keyring):
        """Should return None when no token stored."""
        mock_keyring.get_password.return_value = None
        assert get_stored_token() is None

    @patch("google_slidebot.slides.keyring")
    def test_get_stored_token_returns_dict_when_present(self, mock_keyring):
        """Should return parsed token dict when stored."""
        token_data = {"token": "abc", "refresh_token": "xyz"}
        mock_keyring.get_password.return_value = json.dumps(token_data)
        result = get_stored_token()
        assert result == token_data

    @patch("google_slidebot.slides.keyring")
    def test_store_token_serializes_to_json(self, mock_keyring):
        """Should store token as JSON string."""
        token_data = {"token": "abc", "refresh_token": "xyz"}
        store_token(token_data)
        mock_keyring.set_password.assert_called_once()
        call_args = mock_keyring.set_password.call_args
        stored_json = call_args[0][2]
        assert json.loads(stored_json) == token_data

    @patch("google_slidebot.slides.keyring")
    def test_delete_stored_token_calls_keyring(self, mock_keyring):
        """Should call keyring delete."""
        delete_stored_token()
        mock_keyring.delete_password.assert_called_once()
