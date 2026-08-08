# Agile Project Manager

🚀 **[Live Demo](https://agile-project-manager-frontend.onrender.com)**

A full-stack web application designed for small teams (~3–10 users) to manage projects, track user stories, execute tasks, and generate progress reports using a clean Agile workflow.

---

## 1. Project Overview

Managing software development initiatives in small teams requires a simple, intuitive, and structured tool without the bloat of enterprise project management platforms.

The Agile Project Manager provides a strict 3-tier work tracking hierarchy (`Project` --> `User Story` --> `Task`), real-time metric dashboards, an interactive management UI, non-blocking asynchronous progress report generation, and robust REST APIs.

---

## 2. Key Features

- **Dashboard View**: Real-time high-level metrics (Total, Active, Completed, In Planning projects) and project summary grid cards.
- **Project Management (CRUD)**: Create, view, search filter, update, and delete projects with cascade warnings.
- **User Story Management**: Create, edit, and organize user stories under parent projects with inline priority toggles (`LOW`, `MEDIUM`, `HIGH`) and status controls (`TODO`, `IN_PROGRESS`, `DONE`).
- **Task Management**: Create, edit, assign, and track implementation tasks embedded under parent user stories.
- **Asynchronous Progress Reports**: Non-blocking progress report generation (`HTTP 202 Accepted`) with background worker status calculation, bounded retry loops (`MAX_ATTEMPTS = 3`), status polling, and progress visualizations.
- **Automated API Documentation**: Interactive OpenAPI / Swagger UI (`http://localhost:8000/docs`) and ReDoc (`http://localhost:8000/redoc`).

---

## 3. Key Features & Functionality

- **Strict 3-Tier Hierarchy**: Every task belongs to a user story, and every user story belongs to a project.
- **Real-Time Project Metrics**: Auto-calculated completion percentages and status distribution badges across all work items.
- **Background Worker Engine**: Long-running report calculations process asynchronously without blocking API request threads.
- **Cascading Deletions**: Deleting a project automatically cleans up child stories, tasks, and report job records cleanly in SQLite.

---

## 4. Technology Stack

- **Frontend**: React 18, Vite, Vanilla CSS (Glassmorphism design system), Lucide React Icons.
- **Backend**: Python 3.10+ (Python 3.11 verified), FastAPI 0.110+, Pydantic v2, Uvicorn.
- **Database & ORM**: SQLite 3, SQLAlchemy 2.0 ORM (`PRAGMA foreign_keys = ON;`).
- **Testing**: pytest 8.1+ (45 automated unit & integration tests), HTTPX, FastAPI TestClient.

---

## 5. Architecture Overview

The application follows a clean split-stack web architecture:

```text
React 18 (Frontend SPA)
       │
       │ HTTP REST Requests (JSON)
       ▼
FastAPI (Backend REST API)
       │
       ▼
  API Layer (app/api)
       │
       ▼
Service Layer (app/services)
       │
       ▼
Repository Layer (app/repositories)
       │
       ▼
SQLAlchemy (ORM Mapping & Session Management)
       │
       ▼
 SQLite 3 (Relational Database)
```

For full details on component responsibilities and data flow diagrams, see [docs/architecture.md](docs/architecture.md).

---

## 6. Prerequisites

Before installing and running the project, ensure your environment has the following software installed:

* **Python**: `3.10` or higher (verified on Python 3.11)
* **Node.js & npm**: Node.js `18.0.0` or higher & npm `9.0.0` or higher
* **Git**: For cloning the repository
* **Web Browser**: Any modern browser (Google Chrome, Microsoft Edge, Mozilla Firefox, or Apple Safari)

---

## 7. Clone Repository

To clone the repository to your local machine, open your terminal or PowerShell and run:

```bash
git clone https://github.com/sackar06/agile-project-manager.git
cd agile-project-manager
```

> [!IMPORTANT]
> All setup and run commands in the sections below assume you are starting from the root directory of the repository (`agile-project-manager`).

---

## 8. Backend Setup

From the project root (`agile-project-manager`), follow these steps to set up the backend environment:

1. **Navigate to the backend directory:**
   ```powershell
   cd backend
   ```

2. **Create a Python virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment (Windows PowerShell):**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   > [!NOTE]
   > **PowerShell Execution Policy Fallback:**
   > If PowerShell blocks `Activate.ps1` with a script execution policy error, you do **not** need to change system settings. You can run all Python and pip commands directly using `.\venv\Scripts\python.exe`:

4. **Install backend dependencies:**
   ```powershell
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

---

## 9. Frontend Setup

From the project root (`agile-project-manager`), follow these steps to set up the frontend environment:

1. **Navigate to the frontend directory:**
   ```powershell
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```cmd
   npm install
   ```

   > [!NOTE]
   > If running on Windows PowerShell where `npm.ps1` is restricted by execution policy, use `npm.cmd install` instead.

---

## 10. Environment Configuration

### Frontend API URL Configuration

The frontend communicates with the backend REST API using the base URL defined in its environment file (`.env`).

1. **Create the `.env` file from `.env.example` in `frontend/`:**
   ```cmd
   cd frontend
   copy .env.example .env
   ```

2. **Default Environment Variable (`frontend/.env`):**
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

3. **When to change this configuration:**
   - **Local Testing (Same Machine)**: Keep the default `http://localhost:8000/api/v1`.
   - **LAN Testing (Other Devices on Same Network)**: Update `VITE_API_BASE_URL` to `http://<HOST_MACHINE_IP>:8000/api/v1` so remote devices can reach the backend server.

---

## 11. Run the Project

To run the complete application, open **two separate terminal windows** from the project root (`agile-project-manager`).

### Terminal 1 — Backend REST API

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> [!NOTE]
> `--host 0.0.0.0` instructs the server to bind to all network interfaces (listening for both local and LAN connections). It is **not** a browser URL.

* **Local Browser URL**: [http://localhost:8000](http://localhost:8000)
* **Swagger UI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **Health Check Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)
* **LAN Access (Other Devices)**: `http://<HOST_MACHINE_IP>:8000`

### Terminal 2 — Frontend Development Server

```cmd
cd frontend
npm.cmd run dev -- --host 0.0.0.0
```

* **Local Browser URL**: [http://localhost:5173](http://localhost:5173)
* **LAN Access (Other Devices)**: `http://<HOST_MACHINE_IP>:5173`

---

## 12. API Documentation

The backend automatically generates interactive API documentation via FastAPI.

* **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs) — Test all API routes interactively in your browser.
* **ReDoc UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc) — Clean structured OpenAPI reference.
* **Full API Reference File**: For detailed request/response JSON schemas, see [docs/api-documentation.md](docs/api-documentation.md).

