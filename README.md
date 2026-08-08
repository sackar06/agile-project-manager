# Agile Project Management Tool

A full-stack web application designed for small teams (~3–10 users) to manage projects, track user stories, execute tasks, and generate progress reports using a clean Agile workflow.

---

## 1. Overview

Managing software development initiatives in small teams requires a simple, intuitive, and structured tool without the bloat of enterprise project management platforms. 

The Agile Project Management Tool provides a strict 3-tier hierarchy (`Project` $\rightarrow$ `User Story` $\rightarrow$ `Task`), real-time metric dashboards, interactive project management UI, non-blocking asynchronous progress report generation, and robust REST APIs.

---

## 2. Implemented Features

- **Dashboard View**: Real-time high-level metrics (Total, Active, Completed, In Planning projects) and project summary grid cards.
- **Project Management (CRUD)**: Create, view, search filter, update, and delete projects with cascade warnings.
- **User Story Management**: Create, edit, and organize user stories under parent projects with inline priority toggles (`LOW`, `MEDIUM`, `HIGH`) and status controls (`TODO`, `IN_PROGRESS`, `DONE`).
- **Task Management**: Create, edit, assign, and track implementation tasks embedded under parent user stories.
- **Asynchronous Progress Reports**: Non-blocking progress report generation (`HTTP 202 Accepted`) with background worker status calculation, bounded retry loops (`MAX_ATTEMPTS = 3`), status polling, and progress visualizations.
- **Automated API Documentation**: Interactive OpenAPI / Swagger UI (`/docs`) and ReDoc (`/redoc`).

---

## 3. Technology Stack

- **Frontend**: React 18, Vite, Vanilla CSS (Glassmorphism design system), Lucide React Icons.
- **Backend**: Python 3.10+, FastAPI, Pydantic v2, Uvicorn.
- **Database & ORM**: SQLite 3, SQLAlchemy 2.0 ORM (`PRAGMA foreign_keys = ON;`).
- **Testing**: pytest, HTTPX, FastAPI TestClient.

---

## 4. Project Hierarchy

The application enforces a strict 3-tier work tracking hierarchy:

```text
Project (Top-level initiative)
   │
   └── 1:N ──► User Story (User-facing feature requirement)
                  │
                  └── 1:N ──► Task (Actionable implementation item)
```

---

## 5. Background Report Workflow

Generating progress reports for large projects can block HTTP server threads. The application uses FastAPI `BackgroundTasks` to handle report computation asynchronously:

```text
Client                       Backend REST API                 Background Worker
  │                                 │                                │
  │ POST /projects/{id}/reports     │                                │
  ├────────────────────────────────►│ 1. Validate & Create Job (PENDING)
  │ 202 Accepted { job_id }         ├───────────────────────────────►│ 2. Set RUNNING
  │◄────────────────────────────────┤                                │ 3. Aggregate Stats
  │                                 │                                │ 4. Set COMPLETED
  │ GET /reports/{job_id} (Polling) │                                │
  ├────────────────────────────────►│ 5. Return JSON Report Payload  │
```

---

## 6. Project Structure

```text
agile-project-manager/
├── backend/
│   ├── app/
│   │   ├── api/             # REST API routers (projects, stories, tasks, reports)
│   │   ├── core/            # Database engine, session factory, settings
│   │   ├── models/          # SQLAlchemy ORM models & Enums
│   │   ├── repositories/    # Database query abstractions & pagination
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic & background workers
│   │   └── main.py          # FastAPI application entry point
│   ├── tests/               # Pytest unit & integration test suite (45 tests)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # Common, project, story, task, & report UI components
│   │   ├── pages/           # Dashboard, ProjectsPage, ProjectDetails, NotFound
│   │   ├── services/        # API client modules (project, story, task, report)
│   │   ├── App.jsx          # Shell & route state switcher
│   │   └── index.css        # Core design system & CSS styling
│   ├── package.json
│   └── vite.config.js
├── docs/                    # Complete architectural & API documentation
│   ├── ai-usage.md
│   ├── api-documentation.md
│   ├── architecture.md
│   ├── async-workflow.md
│   ├── database-schema.md
│   ├── design-decisions.md
│   ├── future-improvements.md
│   └── security.md
└── README.md
```

---

## 7. Setup & Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher & npm

### A. Backend Setup
1. Open a terminal in `backend/`:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```powershell
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### B. Frontend Setup
1. Open a terminal in `frontend/`:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```

---

## 8. Running the Application

