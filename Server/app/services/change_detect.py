from __future__ import annotations

import math
from typing import Any

from app.config import settings


def _matches_watch(path: str, patterns: list[str]) -> bool:
    path_l = path.lower()
    for p in patterns:
        pl = p.strip().lower()
        if not pl:
            continue
        if pl == path_l:
            return True
        # Префикс группы: gpu, cpu, ram, ollama
        if "." not in pl and path_l.startswith(pl + "."):
            return True
        if path_l.startswith(pl):
            return True
    return False


def _close(
    a: Any,
    b: Any,
    path: str,
) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    if isinstance(a, bool) and isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        fa, fb = float(a), float(b)
        if math.isnan(fa) or math.isnan(fb):
            return fa == fb
        if "temp" in path or "temp_c" in path:
            return abs(fa - fb) < settings.change_epsilon_temp
        if "watt" in path or "power" in path:
            return abs(fa - fb) < settings.change_epsilon_watts
        if "percent" in path or path.endswith(".util_percent"):
            return abs(fa - fb) < settings.change_epsilon_percent
        if "mib" in path or "bytes" in path:
            return abs(fa - fb) < settings.change_epsilon_mib
        return abs(fa - fb) < settings.change_epsilon_percent
    return a == b


def has_watched_change(
    old_flat: dict[str, Any],
    new_flat: dict[str, Any],
    watch: list[str],
) -> bool:
    """True, если по любому из отслеживаемых путей значение «заметно» изменилось."""
    all_paths = set(old_flat) | set(new_flat)
    for path in all_paths:
        if not _matches_watch(path, watch):
            continue
        if path not in old_flat or path not in new_flat:
            return True
        if not _close(old_flat[path], new_flat[path], path):
            return True
    return False
