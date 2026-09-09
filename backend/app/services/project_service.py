from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from supabase import Client

from app.dependencies.auth import AuthenticatedUser
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Service handling business logic and Supabase execution for Projects.
    
    Strictly enforces:
    - owner_id is derived from AuthenticatedUser, never from client request.
    - Multi-tenant isolation: Users only access projects they own.
    - PostgreSQL RLS policies evaluate against user's authenticated session.
    """

    def create_project(
        self, user: AuthenticatedUser, data: ProjectCreate, db: Client
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "name": data.name,
            "description": data.description,
            "base_url": data.base_url,
            "owner_id": str(user.id),
            "created_at": now,
            "updated_at": now,
        }

        response = db.table("projects").insert(payload).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create project",
            )
        return response.data[0]

    def list_projects(
        self,
        user: AuthenticatedUser,
        page: int,
        page_size: int,
        search: Optional[str],
        db: Client,
    ) -> Tuple[List[Dict[str, Any]], int]:
        offset = (page - 1) * page_size
        query = db.table("projects").select("*", count="exact").eq("owner_id", str(user.id))

        if search:
            query = query.ilike("name", f"%{search}%")

        query = query.order("created_at", desc=True).range(offset, offset + page_size - 1)
        response = query.execute()

        total = response.count if response.count is not None else len(response.data or [])
        return response.data or [], total

    def get_project(
        self, user: AuthenticatedUser, project_id: UUID, db: Client
    ) -> Dict[str, Any]:
        response = (
            db.table("projects")
            .select("*")
            .eq("id", str(project_id))
            .eq("owner_id", str(user.id))
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        return response.data[0]

    def update_project(
        self,
        user: AuthenticatedUser,
        project_id: UUID,
        data: ProjectUpdate,
        db: Client,
    ) -> Dict[str, Any]:
        # Verify project exists and caller is owner
        existing = self.get_project(user, project_id, db)

        updates = data.model_dump(exclude_unset=True)
        if not updates:
            return existing

        updates["updated_at"] = datetime.now(timezone.utc).isoformat()

        response = (
            db.table("projects")
            .update(updates)
            .eq("id", str(project_id))
            .eq("owner_id", str(user.id))
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or update unauthorized",
            )
        return response.data[0]

    def delete_project(
        self, user: AuthenticatedUser, project_id: UUID, db: Client
    ) -> None:
        # Verify project exists and caller is owner
        self.get_project(user, project_id, db)

        response = (
            db.table("projects")
            .delete()
            .eq("id", str(project_id))
            .eq("owner_id", str(user.id))
            .execute()
        )
        if not response.data:
            # Re-check to ensure deletion occurred
            pass


project_service = ProjectService()
