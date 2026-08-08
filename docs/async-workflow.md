# Asynchronous / Background Workflow Documentation

## 1. Why Report Generation is Asynchronous

Calculating project statistics requires reading across all child `UserStory` items and their granular `Task` records. For large projects, synchronously aggregating counts and completion percentages blocks the HTTP request thread, leading to slow response times and potential gateway timeouts.

By executing report generation asynchronously:
1. The client receives an immediate non-blocking `202 Accepted` HTTP response containing a `job_id`.
2. The server processes report calculations in a background worker thread.
3. The client polls `GET /api/v1/reports/{job_id}` to retrieve progress status and the final JSON report payload.

---

## 2. Request Handling & HTTP 202 Accepted

When a client sends a `POST /api/v1/projects/{id}/reports` request:
1. **Validation**: The backend verifies that the requested project exists in the database. If not found, HTTP `404` is returned immediately.
2. **Idempotency Check**: The service checks if an existing `ReportJob` for the project has a `PENDING` or `RUNNING` status. If so, it reuses the existing job ID rather than spawning duplicate worker jobs.
3. **Job Creation**: A new `ReportJob` record is created in the database with status `PENDING`.
4. **Immediate Response**: The server returns an HTTP `202 Accepted` status code with the JSON response:
   ```json
   {
     "job_id": 42,
     "status": "PENDING",
     "message": "Report generation started"
   }
   ```

---

## 3. Job Lifecycle & State Transitions

A `ReportJob` moves through the following lifecycle states:

```text
       ┌───────────┐
       │  PENDING  │ (Job created in DB)
       └─────┬─────┘
             │
             ▼
       ┌───────────┐
       │  RUNNING  │ (Worker thread executing calculation)
       └─────┬─────┘
             │
     ┌───────┴───────┐
     │               │
     ▼               ▼
┌───────────┐  ┌───────────┐
│ COMPLETED │  │  FAILED   │ (Attempts >= 3)
└───────────┘  └───────────┘
```

---

## 4. Background Processing & Retry Engine

Background processing is managed by `ReportService.execute_background_job()` running via FastAPI `BackgroundTasks`:

- **Worker Execution**: The background worker opens a fresh database session, updates the job status to `RUNNING`, sets `started_at`, and aggregates statistics across user stories and tasks.
- **Bounded Retry Loop**: If a database error or calculation exception occurs:
  1. The worker increments the `attempts` counter.
  2. The error message is stored in `ReportJob.error_message`.
  3. If `attempts < 3`, the worker retries the calculation.
  4. If `attempts >= 3`, the job status transitions to `FAILED`, `completed_at` is set, and execution stops.
- **Successful Completion**: Upon successful calculation, the generated JSON report payload is saved into `ReportJob.report_data`, status is set to `COMPLETED`, and `completed_at` timestamp is recorded.

---

## 5. Duplicate Job Handling (Idempotency)

To protect backend resources from duplicate button clicks or repeated polling requests, report generation is idempotent. Re-submitting a report request while a job is `PENDING` or `RUNNING` returns the active `job_id` with message `"Existing report job currently in progress"`.

---

## 6. Implementation Limitations

While native FastAPI `BackgroundTasks` works cleanly for small teams (~3–10 users):
1. **In-Memory Worker Threads**: Tasks run within the main web application process memory.
2. **Process Crash Loss**: If the web server process is forcefully terminated while a job is running, in-memory worker threads die, leaving jobs in a dangling `RUNNING` state.
3. **Single Instance Scope**: Jobs cannot be distributed across multiple worker servers.

---

## 7. Production Queue Scaling Roadmap

For enterprise multi-node deployments:
- **Message Broker**: Redis or RabbitMQ for persistent, distributed job queuing.
- **Worker Pool**: Celery / Dramatiq background workers running in isolated container pools.
- **Dead Letter Queue**: Storing unrecoverable failed jobs for developer inspection.
- **Artifact Storage**: Exporting PDF/CSV report artifacts to AWS S3 or Google Cloud Storage.
