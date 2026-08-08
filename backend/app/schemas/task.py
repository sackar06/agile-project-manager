from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import WorkItemStatus, PriorityLevel


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, json_schema_extra={"example": "Create login API"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "Implement POST /api/v1/auth/login endpoint"})
    status: WorkItemStatus = Field(default=WorkItemStatus.TODO)
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    assigned_to: Optional[str] = Field(None, max_length=100, json_schema_extra={"example": "Alice"})


class TaskCreate(TaskBase):
    user_story_id: int = Field(..., json_schema_extra={"example": 1})


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[WorkItemStatus] = None
    priority: Optional[PriorityLevel] = None
    assigned_to: Optional[str] = None
    user_story_id: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    user_story_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
