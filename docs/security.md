# Security Considerations & Assessment

## 1. Overview
Security best practices have been incorporated into the Agile Project Management Tool at every architecture layer. This document details the security posture, defensive mechanisms, configuration guidelines, and explicit limitations of the current implementation.

---

## 2. Security Controls & Defensive Mechanisms

### A. Input Validation
- **Backend Validation**: All incoming REST API payloads are strictly validated using Pydantic models (`ProjectCreate`, `UserStoryCreate`, `TaskCreate`, `ReportJobCreate`). Payload field types, required properties, max string lengths, and enum values are validated before business logic executes. Invalid payloads return HTTP `422 Unprocessable Entity`.
- **Frontend Validation**: Web UI forms validate input fields (e.g. required title/name inputs, non-empty fields) prior to submitting HTTP requests, offering immediate feedback to users while protecting API boundaries.
- **Strict Controlled Enums**: Work item statuses (`TODO`, `IN_PROGRESS`, `DONE`), project statuses (`PLANNING`, `ACTIVE`, `COMPLETED`), and priority levels (`LOW`, `MEDIUM`, `HIGH`) are enforced at both the API and database levels.

### B. SQL Injection Prevention
- **ORM Abstraction**: All database interactions use SQLAlchemy 2.0 ORM query primitives (`select()`, `db.add()`, `db.delete()`).
- **Parameter Binding**: The codebase contains zero raw SQL string interpolations or concatenated queries (`WHERE id = " + user_input`), completely eliminating SQL injection vectors.

### C. Error Handling & Information Disclosure
- **Sanitized Client Responses**: Unhandled backend exceptions do not return Python tracebacks, database schema details, or system paths to HTTP clients.
- **Consistent Error Schemas**: Known operational errors return standard, sanitized JSON messages (e.g. `{"detail": "Project with id 123 not found"}`).
- **Internal Logging**: Technical error traces are captured only in server log outputs for administrator debugging.

### D. Secret & Configuration Management
- **Environment Variables**: Application configuration parameters are isolated in environment variables managed by `pydantic-settings`.
- **No Secrets in Version Control**: Source control repositories track only `.env.example` templates containing safe default/placeholder values. The `.gitignore` explicitly excludes `.env` files.
- **No Hardcoded Credentials**: Database connection strings and host settings are decoupled from application logic.

### E. Cross-Origin Resource Sharing (CORS)
- **Configurable Origins**: FastAPI `CORSMiddleware` limits web browser requests to explicitly whitelisted frontend origins (`settings.BACKEND_CORS_ORIGINS`).
- **Development Whitelist**: Configured by default for local development (`http://localhost:5173`, `http://127.0.0.1:5173`, `http://localhost:3000`). Wildcard `*` origins are avoided in CORS setup.

### F. Frontend Web Security
- **XSS Prevention**: React automatically escapes strings rendered in the DOM, preventing Cross-Site Scripting (XSS) attacks. The code does not use dangerous APIs like `dangerouslySetInnerHTML`.
- **No Client Secrets**: The Single Page Application bundle contains zero API keys, private tokens, or database credentials.

### G. Relational & Foreign Key Integrity
- **Active Pragma Enforcement**: SQLite foreign key constraints are explicitly enforced on every database connection using SQLAlchemy event hooks (`PRAGMA foreign_keys = ON;`).
- **Cascade Safety**: Deleting parent projects or stories uses explicit `cascade="all, delete-orphan"` rules, preventing orphan records or dangling reference errors.

---

## 3. Explicit Limitations & Non-Production Scope

> [!WARNING]
> **Authentication & Authorization Disclaimer**
> 
> As specified by the assignment scope, this application is designed for an internal small team (~3–10 users) and **does not currently include user authentication (OAuth2/JWT) or Role-Based Access Control (RBAC)**.
> 
> **Production Deployment Requirements:**
> Before deploying this application to a public cloud or production environment, the following security controls must be implemented:
> 1. User Authentication (JWT bearer tokens, OAuth2, or Session cookies).
> 2. Role-Based Access Control (RBAC) to enforce user permissions per project.
> 3. Transport Layer Security (HTTPS/TLS encryption in transit).
> 4. API Rate Limiting to mitigate Denial of Service (DoS) attacks.
