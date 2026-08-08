from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "ok"}, description="Status of the API service")
    app_name: str = Field(..., json_schema_extra={"example": "Agile Project Manager"}, description="Application name")
    version: str = Field(..., json_schema_extra={"example": "0.1.0"}, description="Application version")
    database: str = Field(..., json_schema_extra={"example": "connected"}, description="Database connectivity status")

