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
