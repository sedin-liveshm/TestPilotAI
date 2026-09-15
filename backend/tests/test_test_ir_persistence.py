import copy
import json
import pytest
from fastapi.testclient import TestClient

from app.schemas.test_ir import TestIR


# ============================================================================
# CANONICAL TEST IR FIXTURES (Dev 2 Contract)
# ============================================================================

SAMPLE_LOGIN_IR = {
    "version": "1",
    "id": "login-smoke",
    "name": "Login smoke test",
    "description": "Verifies that the login page loads and basic assertions pass",
    "actions": [
        {"type": "navigate", "url": "/login"},
        {
            "type": "fill",
            "target": {"strategy": "label", "value": "Email"},
            "value": "user@example.com",
        },
        {
            "type": "fill",
            "target": {"strategy": "placeholder", "value": "Password"},
            "value": "securepassword123",
        },
        {
            "type": "click",
            "target": {"strategy": "role", "role": "button", "name": "Login"},
        },
        {
            "type": "assertVisible",
            "target": {"strategy": "role", "role": "heading", "name": "Dashboard"},
        },
        {"type": "assertUrl", "url": "/dashboard"},
    ],
}

COMPREHENSIVE_IR = {
    "version": "1",
    "id": "comprehensive-suite",
    "name": "Comprehensive Test IR Suite",
    "description": "Exercises all 12 actions and all 6 locator strategies",
    "actions": [
        {"type": "navigate", "url": "/app"},
        {"type": "fill", "target": {"strategy": "label", "value": "Username"}, "value": "tester"},
        {"type": "fill", "target": {"strategy": "placeholder", "value": "Code"}, "value": "1234"},
        {"type": "click", "target": {"strategy": "role", "role": "button", "name": "Proceed"}},
        {"type": "check", "target": {"strategy": "text", "value": "Agree to Terms"}},
        {"type": "uncheck", "target": {"strategy": "text", "value": "Opt In"}},
        {"type": "select", "target": {"strategy": "label", "value": "Country"}, "value": "US"},
        {"type": "wait", "durationMs": 500},
        {"type": "press", "target": {"strategy": "role", "role": "combobox"}, "key": "Enter"},
        {"type": "press", "key": "Escape"},
        {"type": "assertText", "target": {"strategy": "testId", "value": "status-msg"}, "text": "Active"},
        {"type": "assertVisible", "target": {"strategy": "css", "value": ".dashboard-container"}},
        {"type": "assertUrl", "url": "/app/dashboard"},
        {"type": "screenshot", "name": "dashboard-view"},
        {"type": "screenshot"},
    ],
}


# ============================================================================
# PHASE 10: ROUND-TRIP PERSISTENCE TESTS (The Most Important Test)
# ============================================================================

def test_test_ir_round_trip_equality_standard(client: TestClient, user_a_headers):
    """Phase 10: IR_original survives Supabase round-trip without semantic changes."""
    # 1. Validate IR_original against canonical schema
    validated_original = TestIR.model_validate(SAMPLE_LOGIN_IR)
    ir_original = validated_original.model_dump(mode="json", exclude_none=True)

    # 2. Setup project
    proj_resp = client.post(
        "/projects",
        json={"name": "Persistence Project", "base_url": "https://test.com"},
        headers=user_a_headers,
    )
    assert proj_resp.status_code == 201
    project_id = proj_resp.json()["data"]["id"]

    # 3. Create test through backend
    create_payload = {
        "name": "Round Trip Test",
        "description": "Verifies lossless persistence",
        "test_ir": ir_original,
    }
    create_resp = client.post(
        f"/projects/{project_id}/tests",
        json=create_payload,
        headers=user_a_headers,
    )
    assert create_resp.status_code == 201
    created_data = create_resp.json()["data"]
    test_id = created_data["id"]

    # 4. Read the test back
    get_resp = client.get(f"/tests/{test_id}", headers=user_a_headers)
    assert get_resp.status_code == 200
    ir_loaded = get_resp.json()["data"]["test_ir"]

    # 5. Validate the loaded IR
    validated_loaded = TestIR.model_validate(ir_loaded)
    ir_loaded_dump = validated_loaded.model_dump(mode="json", exclude_none=True)

    # 6. Compare semantic equality: IR_original == IR_loaded
    assert ir_loaded == ir_original
    assert ir_loaded_dump == ir_original
    assert get_resp.json()["data"]["ir_version"] == 1


