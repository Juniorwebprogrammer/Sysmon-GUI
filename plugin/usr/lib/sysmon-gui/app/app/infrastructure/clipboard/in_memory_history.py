from app.application.ports.clipboard_repository import ClipboardHistoryRepository
from app.domain.clipboard_item import ClipboardItem


class InMemoryHistoryRepository(ClipboardHistoryRepository):
    """In-memory clipboard history with deduplication and a max size limit."""

    def __init__(self, max_items: int = 20) -> None:
        self._items: list[ClipboardItem] = []
        self._max_items = max_items

    def add(self, item: ClipboardItem) -> None:
        """Insert item at front, removing duplicates. Evict oldest if over limit."""
        self._items = [existing for existing in self._items if existing.text != item.text]
        self._items.insert(0, item)
        if len(self._items) > self._max_items:
            self._items.pop()

    def get_all(self) -> list[ClipboardItem]:
        """Return a copy of all stored history items."""
        return list(self._items)

    def search(self, query: str) -> list[ClipboardItem]:
        """Filter items whose text or app origin contains the query (case-insensitive)."""
        lower_query = query.lower()
        return [
            item
            for item in self._items
            if lower_query in item.text.lower() or lower_query in item.app_origin.lower()
        ]
