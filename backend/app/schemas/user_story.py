from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import WorkItemStatus, PriorityLevel


class UserStoryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, json_schema_extra={"example": "Customer Login"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "As a customer, I want to log in using my email and password."})
    status: WorkItemStatus = Field(default=WorkItemStatus.TODO)
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)


class UserStoryCreate(UserStoryBase):
    project_id: int = Field(..., json_schema_extra={"example": 1})


class UserStoryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[WorkItemStatus] = None
    priority: Optional[PriorityLevel] = None
    project_id: Optional[int] = None


class UserStoryResponse(UserStoryBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
