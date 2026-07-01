"""Generated-code workspace + sandbox for let-us-build.

The Dev agent edits real files under `./workspaces/<project>/`; builds/tests run in a
Docker-per-project sandbox (subprocess fallback). Generated code only runs in the sandbox (SR-7).
Lands in M8 (LUB-080..082).
"""

from lub_workspace.manager import WorkspaceManager
from lub_workspace.sandbox import Sandbox

__all__ = ["Sandbox", "WorkspaceManager"]
