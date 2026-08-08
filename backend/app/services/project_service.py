from typing import Tuple, List, Optional
from app.repositories.project_repository import ProjectRepository
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def get_project(self, project_id: int) -> Optional[Project]:
        return self.repository.get_by_id(project_id)

    def list_projects_paginated(self, page: int = 1, page_size: int = 10) -> Tuple[List[Project], int]:
        skip = (page - 1) * page_size
        items = self.repository.get_all(skip=skip, limit=page_size)
        total = self.repository.get_count()
        return items, total

    def create_project(self, schema: ProjectCreate) -> Project:
        project = Project(
            name=schema.name,
            description=schema.description,
            status=schema.status
        )
        return self.repository.create(project)

    def update_project(self, project_id: int, schema: ProjectUpdate) -> Optional[Project]:
        project = self.repository.get_by_id(project_id)
        if not project:
            return None

        if schema.name is not None:
            project.name = schema.name
        if schema.description is not None:
            project.description = schema.description
        if schema.status is not None:
            project.status = schema.status

        return self.repository.update(project)

    def delete_project(self, project_id: int) -> bool:
        project = self.repository.get_by_id(project_id)
        if not project:
            return False
        self.repository.delete(project)
        return True
