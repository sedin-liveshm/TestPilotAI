import pytest

VALID_TEST_IR = {
    "version": "1",
    "id": "login-smoke",
    "name": "Login smoke test",
    "description": "Verifies login",
    "actions": [
        {"type": "navigate", "url": "/login"},
        {"type": "fill", "target": {"strategy": "label", "value": "Email"}, "value": "user@example.com"},
        {"type": "fill", "target": {"strategy": "placeholder", "value": "Password"}, "value": "secret"},
        {"type": "click", "target": {"strategy": "role", "role": "button", "name": "Login"}},
        {"type": "assertVisible", "target": {"strategy": "role", "role": "heading", "name": "Dashboard"}},
    ],
}


# ============================================================================
# TEST CRUD TESTS (Cases 11, 12, 13, 14)
# ============================================================================

def test_user_a_creates_test_under_project_a(client, user_a_headers):
    """Case 11: User A creates test under Project A -> PASS (201 Created)."""
    # Create Project A
    proj_resp = client.post(
        "/projects",
        json={"name": "Project A", "base_url": "https://a.example.com"},
        headers=user_a_headers,
    )
    project_id = proj_resp.json()["data"]["id"]

    # Create Test A
    test_payload = {
        "name": "Login smoke test",
        "description": "Verifies that the login page loads and asserts dashboard",
        "test_ir": VALID_TEST_IR,
    }
    response = client.post(f"/projects/{project_id}/tests", json=test_payload, headers=user_a_headers)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["name"] == "Login smoke test"
    assert data["project_id"] == project_id
    assert data["ir_version"] == 1
    assert data["test_ir"]["version"] == "1"
    assert len(data["test_ir"]["actions"]) == 5
    assert "id" in data


