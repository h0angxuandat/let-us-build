"""LLM router contract — per-agent provider/model behind one interface (LiteLLM in M3)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from lub_llm.config import AgentLLMConfig


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


class LLMRouter(Protocol):
    """Routes a chat completion for a given agent config. Centralizes keys/cost/rate/fallback."""

    async def complete(
        self, config: AgentLLMConfig, messages: list[ChatMessage]
    ) -> str: ...
