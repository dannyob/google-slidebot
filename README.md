# google-slidebot

Share links from Google Slides presentations to Zoom chat during live presentations.

## Features

- Extracts all hyperlinks from a Google Slides presentation
- Connects to Zoom web client via Chrome DevTools Protocol
- TUI interface for browsing slides and sending links
- Securely stores Google OAuth tokens in system keychain

## Prerequisites

1. **Google Cloud credentials** - OAuth client ID for Desktop app with Slides API enabled
2. **Chrome browser** - Started with remote debugging enabled
3. **Zoom web client** - Join meeting via Chrome (not the desktop app)

## Installation

```bash
# Install with uv
uv sync

# Install Playwright browser
uv run playwright install chromium
```

## Setup

### 1. Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable the **Google Slides API**
3. Create OAuth credentials (Desktop app type)
4. Download and save as `~/.config/google-slidebot/credentials.json`

### 2. Start Chrome with Remote Debugging

Quit Chrome completely, then:

**Mac:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

**Linux:**
```bash
google-chrome --remote-debugging-port=9222
```

### 3. Join Zoom Meeting in Chrome

Navigate to `https://app.zoom.us/wc/join` and join your meeting.

## Usage

```bash
uv run google-slidebot "https://docs.google.com/presentation/d/YOUR_PRESENTATION_ID/edit"
```

Or with just the presentation ID:

```bash
uv run google-slidebot "YOUR_PRESENTATION_ID"
```

### TUI Controls

- **Arrow keys** - Navigate slides
- **Enter** - View links / Send to chat
- **Escape** - Go back
- **q** - Quit

## Development

```bash
make help          # Show all commands
make test          # Run tests
make check         # Lint + format + test
```

## License

MIT
