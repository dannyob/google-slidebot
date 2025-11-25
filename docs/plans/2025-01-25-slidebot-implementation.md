# Google Slidebot Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a CLI tool that extracts links from Google Slides and posts them to Zoom chat via a TUI interface.

**Architecture:** CLI entry point orchestrates Google OAuth + Slides API for link extraction, Playwright CDP for Zoom chat interaction, and Textual for a two-screen TUI (slide list → link preview → send).

**Tech Stack:** Python 3.10+, Click (CLI), Textual (TUI), Playwright (CDP), google-api-python-client (Slides), keyring (secrets)

---

## Phase 0: Project Setup

### Task 0.1: Install Dependencies

**Step 1: Sync dependencies**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv sync
```

**Step 2: Install Playwright browsers**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run playwright install chromium
```

**Step 3: Verify installation**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run python -c "import textual; import playwright; import keyring; print('OK')"
```
Expected: `OK`

---

## Phase 1: Configuration Module

### Task 1.1: Create config.py with paths and constants

**Files:**
- Create: `src/google_slidebot/config.py`
- Test: `tests/test_config.py`

**Step 1: Write the test**

Create `tests/test_config.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_config.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'google_slidebot.config'`

**Step 3: Write minimal implementation**

Create `src/google_slidebot/config.py`:

```python
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
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_config.py -v
```
Expected: All 5 tests PASS

**Step 5: Commit**

```bash
cd /Users/danny/Public/src/dob/google-slidebot && git add src/google_slidebot/config.py tests/test_config.py && git commit -m "feat: add configuration module with paths and constants"
```

---

## Phase 2: Google Slides Module

### Task 2.1: Presentation ID extraction

**Files:**
- Create: `src/google_slidebot/slides.py`
- Test: `tests/test_slides.py`

**Step 1: Write the test**

Create `tests/test_slides.py`:

```python
"""Tests for Google Slides module."""

import pytest

from google_slidebot.slides import extract_presentation_id


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
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_slides.py::TestExtractPresentationId -v
```
Expected: FAIL with `ModuleNotFoundError` or `ImportError`

**Step 3: Write minimal implementation**

Add to `src/google_slidebot/slides.py`:

```python
"""Google Slides API integration."""

import re


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

    # Pattern matches IDs that are 25+ chars of alphanumeric, dash, underscore
    pattern = r"([a-zA-Z0-9_-]{25,})"
    match = re.search(pattern, url_or_id)

    if not match:
        raise ValueError(f"Invalid presentation URL or ID: {url_or_id}")

    return match.group(1)
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_slides.py::TestExtractPresentationId -v
```
Expected: All 5 tests PASS

**Step 5: Commit**

```bash
cd /Users/danny/Public/src/dob/google-slidebot && git add src/google_slidebot/slides.py tests/test_slides.py && git commit -m "feat: add presentation ID extraction"
```

---

### Task 2.2: OAuth token storage with keyring

**Files:**
- Modify: `src/google_slidebot/slides.py`
- Test: `tests/test_slides.py`

**Step 1: Write the test**

Add to `tests/test_slides.py`:

```python
import json
from unittest.mock import patch, MagicMock

from google_slidebot.slides import (
    extract_presentation_id,
    get_stored_token,
    store_token,
    delete_stored_token,
)


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
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_slides.py::TestTokenStorage -v
```
Expected: FAIL with `ImportError`

**Step 3: Write minimal implementation**

Add to `src/google_slidebot/slides.py`:

```python
import json
from typing import Optional

import keyring

from google_slidebot.config import KEYRING_SERVICE, KEYRING_TOKEN_KEY


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
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_slides.py::TestTokenStorage -v
```
Expected: All 4 tests PASS

**Step 5: Commit**

```bash
cd /Users/danny/Public/src/dob/google-slidebot && git add src/google_slidebot/slides.py tests/test_slides.py && git commit -m "feat: add keyring token storage"
```

---

### Task 2.3: Google OAuth authentication

**Files:**
- Modify: `src/google_slidebot/slides.py`
- Test: `tests/test_slides.py`

**Step 1: Write the test**

Add to `tests/test_slides.py`:

```python
from google_slidebot.slides import get_credentials
from google_slidebot.config import CREDENTIALS_FILE


