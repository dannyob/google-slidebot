"""Tests for CLI module."""

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
        runner.invoke(
            cli,
            [
                "https://docs.google.com/presentation/d/valid-id-12345678901234567890/edit"
            ],
        )

        # Should have attempted to fetch and run
        mock_fetch.assert_called_once_with("valid-id-12345678901234567890")
