import math

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk


class ToggleSwitch(Gtk.DrawingArea):
    """A custom animated toggle switch widget with rounded track and thumb."""

    __gsignals__ = {
        "toggled": (
            0,
            None,
            (bool,),
        ),
    }

    _ON_TRACK_COLOR = (0.0, 0.75, 0.85)
    _OFF_TRACK_COLOR = (0.25, 0.25, 0.25)
    _THUMB_COLOR = (1.0, 1.0, 1.0)
    _WIDTH = 48
    _HEIGHT = 26

    def __init__(self, active=False):
        super().__init__()
        self._active = active
        self._animation_progress = 1.0 if active else 0.0
        self._animation_id = None

        self.set_size_request(self._WIDTH, self._HEIGHT)
        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.ENTER_NOTIFY_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK
        )
        self.connect("draw", self._on_draw)
        self.connect("button-press-event", self._on_click)

    def get_active(self):
        """Return whether the switch is currently toggled on."""
        return self._active

    def set_active(self, value, emit=False):
        """Set the switch state with optional signal emission."""
        if value == self._active:
            return
        self._active = value
        self._start_animation()
        if emit:
            self.emit("toggled", self._active)

    def _on_click(self, widget, event):
        """Toggle state on mouse click and emit signal."""
        self.set_active(not self._active, emit=True)

    def _start_animation(self):
        """Begin the smooth transition animation between on/off states."""
        if self._animation_id:
            GLib.source_remove(self._animation_id)
        self._animation_id = GLib.timeout_add(16, self._step_animation)

    def _step_animation(self):
        """Animate one frame toward the target state."""
        target = 1.0 if self._active else 0.0
        step_size = 0.12
        step_diff = target - self._animation_progress
        if abs(step_diff) < step_size:
            self._animation_progress = target
            self._animation_id = None
            self.queue_draw()
            return False
        self._animation_progress += step_size if step_diff > 0 else -step_size
        self.queue_draw()
        return True

    def _on_draw(self, widget, cr):
        """Render the toggle switch: track background, border, and thumb circle."""
        total_width = self._WIDTH
        total_height = self._HEIGHT
        corner_radius = total_height / 2
        progress = self._animation_progress

        # Interpolate track color between off and on
        on_r, on_g, on_b = self._ON_TRACK_COLOR
        off_r, off_g, off_b = self._OFF_TRACK_COLOR
        cr.set_source_rgb(
            off_r + (on_r - off_r) * progress,
            off_g + (on_g - off_g) * progress,
            off_b + (on_b - off_b) * progress,
        )
        self._rounded_rect(cr, 0, 0, total_width, total_height, corner_radius)
        cr.fill()

        # Thin border around track
        cr.set_source_rgba(1, 1, 1, 0.10)
        cr.set_line_width(0.8)
        self._rounded_rect(cr, 0, 0, total_width, total_height, corner_radius)
        cr.stroke()

        # Thumb position
        padding = 3
        thumb_travel = total_width - total_height
        thumb_x = padding + corner_radius - padding + thumb_travel * progress
        thumb_y = total_height / 2
        thumb_radius = corner_radius - padding

        cr.set_source_rgb(*self._THUMB_COLOR)
        cr.arc(thumb_x, thumb_y, thumb_radius, 0, 2 * math.pi)
        cr.fill()

        # Subtle thumb border
        cr.set_source_rgba(0, 0, 0, 0.20)
        cr.set_line_width(0.5)
        cr.arc(thumb_x, thumb_y, thumb_radius, 0, 2 * math.pi)
        cr.stroke()

    @staticmethod
    def _rounded_rect(cr, x, y, width, height, radius):
        """Draw a rounded rectangle path using Cairo."""
        cr.new_sub_path()
        cr.arc(x + radius, y + radius, radius, math.pi, 1.5 * math.pi)
        cr.arc(x + width - radius, y + radius, radius, 1.5 * math.pi, 0)
        cr.arc(x + width - radius, y + height - radius, radius, 0, 0.5 * math.pi)
        cr.arc(x + radius, y + height - radius, radius, 0.5 * math.pi, math.pi)
        cr.close_path()
