"""Pydantic request/response DTOs at the API boundary (immutable where read-only)."""

from __future__ import annotations

from uuid import UUID

from lub_store import Lane, Role, TicketType
from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = ""
    target_platform: str | None = None
    constraints: str = ""


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    description: str
    target_platform: str | None
    status: str


class RequirementCreate(BaseModel):
    kind: str = "brief"
    content: str = ""
    file_ref: str | None = None


class RequirementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    kind: str
    content: str
    file_ref: str | None


class AgentCreate(BaseModel):
    role: Role
    display_name: str = ""
    provider: str = "anthropic"
    model: str = "claude-opus-4-8"
    temperature: float = 0.2
    system_prompt: str = ""
    skill_ids: list[str] = Field(default_factory=list)


class AgentUpdate(BaseModel):
    """Partial update of an agent's config; only provided fields change."""

    display_name: str | None = None
    enabled: bool | None = None
    provider: str | None = None
    model: str | None = None
    temperature: float | None = None
    system_prompt: str | None = None
    skill_ids: list[str] | None = None


class AgentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID | None
    role: Role
    display_name: str
    enabled: bool
    provider: str
    model: str
    temperature: float
    skill_ids: list[str]


class TicketCreate(BaseModel):
    """Manual ticket add — always lands in the `plan` lane (FR-WEB-4)."""

    title: str = Field(min_length=1, max_length=300)
    description: str = ""
    type: TicketType = TicketType.USER_STORY
    priority: int = 0
    acceptance_criteria: str | None = None


class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    lane: Lane | None = None
    status: str | None = None
    priority: int | None = None
    assignee_role: Role | None = None


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    key: str
    title: str
    description: str
    type: TicketType
    lane: Lane
    status: str
    priority: int
    assignee_role: Role | None
    created_by: str


class ArtifactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    ticket_id: UUID
    type: str
    inline: str | None
    version: int
    produced_by: Role | None
