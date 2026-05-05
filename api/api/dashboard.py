import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, case, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import (
    User, Project, MonitoringRun, RunStatus,
    Result, Mention, Citation, Query,
)
from schemas.dashboard import (
    OverviewResponse,
    MentionsByQuery,
    MentionsResponse,
    CompetitorScore,
    CompetitorComparisonResponse,
    TrendPoint,
    TrendsResponse,
    SourceSummary,
    SourcesResponse,
    RunSummary,
    RunsResponse,
)
from engine.scorer import compute_visibility_score
from .deps import get_db, get_current_user

router = APIRouter(prefix="/projects/{project_id}", tags=["dashboard"])


async def _verify_ownership(
    project_id: uuid.UUID, user: User, db: AsyncSession
) -> Project:
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user.user_uid)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def _get_latest_run(db: AsyncSession, project_id: uuid.UUID) -> MonitoringRun | None:
    result = await db.execute(
        select(MonitoringRun)
        .where(
            MonitoringRun.project_id == project_id,
            MonitoringRun.status == RunStatus.completed,
        )
        .order_by(MonitoringRun.completed_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


@router.get("/overview", response_model=OverviewResponse)
async def get_overview(
    project_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Top-level dashboard metrics for the latest run."""
    project = await _verify_ownership(project_id, user, db)
    run = await _get_latest_run(db, project_id)

    if not run:
        return OverviewResponse(
            visibility_score=0,
            total_mentions=0,
            total_queries=0,
            competitor_gap=0,
            sentiment_positive_pct=0.0,
            last_run_at=None,
        )

    # Count target brand mentions
    target_mentions = await db.execute(
        select(func.count(Mention.id))
        .join(Result)
        .where(Result.run_id == run.id, Mention.is_target_brand == True)
    )
    total_mentions = target_mentions.scalar_one()

    # Count competitor mentions (most mentioned competitor)
    top_competitor_mentions = await db.execute(
        select(func.count(Mention.id))
        .join(Result)
        .where(Result.run_id == run.id, Mention.is_target_brand == False)
        .group_by(Mention.brand_name)
        .order_by(func.count(Mention.id).desc())
        .limit(1)
    )
    top_comp_count = top_competitor_mentions.scalar_one_or_none() or 0

    # Sentiment breakdown for target brand
    sentiment_counts = await db.execute(
        select(Mention.sentiment, func.count(Mention.id))
        .join(Result)
        .where(Result.run_id == run.id, Mention.is_target_brand == True)
        .group_by(Mention.sentiment)
    )
    sentiments = dict(sentiment_counts.all())
    total_sent = sum(sentiments.values()) or 1
    positive_pct = (sentiments.get("positive", 0) / total_sent) * 100

    return OverviewResponse(
        visibility_score=run.mention_count,  # will be replaced with scorer
        total_mentions=total_mentions,
        total_queries=run.query_count,
        competitor_gap=total_mentions - top_comp_count,
        sentiment_positive_pct=round(positive_pct, 1),
        last_run_at=run.completed_at,
    )


@router.get("/mentions", response_model=MentionsResponse)
async def get_mentions(
    project_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Per-query mention breakdown for the latest run."""
    project = await _verify_ownership(project_id, user, db)
    run = await _get_latest_run(db, project_id)

    if not run:
        return MentionsResponse(mentions=[], total_mentioned=0, total_queries=0)

    # Get all queries for the project
    queries_result = await db.execute(
        select(Query).where(Query.project_id == project_id)
    )
    queries = queries_result.scalars().all()

    mentions_by_query = []
    total_mentioned = 0

    for query in queries:
        # For each query, check which providers mentioned the target brand
        results = await db.execute(
            select(Result)
            .options(selectinload(Result.mentions))
            .where(Result.run_id == run.id, Result.query_id == query.id)
        )
        query_results = results.scalars().all()

        providers = {}
        sentiment = None

        for r in query_results:
            target_mention = next(
                (m for m in r.mentions if m.is_target_brand), None
            )
            providers[r.provider.value] = target_mention is not None
            if target_mention and sentiment is None:
                sentiment = target_mention.sentiment.value

        mentioned = any(providers.values())
        if mentioned:
            total_mentioned += 1

        mentions_by_query.append(
            MentionsByQuery(
                query_id=query.id,
                query_text=query.text,
                providers=providers,
                sentiment=sentiment,
            )
        )

    return MentionsResponse(
        mentions=mentions_by_query,
        total_mentioned=total_mentioned,
        total_queries=len(queries),
    )


@router.get("/competitors", response_model=CompetitorComparisonResponse)
async def get_competitor_comparison(
    project_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Competitor comparison for the latest run."""
    project = await _verify_ownership(project_id, user, db)
    run = await _get_latest_run(db, project_id)

    if not run:
        return CompetitorComparisonResponse(scores=[], total_queries=0)

    # Get mention stats grouped by brand
    brand_stats = await db.execute(
        select(
            Mention.brand_name,
            func.count(distinct(Result.query_id)).label("mention_count"),
            func.avg(Mention.position).label("avg_position"),
        )
        .join(Result)
        .where(Result.run_id == run.id)
        .group_by(Mention.brand_name)
        .order_by(func.count(distinct(Result.query_id)).desc())
    )

    scores = []
    for row in brand_stats.all():
        scores.append(
            CompetitorScore(
                name=row.brand_name,
                mention_count=row.mention_count,
                mention_pct=round((row.mention_count / run.query_count) * 100, 1) if run.query_count else 0,
                avg_position=round(row.avg_position, 1),
                is_target=row.brand_name.lower() == project.brand_name.lower(),
            )
        )

    return CompetitorComparisonResponse(
        scores=scores,
        total_queries=run.query_count,
    )


@router.get("/trends", response_model=TrendsResponse)
async def get_trends(
    project_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Time-series data across completed runs."""
    await _verify_ownership(project_id, user, db)

    runs_result = await db.execute(
        select(MonitoringRun)
        .where(
            MonitoringRun.project_id == project_id,
            MonitoringRun.status == RunStatus.completed,
        )
        .order_by(MonitoringRun.completed_at.asc())
        .limit(52)  # up to a year of weekly data
    )
    runs = runs_result.scalars().all()

    data = []
    for run in runs:
        # Sentiment for this run
        sentiment_result = await db.execute(
            select(func.count(Mention.id))
            .join(Result)
            .where(
                Result.run_id == run.id,
                Mention.is_target_brand == True,
                Mention.sentiment == "positive",
            )
        )
        positive_count = sentiment_result.scalar_one()
        total = run.mention_count or 1

        data.append(
            TrendPoint(
                run_id=run.id,
                date=run.completed_at,
                visibility_score=run.mention_count,
                mention_count=run.mention_count,
                sentiment_positive_pct=round((positive_count / total) * 100, 1),
            )
        )

    return TrendsResponse(data=data)


@router.get("/sources", response_model=SourcesResponse)
async def get_sources(
    project_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cited sources aggregated by domain for the latest run."""
    await _verify_ownership(project_id, user, db)
    run = await _get_latest_run(db, project_id)

    if not run:
        return SourcesResponse(sources=[])

    source_stats = await db.execute(
        select(
            Citation.domain,
            func.count(Citation.id).label("citation_count"),
            func.array_agg(distinct(Result.provider)).label("providers"),
        )
        .join(Result)
        .where(Result.run_id == run.id)
        .group_by(Citation.domain)
        .order_by(func.count(Citation.id).desc())
        .limit(50)
    )

    sources = [
        SourceSummary(
            domain=row.domain,
            citation_count=row.citation_count,
            providers=[p.value for p in row.providers] if row.providers else [],
        )
        for row in source_stats.all()
    ]

    return SourcesResponse(sources=sources)


@router.get("/runs", response_model=RunsResponse)
async def get_runs(
    project_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List monitoring run history."""
    await _verify_ownership(project_id, user, db)

    result = await db.execute(
        select(MonitoringRun)
        .where(MonitoringRun.project_id == project_id)
        .order_by(MonitoringRun.created_at.desc())
        .limit(20)
    )

    return RunsResponse(runs=result.scalars().all())
