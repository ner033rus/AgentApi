from __future__ import annotations

import psutil

from app.config import settings
from app.models.schemas import OllamaMetrics, OllamaProcessInfo


def _proc_name(proc: psutil.Process) -> str:
    try:
        return proc.name() or ""
    except (psutil.Error, OSError):
        return ""


def _cmdline_str(proc: psutil.Process) -> str:
    try:
        cmd = proc.cmdline()
        return " ".join(cmd) if cmd else ""
    except (psutil.Error, OSError):
        return ""


def is_ollama_process(proc: psutil.Process) -> bool:
    name = _proc_name(proc).lower()
    if any(s in name for s in settings.ollama_name_substrings):
        return True
    cmd = _cmdline_str(proc).lower()
    return any(s in cmd for s in settings.ollama_name_substrings)


def get_ollama_metrics() -> OllamaMetrics:
    processes: list[OllamaProcessInfo] = []
    for p in psutil.process_iter():
        try:
            if not is_ollama_process(p):
                continue
            mem = p.memory_info()
            rss = int(getattr(mem, "rss", 0) or 0)
            cmdline = _cmdline_str(p)
            processes.append(
                OllamaProcessInfo(
                    pid=p.pid,
                    name=_proc_name(p) or "unknown",
                    memory_bytes=rss,
                    memory_mib=round(rss / (1024 * 1024), 2),
                    cmdline=cmdline[:2000],
                )
            )
        except (psutil.Error, OSError):
            continue
    processes.sort(key=lambda x: x.memory_bytes, reverse=True)
    return OllamaMetrics(processes=processes)


def ollama_metrics_to_flat(o: OllamaMetrics) -> dict[str, float | int | str]:
    """Для сравнения изменений: сумма памяти и количество процессов + сигнатура pid."""
    total_mem = sum(p.memory_bytes for p in o.processes)
    pids = ",".join(str(p.pid) for p in sorted(o.processes, key=lambda x: x.pid))
    return {
        "ollama.process_count": len(o.processes),
        "ollama.total_memory_bytes": total_mem,
        "ollama.pids_signature": hash(pids) & 0xFFFFFFFF,
    }
