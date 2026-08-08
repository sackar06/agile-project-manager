# Database Schema Documentation

## 1. Overview & Entity Relationship Diagram

The Agile Project Management Tool utilizes an SQLite database managed via SQLAlchemy 2.0 ORM entities structured in a strict relational hierarchy:

```text
       Project
       │     │
   1:N │     │ 1:N (Cascade Delete-Orphan)
       ▼     ▼
UserStory   ReportJob
   │
1:N│ (Cascade Delete-Orphan)
   ▼
 Task
```

---

## 2. Table Specifications

### A. `projects` Table
Represents top-level initiatives or product codebases managed by the team.

| Column Name | Data Type | Nullable | Key Type | Purpose & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | No | Primary Key | Autoincremented project identifier |
| `name` | `VARCHAR(100)` | No | None | Name of project (Max 100 chars) |
| `description` | `TEXT` | Yes | None | Optional scope description |
| `status` | `VARCHAR(20)` | No | Enum (`ProjectStatus`) | `PLANNING`, `ACTIVE`, or `COMPLETED` |
| `created_at` | `DATETIME` | No | None | UTC creation timestamp |
| `updated_at` | `DATETIME` | No | None | UTC last update timestamp |

---

### B. `user_stories` Table
Represents user-facing features or requirements belonging to a project.

| Column Name | Data Type | Nullable | Key Type | Purpose & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | No | Primary Key | Autoincremented story identifier |
| `project_id` | `INTEGER` | No | Foreign Key (`projects.id`) | Indexed parent project reference (Cascade Delete) |
| `title` | `VARCHAR(200)` | No | None | User story summary title |
| `description` | `TEXT` | Yes | None | Optional acceptance criteria |
| `status` | `VARCHAR(20)` | No | Enum (`WorkItemStatus`) | `TODO`, `IN_PROGRESS`, or `DONE` |
| `priority` | `VARCHAR(20)` | No | Enum (`PriorityLevel`) | `LOW`, `MEDIUM`, or `HIGH` |
| `created_at` | `DATETIME` | No | None | UTC creation timestamp |
| `updated_at` | `DATETIME` | No | None | UTC last update timestamp |

---

### C. `tasks` Table
Represents concrete implementation items required to complete a user story.

| Column Name | Data Type | Nullable | Key Type | Purpose & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | No | Primary Key | Autoincremented task identifier |
| `user_story_id` | `INTEGER` | No | Foreign Key (`user_stories.id`) | Indexed parent story reference (Cascade Delete) |
| `title` | `VARCHAR(200)` | No | None | Actionable task summary |
| `description` | `TEXT` | Yes | None | Optional implementation notes |
| `status` | `VARCHAR(20)` | No | Enum (`WorkItemStatus`) | `TODO`, `IN_PROGRESS`, or `DONE` |
| `priority` | `VARCHAR(20)` | No | Enum (`PriorityLevel`) | `LOW`, `MEDIUM`, or `HIGH` |
| `assigned_to` | `VARCHAR(100)` | Yes | None | Optional assignee name |
| `created_at` | `DATETIME` | No | None | UTC creation timestamp |
| `updated_at` | `DATETIME` | No | None | UTC last update timestamp |

---

### D. `report_jobs` Table
Tracks asynchronous project progress report calculation jobs, execution attempts, error logs, and computed JSON output payloads.

| Column Name | Data Type | Nullable | Key Type | Purpose & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | No | Primary Key | Autoincremented job identifier |
| `project_id` | `INTEGER` | No | Foreign Key (`projects.id`) | Indexed project reference (Cascade Delete) |
| `status` | `VARCHAR(20)` | No | Enum (`JobStatus`) | `PENDING`, `RUNNING`, `COMPLETED`, or `FAILED` |
| `attempts` | `INTEGER` | No | None | Execution attempt counter (Max 3) |
| `error_message` | `TEXT` | Yes | None | Error log trace if calculation fails |
| `report_data` | `JSON` | Yes | None | Output statistics JSON payload |
| `created_at` | `DATETIME` | No | None | UTC job creation timestamp |
| `started_at` | `DATETIME` | Yes | None | UTC job start timestamp |
| `completed_at` | `DATETIME` | Yes | None | UTC job completion timestamp |

---

## 3. Enumeration Values

### `ProjectStatus`
- `PLANNING` (Default): Initial project scoping phase.
- `ACTIVE`: Development work is actively underway.
- `COMPLETED`: All project deliverables have been finalized.

### `WorkItemStatus`
- `TODO` (Default): Backlogged item waiting to start.
- `IN_PROGRESS`: Item is currently being executed.
- `DONE`: Item implementation is complete and verified.

### `PriorityLevel`
- `LOW`: Low urgency item.
- `MEDIUM` (Default): Standard feature priority.
- `HIGH`: Critical blocking priority.

### `JobStatus`
- `PENDING`: Report job enqueued.
- `RUNNING`: Worker thread calculating statistics.
- `COMPLETED`: Calculation finished and JSON report persisted.
- `FAILED`: Report calculation failed after maximum retry attempts.

---

## 4. Foreign Key Enforcement & Cascades
- Foreign keys are enforced on all SQLite connections via SQLAlchemy event listener (`PRAGMA foreign_keys = ON;`).
- Cascading deletes (`cascade="all, delete-orphan"`) ensure that deleting a project automatically removes all child user stories, tasks, and report jobs.
