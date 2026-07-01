"""Repository pattern — one repository per aggregate root (DDD, SR-7).

`Repository` is the abstract contract business logic depends on; `SqlAlchemyRepository` is the
async SQLAlchemy implementation. Concrete per-aggregate repositories are thin subclasses.
"""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lub_store.db import Base
from lub_store.models import Agent, Project, Requirement, Sprint, Ticket


class Repository[T](Protocol):
    """Generic aggregate-root repository. Business logic depends on this, not on the ORM."""

    async def get(self, id: UUID) -> T | None: ...
    async def list(self, **filters: object) -> list[T]: ...
    async def add(self, entity: T) -> T: ...
    async def update(self, entity: T) -> T: ...
    async def delete(self, id: UUID) -> None: ...


class SqlAlchemyRepository[M: Base]:
    """Async SQLAlchemy repository for one model. Flushes so DB defaults/ids populate."""

    model: type[M]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id: UUID) -> M | None:
        return await self.session.get(self.model, id)

    async def list(self, **filters: object) -> list[M]:
        stmt = select(self.model).filter_by(**filters)
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def add(self, entity: M) -> M:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, entity: M) -> M:
        merged = await self.session.merge(entity)
        await self.session.flush()
        return merged

    async def delete(self, id: UUID) -> None:
        await self.session.execute(sa_delete(self.model).where(self.model.id == id))  # type: ignore[attr-defined]


class ProjectRepository(SqlAlchemyRepository[Project]):
    model = Project


class RequirementRepository(SqlAlchemyRepository[Requirement]):
    model = Requirement


class AgentRepository(SqlAlchemyRepository[Agent]):
    model = Agent


class SprintRepository(SqlAlchemyRepository[Sprint]):
    model = Sprint


class TicketRepository(SqlAlchemyRepository[Ticket]):
    model = Ticket
