import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')

from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

from app.charts        import DonutChart
from app.processes     import ProcessPanel
from app.toggle_switch import ToggleSwitch
from app import collector
from app.utils import set_keyboard_enabled

_INSTALLED = "/usr/share/icons/hicolor/256x256/apps/sysmon-gui.png"
_LOCAL     = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.png")
ICON_PATH  = _INSTALLED if os.path.exists(_INSTALLED) else _LOCAL


def _load_pixbuf(path, size=22):
    try:
        return GdkPixbuf.Pixbuf.new_from_file_at_size(path, size, size)
    except Exception as e:
        print(f"[sysmon] Could not load {path}: {e}")
        return None


class MainWindow:
    def __init__(self):
        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.set_wmclass("sysmon-gui", "sysmon-gui")
        self.window.set_icon_name("sysmon-gui")
        self.window.set_decorated(False)
        self.window.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.window.set_keep_above(True)
        self.window.set_skip_taskbar_hint(False)

        screen = self.window.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.window.set_visual(visual)
        self.window.set_app_paintable(True)
        self.window.connect('focus-out-event', self._on_focus_out)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.main_box.set_border_width(18)
        self.main_box.get_style_context().add_class('glass-panel')
        self.window.add(self.main_box)

        charts_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.cpu  = DonutChart('CPU')
        self.ram  = DonutChart('RAM')
        self.disk = DonutChart('Disk')
        for chart in [self.cpu, self.ram, self.disk]:
            charts_box.pack_start(chart, True, True, 0)
        self.main_box.pack_start(charts_box, False, False, 0)

        clean_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        clean_row.set_margin_start(15)
        clean_row.set_margin_end(15)
        clean_row.set_margin_top(12)
        clean_row.set_margin_bottom(12)

        lbl_clean = Gtk.Label(label='CLEAN MODE')
        lbl_clean.set_xalign(0)
        lbl_clean.get_style_context().add_class('clean-label')

        self.kb_switch = ToggleSwitch(active=False)
        self.kb_switch.set_valign(Gtk.Align.CENTER)
        self.kb_switch.set_margin_start(12)
        self.kb_switch.connect('toggled', self._on_kb_toggle)

        clean_row.pack_start(lbl_clean, True, True, 0)
        clean_row.pack_end(self.kb_switch, False, False, 0)
        self.main_box.pack_start(clean_row, False, False, 0)

        self.proc_panel = ProcessPanel(on_resize_callback=self._shrink_window)
        self.main_box.pack_start(self.proc_panel, True, True, 0)

        self._apply_styles()

        self.status_icon = Gtk.StatusIcon()
        self.status_icon.set_from_icon_name("sysmon-gui")
        icon_pb = _load_pixbuf(ICON_PATH, size=22)
        if not self.status_icon.get_visible():
            icon_pb = _load_pixbuf(ICON_PATH, size=22)
            if icon_pb:
                self.status_icon.set_from_pixbuf(icon_pb)
        self.status_icon.set_tooltip_text("System Monitor")
        self.status_icon.connect('activate', self._on_icon_click)

        self.update_count = 0
        GLib.timeout_add(1000, self._update)

    def _on_focus_out(self, widget, event):
        if not self.kb_switch.get_active():
            self.window.hide()

    def _shrink_window(self):
        self.window.resize(1, 1)
        return False

    def _on_kb_toggle(self, switch, state):
        success = set_keyboard_enabled(enabled=not state)
        if success:
            if state:
                self.main_box.get_style_context().add_class('warning-mode')
            else:
                self.main_box.get_style_context().remove_class('warning-mode')

    def _on_icon_click(self, icon):
        if self.window.get_visible():
            self.window.hide()
        else:
            display = Gdk.Display.get_default()
            pointer = display.get_device_manager().get_client_pointer()
            _, x, y = pointer.get_position()
            self._shrink_window()
            self.window.move(x - 180, y + 15)
            self.window.show_all()

    def _update(self):
        metrics = collector.get_metrics()
        self.cpu.set_value(metrics['cpu']['value'])
        self.ram.set_value(metrics['ram']['value'])
        self.disk.set_value(metrics['disk']['value'])
        if self.update_count % 6 == 0:
            self.proc_panel.update(collector.get_processes(n=8))
        self.update_count += 1
        return True

    def _apply_styles(self):
        css = Gtk.CssProvider()
        css.load_from_data(
            b'.glass-panel {'
            b'  background-color: rgba(20,20,20,0.88);'
            b'  border-radius: 20px;'
            b'  border: 1px solid rgba(255,255,255,0.12);'
            b'}'
            b'.warning-mode {'
            b'  background-color: rgba(60,10,10,0.92);'
            b'  border: 1px solid rgba(255,50,50,0.5);'
            b'}'
            b'.clean-label {'
            b'  color: #ffffff;'
            b'  font-size: 10.5pt;'
            b'  font-weight: bold;'
            b'  letter-spacing: 0.8px;'
            b'}'
            b'button {'
            b'  color: #ffffff;'
            b'  background: rgba(255,255,255,0.08);'
            b'  border-radius: 8px;'
            b'}'
            b'treeview { color: #dddddd; font-size: 10pt; }'
        )
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css, 800
        )


if __name__ == '__main__':
    app = MainWindow()
    app.window.connect('destroy', Gtk.main_quit)
    Gtk.main()