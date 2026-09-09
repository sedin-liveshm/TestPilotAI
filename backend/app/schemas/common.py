from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata matching frontend expectation."""
    page: int
    page_size: int
    total: int

    model_config = ConfigDict(from_attributes=True)


class ApiResponse(BaseModel, Generic[T]):
    """Standardized API response wrapper matching frontend api-client."""
    data: T
    meta: Optional[PaginationMeta] = None

    model_config = ConfigDict(from_attributes=True)


class ApiErrorDetail(BaseModel):
    """Standard error detail object."""
    message: str
    code: Optional[str] = None
    details: Optional[Any] = None


class ApiErrorResponse(BaseModel):
    """Standardized API error response."""
    error: ApiErrorDetail
