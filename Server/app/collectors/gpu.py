from __future__ import annotations

import csv
import logging
import re
import shutil
import subprocess
from io import StringIO
from typing import Any

from app.models.schemas import GpuMetrics

log = logging.getLogger(__name__)

_NVIDIA_SMI = shutil.which("nvidia-smi")


def _parse_csv_line(line: str) -> list[str]:
    r = csv.reader(StringIO(line.strip()), skipinitialspace=True)
    row = next(r, [])
    return [c.strip() for c in row]


def _to_float(s: str) -> float | None:
    s = s.strip().strip('"')
    if not s or s.lower() in ("n/a", "[n/a]", "nan"):
        return None
    m = re.match(r"^([\d.]+)", s)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return None


def get_gpu_metrics() -> GpuMetrics:
    if not _NVIDIA_SMI:
        return GpuMetrics(available=False, error="nvidia-smi не найден в PATH")

    # fan.speed может отсутствовать на некоторых GPU — тогда [N/A]
    q = (
        "fan.speed,temperature.gpu,power.draw,power.limit,"
        "memory.used,memory.total,utilization.gpu"
    )
    try:
        proc = subprocess.run(
            [
                _NVIDIA_SMI,
                f"--query-gpu={q}",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        log.warning("nvidia-smi failed: %s", e)
        return GpuMetrics(available=False, error=str(e))

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        return GpuMetrics(available=False, error=err or f"exit {proc.returncode}")

    line = (proc.stdout or "").strip().splitlines()
    if not line:
        return GpuMetrics(available=False, error="Пустой вывод nvidia-smi")

    parts = _parse_csv_line(line[0])
    # Ожидаем 7 полей; если меньше — добиваем None
    while len(parts) < 7:
        parts.append("")

    fan = _to_float(parts[0])
    temp = _to_float(parts[1])
    p_draw = _to_float(parts[2])
    p_lim = _to_float(parts[3])
    mem_u = _to_float(parts[4])
    mem_t = _to_float(parts[5])
    util = _to_float(parts[6])

    power_display = None
    if p_draw is not None and p_lim is not None:
        power_display = f"{int(round(p_draw))}W/{int(round(p_lim))}W"
    elif p_draw is not None:
        power_display = f"{int(round(p_draw))}W/?"

    mem_disp = None
    if mem_u is not None and mem_t is not None:
        mem_disp = f"{int(round(mem_u))} MiB / {int(round(mem_t))} MiB"

    return GpuMetrics(
        fan_percent=round(fan, 1) if fan is not None else None,
        temp_c=round(temp, 1) if temp is not None else None,
        power_draw_w=round(p_draw, 2) if p_draw is not None else None,
        power_limit_w=round(p_lim, 2) if p_lim is not None else None,
        power_display=power_display,
        memory_used_mib=round(mem_u, 1) if mem_u is not None else None,
        memory_total_mib=round(mem_t, 1) if mem_t is not None else None,
        memory_display=mem_disp,
        util_percent=round(util, 1) if util is not None else None,
    )


def gpu_metrics_to_flat(g: GpuMetrics) -> dict[str, Any]:
    if not g.available:
        return {"gpu.available": False, "gpu.error": g.error or ""}
    return {
        "gpu.available": True,
        "gpu.fan_percent": g.fan_percent,
        "gpu.temp_c": g.temp_c,
        "gpu.power_draw_w": g.power_draw_w,
        "gpu.power_limit_w": g.power_limit_w,
        "gpu.memory_used_mib": g.memory_used_mib,
        "gpu.memory_total_mib": g.memory_total_mib,
        "gpu.util_percent": g.util_percent,
    }
