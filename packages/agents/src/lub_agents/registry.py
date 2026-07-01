"""Role → agent factory."""

from __future__ import annotations

from lub_store import Role

from lub_agents.base import Agent, AgentConfig
from lub_agents.roles import (
    BusinessAnalyst,
    Designer,
    Developer,
    ProjectManager,
    QeEngineer,
    TechLead,
)

_REGISTRY: dict[Role, type[Agent]] = {
    Role.PM: ProjectManager,
    Role.BA: BusinessAnalyst,
    Role.DESIGNER: Designer,
    Role.TECH_LEAD: TechLead,
    Role.DEVELOPER: Developer,
    Role.QE: QeEngineer,
}


def build_agent(config: AgentConfig) -> Agent:
    """Instantiate the agent class for a role from its config."""
    return _REGISTRY[config.role](config)
