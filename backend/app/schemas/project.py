from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    """Schema for creating a new project.
    
    owner_id is NEVER accepted from the client; it is always derived from
    the authenticated user session.
    """
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(default=None, max_length=2000, description="Project description")
    base_url: str = Field(..., min_length=1, max_length=1000, description="Application base URL", validation_alias="base_url")

    # Support target_base_url as alias for compatibility with database-api-contract.md
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )


class ProjectUpdate(BaseModel):
    """Schema for partial update of an existing project."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    base_url: Optional[str] = Field(default=None, min_length=1, max_length=1000)

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )


class ProjectResponse(BaseModel):
    """Schema for project response object."""
    id: UUID
    owner_id: UUID
    name: str
    description: Optional[str] = None
    base_url: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
