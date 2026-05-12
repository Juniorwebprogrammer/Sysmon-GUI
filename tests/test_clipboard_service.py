from unittest.mock import Mock

import pytest

from app.application.ports.clipboard_repository import ClipboardHistoryRepository
from app.application.services.clipboard_service import ClipboardService
from app.domain.clipboard_item import ClipboardItem


class MockHistoryRepository(ClipboardHistoryRepository):
    def __init__(self):
        self._items: list[ClipboardItem] = []

    def add(self, item: ClipboardItem) -> None:
        self._items.insert(0, item)

    def get_all(self) -> list[ClipboardItem]:
        return list(self._items)

    def search(self, query: str) -> list[ClipboardItem]:
        lower_query = query.lower()
        return [
            item
            for item in self._items
            if lower_query in item.text.lower()
        ]


class TestClipboardService:
    @pytest.fixture
    def service(self):
        return ClipboardService(
            clipboard=Mock(),
            history=MockHistoryRepository(),
            monitor=Mock(),
            hotkey=Mock(),
        )

    def test_adds_item_on_clipboard_change(self, service):
        service._on_clipboard_change("hello world", "chrome")
        items = service.get_history()
        assert len(items) == 1
        assert items[0].text == "hello world"
        assert items[0].app_origin == "chrome"

    def test_does_not_duplicate_items(self, service):
        service._on_clipboard_change("hello world", "chrome")
        service._on_clipboard_change("hello world", "firefox")
        items = service.get_history()
        assert len(items) == 1

    def test_search_filters_by_text(self, service):
        service._on_clipboard_change("hello world", "chrome")
        service._on_clipboard_change("goodbye world", "terminal")

        result = service.get_history("hello")
        assert len(result) == 1
        assert result[0].text == "hello world"

    def test_search_returns_all_with_empty_query(self, service):
        service._on_clipboard_change("hello world", "chrome")
        service._on_clipboard_change("goodbye world", "terminal")

        result = service.get_history("")
        assert len(result) == 2

    def test_paste_item_calls_repository(self, service):
        mock_clipboard = Mock()
        service._clipboard = mock_clipboard
        service.paste_item("test text")
        mock_clipboard.copy.assert_called_once_with("test text")
        mock_clipboard.paste.assert_called_once_with("test text")

    def test_set_activate_callback(self, service):
        callback = Mock()
        service.set_activate_callback(callback)
        service._on_hotkey()
        callback.assert_called_once()

    def test_start_calls_monitor_and_hotkey(self, service):
        service.start()
        service._monitor.start.assert_called_once()
        service._hotkey.start.assert_called_once()
