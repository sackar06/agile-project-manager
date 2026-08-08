# REST API Documentation

The Agile Project Management API is built with FastAPI and follows RESTful principles. It provides endpoints for managing the 3-tier work tracking hierarchy (**Project $\rightarrow$ User Story $\rightarrow$ Task**) and executing asynchronous background report generation.

---

## 1. Overview & Base URLs

- **Base API URL**: `http://localhost:8000/api/v1`
- **Interactive Swagger UI**: `http://localhost:8000/docs`
- **ReDoc UI**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/api/v1/openapi.json`

### Core Response Status Codes
| Status Code | Meaning | Description |
|---|---|---|
| **200 OK** | Success | Request succeeded and returned requested data. |
| **201 Created** | Created | Resource successfully created. |
| **202 Accepted** | Accepted | Asynchronous report job accepted for background processing. |
| **204 No Content** | Deleted | Resource successfully deleted. |
| **422 Unprocessable Entity** | Validation Error | Request payload or query parameter failed Pydantic validation. |
| **404 Not Found** | Not Found | Requested entity or parent resource does not exist. |
| **500 Internal Error** | Server Error | Unhandled server exception. |

---

## 2. Global Pagination Format

All listing endpoints support standard query-based pagination (`page` and `page_size`) and return a standardized JSON structure:

### Query Parameters
- `page` *(int, default: 1)*: Page number (1-indexed, $\ge 1$).
- `page_size` *(int, default: 10)*: Number of items per page ($1 \le \text{page\_size} \le 100$).

### Paginated Response Structure
```json
{
  "items": [ ... ],
  "page": 1,
  "page_size": 10,
  "total": 42
}
```

---

## 3. Health Endpoint

### `GET /health`
Verifies service health and active database connectivity.

- **URL Path**: `/health`
- **Method**: `GET`
- **Response Model**: `HealthResponse`
- **Status Code**: `200 OK`

#### Response Example
```json
{
  "status": "ok",
  "app_name": "Agile Project Manager",
  "version": "0.1.0",
  "database": "connected"
}
```

---

## 4. Projects API

### Enums
- **ProjectStatus**: `"PLANNING"`, `"ACTIVE"`, `"COMPLETED"`

---

### `POST /api/v1/projects`
Creates a new Project container.

- **Status Code**: `201 Created`
- **Request Body**: `ProjectCreate`

```json
{
  "name": "E-Commerce Website",
  "description": "Online store front for team project management",
  "status": "ACTIVE"
}
```

- **Response Example**:
```json
{
  "id": 1,
  "name": "E-Commerce Website",
  "description": "Online store front for team project management",
  "status": "ACTIVE",
  "created_at": "2026-08-08T12:00:00.000000",
  "updated_at": "2026-08-08T12:00:00.000000"
}
```

---

### `GET /api/v1/projects`
Lists all projects with pagination.

- **Status Code**: `200 OK`
- **Query Parameters**: `page` (default `1`), `page_size` (default `10`)
- **Response Example**:
```json
{
  "items": [
    {
      "id": 1,
      "name": "E-Commerce Website",
      "description": "Online store front for team project management",
      "status": "ACTIVE",
      "created_at": "2026-08-08T12:00:00.000000",
      "updated_at": "2026-08-08T12:00:00.000000"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 1
}
```

---

### `GET /api/v1/projects/{project_id}`
Retrieves a project by ID, including its associated User Stories.

- **Status Code**: `200 OK`
- **Path Parameter**: `project_id` *(int)*
- **Error Response (404)**: `{"detail": "Project with id 999 not found"}`
- **Response Example**:
```json
{
  "id": 1,
  "name": "E-Commerce Website",
  "description": "Online store front for team project management",
  "status": "ACTIVE",
  "created_at": "2026-08-08T12:00:00.000000",
  "updated_at": "2026-08-08T12:00:00.000000",
  "user_stories": [
    {
      "id": 1,
      "project_id": 1,
      "title": "Customer Login",
      "description": "As a customer, I want to log in securely.",
      "status": "IN_PROGRESS",
      "priority": "HIGH",
      "created_at": "2026-08-08T12:05:00.000000",
      "updated_at": "2026-08-08T12:05:00.000000"
    }
  ]
}
```

---

### `PUT /api/v1/projects/{project_id}`
Updates an existing project's fields.

- **Status Code**: `200 OK`
- **Request Body**: `ProjectUpdate` (All fields optional)
```json
{
  "name": "Updated E-Commerce Website",
  "status": "COMPLETED"
}
```

---

### `DELETE /api/v1/projects/{project_id}`
Deletes a project and automatically cascade-deletes all its child User Stories and Tasks.

- **Status Code**: `204 No Content`
- **Path Parameter**: `project_id` *(int)*

---

## 5. User Stories API

### Enums
- **WorkItemStatus**: `"TODO"`, `"IN_PROGRESS"`, `"DONE"`
- **PriorityLevel**: `"LOW"`, `"MEDIUM"`, `"HIGH"`

---

### `POST /api/v1/projects/{project_id}/stories`
Creates a new User Story under a target Project.

- **Status Code**: `201 Created`
- **Request Body**: `UserStoryCreate`
```json
{
  "title": "Customer Login",
  "description": "As a customer, I want to log in securely.",
  "status": "IN_PROGRESS",
  "priority": "HIGH"
}
```

---

### `GET /api/v1/projects/{project_id}/stories`
Lists User Stories belonging to a specific Project (Paginated).

- **Status Code**: `200 OK`
- **Query Parameters**: `page` (default `1`), `page_size` (default `10`)

---

### `GET /api/v1/stories/{story_id}`
Retrieves a single User Story by ID.

- **Status Code**: `200 OK`

---

### `PUT /api/v1/stories/{story_id}`
Updates a User Story's title, description, status, or priority.

- **Status Code**: `200 OK`
- **Request Body**: `UserStoryUpdate`

---

### `DELETE /api/v1/stories/{story_id}`
Deletes a User Story and cascade-deletes its child Tasks.

- **Status Code**: `204 No Content`

---

## 6. Tasks API

### `POST /api/v1/stories/{story_id}/tasks`
Creates a Task under a parent User Story.

- **Status Code**: `201 Created`
- **Request Body**: `TaskCreate`
```json
{
  "title": "Create Login API",
  "description": "Implement authentication API endpoint",
  "status": "IN_PROGRESS",
  "priority": "HIGH",
  "assigned_to": "Alice"
}
```

---

### `GET /api/v1/stories/{story_id}/tasks`
Lists Tasks for a specific User Story (Paginated).

- **Status Code**: `200 OK`
- **Query Parameters**: `page` (default `1`), `page_size` (default `10`)

---

### `GET /api/v1/tasks/{task_id}`
Retrieves a single Task by ID.

- **Status Code**: `200 OK`

---

### `PUT /api/v1/tasks/{task_id}`
Updates a Task's details (title, description, status, priority, assigned_to).

- **Status Code**: `200 OK`
- **Request Body**: `TaskUpdate`

---

### `DELETE /api/v1/tasks/{task_id}`
Deletes a single Task.

- **Status Code**: `204 No Content`

---

## 7. Asynchronous Progress Reports API

### Enums
- **ReportJobStatus**: `"PENDING"`, `"RUNNING"`, `"COMPLETED"`, `"FAILED"`

---

### `POST /api/v1/projects/{project_id}/reports`
Asynchronously requests progress report generation for a project.

- **Status Code**: `202 Accepted`
- **Response Body**:
```json
{
  "job_id": 1,
  "status": "PENDING",
  "message": "Report generation started"
}
```

---

### `GET /api/v1/reports/{job_id}`
Polls report generation status and retrieves final report data when status is `"COMPLETED"`.

- **Status Code**: `200 OK`
- **Response Example (Completed)**:
```json
{
  "id": 1,
  "project_id": 1,
  "status": "COMPLETED",
  "attempts": 1,
  "error_message": null,
  "report_data": {
    "project_id": 1,
    "project_name": "E-Commerce Website",
    "project_status": "ACTIVE",
    "user_stories": {
      "total": 1,
      "todo": 0,
      "in_progress": 1,
      "done": 0
    },
    "tasks": {
      "total": 3,
      "todo": 1,
      "in_progress": 1,
      "done": 1
    },
    "task_completion_percentage": 33.33
  },
  "created_at": "2026-08-08T12:10:00.000000",
  "started_at": "2026-08-08T12:10:00.500000",
  "completed_at": "2026-08-08T12:10:01.000000"
}
```
