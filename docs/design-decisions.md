# Architectural & Design Decisions

This document records the key architectural choices, design rationale, and engineering tradeoffs made during the development of the Agile Project Management Tool.

---

## 1. Framework & Tech Stack Decisions

### Decision 1: Python with FastAPI for Backend
- **Decision**: Select FastAPI as the backend web framework.
- **Reason**: Provides high performance via ASGI/asyncio, automatic Pydantic request body validation, and out-of-the-box interactive OpenAPI/Swagger documentation generation (`/docs`).
- **Tradeoff**: Offers less built-in administration tools than Django, requiring explicit architecture design (Service/Repository layers).

### Decision 2: React 18 with Vite for Frontend
- **Decision**: Build the Single Page Application using React 18 powered by Vite.
- **Reason**: Delivers extremely fast hot-module replacement (HMR), component-driven UI architecture, lightweight bundle size, and seamless modern JavaScript developer tooling.
- **Tradeoff**: SPA architectures require client-side routing and state management compared to server-rendered HTML frameworks.

### Decision 3: SQLite for Database Storage
- **Decision**: Use SQLite as the relational storage engine.
- **Reason**: Zero-configuration, file-based embedded relational database perfect for local development and small team environments (~3–10 users). Requires no separate daemon installation.
- **Tradeoff**: SQLite uses database-level locking for writes, making it unsuitable for high-concurrency multi-node production writes without migrating to PostgreSQL.

### Decision 4: SQLAlchemy 2.0 ORM
- **Decision**: Utilize SQLAlchemy 2.0 ORM for database abstraction.
- **Reason**: Offers complete Python object-relational mapping, strict parameter binding to prevent SQL injection, relationship management, and database-agnostic SQL generation.
- **Tradeoff**: Slightly higher abstraction overhead compared to raw SQL queries, but yields vastly superior maintainability and safety.

### Decision 5: RESTful API Conventions
- **Decision**: Adopt standard RESTful API conventions (`GET`, `POST`, `PUT`, `DELETE`).
- **Reason**: Standardized HTTP verbs, URL path hierarchies (`/projects/{id}/stories`), and status codes (`200`, `201`, `202`, `204`, `404`, `422`) ensure intuitive client-server integration.
- **Tradeoff**: REST endpoints can suffer from over-fetching or under-fetching compared to GraphQL, but REST remains vastly simpler to implement, document, and test.

---

## 2. Work Tracking & Data Modeling Decisions

### Decision 6: 3-Tier Hierarchy (`Project` → `User Story` → `Task`)
- **Decision**: Enforce a strict 3-tier work item hierarchy: `Project` $\rightarrow$ `User Story` $\rightarrow$ `Task`.
- **Reason**: Precisely mirrors Agile methodologies for small teams, balancing high-level initiative tracking with granular task execution while avoiding complex n-tier work item trees.
- **Tradeoff**: Does not support arbitrary custom depth levels (e.g. Epics, Sub-tasks), but maintains clear conceptual boundaries.

### Decision 7: 4-Layer Separation (`API` → `Service` → `Repository` → `ORM`)
- **Decision**: Structure backend code into 4 strict decoupled layers: `API` $\rightarrow$ `Service` $\rightarrow$ `Repository` $\rightarrow$ `ORM`.
- **Reason**: Ensures complete separation of concerns. HTTP routes handle requests, services enforce business rules, repositories isolate database queries, and ORM models define schemas.
- **Tradeoff**: Requires slightly more boilerplate files, but prevents business logic leakage into API routes or database models.

### Decision 8: Controlled Enum Work Item & Project Statuses
- **Decision**: Enforce fixed Python `Enum` types for statuses (`ProjectStatus`: `PLANNING`, `ACTIVE`, `COMPLETED`; `WorkItemStatus`: `TODO`, `IN_PROGRESS`, `DONE`).
- **Reason**: Guarantees data integrity across backend services and frontend badge renderers, preventing freeform invalid status strings from entering the database.
- **Tradeoff**: Changing or adding status types requires code deployments and schema migrations rather than runtime string insertions.

### Decision 9: Controlled Enum Priority Levels
- **Decision**: Enforce fixed `PriorityLevel` enums (`LOW`, `MEDIUM`, `HIGH`).
- **Reason**: Standardizes priority sorting, visual badge highlighting, and report metric categorization.
- **Tradeoff**: Prevents custom numerical priority weights, but maintains intuitive UI simplicity for team members.

---

## 3. Asynchronous Workflow & Systems Decisions

### Decision 10: Asynchronous Project Progress Report Generation
- **Decision**: Execute project progress report calculations asynchronously.
- **Reason**: Aggregating completion percentages across all stories and tasks in large projects can block HTTP server threads. Asynchronous processing returns an immediate `202 Accepted` response.
- **Tradeoff**: Requires client-side status polling or WebSocket connections to retrieve finished report artifacts.

### Decision 11: FastAPI `BackgroundTasks` vs External Queues (Celery/Redis)
- **Decision**: Use FastAPI's native `BackgroundTasks` rather than Celery + Redis.
- **Reason**: Perfectly satisfies the small-team deployment requirement (~3–10 users) with zero extra infrastructure overhead (no Redis containers or worker daemons needed).
- **Tradeoff**: Tasks run within the main application process. If the server crashes during execution, in-memory task states are lost.

### Decision 12: Standardized API Pagination
- **Decision**: Implement `page` and `page_size` query pagination across collection GET endpoints (`/projects`, `/stories`, `/tasks`).
- **Reason**: Prevents out-of-memory errors and slow network payloads when retrieving large lists of items.
- **Tradeoff**: Clients must manage pagination state when rendering scrollable lists.

### Decision 13: Database-Backed `ReportJob` Entity
- **Decision**: Store report job state, attempts, error messages, and output payloads in a dedicated `report_jobs` database table.
- **Reason**: Provides persistent job tracking, allows clients to query report job history across restarts, and enables idempotent duplicate request detection.
- **Tradeoff**: Requires database table maintenance and periodic cleanup of legacy report jobs.

### Decision 14: Relational Cascade Deletes (`delete-orphan`)
- **Decision**: Configure SQLAlchemy relationships with `cascade="all, delete-orphan"`.
- **Reason**: Ensures referential integrity. Deleting a parent `Project` automatically deletes all associated `UserStory` items, `Task` items, and `ReportJob` records.
- **Tradeoff**: Deletions are permanent and destructive. The frontend explicitly prompts users with confirmation modals prior to delete API calls.

### Decision 15: Single Database Session Per Request Lifecycle
- **Decision**: Inject SQLAlchemy sessions via FastAPI dependency injection (`get_db`) yielding a single session closed in a `finally` block.
- **Reason**: Prevents database connection leaks and guarantees that every HTTP request runs within an isolated session scope.
- **Tradeoff**: Requires passing background worker session factories explicitly to async worker threads outside the HTTP request lifecycle.
