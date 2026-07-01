"""The execution context handed to an agent's run()."""

from __future__ import annotations

from dataclasses import dataclass

from lub_llm import LLMRouter
from lub_store.models import Ticket
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(slots=True)
class AgentContext:
    """What an agent needs to work a ticket: the ticket, an LLM router, and a DB session.

    Memory (recall/consolidate) is injected here from M6; the orchestrator/scheduler from M4.
    """

    ticket: Ticket
    router: LLMRouter
    session: AsyncSession
