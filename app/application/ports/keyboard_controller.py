from abc import ABC, abstractmethod


class KeyboardController(ABC):
    """Interface for enabling/disabling physical keyboard input."""

    @abstractmethod
    def set_enabled(self, enabled: bool) -> bool: ...
