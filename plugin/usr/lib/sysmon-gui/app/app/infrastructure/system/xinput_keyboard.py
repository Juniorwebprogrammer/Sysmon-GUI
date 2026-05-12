import re
import subprocess

from app.application.ports.keyboard_controller import KeyboardController


class XinputKeyboardController(KeyboardController):
    """Enables/disables physical keyboards via xinput property changes."""

    def set_enabled(self, enabled: bool) -> bool:
        """Set 'Device Enabled' property on all detected keyboards via xinput."""
        try:
            xinput_output = subprocess.check_output(["xinput", "list"], text=True)
            lines = xinput_output.split("\n")
            keyboard_ids: list[str] = []

            for line in lines:
                if "keyboard" in line.lower() and "virtual core" not in line.lower():
                    match = re.search(r"id=(\d+)", line)
                    if match:
                        keyboard_ids.append(match.group(1))

            if not keyboard_ids:
                print("No keyboard IDs found.")
                return False

            device_status = "1" if enabled else "0"
            for keyboard_id in keyboard_ids:
                subprocess.run(
                    ["xinput", "set-prop", keyboard_id, "Device Enabled", device_status],
                    check=False,
                )
            return True
        except Exception as error:
            print(f"Error changing keyboard state: {error}")
            return False
