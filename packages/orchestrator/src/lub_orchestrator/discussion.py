"""Agent discussion subgraph (blackboard transcript).

STUB (M0): built in M5 (LUB-054). Chair defaults by ticket type (business→PM, technical→TL, D13).
Full mechanism: `document/agent-discussion-protocol.md`.
"""

from __future__ import annotations

from dataclasses import dataclass

from lub_store import Role


@dataclass(frozen=True, slots=True)
class DiscussionSpec:
    """What kicks off a discussion (FR-AGT-3)."""

    topic: str
    question: str
    participants: tuple[Role, ...]
    chair: Role


@dataclass(frozen=True, slots=True)
class Decision:
    """Structured output of a discussion — persisted to ticket + memory (procedural tier)."""

    decision: str
    rationale: str
    alternatives_considered: tuple[str, ...] = ()
    dissent: str | None = None
    follow_up_tickets: tuple[str, ...] = ()


async def run_discussion(spec: DiscussionSpec, ticket_id: str) -> Decision:
    """Run the bounded blackboard loop; return a Decision or escalate to `human needed`."""
    raise NotImplementedError("discussion subgraph lands in M5 (LUB-054)")
