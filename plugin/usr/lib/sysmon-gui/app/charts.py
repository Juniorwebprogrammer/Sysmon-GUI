import math
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import cairo

COLORS = {
    "CPU":   (0.0, 0.9, 1.0),
    "RAM":   (0.7, 0.4, 1.0),
    "Disk": (1.0, 0.4, 0.4),
}

class DonutChart(Gtk.DrawingArea):
    def __init__(self, label="CPU", size=110):
        super().__init__()
        self._label = label
        self._value = 0.0
        self._hovering = False
        self._color = COLORS.get(label, (0.4, 0.4, 0.4))
        self.set_size_request(size, size)
        
        self.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
        self.connect("enter-notify-event", self._on_hover_in)
        self.connect("leave-notify-event", self._on_hover_out)
        self.connect("draw", self._on_draw)

    def set_value(self, value):
        self._value = value
        self.queue_draw()

    def _on_hover_in(self, widget, event):
        self._hovering = True
        self.queue_draw()

    def _on_hover_out(self, widget, event):
        self._hovering = False
        self.queue_draw()

    def _on_draw(self, widget, cr):
        w, h = widget.get_allocated_width(), widget.get_allocated_height()
        cx, cy = w / 2, h / 2
        r = min(w, h) / 2 - 10

        cr.set_line_width(7)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_source_rgba(1, 1, 1, 0.07) 
        cr.arc(cx, cy, r, 0, 2 * math.pi)
        cr.stroke()

        cr.set_source_rgb(*self._color)
        cr.set_line_width(8)
        cr.arc(cx, cy, r, math.radians(-90), math.radians(-90 + (3.6 * self._value)))
        cr.stroke()

        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(12)
        cr.set_source_rgba(1, 1, 1, 0.9)
        te = cr.text_extents(self._label)
        
        text_y = cy + 5 if not self._hovering else cy - 2
        cr.move_to(cx - te.width / 2, text_y)
        cr.show_text(self._label)

        if self._hovering:
            cr.set_source_rgba(1, 1, 1, 0.6)
            cr.set_font_size(11)
            val_txt = f"{self._value:.0f}%"
            te_v = cr.text_extents(val_txt)
            cr.move_to(cx - te_v.width / 2, cy + 14)
            cr.show_text(val_txt)