### Summary of REST API Endpoints

| Category | HTTP Method | Path | Description |
|---|---|---|---|
| **Health** | `GET` | `/health` | Health status check and database connection verification |
| **Projects** | `POST` | `/api/v1/projects` | Create a new Project |
| | `GET` | `/api/v1/projects` | List projects (Paginated: `page`, `page_size`) |
| | `GET` | `/api/v1/projects/{id}` | Get project detail & associated User Stories |
| | `PUT` | `/api/v1/projects/{id}` | Update project fields |
| | `DELETE` | `/api/v1/projects/{id}` | Delete project (Cascades to stories & tasks) |
| **User Stories** | `POST` | `/api/v1/projects/{project_id}/stories` | Create user story under project |
| | `GET` | `/api/v1/projects/{project_id}/stories` | List stories for project (Paginated) |
| | `GET` | `/api/v1/stories/{id}` | Get user story details |
| | `PUT` | `/api/v1/stories/{id}` | Update user story |
| | `DELETE` | `/api/v1/stories/{id}` | Delete user story (Cascades to tasks) |
| **Tasks** | `POST` | `/api/v1/stories/{story_id}/tasks` | Create task under user story |
| | `GET` | `/api/v1/stories/{story_id}/tasks` | List tasks for story (Paginated) |
| | `GET` | `/api/v1/tasks/{id}` | Get task details |
| | `PUT` | `/api/v1/tasks/{id}` | Update task |
| | `DELETE` | `/api/v1/tasks/{id}` | Delete task |
| **Reports** | `POST` | `/api/v1/projects/{id}/reports` | Initiate async progress report generation (HTTP `202`) |
| | `GET` | `/api/v1/reports/{job_id}` | Poll background report job status & JSON results |

