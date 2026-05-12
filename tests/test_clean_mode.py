from unittest.mock import Mock

import pytest

from app.application.services.clean_mode_service import CleanModeService


class TestCleanModeService:
    @pytest.fixture
    def controller(self):
        return Mock()

    @pytest.fixture
    def service(self, controller):
        return CleanModeService(controller)

    def test_disable_keyboards(self, service, controller):
        service.disable_keyboards()
        controller.set_enabled.assert_called_once_with(False)

    def test_enable_keyboards(self, service, controller):
        service.enable_keyboards()
        controller.set_enabled.assert_called_once_with(True)

    def test_disable_returns_controller_result(self, service, controller):
        controller.set_enabled.return_value = True
        assert service.disable_keyboards() is True

    def test_disable_returns_false_on_failure(self, service, controller):
        controller.set_enabled.return_value = False
        assert service.disable_keyboards() is False
