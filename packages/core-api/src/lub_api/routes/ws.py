"""WebSocket gateway — streams project events to the board (FR-WEB-3)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/ws/projects/{project_id}")
async def project_ws(websocket: WebSocket, project_id: UUID) -> None:
    """Subscribe to a project's event stream (subscribe-only; client messages are ignored)."""
    await websocket.accept()
    bus = websocket.app.state.events
    async with bus.subscribe(project_id) as queue:
        try:
            while True:
                event = await queue.get()
                await websocket.send_json(event)
        except WebSocketDisconnect:
            return
