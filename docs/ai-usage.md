# AI Assistance & Usage Statement

## Overview
Generative AI assistance (Google Antigravity AI Coding Assistant) was utilized during the development of the Agile Project Management Tool. This document transparently outlines how AI tools were integrated into the engineering workflow, the scope of assistance, and the verification methods applied.

---

## 1. Scope of AI Assistance

AI assistance was leveraged across the following project lifecycle phases:

- **Architecture & System Design**: Assisting in structuring the 4-layer backend pattern (`API` $\rightarrow$ `Service` $\rightarrow$ `Repository` $\rightarrow$ `ORM`) and modeling the 3-tier work item hierarchy (`Project` $\rightarrow$ `UserStory` $\rightarrow$ `Task`).
- **Boilerplate & Schema Generation**: Generating initial FastAPI Pydantic request/response schemas, SQLAlchemy model declarations, and React UI component skeletons.
- **Async Workflow Engineering**: Designing the non-blocking report generation workflow utilizing FastAPI `BackgroundTasks`, status polling endpoints, and bounded retry loops (`MAX_ATTEMPTS = 3`).
- **Documentation & Test Suite Creation**: Drafting comprehensive markdown documentation (`architecture.md`, `database-schema.md`, `design-decisions.md`, `async-workflow.md`, `security.md`) and generating pytest unit/integration test cases.

---

## 2. Developer Review, Ownership & Verification

While AI tools assisted in code generation and drafting, **all architectural decisions, source code changes, and configuration settings were reviewed, validated, and tested by the developer**.

Specific verification steps performed include:
1. **Requirement Alignment**: Every feature was verified against the assignment specification to ensure zero scope creep or missing core requirements.
2. **Automated Testing**: Running the complete backend pytest suite (45/45 tests passing) to ensure 100% functional correctness, parent-child integrity, and error response handling.
3. **Frontend Production Build**: Running Vite production builds to ensure zero bundle errors, TypeScript/JavaScript syntax issues, or styling defects.
4. **Manual End-to-End Walkthrough**: Executing realistic project management scenarios (creating projects, stories, tasks, updating statuses, triggering async reports, and verifying DB metrics).