### A. Start Backend Server
```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- API Server: `http://localhost:8000`
- Interactive API Docs: `http://localhost:8000/docs`

### B. Start Frontend Dev Server
```cmd
cd frontend
npm.cmd run dev -- --host 0.0.0.0
```
- Web Application UI (Local): `http://localhost:5173`
- Network/LAN Access: `http://<YOUR_LOCAL_IP>:5173` (Find your IP using `ipconfig` on Windows or `ifconfig` on Linux/Mac)

---

## 8.1 API Endpoints Summary

For complete schema details and JSON examples, see [docs/api-documentation.md](docs/api-documentation.md) or open the interactive Swagger UI at `http://localhost:8000/docs`.

| Module | Method | Endpoint | Description |
|---|---|---|---|
| **Health** | `GET` | `/health` | Service health check and database status |
| **Projects** | `POST` | `/api/v1/projects` | Create a new Project |
| | `GET` | `/api/v1/projects` | List projects (Paginated) |
| | `GET` | `/api/v1/projects/{project_id}` | Get project details & associated user stories |
| | `PUT` | `/api/v1/projects/{project_id}` | Update project fields |
| | `DELETE` | `/api/v1/projects/{project_id}` | Delete project (Cascade deletes stories & tasks) |
| **User Stories** | `POST` | `/api/v1/projects/{project_id}/stories` | Create user story under project |
| | `GET` | `/api/v1/projects/{project_id}/stories` | List stories for project (Paginated) |
| | `GET` | `/api/v1/stories/{story_id}` | Get user story details |
| | `PUT` | `/api/v1/stories/{story_id}` | Update user story |
| | `DELETE` | `/api/v1/stories/{story_id}` | Delete user story (Cascade deletes tasks) |
| **Tasks** | `POST` | `/api/v1/stories/{story_id}/tasks` | Create task under user story |
| | `GET` | `/api/v1/stories/{story_id}/tasks` | List tasks for story (Paginated) |
| | `GET` | `/api/v1/tasks/{task_id}` | Get task details |
| | `PUT` | `/api/v1/tasks/{task_id}` | Update task |
| | `DELETE` | `/api/v1/tasks/{task_id}` | Delete task |
| **Reports** | `POST` | `/api/v1/projects/{project_id}/reports` | Request async report generation (HTTP 202) |
| | `GET` | `/api/v1/reports/{job_id}` | Poll background report job status & results |

---

## 9. Testing

### Run Backend Pytest Suite
```bash
cd backend
.\venv\Scripts\pytest
```
- Executes all 45 automated unit, integration, and database relationship tests.

### Build Frontend Production Bundle
```bash
cd frontend
npm run build
```
- Compiles the React + Vite frontend into optimized static production assets in `frontend/dist/`.

---

## 10. Example Workflow

1. **Create Project**: Click **+ New Project** on the Projects page to create "E-Commerce Website" (Status: `ACTIVE`).
2. **Create User Story**: Navigate into the project details page and click **+ Add Story** to create "Customer Login" (Priority: `HIGH`, Status: `TODO`).
3. **Create Tasks**: Under "Customer Login", create task "Create login API" (Assignee: `Alice`, Status: `TODO`).
4. **Update Status**: Toggle the task status to `DONE`. The parent user story status updates to `IN_PROGRESS`.
5. **Generate Report**: Click **Generate Progress Report**. The system returns `HTTP 202 Accepted`, background worker processes the job, and the UI displays the formatted completion stats.

---

## 11. Database & Security

- **Database**: SQLite database stored locally in `backend/agile_project_manager.db`. Foreign keys are strictly enforced via `PRAGMA foreign_keys = ON;`. Cascading deletes ensure clean data cleanup.
- **Security**: Full input validation (Pydantic/Forms), parameterized ORM queries to prevent SQL injection, sanitized error responses, and environment configuration management. See [docs/security.md](docs/security.md) for full audit details.

---

## 12. Documentation Links

- [Architecture Documentation](docs/architecture.md)
- [API Documentation & Endpoint Reference](docs/api-documentation.md)
- [Database Schema & ER Diagram](docs/database-schema.md)
- [Asynchronous Workflow Documentation](docs/async-workflow.md)
- [Design Decisions & Tradeoffs](docs/design-decisions.md)
- [Security Assessment](docs/security.md)
- [AI Usage Statement](docs/ai-usage.md)
- [Future Improvements & Roadmap](docs/future-improvements.md)

---

## 13. Demo & Walkthrough Links

- **Demo link**: Not provided.
- **Walkthrough video**: Not provided.
