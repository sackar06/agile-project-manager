from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine
from app.models import Base, Project, UserStory, Task, ReportJob
from app.api.health import router as health_router
from app.api.projects import router as projects_router
from app.api.user_stories import router as user_stories_router
from app.api.tasks import router as tasks_router
from app.api.reports import router as reports_router

# Create database tables on startup
Base.metadata.create_all(bind=engine)

description = """
### Agile Project Management Tool - REST API

This API supports a strict 3-tier work tracking hierarchy:

$$\\text{Project} \\longrightarrow \\text{User Story} \\longrightarrow \\text{Task}$$

* **Project**: Top-level initiative or codebase container.
* **User Story**: Belongs to a Project; represents user-facing requirements.
* **Task**: Belongs to a User Story; represents actionable implementation items.
* **Reports**: Asynchronous progress report generation (`POST /api/v1/projects/{id}/reports`, `GET /api/v1/reports/{job_id}`).
"""

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=description,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(projects_router, prefix=settings.API_V1_STR)
app.include_router(user_stories_router, prefix=settings.API_V1_STR)
app.include_router(tasks_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "health": "/health",
        "api_v1": settings.API_V1_STR
    }
