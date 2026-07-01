"""Shared domain enums — the ubiquitous language of the platform (DDD, SR-9)."""

from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    """The six default agent roles."""

    PM = "pm"
    BA = "ba"
    DESIGNER = "designer"
    TECH_LEAD = "tech_lead"
    DEVELOPER = "developer"
    QE = "qe"


class Lane(StrEnum):
    """The 4-lane Kanban board contract (SR-3). `human_needed` = paused for the user."""

    PLAN = "plan"
    HUMAN_NEEDED = "human_needed"
    PROCESSING = "processing"
    TESTING = "testing"
    DONE = "done"


class TicketType(StrEnum):
    """Agile work item types; Epic→Story→Task hierarchy via parent_id."""

    EPIC = "epic"
    USER_STORY = "user_story"
    TASK = "task"
    DESIGN = "design"
    TECH_DESIGN = "tech_design"
    BUG = "bug"
    CHORE = "chore"
    DECISION = "decision"
    SPIKE = "spike"


class SprintStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    REVIEW = "review"
    DONE = "done"


class RunStatus(StrEnum):
    RUNNING = "running"
    PAUSED = "paused"
    DONE = "done"


class MemoryTier(StrEnum):
    """agentmemory-inspired consolidation tiers (see lub_memory)."""

    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
