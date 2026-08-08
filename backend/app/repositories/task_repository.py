from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.task import Task


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, task_id: int) -> Optional[Task]:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_by_user_story_id(self, user_story_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        return (
            self.db.query(Task)
            .filter(Task.user_story_id == user_story_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_count_by_story(self, user_story_id: int) -> int:
        return self.db.query(Task).filter(Task.user_story_id == user_story_id).count()

    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task: Task) -> Task:
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()