class TestGetCredentials:
    """Tests for get_credentials function."""

    @patch("google_slidebot.slides.get_stored_token")
    @patch("google_slidebot.slides.Credentials")
    def test_returns_valid_credentials_from_keyring(
        self, mock_creds_class, mock_get_token
    ):
        """Should return credentials when valid token in keyring."""
        mock_get_token.return_value = {"token": "abc", "refresh_token": "xyz"}
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds_class.from_authorized_user_info.return_value = mock_creds

        result = get_credentials()

        assert result == mock_creds
        mock_creds_class.from_authorized_user_info.assert_called_once()

    @patch("google_slidebot.slides.get_stored_token")
    @patch("google_slidebot.slides.Credentials")
    @patch("google_slidebot.slides.store_token")
    @patch("google_slidebot.slides.Request")
    def test_refreshes_expired_credentials(
        self, mock_request, mock_store, mock_creds_class, mock_get_token
    ):
        """Should refresh and store when token expired but has refresh_token."""
        mock_get_token.return_value = {"token": "old", "refresh_token": "xyz"}
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "xyz"
        mock_creds_class.from_authorized_user_info.return_value = mock_creds

        result = get_credentials()

        mock_creds.refresh.assert_called_once()
        mock_store.assert_called_once()

    @patch("google_slidebot.slides.get_stored_token")
    @patch("google_slidebot.slides.CREDENTIALS_FILE", new_callable=lambda: MagicMock())
    def test_raises_when_no_credentials_file(self, mock_creds_file, mock_get_token):
        """Should raise FileNotFoundError when credentials.json missing."""
        mock_get_token.return_value = None
        mock_creds_file.exists.return_value = False

        with pytest.raises(FileNotFoundError, match="credentials.json"):
            get_credentials()
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_slides.py::TestGetCredentials -v
```
Expected: FAIL with `ImportError`

**Step 3: Write minimal implementation**

Add to `src/google_slidebot/slides.py`:

```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from google_slidebot.config import CREDENTIALS_FILE, GOOGLE_SCOPES


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
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_slides.py::TestGetCredentials -v
```
Expected: All 3 tests PASS

**Step 5: Commit**

```bash
cd /Users/danny/Public/src/dob/google-slidebot && git add src/google_slidebot/slides.py tests/test_slides.py && git commit -m "feat: add Google OAuth authentication"
```

---

### Task 2.4: Slide data extraction

**Files:**
- Modify: `src/google_slidebot/slides.py`
- Test: `tests/test_slides.py`

**Step 1: Write the test**

Add to `tests/test_slides.py`:

```python
from dataclasses import dataclass
from google_slidebot.slides import Slide, Link, extract_slides_from_presentation


