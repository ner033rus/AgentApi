from __future__ import annotations

import json
from typing import Any

from app.collectors.gpu import get_gpu_metrics, gpu_metrics_to_flat
from app.collectors.ollama import get_ollama_metrics, ollama_metrics_to_flat
from app.collectors.system import get_cpu_metrics, get_ram_metrics
from app.models.schemas import FullMetrics


def collect_full_metrics(cpu_interval: float | None = 0.1) -> FullMetrics:
    """cpu_interval=None — неблокирующий замер CPU с момента прошлого вызова (как psutil)."""
    cpu = get_cpu_metrics(interval=cpu_interval)
    ram = get_ram_metrics()
    gpu = get_gpu_metrics()
    ollama = get_ollama_metrics()
    return FullMetrics(cpu=cpu, ram=ram, gpu=gpu, ollama=ollama)


def build_full_metrics_dict(full: FullMetrics) -> dict[str, Any]:
    """Словарь для JSON (вложенный)."""
    return json.loads(full.model_dump_json())


def flatten_metrics(full: FullMetrics) -> dict[str, Any]:
    """Плоский словарь для сравнения по путям watch."""
    out: dict[str, Any] = {}
    out["cpu.percent"] = full.cpu.percent
    out["ram.percent"] = full.ram.percent
    out["ram.used_bytes"] = float(full.ram.used_bytes)
    out["ram.total_bytes"] = float(full.ram.total_bytes)
    out.update(gpu_metrics_to_flat(full.gpu))
    out.update(ollama_metrics_to_flat(full.ollama))
    return out
