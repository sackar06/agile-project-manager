from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user_story import UserStory


class UserStoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_story_id: int) -> Optional[UserStory]:
        return self.db.query(UserStory).filter(UserStory.id == user_story_id).first()

    def get_by_project_id(self, project_id: int, skip: int = 0, limit: int = 100) -> List[UserStory]:
        return (
            self.db.query(UserStory)
            .filter(UserStory.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_count_by_project(self, project_id: int) -> int:
        return self.db.query(UserStory).filter(UserStory.project_id == project_id).count()

    def create(self, user_story: UserStory) -> UserStory:
        self.db.add(user_story)
        self.db.commit()
        self.db.refresh(user_story)
        return user_story

    def update(self, user_story: UserStory) -> UserStory:
        self.db.commit()
        self.db.refresh(user_story)
        return user_story

    def delete(self, user_story: UserStory) -> None:
        self.db.delete(user_story)
        self.db.commit()
