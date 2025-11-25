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