def test_test_ir_round_trip_equality_comprehensive(client: TestClient, user_a_headers):
    """Phase 10: Round-trip with all 12 action types and all 6 locator strategies."""
    validated_original = TestIR.model_validate(COMPREHENSIVE_IR)
    ir_original = validated_original.model_dump(mode="json", exclude_none=True)

    proj_resp = client.post(
        "/projects",
        json={"name": "Comprehensive Suite Project", "base_url": "https://suite.com"},
        headers=user_a_headers,
    )
    project_id = proj_resp.json()["data"]["id"]

    create_resp = client.post(
        f"/projects/{project_id}/tests",
        json={"name": "All Actions & Locators", "test_ir": ir_original},
        headers=user_a_headers,
    )
    assert create_resp.status_code == 201
    test_id = create_resp.json()["data"]["id"]

    get_resp = client.get(f"/tests/{test_id}", headers=user_a_headers)
    assert get_resp.status_code == 200
    ir_loaded = get_resp.json()["data"]["test_ir"]

    # Semantic equality check
    assert ir_loaded == ir_original
    assert len(ir_loaded["actions"]) == 15
    assert ir_loaded["version"] == "1"


def test_test_ir_round_trip_minimal_without_optional_fields(client: TestClient, user_a_headers):
    """Phase 10: Round-trip with minimal Test IR (omitting description and optional action fields)."""
    minimal_ir = {
        "version": "1",
        "id": "minimal-test",
        "name": "Minimal",
        "actions": [
            {"type": "navigate", "url": "/"},
            {"type": "screenshot"},
            {"type": "press", "key": "Tab"},
        ],
    }
    validated_original = TestIR.model_validate(minimal_ir)
    ir_original = validated_original.model_dump(mode="json", exclude_none=True)

    proj_resp = client.post(
        "/projects",
        json={"name": "Minimal Project", "base_url": "https://min.com"},
        headers=user_a_headers,
    )
    project_id = proj_resp.json()["data"]["id"]

    create_resp = client.post(
        f"/projects/{project_id}/tests",
        json={"name": "Minimal", "test_ir": ir_original},
        headers=user_a_headers,
    )
    assert create_resp.status_code == 201
    test_id = create_resp.json()["data"]["id"]

    get_resp = client.get(f"/tests/{test_id}", headers=user_a_headers)
    assert get_resp.status_code == 200
    ir_loaded = get_resp.json()["data"]["test_ir"]

    # Ensure no synthetic 'null' fields were injected
    assert "description" not in ir_loaded
    assert "name" not in ir_loaded["actions"][1]
    assert "target" not in ir_loaded["actions"][2]
    assert ir_loaded == ir_original


# ============================================================================
# PHASE 11: INVALID IR TESTS (Write Validation)
# ============================================================================

def test_invalid_ir_missing_required_fields(client: TestClient, user_a_headers):
    """Phase 11: Missing required fields (version, id, name, actions) are rejected."""
    proj_resp = client.post(
        "/projects",
        json={"name": "Validation Project", "base_url": "https://v.com"},
        headers=user_a_headers,
    )
    project_id = proj_resp.json()["data"]["id"]

    # Missing 'version'
    bad_no_version = {
        "id": "bad-1",
        "name": "No Version",
        "actions": [{"type": "navigate", "url": "/"}],
    }
    res = client.post(
        f"/projects/{project_id}/tests",
        json={"name": "Bad", "test_ir": bad_no_version},
        headers=user_a_headers,
    )
    assert res.status_code == 422

    # Missing 'id'
    bad_no_id = {
        "version": "1",
        "name": "No ID",
        "actions": [{"type": "navigate", "url": "/"}],
    }
    res = client.post(
        f"/projects/{project_id}/tests",
        json={"name": "Bad", "test_ir": bad_no_id},
        headers=user_a_headers,
    )
    assert res.status_code == 422

    # Missing 'name'
    bad_no_name = {
        "version": "1",
        "id": "no-name",
        "actions": [{"type": "navigate", "url": "/"}],
    }
    res = client.post(
        f"/projects/{project_id}/tests",
        json={"name": "Bad", "test_ir": bad_no_name},
        headers=user_a_headers,
    )
    assert res.status_code == 422

    # Missing 'actions'
    bad_no_actions = {
        "version": "1",
        "id": "no-actions",
        "name": "No Actions",
    }
    res = client.post(
        f"/projects/{project_id}/tests",
        json={"name": "Bad", "test_ir": bad_no_actions},
        headers=user_a_headers,
    )
    assert res.status_code == 422

    # Empty 'actions' array
    bad_empty_actions = {
        "version": "1",
        "id": "empty-actions",
        "name": "Empty Actions",
        "actions": [],
    }
    res = client.post(
        f"/projects/{project_id}/tests",
        json={"name": "Bad", "test_ir": bad_empty_actions},
        headers=user_a_headers,
    )
    assert res.status_code == 422


