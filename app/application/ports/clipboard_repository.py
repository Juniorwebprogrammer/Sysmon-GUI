from abc import ABC, abstractmethod

from app.domain.clipboard_item import ClipboardItem


class SystemClipboard(ABC):
    """Interface for low-level clipboard read/write operations."""

    @abstractmethod
    def copy(self, text: str) -> None: ...

    @abstractmethod
    def paste(self, text: str) -> None: ...


class ClipboardHistoryRepository(ABC):
    """Persistence interface for clipboard history items."""

    @abstractmethod
    def add(self, item: ClipboardItem) -> None: ...

    @abstractmethod
    def get_all(self) -> list[ClipboardItem]: ...

    @abstractmethod
    def search(self, query: str) -> list[ClipboardItem]: ...
