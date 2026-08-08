from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db, SessionLocal
from app.repositories.report_job_repository import ReportJobRepository
from app.repositories.project_repository import ProjectRepository
from app.services.report_service import ReportService
from app.schemas.report_job import ReportJobCreateResponse, ReportJobResponse

router = APIRouter(tags=["Reports"])


def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    report_repo = ReportJobRepository(db)
    proj_repo = ProjectRepository(db)
    return ReportService(report_repo, proj_repo)


@router.post(
    "/projects/{project_id}/reports",
    response_model=ReportJobCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Request Project Progress Report Generation",
    description=(
        "Asynchronously request generation of a project progress report. "
        "Returns HTTP 202 Accepted immediately with a job_id for status polling."
    )
)
def request_project_report(
    project_id: int,
    background_tasks: BackgroundTasks,
    service: ReportService = Depends(get_report_service)
) -> ReportJobCreateResponse:
    result = service.request_project_report(project_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

    job, is_newly_created = result
    if is_newly_created:
        background_tasks.add_task(
            ReportService.execute_background_job,
            job.id,
            SessionLocal
        )
        msg = "Report generation started"
    else:
        msg = "Existing report job currently in progress"

    return ReportJobCreateResponse(
        job_id=job.id,
        status=job.status,
        message=msg
    )


@router.get(
    "/reports/{job_id}",
    response_model=ReportJobResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Report Generation Status",
    description="Poll progress report generation job status and retrieve generated report data."
)
def get_report_job_status(
    job_id: int,
    service: ReportService = Depends(get_report_service)
) -> ReportJobResponse:
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report job with id {job_id} not found"
        )
    return job