def test_invalid_ir_invalid_action_type(client: TestClient, user_a_headers):
    """Phase 11: Unknown action type is rejected."""
    proj = client.post(
        "/projects",
        json={"name": "V", "base_url": "https://v.com"},
        headers=user_a_headers,
    ).json()["data"]["id"]

    bad_ir = {
        "version": "1",
        "id": "unknown-act",
        "name": "Unknown Action",
        "actions": [{"type": "hover_and_swipe"}],
    }
    res = client.post(f"/projects/{proj}/tests", json={"name": "Bad", "test_ir": bad_ir}, headers=user_a_headers)
    assert res.status_code == 422


def test_invalid_ir_unsupported_locator_strategy(client: TestClient, user_a_headers):
    """Phase 11: Unsupported locator strategy (e.g. xpath) is rejected per ADR-001."""
    proj = client.post(
        "/projects",
        json={"name": "V", "base_url": "https://v.com"},
        headers=user_a_headers,
    ).json()["data"]["id"]

    bad_ir = {
        "version": "1",
        "id": "xpath-act",
        "name": "XPath Action",
        "actions": [{"type": "click", "target": {"strategy": "xpath", "value": "//button"}}],
    }
    res = client.post(f"/projects/{proj}/tests", json={"name": "Bad", "test_ir": bad_ir}, headers=user_a_headers)
    assert res.status_code == 422


def test_invalid_ir_wrong_field_types(client: TestClient, user_a_headers):
    """Phase 11: Wrong field data types (e.g. string durationMs, non-positive duration)."""
    proj = client.post(
        "/projects",
        json={"name": "V", "base_url": "https://v.com"},
        headers=user_a_headers,
    ).json()["data"]["id"]

    # String durationMs
    bad_type = {
        "version": "1",
        "id": "bad-type",
        "name": "Bad Type",
        "actions": [{"type": "wait", "durationMs": "1000"}],
    }
    res = client.post(f"/projects/{proj}/tests", json={"name": "Bad", "test_ir": bad_type}, headers=user_a_headers)
    assert res.status_code == 422

    # Negative durationMs
    bad_negative = {
        "version": "1",
        "id": "bad-neg",
        "name": "Bad Negative",
        "actions": [{"type": "wait", "durationMs": -500}],
    }
    res = client.post(f"/projects/{proj}/tests", json={"name": "Bad", "test_ir": bad_negative}, headers=user_a_headers)
    assert res.status_code == 422


def test_invalid_ir_malformed_nested_structure(client: TestClient, user_a_headers):
    """Phase 11: Malformed nested structure (fill missing value, role missing role)."""
    proj = client.post(
        "/projects",
        json={"name": "V", "base_url": "https://v.com"},
        headers=user_a_headers,
    ).json()["data"]["id"]

    # fill missing 'value'
    bad_fill = {
        "version": "1",
        "id": "bad-fill",
        "name": "Bad Fill",
        "actions": [{"type": "fill", "target": {"strategy": "label", "value": "Name"}}],
    }
    res = client.post(f"/projects/{proj}/tests", json={"name": "Bad", "test_ir": bad_fill}, headers=user_a_headers)
    assert res.status_code == 422

    # role locator missing 'role'
    bad_role = {
        "version": "1",
        "id": "bad-role",
        "name": "Bad Role",
        "actions": [{"type": "click", "target": {"strategy": "role", "name": "Login"}}],
    }
    res = client.post(f"/projects/{proj}/tests", json={"name": "Bad", "test_ir": bad_role}, headers=user_a_headers)
    assert res.status_code == 422


