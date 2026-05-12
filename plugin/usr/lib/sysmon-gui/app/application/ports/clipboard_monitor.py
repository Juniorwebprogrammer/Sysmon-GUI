from abc import ABC, abstractmethod
from collections.abc import Callable


class ClipboardMonitor(ABC):
    """Watches the system clipboard for changes and notifies via callback."""

    @abstractmethod
    def start(self, on_change: Callable[[str, str], None]) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...


class GlobalHotkeyListener(ABC):
    """Listens for a global hotkey combination to trigger the clipboard UI."""

    @abstractmethod
    def start(self, on_activate: Callable[[], None]) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...
