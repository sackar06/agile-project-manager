from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.project_repository import ProjectRepository
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailResponse
from app.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/projects", tags=["Projects"])


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    repo = ProjectRepository(db)
    return ProjectService(repo)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a Project",
    description="Create a new Project entity in the Agile management hierarchy."
)
def create_project(
    project_in: ProjectCreate,
    service: ProjectService = Depends(get_project_service)
) -> ProjectResponse:
    return service.create_project(project_in)


@router.get(
    "",
    response_model=PaginatedResponse[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List Projects",
    description="Get a paginated list of all projects."
)
def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    service: ProjectService = Depends(get_project_service)
) -> PaginatedResponse[ProjectResponse]:
    items, total = service.list_projects_paginated(page=page, page_size=page_size)
    return PaginatedResponse[ProjectResponse](
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Project Details",
    description="Get a project by ID, exposing its associated User Stories."
)
def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service)
) -> ProjectDetailResponse:
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    return project


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Project",
    description="Update an existing project's fields."
)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    service: ProjectService = Depends(get_project_service)
) -> ProjectResponse:
    updated = service.update_project(project_id, project_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    return updated


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Project",
    description="Delete a project and automatically cascade-delete all its User Stories and Tasks."
)
def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service)
) -> None:
    success = service.delete_project(project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    return None
