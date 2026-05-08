import subprocess
import re

def set_keyboard_enabled(enabled=True):
    try:
        # 1. Get the list of devices
        result = subprocess.check_output(["xinput", "list"], text=True)
        
        # 2. Find ALL IDs containing the word 'keyboard'
        # Ignore 'slave', 'floating' or '[disabled]'.
        # Only skip 'Virtual core' since that's the system "parent".
        lines = result.split('\n')
        kbd_ids = []
        
        for line in lines:
            if "keyboard" in line.lower() and "virtual core" not in line.lower():
                match = re.search(r"id=(\d+)", line)
                if match:
                    kbd_ids.append(match.group(1))

        if not kbd_ids:
            print("No keyboard IDs found.")
            return False

        # 3. Apply the command to each found ID
        status = "1" if enabled else "0"
        for k_id in kbd_ids:
            # Use check=False so if one fails (ghost pointer), the rest continue
            subprocess.run(["xinput", "set-prop", k_id, "Device Enabled", status], check=False)
            print(f"Device ID {k_id} -> Status: {'Enabled' if enabled else 'Disabled'}")
            
        return True
    except Exception as e:
        print(f"Error changing keyboard state: {e}")
        return False