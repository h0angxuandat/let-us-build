"""Orchestration for let-us-build (LangGraph).

Thread = Ticket; `interrupt()` = `human needed`; durable Postgres checkpoints. The scheduler
auto-picks eligible `plan` tickets; the lane state machine governs transitions; the discussion
subgraph resolves multi-role decisions. Implementation lands in M4 (graph/scheduler/HITL) and
M5 (discussion). See `document/system-design.md` §4 and `document/agent-discussion-protocol.md`.
"""

from lub_orchestrator.discussion import Decision, DiscussionSpec
from lub_orchestrator.lanes import LaneStateMachine
from lub_orchestrator.scheduler import Scheduler

__all__ = ["Decision", "DiscussionSpec", "LaneStateMachine", "Scheduler"]