---

## 13. Database Schema

The application uses an **SQLite 3** relational database located at `backend/agile_project_manager.db`, managed via **SQLAlchemy 2.0 ORM**.

### Entity Relationship Model

```text
Project (1) -------< (N) User Story (1) -------< (N) Task
   │
   └-------------< (N) ReportJob (Async Background Jobs)
```

* **Relational Integrity**: Foreign keys are explicitly enabled on every SQLite connection via `PRAGMA foreign_keys = ON;`.
* **Cascade Deletions**: Configured with `cascade="all, delete-orphan"` so deleting a parent project or story automatically cleans up child items.

For full database table schemas, column types, and constraints, see [docs/database-schema.md](docs/database-schema.md).

---

## 14. Asynchronous Workflow

Generating progress report metrics for a project aggregates statistics across all child stories and tasks. To prevent blocking server threads during heavy calculations, report generation is handled asynchronously:

```text
Client                        Backend REST API                  Background Worker
  │                                  │                                 │
  │ POST /projects/{id}/reports      │                                 │
  ├─────────────────────────────────►│ 1. Validate & Create Job        │
  │ 202 Accepted { job_id }          ├────────────────────────────────►│ 2. Set status = RUNNING
  │◄─────────────────────────────────┤                                 │ 3. Aggregate Stats
  │                                  │                                 │ 4. Set status = COMPLETED
  │ GET /reports/{job_id} (Polling)  │                                 │
  ├─────────────────────────────────►│ 5. Return Status & JSON Payload │
```

### Key Workflow Behaviors
1. **Immediate Response**: Returning HTTP `202 Accepted` with a tracking `job_id`.
2. **State Lifecycle**: `PENDING` --> `RUNNING` --> `COMPLETED` (or `FAILED`).
3. **Idempotency**: Re-requesting a report while a job is `PENDING` or `RUNNING` returns the existing active `job_id`.
4. **Bounded Retries**: If an error occurs, the worker retries up to `MAX_ATTEMPTS = 3` before marking the job as `FAILED`.

For deep architectural details on the background worker engine, see [docs/async-workflow.md](docs/async-workflow.md).

---

## 15. Testing

### Run Backend Automated Pytest Suite

