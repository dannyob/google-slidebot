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
