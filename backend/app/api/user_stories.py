from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.user_story_repository import UserStoryRepository
from app.repositories.project_repository import ProjectRepository
from app.services.user_story_service import UserStoryService
from app.schemas.user_story import UserStoryCreate, UserStoryUpdate, UserStoryResponse
from app.schemas.pagination import PaginatedResponse

router = APIRouter(tags=["User Stories"])


def get_user_story_service(db: Session = Depends(get_db)) -> UserStoryService:
    story_repo = UserStoryRepository(db)
    proj_repo = ProjectRepository(db)
    return UserStoryService(story_repo, proj_repo)


@router.post(
    "/projects/{project_id}/stories",
    response_model=UserStoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User Story under Project",
    description="Create a new User Story associated with a parent Project."
)
def create_user_story_for_project(
    project_id: int,
    story_in: UserStoryCreate,
    service: UserStoryService = Depends(get_user_story_service)
) -> UserStoryResponse:
    story = service.create_user_story(project_id, story_in)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    return story


@router.get(
    "/projects/{project_id}/stories",
    response_model=PaginatedResponse[UserStoryResponse],
    status_code=status.HTTP_200_OK,
    summary="List User Stories for Project",
    description="Get a paginated list of User Stories belonging to a specific Project."
)
def list_user_stories_for_project(
    project_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    service: UserStoryService = Depends(get_user_story_service)
) -> PaginatedResponse[UserStoryResponse]:
    result = service.list_user_stories_for_project_paginated(
        project_id=project_id, page=page, page_size=page_size
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    items, total = result
    return PaginatedResponse[UserStoryResponse](
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )


@router.get(
    "/stories/{story_id}",
    response_model=UserStoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User Story Details",
    description="Get a single User Story by its ID."
)
def get_user_story(
    story_id: int,
    service: UserStoryService = Depends(get_user_story_service)
) -> UserStoryResponse:
    story = service.get_user_story(story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User story with id {story_id} not found"
        )
    return story


@router.put(
    "/stories/{story_id}",
    response_model=UserStoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update User Story",
    description="Update an existing User Story's title, description, status, or priority."
)
def update_user_story(
    story_id: int,
    story_in: UserStoryUpdate,
    service: UserStoryService = Depends(get_user_story_service)
) -> UserStoryResponse:
    updated = service.update_user_story(story_id, story_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User story with id {story_id} not found"
        )
    return updated


@router.delete(
    "/stories/{story_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete User Story",
    description="Delete a User Story and cascade-delete its child Tasks."
)
def delete_user_story(
    story_id: int,
    service: UserStoryService = Depends(get_user_story_service)
) -> None:
    success = service.delete_user_story(story_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User story with id {story_id} not found"
        )
    return None
