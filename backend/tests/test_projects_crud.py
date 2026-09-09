import pytest
from tests.conftest import USER_A_ID, USER_B_ID, create_token


# ============================================================================
# AUTHENTICATION TESTS (Cases 1, 2, 3)
# ============================================================================

def test_unauthenticated_request_rejected(client):
    """Case 1: Unauthenticated request -> rejected with 401."""
    response = client.get("/projects")
    assert response.status_code == 401
    assert "error" in response.json()
    assert response.json()["error"]["code"] == "HTTP_401"


def test_invalid_authentication_rejected(client):
    """Case 2: Invalid authentication -> rejected with 401."""
    # Bad header format
    res1 = client.get("/projects", headers={"Authorization": "Basic 12345"})
    assert res1.status_code == 401

    # Malformed JWT
    res2 = client.get("/projects", headers={"Authorization": "Bearer not-a-valid-jwt"})
    assert res2.status_code == 401

    # Expired JWT
    expired_token = create_token(USER_A_ID, "user_a@example.com", expired=True)
    res3 = client.get("/projects", headers={"Authorization": f"Bearer {expired_token}"})
    assert res3.status_code == 401


def test_authenticated_request_accepted(client, user_a_headers):
    """Case 3: Authenticated request -> accepted with 200."""
    response = client.get("/projects", headers=user_a_headers)
    assert response.status_code == 200
    assert "data" in response.json()
    assert isinstance(response.json()["data"], list)


# ============================================================================
# PROJECT CRUD TESTS (Cases 4, 5, 6, 7)
# ============================================================================

def test_user_a_creates_project(client, user_a_headers):
    """Case 4: User A creates project -> PASS (201 Created)."""
    payload = {
        "name": "E-Commerce App",
        "description": "Store test suite",
        "base_url": "https://store.example.com",
    }
    response = client.post("/projects", json=payload, headers=user_a_headers)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["name"] == "E-Commerce App"
    assert data["base_url"] == "https://store.example.com"
    assert data["owner_id"] == USER_A_ID
    assert "id" in data
    assert "created_at" in data


