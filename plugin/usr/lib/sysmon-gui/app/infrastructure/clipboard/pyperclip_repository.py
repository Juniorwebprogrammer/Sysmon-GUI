import threading
import time

import pyperclip
from pynput import keyboard

from app.application.ports.clipboard_repository import SystemClipboard


class PyperclipRepository(SystemClipboard):
    """Uses pyperclip for clipboard access and pynput to simulate Ctrl+V paste."""

    def __init__(self) -> None:
        self._keyboard_controller = keyboard.Controller()
        self._copy_delay = 0.4

    def copy(self, text: str) -> None:
        """Copy text to the system clipboard."""
        pyperclip.copy(text)

    def paste(self, text: str) -> None:
        """Copy text then simulate Ctrl+V in a background thread."""
        pyperclip.copy(text)

        def _do_paste() -> None:
            """Wait briefly for clipboard sync, then press Ctrl+V."""
            time.sleep(self._copy_delay)
            self._keyboard_controller.press(keyboard.Key.ctrl)
            self._keyboard_controller.press("v")
            self._keyboard_controller.release("v")
            self._keyboard_controller.release(keyboard.Key.ctrl)

        threading.Thread(target=_do_paste, daemon=True).start()
