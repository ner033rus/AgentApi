from __future__ import annotations

import logging

from fastapi import FastAPI

from app.api.routes_metrics import router as metrics_router
from app.api.routes_processes import router as processes_router
from app.api.ws_stream import router as ws_router
from app.config import settings

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
log = logging.getLogger(__name__)

app = FastAPI(
    title="AgentAPI",
    description="CPU, RAM, NVIDIA GPU, процессы Ollama; REST и WebSocket при изменении метрик.",
    version="1.0.0",
)

API_PREFIX = "/api/v1"

app.include_router(metrics_router, prefix=API_PREFIX)
app.include_router(processes_router, prefix=API_PREFIX)
app.include_router(ws_router, prefix=API_PREFIX)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "AgentAPI",
        "docs": "/docs",
        "metrics": f"{API_PREFIX}/metrics",
        "stream_ws": f"{API_PREFIX}/stream",
    }
