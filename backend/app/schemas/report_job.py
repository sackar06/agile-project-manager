from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import JobStatus


class StoryStatusBreakdown(BaseModel):
    total: int = 0
    todo: int = 0
    in_progress: int = 0
    done: int = 0


class TaskStatusBreakdown(BaseModel):
    total: int = 0
    todo: int = 0
    in_progress: int = 0
    done: int = 0


class ProjectReportData(BaseModel):
    project_id: int
    project_name: str
    project_status: str
    user_stories: StoryStatusBreakdown
    tasks: TaskStatusBreakdown
    task_completion_percentage: float = 0.0


class ReportJobCreateResponse(BaseModel):
    job_id: int = Field(..., json_schema_extra={"example": 1})
    status: JobStatus = Field(..., json_schema_extra={"example": "PENDING"})
    message: str = Field(default="Report generation started", json_schema_extra={"example": "Report generation started"})


class ReportJobResponse(BaseModel):
    job_id: int = Field(..., alias="id")
    project_id: int
    status: JobStatus
    attempts: int
    error_message: Optional[str] = None
    report_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
