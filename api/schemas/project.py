import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# --- Competitors ---

class CompetitorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class CompetitorResponse(BaseModel):
    id: uuid.UUID
    name: str

    model_config = {"from_attributes": True}


# --- Queries ---

class QueryCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)


class QueryResponse(BaseModel):
    id: uuid.UUID
    text: str

    model_config = {"from_attributes": True}


# --- Projects ---

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    brand_name: str = Field(..., min_length=1, max_length=255)
    competitors: list[CompetitorCreate] = Field(default_factory=list, max_length=5)
    queries: list[QueryCreate] = Field(default_factory=list, max_length=20)


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    brand_name: str | None = Field(None, min_length=1, max_length=255)
    is_active: bool | None = None


class ProjectSummary(BaseModel):
    """List view — lightweight, no nested relations."""

    id: uuid.UUID
    name: str
    brand_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectDetail(BaseModel):
    """Detail view — includes competitors and queries."""

    id: uuid.UUID
    name: str
    brand_name: str
    is_active: bool
    created_at: datetime
    competitors: list[CompetitorResponse]
    queries: list[QueryResponse]

    model_config = {"from_attributes": True}
