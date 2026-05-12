import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

from app.application.services.clean_mode_service import CleanModeService
from app.application.services.monitor_service import MonitorService
from app.presentation.helpers import load_css, load_pixbuf
from app.presentation.widgets.donut_chart import DonutChart
from app.presentation.widgets.process_panel import ProcessPanel
from app.presentation.widgets.toggle_switch import ToggleSwitch


class MainWindow:
    """Primary overlay window showing system metrics, clean mode toggle, and process list."""

    def __init__(
        self,
        monitor_service: MonitorService,
        clean_mode_service: CleanModeService,
        test_mode: bool = False,
    ):
        self._monitor_service = monitor_service
        self._clean_mode_service = clean_mode_service
        self._test_mode = test_mode

        # Window configuration: undecorated, always-on-top overlay
        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        wm_class = "sysmon-gui-test" if test_mode else "sysmon-gui"
        app_title = "Sysmon GUI [TEST]" if test_mode else "Sysmon GUI"
        self.window.set_wmclass(wm_class, wm_class)
        self.window.set_title(app_title)
        self.window.set_icon_name("sysmon-gui")
        self.window.set_decorated(False)
        self.window.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.window.set_keep_above(True)
        self.window.set_skip_taskbar_hint(False)

        # Enable RGBA transparency if compositor is available
        screen = self.window.get_screen()
        rgba_visual = screen.get_rgba_visual()
        if rgba_visual and screen.is_composited():
            self.window.set_visual(rgba_visual)
        self.window.set_app_paintable(True)
        self.window.connect("focus-out-event", self._on_focus_out)

        # Main vertical layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.main_box.set_border_width(18)
        self.main_box.get_style_context().add_class("glass-panel")
        self.window.add(self.main_box)

        if test_mode:
            test_badge = Gtk.Label(label="\u26a0 TEST MODE")
            test_badge.get_style_context().add_class("test-badge")
            self.main_box.pack_start(test_badge, False, False, 0)

        # Resource donut charts row
        charts_layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.cpu_chart = DonutChart("CPU")
        self.ram_chart = DonutChart("RAM")
        self.disk_chart = DonutChart("Disk")
        for chart_widget in [self.cpu_chart, self.ram_chart, self.disk_chart]:
            charts_layout.pack_start(chart_widget, True, True, 0)
        self.main_box.pack_start(charts_layout, False, False, 0)

        # Clean mode toggle row
        clean_mode_row = self._build_clean_mode_row()
        self.main_box.pack_start(clean_mode_row, False, False, 0)

        # Expandable process list panel
        self.process_panel = ProcessPanel(on_resize_callback=self._shrink_window)
        self.main_box.pack_start(self.process_panel, True, True, 0)

        self._apply_styles()
        self._setup_status_icon()
        self._update_counter = 0
        GLib.timeout_add(1000, self._periodic_update)

    def _build_clean_mode_row(self):
        """Build the row containing the CLEAN MODE label and toggle switch."""
        clean_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        clean_row.set_margin_start(15)
        clean_row.set_margin_end(15)
        clean_row.set_margin_top(12)
        clean_row.set_margin_bottom(12)

        clean_label = Gtk.Label(label="CLEAN MODE")
        clean_label.set_xalign(0)
        clean_label.get_style_context().add_class("clean-label")

        self.clean_mode_switch = ToggleSwitch(active=False)
        self.clean_mode_switch.set_valign(Gtk.Align.CENTER)
        self.clean_mode_switch.set_margin_start(12)
        self.clean_mode_switch.connect("toggled", self._on_clean_mode_toggle)

        clean_row.pack_start(clean_label, True, True, 0)
        clean_row.pack_end(self.clean_mode_switch, False, False, 0)
        return clean_row

    def _setup_status_icon(self) -> None:
        """Create the system tray icon for showing/hiding the window."""
        self.status_icon = Gtk.StatusIcon()
        self.status_icon.set_from_icon_name("sysmon-gui")
        tray_icon = load_pixbuf(size=22)
        if not self.status_icon.get_visible():
            tray_icon = load_pixbuf(size=22)
            if tray_icon:
                self.status_icon.set_from_pixbuf(tray_icon)
        self.status_icon.set_tooltip_text("System Monitor")
        self.status_icon.connect("activate", self._on_tray_icon_click)

    def _on_focus_out(self, widget: Gtk.Widget, event: Gdk.EventFocus) -> bool:
        """Hide the window when it loses focus (unless clean mode is active)."""
        if not self.clean_mode_switch.get_active():
            self.window.hide()
        return False

    def _shrink_window(self) -> bool:
        """Resize window to minimum to force recalculation around content."""
        self.window.resize(1, 1)
        return False

    def _on_clean_mode_toggle(self, switch: ToggleSwitch, state: bool) -> None:
        """Enable or disable clean mode (keyboard blocking)."""
        if state:
            self._clean_mode_service.disable_keyboards()
            self.main_box.get_style_context().add_class("warning-mode")
        else:
            self._clean_mode_service.enable_keyboards()
            self.main_box.get_style_context().remove_class("warning-mode")

    def _on_tray_icon_click(self, icon: Gtk.StatusIcon) -> None:
        """Toggle the main window visibility from the system tray."""
        if self.window.get_visible():
            self.window.hide()
        else:
            display = Gdk.Display.get_default()
            seat = display.get_default_seat()
            pointer = seat.get_pointer()
            _, pointer_x, pointer_y = pointer.get_position()
            self._shrink_window()
            self.window.move(pointer_x - 180, pointer_y + 15)
            self.window.show_all()

    def _periodic_update(self) -> bool:
        """Update charts and process list every second."""
        metrics = self._monitor_service.get_metrics()
        self.cpu_chart.set_value(metrics.cpu_percent)
        self.ram_chart.set_value(metrics.ram_percent)
        self.disk_chart.set_value(metrics.disk_percent)

        # Refresh process list every 6 seconds
        if self._update_counter % 6 == 0:
            self.process_panel.update(self._monitor_service.get_processes(top_n=8))

        self._update_counter += 1
        return True

    def _apply_styles(self) -> None:
        """Load custom CSS for the main window and its children."""
        load_css(
            b".glass-panel {"
            b"  background-color: rgba(20,20,20,0.88);"
            b"  border-radius: 20px;"
            b"  border: 1px solid rgba(255,255,255,0.12);"
            b"}"
            b".test-badge {"
            b"  color: #ff9800;"
            b"  font-size: 8pt;"
            b"  font-weight: bold;"
            b"  letter-spacing: 1px;"
            b"}"
            b".warning-mode {"
            b"  background-color: rgba(60,10,10,0.92);"
            b"  border: 1px solid rgba(255,50,50,0.5);"
            b"}"
            b".clean-label {"
            b"  color: #ffffff;"
            b"  font-size: 10.5pt;"
            b"  font-weight: bold;"
            b"  letter-spacing: 0.8px;"
            b"}"
            b"button {"
            b"  color: #ffffff;"
            b"  background: rgba(255,255,255,0.08);"
            b"  border-radius: 8px;"
            b"}"
            b"treeview { color: #dddddd; font-size: 10pt; }"
        )
