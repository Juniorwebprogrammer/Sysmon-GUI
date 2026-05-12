#!/usr/bin/env python3
import signal
import sys

import gi
import psutil

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

from app.application.services.clean_mode_service import CleanModeService
from app.application.services.clipboard_service import ClipboardService
from app.application.services.monitor_service import MonitorService
from app.infrastructure.clipboard.in_memory_history import InMemoryHistoryRepository
from app.infrastructure.clipboard.pynput_monitor import PynputHotkeyListener, PynputMonitor
from app.infrastructure.clipboard.pyperclip_repository import PyperclipRepository
from app.infrastructure.system.psutil_collector import PsutilCollector
from app.infrastructure.system.xinput_keyboard import XinputKeyboardController
from app.presentation.clipboard_window import ClipboardWindow
from app.presentation.main_window import MainWindow


class SysmonApplication(Gtk.Application):
    """Top-level GTK application that wires together all services and windows."""

    def __init__(self, test_mode: bool = False):
        self._test_mode = test_mode
        app_id = (
            "com.test.sysmon-gui.test"
            if test_mode
            else "com.test.sysmon-gui"
        )
        super().__init__(application_id=app_id)

    def do_activate(self):
        """Build the full application: services, clipboard UI, and main window."""
        program_name = "sysmon-gui-test" if self._test_mode else "sysmon-gui"
        app_title = "Sysmon GUI [TEST]" if self._test_mode else "Sysmon GUI"
        GLib.set_prgname(program_name)
        GLib.set_application_name(app_title)

        # Graceful shutdown on SIGTERM / SIGINT
        signal.signal(signal.SIGTERM, lambda *_: self.quit())
        signal.signal(signal.SIGINT, lambda *_: self.quit())

        # Warm up psutil so first CPU reading is non-zero
        psutil.cpu_percent(interval=None)

        from pynput import keyboard

        # Infrastructure
        clipboard_adapter = PyperclipRepository()
        history_repo = InMemoryHistoryRepository(max_items=20)
        clipboard_monitor = PynputMonitor()
        if self._test_mode:
            hotkey_listener = PynputHotkeyListener(
                modifier=keyboard.Key.alt, hotkey_char="b"
            )
        else:
            hotkey_listener = PynputHotkeyListener()

        # Services
        clipboard_service = ClipboardService(
            clipboard_adapter, history_repo, clipboard_monitor, hotkey_listener
        )
        monitor_service = MonitorService(PsutilCollector())
        clean_mode_service = CleanModeService(XinputKeyboardController())

        # Clipboard UI window
        self.clipboard_ui = ClipboardWindow(
            clipboard_service, test_mode=self._test_mode
        )
        clipboard_service.set_activate_callback(
            lambda: self.clipboard_ui.refresh()
        )
        clipboard_service.start()

        # Main system monitor window
        self.main_window_obj = MainWindow(
            monitor_service, clean_mode_service, test_mode=self._test_mode
        )

        self.hold()


def main():
    """Parse arguments, create application, and run the GTK main loop."""
    argv = [arg for arg in sys.argv if arg != "--test"]
    test_mode = "--test" in sys.argv
    app = SysmonApplication(test_mode=test_mode)
    exit_status = app.run(argv)
    sys.exit(exit_status)


if __name__ == "__main__":
    main()
