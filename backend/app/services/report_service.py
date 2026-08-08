from datetime import datetime, timezone
from typing import Dict, Optional, Tuple, Any
from sqlalchemy.orm import Session, sessionmaker
from app.repositories.report_job_repository import ReportJobRepository
from app.repositories.project_repository import ProjectRepository
from app.models.report_job import ReportJob
from app.models.enums import JobStatus, WorkItemStatus
from app.models.project import Project
from app.models.user_story import UserStory
from app.models.task import Task

MAX_ATTEMPTS = 3


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ReportService:
    def __init__(self, repository: ReportJobRepository, project_repository: ProjectRepository):
        self.repository = repository
        self.project_repository = project_repository

    def get_job(self, job_id: int) -> Optional[ReportJob]:
        return self.repository.get_by_id(job_id)

    def request_project_report(self, project_id: int) -> Optional[Tuple[ReportJob, bool]]:
        """
        Creates a new ReportJob or reuses an existing active PENDING/RUNNING job for idempotency.
        Returns Tuple of (ReportJob, is_newly_created).
        Returns None if Project does not exist.
        """
        project = self.project_repository.get_by_id(project_id)
        if not project:
            return None

        # Check for active existing job (idempotency rule)
        active_job = self.repository.get_active_job_for_project(project_id)
        if active_job:
            return active_job, False

        new_job = ReportJob(
            project_id=project_id,
            status=JobStatus.PENDING,
            attempts=0
        )
        created_job = self.repository.create(new_job)
        return created_job, True

    @staticmethod
    def calculate_project_statistics(db: Session, project_id: int) -> Dict[str, Any]:
        """
        Pure calculation function retrieving actual Project -> User Stories -> Tasks data.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project with id {project_id} does not exist.")

        stories = db.query(UserStory).filter(UserStory.project_id == project_id).all()
        story_ids = [s.id for s in stories]

        tasks = []
        if story_ids:
            tasks = db.query(Task).filter(Task.user_story_id.in_(story_ids)).all()

        # Story status counts
        stories_total = len(stories)
        stories_todo = sum(1 for s in stories if s.status == WorkItemStatus.TODO)
        stories_in_progress = sum(1 for s in stories if s.status == WorkItemStatus.IN_PROGRESS)
        stories_done = sum(1 for s in stories if s.status == WorkItemStatus.DONE)

        # Task status counts
        tasks_total = len(tasks)
        tasks_todo = sum(1 for t in tasks if t.status == WorkItemStatus.TODO)
        tasks_in_progress = sum(1 for t in tasks if t.status == WorkItemStatus.IN_PROGRESS)
        tasks_done = sum(1 for t in tasks if t.status == WorkItemStatus.DONE)

        completion_percentage = (
            round((tasks_done / tasks_total) * 100.0, 2) if tasks_total > 0 else 0.0
        )

        return {
            "project_id": project.id,
            "project_name": project.name,
            "project_status": project.status.value,
            "user_stories": {
                "total": stories_total,
                "todo": stories_todo,
                "in_progress": stories_in_progress,
                "done": stories_done
            },
            "tasks": {
                "total": tasks_total,
                "todo": tasks_todo,
                "in_progress": tasks_in_progress,
                "done": tasks_done
            },
            "task_completion_percentage": completion_percentage
        }

    @classmethod
    def execute_background_job(cls, job_id: int, session_factory: sessionmaker, raise_on_failure_for_testing: bool = False):
        """
        Background task worker execution function with bounded retries (MAX_ATTEMPTS = 3).
        """
        db: Session = session_factory()
        repo = ReportJobRepository(db)

        try:
            job = repo.get_by_id(job_id)
            if not job:
                return

            while job.attempts < MAX_ATTEMPTS:
                job.attempts += 1
                job.status = JobStatus.RUNNING
                if not job.started_at:
                    job.started_at = utc_now()
                repo.update(job)

                try:
                    stats = cls.calculate_project_statistics(db, job.project_id)
                    job.report_data = stats
                    job.status = JobStatus.COMPLETED
                    job.completed_at = utc_now()
                    job.error_message = None
                    repo.update(job)
                    break  # Success!
                except Exception as exc:
                    job.error_message = str(exc)
                    if job.attempts >= MAX_ATTEMPTS:
                        job.status = JobStatus.FAILED
                        repo.update(job)
                        if raise_on_failure_for_testing:
                            raise exc
                        break
                    else:
                        repo.update(job)
        finally:
            db.close()
