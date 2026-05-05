import uuid
from datetime import datetime

from pydantic import BaseModel


# --- Overview ---

class OverviewResponse(BaseModel):
    visibility_score: int  # 0-100
    total_mentions: int
    total_queries: int
    competitor_gap: int  # positive = leading, negative = trailing
    sentiment_positive_pct: float
    last_run_at: datetime | None


# --- Mentions ---

class MentionDetail(BaseModel):
    query_text: str
    provider: str
    brand_name: str
    is_target_brand: bool
    sentiment: str
    context: str
    position: int

    model_config = {"from_attributes": True}


class MentionsByQuery(BaseModel):
    query_id: uuid.UUID
    query_text: str
    providers: dict[str, bool]  # {"chatgpt": True, "gemini": False, ...}
    sentiment: str | None  # overall sentiment when mentioned


class MentionsResponse(BaseModel):
    mentions: list[MentionsByQuery]
    total_mentioned: int  # queries where brand appears
    total_queries: int


# --- Competitors ---

class CompetitorScore(BaseModel):
    name: str
    mention_count: int
    mention_pct: float  # % of queries where mentioned
    avg_position: float
    is_target: bool


class CompetitorComparisonResponse(BaseModel):
    scores: list[CompetitorScore]
    total_queries: int


# --- Trends ---

class TrendPoint(BaseModel):
    run_id: uuid.UUID
    date: datetime
    visibility_score: int
    mention_count: int
    sentiment_positive_pct: float


class TrendsResponse(BaseModel):
    data: list[TrendPoint]


# --- Sources ---

class SourceSummary(BaseModel):
    domain: str
    citation_count: int
    providers: list[str]  # which providers cite this domain


class SourcesResponse(BaseModel):
    sources: list[SourceSummary]


# --- Runs ---

class RunSummary(BaseModel):
    id: uuid.UUID
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    query_count: int
    mention_count: int

    model_config = {"from_attributes": True}


class RunsResponse(BaseModel):
    runs: list[RunSummary]
