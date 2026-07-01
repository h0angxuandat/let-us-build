"""Auto-pick scheduler. STUB (M0): built in M4 (LUB-042)."""

from __future__ import annotations


class Scheduler:
    """Scans `plan` for tickets whose deps are satisfied and dispatches them to matching agents."""

    async def tick(self) -> None:
        """One scheduling pass (auto-pick + concurrency/rate caps). Implemented in M4."""
        raise NotImplementedError("scheduler lands in M4 (LUB-042)")
