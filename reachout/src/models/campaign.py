from typing import TYPE_CHECKING
from enum import Enum
from sqlalchemy import ForeignKey, String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from reachout.src.models.base import Base

if TYPE_CHECKING:
    from reachout.src.models.user import Manager
    from reachout.src.models.template import Template


class StatusEnum(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    

class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    manager_id: Mapped[int] = mapped_column(ForeignKey("managers.id", ondelete="CASCADE"), nullable=False)
    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    target_tag: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[StatusEnum] = mapped_column(SAEnum(StatusEnum), default=StatusEnum.PENDING, nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(nullable=True)
    total_recipients: Mapped[int] = mapped_column(default=0)
    sent_successfully: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default_factory=lambda: datetime.now(timezone.utc), init=False)
        
    manager: Mapped["Manager"] = relationship("Manager", back_populates="campaigns", init=False)
    template: Mapped["Template"] = relationship("Template", back_populates="campaigns", init=False)