def test_user_a_reads_project(client, user_a_headers):
    """Case 5: User A reads project -> PASS (200 OK)."""
    # Create project
    create_resp = client.post(
        "/projects",
        json={"name": "Read Test Project", "base_url": "https://read.example.com"},
        headers=user_a_headers,
    )
    project_id = create_resp.json()["data"]["id"]

    # Read project by ID
    get_resp = client.get(f"/projects/{project_id}", headers=user_a_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["id"] == project_id
    assert get_resp.json()["data"]["name"] == "Read Test Project"


def test_user_a_updates_project(client, user_a_headers):
    """Case 6: User A updates project -> PASS (200 OK)."""
    create_resp = client.post(
        "/projects",
        json={"name": "Old Project Name", "base_url": "https://old.example.com"},
        headers=user_a_headers,
    )
    project_id = create_resp.json()["data"]["id"]

    # Update project
    patch_resp = client.patch(
        f"/projects/{project_id}",
        json={"name": "New Project Name", "description": "Updated description"},
        headers=user_a_headers,
    )
    assert patch_resp.status_code == 200
    updated_data = patch_resp.json()["data"]
    assert updated_data["name"] == "New Project Name"
    assert updated_data["description"] == "Updated description"
    assert updated_data["base_url"] == "https://old.example.com"


def test_user_a_deletes_project(client, user_a_headers):
    """Case 7: User A deletes project -> PASS (204 No Content)."""
    create_resp = client.post(
        "/projects",
        json={"name": "To Delete", "base_url": "https://del.example.com"},
        headers=user_a_headers,
    )
    project_id = create_resp.json()["data"]["id"]

    # Delete project
    del_resp = client.delete(f"/projects/{project_id}", headers=user_a_headers)
    assert del_resp.status_code == 204

    # Verify project is gone
    get_resp = client.get(f"/projects/{project_id}", headers=user_a_headers)
    assert get_resp.status_code == 404


# ============================================================================
# OWNERSHIP & ISOLATION TESTS (Cases 8, 9, 10)
# ============================================================================

def test_user_a_attempts_read_user_b_project_denied(client, user_a_headers, user_b_headers):
    """Case 8: User A attempts to read User B's project -> DENIED (404)."""
    # User B creates project
    b_resp = client.post(
        "/projects",
        json={"name": "User B Secret Project", "base_url": "https://b.example.com"},
        headers=user_b_headers,
    )
    b_project_id = b_resp.json()["data"]["id"]

    # User A tries to read User B's project
    a_read_resp = client.get(f"/projects/{b_project_id}", headers=user_a_headers)
    assert a_read_resp.status_code == 404
    assert a_read_resp.json()["error"]["message"] == "Project not found"

    # User A lists projects -> User B's project must not appear
    a_list_resp = client.get("/projects", headers=user_a_headers)
    assert a_list_resp.status_code == 200
    a_projects = a_list_resp.json()["data"]
    assert not any(p["id"] == b_project_id for p in a_projects)


def test_user_a_attempts_update_user_b_project_denied(client, user_a_headers, user_b_headers):
    """Case 9: User A attempts to update User B's project -> DENIED (404)."""
    # User B creates project
    b_resp = client.post(
        "/projects",
        json={"name": "User B Project", "base_url": "https://b.example.com"},
        headers=user_b_headers,
    )
    b_project_id = b_resp.json()["data"]["id"]

    # User A tries to update User B's project
    patch_resp = client.patch(
        f"/projects/{b_project_id}",
        json={"name": "Hacked by User A"},
        headers=user_a_headers,
    )
    assert patch_resp.status_code == 404

    # Verify project name was NOT changed
    b_verify = client.get(f"/projects/{b_project_id}", headers=user_b_headers)
    assert b_verify.json()["data"]["name"] == "User B Project"


def test_user_a_attempts_delete_user_b_project_denied(client, user_a_headers, user_b_headers):
    """Case 10: User A attempts to delete User B's project -> DENIED (404)."""
    # User B creates project
    b_resp = client.post(
        "/projects",
        json={"name": "User B Project", "base_url": "https://b.example.com"},
        headers=user_b_headers,
    )
    b_project_id = b_resp.json()["data"]["id"]

    # User A tries to delete User B's project
    del_resp = client.delete(f"/projects/{b_project_id}", headers=user_a_headers)
    assert del_resp.status_code == 404

    # Verify project still exists for User B
    b_verify = client.get(f"/projects/{b_project_id}", headers=user_b_headers)
    assert b_verify.status_code == 200


# ============================================================================
# OWNER SPOOFING TEST (Case 19)
# ============================================================================

def test_user_a_attempts_owner_spoofing_prevented(client, user_a_headers):
    """Case 19: User A creates project providing User B's owner_id -> owner remains User A."""
    payload = {
        "name": "Spoofed Project",
        "base_url": "https://spoof.example.com",
        "owner_id": USER_B_ID,  # Attempting to assign project to User B
    }
    response = client.post("/projects", json=payload, headers=user_a_headers)
    assert response.status_code == 201
    data = response.json()["data"]
    # Enforced: owner_id MUST remain User A!
    assert data["owner_id"] == USER_A_ID
    assert data["owner_id"] != USER_B_ID


# ============================================================================
# PAGINATION & SEARCH FILTERING
# ============================================================================

def test_project_pagination_and_search(client, user_a_headers):
    """Verify page, page_size, and search parameters on GET /projects."""
    # Create 3 projects
    for i in range(3):
        client.post(
            "/projects",
            json={"name": f"App {i}", "base_url": f"https://app{i}.example.com"},
            headers=user_a_headers,
        )

    # Page 1, size 2
    res = client.get("/projects?page=1&page_size=2", headers=user_a_headers)
    assert res.status_code == 200
    body = res.json()
    assert len(body["data"]) == 2
    assert body["meta"]["page"] == 1
    assert body["meta"]["page_size"] == 2
    assert body["meta"]["total"] >= 3

    # Search filter
    search_res = client.get("/projects?search=App 1", headers=user_a_headers)
    assert search_res.status_code == 200
    search_body = search_res.json()
    assert len(search_body["data"]) == 1
    assert search_body["data"][0]["name"] == "App 1"


def test_api_v1_route_prefix_compatibility(client, user_a_headers):
    """Verify endpoints also resolve with /api/v1 prefix for frontend api-client."""
    res = client.get("/api/v1/projects", headers=user_a_headers)
    assert res.status_code == 200
    assert "data" in res.json()