def test_invalid_ir_unsupported_version(client: TestClient, user_a_headers):
    """Phase 11: Unsupported versions (e.g. '2', 'v1.0') are rejected."""
    proj = client.post(
        "/projects",
        json={"name": "V", "base_url": "https://v.com"},
        headers=user_a_headers,
    ).json()["data"]["id"]

    for unsupported in ["2", "v1.0", "1.0", "0.1"]:
        bad_ver = {
            "version": unsupported,
            "id": "bad-ver",
            "name": "Bad Version",
            "actions": [{"type": "navigate", "url": "/"}],
        }
        res = client.post(f"/projects/{proj}/tests", json={"name": "Bad", "test_ir": bad_ver}, headers=user_a_headers)
        assert res.status_code == 422, f"Expected 422 for unsupported version '{unsupported}'"


def test_invalid_ir_not_persisted_in_database(client: TestClient, user_a_headers):
    """Phase 11: When write validation fails, no test record is inserted into DB."""
    proj = client.post(
        "/projects",
        json={"name": "Clean Project", "base_url": "https://clean.com"},
        headers=user_a_headers,
    ).json()["data"]["id"]

    # Attempt to insert invalid IR
    res = client.post(
        f"/projects/{proj}/tests",
        json={"name": "Invalid", "test_ir": {"version": "99"}},
        headers=user_a_headers,
    )
    assert res.status_code == 422

    # Verify project tests list is completely empty
    list_res = client.get(f"/projects/{proj}/tests", headers=user_a_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) == 0


# ============================================================================
# PHASE 12: UPDATE TESTS
# ============================================================================

