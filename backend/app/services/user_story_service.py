from typing import Tuple, List, Optional
from app.repositories.user_story_repository import UserStoryRepository
from app.repositories.project_repository import ProjectRepository
from app.models.user_story import UserStory
from app.schemas.user_story import UserStoryCreate, UserStoryUpdate


class UserStoryService:
    def __init__(self, repository: UserStoryRepository, project_repository: ProjectRepository):
        self.repository = repository
        self.project_repository = project_repository

    def get_user_story(self, user_story_id: int) -> Optional[UserStory]:
        return self.repository.get_by_id(user_story_id)

    def list_user_stories_for_project_paginated(
        self, project_id: int, page: int = 1, page_size: int = 10
    ) -> Optional[Tuple[List[UserStory], int]]:
        project = self.project_repository.get_by_id(project_id)
        if not project:
            return None

        skip = (page - 1) * page_size
        items = self.repository.get_by_project_id(project_id, skip=skip, limit=page_size)
        total = self.repository.get_count_by_project(project_id)
        return items, total

    def create_user_story(self, project_id: int, schema: UserStoryCreate) -> Optional[UserStory]:
        project = self.project_repository.get_by_id(project_id)
        if not project:
            return None

        user_story = UserStory(
            project_id=project_id,
            title=schema.title,
            description=schema.description,
            status=schema.status,
            priority=schema.priority
        )
        return self.repository.create(user_story)

    def update_user_story(self, user_story_id: int, schema: UserStoryUpdate) -> Optional[UserStory]:
        user_story = self.repository.get_by_id(user_story_id)
        if not user_story:
            return None

        if schema.title is not None:
            user_story.title = schema.title
        if schema.description is not None:
            user_story.description = schema.description
        if schema.status is not None:
            user_story.status = schema.status
        if schema.priority is not None:
            user_story.priority = schema.priority
        if schema.project_id is not None:
            # Check target project exists if moving story
            target_proj = self.project_repository.get_by_id(schema.project_id)
            if not target_proj:
                return None
            user_story.project_id = schema.project_id

        return self.repository.update(user_story)

    def delete_user_story(self, user_story_id: int) -> bool:
        user_story = self.repository.get_by_id(user_story_id)
        if not user_story:
            return False
        self.repository.delete(user_story)
        return True
