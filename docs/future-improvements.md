# Project Roadmap & Future Improvements

## 1. Overview
This document clearly distinguishes between the **Current Scope** delivered in the Agile Project Management Tool and the **Future Enhancements Roadmap** planned for production scaling.

---

## 2. Current Implementation Scope

The application currently delivers a complete small-team project management tool suitable for local development and small-team usage with:
- **Architecture**: Split-stack React + Vite frontend and FastAPI backend with a 4-layer clean architecture (`API` $\rightarrow$ `Service` $\rightarrow$ `Repository` $\rightarrow$ `ORM`).
- **Hierarchy**: Strict 3-tier work tracking hierarchy (`Project` $\rightarrow$ `UserStory` $\rightarrow$ `Task`).
- **Persistence**: Relational SQLite database with explicit foreign key enforcement (`PRAGMA foreign_keys = ON;`) and cascading deletes.
- **Async Workflow**: Database-backed non-blocking progress report generation (`ReportJob`) using FastAPI `BackgroundTasks`, polling endpoints, and bounded retry loops.
- **Testing**: 45 automated pytest unit/integration tests and verified Vite production build.

---

## 3. Future Enhancements Roadmap

The following technical enhancements represent the logical next steps for scaling the application from a small-team tool (~3–10 users) to an enterprise-grade platform:

### A. Authentication & Access Control
1. **Authentication (JWT / OAuth2)**: Integrate secure user login using JSON Web Tokens (JWT) or OAuth2 providers (GitHub / Google SSO).
2. **Role-Based Access Control (RBAC)**: Implement granular user roles (`Admin`, `Project Manager`, `Developer`, `Viewer`) to restrict modification privileges.
3. **Multi-Tenant User Management**: Support real user accounts, team creation, and user assignment lookup tables.

### B. Enterprise Infrastructure & Database
4. **PostgreSQL Migration**: Replace SQLite with PostgreSQL for concurrent write scalability, multi-node hosting, and JSONB index support.
5. **Distributed Task Queue (Redis + Celery / Dramatiq)**: Upgrade from FastAPI in-memory `BackgroundTasks` to a distributed task broker (Redis / RabbitMQ) with Celery workers for multi-node background job processing.
6. **Automated Backups & Disaster Recovery**: Configure automated point-in-time database backups and replica failover.

### C. Advanced Collaboration & Monitoring
7. **Email & Slack Notifications**: Trigger automated alerts when tasks are assigned or status transitions occur.
8. **Deadline & Sprint Reminders**: Add target completion dates, sprint boundaries, and automated overdue task reminders.
9. **Activity History & Audit Logging**: Track full mutation logs per work item (who changed what status and when).
10. **Application Performance Monitoring (APM)**: Integrate OpenTelemetry / Sentry / Prometheus for backend telemetry, error tracing, and performance tracking.

### D. DevOps & Cloud Deployment
11. **Docker Containerization**: Package frontend and backend services into multi-stage Docker containers with `docker-compose` orchestration.
12. **Continuous Integration & Deployment (CI/CD)**: Set up GitHub Actions pipelines for automated linting, pytest execution, build validation, and deployment.
13. **Cloud Hosting**: Deploy backend to AWS ECS / GCP Cloud Run and frontend to Vercel / Cloudflare Pages.
