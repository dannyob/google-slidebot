"""Tests for TUI module."""

import pytest
from unittest.mock import MagicMock, AsyncMock

from google_slidebot.slides import Slide, Link
from google_slidebot.tui import SlideListScreen, LinkPreviewScreen


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
