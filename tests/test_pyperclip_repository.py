from unittest.mock import MagicMock, patch

import pytest

from app.infrastructure.clipboard.pyperclip_repository import PyperclipRepository


class TestPyperclipRepository:
    @pytest.fixture
    def repository(self):
        return PyperclipRepository()

    def test_copy_calls_pyperclip(self, repository):
        with patch(
            "app.infrastructure.clipboard.pyperclip_repository.pyperclip"
        ) as mock_pyperclip:
            repository.copy("test text")
            mock_pyperclip.copy.assert_called_once_with("test text")

    def test_paste_calls_pyperclip_and_keyboard(self, repository):
        with (
            patch(
                "app.infrastructure.clipboard.pyperclip_repository.pyperclip"
            ) as mock_pyperclip,
            patch(
                "app.infrastructure.clipboard.pyperclip_repository.keyboard.Controller"
            ) as mock_controller,
        ):
            mock_controller_instance = MagicMock()
            mock_controller.return_value = mock_controller_instance

            repository.paste("test text")

            mock_pyperclip.copy.assert_called_once_with("test text")

    def test_paste_uses_passed_text(self, repository):
        with (
            patch(
                "app.infrastructure.clipboard.pyperclip_repository.pyperclip"
            ) as mock_pyperclip,
            patch(
                "app.infrastructure.clipboard.pyperclip_repository.keyboard.Controller"
            ) as mock_controller,
        ):
            mock_controller_instance = MagicMock()
            mock_controller.return_value = mock_controller_instance

            repository.paste("custom text")

            mock_pyperclip.copy.assert_called_once_with("custom text")

    def test_paste_do_paste_triggers_keyboard(self):
        with (
            patch(
                "app.infrastructure.clipboard.pyperclip_repository.keyboard.Controller"
            ) as mock_controller,
            patch(
                "app.infrastructure.clipboard.pyperclip_repository.threading.Thread"
            ) as mock_thread,
        ):
            mock_controller_instance = MagicMock()
            mock_controller.return_value = mock_controller_instance
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance

            repository = PyperclipRepository()
            repository.paste("text")

            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()
            target_function = mock_thread.call_args[1]["target"]
            target_function()
            assert mock_controller_instance.press.call_count >= 2
            assert mock_controller_instance.release.call_count >= 2
