from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import ProjectStatus
from app.schemas.user_story import UserStoryResponse


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "E-Commerce Website"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "Main online store front development initiative"})
    status: ProjectStatus = Field(default=ProjectStatus.PLANNING)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailResponse(ProjectResponse):
    user_stories: List[UserStoryResponse] = []

    model_config = ConfigDict(from_attributes=True)
