import psutil

from app.application.ports.system_collector import SystemCollector
from app.domain.process_info import ProcessInfo
from app.domain.system_metrics import SystemMetrics


class PsutilCollector(SystemCollector):
    """Collects system metrics and process info using the psutil library."""

    def get_metrics(self) -> SystemMetrics:
        """Gather current CPU, RAM, disk, and network statistics."""
        cpu_usage = psutil.cpu_percent(interval=None)
        virtual_memory = psutil.virtual_memory()
        disk_usage = psutil.disk_usage("/")
        network_counters = psutil.net_io_counters()

        return SystemMetrics(
            cpu_percent=cpu_usage,
            ram_percent=virtual_memory.percent,
            ram_detail=(
                f"{self._format_bytes(virtual_memory.used)}"
                f" / {self._format_bytes(virtual_memory.total)}"
            ),
            disk_percent=disk_usage.percent,
            disk_detail=(
                f"{self._format_bytes(disk_usage.used)}"
                f" / {self._format_bytes(disk_usage.total)}"
            ),
            net_sent=network_counters.bytes_sent,
            net_recv=network_counters.bytes_recv,
        )

    def get_processes(self, top_n: int = 20) -> list[ProcessInfo]:
        """Return the top-N processes sorted by CPU usage descending."""
        process_list: list[ProcessInfo] = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                proc_info = proc.info
                process_list.append(
                    ProcessInfo(
                        pid=proc_info["pid"],
                        name=proc_info["name"] or "?",
                        cpu_percent=round(proc_info["cpu_percent"] or 0.0, 1),
                        mem_percent=round(proc_info["memory_percent"] or 0.0, 1),
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        process_list.sort(key=lambda entry: entry.cpu_percent, reverse=True)
        return process_list[:top_n]

    @staticmethod
    def _format_bytes(byte_count: float | int) -> str:
        """Convert a byte value into a human-readable string (e.g. '1.5 GB')."""
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if byte_count < 1024:
                return f"{byte_count:.1f} {unit}"
            byte_count /= 1024
        return f"{byte_count:.1f} PB"