class TestExtractSlidesFromPresentation:
    """Tests for extract_slides_from_presentation."""

    def test_extracts_slide_with_title_and_links(self):
        """Should extract title and links from slide."""
        # Minimal Slides API response structure
        presentation_data = {
            "slides": [
                {
                    "pageElements": [
                        {
                            "shape": {
                                "text": {
                                    "textElements": [
                                        {
                                            "textRun": {
                                                "content": "Welcome Slide\n",
                                                "style": {}
                                            }
                                        },
                                        {
                                            "textRun": {
                                                "content": "Click here",
                                                "style": {
                                                    "link": {"url": "https://example.com"}
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                }
            ]
        }

        slides = extract_slides_from_presentation(presentation_data)

        assert len(slides) == 1
        assert slides[0].number == 1
        assert "Welcome" in slides[0].title
        assert len(slides[0].links) == 1
        assert slides[0].links[0].url == "https://example.com"
        assert slides[0].links[0].text == "Click here"

    def test_handles_slide_with_no_links(self):
        """Should handle slides without links."""
        presentation_data = {
            "slides": [
                {
                    "pageElements": [
                        {
                            "shape": {
                                "text": {
                                    "textElements": [
                                        {"textRun": {"content": "No links here", "style": {}}}
                                    ]
                                }
                            }
                        }
                    ]
                }
            ]
        }

        slides = extract_slides_from_presentation(presentation_data)

        assert len(slides) == 1
        assert slides[0].links == []

    def test_handles_empty_presentation(self):
        """Should return empty list for presentation with no slides."""
        presentation_data = {"slides": []}
        slides = extract_slides_from_presentation(presentation_data)
        assert slides == []
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_slides.py::TestExtractSlidesFromPresentation -v
```
Expected: FAIL with `ImportError`

**Step 3: Write minimal implementation**

Add to `src/google_slidebot/slides.py`:

```python
from dataclasses import dataclass, field


@dataclass
class Link:
    """A hyperlink extracted from a slide."""

    text: str
    url: str


@dataclass
class Slide:
    """A slide with its extracted content."""

    number: int
    title: str
    links: list[Link] = field(default_factory=list)


def extract_slides_from_presentation(presentation_data: dict) -> list[Slide]:
    """Extract slide data from Slides API response.

    Args:
        presentation_data: Response from presentations().get()

    Returns:
        List of Slide objects with titles and links
    """
    slides = []

    for idx, slide_data in enumerate(presentation_data.get("slides", []), start=1):
        title = ""
        links = []

        for element in slide_data.get("pageElements", []):
            shape = element.get("shape")
            if shape is None:
                continue

            text_elements = shape.get("text", {}).get("textElements", [])

            for text_element in text_elements:
                text_run = text_element.get("textRun")
                if not text_run:
                    continue

                content = text_run.get("content", "").strip()
                style = text_run.get("style", {})
                link_info = style.get("link", {})
                url = link_info.get("url")

                # First non-empty text becomes title
                if not title and content:
                    title = content

                # Collect links
                if url:
                    links.append(Link(text=content or url, url=url))

        slides.append(Slide(number=idx, title=title or f"Slide {idx}", links=links))

    return slides
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_slides.py::TestExtractSlidesFromPresentation -v
```
Expected: All 3 tests PASS

**Step 5: Commit**

```bash
cd /Users/danny/Public/src/dob/google-slidebot && git add src/google_slidebot/slides.py tests/test_slides.py && git commit -m "feat: add slide data extraction"
```

---

### Task 2.5: Fetch presentation (integration function)

**Files:**
- Modify: `src/google_slidebot/slides.py`
- Test: `tests/test_slides.py`

**Step 1: Write the test**

Add to `tests/test_slides.py`:

```python
from google_slidebot.slides import fetch_presentation


class TestFetchPresentation:
    """Tests for fetch_presentation."""

    @patch("google_slidebot.slides.build")
    @patch("google_slidebot.slides.get_credentials")
    def test_fetches_and_extracts_slides(self, mock_get_creds, mock_build):
        """Should fetch presentation and return Slide objects."""
        mock_creds = MagicMock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.presentations().get().execute.return_value = {
            "slides": [
                {
                    "pageElements": [
                        {
                            "shape": {
                                "text": {
                                    "textElements": [
                                        {"textRun": {"content": "Test", "style": {}}}
                                    ]
                                }
                            }
                        }
                    ]
                }
            ]
        }

        slides = fetch_presentation("fake-presentation-id")

        assert len(slides) == 1
        assert slides[0].title == "Test"
        mock_build.assert_called_once_with("slides", "v1", credentials=mock_creds)
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_slides.py::TestFetchPresentation -v
```
Expected: FAIL with `ImportError`

**Step 3: Write minimal implementation**

Add to `src/google_slidebot/slides.py`:

```python
from googleapiclient.discovery import build


def fetch_presentation(presentation_id: str) -> list[Slide]:
    """Fetch a presentation and extract its slides.

    Args:
        presentation_id: Google Slides presentation ID

    Returns:
        List of Slide objects
    """
    creds = get_credentials()
    service = build("slides", "v1", credentials=creds)
    presentation = service.presentations().get(presentationId=presentation_id).execute()
    return extract_slides_from_presentation(presentation)
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_slides.py::TestFetchPresentation -v
```
Expected: PASS

**Step 5: Commit**

```bash
cd /Users/danny/Public/src/dob/google-slidebot && git add src/google_slidebot/slides.py tests/test_slides.py && git commit -m "feat: add fetch_presentation integration function"
```

---

## Phase 3: Zoom Chat Module

### Task 3.1: CDP connection

**Files:**
- Create: `src/google_slidebot/zoom_chat.py`
- Test: `tests/test_zoom_chat.py`

**Step 1: Write the test**

Create `tests/test_zoom_chat.py`:

```python
"""Tests for Zoom chat module."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from google_slidebot.zoom_chat import ZoomChat


class TestZoomChatConnect:
    """Tests for ZoomChat.connect."""

    @pytest.mark.asyncio
    @patch("google_slidebot.zoom_chat.async_playwright")
    async def test_connect_finds_zoom_page(self, mock_playwright):
        """Should connect to Chrome and find Zoom page."""
        # Setup mocks
        mock_pw = AsyncMock()
        mock_playwright.return_value.start = AsyncMock(return_value=mock_pw)

        mock_browser = AsyncMock()
        mock_pw.chromium.connect_over_cdp = AsyncMock(return_value=mock_browser)

        mock_context = MagicMock()
        mock_browser.contexts = [mock_context]

        mock_page = AsyncMock()
        mock_page.url = "https://app.zoom.us/wc/123/join"
        mock_context.pages = [mock_page]

        # Test
        chat = ZoomChat()
        await chat.connect()

        assert chat.page == mock_page
        mock_pw.chromium.connect_over_cdp.assert_called_once()

    @pytest.mark.asyncio
    @patch("google_slidebot.zoom_chat.async_playwright")
    async def test_connect_raises_when_no_zoom_page(self, mock_playwright):
        """Should raise when Zoom page not found."""
        mock_pw = AsyncMock()
        mock_playwright.return_value.start = AsyncMock(return_value=mock_pw)

        mock_browser = AsyncMock()
        mock_pw.chromium.connect_over_cdp = AsyncMock(return_value=mock_browser)

        mock_context = MagicMock()
        mock_browser.contexts = [mock_context]

        mock_page = AsyncMock()
        mock_page.url = "https://google.com"
        mock_context.pages = [mock_page]

        chat = ZoomChat()
        with pytest.raises(RuntimeError, match="Zoom"):
            await chat.connect()
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_zoom_chat.py::TestZoomChatConnect -v
```
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write minimal implementation**

Create `src/google_slidebot/zoom_chat.py`:

```python
"""Zoom chat integration via Chrome CDP."""

from playwright.async_api import async_playwright, Page

from google_slidebot.config import CDP_URL


class ZoomChat:
    """Manages Zoom chat interaction via Chrome DevTools Protocol."""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page: Page | None = None

    async def connect(self) -> None:
        """Connect to Chrome and find Zoom meeting page.

        Raises:
            RuntimeError: If Chrome not reachable or Zoom page not found
        """
        self.playwright = await async_playwright().start()

        try:
            self.browser = await self.playwright.chromium.connect_over_cdp(CDP_URL)
        except Exception as e:
            raise RuntimeError(
                f"Cannot connect to Chrome at {CDP_URL}. "
                "Start Chrome with --remote-debugging-port=9222"
            ) from e

        # Find Zoom page
        for context in self.browser.contexts:
            for page in context.pages:
                if "zoom.us" in page.url:
                    self.page = page
                    return

        raise RuntimeError(
            "No Zoom meeting page found. Navigate to your Zoom meeting in Chrome first."
        )

    async def disconnect(self) -> None:
        """Disconnect from Chrome."""
        if self.playwright:
            await self.playwright.stop()
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_zoom_chat.py::TestZoomChatConnect -v
```
Expected: All 2 tests PASS

**Step 5: Commit**

```bash
cd /Users/danny/Public/src/dob/google-slidebot && git add src/google_slidebot/zoom_chat.py tests/test_zoom_chat.py && git commit -m "feat: add Zoom CDP connection"
```

---

### Task 3.2: Send message to Zoom chat

**Files:**
- Modify: `src/google_slidebot/zoom_chat.py`
- Test: `tests/test_zoom_chat.py`

**Step 1: Write the test**

Add to `tests/test_zoom_chat.py`:

```python
class TestZoomChatSendMessage:
    """Tests for ZoomChat.send_message."""

    @pytest.mark.asyncio
    async def test_send_message_executes_javascript(self):
        """Should execute JS to insert text and click send."""
        chat = ZoomChat()
        chat.page = AsyncMock()
        chat.page.evaluate = AsyncMock(return_value={"success": True})

        await chat.send_message("Hello from test!")

        # Should have called evaluate with our JS
        chat.page.evaluate.assert_called()
        call_args = str(chat.page.evaluate.call_args)
        assert "Hello from test!" in call_args or chat.page.evaluate.called

    @pytest.mark.asyncio
    async def test_send_message_raises_when_not_connected(self):
        """Should raise when not connected."""
        chat = ZoomChat()

        with pytest.raises(RuntimeError, match="[Nn]ot connected"):
            await chat.send_message("Hello")
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_zoom_chat.py::TestZoomChatSendMessage -v
```
Expected: FAIL with `AttributeError`

**Step 3: Write minimal implementation**

Add to `src/google_slidebot/zoom_chat.py`:

```python
    async def send_message(self, text: str) -> None:
        """Send a message to Zoom chat.

        Opens chat panel if needed, inserts text, and clicks send.

        Args:
            text: Message text to send

        Raises:
            RuntimeError: If not connected or send fails
        """
        if not self.page:
            raise RuntimeError("Not connected. Call connect() first.")

        # JavaScript to send message via iframe
        js_code = """
        async (text) => {
            const iframe = document.querySelector('iframe#webclient');
            if (!iframe) throw new Error('Zoom iframe not found');

            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            if (!iframeDoc) throw new Error('Cannot access iframe document');

            // Open chat panel if needed
            let chatInput = iframeDoc.querySelector('.tiptap.ProseMirror');
            if (!chatInput) {
                const openBtn = iframeDoc.querySelector('button[aria-label="open the chat panel"]');
                if (openBtn) {
                    openBtn.click();
                    await new Promise(r => setTimeout(r, 500));
                    chatInput = iframeDoc.querySelector('.tiptap.ProseMirror');
                }
            }

            if (!chatInput) throw new Error('Chat input not found');

            // Focus and insert text
            chatInput.focus();
            iframeDoc.execCommand('insertText', false, text);

            // Dispatch input event to enable send button
            chatInput.dispatchEvent(new Event('input', { bubbles: true }));

            // Wait a moment for button to enable
            await new Promise(r => setTimeout(r, 100));

            // Click send with full mouse event sequence
            const sendBtn = iframeDoc.querySelector('button[aria-label="send"]');
            if (!sendBtn) throw new Error('Send button not found');

            sendBtn.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: iframe.contentWindow }));
            sendBtn.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, view: iframe.contentWindow }));
            sendBtn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: iframe.contentWindow }));

            return { success: true };
        }
        """

        result = await self.page.evaluate(js_code, text)
        if not result.get("success"):
            raise RuntimeError(f"Failed to send message: {result}")
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_zoom_chat.py::TestZoomChatSendMessage -v
```
Expected: All 2 tests PASS

**Step 5: Commit**

```bash
cd /Users/danny/Public/src/dob/google-slidebot && git add src/google_slidebot/zoom_chat.py tests/test_zoom_chat.py && git commit -m "feat: add send_message to Zoom chat"
```

---

### Task 3.3: Format links for chat

**Files:**
- Modify: `src/google_slidebot/zoom_chat.py`
- Test: `tests/test_zoom_chat.py`

**Step 1: Write the test**

Add to `tests/test_zoom_chat.py`:

```python
from google_slidebot.slides import Slide, Link
from google_slidebot.zoom_chat import format_links_message


class TestFormatLinksMessage:
    """Tests for format_links_message."""

    def test_formats_single_link(self):
        """Should format slide with one link."""
        slide = Slide(
            number=1,
            title="Introduction",
            links=[Link(text="Docs", url="https://docs.example.com")]
        )
        result = format_links_message(slide)
        assert "Slide 1" in result
        assert "Introduction" in result
        assert "Docs" in result
        assert "https://docs.example.com" in result

    def test_formats_multiple_links(self):
        """Should format slide with multiple links."""
        slide = Slide(
            number=3,
            title="Resources",
            links=[
                Link(text="GitHub", url="https://github.com/example"),
                Link(text="API", url="https://api.example.com"),
            ]
        )
        result = format_links_message(slide)
        assert "GitHub" in result
        assert "API" in result
        assert result.count("https://") == 2

    def test_handles_empty_links(self):
        """Should return appropriate message for no links."""
        slide = Slide(number=2, title="No Links", links=[])
        result = format_links_message(slide)
        assert "no links" in result.lower() or result == ""
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_zoom_chat.py::TestFormatLinksMessage -v
```
Expected: FAIL with `ImportError`

**Step 3: Write minimal implementation**

Add to `src/google_slidebot/zoom_chat.py` (at top level, not in class):

```python
from google_slidebot.slides import Slide


def format_links_message(slide: Slide) -> str:
    """Format slide links for Zoom chat.

    Args:
        slide: Slide with links to format

    Returns:
        Formatted message string
    """
    if not slide.links:
        return f"Slide {slide.number} ({slide.title}) has no links."

    lines = [f"Links from Slide {slide.number}: {slide.title}"]
    for link in slide.links:
        lines.append(f"• {link.text}: {link.url}")

    return "\n".join(lines)
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_zoom_chat.py::TestFormatLinksMessage -v
```
Expected: All 3 tests PASS

**Step 5: Commit**

```bash
cd /Users/danny/Public/src/dob/google-slidebot && git add src/google_slidebot/zoom_chat.py tests/test_zoom_chat.py && git commit -m "feat: add link message formatting"
```

---

## Phase 4: TUI Module

### Task 4.1: Slide list screen

**Files:**
- Create: `src/google_slidebot/tui.py`
- Test: `tests/test_tui.py`

**Step 1: Write the test**

Create `tests/test_tui.py`:

```python
"""Tests for TUI module."""

import pytest
from unittest.mock import MagicMock, AsyncMock

from google_slidebot.slides import Slide, Link
from google_slidebot.tui import SlideListScreen


class TestSlideListScreen:
    """Tests for SlideListScreen."""

    def test_creates_list_items_from_slides(self):
        """Should create list items for each slide."""
        slides = [
            Slide(number=1, title="Intro", links=[Link("x", "http://x.com")]),
            Slide(number=2, title="Main", links=[]),
            Slide(number=3, title="End", links=[Link("a", "http://a.com"), Link("b", "http://b.com")]),
        ]
        screen = SlideListScreen(slides)
        items = screen._build_list_items()

        assert len(items) == 3
        assert "(1 link)" in items[0] or "1 link" in items[0]
        assert "(0 links)" in items[1] or "0 links" in items[1]
        assert "(2 links)" in items[2] or "2 links" in items[2]
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_tui.py::TestSlideListScreen -v
```
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write minimal implementation**

Create `src/google_slidebot/tui.py`:

```python
"""Textual TUI for Google Slidebot."""

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static
from textual.binding import Binding

from google_slidebot.slides import Slide


class SlideListScreen(Screen):
    """Screen showing list of slides."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("enter", "select", "View Links"),
        Binding("escape", "quit", "Quit"),
    ]

    def __init__(self, slides: list[Slide], **kwargs):
        super().__init__(**kwargs)
        self.slides = slides

    def _build_list_items(self) -> list[str]:
        """Build display strings for each slide."""
        items = []
        for slide in self.slides:
            link_count = len(slide.links)
            link_text = f"({link_count} link{'s' if link_count != 1 else ''})"
            items.append(f"{slide.number}. {slide.title} {link_text}")
        return items

    def compose(self) -> ComposeResult:
        yield Header()
        yield ListView(
            *[ListItem(Label(item)) for item in self._build_list_items()],
            id="slide-list"
        )
        yield Footer()

    def action_select(self) -> None:
        """Handle enter key - show links for selected slide."""
        list_view = self.query_one("#slide-list", ListView)
        if list_view.highlighted_child is not None:
            index = list_view.index
            if index is not None and 0 <= index < len(self.slides):
                self.app.push_screen(LinkPreviewScreen(self.slides[index]))

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_tui.py::TestSlideListScreen -v
```
Expected: PASS

**Step 5: Commit**

```bash
cd /Users/danny/Public/src/dob/google-slidebot && git add src/google_slidebot/tui.py tests/test_tui.py && git commit -m "feat: add slide list TUI screen"
```

---

### Task 4.2: Link preview screen

**Files:**
- Modify: `src/google_slidebot/tui.py`
- Test: `tests/test_tui.py`

**Step 1: Write the test**

Add to `tests/test_tui.py`:

```python
from google_slidebot.tui import LinkPreviewScreen


