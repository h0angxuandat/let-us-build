"""SQLAlchemy models — the delivery-domain aggregates (DDD, system-design.md §3).

Portable types (Uuid/JSON/Enum native_enum=False) so the same models run on Postgres (prod) and
SQLite (tests). Memory/Lesson persistence is deferred to M6/M7.
"""

from __future__ import annotations

import uuid

from sqlalchemy import JSON as SA_JSON
from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lub_store.db import Base, TimestampMixin
from lub_store.enums import Lane, Role, RunStatus, SprintStatus, TicketType


def _enum(enum_cls: type) -> Enum:
    """Portable string-backed enum column (VARCHAR + CHECK on any dialect)."""
    return Enum(
        enum_cls, native_enum=False, length=32, values_callable=lambda e: [m.value for m in e]
    )


class Project(TimestampMixin, Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    target_platform: Mapped[str | None] = mapped_column(String(100), default=None)
    constraints: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(30), default="active")

    requirements: Mapped[list[Requirement]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    tickets: Mapped[list[Ticket]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    sprints: Mapped[list[Sprint]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Requirement(TimestampMixin, Base):
    __tablename__ = "requirements"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(20), default="brief")  # brief|design|file|link
    content: Mapped[str] = mapped_column(Text, default="")
    file_ref: Mapped[str | None] = mapped_column(String(500), default=None)

    project: Mapped[Project] = relationship(back_populates="requirements")


class Agent(TimestampMixin, Base):
    """Per-agent config. project_id NULL = a global default template."""

    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), default=None
    )
    role: Mapped[Role] = mapped_column(_enum(Role))
    display_name: Mapped[str] = mapped_column(String(100), default="")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    provider: Mapped[str] = mapped_column(String(50), default="anthropic")
    model: Mapped[str] = mapped_column(String(100), default="claude-opus-4-8")
    temperature: Mapped[float] = mapped_column(default=0.2)
    system_prompt: Mapped[str] = mapped_column(Text, default="")
    skill_ids: Mapped[list[str]] = mapped_column(SA_JSON, default=list)
    config: Mapped[dict[str, object]] = mapped_column(SA_JSON, default=dict)


class Sprint(TimestampMixin, Base):
    """Agile iteration. Sprint length = a work-batch, not wall-clock."""

    __tablename__ = "sprints"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    index: Mapped[int] = mapped_column(Integer, default=1)
    goal: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[SprintStatus] = mapped_column(_enum(SprintStatus), default=SprintStatus.PLANNED)
    batch_limit: Mapped[int | None] = mapped_column(Integer, default=None)

    project: Mapped[Project] = relationship(back_populates="sprints")
    tickets: Mapped[list[Ticket]] = relationship(back_populates="sprint")


class Ticket(TimestampMixin, Base):
    """Epic/Story/Task hierarchy via parent_id; DDD tags bounded_context + aggregate."""

    __tablename__ = "tickets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    sprint_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("sprints.id", ondelete="SET NULL"), default=None
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("tickets.id", ondelete="SET NULL"), default=None
    )
    key: Mapped[str] = mapped_column(String(30), index=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text, default="")
    type: Mapped[TicketType] = mapped_column(_enum(TicketType), default=TicketType.USER_STORY)
    lane: Mapped[Lane] = mapped_column(_enum(Lane), default=Lane.PLAN)
    status: Mapped[str] = mapped_column(String(30), default="open")
    priority: Mapped[int] = mapped_column(Integer, default=0)
    story_points: Mapped[int | None] = mapped_column(Integer, default=None)
    acceptance_criteria: Mapped[str | None] = mapped_column(Text, default=None)
    bounded_context: Mapped[str | None] = mapped_column(String(100), default=None)
    aggregate: Mapped[str | None] = mapped_column(String(100), default=None)
    assignee_role: Mapped[Role | None] = mapped_column(_enum(Role), default=None)
    depends_on: Mapped[list[str]] = mapped_column(SA_JSON, default=list)
    created_by: Mapped[str] = mapped_column(String(20), default="agent")  # user|agent
    sdlc_stage: Mapped[str | None] = mapped_column(String(40), default=None)

    project: Mapped[Project] = relationship(back_populates="tickets")
    sprint: Mapped[Sprint | None] = relationship(back_populates="tickets")
    events: Mapped[list[TicketEvent]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )
    artifacts: Mapped[list[Artifact]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )


class TicketEvent(TimestampMixin, Base):
    __tablename__ = "ticket_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(30))  # lane_change|assign|comment|artifact|...
    actor: Mapped[str] = mapped_column(String(60), default="")
    payload: Mapped[dict[str, object]] = mapped_column(SA_JSON, default=dict)

    ticket: Mapped[Ticket] = relationship(back_populates="events")


class Discussion(TimestampMixin, Base):
    __tablename__ = "discussions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    topic: Mapped[str] = mapped_column(String(300), default="")
    participants: Mapped[list[str]] = mapped_column(SA_JSON, default=list)  # role values
    chair: Mapped[Role | None] = mapped_column(_enum(Role), default=None)
    status: Mapped[str] = mapped_column(String(20), default="open")  # open|resolved
    decision: Mapped[str | None] = mapped_column(Text, default=None)
    rationale: Mapped[str | None] = mapped_column(Text, default=None)

    messages: Mapped[list[Message]] = relationship(
        back_populates="discussion", cascade="all, delete-orphan"
    )


class Message(TimestampMixin, Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    discussion_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("discussions.id", ondelete="CASCADE")
    )
    agent_role: Mapped[Role] = mapped_column(_enum(Role))
    content: Mapped[str] = mapped_column(Text, default="")

    discussion: Mapped[Discussion] = relationship(back_populates="messages")


class Artifact(TimestampMixin, Base):
    __tablename__ = "artifacts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(40))  # BRD|PRD|domain_model|code|test_result|...
    path: Mapped[str | None] = mapped_column(String(500), default=None)
    inline: Mapped[str | None] = mapped_column(Text, default=None)
    version: Mapped[int] = mapped_column(Integer, default=1)
    produced_by: Mapped[Role | None] = mapped_column(_enum(Role), default=None)

    ticket: Mapped[Ticket] = relationship(back_populates="artifacts")


class HumanRequest(TimestampMixin, Base):
    __tablename__ = "human_requests"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    question: Mapped[str] = mapped_column(Text)
    options: Mapped[list[str]] = mapped_column(SA_JSON, default=list)
    status: Mapped[str] = mapped_column(String(20), default="open")  # open|answered
    answer: Mapped[str | None] = mapped_column(Text, default=None)


class Run(TimestampMixin, Base):
    __tablename__ = "runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    status: Mapped[RunStatus] = mapped_column(_enum(RunStatus), default=RunStatus.RUNNING)
    stop_reason: Mapped[str | None] = mapped_column(String(200), default=None)
