import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import User, Project, Competitor, Query
from schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectSummary,
    ProjectDetail,
    CompetitorCreate,
    CompetitorResponse,
    QueryCreate,
    QueryResponse,
)
from .deps import get_db, get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])


# --- Helpers ---

async def _get_project(
    project_id: uuid.UUID, user: User, db: AsyncSession
) -> Project:
    """Get a project by ID, ensuring it belongs to the current user."""
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.competitors), selectinload(Project.queries))
        .where(Project.id == project_id, Project.user_id == user.user_uid)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# --- Projects ---

@router.get("", response_model=list[ProjectSummary])
async def list_projects(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all projects for the current user."""
    result = await db.execute(
        select(Project)
        .where(Project.user_id == user.user_uid)
        .order_by(Project.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=ProjectDetail, status_code=201)
async def create_project(
    data: ProjectCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new project with competitors and queries."""
    project = Project(
        user_id=user.user_uid,
        name=data.name,
        brand_name=data.brand_name,
    )
    db.add(project)
    await db.flush()

    for c in data.competitors:
        db.add(Competitor(project_id=project.id, name=c.name))

    for q in data.queries:
        db.add(Query(project_id=project.id, text=q.text))

    await db.commit()

    return await _get_project(project.id, user, db)


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(
    project_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single project with its competitors and queries."""
    return await _get_project(project_id, user, db)


@router.patch("/{project_id}", response_model=ProjectDetail)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update project name, brand name, or active status."""
    project = await _get_project(project_id, user, db)

    if data.name is not None:
        project.name = data.name
    if data.brand_name is not None:
        project.brand_name = data.brand_name
    if data.is_active is not None:
        project.is_active = data.is_active

    await db.commit()
    return await _get_project(project_id, user, db)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a project and all its data."""
    project = await _get_project(project_id, user, db)
    await db.delete(project)
    await db.commit()


# --- Competitors ---

@router.post("/{project_id}/competitors", response_model=CompetitorResponse, status_code=201)
async def add_competitor(
    project_id: uuid.UUID,
    data: CompetitorCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a competitor to a project. Max 5."""
    project = await _get_project(project_id, user, db)

    if len(project.competitors) >= 5:
        raise HTTPException(status_code=400, detail="Maximum 5 competitors per project")

    competitor = Competitor(project_id=project.id, name=data.name)
    db.add(competitor)
    await db.commit()
    await db.refresh(competitor)
    return competitor


@router.delete("/{project_id}/competitors/{competitor_id}", status_code=204)
async def remove_competitor(
    project_id: uuid.UUID,
    competitor_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a competitor from a project."""
    await _get_project(project_id, user, db)  # ownership check

    result = await db.execute(
        select(Competitor).where(
            Competitor.id == competitor_id,
            Competitor.project_id == project_id,
        )
    )
    competitor = result.scalar_one_or_none()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    await db.delete(competitor)
    await db.commit()


# --- Queries ---

@router.post("/{project_id}/queries", response_model=QueryResponse, status_code=201)
async def add_query(
    project_id: uuid.UUID,
    data: QueryCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a tracked query to a project. Max 20."""
    project = await _get_project(project_id, user, db)

    if len(project.queries) >= 20:
        raise HTTPException(status_code=400, detail="Maximum 20 queries per project")

    query = Query(project_id=project.id, text=data.text)
    db.add(query)
    await db.commit()
    await db.refresh(query)
    return query


@router.delete("/{project_id}/queries/{query_id}", status_code=204)
async def remove_query(
    project_id: uuid.UUID,
    query_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a tracked query from a project."""
    await _get_project(project_id, user, db)  # ownership check

    result = await db.execute(
        select(Query).where(
            Query.id == query_id,
            Query.project_id == project_id,
        )
    )
    query = result.scalar_one_or_none()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")

    await db.delete(query)
    await db.commit()
