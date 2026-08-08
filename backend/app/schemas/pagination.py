from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    page: int = Field(..., json_schema_extra={"example": 1}, ge=1)
    page_size: int = Field(..., json_schema_extra={"example": 10}, ge=1, le=100)
    total: int = Field(..., json_schema_extra={"example": 25}, ge=0)
