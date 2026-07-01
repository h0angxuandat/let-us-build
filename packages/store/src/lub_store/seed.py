"""Seed the six default agent templates (LUB-011).

Global templates (project_id = NULL) used as defaults when a project is created. Idempotent:
skips roles that already have a global template. Chair defaults (D13) and skills come from the
agent-sdlc-flow spec; models here reflect D8 (Anthropic + OpenAI day-one).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from lub_store.enums import Role
from lub_store.models import Agent

# role -> (display name, default skills)
_DEFAULTS: dict[Role, tuple[str, list[str]]] = {
    Role.PM: ("Project Manager", ["agile-backlog", "sprint-planning", "retrospective"]),
    Role.BA: (
        "Business Analyst",
        ["requirements-elicitation", "user-story-writing", "ubiquitous-language"],
    ),
    Role.DESIGNER: ("UI/UX Designer", ["wireframing", "design-tokens", "a11y-wcag", "ux-flow"]),
    Role.TECH_LEAD: (
        "Technical Lead",
        ["ddd-strategic", "ddd-tactical", "adr-authoring", "api-design"],
    ),
    Role.DEVELOPER: ("Developer", ["tdd", "ddd-implementation", "code-implementation"]),
    Role.QE: ("QE Engineer", ["test-planning", "test-case-design", "cross-artifact-review"]),
}


async def seed_default_agents(sessionmaker: async_sessionmaker[AsyncSession]) -> int:
    """Insert any missing global agent templates. Returns the number created."""
    created = 0
    async with sessionmaker() as session:
        existing = set(
            (await session.scalars(select(Agent.role).where(Agent.project_id.is_(None)))).all()
        )
        for role, (name, skills) in _DEFAULTS.items():
            if role in existing:
                continue
            session.add(Agent(role=role, display_name=name, skill_ids=skills))
            created += 1
        await session.commit()
    return created
