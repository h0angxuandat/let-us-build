"""In-process pub/sub event bus for realtime board updates over WebSocket.

M2 broadcasts CRUD events (ticket.created / ticket.updated / ticket.lane_changed). From M4 the
orchestrator publishes agent/discussion/run events through the same bus. Single-process only;
a cross-process broker (Redis) would slot in behind this interface if we scale out.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from typing import Any
from uuid import UUID


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[UUID, set[asyncio.Queue[dict[str, Any]]]] = defaultdict(set)

    async def publish(self, project_id: UUID, event: dict[str, Any]) -> None:
        for queue in list(self._subscribers.get(project_id, ())):
            with suppress(asyncio.QueueFull):
                queue.put_nowait(event)

    @asynccontextmanager
    async def subscribe(self, project_id: UUID) -> AsyncIterator[asyncio.Queue[dict[str, Any]]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=100)
        self._subscribers[project_id].add(queue)
        try:
            yield queue
        finally:
            self._subscribers[project_id].discard(queue)
