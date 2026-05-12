# Test Environment

## Problem

The application uses `Gtk.Application` with a unique `application_id` (`com.test.sysmon-gui`). GTK only allows one instance per `application_id`; attempting to open a second one merely activates the first. Additionally, the global `Alt+V` listener cannot be shared by two processes.

## Solution

A `--test` flag has been added to run a parallel instance with its own identity.

### Differences between production and test

| Aspect | Production | Test |
|---|---|---|
| Command | `python3 main.py` | `python3 main.py --test` |
| Launcher | `./run_app.sh` | `./run_test.sh` |
| App ID | `com.test.sysmon-gui` | `com.test.sysmon-gui.test` |
| Hotkey | `Alt + V` | `Alt + B` |
| Window title | Sysmon GUI | Sysmon GUI [TEST] |
| WM class | `sysmon-gui` | `sysmon-gui-test` |

### Usage

```bash
# Terminal 1: production
./run_app.sh

# Terminal 2: test (can be opened simultaneously)
./run_test.sh
```

### How it works

1. `main.py` detects `--test` in `sys.argv` and passes it to `SysmonApplication`.
2. In test mode, `application_id = "com.test.sysmon-gui.test"` is used, allowing a second independent GTK instance.
3. `PynputHotkeyListener` receives `hotkey_char="b"`, so the shortcut is `Alt+B` instead of `Alt+V`, avoiding collisions with the production instance.
4. Windows display "[TEST]" in the title to visually identify each instance.

### Notes

- `ClipboardService` and `MonitorService` can run in parallel without conflict (shared read access to clipboard and system metrics).
- `CleanModeService` (disabling keyboards) works independently in each instance — it is recommended not to use it simultaneously from both.
- Each instance maintains its own in-memory clipboard history.
