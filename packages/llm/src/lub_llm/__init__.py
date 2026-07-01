"""LLM provider abstraction for let-us-build.

The only package that talks to LLM providers (SR-7). Each agent carries its own `AgentLLMConfig`
(provider + model + params); an `LLMRouter` routes calls. `LiteLLMRouter` hits real providers;
`TemplateRouter` is an offline fallback. `build_router` picks based on configured keys.
"""

from lub_llm.config import AgentLLMConfig
from lub_llm.router import ChatMessage, LLMRouter
from lub_llm.routers import LiteLLMRouter, TemplateRouter, build_router

__all__ = [
    "AgentLLMConfig",
    "ChatMessage",
    "LLMRouter",
    "LiteLLMRouter",
    "TemplateRouter",
    "build_router",
]