def test_test_ir_update_flow(client: TestClient, user_a_headers):
    """Phase 12: Valid IR v1 -> Create -> Update with another valid IR v1 -> Read -> Verify."""
    proj = client.post(
        "/projects",
        json={"name": "Update Flow Proj", "base_url": "https://flow.com"},
        headers=user_a_headers,
    ).json()["data"]["id"]

    # 1. Create with initial valid IR
    create_resp = client.post(
        f"/projects/{proj}/tests",
        json={"name": "Initial Test", "test_ir": SAMPLE_LOGIN_IR},
        headers=user_a_headers,
    )
    assert create_resp.status_code == 201
    test_id = create_resp.json()["data"]["id"]

    # 2. Update with second valid IR (Comprehensive)
    patch_resp = client.patch(
        f"/tests/{test_id}",
        json={"name": "Updated Test", "test_ir": COMPREHENSIVE_IR},
        headers=user_a_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["data"]["name"] == "Updated Test"
    assert patch_resp.json()["data"]["test_ir"]["id"] == COMPREHENSIVE_IR["id"]

    # 3. Read back and verify exact equality with updated IR
    get_resp = client.get(f"/tests/{test_id}", headers=user_a_headers)
    assert get_resp.status_code == 200
    ir_loaded = get_resp.json()["data"]["test_ir"]
    assert ir_loaded == COMPREHENSIVE_IR


def test_test_ir_update_rejected_preserves_previous_valid_ir(client: TestClient, user_a_headers):
    """Phase 12: Attempt invalid update -> Rejected -> Previous valid IR remains unchanged."""
    proj = client.post(
        "/projects",
        json={"name": "Preserve Proj", "base_url": "https://p.com"},
        headers=user_a_headers,
    ).json()["data"]["id"]

    create_resp = client.post(
        f"/projects/{proj}/tests",
        json={"name": "Original", "test_ir": SAMPLE_LOGIN_IR},
        headers=user_a_headers,
    )
    test_id = create_resp.json()["data"]["id"]

    # Attempt update with invalid IR (version: "2")
    bad_update = dict(SAMPLE_LOGIN_IR)
    bad_update["version"] = "2"
    patch_resp = client.patch(
        f"/tests/{test_id}",
        json={"test_ir": bad_update},
        headers=user_a_headers,
    )
    assert patch_resp.status_code == 422

    # Verify previous valid IR is untouched
    get_resp = client.get(f"/tests/{test_id}", headers=user_a_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["test_ir"] == SAMPLE_LOGIN_IR


# ============================================================================
# PHASE 5 & 6: VALIDATION ON READ & VERSION INTEGRITY
# ============================================================================

def test_validation_on_read_rejects_corrupted_ir(client: TestClient, mock_db, user_a_headers):
    """Phase 5: Corrupted stored IR is rejected on read (500) without mutating data."""
    proj = client.post(
        "/projects",
        json={"name": "Corrupt Proj", "base_url": "https://corrupt.com"},
        headers=user_a_headers,
    ).json()["data"]["id"]

    create_resp = client.post(
        f"/projects/{proj}/tests",
        json={"name": "Valid First", "test_ir": SAMPLE_LOGIN_IR},
        headers=user_a_headers,
    )
    test_id = create_resp.json()["data"]["id"]

    # Directly corrupt the database row behind the scenes
    mock_db.tests[test_id]["test_ir"] = {"corrupted": True, "no_version": True}

    # Reading the test must trigger read validation and fail cleanly
    get_resp = client.get(f"/tests/{test_id}", headers=user_a_headers)
    assert get_resp.status_code == 500
    assert "Stored Test IR failed validation" in get_resp.json()["error"]["message"]

    # Verify database state was NOT mutated or silently transformed
    assert mock_db.tests[test_id]["test_ir"] == {"corrupted": True, "no_version": True}


def test_validation_on_read_rejects_unsupported_ir_version(client: TestClient, mock_db, user_a_headers):
    """Phase 5 & 6: Unsupported ir_version in DB is rejected on read."""
    proj = client.post(
        "/projects",
        json={"name": "Version Proj", "base_url": "https://ver.com"},
        headers=user_a_headers,
    ).json()["data"]["id"]

    create_resp = client.post(
        f"/projects/{proj}/tests",
        json={"name": "Valid Test", "test_ir": SAMPLE_LOGIN_IR},
        headers=user_a_headers,
    )
    test_id = create_resp.json()["data"]["id"]

    # Tamper with the ir_version in DB to simulate an unsupported version
    mock_db.tests[test_id]["ir_version"] = 2

    # Read must fail with version error
    get_resp = client.get(f"/tests/{test_id}", headers=user_a_headers)
    assert get_resp.status_code == 500
    assert "unsupported version" in get_resp.json()["error"]["message"]


# ============================================================================
# PHASE 13: MULTI-TENANT OWNERSHIP & ISOLATION
# ============================================================================

def test_user_ownership_and_cross_user_isolation(client: TestClient, user_a_headers, user_b_headers):
    """Phase 13: User A and User B remain completely isolated."""
    # User B creates a project and test
    b_proj = client.post(
        "/projects",
        json={"name": "User B Project", "base_url": "https://b.com"},
        headers=user_b_headers,
    ).json()["data"]["id"]

    b_test = client.post(
        f"/projects/{b_proj}/tests",
        json={"name": "User B Private Test", "test_ir": SAMPLE_LOGIN_IR},
        headers=user_b_headers,
    ).json()["data"]["id"]

    # 1. User A cannot read User B's Test IR
    a_get = client.get(f"/tests/{b_test}", headers=user_a_headers)
    assert a_get.status_code == 404

    # 2. User A cannot update User B's Test IR
    a_patch = client.patch(
        f"/tests/{b_test}",
        json={"name": "Hacked", "test_ir": COMPREHENSIVE_IR},
        headers=user_a_headers,
    )
    assert a_patch.status_code == 404

    # 3. User A cannot delete User B's test
    a_del = client.delete(f"/tests/{b_test}", headers=user_a_headers)
    assert a_del.status_code == 404

    # 4. User A cannot create a test inside User B's project
    a_create = client.post(
        f"/projects/{b_proj}/tests",
        json={"name": "Injected", "test_ir": SAMPLE_LOGIN_IR},
        headers=user_a_headers,
    )
    assert a_create.status_code == 404

    # 5. User B's test remains intact and undisturbed
    b_verify = client.get(f"/tests/{b_test}", headers=user_b_headers)
    assert b_verify.status_code == 200
    assert b_verify.json()["data"]["name"] == "User B Private Test"
    assert b_verify.json()["data"]["test_ir"] == SAMPLE_LOGIN_IR
