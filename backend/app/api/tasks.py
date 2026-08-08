from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.task_repository import TaskRepository
from app.repositories.user_story_repository import UserStoryRepository
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.schemas.pagination import PaginatedResponse

router = APIRouter(tags=["Tasks"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    task_repo = TaskRepository(db)
    story_repo = UserStoryRepository(db)
    return TaskService(task_repo, story_repo)


@router.post(
    "/stories/{story_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Task under User Story",
    description="Create a new Task associated with a parent User Story."
)
def create_task_for_user_story(
    story_id: int,
    task_in: TaskCreate,
    service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    task = service.create_task(story_id, task_in)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User story with id {story_id} not found"
        )
    return task


@router.get(
    "/stories/{story_id}/tasks",
    response_model=PaginatedResponse[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List Tasks for User Story",
    description="Get a paginated list of Tasks belonging to a specific User Story."
)
def list_tasks_for_user_story(
    story_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    service: TaskService = Depends(get_task_service)
) -> PaginatedResponse[TaskResponse]:
    result = service.list_tasks_for_user_story_paginated(
        user_story_id=story_id, page=page, page_size=page_size
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User story with id {story_id} not found"
        )
    items, total = result
    return PaginatedResponse[TaskResponse](
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Task Details",
    description="Get a single Task by its ID."
)
def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task


@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Task",
    description="Update an existing Task's title, description, status, priority, or assigned_to."
)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    updated = service.update_task(task_id, task_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return updated


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Task",
    description="Delete a single Task."
)
def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service)
) -> None:
    success = service.delete_task(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return None
