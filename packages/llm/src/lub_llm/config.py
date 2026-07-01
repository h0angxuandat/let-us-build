"""Per-agent LLM configuration (D3/D8: provider abstraction, Anthropic + OpenAI day-one)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class AgentLLMConfig:
    """Immutable per-agent LLM settings. Resolved to a LiteLLM model string at call time."""

    provider: str = "anthropic"
    model: str = "claude-opus-4-8"
    temperature: float = 0.2
    max_tokens: int | None = None
    extra: dict[str, object] = field(default_factory=dict)
