"""Lesson record. STUB (M0): loop lands in M7 (LUB-070..073)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from lub_store import Role, TicketType


@dataclass(frozen=True, slots=True)
class Lesson:
    """A reusable lesson mined from a ticket's outcome; promoted to procedural memory."""

    role: Role
    ticket_type: TicketType
    context: str
    what_happened: str
    lesson: str
    score: float
    source_ticket_id: UUID | None = None
