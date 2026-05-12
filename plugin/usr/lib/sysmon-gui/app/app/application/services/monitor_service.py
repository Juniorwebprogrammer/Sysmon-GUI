from app.application.ports.system_collector import SystemCollector
from app.domain.process_info import ProcessInfo
from app.domain.system_metrics import SystemMetrics


class MonitorService:
    """Provides system metrics and process data by delegating to a collector."""

    def __init__(self, collector: SystemCollector):
        self._collector = collector

    def get_metrics(self) -> SystemMetrics:
        """Return a snapshot of current CPU, RAM, disk, and network usage."""
        return self._collector.get_metrics()

    def get_processes(self, top_n: int = 20) -> list[ProcessInfo]:
        """Return the top-N processes sorted by CPU usage."""
        return self._collector.get_processes(top_n=top_n)
