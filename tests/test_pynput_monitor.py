from unittest.mock import MagicMock, patch

import pytest
from pynput import keyboard

from app.infrastructure.clipboard.pynput_monitor import PynputHotkeyListener, PynputMonitor


class TestPynputMonitor:
    @pytest.fixture
    def monitor(self):
        return PynputMonitor()

    def test_start_starts_thread(self, monitor):
        with patch("app.infrastructure.clipboard.pynput_monitor.threading") as mock_threading:
            mock_threading.Thread = MagicMock()
            monitor.start(on_change=lambda text, app: None)
            mock_threading.Thread.assert_called_once()
            mock_threading.Thread.return_value.start.assert_called_once()

    def test_stop_sets_running_false(self, monitor):
        monitor.start(on_change=lambda text, app: None)
        monitor.stop()
        assert monitor._running is False

    def test_get_active_app_returns_app_name(self, monitor):
        with patch(
            "app.infrastructure.clipboard.pynput_monitor.subprocess"
        ) as mock_subprocess:
            mock_subprocess.check_output.side_effect = [
                "123",
                '"WM_CLASS": "firefox"',
            ]
            result = monitor._get_active_app()
            assert result == "firefox"

    def test_get_active_app_returns_system_on_error(self, monitor):
        with patch(
            "app.infrastructure.clipboard.pynput_monitor.subprocess"
        ) as mock_subprocess:
            mock_subprocess.check_output.side_effect = Exception("xdotool error")
            result = monitor._get_active_app()
            assert result == "system"

    def test_monitor_clipboard_detects_change(self, monitor):
        captured_results = []
        monitor._running = True

        def on_change(text, app):
            captured_results.append((text, app))
            monitor._running = False

        with patch("app.infrastructure.clipboard.pynput_monitor.pyperclip") as mock_pyperclip:
            mock_pyperclip.paste.side_effect = ["hello", "hello"]
            with patch.object(monitor, "_get_active_app", return_value="test_app"):
                monitor._monitor_clipboard(on_change)

        assert len(captured_results) == 1
        assert captured_results[0] == ("hello", "test_app")

    def test_monitor_clipboard_skips_unchanged(self, monitor):
        captured_results = []
        monitor._running = True

        def on_change(text, app):
            captured_results.append((text, app))
            monitor._running = False

        with patch("app.infrastructure.clipboard.pynput_monitor.pyperclip") as mock_pyperclip:
            mock_pyperclip.paste.return_value = "same"
            with patch.object(monitor, "_get_active_app", return_value="test_app"):
                monitor._monitor_clipboard(on_change)

        assert len(captured_results) == 1
        monitor._running = False

    def test_monitor_clipboard_handles_exception(self, monitor):
        monitor._running = True
        with patch("app.infrastructure.clipboard.pynput_monitor.pyperclip") as mock_pyperclip:
            mock_pyperclip.paste.side_effect = Exception("clipboard error")
            with patch(
                "app.infrastructure.clipboard.pynput_monitor.time.sleep",
                side_effect=[None, KeyboardInterrupt],
            ):
                with pytest.raises(KeyboardInterrupt):
                    monitor._monitor_clipboard(lambda text, app: None)
        monitor._running = False


class TestPynputHotkeyListener:
    @pytest.fixture
    def listener(self):
        return PynputHotkeyListener()

    def test_default_hotkey_is_alt_v(self, listener):
        assert listener._modifier == keyboard.Key.alt
        assert listener._hotkey_char == "v"

    def test_custom_hotkey(self):
        listener = PynputHotkeyListener(
            modifier=keyboard.Key.alt, hotkey_char="b"
        )
        assert listener._hotkey_char == "b"

    def test_start_starts_thread(self, listener):
        with patch("app.infrastructure.clipboard.pynput_monitor.threading") as mock_threading:
            mock_threading.Thread = MagicMock()
            listener.start(on_activate=lambda: None)
            mock_threading.Thread.assert_called_once()
            mock_threading.Thread.return_value.start.assert_called_once()

    def test_on_press_alt_triggers_modifier(self, listener):
        listener._on_press(keyboard.Key.alt)
        assert listener._mod_pressed is True

    def test_on_press_hotkey_with_alt_calls_callback(self, listener):
        callback = MagicMock()
        listener._on_activate = callback
        listener._mod_pressed = True
        with patch("app.infrastructure.clipboard.pynput_monitor.GLib") as mock_glib:
            listener._on_press(keyboard.KeyCode.from_char("v"))
            mock_glib.idle_add.assert_called_once_with(callback)

    def test_on_press_hotkey_without_alt_does_nothing(self, listener):
        callback = MagicMock()
        listener._on_activate = callback
        listener._mod_pressed = False
        with patch("app.infrastructure.clipboard.pynput_monitor.GLib") as mock_glib:
            listener._on_press(keyboard.KeyCode.from_char("v"))
            mock_glib.idle_add.assert_not_called()

    def test_on_release_alt_clears_modifier(self, listener):
        listener._mod_pressed = True
        listener._on_release(keyboard.Key.alt)
        assert listener._mod_pressed is False

    def test_on_release_alt_l_clears_modifier(self, listener):
        listener._mod_pressed = True
        listener._on_release(keyboard.Key.alt_l)
        assert listener._mod_pressed is False

    def test_on_press_alt_l_sets_modifier(self, listener):
        listener._on_press(keyboard.Key.alt_l)
        assert listener._mod_pressed is True

    def test_non_alt_non_char_key_does_nothing(self, listener):
        with patch("app.infrastructure.clipboard.pynput_monitor.GLib") as mock_glib:
            result = listener._on_press(keyboard.Key.enter)
            mock_glib.idle_add.assert_not_called()
            assert result is None

    def test_stop_is_noop(self, listener):
        result = listener.stop()
        assert result is None

    def test_listen_creates_keyboard_listener(self, listener):
        with patch(
            "app.infrastructure.clipboard.pynput_monitor.keyboard.Listener"
        ) as mock_listener_class:
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_listener_class.return_value = mock_instance

            mock_instance.join.side_effect = [None, KeyboardInterrupt]

            with pytest.raises(KeyboardInterrupt):
                listener._listen()

            mock_listener_class.assert_called_with(
                on_press=listener._on_press,
                on_release=listener._on_release,
            )
