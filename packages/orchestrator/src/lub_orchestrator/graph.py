"""Per-ticket LangGraph graph. STUB (M0): built in M4 (LUB-040)."""

from __future__ import annotations

from typing import Any


def build_ticket_graph() -> Any:
    """Compile the per-ticket graph (role node → artifacts → discussion? → lane advance).

    Uses an AsyncPostgresSaver checkpointer for durable pause/resume. Implemented in M4.
    """
    raise NotImplementedError("ticket graph lands in M4 (LUB-040)")
