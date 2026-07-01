"""SQLAlchemy models — the domain aggregates.

STUB (M0): the ORM models (Project, Sprint, Ticket, Agent, Discussion, Message, Artifact,
HumanRequest, Lesson, Run, MemoryRecord) are defined in M1 (LUB-010). See
`document/system-design.md` §3 for the target schema and §3.2 for bounded-context grouping.
"""

from __future__ import annotations


class Base:
    """Placeholder declarative base. Replaced by a SQLAlchemy `DeclarativeBase` in M1."""
