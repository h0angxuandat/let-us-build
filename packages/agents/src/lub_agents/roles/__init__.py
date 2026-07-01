"""The six role agents. BA is implemented (M3); the rest land in M5."""

from __future__ import annotations

from lub_store import Role
from lub_store.models import Artifact

from lub_agents.base import Agent
from lub_agents.context import AgentContext


class ProjectManager(Agent):
    """Product-owner + scrum-master: backlog, sprints, ceremonies, decision chair (business)."""

    async def run(self, ctx: AgentContext) -> None:
        raise NotImplementedError("PM.run lands in M4/M5")


class BusinessAnalyst(Agent):
    """Requirements, epics/stories, acceptance criteria, ubiquitous-language glossary (DDD)."""

    async def run(self, ctx: AgentContext) -> None:
        prompt = (
            "Write a concise Business Requirements Document for the following work item. "
            "Include a short context summary, user stories, and acceptance criteria.\n\n"
            f"Title: {ctx.ticket.title}\n"
            f"Description: {ctx.ticket.description or '(none provided)'}"
        )
        content = await self.ask(ctx, prompt)
        ctx.session.add(
            Artifact(
                ticket_id=ctx.ticket.id,
                type="BRD",
                inline=content,
                produced_by=Role.BA,
            )
        )
        await ctx.session.flush()


class Designer(Agent):
    """Wireframes, design tokens, UX flows, a11y direction."""

    async def run(self, ctx: AgentContext) -> None:
        raise NotImplementedError("Designer.run lands in M5")


class TechLead(Agent):
    """DDD strategic+tactical, tech design, ADRs, task decomposition, decision chair (technical)."""

    async def run(self, ctx: AgentContext) -> None:
        raise NotImplementedError("TechLead.run lands in M5")


class Developer(Agent):
    """Implements a task per the domain model; writes unit tests."""

    async def run(self, ctx: AgentContext) -> None:
        raise NotImplementedError("Developer.run lands in M5")


class QeEngineer(Agent):
    """Test plan/cases, runs tests in sandbox, cross-artifact review, sprint-review acceptance."""

    async def run(self, ctx: AgentContext) -> None:
        raise NotImplementedError("QeEngineer.run lands in M5")


__all__ = [
    "BusinessAnalyst",
    "Designer",
    "Developer",
    "ProjectManager",
    "QeEngineer",
    "TechLead",
]
