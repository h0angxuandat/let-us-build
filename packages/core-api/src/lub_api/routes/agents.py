"""Agent config CRUD (LUB-013 / FR-WEB-6)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from lub_store.models import Agent
from lub_store.repositories import AgentRepository
from sqlalchemy.ext.asyncio import AsyncSession

from lub_api.db import get_session
from lub_api.schemas import AgentCreate, AgentRead, AgentUpdate

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentRead])
async def list_agents(session: AsyncSession = Depends(get_session)) -> list[Agent]:
    return await AgentRepository(session).list()


@router.post("", response_model=AgentRead, status_code=status.HTTP_201_CREATED)
async def create_agent(body: AgentCreate, session: AsyncSession = Depends(get_session)) -> Agent:
    return await AgentRepository(session).add(Agent(**body.model_dump()))


@router.patch("/{agent_id}", response_model=AgentRead)
async def update_agent(
    agent_id: UUID, body: AgentUpdate, session: AsyncSession = Depends(get_session)
) -> Agent:
    repo = AgentRepository(session)
    agent = await repo.get(agent_id)
    if agent is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "agent not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)
    await session.flush()
    return agent
