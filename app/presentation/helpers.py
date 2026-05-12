import os

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gdk, GdkPixbuf, Gtk

_INSTALLED_ICON_PATH = "/usr/share/icons/hicolor/256x256/apps/sysmon-gui.png"


def _find_project_root() -> str:
    """Return the absolute path of the project root (three levels up from this file)."""
    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )


def icon_path() -> str:
    """Return the path to the application icon (installed or local fallback)."""
    local_icon = os.path.join(_find_project_root(), "icon.png")
    return _INSTALLED_ICON_PATH if os.path.exists(_INSTALLED_ICON_PATH) else local_icon


def load_pixbuf(size: int = 256):
    """Load the application icon as a GdkPixbuf.Pixbuf at the requested size."""
    path = icon_path()
    try:
        return GdkPixbuf.Pixbuf.new_from_file_at_size(path, size, size)
    except Exception as error:
        print(f"[sysmon] Could not load {path}: {error}")
        return None


def load_css(css_data: bytes, priority: int = 800) -> None:
    """Register a global Gtk CSS provider from raw bytes."""
    css_provider = Gtk.CssProvider()
    css_provider.load_from_data(css_data)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), css_provider, priority
    )
