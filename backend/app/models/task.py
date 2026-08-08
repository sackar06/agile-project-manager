from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enums import WorkItemStatus, PriorityLevel

if TYPE_CHECKING:
    from app.models.user_story import UserStory


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_story_id: Mapped[int] = mapped_column(
        ForeignKey("user_stories.id", ondelete="CASCADE"),
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
    assigned_to: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
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
    user_story: Mapped["UserStory"] = relationship(
        "UserStory",
        back_populates="tasks"
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, user_story_id={self.user_story_id}, title='{self.title}', status='{self.status}')>"
