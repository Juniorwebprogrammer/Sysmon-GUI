from unittest.mock import MagicMock

import gi
import pytest

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

Gtk.init_check()

from app.application.services.clipboard_service import ClipboardService
from app.domain.clipboard_item import ClipboardItem
from app.presentation.clipboard_window import ClipboardCard, ClipboardWindow, _app_icon, _truncate


class TestHelpers:
    def test_truncate_short_text(self):
        assert _truncate("hello") == "hello"

    def test_truncate_long_text(self):
        text = "a" * 100
        assert len(_truncate(text)) == 60

    def test_truncate_replaces_newlines(self):
        assert _truncate("hello\nworld") == "hello world"

    def test_app_icon_code(self):
        assert _app_icon("code") == "com.visualstudio.code"

    def test_app_icon_chrome(self):
        assert _app_icon("chrome") == "google-chrome"

    def test_app_icon_firefox(self):
        assert _app_icon("firefox") == "firefox"

    def test_app_icon_terminal(self):
        assert _app_icon("terminal") == "utilities-terminal"

    def test_app_icon_unknown(self):
        assert _app_icon("unknown") == "text-x-generic"

    def test_app_icon_case_insensitive(self):
        assert _app_icon("CHROME") == "google-chrome"


class TestClipboardCard:
    def test_creation(self):
        card = ClipboardCard("hello world", "chrome")
        assert card.full_text == "hello world"


class TestClipboardWindow:
    @pytest.fixture
    def service(self):
        svc = MagicMock(spec=ClipboardService)
        svc.get_history.return_value = [
            ClipboardItem(text="hello", app_origin="chrome"),
            ClipboardItem(text="world", app_origin="terminal"),
        ]
        return svc

    @pytest.fixture
    def window(self, service):
        cw = ClipboardWindow(service)
        yield cw
        cw.destroy()

    @pytest.fixture
    def test_window(self, service):
        cw = ClipboardWindow(service, test_mode=True)
        yield cw
        cw.destroy()

    def test_creation(self, window):
        assert isinstance(window, Gtk.Window)

    def test_load_cards(self, window):
        window._load_cards()
        assert len(window.listbox.get_children()) == 2

    def test_load_cards_with_query(self, window, service):
        service.get_history.return_value = [
            ClipboardItem(text="hello", app_origin="chrome"),
        ]
        window._load_cards(query="hello")
        assert len(window.listbox.get_children()) == 1

    def test_refresh_shows_window(self, window):
        window.refresh()
        assert window.get_visible() is True

    def test_search_calls_load_cards(self, window):
        window.search_entry.set_text("test")
        window._on_search(window.search_entry)
        assert len(window.listbox.get_children()) == 2

    def test_escape_hides_window(self, window):
        window.show_all()
        from gi.repository import Gdk

        event = Gdk.EventKey()
        event.keyval = Gdk.KEY_Escape
        window._on_global_key(window, event)
        assert window.get_visible() is False

    def test_non_escape_key_does_not_hide(self, window):
        window.show_all()
        from gi.repository import Gdk

        event = Gdk.EventKey()
        event.keyval = Gdk.KEY_a
        result = window._on_global_key(window, event)
        assert window.get_visible() is True
        assert result is False

    def test_row_clicked_pastes(self, window, service):
        card = ClipboardCard("some text", "app")
        window.listbox.add(card)
        window._on_row_clicked(window.listbox, card)
        service.paste_item.assert_called_once_with("some text")

    def test_test_mode_has_badge(self, test_window):
        header = test_window.main_box.get_children()[0]
        labels = [c for c in header.get_children() if isinstance(c, Gtk.Label)]
        badge_text = "".join(label.get_text() for label in labels)
        assert "TEST" in badge_text
