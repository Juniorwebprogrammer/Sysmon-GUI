import pytest

from app.domain.clipboard_item import ClipboardItem
from app.infrastructure.clipboard.in_memory_history import InMemoryHistoryRepository


class TestInMemoryHistoryRepository:
    @pytest.fixture
    def repository(self):
        return InMemoryHistoryRepository(max_items=3)

    def test_add_item(self, repository):
        item = ClipboardItem(text="hello", app_origin="test")
        repository.add(item)
        items = repository.get_all()
        assert len(items) == 1
        assert items[0].text == "hello"

    def test_add_deduplicates_by_text(self, repository):
        repository.add(ClipboardItem(text="dup", app_origin="a"))
        repository.add(ClipboardItem(text="dup", app_origin="b"))
        items = repository.get_all()
        assert len(items) == 1
        assert items[0].app_origin == "b"

    def test_add_respects_max_items(self, repository):
        repository.add(ClipboardItem(text="a", app_origin="test"))
        repository.add(ClipboardItem(text="b", app_origin="test"))
        repository.add(ClipboardItem(text="c", app_origin="test"))
        repository.add(ClipboardItem(text="d", app_origin="test"))
        items = repository.get_all()
        assert len(items) == 3
        assert items[0].text == "d"

    def test_get_all_returns_copy(self, repository):
        repository.add(ClipboardItem(text="x", app_origin="test"))
        items = repository.get_all()
        items.append(ClipboardItem(text="y", app_origin="test"))
        assert len(repository.get_all()) == 1

    def test_search_by_text(self, repository):
        repository.add(ClipboardItem(text="hello world", app_origin="a"))
        repository.add(ClipboardItem(text="goodbye moon", app_origin="b"))
        result = repository.search("hello")
        assert len(result) == 1
        assert result[0].text == "hello world"

    def test_search_by_app_origin(self, repository):
        repository.add(ClipboardItem(text="foo", app_origin="chrome"))
        repository.add(ClipboardItem(text="bar", app_origin="terminal"))
        result = repository.search("chrome")
        assert len(result) == 1
        assert result[0].text == "foo"

    def test_search_case_insensitive(self, repository):
        repository.add(ClipboardItem(text="Hello", app_origin="Test"))
        result = repository.search("hello")
        assert len(result) == 1

    def test_search_empty_query_returns_all(self, repository):
        repository.add(ClipboardItem(text="a", app_origin="test"))
        repository.add(ClipboardItem(text="b", app_origin="test"))
        result = repository.search("")
        assert len(result) == 2

    def test_add_moves_to_front(self, repository):
        repository.add(ClipboardItem(text="first", app_origin="test"))
        repository.add(ClipboardItem(text="second", app_origin="test"))
        items = repository.get_all()
        assert items[0].text == "second"
        assert items[1].text == "first"
