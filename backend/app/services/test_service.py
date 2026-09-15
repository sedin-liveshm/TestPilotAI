from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from supabase import Client

from app.dependencies.auth import AuthenticatedUser
from app.schemas.test import TestCreate, TestUpdate
from app.schemas.test_ir import TestIR
from app.services.project_service import project_service

logger = logging.getLogger(__name__)


class TestService:
    """Service handling business logic and Supabase execution for Tests.
    
    Strictly enforces:
    - Tests belong to parent projects; user must own the parent project.
    - Test IR schema strictly validated against canonical Test IR v1 on write and read.
    - Multi-tenant isolation: Users only access tests belonging to projects they own.
    - PostgreSQL RLS policies evaluate against user's authenticated session.
    - Corrupted or unsupported data is rejected on read without silent mutation.
    """

    def _validate_stored_ir(self, test_record: Dict[str, Any]) -> Dict[str, Any]:
        """Validate stored Test IR and ir_version on read.
        
        Enforces Phase 5 (Validation on Read):
        1. Read test_ir and ir_version.
        2. Validate against supported Test IR v1 contract.
        3. If invalid or unsupported: do not silently transform it, log error
           details for debugging, and raise clear HTTP 500 application error without
           exposing sensitive database details.
        4. Never automatically mutate corrupted data.
        """
        ir_version = test_record.get("ir_version")
        raw_ir = test_record.get("test_ir")

        if ir_version != 1:
            logger.error(
                "Unsupported IR version %s for test %s",
                ir_version,
                test_record.get("id"),
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Stored Test IR has an unsupported version",
            )

        if not isinstance(raw_ir, dict):
            logger.error(
                "Stored Test IR is not a valid JSON object for test %s: %r",
                test_record.get("id"),
                raw_ir,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Stored Test IR is corrupted or invalid",
            )

        try:
            validated_ir = TestIR.model_validate(raw_ir)
        except Exception as err:
            logger.error(
                "Stored Test IR failed validation for test %s: %s",
                test_record.get("id"),
                err,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Stored Test IR failed validation against canonical contract",
            )

        test_record["test_ir"] = validated_ir.model_dump(mode="json", exclude_none=True)
        return test_record

    def create_test(
        self,
        user: AuthenticatedUser,
        project_id: UUID,
        data: TestCreate,
        db: Client,
    ) -> Dict[str, Any]:
        # 1. Enforce parent project ownership
        project_service.get_project(user, project_id, db)

        # 2. Prepare test payload with canonical Test IR JSON
        now = datetime.now(timezone.utc).isoformat()
        test_ir_dict = data.test_ir.model_dump(mode="json", exclude_none=True)

        payload = {
            "project_id": str(project_id),
            "name": data.name,
            "description": data.description,
            "test_ir": test_ir_dict,
            "ir_version": 1,
            "created_at": now,
            "updated_at": now,
        }

        response = db.table("tests").insert(payload).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create test",
            )
        return self._validate_stored_ir(response.data[0])

    def list_tests(
        self,
        user: AuthenticatedUser,
        project_id: UUID,
        page: int,
        page_size: int,
        search: Optional[str],
        db: Client,
    ) -> Tuple[List[Dict[str, Any]], int]:
        # Verify parent project ownership
        project_service.get_project(user, project_id, db)

        offset = (page - 1) * page_size
        query = db.table("tests").select("*", count="exact").eq("project_id", str(project_id))

        if search:
            query = query.ilike("name", f"%{search}%")

        query = query.order("created_at", desc=True).range(offset, offset + page_size - 1)
        response = query.execute()

        total = response.count if response.count is not None else len(response.data or [])
        validated_tests = [self._validate_stored_ir(t) for t in (response.data or [])]
        return validated_tests, total

    def get_test(
        self, user: AuthenticatedUser, test_id: UUID, db: Client
    ) -> Dict[str, Any]:
        response = db.table("tests").select("*").eq("id", str(test_id)).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found",
            )

        test_record = response.data[0]

        # Verify caller owns the parent project
        parent_project_id = UUID(test_record["project_id"])
        project_service.get_project(user, parent_project_id, db)

        return self._validate_stored_ir(test_record)

    def update_test(
        self,
        user: AuthenticatedUser,
        test_id: UUID,
        data: TestUpdate,
        db: Client,
    ) -> Dict[str, Any]:
        existing = self.get_test(user, test_id, db)

        updates: Dict[str, Any] = {}
        if data.name is not None:
            updates["name"] = data.name
        if data.description is not None:
            updates["description"] = data.description
        if data.test_ir is not None:
            updates["test_ir"] = data.test_ir.model_dump(mode="json", exclude_none=True)
            updates["ir_version"] = 1

        if not updates:
            return existing

        updates["updated_at"] = datetime.now(timezone.utc).isoformat()

        response = (
            db.table("tests")
            .update(updates)
            .eq("id", str(test_id))
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found or update unauthorized",
            )
        return self._validate_stored_ir(response.data[0])

    def delete_test(
        self, user: AuthenticatedUser, test_id: UUID, db: Client
    ) -> None:
        self.get_test(user, test_id, db)

        db.table("tests").delete().eq("id", str(test_id)).execute()


test_service = TestService()
