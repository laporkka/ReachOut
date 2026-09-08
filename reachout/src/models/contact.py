from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, ARRAY, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from reachout.src.models.base import Base

if TYPE_CHECKING:
    from reachout.src.models.user import Manager
    

class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    manager_id: Mapped[int] = mapped_column(ForeignKey("managers.id", ondelete="CASCADE"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    birthday: Mapped[str] = mapped_column(String(255), nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(timezone.utc), init=False)
    
    manager: Mapped["Manager"] = relationship("Manager", back_populates="contacts", init=False)
