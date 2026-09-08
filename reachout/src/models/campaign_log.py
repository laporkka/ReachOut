from sqlalchemy import ForeignKey, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

from reachout.src.models.base import Base


class Campaign_log(Base):
    __tablename__ = "campaign_logs"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False) 
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(timezone.utc), init=False)