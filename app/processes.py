import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

class ProcessPanel(Gtk.Box):
    def __init__(self, on_resize_callback=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._on_resize = on_resize_callback
        self._expanded = False
        
        # Button taking up all space
        self._toggle_btn = Gtk.Button(label="▸ ACTIVE PROCESSES")
        self._toggle_btn.set_hexpand(True)
        self._toggle_btn.set_relief(Gtk.ReliefStyle.NONE)
        self._toggle_btn.connect("clicked", self._on_toggle)
        self._toggle_btn.get_style_context().add_class("proc-header")
        self.pack_start(self._toggle_btn, False, False, 0)

        self._revealer = Gtk.Revealer()
        scroll = Gtk.ScrolledWindow()
        scroll.set_min_content_height(160)
        
        self._store = Gtk.ListStore(int, str, float, float)
        self._tree = Gtk.TreeView(model=self._store)
        
        for i, t in enumerate(["PID", "NAME", "CPU%", "MEM%"]):
            renderer = Gtk.CellRendererText()
            renderer.set_property("foreground", "#888")
            self._tree.append_column(Gtk.TreeViewColumn(t, renderer, text=i))

        scroll.add(self._tree)
        self._revealer.add(scroll)
        self.pack_start(self._revealer, True, True, 0)
        self._apply_styles()

    def _apply_styles(self):
        css = Gtk.CssProvider()
        css.load_from_data(b"""
            .proc-header { 
                background: #1a1a1a; color: #00f2ff; border-top: 1px solid #333; 
                padding: 12px; border-radius: 0; font-weight: bold;
            }
            .proc-header:hover { background: #222; }
            treeview { background: #121212; color: #ccc; }
        """)
        self.get_style_context().add_provider(css, 800)

    def _on_toggle(self, btn):
        self._expanded = not self._expanded
        self._revealer.set_reveal_child(self._expanded)
        btn.set_label(f"{'▾' if self._expanded else '▸'} ACTIVE PROCESSES")
        if self._on_resize: GLib.timeout_add(300, self._on_resize)

    def update(self, procs):
        if self._expanded:
            self._store.clear()
            for p in procs: self._store.append([p["pid"], p["name"], p["cpu"], p["mem"]])