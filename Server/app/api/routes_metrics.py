from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.models.schemas import INCLUDE_ALL, MetricsIncludeQuery, metrics_partial
from app.services.metrics_snapshot import build_full_metrics_dict, collect_full_metrics

router = APIRouter(prefix="/metrics", tags=["metrics"])


def _parse_include(include: str | None) -> set[str]:
    return MetricsIncludeQuery(include=include).keys()


@router.get("")
async def get_metrics(include: str | None = Query(None, description="Список через запятую: cpu,ram,gpu,ollama")) -> dict[str, Any]:
    full = collect_full_metrics(cpu_interval=0.1)
    data = build_full_metrics_dict(full)
    keys = _parse_include(include)
    if keys == INCLUDE_ALL:
        return data
    return metrics_partial(data, keys)


@router.get("/cpu")
async def get_cpu() -> dict[str, Any]:
    full = collect_full_metrics(cpu_interval=0.1)
    return {"cpu": build_full_metrics_dict(full)["cpu"]}


@router.get("/ram")
async def get_ram() -> dict[str, Any]:
    full = collect_full_metrics(cpu_interval=0.1)
    return {"ram": build_full_metrics_dict(full)["ram"]}


@router.get("/gpu")
async def get_gpu() -> dict[str, Any]:
    full = collect_full_metrics(cpu_interval=0.1)
    return {"gpu": build_full_metrics_dict(full)["gpu"]}


@router.get("/ollama")
async def get_ollama() -> dict[str, Any]:
    full = collect_full_metrics(cpu_interval=0.1)
    return {"ollama": build_full_metrics_dict(full)["ollama"]}
