import re
import subprocess
import threading
import time
from collections.abc import Callable

import pyperclip
from gi.repository import GLib
from pynput import keyboard

from app.application.ports.clipboard_monitor import ClipboardMonitor, GlobalHotkeyListener


class PynputMonitor(ClipboardMonitor):
    """Polls the system clipboard in a background thread and reports changes."""

    def __init__(self) -> None:
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self, on_change: Callable[[str, str], None]) -> None:
        """Launch a daemon thread that polls the clipboard every 500ms."""
        self._running = True
        self._thread = threading.Thread(
            target=self._monitor_clipboard, args=(on_change,), daemon=True
        )
        self._thread.start()

    def _monitor_clipboard(self, on_change: Callable[[str, str], None]) -> None:
        """Poll clipboard content and notify callback when it changes."""
        previous_content = ""
        while self._running:
            try:
                current_content = pyperclip.paste()
                if current_content and current_content != previous_content:
                    active_app = self._get_active_app()
                    on_change(current_content, active_app)
                    previous_content = current_content
            except Exception:
                pass
            time.sleep(0.5)

    @staticmethod
    def _get_active_app() -> str:
        """Detect the name of the currently focused application window."""
        try:
            window_id = subprocess.check_output(["xdotool", "getactivewindow"], text=True).strip()
            xprop_output = subprocess.check_output(
                ["xprop", "-id", window_id, "WM_CLASS"], text=True
            )
            app_names = re.findall(r'"([^"]*)"', xprop_output)
            return app_names[-1].lower() if app_names else "system"
        except Exception:
            return "system"

    def stop(self) -> None:
        """Signal the monitoring thread to exit."""
        self._running = False


class PynputHotkeyListener(GlobalHotkeyListener):
    """Listens for a global hotkey (default Alt+V) using pynput."""

    def __init__(
        self,
        modifier: keyboard.Key = keyboard.Key.alt,
        hotkey_char: str = "v",
    ) -> None:
        self._modifier = modifier
        self._hotkey_char = hotkey_char
        self._mod_pressed = False
        self._on_activate: Callable[[], None] | None = None

    def start(self, on_activate: Callable[[], None]) -> None:
        """Begin listening for the hotkey in a daemon thread."""
        self._on_activate = on_activate
        thread = threading.Thread(target=self._listen, daemon=True)
        thread.start()

    def _listen(self) -> None:
        """Blocking loop that runs the pynput listener."""
        while True:
            with keyboard.Listener(
                on_press=self._on_press, on_release=self._on_release
            ) as listener:
                listener.join()

    def _on_press(self, key: keyboard.Key | keyboard.KeyCode | None) -> bool | None:
        """Track modifier state and fire callback when hotkey combo is pressed."""
        if key in (self._modifier, keyboard.Key.alt_l, keyboard.Key.alt_r):
            self._mod_pressed = True
        if (
            hasattr(key, "char")
            and key.char == self._hotkey_char
            and self._mod_pressed
        ):
            GLib.idle_add(self._on_activate)
            return False
        return None

    def _on_release(self, key: keyboard.Key | keyboard.KeyCode | None) -> None:
        """Clear modifier state when the modifier key is released."""
        if key in (self._modifier, keyboard.Key.alt_l, keyboard.Key.alt_r):
            self._mod_pressed = False

    def stop(self) -> None:
        """No-op: the listener runs in a daemon thread that exits with the process."""
        pass
