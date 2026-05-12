from unittest.mock import Mock

import pytest

from app.application.services.monitor_service import MonitorService
from app.domain.process_info import ProcessInfo
from app.domain.system_metrics import SystemMetrics


class TestMonitorService:
    @pytest.fixture
    def collector(self):
        return Mock()

    @pytest.fixture
    def service(self, collector):
        return MonitorService(collector)

    def test_get_metrics_delegates(self, service, collector):
        collector.get_metrics.return_value = SystemMetrics(
            cpu_percent=50.0,
            ram_percent=60.0,
            ram_detail="",
            disk_percent=70.0,
            disk_detail="",
            net_sent=100,
            net_recv=200,
        )
        result = service.get_metrics()
        assert result.cpu_percent == 50.0
        collector.get_metrics.assert_called_once()

    def test_get_processes_delegates(self, service, collector):
        proc = ProcessInfo(pid=1, name="test", cpu_percent=10.0, mem_percent=5.0)
        collector.get_processes.return_value = [proc]
        result = service.get_processes(top_n=5)
        assert len(result) == 1
        assert result[0].name == "test"
        collector.get_processes.assert_called_once_with(top_n=5)
