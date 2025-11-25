"""Command-line interface for google-slidebot."""

import asyncio
import click

from google_slidebot.slides import extract_presentation_id, fetch_presentation
from google_slidebot.zoom_chat import ZoomChat
from google_slidebot.tui import SlidebotApp


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

    click.echo(
        f"Found {len(slides)} slides with {sum(len(s.links) for s in slides)} total links"
    )

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
