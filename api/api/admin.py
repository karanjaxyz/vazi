import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, Project
from worker.tasks import run_monitoring_task
from .deps import get_db, get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/run/{project_id}")
async def trigger_run(
    project_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger a monitoring run for a project."""
    from sqlalchemy import select

    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == user.user_uid,
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Queue the task
    task = run_monitoring_task.delay(str(project_id))

    return {
        "status": "queued",
        "task_id": task.id,
        "project_id": str(project_id),
    }
