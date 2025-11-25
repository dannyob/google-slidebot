"""Configuration constants for google-slidebot."""

from pathlib import Path

# Paths
CONFIG_DIR = Path.home() / ".config" / "google-slidebot"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"

# Keyring
KEYRING_SERVICE = "google-slidebot"
KEYRING_TOKEN_KEY = "oauth-token"

# Google API
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/presentations.readonly"]

# Chrome CDP
CDP_URL = "http://localhost:9222"
