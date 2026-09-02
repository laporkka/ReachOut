from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.contact import Contact
    from src.models.template import Template
    from src.models.campaign import Campaign


class Manager(Base):
    __tablename__ = "managers"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default_factory=lambda: datetime.now(timezone.utc), init=False)

    contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="manager", cascade="all, delete-orphan", init=False)
    templates: Mapped[list["Template"]] = relationship("Template", back_populates="manager", cascade="all, delete-orphan", init=False)
    campaigns: Mapped[list["Campaign"]] = relationship("Campaign", back_populates="manager", cascade="all, delete-orphan", init=False)
