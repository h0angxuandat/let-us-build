"""LLM provider abstraction for let-us-build.

The only package that talks to LLM providers (SR-7). Each agent carries its own
`AgentLLMConfig` (provider + model + params); `LLMRouter` routes calls via LiteLLM and
centralizes keys/cost/rate/fallback. Implementation lands in M3 (LUB-030).
"""

from lub_llm.config import AgentLLMConfig
from lub_llm.router import ChatMessage, LLMRouter

__all__ = ["AgentLLMConfig", "ChatMessage", "LLMRouter"]
