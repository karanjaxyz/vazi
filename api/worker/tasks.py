import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .celery import celery_app
from database import get_sync_session
from models import Project, MonitoringRun, RunStatus, User
from engine.runner import run_monitoring
from engine.alerts import check_for_changes
from services import email

logger = logging.getLogger(__name__)


@celery_app.task(name="worker.tasks.check_due_projects")
def check_due_projects():
    """Find projects that haven't been scanned in 7+ days and queue runs."""
    with get_sync_session() as db:
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)

        # Get active projects with their latest run
        projects = db.execute(
            select(Project).where(Project.is_active == True)
        ).scalars().all()

        queued = 0
        for project in projects:
            # Check if there's a recent completed run
            latest_run = db.execute(
                select(MonitoringRun)
                .where(
                    MonitoringRun.project_id == project.id,
                    MonitoringRun.status == RunStatus.completed,
                )
                .order_by(MonitoringRun.completed_at.desc())
                .limit(1)
            ).scalar_one_or_none()

            # Queue if never scanned or last scan is older than 7 days
            if latest_run is None or latest_run.completed_at < cutoff:
                run_monitoring_task.delay(str(project.id))
                queued += 1

        logger.info(f"Queued {queued} monitoring runs")
        return {"queued": queued}


@celery_app.task(
    name="worker.tasks.run_monitoring_task",
    bind=True,
    max_retries=2,
    default_retry_delay=300,  # 5 min between retries
)
def run_monitoring_task(self, project_id: str):
    """Run a full monitoring scan for a project.

    Queries AI providers for each tracked query,
    parses all responses, stores results, and checks for changes.
    """
    try:
        # Run the async engine in a sync context (Celery tasks are sync)
        result = asyncio.run(_run_monitoring(project_id))
        return result
    except Exception as exc:
        logger.error(f"Monitoring run failed for project {project_id}: {exc}")
        # Retry on transient failures (API timeouts, rate limits)
        raise self.retry(exc=exc)


async def _run_monitoring(project_id: str) -> dict:
    """Async wrapper for the monitoring engine."""
    with get_sync_session() as db:
        project = db.execute(
            select(Project)
            .options(
                selectinload(Project.competitors),
                selectinload(Project.queries),
            )
            .where(Project.id == project_id)
        ).scalar_one_or_none()

        if not project:
            logger.error(f"Project {project_id} not found")
            return {"error": "project_not_found"}

        # Create the run record
        run = MonitoringRun(
            project_id=project.id,
            status=RunStatus.running,
            started_at=datetime.now(timezone.utc),
            query_count=len(project.queries),
        )
        db.add(run)
        db.commit()

        try:
            # Execute the monitoring run (queries AI providers, parses responses)
            mention_count = await run_monitoring(db, project, run)

            # Mark complete
            run.status = RunStatus.completed
            run.completed_at = datetime.now(timezone.utc)
            run.mention_count = mention_count
            db.commit()

            # Check for changes and send alerts
            check_and_alert.delay(str(project.id), str(run.id))

            logger.info(
                f"Monitoring complete for {project.brand_name}: "
                f"{mention_count} mentions across {run.query_count} queries"
            )
            return {
                "project_id": project_id,
                "run_id": str(run.id),
                "mentions": mention_count,
            }

        except Exception as exc:
            run.status = RunStatus.failed
            run.error_message = str(exc)[:500]
            run.completed_at = datetime.now(timezone.utc)
            db.commit()
            raise


@celery_app.task(name="worker.tasks.check_and_alert")
def check_and_alert(project_id: str, run_id: str):
    """Compare this run to the previous one and send alerts if changes detected."""
    with get_sync_session() as db:
        project = db.execute(
            select(Project).where(Project.id == project_id)
        ).scalar_one_or_none()

        if not project:
            return

        user = db.execute(
            select(User).where(User.user_uid == project.user_id)
        ).scalar_one_or_none()

        if not user:
            return

        changes = check_for_changes(db, project_id, run_id)

        if changes:
            asyncio.run(
                email.send_alert(
                    to=user.email,
                    project_name=project.brand_name,
                    changes=changes,
                )
            )
            logger.info(f"Sent alert for {project.brand_name}: {len(changes)} changes")

    return {"changes": len(changes) if changes else 0}


@celery_app.task(name="worker.tasks.send_weekly_digests")
def send_weekly_digests():
    """Send weekly summary emails to all users with completed runs."""
    with get_sync_session() as db:
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        # Find all runs completed in the last week
        recent_runs = db.execute(
            select(MonitoringRun)
            .where(
                MonitoringRun.status == RunStatus.completed,
                MonitoringRun.completed_at >= week_ago,
            )
            .options(selectinload(MonitoringRun.project))
        ).scalars().all()

        sent = 0
        for run in recent_runs:
            user = db.execute(
                select(User).where(User.user_uid == run.project.user_id)
            ).scalar_one_or_none()

            if user:
                asyncio.run(
                    email.send_email(
                        to=user.email,
                        subject=f"Vazi Weekly: {run.project.brand_name}",
                        html=_build_digest_html(run),
                    )
                )
                sent += 1

        logger.info(f"Sent {sent} weekly digests")
        return {"sent": sent}


def _build_digest_html(run: MonitoringRun) -> str:
    """Build a simple HTML digest email."""
    # TODO: Might need to mention competitor brnads here
    return f"""
    <h2>Weekly Report: {run.project.brand_name}</h2>
    <p>Your latest scan completed on {run.completed_at.strftime('%B %d, %Y')}.</p>
    <ul>
        <li><strong>Queries scanned:</strong> {run.query_count}</li>
        <li><strong>Mentions found:</strong> {run.mention_count}</li>
    </ul>
    <p><a href="https://app.vazi.io/projects/{run.project_id}">View full report →</a></p>
    """
