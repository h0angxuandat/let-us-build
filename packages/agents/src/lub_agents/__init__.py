"""The six role agents for let-us-build.

Each agent has independent config (provider/model/skills/enabled) and a `run()` that works one
ticket. Agents share memory and can discuss (see lub_orchestrator.discussion). Concrete role
behaviour lands in M3 (BA) and M5 (full roster). M0 ships the base + registry + role stubs.
"""

from lub_agents.base import Agent, AgentConfig
from lub_agents.registry import build_agent

__all__ = ["Agent", "AgentConfig", "build_agent"]
