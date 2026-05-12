import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

Gtk.init_check()

from app.presentation.widgets.donut_chart import DonutChart


class TestDonutChart:
    def test_creation(self):
        chart = DonutChart("CPU")
        assert chart._label == "CPU"
        assert chart._value == 0.0

    def test_set_value(self):
        chart = DonutChart("RAM")
        chart.set_value(75.5)
        assert chart._value == 75.5

    def test_set_value_accepts_any_float(self):
        chart = DonutChart("Disk")
        chart.set_value(150.0)
        assert chart._value == 150.0

    def test_set_value_negative(self):
        chart = DonutChart("Test")
        chart.set_value(-10.0)
        assert chart._value == -10.0

    def test_multiple_charts_independent(self):
        cpu = DonutChart("CPU")
        ram = DonutChart("RAM")
        cpu.set_value(50.0)
        ram.set_value(80.0)
        assert cpu._value == 50.0
        assert ram._value == 80.0

    def test_chart_is_drawing_area(self):
        chart = DonutChart("CPU")
        assert isinstance(chart, Gtk.DrawingArea)

    def test_do_draw_does_not_crash(self):
        chart = DonutChart("CPU")
        chart.set_size_request(100, 100)
        chart.show_all()
