import sys
import os
from unittest.mock import patch
from fastapi.testclient import TestClient

# Add backend directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.services.report_service import ReportService

client = TestClient(app)


def run_step4_workflow():
    print("==================================================")
    print("STEP 4 ASYNCHRONOUS WORKFLOW VERIFICATION")
    print("==================================================")

    # 1. Create Project
    print("\n1. Creating Project 'E-Commerce Website'...")
    p_res = client.post("/api/v1/projects", json={
        "name": "E-Commerce Website",
        "description": "Main store platform project",
        "status": "ACTIVE"
    })
    assert p_res.status_code == 201
    project_id = p_res.json()["id"]
    print(f"   [SUCCESS] Created Project ID: {project_id}")

    # 2. Create User Story 1: Customer Login
    print("\n2. Creating User Story 1 'Customer Login'...")
    s1_res = client.post(f"/api/v1/projects/{project_id}/stories", json={
        "title": "Customer Login",
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "project_id": project_id
    })
    assert s1_res.status_code == 201
    s1_id = s1_res.json()["id"]

    # Create 3 Tasks for Story 1
    t1_res = client.post(f"/api/v1/stories/{s1_id}/tasks", json={"title": "Create login API", "status": "DONE", "user_story_id": s1_id})
    t2_res = client.post(f"/api/v1/stories/{s1_id}/tasks", json={"title": "Create login page", "status": "IN_PROGRESS", "user_story_id": s1_id})
    t3_res = client.post(f"/api/v1/stories/{s1_id}/tasks", json={"title": "Add authentication validation", "status": "TODO", "user_story_id": s1_id})
    assert t1_res.status_code == 201 and t2_res.status_code == 201 and t3_res.status_code == 201
    print("   [SUCCESS] Created Story 1 with 3 Tasks (1 DONE, 1 IN_PROGRESS, 1 TODO)")

    # 3. Create User Story 2: Product Search
    print("\n3. Creating User Story 2 'Product Search'...")
    s2_res = client.post(f"/api/v1/projects/{project_id}/stories", json={
        "title": "Product Search",
        "status": "TODO",
        "priority": "MEDIUM",
        "project_id": project_id
    })
    assert s2_res.status_code == 201
    s2_id = s2_res.json()["id"]

    # Create 2 Tasks for Story 2
    t4_res = client.post(f"/api/v1/stories/{s2_id}/tasks", json={"title": "Create search API", "status": "IN_PROGRESS", "user_story_id": s2_id})
    t5_res = client.post(f"/api/v1/stories/{s2_id}/tasks", json={"title": "Create search UI", "status": "TODO", "user_story_id": s2_id})
    assert t4_res.status_code == 201 and t5_res.status_code == 201
    print("   [SUCCESS] Created Story 2 with 2 Tasks (1 IN_PROGRESS, 1 TODO)")

    # 4. Request Project Progress Report Generation
    print(f"\n4. Requesting Project Report for Project ID {project_id}...")
    report_req_res = client.post(f"/api/v1/projects/{project_id}/reports")
    assert report_req_res.status_code == 202, f"Failed: {report_req_res.text}"
    job_info = report_req_res.json()
    job_id = job_info["job_id"]
    print(f"   [SUCCESS] Immediate Response HTTP 202 Accepted: Job ID={job_id}, Status={job_info['status']}")

    # 5. Retrieve / Poll Report Job Status
    print(f"\n5. Polling GET /api/v1/reports/{job_id}...")
    get_job_res = client.get(f"/api/v1/reports/{job_id}")
    assert get_job_res.status_code == 200
    job_data = get_job_res.json()
    print(f"   * Status: {job_data['status']}")
    print(f"   * Attempts: {job_data['attempts']}")

    if job_data["report_data"]:
        rep = job_data["report_data"]
        print("\n--- GENERATED REPORT DATA ---")
        print(f"Project: {rep['project_name']} (Status: {rep['project_status']})")
        print(f"User Stories: Total={rep['user_stories']['total']} [TODO={rep['user_stories']['todo']}, IN_PROGRESS={rep['user_stories']['in_progress']}, DONE={rep['user_stories']['done']}]")
        print(f"Tasks: Total={rep['tasks']['total']} [TODO={rep['tasks']['todo']}, IN_PROGRESS={rep['tasks']['in_progress']}, DONE={rep['tasks']['done']}]")
        print(f"Task Completion Percentage: {rep['task_completion_percentage']}%")

        assert rep["user_stories"]["total"] == 2
        assert rep["tasks"]["total"] == 5
        assert rep["tasks"]["done"] == 1
        assert rep["task_completion_percentage"] == 20.0

    # 6. Test Failure & Bounded Retry Scenario
    print("\n6. Testing Failure Scenario & Bounded Retry (Simulating calculation error)...")
    p_fail_res = client.post("/api/v1/projects", json={"name": "Failing Project"})
    fail_proj_id = p_fail_res.json()["id"]

    fail_job_res = client.post(f"/api/v1/projects/{fail_proj_id}/reports")
    fail_job_id = fail_job_res.json()["job_id"]

    from app.core.database import SessionLocal
    with patch.object(ReportService, "calculate_project_statistics", side_effect=RuntimeError("Simulated Worker Error")):
        ReportService.execute_background_job(fail_job_id, SessionLocal)

    fail_status_res = client.get(f"/api/v1/reports/{fail_job_id}")
    assert fail_status_res.status_code == 200
    fail_job_data = fail_status_res.json()
    print(f"   [SUCCESS] Failed Job Status: {fail_job_data['status']}")
    print(f"   [SUCCESS] Attempts Recorded: {fail_job_data['attempts']} (Max: 3)")
    print(f"   [SUCCESS] Error Message Saved: {fail_job_data['error_message']}")

    assert fail_job_data["status"] == "FAILED"
    assert fail_job_data["attempts"] == 3

    print("\n==================================================")
    print("STEP 4 ALL ASYNCHRONOUS WORKFLOW STEPS PASSED!")
    print("==================================================")


if __name__ == "__main__":
    run_step4_workflow()