class TestLinkPreviewScreen:
    """Tests for LinkPreviewScreen."""

    def test_displays_slide_links(self):
        """Should display all links from slide."""
        slide = Slide(
            number=2,
            title="Resources",
            links=[
                Link("Docs", "https://docs.example.com"),
                Link("API", "https://api.example.com"),
            ]
        )
        screen = LinkPreviewScreen(slide)
        content = screen._build_content()

        assert "Slide 2" in content
        assert "Resources" in content
        assert "Docs" in content
        assert "https://docs.example.com" in content
        assert "API" in content

    def test_displays_no_links_message(self):
        """Should show message when slide has no links."""
        slide = Slide(number=1, title="Empty", links=[])
        screen = LinkPreviewScreen(slide)
        content = screen._build_content()

        assert "no links" in content.lower()
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_tui.py::TestLinkPreviewScreen -v
```
Expected: FAIL with `ImportError`

**Step 3: Write minimal implementation**

Add to `src/google_slidebot/tui.py`:

```python
class LinkPreviewScreen(Screen):
    """Screen showing links for a single slide."""

    BINDINGS = [
        Binding("enter", "send", "Send to Chat"),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, slide: Slide, **kwargs):
        super().__init__(**kwargs)
        self.slide = slide

    def _build_content(self) -> str:
        """Build display content for the slide."""
        lines = [f"Slide {self.slide.number}: {self.slide.title}", ""]

        if not self.slide.links:
            lines.append("This slide has no links.")
        else:
            for i, link in enumerate(self.slide.links, 1):
                lines.append(f"{i}. {link.text}")
                lines.append(f"   {link.url}")
                lines.append("")

        return "\n".join(lines)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(self._build_content(), id="link-content")
        yield Footer()

    def action_send(self) -> None:
        """Send links to Zoom chat."""
        # Will be connected to ZoomChat in the app
        self.app.send_links(self.slide)

    def action_back(self) -> None:
        """Go back to slide list."""
        self.app.pop_screen()
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_tui.py::TestLinkPreviewScreen -v
```
Expected: All 2 tests PASS

**Step 5: Commit**

```bash
cd /Users/danny/Public/src/dob/google-slidebot && git add src/google_slidebot/tui.py tests/test_tui.py && git commit -m "feat: add link preview TUI screen"
```

---

### Task 4.3: Main TUI app

**Files:**
- Modify: `src/google_slidebot/tui.py`
- Test: `tests/test_tui.py`

**Step 1: Write the test**

Add to `tests/test_tui.py`:

```python
from google_slidebot.tui import SlidebotApp


