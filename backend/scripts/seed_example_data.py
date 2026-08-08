import sys
import os

# Add backend directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base, SessionLocal
from app.models.enums import ProjectStatus, WorkItemStatus, PriorityLevel
from app.models.project import Project
from app.models.user_story import UserStory
from app.models.task import Task


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("Seeding database with example records...")

        # 1. Create Project
        project = Project(
            name="E-Commerce Website",
            description="Main online store front initiative for small team project management",
            status=ProjectStatus.ACTIVE
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        print(f"Created Project: ID={project.id}, Name='{project.name}', Status={project.status.value}")

        # 2. Create User Story
        user_story = UserStory(
            project_id=project.id,
            title="Customer Login",
            description="As a customer, I want to securely log in to access my user dashboard.",
            status=WorkItemStatus.IN_PROGRESS,
            priority=PriorityLevel.HIGH
        )
        db.add(user_story)
        db.commit()
        db.refresh(user_story)
        print(f"Created User Story: ID={user_story.id}, Title='{user_story.title}', ProjectID={user_story.project_id}")

        # 3. Create Tasks
        tasks_data = [
            ("Create login API", "Implement POST /api/v1/auth/login with Pydantic validation", WorkItemStatus.DONE, PriorityLevel.HIGH, "Alice"),
            ("Create login page", "Build React login page component with glassmorphism UI", WorkItemStatus.IN_PROGRESS, PriorityLevel.HIGH, "Bob"),
            ("Add authentication validation", "Add form input validation and error feedback messages", WorkItemStatus.TODO, PriorityLevel.MEDIUM, "Charlie"),
        ]

        for title, desc, status, priority, assignee in tasks_data:
            task = Task(
                user_story_id=user_story.id,
                title=title,
                description=desc,
                status=status,
                priority=priority,
                assigned_to=assignee
            )
            db.add(task)
            print(f"  * Created Task: Title='{task.title}', Status={status.value}, AssignedTo={assignee}")

        db.commit()
        print("\nSeed completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