From the `backend` directory, run:

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest
```

* **Test Suite Output**: 45 passed automated unit and integration tests across 4 test modules (`test_api.py`, `test_async_workflow.py`, `test_health.py`, `test_models.py`).
* **Coverage**: Validates REST API routes, Pydantic request/response schemas, SQLAlchemy model constraints, parent-child cascade deletions, health status endpoints, and background worker state transitions.

### Validate Frontend Production Build

From the `frontend` directory, run:

```cmd
cd frontend
npm.cmd run build
```

* Compiles and bundles React 18 production assets into `frontend/dist/` with zero build errors.

---

## 16. Security Considerations

* **Input Validation**: All incoming REST payloads are strictly validated using Pydantic v2 schemas (`ProjectCreate`, `UserStoryCreate`, `TaskCreate`).
* **SQL Injection Prevention**: Built entirely with SQLAlchemy 2.0 ORM parameter binding with zero raw SQL queries.
* **XSS Protection**: React automatically sanitizes rendered DOM elements.
* **CORS Protection**: FastAPI `CORSMiddleware` restricts browser requests to explicitly configured origin domains.
* **Environment Secrets**: Sensitive settings are isolated in `.env` files; `.gitignore` prevents database files and `.env` credentials from being committed to version control.

> [!WARNING]
> **Scope Disclaimer**: Designed for an internal small team (~3–10 users), this project does not include user authentication (OAuth2/JWT) or Role-Based Access Control (RBAC).

For a complete security review, see [docs/security.md](docs/security.md).

---

## 17. Design Decisions & Tradeoffs

* **FastAPI vs. Django**: Selected FastAPI for performance, native async support, and out-of-the-box OpenAPI documentation.
* **React + Vite vs. Next.js**: Chosen for client-side SPA speed and zero server-side rendering complexity for small teams.
* **SQLite vs. PostgreSQL**: Selected SQLite for zero-configuration, file-based persistence suited for local/small team usage.
* **FastAPI `BackgroundTasks` vs. Celery + Redis**: Native background worker eliminates extra infrastructure overhead for small teams.

For full rationale on technical tradeoffs, see [docs/design-decisions.md](docs/design-decisions.md).

---

## 18. AI Usage Statement

Generative AI assistance (Google Antigravity AI Coding Assistant) was utilized during development for scaffold generation, Pydantic schema boilerplate, unit test generation, and documentation drafting. All code, database schemas, and architectural patterns were reviewed, refined, and verified by the developer.

For complete AI usage details, see [docs/ai-usage.md](docs/ai-usage.md).

---

## 19. Future Improvements

What I would improve with more engineering time:
1. **Authentication & RBAC**: Implement JWT authentication and role-based permissions (`Admin`, `Manager`, `Developer`).
2. **PostgreSQL Migration**: Replace SQLite with PostgreSQL for multi-node production concurrency.
3. **Distributed Task Queue**: Upgrade background worker engine from FastAPI `BackgroundTasks` to Redis + Celery.
4. **Containerization & CI/CD**: Package backend and frontend into Docker containers with GitHub Actions automated deployment pipelines.

For the full scaling roadmap, see [docs/future-improvements.md](docs/future-improvements.md).

---

## 20. Documentation Links

- [Architecture Overview](docs/architecture.md)
- [API Documentation](docs/api-documentation.md)
- [Database Schema](docs/database-schema.md)
- [Async Progress Workflow](docs/async-workflow.md)
- [Design Decisions & Tradeoffs](docs/design-decisions.md)
- [Security Considerations](docs/security.md)
- [AI Usage Statement](docs/ai-usage.md)
- [Future Improvements Roadmap](docs/future-improvements.md)

---

## 21. Project Structure

```text
agile-project-manager/
├── backend/
│   ├── app/
│   │   ├── api/             # REST API routes (health, projects, stories, tasks, reports)
│   │   ├── core/            # Database engine, session factory, settings configuration
│   │   ├── models/          # SQLAlchemy 2.0 ORM models & status Enums
│   │   ├── repositories/    # Database query layer & pagination helpers
│   │   ├── schemas/         # Pydantic v2 request & response schemas
│   │   ├── services/        # Business logic & background report worker
│   │   └── main.py          # FastAPI application entry point
│   ├── tests/               # Pytest suite (45 unit & integration tests)
│   ├── .env.example         # Backend environment configuration template
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # Common UI, project cards, story lists, task items, reports
│   │   ├── pages/           # Dashboard, ProjectsPage, ProjectDetails, NotFound
│   │   ├── services/        # Centralized HTTP fetch client & API wrappers
│   │   ├── App.jsx          # React app shell & routing
│   │   └── index.css        # Glassmorphism design tokens & styles
│   ├── .env.example         # Frontend environment configuration template
│   ├── package.json         # Node.js dependencies & scripts
│   └── vite.config.js       # Vite build configuration
├── docs/                    # Complete technical documentation
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
