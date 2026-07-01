"""Workspace lifecycle. STUB (M0): built in M8 (LUB-080)."""

from __future__ import annotations

from pathlib import Path


class WorkspaceManager:
    """Manages `./workspaces/<project>/` where the Dev agent writes generated code."""

    def path_for(self, project_id: str) -> Path:
        raise NotImplementedError("workspace manager lands in M8 (LUB-080)")
