"""Per-role verifier contract (SR-6). STUB (M0): defined in M7 (LUB-071).

The verifier is the crux of self-improvement — a concrete reward per role (Dev: tests pass;
QE: defects caught; BA: requirement churn; ...). Guarded against Goodhart by cross-role review.
"""

from __future__ import annotations

from typing import Protocol


class Verifier(Protocol):
    """Scores a role's work on a ticket. Returns a reward in [0, 1]."""

    async def score(self, ticket_id: str) -> float: ...
