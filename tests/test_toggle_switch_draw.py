import cairo
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

Gtk.init_check()

from app.presentation.widgets.toggle_switch import ToggleSwitch


class TestToggleSwitchDraw:
    def test_on_draw_off(self):
        switch = ToggleSwitch(active=False)
        switch.set_size_request(48, 26)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 48, 26)
        cr = cairo.Context(surface)
        switch._on_draw(switch, cr)

    def test_on_draw_on(self):
        switch = ToggleSwitch(active=True)
        switch.set_size_request(48, 26)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 48, 26)
        cr = cairo.Context(surface)
        switch._on_draw(switch, cr)

    def test_step_animation_towards_on(self):
        switch = ToggleSwitch(active=False)
        switch._animation_progress = 0.0
        switch.set_active(True)
        result = switch._step_animation()
        assert switch._animation_progress > 0.0
        assert result is True

    def test_step_animation_towards_off(self):
        switch = ToggleSwitch(active=True)
        switch._animation_progress = 1.0
        switch.set_active(False)
        result = switch._step_animation()
        assert switch._animation_progress < 1.0
        assert result is True

    def test_step_animation_reaches_target(self):
        switch = ToggleSwitch(active=False)
        switch._animation_progress = 0.95
        switch.set_active(True)
        result = switch._step_animation()
        assert switch._animation_progress == 1.0
        assert result is False

    def test_rounded_rect(self):
        switch = ToggleSwitch()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 48, 26)
        cr = cairo.Context(surface)
        switch._rounded_rect(cr, 0, 0, 48, 26, 13)
