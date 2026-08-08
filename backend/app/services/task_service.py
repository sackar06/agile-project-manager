from typing import Tuple, List, Optional
from app.repositories.task_repository import TaskRepository
from app.repositories.user_story_repository import UserStoryRepository
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, repository: TaskRepository, user_story_repository: UserStoryRepository):
        self.repository = repository
        self.user_story_repository = user_story_repository

    def get_task(self, task_id: int) -> Optional[Task]:
        return self.repository.get_by_id(task_id)

    def list_tasks_for_user_story_paginated(
        self, user_story_id: int, page: int = 1, page_size: int = 10
    ) -> Optional[Tuple[List[Task], int]]:
        user_story = self.user_story_repository.get_by_id(user_story_id)
        if not user_story:
            return None

        skip = (page - 1) * page_size
        items = self.repository.get_by_user_story_id(user_story_id, skip=skip, limit=page_size)
        total = self.repository.get_count_by_story(user_story_id)
        return items, total

    def create_task(self, user_story_id: int, schema: TaskCreate) -> Optional[Task]:
        user_story = self.user_story_repository.get_by_id(user_story_id)
        if not user_story:
            return None

        task = Task(
            user_story_id=user_story_id,
            title=schema.title,
            description=schema.description,
            status=schema.status,
            priority=schema.priority,
            assigned_to=schema.assigned_to
        )
        return self.repository.create(task)

    def update_task(self, task_id: int, schema: TaskUpdate) -> Optional[Task]:
        task = self.repository.get_by_id(task_id)
        if not task:
            return None

        if schema.title is not None:
            task.title = schema.title
        if schema.description is not None:
            task.description = schema.description
        if schema.status is not None:
            task.status = schema.status
        if schema.priority is not None:
            task.priority = schema.priority
        if schema.assigned_to is not None:
            task.assigned_to = schema.assigned_to
        if schema.user_story_id is not None:
            target_story = self.user_story_repository.get_by_id(schema.user_story_id)
            if not target_story:
                return None
            task.user_story_id = schema.user_story_id

        return self.repository.update(task)

    def delete_task(self, task_id: int) -> bool:
        task = self.repository.get_by_id(task_id)
        if not task:
            return False
        self.repository.delete(task)
        return True
