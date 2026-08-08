import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import Base, get_db
from app.models.enums import JobStatus, WorkItemStatus
from app.services.report_service import ReportService, MAX_ATTEMPTS


@pytest.fixture
def client_and_session():
    """
    Creates a shared in-memory SQLite DB for testing async report jobs and API endpoints.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    from app.models import Project, UserStory, Task, ReportJob

    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client, TestingSessionLocal
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_01_request_report_for_existing_project(client_and_session):
    client, session_factory = client_and_session
    p_res = client.post("/api/v1/projects", json={"name": "Report Test Project"})
    project_id = p_res.json()["id"]

    res = client.post(f"/api/v1/projects/{project_id}/reports")
    assert res.status_code == 202
    data = res.json()
    assert "job_id" in data
    assert data["status"] == "PENDING"
    assert data["message"] == "Report generation started"


def test_02_request_report_for_nonexistent_project(client_and_session):
    client, _ = client_and_session
    res = client.post("/api/v1/projects/99999/reports")
    assert res.status_code == 404
    assert res.json()["detail"] == "Project with id 99999 not found"


def test_03_04_05_background_processing_completion_and_statistics(client_and_session):
    client, session_factory = client_and_session

    # Create Project
    p_res = client.post("/api/v1/projects", json={"name": "Analytics Proj", "status": "ACTIVE"})
    project_id = p_res.json()["id"]

    # Create 2 User Stories
    s1_res = client.post(f"/api/v1/projects/{project_id}/stories", json={"title": "Story 1", "project_id": project_id, "status": "DONE"})
    s2_res = client.post(f"/api/v1/projects/{project_id}/stories", json={"title": "Story 2", "project_id": project_id, "status": "IN_PROGRESS"})
    s1_id = s1_res.json()["id"]
    s2_id = s2_res.json()["id"]

    # Create Tasks (3 tasks total, 2 DONE -> 66.67% completion)
    client.post(f"/api/v1/stories/{s1_id}/tasks", json={"title": "T1", "status": "DONE", "user_story_id": s1_id})
    client.post(f"/api/v1/stories/{s1_id}/tasks", json={"title": "T2", "status": "DONE", "user_story_id": s1_id})
    client.post(f"/api/v1/stories/{s2_id}/tasks", json={"title": "T3", "status": "TODO", "user_story_id": s2_id})

    # Request report
    post_res = client.post(f"/api/v1/projects/{project_id}/reports")
    assert post_res.status_code == 202
    job_id = post_res.json()["job_id"]

    # Execute background worker explicitly for testing determinism
    ReportService.execute_background_job(job_id, session_factory)

    # Check GET endpoint
    get_res = client.get(f"/api/v1/reports/{job_id}")
    assert get_res.status_code == 200
    job_data = get_res.json()
    assert job_data["status"] == "COMPLETED"
    assert job_data["report_data"] is not None

    rep = job_data["report_data"]
    assert rep["project_name"] == "Analytics Proj"
    assert rep["user_stories"]["total"] == 2
    assert rep["user_stories"]["done"] == 1
    assert rep["user_stories"]["in_progress"] == 1
    assert rep["tasks"]["total"] == 3
    assert rep["tasks"]["done"] == 2
    assert rep["tasks"]["todo"] == 1
    assert rep["task_completion_percentage"] == 66.67


def test_06_07_08_09_failure_and_bounded_retry(client_and_session):
    client, session_factory = client_and_session
    p_res = client.post("/api/v1/projects", json={"name": "Failure Test Proj"})
    project_id = p_res.json()["id"]

    post_res = client.post(f"/api/v1/projects/{project_id}/reports")
    job_id = post_res.json()["job_id"]

    # Mock calculate_project_statistics to raise exception
    with patch.object(ReportService, "calculate_project_statistics", side_effect=ValueError("Simulated DB calculation error")):
        ReportService.execute_background_job(job_id, session_factory)

    # Poll status
    get_res = client.get(f"/api/v1/reports/{job_id}")
    assert get_res.status_code == 200
    job_data = get_res.json()
    assert job_data["status"] == "FAILED"
    assert job_data["attempts"] == MAX_ATTEMPTS
    assert "Simulated DB calculation error" in job_data["error_message"]


def test_10_get_nonexistent_report_job(client_and_session):
    client, _ = client_and_session
    res = client.get("/api/v1/reports/99999")
    assert res.status_code == 404
    assert res.json()["detail"] == "Report job with id 99999 not found"


def test_11_idempotent_duplicate_job_request(client_and_session):
    client, session_factory = client_and_session
    p_res = client.post("/api/v1/projects", json={"name": "Idempotent Proj"})
    project_id = p_res.json()["id"]

    res1 = client.post(f"/api/v1/projects/{project_id}/reports")
    job_id_1 = res1.json()["job_id"]

    # Request report again before worker finishes
    res2 = client.post(f"/api/v1/projects/{project_id}/reports")
    job_id_2 = res2.json()["job_id"]

    assert job_id_1 == job_id_2
    assert res2.json()["message"] == "Existing report job currently in progress"
