"""Test IR v1.0 Pydantic Schema Validation & Serializer Unit Tests.

Verifies:
- Complete parity with Day 2 Test IR v1 contract (automation/src/ir/schema.ts)
- Acceptance of all 12 supported actions and 6 locator strategies
- Strict rejection of invalid action types (especially unknown actions)
- Strict rejection of malformed or missing fields and forbidden extra fields
- Accurate serialization to JSON-compatible data suitable for database persistence
- Full roundtrip validation: JSON/dict -> validate -> serialize -> validate -> PASS
"""

import json
from pathlib import Path
from typing import Any, Dict

import pytest
from pydantic import ValidationError

from app.schemas.test_ir import (
    AssertTextAction,
    AssertUrlAction,
    AssertVisibleAction,
    CheckAction,
    ClickAction,
    CssLocator,
    FillAction,
    LabelLocator,
    LocatorTarget,
    NavigateAction,
    PlaceholderLocator,
    PressAction,
    RoleLocator,
    ScreenshotAction,
    SelectAction,
    TestAction,
    TestIdLocator,
    TestIR,
    TextLocator,
    UncheckAction,
    WaitAction,
    serialize_test_ir,
    validate_test_ir,
)


# ============================================================================
# TEST FIXTURES & SAMPLES
# ============================================================================

MINIMAL_VALID_IR: Dict[str, Any] = {
    "version": "1",
    "id": "minimal-test-1",
    "name": "Minimal Test",
    "actions": [
        {"type": "navigate", "url": "/home"},
    ],
}

ALL_ACTIONS_IR: Dict[str, Any] = {
    "version": "1",
    "id": "all-actions-test-suite",
    "name": "Comprehensive Test Suite",
    "description": "Exercises all 12 action types and 6 locator strategies",
    "actions": [
        {"type": "navigate", "url": "/login"},
        {"type": "fill", "target": {"strategy": "label", "value": "Email"}, "value": "user@example.com"},
        {"type": "fill", "target": {"strategy": "placeholder", "value": "Password"}, "value": "secret"},
        {"type": "click", "target": {"strategy": "role", "role": "button", "name": "Login"}},
        {"type": "wait", "durationMs": 1000},
        {"type": "assertText", "target": {"strategy": "testId", "value": "welcome-heading"}, "text": "Welcome back"},
        {"type": "assertVisible", "target": {"strategy": "css", "value": ".user-avatar"}},
        {"type": "assertUrl", "url": "/dashboard"},
        {"type": "screenshot", "name": "dashboard-view"},
        {"type": "check", "target": {"strategy": "text", "value": "Remember me"}},
        {"type": "uncheck", "target": {"strategy": "text", "value": "Subscribe"}},
        {"type": "select", "target": {"strategy": "label", "value": "Country"}, "value": "US"},
        {"type": "press", "target": {"strategy": "role", "role": "combobox"}, "key": "Enter"},
        {"type": "press", "key": "Escape"},
    ],
}


# ============================================================================
# 1. VALID TEST IR TESTS
# ============================================================================

