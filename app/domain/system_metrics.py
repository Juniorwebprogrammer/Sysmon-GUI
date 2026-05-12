from dataclasses import dataclass


@dataclass
class SystemMetrics:
    """Aggregated system resource snapshot returned by the collector."""

    cpu_percent: float
    ram_percent: float
    ram_detail: str
    disk_percent: float
    disk_detail: str
    net_sent: int
    net_recv: int
