"""The six role agents. STUB (M0): behaviour lands in M3 (BA) and M5 (rest)."""

from __future__ import annotations

from lub_agents.base import Agent


class ProjectManager(Agent):
    """Product-owner + scrum-master: backlog, sprints, ceremonies, decision chair (business)."""

    async def run(self, ticket_id: str) -> None:
        raise NotImplementedError("PM.run lands in M4/M5")


class BusinessAnalyst(Agent):
    """Requirements, epics/stories, acceptance criteria, ubiquitous-language glossary (DDD)."""

    async def run(self, ticket_id: str) -> None:
        raise NotImplementedError("BA.run lands in M3")


class Designer(Agent):
    """Wireframes, design tokens, UX flows, a11y direction."""

    async def run(self, ticket_id: str) -> None:
        raise NotImplementedError("Designer.run lands in M5")


class TechLead(Agent):
    """DDD strategic+tactical, tech design, ADRs, task decomposition, decision chair (technical)."""

    async def run(self, ticket_id: str) -> None:
        raise NotImplementedError("TechLead.run lands in M5")


class Developer(Agent):
    """Implements a task per the domain model; writes unit tests."""

    async def run(self, ticket_id: str) -> None:
        raise NotImplementedError("Developer.run lands in M5")


class QeEngineer(Agent):
    """Test plan/cases, runs tests in sandbox, cross-artifact review, sprint-review acceptance."""

    async def run(self, ticket_id: str) -> None:
        raise NotImplementedError("QeEngineer.run lands in M5")


__all__ = [
    "BusinessAnalyst",
    "Designer",
    "Developer",
    "ProjectManager",
    "QeEngineer",
    "TechLead",
]
