import psutil

from app.models.schemas import CpuMetrics, RamMetrics


def get_cpu_metrics(interval: float | None = 0.1) -> CpuMetrics:
    """interval: секунды для первого замера (как у psutil.cpu_percent)."""
    p = psutil.cpu_percent(interval=interval)
    return CpuMetrics(percent=round(float(p), 2))


def get_ram_metrics() -> RamMetrics:
    v = psutil.virtual_memory()
    return RamMetrics(
        percent=round(float(v.percent), 2),
        used_bytes=int(v.used),
        total_bytes=int(v.total),
    )
