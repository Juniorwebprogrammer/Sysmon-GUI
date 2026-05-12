from dataclasses import dataclass


@dataclass
class ProcessInfo:
    """Lightweight model holding a snapshot of a running process."""

    pid: int
    name: str
    cpu_percent: float
    mem_percent: float
