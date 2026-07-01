"""Project CRUD (LUB-013)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from lub_store.models import Project
from lub_store.repositories import ProjectRepository
from sqlalchemy.ext.asyncio import AsyncSession

from lub_api.db import get_session
from lub_api.schemas import ProjectCreate, ProjectRead

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    body: ProjectCreate, session: AsyncSession = Depends(get_session)
) -> Project:
    project = Project(**body.model_dump())
    return await ProjectRepository(session).add(project)


@router.get("", response_model=list[ProjectRead])
async def list_projects(session: AsyncSession = Depends(get_session)) -> list[Project]:
    return await ProjectRepository(session).list()


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: UUID, session: AsyncSession = Depends(get_session)) -> Project:
    project = await ProjectRepository(session).get(project_id)
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "project not found")
    return project
