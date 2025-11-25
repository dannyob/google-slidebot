# Google Slidebot Design

**Date:** 2025-01-25
**Status:** Approved

## Overview

A CLI tool that extracts links from Google Slides presentations and posts them to Zoom chat during meetings. Helps presenters share relevant links with participants as they navigate through slides.

## User Flow

```
1. Start Chrome with --remote-debugging-port=9222
2. Navigate to Zoom web meeting, join, open chat panel
3. Run: slidebot <presentation-url>

slidebot then:
  a) Authenticates with Google (if needed)
  b) Fetches all slides + links from presentation
  c) Connects to Chrome via Playwright CDP
  d) Monitors until it finds Zoom chat input
  e) Launches TUI
```

## TUI Interface

### Screen 1: Slide List

```
┌────────────────────────────────────────────────────────┐
│  Google Slidebot              [Connected to Zoom ✓]    │
│────────────────────────────────────────────────────────│
│  > 1. Introduction to the Project         (2 links)    │
│    2. Architecture Overview               (5 links)    │
│    3. Demo & Screenshots                  (0 links)    │
│    4. Resources & Further Reading         (8 links)    │
│                                                        │
│  [↑/↓] Navigate  [Enter] View links  [q] Quit          │
└────────────────────────────────────────────────────────┘
```

Slide preview text comes from the first text element on each slide (title or first paragraph), truncated to fit.

### Screen 2: Link Preview

```
┌────────────────────────────────────────────────────────┐
│  Slide 4: Resources & Further Reading                  │
│────────────────────────────────────────────────────────│
│  1. Documentation → https://docs.example.com           │
│  2. GitHub repo → https://github.com/...               │
│  3. API Reference → https://api.example.com            │
│                                                        │
│  [Enter] Send to Zoom chat  [Esc] Back to list         │
└────────────────────────────────────────────────────────┘
```

After sending: brief "Sent!" flash, return to slide list.

## Architecture

```
google_slidebot/
├── cli.py                 # Entry point, orchestrates setup flow
├── tui.py                 # TUI screens using Textual
├── slides.py              # Google Slides API: auth + link extraction
├── zoom_chat.py           # Playwright CDP: connect, detect chat, send messages
└── config.py              # Paths for credentials, keyring service name
```

### slides.py

Adapts existing `slidebot.py` logic:
- OAuth flow using credentials.json from `~/.config/google-slidebot/`
- Token storage via **keyring** (service: `google-slidebot`)
- Fetch presentation, extract per-slide:
  - Title/preview text (first text element)
  - List of (link_text, url) tuples
- Scope: `https://www.googleapis.com/auth/presentations.readonly`

### zoom_chat.py

Chrome CDP integration via Playwright:

```python
from playwright.async_api import async_playwright

async def connect_to_zoom():
    pw = await async_playwright().start()
    browser = await pw.chromium.connect_over_cdp("http://localhost:9222")
    # Find Zoom tab, locate chat input
    # Return page object for sending messages
```

Functions:
- `connect()` - Connect to Chrome, find Zoom tab
- `is_ready()` - Returns True when Zoom page found
- `send_message(text)` - Opens chat if needed, types into chat, submits

**Zoom DOM Structure (validated via spike):**

Chat lives inside an iframe. Key selectors:
- Iframe: `iframe#webclient`
- Open chat button: `button[aria-label="open the chat panel"]`
- Close chat button: `button[aria-label="close the chat panel"]`
- Chat input: `.tiptap.ProseMirror` (ProseMirror contenteditable, only exists when panel open)
- Send button: `button[aria-label="send"]`

**Send message workflow:**
1. Check if chat input exists (panel may be closed)
2. If not, click `button[aria-label="open the chat panel"]`, wait ~300ms
3. Focus chat input
4. Insert text via `iframeDoc.execCommand('insertText', false, text)`
5. Dispatch `input` event to enable send button
6. Click send button with full mouse event sequence (mousedown, mouseup, click)

Message format:
```
Links from slide 4:
• Documentation: https://docs.example.com
• GitHub: https://github.com/example/repo
```

### tui.py

Two-screen Textual application:
- `SlideListScreen` - Navigable list with link counts
- `LinkPreviewScreen` - Shows links, confirms send

### cli.py

Orchestration:
- Parse presentation URL (extract presentation ID)
- Check for credentials, run auth if needed
- Poll for Zoom connection (every 2s)
- Launch TUI once connected

## Credential Storage

| Item | Storage |
|------|---------|
| `credentials.json` | File: `~/.config/google-slidebot/credentials.json` |
| OAuth token | keyring service: `google-slidebot`, key: `oauth-token` |

First-run experience:
```
$ slidebot https://docs.google.com/presentation/d/1abc.../edit

No Google credentials found.
Place your credentials.json in ~/.config/google-slidebot/
(Get it from: https://console.cloud.google.com/apis/credentials)

Then run this command again.
```

## Chrome Setup Instructions

Printed by CLI before waiting for connection:

```
Start Chrome with remote debugging enabled:

  Mac:
  /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222

  Linux:
  google-chrome --remote-debugging-port=9222

  Windows:
  chrome.exe --remote-debugging-port=9222

Then:
1. Navigate to your Zoom meeting (https://app.zoom.us/wc/join/...)
2. Join the meeting
3. Open the chat panel

Waiting for Zoom chat connection...
```

## Dependencies

```toml
[project]
dependencies = [
    "click>=8.0",
    "textual>=0.40",
    "playwright>=1.40",
    "google-api-python-client>=2.0",
    "google-auth-oauthlib>=1.0",
    "google-auth-httplib2>=0.2",
    "keyring>=24.0",
]
```

## Deferred / Future Work

- **Zoom DOM investigation** - Exact selectors for chat input TBD during implementation
- **CDP error handling** - Reconnection on disconnect
- **Automatic slide detection** - Screen capture + image matching, or Google Slides presenter mode monitoring
- **Multiple output targets** - Other chat platforms beyond Zoom

## Gitignore Additions

```
credentials.json
token.pickle
```

(token.pickle kept in gitignore even though we use keyring, in case of fallback or testing)
