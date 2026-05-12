import math

import cairo
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

# RGB color palette for each chart label
_CHART_COLORS = {
    "CPU": (0.0, 0.9, 1.0),
    "RAM": (0.7, 0.4, 1.0),
    "Disk": (1.0, 0.4, 0.4),
}


class DonutChart(Gtk.DrawingArea):
    """A circular donut chart widget that displays a percentage value."""

    def __init__(self, label="CPU", size=110):
        super().__init__()
        self._label = label
        self._value = 0.0
        self._hovering = False
        self._color = _CHART_COLORS.get(label, (0.4, 0.4, 0.4))
        self.set_size_request(size, size)

        self.add_events(
            Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK
        )
        self.connect("enter-notify-event", self._on_mouse_enter)
        self.connect("leave-notify-event", self._on_mouse_leave)
        self.connect("draw", self._on_draw)

    def set_value(self, value):
        """Update the displayed percentage and trigger a redraw."""
        self._value = value
        self.queue_draw()

    def _on_mouse_enter(self, widget, event):
        """Show the numeric percentage on hover."""
        self._hovering = True
        self.queue_draw()

    def _on_mouse_leave(self, widget, event):
        """Hide the numeric percentage when not hovering."""
        self._hovering = False
        self.queue_draw()

    def _on_draw(self, widget, cr):
        """Render the donut chart: background arc, foreground arc, label text."""
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 10

        # Background track
        cr.set_line_width(7)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_source_rgba(1, 1, 1, 0.07)
        cr.arc(center_x, center_y, radius, 0, 2 * math.pi)
        cr.stroke()

        # Value arc
        cr.set_source_rgb(*self._color)
        cr.set_line_width(8)
        cr.arc(
            center_x,
            center_y,
            radius,
            math.radians(-90),
            math.radians(-90 + (3.6 * self._value)),
        )
        cr.stroke()

        # Label text
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(12)
        cr.set_source_rgba(1, 1, 1, 0.9)
        label_extents = cr.text_extents(self._label)

        text_y = center_y + 5 if not self._hovering else center_y - 2
        cr.move_to(center_x - label_extents.width / 2, text_y)
        cr.show_text(self._label)

        # Value tooltip on hover
        if self._hovering:
            cr.set_source_rgba(1, 1, 1, 0.6)
            cr.set_font_size(11)
            value_text = f"{self._value:.0f}%"
            value_extents = cr.text_extents(value_text)
            cr.move_to(center_x - value_extents.width / 2, center_y + 14)
            cr.show_text(value_text)
