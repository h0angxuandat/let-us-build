"""Memory client contract (M6). Stable across retrieval phases (vector → +RRF → +graph)."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from lub_store import Role

from lub_memory.records import MemoryRecord


class MemoryClient(Protocol):
    """Shared, retrievable memory scoped by project/ticket/role. Enforces the permission matrix."""

    async def remember(self, record: MemoryRecord) -> MemoryRecord: ...

    async def recall(
        self,
        project_id: UUID,
        ticket_id: UUID | None = None,
        role: Role | None = None,
        query: str | None = None,
        limit: int = 8,
    ) -> list[MemoryRecord]: ...

    async def consolidate(self, ticket_id: UUID) -> None:
        """On ticket close: collapse working memory into an episodic summary."""
        ...

    async def forget(self, record_id: UUID) -> None: ...
