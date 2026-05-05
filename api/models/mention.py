import enum
import uuid

from sqlalchemy import String, Text, Integer, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, IDMixin, TimestampMixin


class Sentiment(str, enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class Mention(IDMixin, TimestampMixin, Base):
    __tablename__ = "mentions"

    result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("results.id", ondelete="CASCADE"), nullable=False
    )
    brand_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    is_target_brand: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sentiment: Mapped[Sentiment] = mapped_column(Enum(Sentiment), nullable=False)
    context: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    result: Mapped["Result"] = relationship(back_populates="mentions")
