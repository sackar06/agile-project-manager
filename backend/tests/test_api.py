import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db


from sqlalchemy.pool import StaticPool


@pytest.fixture
def client_with_db():
    """
    Creates a fresh in-memory SQLite DB for testing API endpoints with foreign keys enabled.
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

    # Import models so Base metadata has all table definitions registered
    from app.models.project import Project
    from app.models.user_story import UserStory
    from app.models.task import Task

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
        yield client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)



# =====================================================================
# PROJECTS API TESTS
# =====================================================================

def test_01_create_project(client_with_db):
    res = client_with_db.post("/api/v1/projects", json={
        "name": "E-Commerce Store",
        "description": "Online storefront project",
        "status": "PLANNING"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["id"] is not None
    assert data["name"] == "E-Commerce Store"
    assert data["status"] == "PLANNING"


def test_02_get_all_projects(client_with_db):
    client_with_db.post("/api/v1/projects", json={"name": "Project A"})
    client_with_db.post("/api/v1/projects", json={"name": "Project B"})

    res = client_with_db.get("/api/v1/projects?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["page"] == 1


def test_03_get_project_by_id(client_with_db):
    create_res = client_with_db.post("/api/v1/projects", json={"name": "Project Alpha"})
    project_id = create_res.json()["id"]

    res = client_with_db.get(f"/api/v1/projects/{project_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == project_id
    assert data["name"] == "Project Alpha"
    assert "user_stories" in data


def test_04_update_project(client_with_db):
    create_res = client_with_db.post("/api/v1/projects", json={"name": "Old Project Name"})
    project_id = create_res.json()["id"]

    res = client_with_db.put(f"/api/v1/projects/{project_id}", json={
        "name": "New Project Name",
        "status": "ACTIVE"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "New Project Name"
    assert data["status"] == "ACTIVE"


def test_05_delete_project(client_with_db):
    create_res = client_with_db.post("/api/v1/projects", json={"name": "To Delete"})
    project_id = create_res.json()["id"]

    del_res = client_with_db.delete(f"/api/v1/projects/{project_id}")
    assert del_res.status_code == 204

    get_res = client_with_db.get(f"/api/v1/projects/{project_id}")
    assert get_res.status_code == 404


def test_06_get_nonexistent_project(client_with_db):
    res = client_with_db.get("/api/v1/projects/99999")
    assert res.status_code == 404
    assert res.json()["detail"] == "Project with id 99999 not found"


# =====================================================================
# USER STORIES API TESTS
# =====================================================================

def test_07_create_story_under_project(client_with_db):
    p_res = client_with_db.post("/api/v1/projects", json={"name": "E-Commerce"})
    project_id = p_res.json()["id"]

    res = client_with_db.post(f"/api/v1/projects/{project_id}/stories", json={
        "title": "Customer Login",
        "description": "Log in story",
        "status": "TODO",
        "priority": "HIGH",
        "project_id": project_id
    })
    assert res.status_code == 201
    data = res.json()
    assert data["id"] is not None
    assert data["project_id"] == project_id
    assert data["title"] == "Customer Login"


def test_08_get_stories_for_project(client_with_db):
    p_res = client_with_db.post("/api/v1/projects", json={"name": "E-Commerce"})
    project_id = p_res.json()["id"]

    client_with_db.post(f"/api/v1/projects/{project_id}/stories", json={"title": "Story 1", "project_id": project_id})
    client_with_db.post(f"/api/v1/projects/{project_id}/stories", json={"title": "Story 2", "project_id": project_id})

    res = client_with_db.get(f"/api/v1/projects/{project_id}/stories?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_09_get_story_by_id(client_with_db):
    p_res = client_with_db.post("/api/v1/projects", json={"name": "E-Commerce"})
    project_id = p_res.json()["id"]

    s_res = client_with_db.post(f"/api/v1/projects/{project_id}/stories", json={"title": "Login Story", "project_id": project_id})
    story_id = s_res.json()["id"]

    res = client_with_db.get(f"/api/v1/stories/{story_id}")
    assert res.status_code == 200
    assert res.json()["id"] == story_id
    assert res.json()["title"] == "Login Story"


def test_10_update_story(client_with_db):
    p_res = client_with_db.post("/api/v1/projects", json={"name": "E-Commerce"})
    project_id = p_res.json()["id"]

    s_res = client_with_db.post(f"/api/v1/projects/{project_id}/stories", json={"title": "Story Draft", "project_id": project_id})
    story_id = s_res.json()["id"]

    res = client_with_db.put(f"/api/v1/stories/{story_id}", json={
        "title": "Story Finalized",
        "status": "IN_PROGRESS",
        "priority": "HIGH"
    })
    assert res.status_code == 200
    assert res.json()["title"] == "Story Finalized"
    assert res.json()["status"] == "IN_PROGRESS"


def test_11_delete_story(client_with_db):
    p_res = client_with_db.post("/api/v1/projects", json={"name": "E-Commerce"})
    project_id = p_res.json()["id"]

    s_res = client_with_db.post(f"/api/v1/projects/{project_id}/stories", json={"title": "Story To Delete", "project_id": project_id})
    story_id = s_res.json()["id"]

    del_res = client_with_db.delete(f"/api/v1/stories/{story_id}")
    assert del_res.status_code == 204

    get_res = client_with_db.get(f"/api/v1/stories/{story_id}")
    assert get_res.status_code == 404


def test_12_create_story_under_nonexistent_project(client_with_db):
    res = client_with_db.post("/api/v1/projects/99999/stories", json={
        "title": "Orphan Story",
        "project_id": 99999
    })
    assert res.status_code == 404
    assert res.json()["detail"] == "Project with id 99999 not found"


def test_13_get_nonexistent_story(client_with_db):
    res = client_with_db.get("/api/v1/stories/99999")
    assert res.status_code == 404
    assert res.json()["detail"] == "User story with id 99999 not found"


# =====================================================================
# TASKS API TESTS
# =====================================================================

def test_14_create_task_under_story(client_with_db):
    p_res = client_with_db.post("/api/v1/projects", json={"name": "E-Commerce"})
    project_id = p_res.json()["id"]

    s_res = client_with_db.post(f"/api/v1/projects/{project_id}/stories", json={"title": "Login Story", "project_id": project_id})
    story_id = s_res.json()["id"]

    res = client_with_db.post(f"/api/v1/stories/{story_id}/tasks", json={
        "title": "Create Login API",
        "description": "Implement authentication endpoint",
        "status": "TODO",
        "priority": "HIGH",
        "assigned_to": "Alice",
        "user_story_id": story_id
    })
    assert res.status_code == 201
    data = res.json()
    assert data["id"] is not None
    assert data["user_story_id"] == story_id
    assert data["assigned_to"] == "Alice"


def test_15_get_tasks_for_story(client_with_db):
    p_res = client_with_db.post("/api/v1/projects", json={"name": "E-Commerce"})
    project_id = p_res.json()["id"]

    s_res = client_with_db.post(f"/api/v1/projects/{project_id}/stories", json={"title": "Login Story", "project_id": project_id})
    story_id = s_res.json()["id"]

    client_with_db.post(f"/api/v1/stories/{story_id}/tasks", json={"title": "Task A", "user_story_id": story_id})
    client_with_db.post(f"/api/v1/stories/{story_id}/tasks", json={"title": "Task B", "user_story_id": story_id})

    res = client_with_db.get(f"/api/v1/stories/{story_id}/tasks?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_16_get_task_by_id(client_with_db):
    p_res = client_with_db.post("/api/v1/projects", json={"name": "E-Commerce"})
    project_id = p_res.json()["id"]

    s_res = client_with_db.post(f"/api/v1/projects/{project_id}/stories", json={"title": "Login Story", "project_id": project_id})
    story_id = s_res.json()["id"]

    t_res = client_with_db.post(f"/api/v1/stories/{story_id}/tasks", json={"title": "Task 1", "user_story_id": story_id})
    task_id = t_res.json()["id"]

    res = client_with_db.get(f"/api/v1/tasks/{task_id}")
    assert res.status_code == 200
    assert res.json()["id"] == task_id
    assert res.json()["title"] == "Task 1"


def test_17_update_task(client_with_db):
    p_res = client_with_db.post("/api/v1/projects", json={"name": "E-Commerce"})
    project_id = p_res.json()["id"]

    s_res = client_with_db.post(f"/api/v1/projects/{project_id}/stories", json={"title": "Login Story", "project_id": project_id})
    story_id = s_res.json()["id"]

    t_res = client_with_db.post(f"/api/v1/stories/{story_id}/tasks", json={"title": "Task Pending", "user_story_id": story_id})
    task_id = t_res.json()["id"]

    res = client_with_db.put(f"/api/v1/tasks/{task_id}", json={
        "title": "Task Finished",
        "status": "DONE",
        "assigned_to": "Bob"
    })
    assert res.status_code == 200
    assert res.json()["title"] == "Task Finished"
    assert res.json()["status"] == "DONE"
    assert res.json()["assigned_to"] == "Bob"


def test_18_delete_task(client_with_db):
    p_res = client_with_db.post("/api/v1/projects", json={"name": "E-Commerce"})
    project_id = p_res.json()["id"]

    s_res = client_with_db.post(f"/api/v1/projects/{project_id}/stories", json={"title": "Login Story", "project_id": project_id})
    story_id = s_res.json()["id"]

    t_res = client_with_db.post(f"/api/v1/stories/{story_id}/tasks", json={"title": "Task To Delete", "user_story_id": story_id})
    task_id = t_res.json()["id"]

    del_res = client_with_db.delete(f"/api/v1/tasks/{task_id}")
    assert del_res.status_code == 204

    get_res = client_with_db.get(f"/api/v1/tasks/{task_id}")
    assert get_res.status_code == 404


def test_19_create_task_under_nonexistent_story(client_with_db):
    res = client_with_db.post("/api/v1/stories/99999/tasks", json={
        "title": "Orphan Task",
        "user_story_id": 99999
    })
    assert res.status_code == 404
    assert res.json()["detail"] == "User story with id 99999 not found"


def test_20_get_nonexistent_task(client_with_db):
    res = client_with_db.get("/api/v1/tasks/99999")
    assert res.status_code == 404
    assert res.json()["detail"] == "Task with id 99999 not found"


# =====================================================================
# VALIDATION TESTS
# =====================================================================

def test_21_invalid_project_data_rejected(client_with_db):
    res = client_with_db.post("/api/v1/projects", json={})
    assert res.status_code == 422


def test_22_invalid_story_status_rejected(client_with_db):
    p_res = client_with_db.post("/api/v1/projects", json={"name": "E-Commerce"})
    project_id = p_res.json()["id"]

    res = client_with_db.post(f"/api/v1/projects/{project_id}/stories", json={
        "title": "Story",
        "status": "INVALID_STATUS",
        "project_id": project_id
    })
    assert res.status_code == 422


def test_23_invalid_story_priority_rejected(client_with_db):
    p_res = client_with_db.post("/api/v1/projects", json={"name": "E-Commerce"})
    project_id = p_res.json()["id"]

    res = client_with_db.post(f"/api/v1/projects/{project_id}/stories", json={
        "title": "Story",
        "priority": "INVALID_PRIORITY",
        "project_id": project_id
    })
    assert res.status_code == 422


def test_24_invalid_task_status_rejected(client_with_db):
    p_res = client_with_db.post("/api/v1/projects", json={"name": "E-Commerce"})
    project_id = p_res.json()["id"]
    s_res = client_with_db.post(f"/api/v1/projects/{project_id}/stories", json={"title": "Story", "project_id": project_id})
    story_id = s_res.json()["id"]

    res = client_with_db.post(f"/api/v1/stories/{story_id}/tasks", json={
        "title": "Task",
        "status": "NOT_A_STATUS",
        "user_story_id": story_id
    })
    assert res.status_code == 422


def test_25_invalid_task_priority_rejected(client_with_db):
    p_res = client_with_db.post("/api/v1/projects", json={"name": "E-Commerce"})
    project_id = p_res.json()["id"]
    s_res = client_with_db.post(f"/api/v1/projects/{project_id}/stories", json={"title": "Story", "project_id": project_id})
    story_id = s_res.json()["id"]

    res = client_with_db.post(f"/api/v1/stories/{story_id}/tasks", json={
        "title": "Task",
        "priority": "NOT_A_PRIORITY",
        "user_story_id": story_id
    })
    assert res.status_code == 422


# =====================================================================
# HIERARCHY TEST
# =====================================================================

def test_26_to_29_full_hierarchy_integration(client_with_db):
    # 26. Create one Project
    p_res = client_with_db.post("/api/v1/projects", json={
        "name": "E-Commerce Website",
        "description": "Main platform project",
        "status": "ACTIVE"
    })
    assert p_res.status_code == 201
    project_id = p_res.json()["id"]

    # 27. Create multiple User Stories under Project
    s1_res = client_with_db.post(f"/api/v1/projects/{project_id}/stories", json={
        "title": "Customer Login",
        "project_id": project_id,
        "status": "IN_PROGRESS",
        "priority": "HIGH"
    })
    s2_res = client_with_db.post(f"/api/v1/projects/{project_id}/stories", json={
        "title": "Product Search",
        "project_id": project_id,
        "status": "TODO",
        "priority": "MEDIUM"
    })
    assert s1_res.status_code == 201
    assert s2_res.status_code == 201
    story_id = s1_res.json()["id"]

    # 28. Create multiple Tasks under User Story
    t1_res = client_with_db.post(f"/api/v1/stories/{story_id}/tasks", json={
        "title": "Create login API",
        "user_story_id": story_id,
        "status": "DONE",
        "priority": "HIGH",
        "assigned_to": "Alice"
    })
    t2_res = client_with_db.post(f"/api/v1/stories/{story_id}/tasks", json={
        "title": "Create login page",
        "user_story_id": story_id,
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "assigned_to": "Bob"
    })
    t3_res = client_with_db.post(f"/api/v1/stories/{story_id}/tasks", json={
        "title": "Add authentication validation",
        "user_story_id": story_id,
        "status": "TODO",
        "priority": "MEDIUM",
        "assigned_to": "Charlie"
    })
    assert t1_res.status_code == 201
    assert t2_res.status_code == 201
    assert t3_res.status_code == 201

    # 29. Retrieve hierarchy and verify relationships
    p_get = client_with_db.get(f"/api/v1/projects/{project_id}")
    assert p_get.status_code == 200
    p_data = p_get.json()
    assert len(p_data["user_stories"]) == 2
    story_titles = [s["title"] for s in p_data["user_stories"]]
    assert "Customer Login" in story_titles
    assert "Product Search" in story_titles

    t_get = client_with_db.get(f"/api/v1/stories/{story_id}/tasks")
    assert t_get.status_code == 200
    t_data = t_get.json()
    assert t_data["total"] == 3
    task_titles = [t["title"] for t in t_data["items"]]
    assert "Create login API" in task_titles
    assert "Create login page" in task_titles
    assert "Add authentication validation" in task_titles
