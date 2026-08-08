import sys
import os
from fastapi.testclient import TestClient

# Add backend directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)


def run_manual_workflow():
    print("==================================================")
    print("STEP 3 MANUAL API WORKFLOW VERIFICATION")
    print("==================================================")

    # 1. Create Project
    print("\n1. Creating Project 'E-Commerce Website'...")
    p_res = client.post("/api/v1/projects", json={
        "name": "E-Commerce Website",
        "description": "Main online store front initiative",
        "status": "ACTIVE"
    })
    assert p_res.status_code == 201, f"Failed: {p_res.text}"
    project = p_res.json()
    project_id = project["id"]
    print(f"   [SUCCESS] Created Project ID: {project_id}, Status: {project['status']}")

    # 2. Create User Story
    print("\n2. Creating User Story 'Customer Login' under Project...")
    s_res = client.post(f"/api/v1/projects/{project_id}/stories", json={
        "title": "Customer Login",
        "description": "As a customer, I want to securely log in to access my account.",
        "status": "TODO",
        "priority": "HIGH",
        "project_id": project_id
    })
    assert s_res.status_code == 201, f"Failed: {s_res.text}"
    story = s_res.json()
    story_id = story["id"]
    print(f"   [SUCCESS] Created User Story ID: {story_id}, Status: {story['status']}")

    # 3. Create 3 Tasks
    print("\n3. Creating Tasks under User Story...")
    task_titles = [
        "Create login API",
        "Create login page",
        "Add authentication validation"
    ]
    created_tasks = {}
    for title in task_titles:
        t_res = client.post(f"/api/v1/stories/{story_id}/tasks", json={
            "title": title,
            "description": f"Implementation details for {title}",
            "status": "TODO",
            "priority": "HIGH",
            "assigned_to": "Developer",
            "user_story_id": story_id
        })
        assert t_res.status_code == 201, f"Failed: {t_res.text}"
        task = t_res.json()
        created_tasks[title] = task["id"]
        print(f"   * [SUCCESS] Created Task ID: {task['id']}, Title: '{title}'")

    # 4. Update Customer Login status -> IN_PROGRESS
    print("\n4. Updating User Story status to IN_PROGRESS...")
    s_update_res = client.put(f"/api/v1/stories/{story_id}", json={
        "status": "IN_PROGRESS"
    })
    assert s_update_res.status_code == 200, f"Failed: {s_update_res.text}"
    print(f"   [SUCCESS] User Story ID {story_id} status updated to: {s_update_res.json()['status']}")

    # 5. Update Create login API -> DONE
    task_api_id = created_tasks["Create login API"]
    print(f"\n5. Updating Task 'Create login API' (ID: {task_api_id}) status to DONE...")
    t_update_res = client.put(f"/api/v1/tasks/{task_api_id}", json={
        "status": "DONE"
    })
    assert t_update_res.status_code == 200, f"Failed: {t_update_res.text}"
    print(f"   [SUCCESS] Task ID {task_api_id} status updated to: {t_update_res.json()['status']}")

    # 6. Retrieve Project and verify hierarchy
    print(f"\n6. Retrieving Project ID {project_id} to verify hierarchy preservation...")
    p_get_res = client.get(f"/api/v1/projects/{project_id}")
    assert p_get_res.status_code == 200, f"Failed: {p_get_res.text}"
    p_data = p_get_res.json()

    print("\n--- RETRIEVED HIERARCHY DATA ---")
    print(f"Project: [ID: {p_data['id']}] {p_data['name']} (Status: {p_data['status']})")
    assert len(p_data["user_stories"]) >= 1
    for s in p_data["user_stories"]:
        if s["id"] == story_id:
            print(f"  +-- User Story: [ID: {s['id']}] {s['title']} (Status: {s['status']}, Priority: {s['priority']})")
            assert s["status"] == "IN_PROGRESS"
            
            # Fetch tasks for story
            tasks_res = client.get(f"/api/v1/stories/{story_id}/tasks")
            assert tasks_res.status_code == 200
            tasks_data = tasks_res.json()
            for t in tasks_data["items"]:
                print(f"        +-- Task: [ID: {t['id']}] {t['title']} (Status: {t['status']}, Assigned: {t['assigned_to']})")
                if t["id"] == task_api_id:
                    assert t["status"] == "DONE"

    print("\n==================================================")
    print("ALL WORKFLOW STEPS VERIFIED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    run_manual_workflow()
