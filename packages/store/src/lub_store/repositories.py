"""Repository pattern — one repository per aggregate root (DDD, SR-7).

STUB (M0): concrete repositories land in M1 (LUB-012). This defines the generic contract.
"""

from __future__ import annotations

from typing import Protocol, TypeVar
from uuid import UUID

T = TypeVar("T")


class Repository(Protocol[T]):
    """Generic aggregate-root repository. Business logic depends on this, not on the ORM."""

    async def get(self, id: UUID) -> T | None: ...

    async def list(self, **filters: object) -> list[T]: ...

    async def add(self, entity: T) -> T: ...

    async def update(self, entity: T) -> T: ...

    async def delete(self, id: UUID) -> None: ...
