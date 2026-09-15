from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.test_ir import TestIR


class TestCreate(BaseModel):
    """Schema for creating a new test case under a project.
    
    Must conform to canonical Test IR schema defined by Dev 2.
    """
    __test__ = False
    name: str = Field(..., min_length=1, max_length=255, description="Test name")
    description: Optional[str] = Field(default=None, max_length=2000, description="Test description")
    test_ir: TestIR = Field(..., description="Canonical Test IR definition")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )


class TestUpdate(BaseModel):
    """Schema for partial update of an existing test."""
    __test__ = False
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    test_ir: Optional[TestIR] = Field(default=None, description="Updated canonical Test IR")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )


class TestResponse(BaseModel):
    """Schema for test response object."""
    __test__ = False
    id: UUID
    project_id: UUID
    name: str
    description: Optional[str] = None
    test_ir: Dict[str, Any]
    ir_version: int = 1
    created_at: datetime
    updated_at: datetime

    @field_validator("test_ir")
    @classmethod
    def validate_test_ir(cls, v: Any) -> Dict[str, Any]:
        if isinstance(v, TestIR):
            return v.model_dump(mode="json", exclude_none=True)
        validated = TestIR.model_validate(v)
        return validated.model_dump(mode="json", exclude_none=True)

    model_config = ConfigDict(from_attributes=True)
