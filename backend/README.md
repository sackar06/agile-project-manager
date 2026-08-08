# Agile Project Manager - Backend

FastAPI backend server for the Agile Project Manager tool.

## Structure

```text
app/
├── api/          # API route definitions
│   └── health.py # Health check endpoint
├── core/         # Settings & database connection setup
│   ├── config.py
│   └── database.py
├── models/       # SQLAlchemy database models
│   └── base.py
├── schemas/      # Pydantic schema validation models
│   └── health.py
├── services/     # Business logic layer
├── repositories/ # Database query access layer
└── main.py       # Application entry point
```

## Running Backend

```bash
# Activate virtual environment
# Windows: .\venv\Scripts\Activate.ps1
# Unix: source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- API Base: `http://127.0.0.1:8000/api/v1`
- Health Endpoint: `http://127.0.0.1:8000/health`
- Interactive OpenAPI Swagger Docs: `http://127.0.0.1:8000/docs`
- ReDoc API Documentation: `http://127.0.0.1:8000/redoc`
- Full API Reference Document: [docs/api-documentation.md](../docs/api-documentation.md)

