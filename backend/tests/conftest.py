import time
import uuid
import jwt
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies.auth import AuthenticatedUser, get_current_user, get_user_db
from tests.mock_supabase import MockSupabaseDB

USER_A_ID = "00000000-0000-0000-0000-000000000001"
USER_B_ID = "00000000-0000-0000-0000-000000000002"
JWT_TEST_SECRET = "super-secret-test-jwt-key-for-testpilot-ai-testing-32chars"


def create_token(user_id: str, email: str, expired: bool = False) -> str:
    now = int(time.time())
    exp = now - 3600 if expired else now + 3600
    payload = {
        "sub": user_id,
        "email": email,
        "role": "authenticated",
        "aud": "authenticated",
        "exp": exp,
    }
    return jwt.encode(payload, JWT_TEST_SECRET, algorithm="HS256")


@pytest.fixture
def mock_db():
    """Provides a fresh in-memory database with RLS simulation."""
    return MockSupabaseDB()


@pytest.fixture
def user_a_token():
    return create_token(USER_A_ID, "user_a@example.com")


@pytest.fixture
def user_b_token():
    return create_token(USER_B_ID, "user_b@example.com")


@pytest.fixture
def user_a_headers(user_a_token):
    return {"Authorization": f"Bearer {user_a_token}"}


@pytest.fixture
def user_b_headers(user_b_token):
    return {"Authorization": f"Bearer {user_b_token}"}


@pytest.fixture
def client(mock_db):
    """Provides TestClient with user-scoped mock Supabase database override."""
    def override_get_user_db(current_user: AuthenticatedUser = pytest.importorskip("fastapi").Depends(get_current_user)):
        return mock_db.get_client(str(current_user.id))

    app.dependency_overrides[get_user_db] = override_get_user_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
