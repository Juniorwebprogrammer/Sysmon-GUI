import psutil

_prev_net = None


def get_metrics():
    global _prev_net

    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    # Red: bytes enviados/recibidos desde el arranque
    net = psutil.net_io_counters()
    net_sent = net.bytes_sent
    net_recv = net.bytes_recv

    return {
        "cpu":        {"value": cpu,          "label": "CPU",   "unit": "%"},
        "ram":        {"value": mem.percent,   "label": "RAM",   "unit": "%",
                       "detail": f"{_fmt(mem.used)} / {_fmt(mem.total)}"},
        "disk":       {"value": disk.percent,  "label": "Disk", "unit": "%",
                       "detail": f"{_fmt(disk.used)} / {_fmt(disk.total)}"},
        "net_sent":   net_sent,
        "net_recv":   net_recv,
    }


def get_processes(n=20):
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = p.info
            procs.append({
                "pid":  info["pid"],
                "name": info["name"] or "?",
                "cpu":  round(info["cpu_percent"] or 0.0, 1),
                "mem":  round(info["memory_percent"] or 0.0, 1),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    procs.sort(key=lambda x: x["cpu"], reverse=True)
    return procs[:n]


def _fmt(b):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"