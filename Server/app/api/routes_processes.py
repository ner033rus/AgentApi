from __future__ import annotations

import os
import signal

import psutil
from fastapi import APIRouter, HTTPException

from app.collectors.ollama import is_ollama_process
from app.models.schemas import KillProcessResponse

router = APIRouter(prefix="/processes", tags=["processes"])


@router.delete("/{pid}", response_model=KillProcessResponse)
async def terminate_process(pid: int) -> KillProcessResponse:
    if pid <= 0:
        raise HTTPException(status_code=400, detail="Некорректный PID")

    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        raise HTTPException(status_code=404, detail="Процесс не найден")

    if not is_ollama_process(proc):
        raise HTTPException(
            status_code=403,
            detail="Разрешено завершать только процессы, связанные с Ollama",
        )

    try:
        os.kill(pid, signal.SIGTERM)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Не удалось отправить SIGTERM: {e}") from e

    return KillProcessResponse(ok=True, pid=pid, message="Отправлен SIGTERM")
