from collections.abc import Callable

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import GLib, Gtk

from app.domain.process_info import ProcessInfo


COLUMN_HEADERS = ["PID", "NAME", "CPU%", "MEM%"]
PID_COLUMN = 0
NAME_COLUMN = 1
CPU_COLUMN = 2
MEM_COLUMN = 3


class ProcessPanel(Gtk.Box):
    """Collapsible panel that displays a list of running processes with CPU and memory usage."""

    def __init__(self, on_resize_callback: Callable[[], bool] | None = None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._on_resize = on_resize_callback
        self._expanded = False

        # Toggle header button with arrow indicator
        self._toggle_btn = Gtk.Button(label="\u25b8 ACTIVE PROCESSES")
        self._toggle_btn.set_hexpand(True)
        self._toggle_btn.set_relief(Gtk.ReliefStyle.NONE)
        self._toggle_btn.connect("clicked", self._on_toggle)
        self._toggle_btn.get_style_context().add_class("proc-header")
        self.pack_start(self._toggle_btn, False, False, 0)

        # Revealer for animated expand/collapse
        self._revealer = Gtk.Revealer()
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_min_content_height(160)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)

        # Data model: PID (int), NAME (str), CPU% (float), MEM% (float)
        self._store = Gtk.ListStore(int, str, float, float)
        self._tree = Gtk.TreeView(model=self._store)

        # Build table columns
        for column_index, column_header in enumerate(COLUMN_HEADERS):
            text_renderer = Gtk.CellRendererText()
            text_renderer.set_property("foreground", "#888")

            # Float columns use custom formatting (2 decimal places)
            if column_index >= CPU_COLUMN:
                tree_column = Gtk.TreeViewColumn(column_header, text_renderer)
                tree_column.set_cell_data_func(
                    text_renderer, self._format_float, column_index
                )
            else:
                tree_column = Gtk.TreeViewColumn(
                    column_header, text_renderer, text=column_index
                )

            # Let the NAME column stretch to fill remaining horizontal space
            if column_index == NAME_COLUMN:
                tree_column.set_expand(True)
                tree_column.set_min_width(120)

            self._tree.append_column(tree_column)

        scrolled_window.add(self._tree)

        # Stack to toggle between loading spinner and data view
        self._stack = Gtk.Stack()
        self._stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

        # Loading indicator page
        loading_container = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=8
        )
        loading_container.set_valign(Gtk.Align.CENTER)
        self._spinner = Gtk.Spinner()
        loading_label = Gtk.Label(label="Loading processes...")
        loading_label.set_name("loading-label")
        loading_container.pack_start(self._spinner, False, False, 0)
        loading_container.pack_start(loading_label, False, False, 0)
        self._stack.add_named(loading_container, "loading")
        self._stack.add_named(scrolled_window, "data")
        self._stack.set_visible_child_name("loading")

        self._revealer.add(self._stack)
        self.pack_start(self._revealer, True, True, 0)
        self._apply_styles()

    def _apply_styles(self):
        """Load custom CSS for the panel and its children."""
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            b"""
            .proc-header {
                background: #1a1a1a; color: #00f2ff; border-top: 1px solid #333;
                padding: 12px; border-radius: 0; font-weight: bold;
            }
            .proc-header:hover { background: #222; }
            treeview { background: #121212; color: #ccc; }
            #loading-label { color: #888; font-size: 10pt; }
        """
        )
        self.get_style_context().add_provider(css_provider, 800)

    def _on_toggle(self, button: Gtk.Button) -> None:
        """Expand or collapse the process list panel."""
        self._expanded = not self._expanded
        self._revealer.set_reveal_child(self._expanded)

        arrow_symbol = "\u25be" if self._expanded else "\u25b8"
        button.set_label(f"{arrow_symbol} ACTIVE PROCESSES")

        if self._expanded:
            # Show loading indicator while waiting for process data
            self._stack.set_visible_child_name("loading")
            self._spinner.start()
        else:
            self._spinner.stop()

        # Notify parent to recalculate window size after animation
        if self._on_resize:
            GLib.timeout_add(300, self._on_resize)

    def update(self, processes: list[ProcessInfo]) -> None:
        """Refresh the process list with the latest data."""
        if self._expanded:
            self._store.clear()
            for process in processes:
                self._store.append(
                    [process.pid, process.name, process.cpu_percent, process.mem_percent]
                )
            # Switch from loading spinner to data view
            self._stack.set_visible_child_name("data")
            self._spinner.stop()

    def _format_float(
        self,
        tree_column: Gtk.TreeViewColumn,
        cell_renderer: Gtk.CellRendererText,
        tree_model: Gtk.TreeModel,
        tree_iter: Gtk.TreeIter,
        column_index: int,
    ) -> None:
        """Format a float cell to show exactly two decimal places."""
        raw_value = tree_model.get_value(tree_iter, column_index)
        cell_renderer.set_property("text", f"{raw_value:.2f}")
