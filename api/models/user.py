from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    user_uid: Mapped[str] = mapped_column(String(128), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    paystack_customer_code: Mapped[str | None] = mapped_column(String(255), nullable=True)

    projects: Mapped[list["Project"]] = relationship(back_populates="user", cascade="all, delete-orphan")