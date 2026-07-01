"""Agent base — config + the `run()` contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from lub_llm import AgentLLMConfig
from lub_store import Role


@dataclass(frozen=True, slots=True)
class AgentConfig:
    """Per-agent configuration (FR-AGT-2)."""

    role: Role
    llm: AgentLLMConfig = field(default_factory=AgentLLMConfig)
    system_prompt: str = ""
    skill_ids: tuple[str, ...] = ()
    enabled: bool = True


class Agent(ABC):
    """Base class for a role agent. One instance works one ticket at a time."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config

    @property
    def role(self) -> Role:
        return self.config.role

    @abstractmethod
    async def run(self, ticket_id: str) -> None:
        """Do this agent's work for the given ticket. Implemented per role (M3/M5)."""
        raise NotImplementedError