class TestValidTestIR:
    """Tests verifying that all valid Test IR structures pass validation."""

    def test_minimal_valid_test_ir(self):
        """Minimal valid Test IR with 1 action passes validation."""
        test_ir = TestIR.model_validate(MINIMAL_VALID_IR)
        assert test_ir.version == "1"
        assert test_ir.id == "minimal-test-1"
        assert test_ir.name == "Minimal Test"
        assert test_ir.description is None
        assert len(test_ir.actions) == 1
        assert isinstance(test_ir.actions[0], NavigateAction)
        assert test_ir.actions[0].url == "/home"

    def test_all_12_actions_and_6_locators(self):
        """Test IR containing all 12 action types and all 6 locator strategies passes."""
        test_ir = TestIR.model_validate(ALL_ACTIONS_IR)
        assert test_ir.version == "1"
        assert test_ir.id == "all-actions-test-suite"
        assert test_ir.description == "Exercises all 12 action types and 6 locator strategies"
        assert len(test_ir.actions) == 14

    def test_individual_actions(self):
        """Verify each of the 12 action models individually."""
        # 1. navigate
        a1 = NavigateAction(type="navigate", url="https://example.com")
        assert a1.type == "navigate" and a1.url == "https://example.com"

        # 2. click
        a2 = ClickAction(type="click", target=RoleLocator(strategy="role", role="button"))
        assert a2.type == "click" and a2.target.strategy == "role"

        # 3. fill
        a3 = FillAction(type="fill", target=LabelLocator(strategy="label", value="Username"), value="swetha")
        assert a3.type == "fill" and a3.value == "swetha"

        # 4. select
        a4 = SelectAction(type="select", target=TextLocator(strategy="text", value="Pick"), value="opt1")
        assert a4.type == "select" and a4.value == "opt1"

        # 5. check
        a5 = CheckAction(type="check", target=TestIdLocator(strategy="testId", value="chk1"))
        assert a5.type == "check"

        # 6. uncheck
        a6 = UncheckAction(type="uncheck", target=TestIdLocator(strategy="testId", value="chk1"))
        assert a6.type == "uncheck"

        # 7. press (with and without target)
        a7a = PressAction(type="press", target=CssLocator(strategy="css", value="#search"), key="Enter")
        a7b = PressAction(type="press", key="Escape")
        assert a7a.target is not None and a7b.target is None
        assert a7b.key == "Escape"

        # 8. wait (int and float)
        a8a = WaitAction(type="wait", durationMs=500)
        a8b = WaitAction(type="wait", durationMs=125.5)
        assert a8a.durationMs == 500
        assert a8b.durationMs == 125.5

        # 9. assertText
        a9 = AssertTextAction(type="assertText", target=CssLocator(strategy="css", value="h1"), text="Heading")
        assert a9.type == "assertText" and a9.text == "Heading"

        # 10. assertVisible
        a10 = AssertVisibleAction(type="assertVisible", target=PlaceholderLocator(strategy="placeholder", value="Search"))
        assert a10.type == "assertVisible"

        # 11. assertUrl
        a11 = AssertUrlAction(type="assertUrl", url="/dashboard")
        assert a11.type == "assertUrl" and a11.url == "/dashboard"

        # 12. screenshot (with and without name)
        a12a = ScreenshotAction(type="screenshot", name="snap1")
        a12b = ScreenshotAction(type="screenshot")
        assert a12a.name == "snap1" and a12b.name is None

    def test_individual_locator_strategies(self):
        """Verify each of the 6 locator models individually."""
        # 1. role (with name and without name)
        l1a = RoleLocator(strategy="role", role="button", name="Submit")
        l1b = RoleLocator(strategy="role", role="link")
        assert l1a.strategy == "role" and l1a.role == "button" and l1a.name == "Submit"
        assert l1b.name is None

        # 2. text
        l2 = TextLocator(strategy="text", value="Click here")
        assert l2.strategy == "text" and l2.value == "Click here"

        # 3. label
        l3 = LabelLocator(strategy="label", value="Email Address")
        assert l3.strategy == "label" and l3.value == "Email Address"

        # 4. placeholder
        l4 = PlaceholderLocator(strategy="placeholder", value="Search items...")
        assert l4.strategy == "placeholder" and l4.value == "Search items..."

        # 5. testId
        l5 = TestIdLocator(strategy="testId", value="submit-btn")
        assert l5.strategy == "testId" and l5.value == "submit-btn"

        # 6. css
        l6 = CssLocator(strategy="css", value="div.container > button.primary")
        assert l6.strategy == "css" and l6.value == "div.container > button.primary"

    def test_load_canonical_fixture_login_smoke(self):
        """Verify automation/examples/test-ir/login-smoke.json validates successfully."""
        fixture_path = Path(__file__).resolve().parent.parent.parent / "automation" / "examples" / "test-ir" / "login-smoke.json"
        if not fixture_path.exists():
            pytest.skip(f"Fixture not found at {fixture_path}")

        with open(fixture_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        test_ir = validate_test_ir(raw_data)
        assert test_ir.version == "1"
        assert test_ir.id == "login-smoke"
        assert test_ir.name == "Login smoke test"
        assert len(test_ir.actions) == 6


# ============================================================================
# 2. INVALID TEST IR TESTS (Error & Schema Rejection)
# ============================================================================

class TestInvalidTestIR:
    """Tests verifying that all invalid Test IR structures are strictly rejected."""

    def test_reject_missing_version(self):
        """Missing version must fail validation."""
        data = {"id": "t1", "name": "N", "actions": [{"type": "navigate", "url": "/"}]}
        with pytest.raises(ValidationError) as exc:
            validate_test_ir(data)
        assert "version" in str(exc.value)

    def test_reject_unsupported_version_string(self):
        """Version other than '1' must be rejected."""
        for bad_version in ["2", "0", "v1", "1.0", ""]:
            data = {"version": bad_version, "id": "t1", "name": "N", "actions": [{"type": "navigate", "url": "/"}]}
            with pytest.raises(ValidationError):
                validate_test_ir(data)

    def test_reject_unsupported_version_type(self):
        """Non-string version (e.g. integer 1) must be rejected."""
        data = {"version": 1, "id": "t1", "name": "N", "actions": [{"type": "navigate", "url": "/"}]}
        with pytest.raises(ValidationError):
            validate_test_ir(data)

    def test_reject_missing_id(self):
        """Missing ID must fail validation."""
        data = {"version": "1", "name": "N", "actions": [{"type": "navigate", "url": "/"}]}
        with pytest.raises(ValidationError) as exc:
            validate_test_ir(data)
        assert "id" in str(exc.value)

    def test_reject_empty_id(self):
        """Empty string ID must be rejected (min_length=1)."""
        data = {"version": "1", "id": "", "name": "N", "actions": [{"type": "navigate", "url": "/"}]}
        with pytest.raises(ValidationError):
            validate_test_ir(data)

    def test_reject_missing_name(self):
        """Missing name must fail validation."""
        data = {"version": "1", "id": "t1", "actions": [{"type": "navigate", "url": "/"}]}
        with pytest.raises(ValidationError) as exc:
            validate_test_ir(data)
        assert "name" in str(exc.value)

    def test_reject_empty_name(self):
        """Empty string name must be rejected (min_length=1)."""
        data = {"version": "1", "id": "t1", "name": "", "actions": [{"type": "navigate", "url": "/"}]}
        with pytest.raises(ValidationError):
            validate_test_ir(data)

    def test_reject_empty_actions(self):
        """Empty actions list must fail validation (min_length=1)."""
        data = {"version": "1", "id": "t1", "name": "N", "actions": []}
        with pytest.raises(ValidationError):
            validate_test_ir(data)

    def test_reject_missing_actions(self):
        """Missing actions field must fail validation."""
        data = {"version": "1", "id": "t1", "name": "N"}
        with pytest.raises(ValidationError):
            validate_test_ir(data)

    # ------------------------------------------------------------------------
    # SECTION 7 MANDATORY REQUIREMENT: Unknown action must be rejected
    # ------------------------------------------------------------------------

    def test_reject_unknown_action_type(self):
        """MANDATORY: Unknown action type must be strictly rejected with ValidationError.

        The validator must NOT:
        - ignore it
        - convert it into another action
        - accept it as an arbitrary dictionary
        - accept an unknown discriminator
        - fall back to Any
        """
        data = {
            "version": "1",
            "id": "t1",
            "name": "N",
            "actions": [
                {"type": "unknown_action"},
            ],
        }
        with pytest.raises(ValidationError) as exc_info:
            validate_test_ir(data)

        # Confirm the error indicates an invalid union tag / discriminator
        errors = exc_info.value.errors()
        assert len(errors) > 0
        error = errors[0]
        assert error["loc"] == ("actions", 0)
        assert "unknown_action" in str(error)

    def test_reject_unknown_action_with_payload(self):
        """Unsupported action with realistic payload (e.g. hover, dragAndDrop) must be rejected."""
        unsupported_actions = [
            {"type": "hover", "target": {"strategy": "css", "value": "#btn"}},
            {"type": "dragAndDrop", "source": "#a", "target": "#b"},
            {"type": "upload", "file": "test.txt"},
            {"type": "custom", "script": "console.log(1)"},
        ]
        for bad_action in unsupported_actions:
            data = {
                "version": "1",
                "id": "t1",
                "name": "N",
                "actions": [bad_action],
            }
            with pytest.raises(ValidationError):
                validate_test_ir(data)

    def test_reject_extra_fields_forbidden(self):
        """Extra fields on action or root must be rejected (extra='forbid')."""
        # Extra field on action
        data_action = {
            "version": "1",
            "id": "t1",
            "name": "N",
            "actions": [{"type": "navigate", "url": "/home", "unexpected": "extra"}],
        }
        with pytest.raises(ValidationError) as exc:
            validate_test_ir(data_action)
        assert "unexpected" in str(exc.value)

        # Extra field on root
        data_root = {
            "version": "1",
            "id": "t1",
            "name": "N",
            "actions": [{"type": "navigate", "url": "/home"}],
            "extra_root": "value",
        }
        with pytest.raises(ValidationError) as exc:
            validate_test_ir(data_root)
        assert "extra_root" in str(exc.value)

    def test_reject_missing_required_action_fields(self):
        """Every action must enforce its required fields."""
        # navigate requires 'url'
        with pytest.raises(ValidationError):
            validate_test_ir({"version": "1", "id": "t", "name": "n", "actions": [{"type": "navigate"}]})

        # navigate rejects empty 'url'
        with pytest.raises(ValidationError):
            validate_test_ir({"version": "1", "id": "t", "name": "n", "actions": [{"type": "navigate", "url": ""}]})

        # click requires 'target'
        with pytest.raises(ValidationError):
            validate_test_ir({"version": "1", "id": "t", "name": "n", "actions": [{"type": "click"}]})

        # fill requires 'target' and 'value'
        with pytest.raises(ValidationError):
            validate_test_ir({
                "version": "1", "id": "t", "name": "n",
                "actions": [{"type": "fill", "target": {"strategy": "text", "value": "T"}}],  # missing value
            })

        # select requires 'target' and 'value'
        with pytest.raises(ValidationError):
            validate_test_ir({
                "version": "1", "id": "t", "name": "n",
                "actions": [{"type": "select", "target": {"strategy": "text", "value": "T"}}],  # missing value
            })

        # press requires 'key'
        with pytest.raises(ValidationError):
            validate_test_ir({"version": "1", "id": "t", "name": "n", "actions": [{"type": "press"}]})

        # press rejects empty 'key'
        with pytest.raises(ValidationError):
            validate_test_ir({"version": "1", "id": "t", "name": "n", "actions": [{"type": "press", "key": ""}]})

        # wait requires 'durationMs'
        with pytest.raises(ValidationError):
            validate_test_ir({"version": "1", "id": "t", "name": "n", "actions": [{"type": "wait"}]})

        # assertText requires 'target' and 'text'
        with pytest.raises(ValidationError):
            validate_test_ir({
                "version": "1", "id": "t", "name": "n",
                "actions": [{"type": "assertText", "target": {"strategy": "text", "value": "T"}}],  # missing text
            })

        # assertVisible requires 'target'
        with pytest.raises(ValidationError):
            validate_test_ir({"version": "1", "id": "t", "name": "n", "actions": [{"type": "assertVisible"}]})

        # assertUrl requires 'url'
        with pytest.raises(ValidationError):
            validate_test_ir({"version": "1", "id": "t", "name": "n", "actions": [{"type": "assertUrl"}]})

        # assertUrl rejects empty 'url'
        with pytest.raises(ValidationError):
            validate_test_ir({"version": "1", "id": "t", "name": "n", "actions": [{"type": "assertUrl", "url": ""}]})

    def test_reject_invalid_wait_duration(self):
        """wait action durationMs must be strictly positive (gt=0)."""
        for bad_duration in [0, -1, -500.5]:
            data = {
                "version": "1", "id": "t", "name": "n",
                "actions": [{"type": "wait", "durationMs": bad_duration}],
            }
            with pytest.raises(ValidationError):
                validate_test_ir(data)

    def test_reject_invalid_locator_strategy(self):
        """Unsupported locator strategy (e.g. xpath, id, name) must be rejected."""
        unsupported_strategies = ["xpath", "id", "class", "name", "tag", "linkText"]
        for bad_strategy in unsupported_strategies:
            data = {
                "version": "1",
                "id": "t1",
                "name": "N",
                "actions": [
                    {"type": "click", "target": {"strategy": bad_strategy, "value": "//div"}},
                ],
            }
            with pytest.raises(ValidationError):
                validate_test_ir(data)

    def test_reject_missing_locator_field(self):
        """Locator missing required field must be rejected."""
        # role locator missing 'role'
        with pytest.raises(ValidationError):
            validate_test_ir({
                "version": "1", "id": "t", "name": "n",
                "actions": [{"type": "click", "target": {"strategy": "role"}}],
            })

        # role locator with empty 'role'
        with pytest.raises(ValidationError):
            validate_test_ir({
                "version": "1", "id": "t", "name": "n",
                "actions": [{"type": "click", "target": {"strategy": "role", "role": ""}}],
            })

        # text locator missing 'value'
        with pytest.raises(ValidationError):
            validate_test_ir({
                "version": "1", "id": "t", "name": "n",
                "actions": [{"type": "click", "target": {"strategy": "text"}}],
            })

        # text locator with empty 'value'
        with pytest.raises(ValidationError):
            validate_test_ir({
                "version": "1", "id": "t", "name": "n",
                "actions": [{"type": "click", "target": {"strategy": "text", "value": ""}}],
            })

        # testId locator missing 'value'
        with pytest.raises(ValidationError):
            validate_test_ir({
                "version": "1", "id": "t", "name": "n",
                "actions": [{"type": "click", "target": {"strategy": "testId"}}],
            })

        # css locator missing 'value'
        with pytest.raises(ValidationError):
            validate_test_ir({
                "version": "1", "id": "t", "name": "n",
                "actions": [{"type": "click", "target": {"strategy": "css"}}],
            })

    def test_reject_wrong_field_types(self):
        """Wrong types (e.g. wait durationMs as string, actions as string) must fail."""
        # durationMs as non-numeric string
        with pytest.raises(ValidationError):
            validate_test_ir({
                "version": "1", "id": "t", "name": "n",
                "actions": [{"type": "wait", "durationMs": "five_seconds"}],
            })

        # actions as non-list
        with pytest.raises(ValidationError):
            validate_test_ir({
                "version": "1", "id": "t", "name": "n",
                "actions": "not a list",
            })

        # fill value as dictionary instead of string
        with pytest.raises(ValidationError):
            validate_test_ir({
                "version": "1", "id": "t", "name": "n",
                "actions": [
                    {"type": "fill", "target": {"strategy": "text", "value": "t"}, "value": {"nested": "bad"}},
                ],
            })


# ============================================================================
# 3. VALIDATION ENTRY POINT TESTS
# ============================================================================

class TestValidationEntryPoints:
    """Tests for clean validation entry points."""

    def test_validate_from_dict(self):
        """validate_test_ir accepts valid dictionary."""
        test_ir = validate_test_ir(MINIMAL_VALID_IR)
        assert isinstance(test_ir, TestIR)
        assert test_ir.id == MINIMAL_VALID_IR["id"]

    def test_validate_from_json_string(self):
        """validate_test_ir accepts valid JSON string."""
        json_str = json.dumps(MINIMAL_VALID_IR)
        test_ir = validate_test_ir(json_str)
        assert isinstance(test_ir, TestIR)
        assert test_ir.id == MINIMAL_VALID_IR["id"]

    def test_model_validate_methods(self):
        """TestIR class methods from_dict and from_json work correctly."""
        ir1 = TestIR.from_dict(MINIMAL_VALID_IR)
        assert isinstance(ir1, TestIR)

        ir2 = TestIR.from_json(json.dumps(MINIMAL_VALID_IR))
        assert isinstance(ir2, TestIR)
        assert ir1.id == ir2.id


# ============================================================================
# 4. SERIALIZATION & ROUNDTRIP TESTS
# ============================================================================

class TestSerialization:
    """Tests for serialization of Test IR to JSON-compatible data."""

    def test_serialize_to_dict(self):
        """serialize_test_ir produces a dictionary suitable for JSON database storage."""
        test_ir = validate_test_ir(ALL_ACTIONS_IR)
        serialized = serialize_test_ir(test_ir)

        assert isinstance(serialized, dict)
        assert serialized["version"] == "1"
        assert serialized["id"] == "all-actions-test-suite"
        assert serialized["name"] == "Comprehensive Test Suite"
        assert len(serialized["actions"]) == 14

        # Verify json.dumps succeeds without error (proves complete JSON compatibility)
        json_dump = json.dumps(serialized)
        assert isinstance(json_dump, str)

    def test_serialize_to_json_string(self):
        """serialize_test_ir with as_json_string=True produces valid JSON string."""
        test_ir = validate_test_ir(MINIMAL_VALID_IR)
        json_str = serialize_test_ir(test_ir, as_json_string=True)

        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["version"] == "1"
        assert parsed["id"] == MINIMAL_VALID_IR["id"]

    def test_model_instance_methods(self):
        """to_dict() and to_json() on TestIR instance work correctly."""
        test_ir = validate_test_ir(MINIMAL_VALID_IR)
        d = test_ir.to_dict()
        assert isinstance(d, dict)
        assert d["id"] == "minimal-test-1"

        j = test_ir.to_json()
        assert isinstance(j, str)
        assert json.loads(j)["id"] == "minimal-test-1"

    def test_preservation_of_discriminators_and_fields(self):
        """Serialization strictly preserves action type and locator strategy discriminators."""
        test_ir = validate_test_ir(ALL_ACTIONS_IR)
        serialized = serialize_test_ir(test_ir)

        expected_types = [
            "navigate", "fill", "fill", "click", "wait", "assertText",
            "assertVisible", "assertUrl", "screenshot", "check", "uncheck",
            "select", "press", "press",
        ]
        actual_types = [action["type"] for action in serialized["actions"]]
        assert actual_types == expected_types

        # Verify target strategies
        click_target = serialized["actions"][3]["target"]
        assert click_target["strategy"] == "role"
        assert click_target["role"] == "button"
        assert click_target["name"] == "Login"

    def test_roundtrip_minimal_ir(self):
        """Input -> Validate -> Serialize -> Validate again -> PASS."""
        ir1 = validate_test_ir(MINIMAL_VALID_IR)
        serialized1 = serialize_test_ir(ir1)
        ir2 = validate_test_ir(serialized1)
        serialized2 = serialize_test_ir(ir2)

        assert ir1.model_dump() == ir2.model_dump()
        assert serialized1 == serialized2

    def test_roundtrip_all_actions_ir(self):
        """Full suite roundtrip: Input -> Validate -> Serialize -> Validate again -> PASS."""
        ir1 = validate_test_ir(ALL_ACTIONS_IR)
        serialized1 = serialize_test_ir(ir1)
        ir2 = validate_test_ir(serialized1)
        serialized2 = serialize_test_ir(ir2)

        assert ir1.model_dump() == ir2.model_dump()
        assert serialized1 == serialized2

    def test_roundtrip_login_smoke_fixture(self):
        """Fixture roundtrip: Raw file -> Validate -> Serialize -> Validate again -> PASS."""
        fixture_path = Path(__file__).resolve().parent.parent.parent / "automation" / "examples" / "test-ir" / "login-smoke.json"
        if not fixture_path.exists():
            pytest.skip(f"Fixture not found at {fixture_path}")

        with open(fixture_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        ir1 = validate_test_ir(raw)
        serialized = serialize_test_ir(ir1)
        ir2 = validate_test_ir(serialized)

        assert ir1.id == ir2.id == "login-smoke"
        assert len(ir1.actions) == len(ir2.actions) == 6
        assert ir1.model_dump() == ir2.model_dump()
