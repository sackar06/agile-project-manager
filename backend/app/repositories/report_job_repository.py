from typing import Optional
from sqlalchemy.orm import Session
from app.models.report_job import ReportJob
from app.models.enums import JobStatus


class ReportJobRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, job_id: int) -> Optional[ReportJob]:
        return self.db.query(ReportJob).filter(ReportJob.id == job_id).first()

    def get_active_job_for_project(self, project_id: int) -> Optional[ReportJob]:
        return (
            self.db.query(ReportJob)
            .filter(
                ReportJob.project_id == project_id,
                ReportJob.status.in_([JobStatus.PENDING, JobStatus.RUNNING])
            )
            .order_by(ReportJob.id.desc())
            .first()
        )

    def create(self, report_job: ReportJob) -> ReportJob:
        self.db.add(report_job)
        self.db.commit()
        self.db.refresh(report_job)
        return report_job

    def update(self, report_job: ReportJob) -> ReportJob:
        self.db.commit()
        self.db.refresh(report_job)
        return report_job
