from unittest.mock import MagicMock, PropertyMock, patch

import psutil

from app.domain.process_info import ProcessInfo
from app.domain.system_metrics import SystemMetrics
from app.infrastructure.system.psutil_collector import PsutilCollector


class TestDomainEntities:
    def test_system_metrics_creation(self):
        metrics = SystemMetrics(
            cpu_percent=45.5,
            ram_percent=60.0,
            ram_detail="4.0 GB / 8.0 GB",
            disk_percent=70.0,
            disk_detail="200.0 GB / 500.0 GB",
            net_sent=1000,
            net_recv=2000,
        )
        assert metrics.cpu_percent == 45.5
        assert metrics.ram_percent == 60.0
        assert metrics.net_sent == 1000

    def test_process_info_creation(self):
        proc = ProcessInfo(pid=1234, name="python3", cpu_percent=10.5, mem_percent=2.3)
        assert proc.pid == 1234
        assert proc.name == "python3"
        assert proc.cpu_percent == 10.5

    def test_process_info_sorting(self):
        procs = [
            ProcessInfo(pid=1, name="a", cpu_percent=10.0, mem_percent=5.0),
            ProcessInfo(pid=2, name="b", cpu_percent=50.0, mem_percent=5.0),
            ProcessInfo(pid=3, name="c", cpu_percent=30.0, mem_percent=5.0),
        ]
        procs.sort(key=lambda entry: entry.cpu_percent, reverse=True)
        assert procs[0].pid == 2
        assert procs[1].pid == 3
        assert procs[2].pid == 1


class TestPsutilCollector:
    def test_get_metrics_returns_system_metrics(self):
        collector = PsutilCollector()
        metrics = collector.get_metrics()
        assert isinstance(metrics, SystemMetrics)
        assert 0 <= metrics.cpu_percent <= 100
        assert 0 <= metrics.ram_percent <= 100
        assert 0 <= metrics.disk_percent <= 100
        assert metrics.net_sent >= 0
        assert metrics.net_recv >= 0

    def test_get_processes_returns_list(self):
        collector = PsutilCollector()
        processes = collector.get_processes(top_n=5)
        assert len(processes) <= 5
        for proc in processes:
            assert isinstance(proc, ProcessInfo)
            assert proc.pid > 0
            assert proc.name

    def test_get_processes_handles_exceptions(self):
        with patch("app.infrastructure.system.psutil_collector.psutil") as mock_psutil:
            mock_psutil.NoSuchProcess = psutil.NoSuchProcess
            mock_psutil.AccessDenied = psutil.AccessDenied

            mock_valid_proc = MagicMock()
            mock_valid_proc.info = {
                "pid": 1, "name": "test", "cpu_percent": 10.0, "memory_percent": 5.0
            }
            mock_bad_proc = MagicMock()
            type(mock_bad_proc).info = PropertyMock(
                side_effect=psutil.NoSuchProcess(1)
            )
            mock_psutil.process_iter.return_value = [mock_valid_proc, mock_bad_proc]

            collector = PsutilCollector()
            processes = collector.get_processes(top_n=10)
            assert len(processes) == 1

    def test_format_bytes_returns_correct_unit(self):
        assert PsutilCollector._format_bytes(500) == "500.0 B"
        assert PsutilCollector._format_bytes(2048) == "2.0 KB"
        assert PsutilCollector._format_bytes(1048576) == "1.0 MB"
        assert PsutilCollector._format_bytes(1073741824) == "1.0 GB"
        assert PsutilCollector._format_bytes(1099511627776) == "1.0 TB"
        assert PsutilCollector._format_bytes(1125899906842624) == "1.0 PB"

    def test_format_bytes_edge_case_zero(self):
        assert PsutilCollector._format_bytes(0) == "0.0 B"
