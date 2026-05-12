import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

Gtk.init_check()

from app.presentation.widgets.toggle_switch import ToggleSwitch


class TestToggleSwitch:
    def test_creation_default_off(self):
        sw = ToggleSwitch()
        assert sw.get_active() is False

    def test_creation_active(self):
        sw = ToggleSwitch(active=True)
        assert sw.get_active() is True

    def test_toggle_changes_state(self):
        sw = ToggleSwitch()
        sw.set_active(True)
        assert sw.get_active() is True
        sw.set_active(False)
        assert sw.get_active() is False

    def test_toggle_emits_signal(self):
        sw = ToggleSwitch()
        results = []
        sw.connect("toggled", lambda w, s: results.append(s))
        sw.set_active(True, emit=True)
        assert len(results) == 1
        assert results[0] is True

    def test_toggle_emits_signal_on_click(self):
        sw = ToggleSwitch()
        results = []
        sw.connect("toggled", lambda w, s: results.append(s))
        sw._on_click(None, None)
        assert len(results) == 1

    def test_widget_is_drawing_area(self):
        sw = ToggleSwitch()
        assert isinstance(sw, Gtk.DrawingArea)

    def test_do_draw_does_not_crash(self):
        sw = ToggleSwitch()
        sw.set_size_request(50, 30)
        sw.show_all()
