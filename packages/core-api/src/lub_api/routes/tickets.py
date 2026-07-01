"""Ticket CRUD + the manual add-to-plan path (LUB-023/LUB-004). Emits realtime events."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from lub_store import Lane
from lub_store.models import Ticket
from lub_store.repositories import ProjectRepository, TicketRepository
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from lub_api.db import get_session
from lub_api.schemas import TicketCreate, TicketRead, TicketUpdate

router = APIRouter(tags=["tickets"])


def _dto(t: Ticket) -> dict[str, Any]:
    return TicketRead.model_validate(t).model_dump(mode="json")


async def _publish(request: Request, project_id: UUID, event_type: str, ticket: Ticket) -> None:
    await request.app.state.events.publish(project_id, {"type": event_type, "ticket": _dto(ticket)})


@router.get("/projects/{project_id}/tickets", response_model=list[TicketRead], tags=["tickets"])
async def list_tickets(
    project_id: UUID, session: AsyncSession = Depends(get_session)
) -> list[Ticket]:
    return await TicketRepository(session).list(project_id=project_id)


@router.post(
    "/projects/{project_id}/tickets",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
    tags=["tickets"],
)
async def add_ticket(
    project_id: UUID,
    body: TicketCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> Ticket:
    if await ProjectRepository(session).get(project_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "project not found")
    count = await session.scalar(
        select(func.count()).select_from(Ticket).where(Ticket.project_id == project_id)
    )
    ticket = Ticket(
        project_id=project_id,
        key=f"LUB-{(count or 0) + 1}",
        lane=Lane.PLAN,
        created_by="user",
        **body.model_dump(),
    )
    ticket = await TicketRepository(session).add(ticket)
    await session.flush()
    await _publish(request, project_id, "ticket.created", ticket)
    return ticket


@router.get("/tickets/{ticket_id}", response_model=TicketRead, tags=["tickets"])
async def get_ticket(ticket_id: UUID, session: AsyncSession = Depends(get_session)) -> Ticket:
    ticket = await TicketRepository(session).get(ticket_id)
    if ticket is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ticket not found")
    return ticket


@router.patch("/tickets/{ticket_id}", response_model=TicketRead, tags=["tickets"])
async def update_ticket(
    ticket_id: UUID,
    body: TicketUpdate,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> Ticket:
    ticket = await TicketRepository(session).get(ticket_id)
    if ticket is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ticket not found")
    changes = body.model_dump(exclude_unset=True)
    lane_changed = "lane" in changes and changes["lane"] != ticket.lane
    for field, value in changes.items():
        setattr(ticket, field, value)
    await session.flush()
    event_type = "ticket.lane_changed" if lane_changed else "ticket.updated"
    await _publish(request, ticket.project_id, event_type, ticket)
    return ticket
