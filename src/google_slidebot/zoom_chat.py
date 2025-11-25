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
