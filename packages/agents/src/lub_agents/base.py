"""Agent base — config + the `run()` contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from lub_llm import AgentLLMConfig, ChatMessage
from lub_store import Role

from lub_agents.context import AgentContext


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

    async def ask(self, ctx: AgentContext, user_prompt: str) -> str:
        """Send this agent's system prompt + a user prompt through its configured router."""
        messages = [
            ChatMessage(role="system", content=self.config.system_prompt or self._default_system()),
            ChatMessage(role="user", content=user_prompt),
        ]
        return await ctx.router.complete(self.config.llm, messages)

    def _default_system(self) -> str:
        skills = ", ".join(self.config.skill_ids) or "general"
        return f"You are the {self.role.value} agent. Skills: {skills}."

    @abstractmethod
    async def run(self, ctx: AgentContext) -> None:
        """Do this agent's work for the ticket in `ctx`. Implemented per role (M3/M5)."""
        raise NotImplementedError
