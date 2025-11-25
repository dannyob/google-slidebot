"""Tests for configuration module."""

import os
from pathlib import Path

from google_slidebot.config import (
    CONFIG_DIR,
    CREDENTIALS_FILE,
    KEYRING_SERVICE,
    KEYRING_TOKEN_KEY,
    GOOGLE_SCOPES,
    CDP_URL,
)


def test_config_dir_is_in_user_home():
    """Config directory should be under user's home."""
    assert CONFIG_DIR.parent.parent == Path.home()
    assert "google-slidebot" in str(CONFIG_DIR)


def test_credentials_file_is_in_config_dir():
    """Credentials file should be inside config directory."""
    assert CREDENTIALS_FILE.parent == CONFIG_DIR


def test_keyring_constants_are_strings():
    """Keyring constants should be non-empty strings."""
    assert isinstance(KEYRING_SERVICE, str) and len(KEYRING_SERVICE) > 0
    assert isinstance(KEYRING_TOKEN_KEY, str) and len(KEYRING_TOKEN_KEY) > 0


def test_google_scopes_includes_slides_readonly():
    """Google scopes should include slides readonly."""
    assert any("presentations.readonly" in scope for scope in GOOGLE_SCOPES)


def test_cdp_url_is_localhost():
    """CDP URL should point to localhost."""
    assert "localhost" in CDP_URL or "127.0.0.1" in CDP_URL
