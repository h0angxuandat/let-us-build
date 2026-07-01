"""Requirement intake CRUD, nested under a project (LUB-013)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from lub_store.models import Requirement
from lub_store.repositories import ProjectRepository, RequirementRepository
from sqlalchemy.ext.asyncio import AsyncSession

from lub_api.db import get_session
from lub_api.schemas import RequirementCreate, RequirementRead

router = APIRouter(prefix="/projects/{project_id}/requirements", tags=["requirements"])


@router.post("", response_model=RequirementRead, status_code=status.HTTP_201_CREATED)
async def add_requirement(
    project_id: UUID,
    body: RequirementCreate,
    session: AsyncSession = Depends(get_session),
) -> Requirement:
    if await ProjectRepository(session).get(project_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "project not found")
    req = Requirement(project_id=project_id, **body.model_dump())
    return await RequirementRepository(session).add(req)


@router.get("", response_model=list[RequirementRead])
async def list_requirements(
    project_id: UUID, session: AsyncSession = Depends(get_session)
) -> list[Requirement]:
    return await RequirementRepository(session).list(project_id=project_id)
