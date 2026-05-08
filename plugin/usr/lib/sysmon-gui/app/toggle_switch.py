import math
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import cairo


class ToggleSwitch(Gtk.DrawingArea):
    """
    On/off switch drawn with Cairo.
    Emits the 'toggled' signal when state changes.
    Usage:
        sw = ToggleSwitch()
        sw.connect('toggled', lambda w, state: print(state))
    """

    __gsignals__ = {
        "toggled": (
            # GObject.SignalFlags.RUN_FIRST, None, (bool,)
            # Defined manually to avoid importing GObject here
            0,           # RUN_FIRST
            None,        # return type
            (bool,),     # param types
        ),
    }

    # Colors
    _ON_TRACK   = (0.0,  0.75, 0.85)   # cyan
    _OFF_TRACK  = (0.25, 0.25, 0.25)
    _THUMB      = (1.0,  1.0,  1.0)
    _W, _H      = 48, 26                # widget size

    def __init__(self, active=False):
        super().__init__()
        self._active = active
        self._anim   = 1.0 if active else 0.0   # 0.0 = off, 1.0 = on
        self._anim_id = None

        self.set_size_request(self._W, self._H)
        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.ENTER_NOTIFY_MASK |
            Gdk.EventMask.LEAVE_NOTIFY_MASK
        )
        self.connect("draw",                self._on_draw)
        self.connect("button-press-event",  self._on_click)

    # ── Public API ────────────────────────────────────────────────────
    def get_active(self):
        return self._active

    def set_active(self, value, emit=False):
        if value == self._active:
            return
        self._active = value
        self._start_anim()
        if emit:
            self.emit("toggled", self._active)

    # ── Interaction ──────────────────────────────────────────────────
    def _on_click(self, widget, event):
        self.set_active(not self._active, emit=True)

    # ── Animation ────────────────────────────────────────────────────
    def _start_anim(self):
        if self._anim_id:
            from gi.repository import GLib
            GLib.source_remove(self._anim_id)
        from gi.repository import GLib
        self._anim_id = GLib.timeout_add(16, self._step_anim)

    def _step_anim(self):
        from gi.repository import GLib
        target = 1.0 if self._active else 0.0
        step   = 0.12
        diff   = target - self._anim
        if abs(diff) < step:
            self._anim    = target
            self._anim_id = None
            self.queue_draw()
            return False          # stop timer
        self._anim += step if diff > 0 else -step
        self.queue_draw()
        return True               # continue

    # ── Dibujo ───────────────────────────────────────────────────────
    def _on_draw(self, widget, cr):
        w = self._W
        h = self._H
        r = h / 2          # track radius

        # ---- track ----
        t = self._anim     # 0…1
        tr, tg, tb = self._ON_TRACK
        fr, fg, fb = self._OFF_TRACK
        cr.set_source_rgb(
            fr + (tr - fr) * t,
            fg + (tg - fg) * t,
            fb + (tb - fb) * t,
        )
        self._rounded_rect(cr, 0, 0, w, h, r)
        cr.fill()

        # ---- subtle border ----
        cr.set_source_rgba(1, 1, 1, 0.10)
        cr.set_line_width(0.8)
        self._rounded_rect(cr, 0, 0, w, h, r)
        cr.stroke()

        # ---- thumb ----
        pad    = 3
        travel = w - h          # how far the thumb moves
        tx     = pad + r - pad + travel * self._anim
        ty     = h / 2
        tr_    = r - pad

        cr.set_source_rgb(*self._THUMB)
        cr.arc(tx, ty, tr_, 0, 2 * math.pi)
        cr.fill()

        # subtle shadow on thumb
        cr.set_source_rgba(0, 0, 0, 0.20)
        cr.set_line_width(0.5)
        cr.arc(tx, ty, tr_, 0, 2 * math.pi)
        cr.stroke()

    @staticmethod
    def _rounded_rect(cr, x, y, w, h, r):
        cr.new_sub_path()
        cr.arc(x + r,     y + r,     r, math.pi,       1.5 * math.pi)
        cr.arc(x + w - r, y + r,     r, 1.5 * math.pi, 0)
        cr.arc(x + w - r, y + h - r, r, 0,              0.5 * math.pi)
        cr.arc(x + r,     y + h - r, r, 0.5 * math.pi, math.pi)
        cr.close_path()