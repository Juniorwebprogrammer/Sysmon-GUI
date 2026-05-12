from abc import ABC, abstractmethod

from app.domain.process_info import ProcessInfo
from app.domain.system_metrics import SystemMetrics


class SystemCollector(ABC):
    """Interface for reading system metrics and process information."""

    @abstractmethod
    def get_metrics(self) -> SystemMetrics: ...

    @abstractmethod
    def get_processes(self, top_n: int = 20) -> list[ProcessInfo]: ...
