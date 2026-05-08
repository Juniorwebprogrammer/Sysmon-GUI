#!/usr/bin/env python3
import gi
import sys
import os
import psutil
import signal
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from app.window import MainWindow
from app.clipboard_engine import ClipboardEngine
from app.clipboard_ui import ClipboardWindow

class SysmonApplication(Gtk.Application):
    def __init__(self):
        # The ID must be unique to prevent two instances from opening
        super().__init__(application_id="com.junior.sysmon-gui")

    def do_activate(self):
        # 1. IDENTITY: This links the process to the taskbar icon
        GLib.set_prgname("sysmon-gui")
        GLib.set_application_name("Sysmon GUI")
        
        # 2. SHUTDOWN SIGNAL: Allows the uninstaller to close the app instantly
        signal.signal(signal.SIGTERM, lambda *_: self.quit())
        signal.signal(signal.SIGINT, lambda *_: self.quit())

        psutil.cpu_percent(interval=None)

        # 3. COMPONENTS
        self.clip_engine = ClipboardEngine(on_activate_callback=lambda: self.clip_ui.refresh())
        self.clip_ui = ClipboardWindow(self.clip_engine)
        self.clip_engine.start()

        # 4. MAIN WINDOW
        self.main_window_obj = MainWindow()
        # Force the window to have the correct WM_CLASS for the Mint panel
        self.main_window_obj.window.set_wmclass("sysmon-gui", "sysmon-gui")
        
        # Keep the app alive even when no windows are visible
        self.hold()

def main():
    app = SysmonApplication()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)

if __name__ == "__main__":
    main()