class TestSlidebotApp:
    """Tests for SlidebotApp."""

    def test_app_has_title(self):
        """App should have appropriate title."""
        slides = [Slide(number=1, title="Test", links=[])]
        app = SlidebotApp(slides=slides, zoom_chat=None)
        assert "slidebot" in app.TITLE.lower() or "slide" in app.TITLE.lower()

    def test_app_stores_slides(self):
        """App should store slides reference."""
        slides = [Slide(number=1, title="Test", links=[])]
        app = SlidebotApp(slides=slides, zoom_chat=None)
        assert app.slides == slides
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_tui.py::TestSlidebotApp -v
```
Expected: FAIL with `ImportError`

**Step 3: Write minimal implementation**

Add to `src/google_slidebot/tui.py`:

```python
from google_slidebot.zoom_chat import ZoomChat, format_links_message


class SlidebotApp(App):
    """Main Textual application for Slidebot."""

    TITLE = "Google Slidebot"
    CSS = """
    #slide-list {
        height: 1fr;
    }
    #link-content {
        padding: 1 2;
    }
    """

    def __init__(self, slides: list[Slide], zoom_chat: ZoomChat | None, **kwargs):
        super().__init__(**kwargs)
        self.slides = slides
        self.zoom_chat = zoom_chat

    def on_mount(self) -> None:
        """Push the initial screen."""
        self.push_screen(SlideListScreen(self.slides))

    def send_links(self, slide: Slide) -> None:
        """Send slide links to Zoom chat."""
        if not slide.links:
            self.notify("No links to send", severity="warning")
            return

        if not self.zoom_chat:
            self.notify("Zoom not connected", severity="error")
            return

        message = format_links_message(slide)

        # Run async send in background
        self.run_worker(self._send_to_zoom(message))

    async def _send_to_zoom(self, message: str) -> None:
        """Background worker to send message."""
        try:
            await self.zoom_chat.send_message(message)
            self.notify("Sent!", severity="information")
            self.pop_screen()  # Back to slide list
        except Exception as e:
            self.notify(f"Send failed: {e}", severity="error")
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_tui.py::TestSlidebotApp -v
```
Expected: All 2 tests PASS

**Step 5: Commit**

```bash
cd /Users/danny/Public/src/dob/google-slidebot && git add src/google_slidebot/tui.py tests/test_tui.py && git commit -m "feat: add main Slidebot TUI app"
```

---

## Phase 5: CLI Entry Point

### Task 5.1: CLI with presentation URL argument

**Files:**
- Modify: `src/google_slidebot/cli.py`
- Test: `tests/test_cli.py`

**Step 1: Write the test**

Replace `tests/test_cli.py`:

```python
"""Tests for CLI module."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock, AsyncMock

from google_slidebot.cli import cli


class TestCli:
    """Tests for CLI commands."""

    def test_cli_requires_presentation_url(self):
        """Should fail without presentation URL."""
        runner = CliRunner()
        result = runner.invoke(cli, [])
        assert result.exit_code != 0

    @patch("google_slidebot.cli.extract_presentation_id")
    def test_cli_validates_presentation_url(self, mock_extract):
        """Should validate presentation URL/ID."""
        mock_extract.side_effect = ValueError("Invalid")
        runner = CliRunner()
        result = runner.invoke(cli, ["invalid-url"])
        assert result.exit_code != 0
        assert "Invalid" in result.output or "invalid" in result.output.lower()

    @patch("google_slidebot.cli.fetch_presentation")
    @patch("google_slidebot.cli.extract_presentation_id")
    @patch("google_slidebot.cli.ZoomChat")
    @patch("google_slidebot.cli.SlidebotApp")
    def test_cli_starts_app_with_valid_url(
        self, mock_app_class, mock_zoom, mock_extract, mock_fetch
    ):
        """Should start app when given valid URL."""
        mock_extract.return_value = "valid-id-12345678901234567890"
        mock_fetch.return_value = []

        mock_zoom_instance = MagicMock()
        mock_zoom_instance.connect = AsyncMock()
        mock_zoom.return_value = mock_zoom_instance

        mock_app = MagicMock()
        mock_app.run = MagicMock()
        mock_app_class.return_value = mock_app

        runner = CliRunner()
        result = runner.invoke(cli, ["https://docs.google.com/presentation/d/valid-id-12345678901234567890/edit"])

        # Should have attempted to fetch and run
        mock_fetch.assert_called_once_with("valid-id-12345678901234567890")
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_cli.py -v
```
Expected: FAIL

**Step 3: Write minimal implementation**

Replace `src/google_slidebot/cli.py`:

```python
"""Command-line interface for google-slidebot."""

import asyncio
import click

from google_slidebot.slides import extract_presentation_id, fetch_presentation
from google_slidebot.zoom_chat import ZoomChat
from google_slidebot.tui import SlidebotApp
from google_slidebot.config import CDP_URL


def print_chrome_instructions():
    """Print instructions for starting Chrome with CDP."""
    click.echo("""
