import enum
import uuid

from sqlalchemy import Text, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, IDMixin, TimestampMixin


class Provider(str, enum.Enum):
    chatgpt = "chatgpt"
    gemini = "gemini"
    perplexity = "perplexity"
    ai_overview = "ai_overview"


class Result(IDMixin, TimestampMixin, Base):
    __tablename__ = "results"

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("monitoring_runs.id", ondelete="CASCADE"), nullable=False
    )
    query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("queries.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[Provider] = mapped_column(Enum(Provider), nullable=False)
    raw_response: Mapped[str] = mapped_column(Text, nullable=False)

    run: Mapped["MonitoringRun"] = relationship(back_populates="results")
    query: Mapped["Query"] = relationship(back_populates="results")
    mentions: Mapped[list["Mention"]] = relationship(back_populates="result", cascade="all, delete-orphan")
    citations: Mapped[list["Citation"]] = relationship(back_populates="result", cascade="all, delete-orphan")
