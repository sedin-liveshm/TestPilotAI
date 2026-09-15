# Test IR v1.0 Canonical Schema Specification (Frozen)

**Document Version:** 1.0.0  
**Status:** Frozen (Day 5, Week 1)  
**Authors:** Developer 2 (Test Engine & Automation) & Developer 3 (Backend Architecture)  

---

## 1. Overview & Architectural Role

Test Intermediate Representation (Test IR) v1.0 is the canonical, technology-agnostic data contract defining end-to-end browser automation tests in **TestPilot AI**.

```
  ┌─────────────────────────┐          ┌──────────────────────────┐
  │   TypeScript / Zod      │          │   Python / Pydantic v2   │
  │   automation/src/ir/    │          │   backend/app/schemas/   │
  └────────────┬────────────┘          └────────────┬─────────────┘
               │                                    │
               │         Test IR v1.0 JSON          │
               └───────────────►◄───────────────────┘
                                │
               ┌────────────────┴────────────────┐
               ▼                                 ▼
      Playwright Runner                 Supabase Database
      (Execution Engine)                 (JSONB test_ir)
```

Both TypeScript (`automation/src/ir/schema.ts`) and Python (`backend/app/schemas/test_ir.py`) implementations express the identical schema rules, validation constraints, and serialization formats.

---

## 2. Root Structure (`TestIR`)

The root `TestIR` object represents a complete test scenario.

| Field | Type | Required | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `version` | `Literal["1"]` | **Yes** | Exactly `"1"` | Schema version identifier |
| `id` | `string` | **Yes** | `min_length=1` | Unique test identifier |
| `name` | `string` | **Yes** | `min_length=1` | Human-readable test title |
| `description` | `string` | No | `Optional` | Optional test narrative / context |
| `actions` | `List[TestAction]` | **Yes** | `min_length=1` | Non-empty ordered sequence of actions |

**Model Config:** `extra="forbid"` (unrecognized top-level properties are strictly rejected).

---

## 3. Supported Action Catalog (`TestAction`)

All actions use `type` as the discriminated union tag. Unknown `type` tags are rejected immediately.

| Action (`type`) | Parameters | Types & Constraints | Description |
| :--- | :--- | :--- | :--- |
| `navigate` | `url` | `string` (`min_length=1`) | Navigates browser page to target URL |
| `click` | `target` | `LocatorTarget` | Clicks on the resolved element |
| `fill` | `target`, `value` | `LocatorTarget`, `string` | Clears and fills text input |
| `select` | `target`, `value` | `LocatorTarget`, `string` | Selects option from dropdown element |
| `check` | `target` | `LocatorTarget` | Checks a checkbox or radio button |
| `uncheck` | `target` | `LocatorTarget` | Unchecks a checkbox element |
| `press` | `key`, `target?` | `string` (`min_length=1`), `Optional[LocatorTarget]` | Presses a keyboard key, optionally focused |
| `wait` | `durationMs` | `number` (`gt=0`, positive) | Waits for specified duration in milliseconds |
| `assertText` | `target`, `text` | `LocatorTarget`, `string` | Asserts element contains expected text |
| `assertVisible` | `target` | `LocatorTarget` | Asserts element is visible in the viewport |
| `assertUrl` | `url` | `string` (`min_length=1`) | Asserts current browser URL matches |
| `screenshot` | `name?` | `Optional[string]` | Captures viewport screenshot with optional label |

**Action Config:** Every action model specifies `extra="forbid"`.

---

## 4. Supported Locator Strategy Catalog (`LocatorTarget`)

All locators use `strategy` as the discriminated union tag. Legacy locators like `xpath` are explicitly forbidden.

| Strategy (`strategy`) | Parameters | Types & Constraints | Description |
| :--- | :--- | :--- | :--- |
| `role` | `role`, `name?` | `role: string` (`min_length=1`), `name?: string` | Semantic ARIA role with optional accessible name |
| `text` | `value` | `string` (`min_length=1`) | Element matching visible text |
| `label` | `value` | `string` (`min_length=1`) | Input associated with text label |
| `placeholder` | `value` | `string` (`min_length=1`) | Input matching placeholder text |
| `testId` | `value` | `string` (`min_length=1`) | Element matching `data-testid` attribute |
| `css` | `value` | `string` (`min_length=1`) | Standard CSS selector |

**Locator Config:** Every locator model specifies `extra="forbid"`.

---

## 5. Python / Pydantic v2 Implementation

Located in `backend/app/schemas/test_ir.py`.

### Validation Entry Point
```python
from app.schemas.test_ir import validate_test_ir, TestIR

# Validates raw dictionary or JSON string, raising ValidationError on any discrepancy
test_ir = validate_test_ir(raw_data)

# Alternatively using the class method
test_ir = TestIR.from_dict(raw_data)
test_ir = TestIR.from_json(raw_json_str)
```

### Serialization Entry Point
```python
from app.schemas.test_ir import serialize_test_ir

# Returns a JSON-safe dictionary suitable for Supabase JSONB persistence
data_dict = serialize_test_ir(test_ir)

# Returns a valid JSON string
json_str = serialize_test_ir(test_ir, as_json_string=True)

# Alternatively using instance methods
data_dict = test_ir.to_dict()
json_str = test_ir.to_json()
```

---

## 6. Parity with TypeScript / Zod Schema

| Rule | TypeScript / Zod (`schema.ts`) | Python / Pydantic v2 (`test_ir.py`) | Parity Status |
| :--- | :--- | :--- | :--- |
| Version Check | `z.literal('1')` | `Literal["1"]` | Identical |
| ID / Name Min Length | `z.string().min(1)` | `Field(..., min_length=1)` | Identical |
| Non-empty Actions | `z.array(...).min(1)` | `List[...] = Field(..., min_length=1)` | Identical |
| Discriminated Union (Actions) | `z.discriminatedUnion('type', ...)` | `Annotated[Union[...], Field(discriminator="type")]` | Identical |
| Discriminated Union (Locators) | `z.discriminatedUnion('strategy', ...)` | `Annotated[Union[...], Field(discriminator="strategy")]` | Identical |
| Extra Properties | Disallowed by Zod strict objects | `model_config = ConfigDict(extra="forbid")` | Identical |
| Duration Constraint | `z.number().positive()` | `Field(..., gt=0)` | Identical |

---

## 7. Integration Notes for Developer 3 (Database & API)

- When saving test cases in `public.tests`, serialize `test_ir` using `serialize_test_ir(data.test_ir)` or `data.test_ir.model_dump()`.
- The column `test_ir` in table `public.tests` is `JSONB` and stores the dictionary format.
- The `ir_version` integer column is set to `1`.
- Any client request sending an invalid action (e.g. `{"type": "unknown_action"}`) automatically returns `HTTP 422 Unprocessable Entity` via FastAPI's built-in validation handling.
