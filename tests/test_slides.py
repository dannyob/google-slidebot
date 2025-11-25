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
