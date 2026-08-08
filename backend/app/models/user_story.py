from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enums import WorkItemStatus, PriorityLevel

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.task import Task


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserStory(Base):
    __tablename__ = "user_stories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[WorkItemStatus] = mapped_column(
        SQLEnum(WorkItemStatus, native_enum=False, validate_strings=True, values_callable=lambda x: [e.value for e in x]),
        default=WorkItemStatus.TODO,
        nullable=False
    )
    priority: Mapped[PriorityLevel] = mapped_column(
        SQLEnum(PriorityLevel, native_enum=False, validate_strings=True, values_callable=lambda x: [e.value for e in x]),
        default=PriorityLevel.MEDIUM,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="user_stories"
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="user_story",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<UserStory(id={self.id}, project_id={self.project_id}, title='{self.title}', status='{self.status}')>"
