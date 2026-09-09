from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Response, status
from supabase import Client

from app.dependencies.auth import AuthenticatedUser, get_current_user, get_user_db
from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.test import TestCreate, TestResponse, TestUpdate
from app.services.test_service import test_service

router = APIRouter(tags=["Tests"])


@router.post(
    "/projects/{project_id}/tests",
    response_model=ApiResponse[TestResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new test under a project",
)
def create_test(
    project_id: UUID,
    data: TestCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Client = Depends(get_user_db),
):
    test_record = test_service.create_test(current_user, project_id, data, db)
    return ApiResponse(data=TestResponse.model_validate(test_record))


@router.get(
    "/projects/{project_id}/tests",
    response_model=ApiResponse[List[TestResponse]],
    status_code=status.HTTP_200_OK,
    summary="List tests belonging to a project",
)
def list_tests(
    project_id: UUID,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(default=None, description="Search term for test name"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Client = Depends(get_user_db),
):
    tests, total = test_service.list_tests(current_user, project_id, page, page_size, search, db)
    return ApiResponse(
        data=[TestResponse.model_validate(t) for t in tests],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.get(
    "/tests/{test_id}",
    response_model=ApiResponse[TestResponse],
    status_code=status.HTTP_200_OK,
    summary="Get test details including Test IR",
)
def get_test(
    test_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Client = Depends(get_user_db),
):
    test_record = test_service.get_test(current_user, test_id, db)
    return ApiResponse(data=TestResponse.model_validate(test_record))


@router.patch(
    "/tests/{test_id}",
    response_model=ApiResponse[TestResponse],
    status_code=status.HTTP_200_OK,
    summary="Update test details or Test IR",
)
def update_test(
    test_id: UUID,
    data: TestUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Client = Depends(get_user_db),
):
    updated = test_service.update_test(current_user, test_id, data, db)
    return ApiResponse(data=TestResponse.model_validate(updated))


@router.delete(
    "/tests/{test_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete test",
)
def delete_test(
    test_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Client = Depends(get_user_db),
):
    test_service.delete_test(current_user, test_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
