from app.application.ports.keyboard_controller import KeyboardController


class CleanModeService:
    """Toggles keyboard input on/off (clean mode) via the system controller."""

    def __init__(self, controller: KeyboardController):
        self._controller = controller

    def disable_keyboards(self) -> bool:
        """Block all physical keyboards to prevent typing."""
        return self._controller.set_enabled(False)

    def enable_keyboards(self) -> bool:
        """Restore physical keyboard input."""
        return self._controller.set_enabled(True)
