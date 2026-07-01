"""Sandboxed build/test runner. STUB (M0): built in M8 (LUB-081)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class RunResult:
    ok: bool
    stdout: str = ""
    stderr: str = ""


class Sandbox(Protocol):
    """Runs commands isolated from the host (Docker-per-project, subprocess fallback)."""

    async def run(self, project_id: str, command: list[str]) -> RunResult: ...
