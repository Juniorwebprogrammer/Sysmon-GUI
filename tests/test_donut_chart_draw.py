import cairo
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

Gtk.init_check()

from app.presentation.widgets.donut_chart import DonutChart


class TestDonutChartDraw:
    def test_on_draw_does_not_crash_with_zero_value(self):
        chart = DonutChart("CPU")
        chart.set_size_request(110, 110)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 110, 110)
        cr = cairo.Context(surface)
        chart._on_draw(chart, cr)

    def test_on_draw_with_value(self):
        chart = DonutChart("RAM")
        chart.set_value(75.5)
        chart.set_size_request(110, 110)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 110, 110)
        cr = cairo.Context(surface)
        chart._on_draw(chart, cr)

    def test_on_draw_with_hover(self):
        chart = DonutChart("Disk")
        chart.set_value(50.0)
        chart.set_size_request(110, 110)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 110, 110)
        cr = cairo.Context(surface)
        chart._hovering = True
        chart._on_draw(chart, cr)

    def test_on_mouse_enter(self):
        chart = DonutChart("CPU")
        chart._on_mouse_enter(None, None)
        assert chart._hovering is True

    def test_on_mouse_leave(self):
        chart = DonutChart("CPU")
        chart._hovering = True
        chart._on_mouse_leave(None, None)
        assert chart._hovering is False
