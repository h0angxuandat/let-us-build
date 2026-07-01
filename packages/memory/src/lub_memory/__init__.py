"""Own memory subsystem for let-us-build (D4-rev).

Native Python on Postgres+pgvector — NOT the rohitg00 Node sidecar. Borrows agentmemory's
4-tier model (working→episodic→semantic→procedural). Phased retrieval: vector similarity + metadata
filters (M6) → +tsvector/RRF (phase 2) → +graph/decay (phase 3). Implementation lands in M6.
"""

from lub_memory.client import MemoryClient
from lub_memory.records import MemoryRecord

__all__ = ["MemoryClient", "MemoryRecord"]
