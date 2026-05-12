from collections.abc import Callable

from app.application.ports.clipboard_monitor import ClipboardMonitor, GlobalHotkeyListener
from app.application.ports.clipboard_repository import ClipboardHistoryRepository, SystemClipboard
from app.domain.clipboard_item import ClipboardItem


class ClipboardService:
    """Orchestrates clipboard monitoring, history storage, and paste operations."""

    def __init__(
        self,
        clipboard: SystemClipboard,
        history: ClipboardHistoryRepository,
        monitor: ClipboardMonitor,
        hotkey: GlobalHotkeyListener,
    ):
        self._clipboard = clipboard
        self._history = history
        self._monitor = monitor
        self._hotkey = hotkey
        self._on_activate_callback: Callable[[], None] | None = None

    def set_activate_callback(self, callback: Callable[[], None]) -> None:
        """Register a callback invoked when the global hotkey is pressed."""
        self._on_activate_callback = callback

    def start(self) -> None:
        """Begin monitoring clipboard changes and listening for the hotkey."""
        self._monitor.start(self._on_clipboard_change)
        self._hotkey.start(self._on_hotkey)

    def _on_clipboard_change(self, text: str, app: str) -> None:
        """Store new clipboard content if it doesn't already exist in history."""
        existing_items = [
            item
            for item in self._history.get_all()
            if item.text == text
        ]
        if not existing_items:
            self._history.add(ClipboardItem(text=text, app_origin=app))

    def _on_hotkey(self) -> None:
        """Trigger the registered activation callback when hotkey fires."""
        if self._on_activate_callback:
            self._on_activate_callback()

    def paste_item(self, text: str) -> None:
        """Copy text to clipboard and simulate Ctrl+V paste."""
        self._clipboard.copy(text)
        self._clipboard.paste(text)

    def get_history(self, query: str = "") -> list[ClipboardItem]:
        """Return all history items, optionally filtered by search query."""
        if query:
            return self._history.search(query)
        return self._history.get_all()
