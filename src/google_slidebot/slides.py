"""Google Slides API integration."""

import json
import re
from typing import Optional

import keyring
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from google_slidebot.config import KEYRING_SERVICE, KEYRING_TOKEN_KEY, CREDENTIALS_FILE, GOOGLE_SCOPES


def extract_presentation_id(url_or_id: str) -> str:
    """Extract presentation ID from URL or validate bare ID.

    Args:
        url_or_id: Google Slides URL or bare presentation ID

    Returns:
        The presentation ID

    Raises:
        ValueError: If input doesn't contain a valid presentation ID
    """
    if not url_or_id:
        raise ValueError("Empty input")

    # Pattern matches IDs that are 20+ chars of alphanumeric, dash, underscore
    pattern = r"([a-zA-Z0-9_-]{20,})"
    match = re.search(pattern, url_or_id)

    if not match:
        raise ValueError(f"Invalid presentation URL or ID: {url_or_id}")

    return match.group(1)


def get_stored_token() -> Optional[dict]:
    """Retrieve OAuth token from keyring.

    Returns:
        Token dict if found, None otherwise
    """
    stored = keyring.get_password(KEYRING_SERVICE, KEYRING_TOKEN_KEY)
    if stored is None:
        return None
    return json.loads(stored)


def store_token(token_data: dict) -> None:
    """Store OAuth token in keyring.

    Args:
        token_data: Token dict to store
    """
    keyring.set_password(KEYRING_SERVICE, KEYRING_TOKEN_KEY, json.dumps(token_data))


def delete_stored_token() -> None:
    """Delete OAuth token from keyring."""
    keyring.delete_password(KEYRING_SERVICE, KEYRING_TOKEN_KEY)


def get_credentials() -> Credentials:
    """Get valid Google OAuth credentials.

    Tries keyring first, refreshes if expired, or runs OAuth flow.

    Returns:
        Valid Credentials object

    Raises:
        FileNotFoundError: If credentials.json not found and no valid token
    """
    creds = None
    token_data = get_stored_token()

    if token_data:
        creds = Credentials.from_authorized_user_info(token_data, GOOGLE_SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        store_token(json.loads(creds.to_json()))
        return creds

    # Need to run OAuth flow
    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(
            f"credentials.json not found at {CREDENTIALS_FILE}\n"
            f"Download from Google Cloud Console and place it there."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), GOOGLE_SCOPES)
    creds = flow.run_local_server(port=0)
    store_token(json.loads(creds.to_json()))
    return creds
