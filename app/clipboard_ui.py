import os
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

_INSTALLED = "/usr/share/icons/hicolor/256x256/apps/sysmon-gui.png"
_LOCAL     = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.png")
ICON_PATH  = _INSTALLED if os.path.exists(_INSTALLED) else _LOCAL


def _load_pixbuf(path, size=256):
    try:
        return GdkPixbuf.Pixbuf.new_from_file_at_size(path, size, size)
    except Exception as e:
        print(f"[clipboard] Could not load icon: {e}")
        return None


class ClipboardCard(Gtk.ListBoxRow):
    def __init__(self, text, app_name):
        super().__init__()
        self.full_text = text
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_border_width(10)

        icon_name = "text-x-generic"
        app_l = app_name.lower()
        if "code"     in app_l: icon_name = "com.visualstudio.code"
        elif "chrome"  in app_l: icon_name = "google-chrome"
        elif "firefox" in app_l: icon_name = "firefox"
        elif "terminal" in app_l: icon_name = "utilities-terminal"

        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DND)
        box.pack_start(icon, False, False, 0)

        lbl = Gtk.Label(label=text.replace("\n", " ").strip()[:60])
        lbl.set_xalign(0)
        lbl.set_ellipsize(3)
        lbl.get_style_context().add_class("card-text")
        box.pack_start(lbl, True, True, 0)
        self.add(box)


class ClipboardWindow(Gtk.Window):
    def __init__(self, engine):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.engine = engine

        self.set_wmclass("sysmon-gui", "sysmon-gui")
        self.set_icon_name("sysmon-gui")
        
        self.set_role("clipboard-manager")
        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(550, 500)
        self.set_skip_taskbar_hint(False) 
        # Window icon (appears in alt+tab and taskbar)
        pb = _load_pixbuf(ICON_PATH)
        if pb:
            self.set_icon(pb)

        Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", True)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.main_box.get_style_context().add_class("window-bg")
        self.add(self.main_box)

        # Search
        header = Gtk.Box(spacing=10)
        header.set_border_width(15)
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search history...")
        self.search_entry.connect("changed", self._on_search)
        header.pack_start(self.search_entry, True, True, 0)
        self.main_box.pack_start(header, False, False, 0)

        # List
        self.listbox = Gtk.ListBox()
        self.listbox.connect("row-activated", self._on_row_clicked)
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.listbox)
        self.main_box.pack_start(scroll, True, True, 0)

        self.connect("key-press-event", self._on_global_key)
        self._apply_styles()

    def _on_global_key(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.hide()
            return True
        return False

    def _on_row_clicked(self, lb, row):
        self.hide()
        self.engine.paste_item(row.full_text)

    def refresh(self):
        self.search_entry.set_text("")
        self._load_cards()
        self.show_all()
        self.present()
        self.search_entry.grab_focus()

    def _load_cards(self, q=""):
        for c in self.listbox.get_children():
            self.listbox.remove(c)
        for text, app in self.engine.history:
            if q.lower() in text.lower() or q.lower() in app.lower():
                self.listbox.add(ClipboardCard(text, app))
        self.show_all()

    def _on_search(self, entry):
        self._load_cards(entry.get_text())

    def _apply_styles(self):
        css = Gtk.CssProvider()
        css.load_from_data(b"""
            .window-bg { background: #121212; border-radius: 12px; border: 1px solid #333; }
            entry { background: #1e1e1e; color: white; border-radius: 8px; padding: 8px; }
            row { background: #1a1a1a; margin: 2px 10px; border-radius: 6px; }
            row:selected { background: #00f2ff; }
            row:selected .card-text { color: #000; font-weight: bold; }
            .card-text { color: #eee; }
        """)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css, 800)