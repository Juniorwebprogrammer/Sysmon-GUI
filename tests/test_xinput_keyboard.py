from unittest.mock import MagicMock, patch

import pytest

from app.infrastructure.system.xinput_keyboard import XinputKeyboardController


class TestXinputKeyboardController:
    @pytest.fixture
    def controller(self):
        return XinputKeyboardController()

    def test_set_enabled_true_calls_xinput_enable(self, controller):
        with patch(
            "app.infrastructure.system.xinput_keyboard.subprocess"
        ) as mock_subprocess:
            mock_subprocess.check_output.return_value = (
                "id=10  AT Translated Set 2 keyboard\n"
            )
            mock_subprocess.run = MagicMock()

            controller.set_enabled(True)

            mock_subprocess.check_output.assert_called_once()
            mock_subprocess.run.assert_called_once()
            call_args = mock_subprocess.run.call_args[0][0]
            assert "xinput" in call_args
            assert "Device Enabled" in call_args
            assert "1" in call_args

    def test_set_enabled_false_calls_xinput_disable(self, controller):
        with patch(
            "app.infrastructure.system.xinput_keyboard.subprocess"
        ) as mock_subprocess:
            mock_subprocess.check_output.return_value = (
                "id=10  AT Translated Set 2 keyboard\n"
            )
            mock_subprocess.run = MagicMock()

            controller.set_enabled(False)

            mock_subprocess.run.assert_called_once()
            call_args = mock_subprocess.run.call_args[0][0]
            assert "xinput" in call_args
            assert "Device Enabled" in call_args
            assert "0" in call_args

    def test_set_enabled_handles_multiple_keyboards(self, controller):
        with patch(
            "app.infrastructure.system.xinput_keyboard.subprocess"
        ) as mock_subprocess:
            mock_subprocess.check_output.return_value = (
                "id=10  AT Translated Set 2 keyboard\nid=12  USB Keyboard\n"
            )
            mock_subprocess.run = MagicMock()

            controller.set_enabled(True)

            assert mock_subprocess.run.call_count == 2
            first_call_args = mock_subprocess.run.call_args_list[0][0][0]
            second_call_args = mock_subprocess.run.call_args_list[1][0][0]
            assert "10" in first_call_args
            assert "12" in second_call_args

    def test_set_enabled_returns_true_on_success(self, controller):
        with patch(
            "app.infrastructure.system.xinput_keyboard.subprocess"
        ) as mock_subprocess:
            mock_subprocess.check_output.return_value = (
                "id=10  AT Translated Set 2 keyboard\n"
            )
            mock_subprocess.run = MagicMock()

            assert controller.set_enabled(True) is True

    def test_set_enabled_returns_false_on_failure(self, controller):
        with patch(
            "app.infrastructure.system.xinput_keyboard.subprocess"
        ) as mock_subprocess:
            mock_subprocess.check_output.return_value = (
                "id=10  AT Translated Set 2 keyboard\n"
            )
            mock_subprocess.run.side_effect = Exception("xinput error")

            assert controller.set_enabled(True) is False

    def test_set_enabled_returns_false_when_no_keyboard(self, controller):
        with patch(
            "app.infrastructure.system.xinput_keyboard.subprocess"
        ) as mock_subprocess:
            mock_subprocess.check_output.return_value = ""

            assert controller.set_enabled(True) is False
