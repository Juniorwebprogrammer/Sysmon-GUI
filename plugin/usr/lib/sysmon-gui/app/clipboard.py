import threading
import time
import pyperclip
from gi.repository import GLib

class ClipboardManager:
    def __init__(self, max_items=20):
        self.history = []
        self.max_items = max_items
        self.last_item = ""
        
    def start_monitoring(self):
        thread = threading.Thread(target=self._monitor, daemon=True)
        thread.start()

    def _monitor(self):
        while True:
            try:
                current_item = pyperclip.paste()
                if current_item and current_item != self.last_item:
                    self.last_item = current_item
                    # Insert at the beginning
                    if current_item in self.history:
                        self.history.remove(current_item)
                    self.history.insert(0, current_item)
                    
                    if len(self.history) > self.max_items:
                        self.history.pop()
            except:
                pass
            time.sleep(0.5) # Scan every half second

    def get_history(self, filter_text=""):
        if not filter_text:
            return self.history
        return [item for item in self.history if filter_text.lower() in item.lower()]