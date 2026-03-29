from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.models.schemas import INCLUDE_ALL, StreamClientMessage, metrics_partial
from app.services.change_detect import has_watched_change
from app.services.metrics_snapshot import build_full_metrics_dict, collect_full_metrics, flatten_metrics

log = logging.getLogger(__name__)

router = APIRouter(tags=["stream"])


def _apply_send_mode(
    data: dict[str, Any],
    send_mode: str,
    include_fields: list[str] | None,
) -> dict[str, Any]:
    if send_mode != "partial":
        return data
    keys = {k.strip().lower() for k in (include_fields or []) if k.strip()}
    allowed = keys & INCLUDE_ALL
    if not allowed:
        return data
    return metrics_partial(data, allowed)


@router.websocket("/stream")
async def metrics_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    sub = None
    try:
        raw = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
        msg = StreamClientMessage.model_validate_json(raw)
        sub = msg.to_subscribe()
    except (asyncio.TimeoutError, ValueError) as e:
        await websocket.send_json({"error": "Ожидалось JSON с action=subscribe и watch", "detail": str(e)})
        await websocket.close(code=4400)
        return

    if sub is None:
        await websocket.send_json({"error": "Нужно: {\"action\":\"subscribe\",\"watch\":[\"cpu\",...]}"})
        await websocket.close(code=4400)
        return

    await websocket.send_json({"status": "subscribed", "watch": sub.watch, "poll_interval_sec": sub.poll_interval_sec})

    interval = max(0.25, float(sub.poll_interval_sec))
    first_cpu = True
    prev_flat: dict[str, Any] | None = None

    try:
        while True:
            cpu_iv = 0.1 if first_cpu else None
            first_cpu = False
            full = collect_full_metrics(cpu_interval=cpu_iv)
            flat = flatten_metrics(full)
            data = build_full_metrics_dict(full)

            if prev_flat is None:
                prev_flat = flat
                payload = _apply_send_mode(data, sub.send_mode, sub.include_fields)
                await websocket.send_json({"type": "metrics", "changed": True, "data": payload})
            else:
                changed = has_watched_change(prev_flat, flat, sub.watch)
                if changed:
                    prev_flat = flat
                    payload = _apply_send_mode(data, sub.send_mode, sub.include_fields)
                    await websocket.send_json({"type": "metrics", "changed": True, "data": payload})

            await asyncio.sleep(interval)
    except WebSocketDisconnect:
        log.info("WebSocket отключён клиентом")
    except Exception as e:
        log.exception("Ошибка потока: %s", e)
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass
