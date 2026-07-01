"""Lane state machine. STUB (M0): built in M4 (LUB-041).

Lane is derived from a ticket's sdlc_stage + block state; this class centralizes the legal
transitions of the 4-lane board (SR-3) and the done/pause evaluation (SR-4).
"""

from __future__ import annotations

from lub_store import Lane


class LaneStateMachine:
    def can_transition(self, src: Lane, dst: Lane) -> bool:
        raise NotImplementedError("lane rules land in M4 (LUB-041)")
