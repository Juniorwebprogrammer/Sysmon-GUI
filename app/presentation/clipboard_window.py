import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

from app.application.services.clipboard_service import ClipboardService
from app.presentation.helpers import load_css, load_pixbuf

# Map known application names to their icon theme identifiers
_APP_ICON_MAP: dict[str, str] = {
    "code": "com.visualstudio.code",
    "chrome": "google-chrome",
    "firefox": "firefox",
    "terminal": "utilities-terminal",
}


def _app_icon(app_name: str) -> str:
    """Return a themed icon name for the given application name."""
    for key, icon_name in _APP_ICON_MAP.items():
        if key in app_name.lower():
            return icon_name
    return "text-x-generic"


def _truncate(text: str, max_chars: int = 60) -> str:
    """Replace newlines with spaces and truncate to max_chars."""
    return text.replace("\n", " ").strip()[:max_chars]


class ClipboardCard(Gtk.ListBoxRow):
    """A single clipboard history entry displayed as a list row."""

    def __init__(self, text: str, app_name: str):
        super().__init__()
        self.full_text = text

        row_layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row_layout.set_border_width(10)

        app_icon = Gtk.Image.new_from_icon_name(
            _app_icon(app_name), Gtk.IconSize.DND
        )
        row_layout.pack_start(app_icon, False, False, 0)

        text_label = Gtk.Label(label=_truncate(text))
        text_label.set_xalign(0)
        text_label.set_ellipsize(3)
        text_label.get_style_context().add_class("card-text")
        row_layout.pack_start(text_label, True, True, 0)

        self.add(row_layout)


class ClipboardWindow(Gtk.Window):
    """Floating window that displays clipboard history with search."""

    def __init__(self, clipboard_service: ClipboardService, test_mode: bool = False):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self._clipboard_service = clipboard_service
        self._test_mode = test_mode

        wm_class = "sysmon-gui-test" if test_mode else "sysmon-gui"
        self.set_wmclass(wm_class, wm_class)
        self.set_icon_name("sysmon-gui")

        self.set_role("clipboard-manager")
        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(550, 500)
        self.set_skip_taskbar_hint(False)

        app_icon = load_pixbuf(size=256)
        if app_icon:
            self.set_icon(app_icon)

        Gtk.Settings.get_default().set_property(
            "gtk-application-prefer-dark-theme", True
        )

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.main_box.get_style_context().add_class("window-bg")
        self.add(self.main_box)

        self._build_header()
        self._build_list()

        self.connect("key-press-event", self._on_global_key)
        self._apply_styles()

    def _build_header(self) -> None:
        """Construct the top header with optional test badge and search entry."""
        header = Gtk.Box(spacing=10)
        header.set_border_width(15)

        if self._test_mode:
            test_badge = Gtk.Label(label="[TEST]")
            test_badge.get_style_context().add_class("test-badge")
            header.pack_start(test_badge, False, False, 0)

        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search history...")
        self.search_entry.connect("changed", self._on_search)
        header.pack_start(self.search_entry, True, True, 0)
        self.main_box.pack_start(header, False, False, 0)

    def _build_list(self) -> None:
        """Construct the scrollable list of clipboard history cards."""
        self.listbox = Gtk.ListBox()
        self.listbox.connect("row-activated", self._on_row_clicked)
        scroll_container = Gtk.ScrolledWindow()
        scroll_container.add(self.listbox)
        self.main_box.pack_start(scroll_container, True, True, 0)

    def _on_global_key(self, widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        """Hide the window when Escape is pressed."""
        if event.keyval == Gdk.KEY_Escape:
            self.hide()
            return True
        return False

    def _on_row_clicked(self, listbox: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
        """Hide window and paste the selected item's text."""
        self.hide()
        self._clipboard_service.paste_item(row.full_text)

    def refresh(self) -> None:
        """Clear search, reload cards, and present the window."""
        self.search_entry.set_text("")
        self._load_cards()
        self.show_all()
        self.present()
        self.search_entry.grab_focus()

    def _load_cards(self, query: str = "") -> None:
        """Populate the listbox with clipboard history items matching the query."""
        for child in self.listbox.get_children():
            self.listbox.remove(child)
        for item in self._clipboard_service.get_history(query):
            self.listbox.add(ClipboardCard(item.text, item.app_origin))
        self.show_all()

    def _on_search(self, entry: Gtk.Entry) -> None:
        """Filter the displayed cards by search text."""
        self._load_cards(entry.get_text())

    def _apply_styles(self) -> None:
        """Load custom CSS for the clipboard window."""
        load_css(
            b"""
            .window-bg { background: #121212; border-radius: 12px; border: 1px solid #333; }
            entry { background: #1e1e1e; color: white; border-radius: 8px; padding: 8px; }
            row { background: #1a1a1a; margin: 2px 10px; border-radius: 6px; }
            row:selected { background: #00f2ff; }
            row:selected .card-text { color: #000; font-weight: bold; }
            .card-text { color: #eee; }
            .test-badge { color: #ff9800; font-size: 8pt; font-weight: bold; }
        """
        )
