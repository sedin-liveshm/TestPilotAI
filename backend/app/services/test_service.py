from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from supabase import Client

from app.dependencies.auth import AuthenticatedUser
from app.schemas.test import TestCreate, TestUpdate
from app.services.project_service import project_service


class TestService:
    """Service handling business logic and Supabase execution for Tests.
    
    Strictly enforces:
    - Tests belong to parent projects; user must own the parent project.
    - Test IR schema strictly validated against canonical Test IR v1.
    - Multi-tenant isolation: Users only access tests belonging to projects they own.
    - PostgreSQL RLS policies evaluate against user's authenticated session.
    """

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
        test_ir_dict = data.test_ir.model_dump()

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
        return response.data[0]

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
        return response.data or [], total

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

        return test_record

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
            updates["test_ir"] = data.test_ir.model_dump()
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
        return response.data[0]

    def delete_test(
        self, user: AuthenticatedUser, test_id: UUID, db: Client
    ) -> None:
        self.get_test(user, test_id, db)

        db.table("tests").delete().eq("id", str(test_id)).execute()


test_service = TestService()
