import threading
import pyperclip
import subprocess
import re
from pynput import keyboard
from gi.repository import GLib

class ClipboardEngine:
    def __init__(self, on_activate_callback):
        self.history = [] 
        self.on_activate = on_activate_callback
        self.kb_controller = keyboard.Controller()
        self.alt_pressed = False # Track only Alt

    def get_active_app(self):
        try:
            wid = subprocess.check_output(["xdotool", "getactivewindow"], text=True).strip()
            res = subprocess.check_output(["xprop", "-id", wid, "WM_CLASS"], text=True)
            apps = re.findall(r'"([^"]*)"', res)
            return apps[-1].lower() if apps else "system"
        except: return "system"

    def _on_press(self, key):
        # Detect Alt
        if key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            self.alt_pressed = True
        
        # Combination: Alt + V
        if hasattr(key, 'char') and key.char == 'v' and self.alt_pressed:
            GLib.idle_add(self.on_activate)
            return False # Block the 'v' so it doesn't type anything

    def _on_release(self, key):
        if key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            self.alt_pressed = False

    def start(self):
        threading.Thread(target=self._monitor_clipboard, daemon=True).start()
        def listen():
            while True:
                with keyboard.Listener(on_press=self._on_press, on_release=self._on_release) as listener:
                    listener.join()
        threading.Thread(target=listen, daemon=True).start()

    def _monitor_clipboard(self):
        import time
        last = ""
        while True:
            try:
                curr = pyperclip.paste()
                if curr and curr != last:
                    app = self.get_active_app()
                    self.history = [h for h in self.history if h[0] != curr]
                    self.history.insert(0, (curr, app))
                    if len(self.history) > 20: self.history.pop()
                    last = curr
            except: pass
            time.sleep(0.5)

    def paste_item(self, text):
        pyperclip.copy(text)
        def do_paste():
            import time
            time.sleep(0.4) 
            self.kb_controller.press(keyboard.Key.ctrl)
            self.kb_controller.press('v')
            self.kb_controller.release('v')
            self.kb_controller.release(keyboard.Key.ctrl)
        threading.Thread(target=do_paste, daemon=True).start()