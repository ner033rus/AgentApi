from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class CpuMetrics(BaseModel):
    percent: float = Field(description="Загрузка CPU, %")


class RamMetrics(BaseModel):
    percent: float = Field(description="Использование RAM, %")
    used_bytes: int
    total_bytes: int


class GpuMetrics(BaseModel):
    available: bool = True
    error: str | None = None
    fan_percent: float | None = Field(None, description="FAN %")
    temp_c: float | None = Field(None, description="Температура GPU, °C")
    power_draw_w: float | None = Field(None, description="Текущее потребление, Вт")
    power_limit_w: float | None = Field(None, description="Лимит TDP, Вт")
    power_display: str | None = Field(None, description="Например 25W/350W")
    memory_used_mib: float | None = None
    memory_total_mib: float | None = None
    memory_display: str | None = Field(None, description="Использовано/всего MiB")
    util_percent: float | None = Field(None, description="GPU-Util %")


class OllamaProcessInfo(BaseModel):
    pid: int
    name: str
    memory_bytes: int
    memory_mib: float
    cmdline: str


class OllamaMetrics(BaseModel):
    processes: list[OllamaProcessInfo] = Field(default_factory=list)


class FullMetrics(BaseModel):
    cpu: CpuMetrics
    ram: RamMetrics
    gpu: GpuMetrics
    ollama: OllamaMetrics


MetricKey = Literal["cpu", "ram", "gpu", "ollama"]

INCLUDE_ALL: frozenset[str] = frozenset({"cpu", "ram", "gpu", "ollama"})


class MetricsIncludeQuery(BaseModel):
    """Параметр include: через запятую, например cpu,ram,gpu."""

    include: str | None = None

    def keys(self) -> set[str]:
        if not self.include or not self.include.strip():
            return set(INCLUDE_ALL)
        parts = {p.strip().lower() for p in self.include.split(",") if p.strip()}
        allowed = parts & INCLUDE_ALL
        return allowed if allowed else set(INCLUDE_ALL)


class KillProcessResponse(BaseModel):
    ok: bool
    pid: int
    message: str


class StreamSubscribe(BaseModel):
    """Подписка на поток: при изменении любого из watch — отправить данные."""

    action: Literal["subscribe"] = "subscribe"
    watch: list[str] = Field(
        ...,
        description="Ключи или пути: cpu, ram, gpu, ollama или gpu.temp_c, ollama и т.д.",
    )
    send_mode: Literal["all", "partial"] = "all"
    """all — полный снимок; partial — только поля из include_fields."""
    include_fields: list[str] | None = Field(
        None,
        description="Для send_mode=partial: какие верхнеуровневые блоки отдавать (cpu, ram, gpu, ollama).",
    )
    poll_interval_sec: float = Field(1.0, ge=0.25, le=10.0)


class StreamClientMessage(BaseModel):
    """Одно сообщение от клиента WebSocket (расширяемо)."""

    action: str | None = None
    watch: list[str] | None = None
    send_mode: str | None = None
    include_fields: list[str] | None = None
    poll_interval_sec: float | None = None

    def to_subscribe(self) -> StreamSubscribe | None:
        if (self.action or "").lower() != "subscribe":
            return None
        if not self.watch:
            return None
        return StreamSubscribe(
            action="subscribe",
            watch=list(self.watch),
            send_mode=self.send_mode if self.send_mode in ("all", "partial") else "all",
            include_fields=self.include_fields,
            poll_interval_sec=self.poll_interval_sec if self.poll_interval_sec is not None else 1.0,
        )


def metrics_partial(full: dict[str, Any], keys: set[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k in sorted(keys & INCLUDE_ALL):
        if k in full:
            out[k] = full[k]
    return out
