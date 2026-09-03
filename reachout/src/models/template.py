from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from reachout.src.models.base import Base

if TYPE_CHECKING:
    from reachout.src.models.user import Manager
    from reachout.src.models.campaign import Campaign


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    manager_id: Mapped[int] = mapped_column(ForeignKey("managers.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    body: Mapped[Text] = mapped_column(Text, nullable=False)

    manager: Mapped["Manager"] = relationship("Manager", back_populates="templates", init=False)
    campaigns: Mapped[list["Campaign"]] = relationship("Campaign", back_populates="template", cascade="all, delete-orphan", init=False)
