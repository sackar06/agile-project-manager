# Architecture Documentation

## 1. High-Level Architecture Overview

The Agile Project Management Tool uses a modern split-stack web architecture with clean layer boundaries:

```text
React (Frontend SPA)
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
 SQLite (Relational Database)
```

---

## 2. Background Progress Report Generation Flow

```text
React Frontend              FastAPI Backend              Database (SQLite)          Background Worker
      │                            │                            │                           │
      │ POST /projects/{id}/reports│                            │                           │
      ├───────────────────────────►│                            │                           │
      │                            │ 1. Validate Project Exists │                           │
      │                            │ 2. Create ReportJob Record │                           │
      │                            ├───────────────────────────►│                           │
      │                            │    (status = PENDING)      │                           │
      │                            │                            │                           │
      │ 202 Accepted { job_id }    │                            │                           │
      │◄───────────────────────────┤                            │                           │
      │                            │                            │ 3. Spawn BackgroundTask   │
      │                            │                            └──────────────────────────►│
      │                            │                                                        │
      │                            │                               4. Set status = RUNNING  │
      │                            │                               5. Aggregate Statistics  │
      │                            │                                                        │
      │                            │                               ┌── Success ─────────────┐
      │                            │                               │ Store report_data      │
      │                            │                               │ status = COMPLETED     │
      │                            │                               └────────────────────────┘
      │                            │                                                        │
      │                            │                               ┌── Failure (< 3 tries)  │
      │                            │                               │ attempts += 1          │
      │                            │                               │ Retry calculation      │
      │                            │                               └────────────────────────┘
      │                            │                                                        │
      │                            │                               ┌── Failure (>= 3 tries) │
      │                            │                               │ Store error_message    │
      │                            │                               │ status = FAILED        │
      │                            │                               └────────────────────────┘
      │                            │                                                        │
      │ GET /reports/{job_id}      │                                                        │
      ├───────────────────────────►│ 6. Query Job Status & Report Payload                   │
      │◄───────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Component Responsibilities

### A. Frontend Layer (`frontend/src/`)
- Single Page Application built with React 18 and Vite.
- Manages client-side routing, user interface state, modal dialogs, and polling timers.
- Communicates with the backend REST API via a centralized client (`src/services/api.js`).

### B. API Layer (`backend/app/api/`)
- Registers RESTful HTTP endpoints for Projects, User Stories, Tasks, and Reports.
- Handles path parameters, query string parsing, HTTP status codes (`200`, `201`, `202`, `204`, `404`, `422`), and dependency injection (`get_db`).

### C. Schema Layer (`backend/app/schemas/`)
- Pydantic models enforcing strict input validation, data type coercion, default values, and serialization for request bodies and response payloads.

### D. Service Layer (`backend/app/services/`)
- Encapsulates core domain business rules and parent-child entity validation (e.g. verifying parent `Project` existence before creating `UserStory`).

### E. Repository Layer (`backend/app/repositories/`)
- Encapsulates database queries using SQLAlchemy ORM primitives. Isolates limit/offset pagination calculations and filtering logic from business services.

### F. Model Layer (`backend/app/models/`)
- Defines SQLAlchemy 2.0 ORM mapped entities (`Project`, `UserStory`, `Task`, `ReportJob`), foreign key constraints, indices, and cascade rules (`delete-orphan`).

### G. Database Layer (SQLite)
- Embedded relational database storing application entities in `agile_project_manager.db`. Enforces foreign key constraints via `PRAGMA foreign_keys = ON;`.

### H. Background Processing Worker (`backend/app/services/report_service.py`)
- Executes asynchronous report generation in non-blocking worker threads. Manages job status transitions (`PENDING` $\rightarrow$ `RUNNING` $\rightarrow$ `COMPLETED` / `FAILED`), bounded retry execution (`MAX_ATTEMPTS = 3`), and error messaging.
