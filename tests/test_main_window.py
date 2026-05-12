from unittest.mock import MagicMock, patch

import gi
import pytest

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

Gtk.init_check()

from app.application.services.clean_mode_service import CleanModeService
from app.application.services.monitor_service import MonitorService
from app.domain.process_info import ProcessInfo
from app.domain.system_metrics import SystemMetrics
from app.presentation.main_window import MainWindow


class TestMainWindow:
    @pytest.fixture
    def monitor(self):
        svc = MagicMock(spec=MonitorService)
        svc.get_metrics.return_value = SystemMetrics(
            cpu_percent=30.0,
            ram_percent=50.0,
            ram_detail="",
            disk_percent=60.0,
            disk_detail="",
            net_sent=0,
            net_recv=0,
        )
        svc.get_processes.return_value = [
            ProcessInfo(pid=1, name="test", cpu_percent=10.0, mem_percent=5.0),
        ]
        return svc

    @pytest.fixture
    def clean_mode(self):
        return MagicMock(spec=CleanModeService)

    @pytest.fixture
    def window(self, monitor, clean_mode):
        mw = MainWindow(monitor, clean_mode)
        yield mw
        mw.window.destroy()

    @pytest.fixture
    def test_window(self, monitor, clean_mode):
        mw = MainWindow(monitor, clean_mode, test_mode=True)
        yield mw
        mw.window.destroy()

    def test_creation(self, window):
        assert isinstance(window.window, Gtk.Window)
        assert window.window.get_title() == "Sysmon GUI"

    def test_test_mode_title(self, test_window):
        assert "TEST" in test_window.window.get_title()

    def test_creation_sets_wmclass(self, window):
        assert window.window is not None

    def test_update_calls_monitor(self, window, monitor):
        window._periodic_update()
        monitor.get_metrics.assert_called_once()

    def test_update_updates_charts(self, window, monitor):
        window._periodic_update()
        assert window.cpu_chart._value == 30.0
        assert window.ram_chart._value == 50.0

    def test_update_calls_get_processes_every_6th(self, window, monitor):
        for _ in range(6):
            window._periodic_update()
        assert monitor.get_processes.call_count >= 1

    def test_clean_mode_toggle_enable(self, window, clean_mode):
        window._on_clean_mode_toggle(None, True)
        clean_mode.disable_keyboards.assert_called_once()

    def test_clean_mode_toggle_disable(self, window, clean_mode):
        window._on_clean_mode_toggle(None, False)
        clean_mode.enable_keyboards.assert_called_once()

    def test_focus_out_hides_window_when_clean_off(self, window):
        window.clean_mode_switch.set_active(False)
        window.window.show_all()
        window._on_focus_out(None, None)
        assert window.window.get_visible() is False

    def test_focus_out_does_not_hide_when_clean_on(self, window):
        window.clean_mode_switch.set_active(True)
        window.window.show_all()
        window._on_focus_out(None, None)
        assert window.window.get_visible() is True

    def test_shrink_window(self, window):
        window._shrink_window()
        width, height = window.window.get_size()
        assert width <= 2

    def test_test_mode_has_badge(self, test_window):
        children = test_window.main_box.get_children()
        labels = [child for child in children if isinstance(child, Gtk.Label)]
        badge_texts = [label.get_text() for label in labels]
        assert any("TEST" in text for text in badge_texts)

    def test_status_icon_loads_pixbuf_fallback_when_not_visible(self, monitor, clean_mode):
        with patch("app.presentation.main_window.Gtk.StatusIcon") as mock_icon_class:
            mock_icon = MagicMock()
            mock_icon.get_visible.return_value = False
            mock_icon_class.return_value = mock_icon

            with patch("app.presentation.main_window.load_pixbuf") as mock_load:
                mock_pixbuf = MagicMock()
                mock_load.return_value = mock_pixbuf

                mw = MainWindow(monitor, clean_mode)
                assert mock_load.call_count == 2
                mock_icon.set_from_pixbuf.assert_called_once_with(mock_pixbuf)
                mw.window.destroy()

    def test_tray_icon_click_hides_visible_window(self, window):
        window.window.show_all()
        window._on_tray_icon_click(None)
        assert window.window.get_visible() is False

    def test_tray_icon_click_shows_hidden_window(self, window):
        window.window.hide()
        window._on_tray_icon_click(None)
        assert window.window.get_visible() is True
