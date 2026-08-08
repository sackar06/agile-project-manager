import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, StatementError
from app.core.database import Base
from app.models.enums import ProjectStatus, WorkItemStatus, PriorityLevel
from app.models.project import Project
from app.models.user_story import UserStory
from app.models.task import Task


from sqlalchemy.pool import StaticPool


@pytest.fixture
def db_session():
    """
    Creates an in-memory SQLite database session with foreign keys enabled for testing.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    
    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_1_create_project(db_session):
    project = Project(
        name="E-Commerce Website",
        description="Main online store front",
        status=ProjectStatus.ACTIVE
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    assert project.id is not None
    assert project.name == "E-Commerce Website"
    assert project.status == ProjectStatus.ACTIVE
    assert project.created_at is not None


def test_2_user_story_belongs_to_project(db_session):
    project = Project(name="E-Commerce Website", status=ProjectStatus.ACTIVE)
    db_session.add(project)
    db_session.commit()

    story = UserStory(
        project_id=project.id,
        title="Customer Login",
        description="Login functionality",
        status=WorkItemStatus.TODO,
        priority=PriorityLevel.HIGH
    )
    db_session.add(story)
    db_session.commit()
    db_session.refresh(story)

    assert story.id is not None
    assert story.project_id == project.id
    assert story.project.name == "E-Commerce Website"


def test_3_task_belongs_to_user_story(db_session):
    project = Project(name="E-Commerce Website")
    db_session.add(project)
    db_session.commit()

    story = UserStory(project_id=project.id, title="Customer Login")
    db_session.add(story)
    db_session.commit()

    task = Task(
        user_story_id=story.id,
        title="Create login API",
        description="Implement POST /auth/login",
        status=WorkItemStatus.IN_PROGRESS,
        priority=PriorityLevel.HIGH,
        assigned_to="Alice"
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    assert task.id is not None
    assert task.user_story_id == story.id
    assert task.user_story.title == "Customer Login"
    assert task.assigned_to == "Alice"


def test_4_project_retrieves_user_stories(db_session):
    project = Project(name="E-Commerce Website")
    db_session.add(project)
    db_session.commit()

    story1 = UserStory(project_id=project.id, title="Customer Login")
    story2 = UserStory(project_id=project.id, title="Shopping Cart")
    db_session.add_all([story1, story2])
    db_session.commit()

    db_session.refresh(project)
    assert len(project.user_stories) == 2
    story_titles = [s.title for s in project.user_stories]
    assert "Customer Login" in story_titles
    assert "Shopping Cart" in story_titles


def test_5_user_story_retrieves_tasks(db_session):
    project = Project(name="E-Commerce Website")
    db_session.add(project)
    db_session.commit()

    story = UserStory(project_id=project.id, title="Customer Login")
    db_session.add(story)
    db_session.commit()

    task1 = Task(user_story_id=story.id, title="Create login API")
    task2 = Task(user_story_id=story.id, title="Create login page")
    task3 = Task(user_story_id=story.id, title="Add authentication validation")
    db_session.add_all([task1, task2, task3])
    db_session.commit()

    db_session.refresh(story)
    assert len(story.tasks) == 3
    task_titles = [t.title for t in story.tasks]
    assert "Create login API" in task_titles
    assert "Create login page" in task_titles
    assert "Add authentication validation" in task_titles


def test_6_invalid_foreign_key_rejected(db_session):
    # Attempt to create UserStory with non-existent project_id 9999
    invalid_story = UserStory(project_id=9999, title="Orphan Story")
    db_session.add(invalid_story)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_7_required_fields_validated(db_session):
    # Attempt to create Project without required name
    invalid_project = Project(name=None)
    db_session.add(invalid_project)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_8_status_values_restricted(db_session):
    project = Project(name="Test Project")
    db_session.add(project)
    db_session.commit()

    # Attempt to pass an invalid status string to UserStory
    invalid_story = UserStory(project_id=project.id, title="Invalid Status Story", status="INVALID_STATUS")
    db_session.add(invalid_story)

    with pytest.raises((StatementError, IntegrityError, ValueError, LookupError)):
        db_session.commit()
    db_session.rollback()


def test_9_priority_values_restricted(db_session):
    project = Project(name="Test Project")
    db_session.add(project)
    db_session.commit()

    # Attempt to pass an invalid priority string to Task
    story = UserStory(project_id=project.id, title="Story")
    db_session.add(story)
    db_session.commit()

    invalid_task = Task(user_story_id=story.id, title="Task", priority="SUPER_HIGH")
    db_session.add(invalid_task)

    with pytest.raises((StatementError, IntegrityError, ValueError, LookupError)):
        db_session.commit()
    db_session.rollback()



def test_10_cascade_delete(db_session):
    project = Project(name="E-Commerce Website")
    db_session.add(project)
    db_session.commit()

    story = UserStory(project_id=project.id, title="Customer Login")
    db_session.add(story)
    db_session.commit()

    task = Task(user_story_id=story.id, title="Create login API")
    db_session.add(task)
    db_session.commit()

    # Delete project
    db_session.delete(project)
    db_session.commit()

    # Assert children are deleted
    assert db_session.query(UserStory).filter(UserStory.id == story.id).first() is None
    assert db_session.query(Task).filter(Task.id == task.id).first() is None


def test_11_report_job_cascade_delete(db_session):
    from app.models.report_job import ReportJob
    from app.models.enums import JobStatus

    project = Project(name="Report Cascade Proj")
    db_session.add(project)
    db_session.commit()

    job = ReportJob(project_id=project.id, status=JobStatus.PENDING)
    db_session.add(job)
    db_session.commit()

    db_session.delete(project)
    db_session.commit()

    assert db_session.query(ReportJob).filter(ReportJob.id == job.id).first() is None


def test_12_timestamps_auto_populate(db_session):
    project = Project(name="Timestamp Proj")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    assert project.created_at is not None
    assert project.updated_at is not None