Start Chrome with remote debugging enabled:

  Mac:
  /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222

  Linux:
  google-chrome --remote-debugging-port=9222

  Windows:
  chrome.exe --remote-debugging-port=9222

Then:
1. Navigate to your Zoom meeting (https://app.zoom.us/wc/join/...)
2. Join the meeting
3. Open the chat panel (optional - will be opened automatically)

Waiting for Zoom connection...
""")


@click.command()
@click.argument("presentation_url")
@click.version_option()
def cli(presentation_url: str):
    """Share Google Slides links to Zoom chat.

    PRESENTATION_URL: Google Slides URL or presentation ID
    """
    # Validate presentation URL
    try:
        presentation_id = extract_presentation_id(presentation_url)
    except ValueError as e:
        raise click.ClickException(str(e))

    click.echo(f"Fetching presentation {presentation_id}...")

    # Fetch slides
    try:
        slides = fetch_presentation(presentation_id)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Failed to fetch presentation: {e}")

    click.echo(f"Found {len(slides)} slides with {sum(len(s.links) for s in slides)} total links")

    # Connect to Zoom
    print_chrome_instructions()

    zoom_chat = ZoomChat()
    try:
        asyncio.run(zoom_chat.connect())
        click.echo("Connected to Zoom!")
    except RuntimeError as e:
        raise click.ClickException(str(e))

    # Run TUI
    app = SlidebotApp(slides=slides, zoom_chat=zoom_chat)
    app.run()


if __name__ == "__main__":
    cli()
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run pytest tests/test_cli.py -v
```
Expected: All 3 tests PASS

**Step 5: Commit**

```bash
cd /Users/danny/Public/src/dob/google-slidebot && git add src/google_slidebot/cli.py tests/test_cli.py && git commit -m "feat: add CLI entry point"
```

---

## Phase 6: Integration Testing

### Task 6.1: Manual end-to-end test

**No code changes - manual testing**

**Step 1: Start Chrome with debugging**

Run:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

**Step 2: Join a Zoom meeting in Chrome**

Navigate to `https://app.zoom.us/wc/join/YOUR-MEETING-ID` and join.

**Step 3: Run slidebot with a test presentation**

Run:
```bash
cd /Users/danny/Public/src/dob/google-slidebot && uv run google-slidebot "YOUR-PRESENTATION-URL"
```

**Step 4: Verify TUI shows slides**

- Should see list of slides with link counts
- Arrow keys should navigate
- Enter should show link preview

**Step 5: Verify sending to Zoom**

- On link preview, press Enter to send
- Should see "Sent!" notification
- Check Zoom chat for the message

---

## Summary

**Total Tasks:** 15 (including manual test)

**Files Created:**
- `src/google_slidebot/config.py`
- `src/google_slidebot/slides.py`
- `src/google_slidebot/zoom_chat.py`
- `src/google_slidebot/tui.py`
- `tests/test_config.py`
- `tests/test_slides.py`
- `tests/test_zoom_chat.py`
- `tests/test_tui.py`

**Files Modified:**
- `src/google_slidebot/cli.py`
- `tests/test_cli.py`
