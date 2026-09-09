from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Response, status
from supabase import Client

from app.dependencies.auth import AuthenticatedUser, get_current_user, get_user_db
from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import project_service

router = APIRouter(tags=["Projects"])


@router.post(
    "/projects",
    response_model=ApiResponse[ProjectResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
)
def create_project(
    data: ProjectCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Client = Depends(get_user_db),
):
    project = project_service.create_project(current_user, data, db)
    return ApiResponse(data=ProjectResponse.model_validate(project))


@router.get(
    "/projects",
    response_model=ApiResponse[List[ProjectResponse]],
    status_code=status.HTTP_200_OK,
    summary="List projects owned by current user",
)
def list_projects(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(default=None, description="Search term for project name"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Client = Depends(get_user_db),
):
    projects, total = project_service.list_projects(current_user, page, page_size, search, db)
    return ApiResponse(
        data=[ProjectResponse.model_validate(p) for p in projects],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.get(
    "/projects/{project_id}",
    response_model=ApiResponse[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="Get project by ID",
)
def get_project(
    project_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Client = Depends(get_user_db),
):
    project = project_service.get_project(current_user, project_id, db)
    return ApiResponse(data=ProjectResponse.model_validate(project))


@router.patch(
    "/projects/{project_id}",
    response_model=ApiResponse[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="Update project details",
)
def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Client = Depends(get_user_db),
):
    updated = project_service.update_project(current_user, project_id, data, db)
    return ApiResponse(data=ProjectResponse.model_validate(updated))


@router.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project and cascading resources",
)
def delete_project(
    project_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Client = Depends(get_user_db),
):
    project_service.delete_project(current_user, project_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
