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
            items.append(f"{slide.number:2d}. {link_text} {slide.title}")
        return items

    def compose(self) -> ComposeResult:
        yield Header()
        yield ListView(
            *[ListItem(Label(item)) for item in self._build_list_items()],
            id="slide-list",
        )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle item selection from ListView."""
        index = event.list_view.index
        if index is not None and 0 <= index < len(self.slides):
            self.app.push_screen(LinkPreviewScreen(self.slides[index]))

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


class LinkPreviewScreen(Screen):
    """Screen showing links for a single slide."""

    BINDINGS = [
        Binding("enter", "send", "Send to Chat"),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, slide: Slide, **kwargs):
        super().__init__(**kwargs)
        self.slide = slide

    def _build_content(self) -> str:
        """Build display content for the slide."""
        lines = [f"Slide {self.slide.number}: {self.slide.title}", ""]

        if not self.slide.links:
            lines.append("This slide has no links.")
        else:
            for i, link in enumerate(self.slide.links, 1):
                lines.append(f"{i}. {link.text}")
                lines.append(f"   {link.url}")
                lines.append("")

        return "\n".join(lines)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(self._build_content(), id="link-content")
        yield Footer()

    def action_send(self) -> None:
        """Send links to Zoom chat."""
        # Will be connected to ZoomChat in the app
        self.app.send_links(self.slide)

    def action_back(self) -> None:
        """Go back to slide list."""
        self.app.pop_screen()


class SlidebotApp(App):
    """Main Textual application for Slidebot."""

    TITLE = "Google Slidebot"
    CSS = """
    #slide-list {
        height: 1fr;
    }
    #link-content {
        padding: 1 2;
    }
    """

    def __init__(self, slides: list[Slide], zoom_chat, **kwargs):
        super().__init__(**kwargs)
        self.slides = slides
        self.zoom_chat = zoom_chat

    def on_mount(self) -> None:
        """Push the initial screen."""
        self.push_screen(SlideListScreen(self.slides))

    def send_links(self, slide: Slide) -> None:
        """Send slide links to Zoom chat."""
        from google_slidebot.zoom_chat import format_links_message

        if not slide.links:
            self.notify("No links to send", severity="warning")
            return

        if not self.zoom_chat:
            self.notify("Zoom not connected", severity="error")
            return

        message = format_links_message(slide)

        # Run async send in background
        self.run_worker(self._send_to_zoom(message))

    async def _send_to_zoom(self, message: str) -> None:
        """Background worker to send message."""
        try:
            await self.zoom_chat.send_message(message)
            self.notify("Sent!", severity="information")
            self.pop_screen()  # Back to slide list
        except Exception as e:
            self.notify(f"Send failed: {e}", severity="error")
