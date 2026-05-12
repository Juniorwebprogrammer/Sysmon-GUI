import warnings

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

Gtk.init_check()

warnings.filterwarnings("ignore", category=DeprecationWarning)
