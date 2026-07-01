"""Concrete LLM routers (LUB-030).

`LiteLLMRouter` calls real providers via LiteLLM (per-agent provider/model). `TemplateRouter` is a
deterministic offline fallback so the platform runs and is testable without any API keys.
`build_router` picks between them based on which keys are configured.
"""

from __future__ import annotations

from lub_llm.config import AgentLLMConfig
from lub_llm.router import ChatMessage, LLMRouter


class LiteLLMRouter:
    """Routes completions through LiteLLM; each agent uses its own provider/model."""

    async def complete(self, config: AgentLLMConfig, messages: list[ChatMessage]) -> str:
        import litellm

        response = await litellm.acompletion(
            model=f"{config.provider}/{config.model}",
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
        return response.choices[0].message.content or ""


class TemplateRouter:
    """Deterministic offline router — no network. Used when no provider key is set (demo/tests)."""

    async def complete(self, config: AgentLLMConfig, messages: list[ChatMessage]) -> str:
        user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        return (
            "# Business Requirements (draft)\n\n"
            f"_Generated offline (no LLM key configured; model would be "
            f"{config.provider}/{config.model})._\n\n"
            f"## Context\n{user.strip()[:800]}\n\n"
            "## User stories\n"
            "- As a user, I can access the core capability described above.\n"
            "- As a user, I receive clear feedback on success and failure.\n\n"
            "## Acceptance criteria\n"
            "- The described behaviour works end to end.\n"
            "- Errors are handled and surfaced to the user.\n"
        )


def build_router(*, anthropic_key: str = "", openai_key: str = "") -> LLMRouter:
    """Return a live router if any provider key is set, else the offline TemplateRouter."""
    if anthropic_key or openai_key:
        return LiteLLMRouter()
    return TemplateRouter()
