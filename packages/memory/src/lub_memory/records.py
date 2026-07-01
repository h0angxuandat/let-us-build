"""Memory record model (see system-design.md §5)."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from lub_store import MemoryTier, Role


@dataclass(frozen=True, slots=True)
class MemoryRecord:
    """One memory item. Scoping (project/ticket/role) is first-class, not bolted on."""

    id: UUID
    project_id: UUID
    tier: MemoryTier
    content: str
    ticket_id: UUID | None = None
    role: Role | None = None
    visibility: str = "shared"  # "shared" | "role_private"
    metadata: dict[str, object] = field(default_factory=dict)
    salience: float = 1.0
