# These are what get sent to the AI providers.
import uuid

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, IDMixin, TimestampMixin


class Query(IDMixin, TimestampMixin, Base):
    __tablename__ = "queries"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    text: Mapped[str] = mapped_column(String(500), nullable=False)

    project: Mapped["Project"] = relationship(back_populates="queries")
    results: Mapped[list["Result"]] = relationship(back_populates="query", cascade="all, delete-orphan")