def test_user_a_reads_test_a(client, user_a_headers):
    """Case 12: User A reads Test A -> PASS (200 OK)."""
    # Setup project and test
    proj_resp = client.post(
        "/projects",
        json={"name": "Project A", "base_url": "https://a.example.com"},
        headers=user_a_headers,
    )
    project_id = proj_resp.json()["data"]["id"]

    create_resp = client.post(
        f"/projects/{project_id}/tests",
        json={"name": "Read Test", "test_ir": VALID_TEST_IR},
        headers=user_a_headers,
    )
    test_id = create_resp.json()["data"]["id"]

    # Fetch test details
    get_resp = client.get(f"/tests/{test_id}", headers=user_a_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["id"] == test_id
    assert get_resp.json()["data"]["name"] == "Read Test"

    # List tests under project
    list_resp = client.get(f"/projects/{project_id}/tests", headers=user_a_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()["data"]) == 1
    assert list_resp.json()["data"][0]["id"] == test_id


def test_user_a_updates_test_a(client, user_a_headers):
    """Case 13: User A updates Test A -> PASS (200 OK)."""
    proj_resp = client.post(
        "/projects",
        json={"name": "Project A", "base_url": "https://a.example.com"},
        headers=user_a_headers,
    )
    project_id = proj_resp.json()["data"]["id"]

    create_resp = client.post(
        f"/projects/{project_id}/tests",
        json={"name": "Original Test", "test_ir": VALID_TEST_IR},
        headers=user_a_headers,
    )
    test_id = create_resp.json()["data"]["id"]

    # Update title and IR
    updated_ir = dict(VALID_TEST_IR)
    updated_ir["name"] = "Updated Test Name"
    patch_resp = client.patch(
        f"/tests/{test_id}",
        json={"name": "Updated Test Name", "test_ir": updated_ir},
        headers=user_a_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["data"]["name"] == "Updated Test Name"
    assert patch_resp.json()["data"]["test_ir"]["name"] == "Updated Test Name"


def test_user_a_deletes_test_a(client, user_a_headers):
    """Case 14: User A deletes Test A -> PASS (204 No Content)."""
    proj_resp = client.post(
        "/projects",
        json={"name": "Project A", "base_url": "https://a.example.com"},
        headers=user_a_headers,
    )
    project_id = proj_resp.json()["data"]["id"]

    create_resp = client.post(
        f"/projects/{project_id}/tests",
        json={"name": "To Delete Test", "test_ir": VALID_TEST_IR},
        headers=user_a_headers,
    )
    test_id = create_resp.json()["data"]["id"]

    # Delete test
    del_resp = client.delete(f"/tests/{test_id}", headers=user_a_headers)
    assert del_resp.status_code == 204

    # Verify test is gone
    get_resp = client.get(f"/tests/{test_id}", headers=user_a_headers)
    assert get_resp.status_code == 404


# ============================================================================
# CROSS-USER TEST SECURITY TESTS (Cases 15, 16, 17, 18)
# ============================================================================

def test_user_a_attempts_read_test_b_denied(client, user_a_headers, user_b_headers):
    """Case 15: User A attempts to read Test B -> DENIED (404)."""
    # User B creates project & test
    b_proj = client.post(
        "/projects",
        json={"name": "Project B", "base_url": "https://b.example.com"},
        headers=user_b_headers,
    ).json()["data"]["id"]

    b_test = client.post(
        f"/projects/{b_proj}/tests",
        json={"name": "User B Secret Test", "test_ir": VALID_TEST_IR},
        headers=user_b_headers,
    ).json()["data"]["id"]

    # User A tries to read Test B
    a_resp = client.get(f"/tests/{b_test}", headers=user_a_headers)
    assert a_resp.status_code == 404
    assert a_resp.json()["error"]["message"] == "Test not found"

    # User A tries to list tests from User B's project
    a_list = client.get(f"/projects/{b_proj}/tests", headers=user_a_headers)
    assert a_list.status_code == 404


def test_user_a_attempts_update_test_b_denied(client, user_a_headers, user_b_headers):
    """Case 16: User A attempts to update Test B -> DENIED (404)."""
    b_proj = client.post(
        "/projects",
        json={"name": "Project B", "base_url": "https://b.example.com"},
        headers=user_b_headers,
    ).json()["data"]["id"]

    b_test = client.post(
        f"/projects/{b_proj}/tests",
        json={"name": "User B Test", "test_ir": VALID_TEST_IR},
        headers=user_b_headers,
    ).json()["data"]["id"]

    # User A tries to update Test B
    patch_resp = client.patch(
        f"/tests/{b_test}",
        json={"name": "Tampered Name"},
        headers=user_a_headers,
    )
    assert patch_resp.status_code == 404

    # Verify Test B was not altered
    verify_resp = client.get(f"/tests/{b_test}", headers=user_b_headers)
    assert verify_resp.json()["data"]["name"] == "User B Test"


def test_user_a_attempts_delete_test_b_denied(client, user_a_headers, user_b_headers):
    """Case 17: User A attempts to delete Test B -> DENIED (404)."""
    b_proj = client.post(
        "/projects",
        json={"name": "Project B", "base_url": "https://b.example.com"},
        headers=user_b_headers,
    ).json()["data"]["id"]

    b_test = client.post(
        f"/projects/{b_proj}/tests",
        json={"name": "User B Test", "test_ir": VALID_TEST_IR},
        headers=user_b_headers,
    ).json()["data"]["id"]

    # User A tries to delete Test B
    del_resp = client.delete(f"/tests/{b_test}", headers=user_a_headers)
    assert del_resp.status_code == 404

    # Verify Test B still exists for User B
    verify_resp = client.get(f"/tests/{b_test}", headers=user_b_headers)
    assert verify_resp.status_code == 200


def test_user_a_attempts_create_test_under_user_b_project_denied(client, user_a_headers, user_b_headers):
    """Case 18: User A attempts to create a test under User B's project -> DENIED (404)."""
    b_proj = client.post(
        "/projects",
        json={"name": "Project B", "base_url": "https://b.example.com"},
        headers=user_b_headers,
    ).json()["data"]["id"]

    # User A attempts to inject a test into Project B
    inject_resp = client.post(
        f"/projects/{b_proj}/tests",
        json={"name": "Injected Test", "test_ir": VALID_TEST_IR},
        headers=user_a_headers,
    )
    assert inject_resp.status_code == 404
    assert inject_resp.json()["error"]["message"] == "Project not found"

    # Verify Project B has no tests
    list_resp = client.get(f"/projects/{b_proj}/tests", headers=user_b_headers)
    assert len(list_resp.json()["data"]) == 0


# ============================================================================
# CANONICAL TEST IR VALIDATION TESTS
# ============================================================================

def test_test_ir_validation_rejects_missing_version(client, user_a_headers):
    """Reject Test IR without version."""
    proj = client.post(
        "/projects",
        json={"name": "P", "base_url": "https://p.com"},
        headers=user_a_headers,
    ).json()["data"]["id"]

    bad_ir = {
        "id": "bad-1",
        "name": "Bad",
        "actions": [{"type": "navigate", "url": "/"}],
    }
    res = client.post(f"/projects/{proj}/tests", json={"name": "Bad", "test_ir": bad_ir}, headers=user_a_headers)
    assert res.status_code == 422


def test_test_ir_validation_rejects_unsupported_version(client, user_a_headers):
    """Reject Test IR with version != '1'."""
    proj = client.post(
        "/projects",
        json={"name": "P", "base_url": "https://p.com"},
        headers=user_a_headers,
    ).json()["data"]["id"]

    bad_ir = {
        "version": "2",
        "id": "bad-2",
        "name": "Bad",
        "actions": [{"type": "navigate", "url": "/"}],
    }
    res = client.post(f"/projects/{proj}/tests", json={"name": "Bad", "test_ir": bad_ir}, headers=user_a_headers)
    assert res.status_code == 422


def test_test_ir_validation_rejects_empty_actions(client, user_a_headers):
    """Reject Test IR with empty actions list."""
    proj = client.post(
        "/projects",
        json={"name": "P", "base_url": "https://p.com"},
        headers=user_a_headers,
    ).json()["data"]["id"]

    bad_ir = {
        "version": "1",
        "id": "bad-3",
        "name": "Bad",
        "actions": [],
    }
    res = client.post(f"/projects/{proj}/tests", json={"name": "Bad", "test_ir": bad_ir}, headers=user_a_headers)
    assert res.status_code == 422


def test_test_ir_validation_rejects_xpath_locator(client, user_a_headers):
    """Reject Test IR with xpath locator strategy (ADR-001 forbids xpath)."""
    proj = client.post(
        "/projects",
        json={"name": "P", "base_url": "https://p.com"},
        headers=user_a_headers,
    ).json()["data"]["id"]

    bad_ir = {
        "version": "1",
        "id": "bad-xpath",
        "name": "Bad",
        "actions": [
            {"type": "click", "target": {"strategy": "xpath", "value": "//button"}},
        ],
    }
    res = client.post(f"/projects/{proj}/tests", json={"name": "Bad", "test_ir": bad_ir}, headers=user_a_headers)
    assert res.status_code == 422


def test_test_ir_validation_rejects_missing_action_field(client, user_a_headers):
    """Reject fill action missing 'value' field."""
    proj = client.post(
        "/projects",
        json={"name": "P", "base_url": "https://p.com"},
        headers=user_a_headers,
    ).json()["data"]["id"]

    bad_ir = {
        "version": "1",
        "id": "bad-fill",
        "name": "Bad",
        "actions": [
            {"type": "fill", "target": {"strategy": "label", "value": "Email"}},  # missing 'value'
        ],
    }
    res = client.post(f"/projects/{proj}/tests", json={"name": "Bad", "test_ir": bad_ir}, headers=user_a_headers)
    assert res.status_code == 422


def test_all_12_actions_and_6_locators_accepted(client, user_a_headers):
    """Verify that all 12 action types and 6 locator strategies pass validation."""
    proj = client.post(
        "/projects",
        json={"name": "Full Suite", "base_url": "https://suite.com"},
        headers=user_a_headers,
    ).json()["data"]["id"]

    comprehensive_ir = {
        "version": "1",
        "id": "all-actions-test",
        "name": "Comprehensive Test IR",
        "actions": [
            {"type": "navigate", "url": "/login"},
            {"type": "fill", "target": {"strategy": "label", "value": "Email"}, "value": "test@example.com"},
            {"type": "fill", "target": {"strategy": "placeholder", "value": "Password"}, "value": "pwd"},
            {"type": "click", "target": {"strategy": "role", "role": "button", "name": "Submit"}},
            {"type": "wait", "durationMs": 500},
            {"type": "assertText", "target": {"strategy": "testId", "value": "header-title"}, "text": "Dashboard"},
            {"type": "assertVisible", "target": {"strategy": "css", "value": ".user-profile"}},
            {"type": "assertUrl", "url": "/dashboard"},
            {"type": "screenshot", "name": "logged-in"},
            {"type": "check", "target": {"strategy": "text", "value": "Remember me"}},
            {"type": "uncheck", "target": {"strategy": "text", "value": "Subscribe"}},
            {"type": "select", "target": {"strategy": "label", "value": "Country"}, "value": "US"},
            {"type": "press", "target": {"strategy": "role", "role": "combobox"}, "key": "Enter"},
            {"type": "press", "key": "Escape"},
        ],
    }
    res = client.post(f"/projects/{proj}/tests", json={"name": "Comprehensive", "test_ir": comprehensive_ir}, headers=user_a_headers)
    assert res.status_code == 201
    assert len(res.json()["data"]["test_ir"]["actions"]) == 14
