# D05-15 Test IR Persistence Architecture Specification

**Document Version:** 1.0.0  
**Phase:** D05-15 (Day 5, Week 1)  
**Author:** Developer 3 (Backend & Database Architecture)  
**Status:** Approved Architecture Blueprint  

---

## 1. Executive Summary

This document specifies the persistence, validation, versioning, and lifecycle architecture for **Test IR (Intermediate Representation) v1** within the TestPilot AI MVP.

Test IR v1 acts as the decoupling contract between:
1. **Frontend / Test Generation UI** (Dev 1)
2. **Playwright Execution Engine & Automation Runner** (Dev 2)
3. **Database Persistence & CRUD API** (Dev 3)

The goal of D05-15 is to guarantee that a valid Test IR survives storage in Supabase PostgreSQL without semantic alteration, is validated on both write and read, rejects corrupted or unsupported data, and preserves multi-tenant isolation via Row Level Security (RLS).

---

## 2. Canonical Test IR v1 Contract

### 2.1 Canonical Source of Truth
The canonical schema and types are defined in:
- Schema: [`automation/src/ir/schema.ts`](file:///home/liveshm/Desktop/TestPilotAI/automation/src/ir/schema.ts)
- Types: [`automation/src/ir/types.ts`](file:///home/liveshm/Desktop/TestPilotAI/automation/src/ir/types.ts)
- Architectural Decision: [`docs/architecture/ADR-001-test-ir.md`](file:///home/liveshm/Desktop/TestPilotAI/docs/architecture/ADR-001-test-ir.md)
- Reference Example: [`automation/examples/test-ir/login-smoke.json`](file:///home/liveshm/Desktop/TestPilotAI/automation/examples/test-ir/login-smoke.json)

### 2.2 Structure & Types
```typescript
{
  version: "1",                     // Strictly literal "1"
  id: string,                       // min_length: 1
  name: string,                     // min_length: 1
  description?: string,             // Optional description
  actions: TestAction[]             // Non-empty array (min 1 action)
}
```

### 2.3 Supported Actions (`TestAction`)
Discriminated union on `type`:
1. `navigate`: `{ type: "navigate", url: string }`
2. `click`: `{ type: "click", target: LocatorTarget }`
3. `fill`: `{ type: "fill", target: LocatorTarget, value: string }`
4. `select`: `{ type: "select", target: LocatorTarget, value: string }`
5. `check`: `{ type: "check", target: LocatorTarget }`
6. `uncheck`: `{ type: "uncheck", target: LocatorTarget }`
7. `press`: `{ type: "press", target?: LocatorTarget, key: string }`
8. `wait`: `{ type: "wait", durationMs: number (positive) }`
9. `assertText`: `{ type: "assertText", target: LocatorTarget, text: string }`
10. `assertVisible`: `{ type: "assertVisible", target: LocatorTarget }`
11. `assertUrl`: `{ type: "assertUrl", url: string }`
12. `screenshot`: `{ type: "screenshot", name?: string }`

### 2.4 Supported Locator Strategies (`LocatorTarget`)
Discriminated union on `strategy`:
1. `role`: `{ strategy: "role", role: string, name?: string }`
2. `text`: `{ strategy: "text", value: string }`
3. `label`: `{ strategy: "label", value: string }`
4. `placeholder`: `{ strategy: "placeholder", value: string }`
5. `testId`: `{ strategy: "testId", value: string }`
6. `css`: `{ strategy: "css", value: string }`

> Note: Per ADR-001, `xpath` is explicitly disallowed and unsupported.

---

## 3. Database Schema & Persistence Representation

### 3.1 Table Definition
Test IR is stored in `public.tests` (defined in [`backend/migrations/001_initial_schema.sql`](file:///home/liveshm/Desktop/TestPilotAI/backend/migrations/001_initial_schema.sql)):

```sql
CREATE TABLE IF NOT EXISTS public.tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    test_ir JSONB NOT NULL DEFAULT '{}'::jsonb,
    ir_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 3.2 Storage Considerations
- **`test_ir` (`jsonb`)**: Persists the complete structured Test IR. Storing as native PostgreSQL `jsonb` allows:
  - Preserving nested objects, arrays, and type primitives.
  - JSON querying and indexability in PostgreSQL.
  - Absence of arbitrary string escaping.
- **`ir_version` (`integer`)**: Tracks the schema version at the table column level (default: `1`). Ensures fast querying and filtering of tests by schema version without unpacking the JSONB blob.
- **Strict Equality Guarantee**: When stored as JSONB and reloaded, objects and arrays are reconstructed faithfully. Field serialization ensures that optional fields (like `description` or `target` in `press`) are not polluted with synthetic `null` values.

---

## 4. API Endpoints & CRUD Integration Flow

The backend persistence integrates into the canonical D04 CRUD routes without introducing redundant endpoints:

| Method | Endpoint | Description | Test IR Handling |
| :--- | :--- | :--- | :--- |
| `POST` | `/projects/{project_id}/tests` | Create new test | Receives full Test IR in payload, validates against `TestIR` v1, stores `test_ir` and `ir_version = 1`. |
| `GET` | `/projects/{project_id}/tests` | List tests for project | Reads records from Supabase, validates each `test_ir` and `ir_version` on read, returns list. |
| `GET` | `/tests/{test_id}` | Get test details | Reads record from Supabase, validates `test_ir` and `ir_version` on read, returns full test. |
| `PATCH` | `/tests/{test_id}` | Update test | If `test_ir` present in payload, validates against `TestIR` v1, updates `test_ir` and sets `ir_version = 1`. |
| `DELETE` | `/tests/{test_id}` | Delete test | Deletes record via project ownership check and cascading RLS. |

All routes are mounted under both `/api/v1` and `/` root.

---

## 5. Validation Architecture

### 5.1 Validation on Write (Ingestion)
When creating or updating a test:
1. **Request Body Parsing**: FastAPI and Pydantic parse `test_ir` against the `TestIR` model ([`backend/app/schemas/test_ir.py`](file:///home/liveshm/Desktop/TestPilotAI/backend/app/schemas/test_ir.py)).
2. **Schema Invariant Checking**:
   - `version` must equal `"1"`.
   - `id` and `name` must be non-empty strings.
   - `actions` must be a non-empty array (`min_length=1`).
   - Every action must match one of the 12 discriminated union types.
   - Every locator target must match one of the 6 discriminated union strategies.
   - `durationMs` must be positive.
   - Disallowed fields (`extra="forbid"`) reject unknown attributes.
3. **Rejection Handling**: If invalid, FastAPI returns `422 Unprocessable Entity` with standardized error payload (`code: "VALIDATION_ERROR"`). The database insert or update is never attempted.
4. **Storage Cleanliness**: Validated IR is dumped with `exclude_none=True` so optional omitted keys do not add unnecessary `null` keys into PostgreSQL JSONB.

### 5.2 Validation on Read (Retrieval)
When retrieving a test via `GET /tests/{id}` or `GET /projects/{id}/tests`:
1. **Fetch from DB**: Read `test_ir` JSONB and `ir_version` column.
2. **Version Check**: Confirm `ir_version == 1` and `test_ir["version"] == "1"`.
3. **Schema Validation**: Validate `test_ir` against canonical Pydantic model `TestIR.model_validate(record["test_ir"])`.
4. **Integrity Enforcement**:
   - If corrupted or unsupported, the backend logs detailed diagnostic error context (e.g. Test ID, specific validation failure) on the server.
   - The endpoint returns `HTTP 500 Internal Server Error` with `detail: "Stored Test IR failed validation against canonical contract"`.
   - No sensitive database internals or connection strings are leaked in the client response.
   - **Crucial Rule**: The service **never** silently transforms, repairs, or mutates corrupted data in the database.

---

## 6. Automation Engine Consumption

Dev 2's automation engine consumes Test IR directly from the database or API:
- **Runner**: [`automation/src/runner/authenticated-runner.ts`](file:///home/liveshm/Desktop/TestPilotAI/automation/src/runner/authenticated-runner.ts)
- **Consumption Flow**:
  1. Runner receives a `TestIR` object (typed via `automation/src/ir/types.ts`).
  2. Creates a Playwright `BrowserContext` (injecting `storageState` if authenticated).
  3. Iterates through `test.actions`:
     - `navigate` -> `page.goto(action.url)`
     - `click` -> `resolveLocator(page, action.target).click()`
     - `fill` -> `resolveLocator(page, action.target).fill(action.value)`
     - `assertVisible` -> `resolveLocator(page, action.target).waitFor({ state: 'visible' })`
     - `assertUrl` -> checks `page.url().includes(action.url)`
     - `wait` -> `page.waitForTimeout(action.durationMs)`
  4. Returns `RunnerResult` with `success`, `testId`, and `executedActionsCount`.

Because the persisted representation exactly matches `automation/src/ir/schema.ts`, the runner can execute tests directly with zero data translation.

---

## 7. Multi-Tenant Security & Isolation (RLS)

Test persistence strictly adheres to the Supabase Row Level Security model:
- `tests` table has RLS enabled:
  ```sql
  CREATE POLICY "Tests select policy" ON public.tests
      FOR SELECT USING (
          EXISTS (
              SELECT 1 FROM public.projects
              WHERE public.projects.id = public.tests.project_id
                AND public.projects.owner_id = auth.uid()
          )
      );
  ```
- All operations (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) require that the parent project is owned by `auth.uid()`.
- User A cannot read, create, update, or delete tests belonging to User B.
- Even if User A attempts to provide User B's `project_id` in `POST /projects/{id}/tests`, the service and RLS policy reject the request with `404 Not Found`.

---

## 8. Frontend & Backend Mismatches Reconciled

| Component | Dev 1 Initial Draft | Dev 2 Canonical Contract | Reconciliation |
| :--- | :--- | :--- | :--- |
| **Action Collection** | `steps: TestStep[]` in `frontend/src/types/test-ir.ts` | `actions: TestAction[]` in `automation/src/ir/schema.ts` | Dev 2's `actions` is canonical. Backend enforces `actions`. Frontend UI and services align with Dev 2. |
| **Locators** | Flat string target (e.g. `target: string`) | Strongly-typed `LocatorTarget` with 6 strategies | Discriminated union `LocatorTarget` is stored and validated. |
| **IR Version** | `"1.0"` string in some drafts | `"1"` literal string | Strictly `"1"` in JSON, `1` integer in DB column. |
| **Endpoints** | `GET /tests/{id}/ir`, `PUT /tests/{id}/ir` placeholders in `tests-api.ts` | Standard CRUD in D04 (`GET /tests/{id}`, `PATCH /tests/{id}`) | D04 CRUD endpoints are the source of truth; full `test_ir` is returned in `GET /tests/{id}` and updated via `PATCH /tests/{id}`. |
| **Wait Duration** | Number in JS | `durationMs` float | Schema updated to `Union[int, float]` to preserve integer millisecond values without `.0` float drift. |
