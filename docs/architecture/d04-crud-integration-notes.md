# D04-12 Project & Test CRUD API Integration Notes

**Document Version:** 1.0.0  
**Phase:** D04-12 (Day 4, Week 1)  
**Author:** Developer 3 (Backend & Database Architecture)  
**Status:** Approved Integration Specification  

---

## 1. What Dev 1 Implemented That Backend Must Integrate With

Dev 1 implemented the frontend foundation using Next.js 16 (App Router), React 19, Zustand, and Tailwind CSS. Key integration points:

- **API Client Utility (`frontend/src/services/api-client.ts`)**:
  - Configured with `API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'`.
  - Sends standard JSON requests with `Content-Type: application/json`.
  - Normalizes responses: if the response body contains a `data` key, it unwraps `data` while preserving metadata (`meta`); otherwise, wraps the entire body as `{ data }`.
  - Explicitly handles `204 No Content` by returning `{ data: {} }`.
  - Error normalization expects `{ error: { message: string, code?: string, details?: unknown } }` or falls back to `statusText`.
- **Projects Service (`frontend/src/services/projects-api.ts`)**:
  - `getProjects()`: `GET /projects`
  - `getProject(id)`: `GET /projects/{id}`
  - `createProject(data)`: `POST /projects`
  - `updateProject(id, data)`: `PATCH /projects/{id}`
  - `deleteProject(id)`: `DELETE /projects/{id}`
- **Tests Service (`frontend/src/services/tests-api.ts`)**:
  - `getTests(projectId)`: `GET /projects/{projectId}/tests`
  - `getTest(id)`: `GET /tests/{id}`
  - `getTestIR(testId)`: `GET /tests/{testId}/ir`
  - `updateTestIR(testId, ir)`: `PUT /tests/{testId}/ir`
- **Frontend Domain Types (`frontend/src/types/domain.ts`)**:
  - `Project`: `{ id, name, description?, ownerId, createdAt, updatedAt }`
  - `Test`: `{ id, projectId, name, description?, testIrId?, createdAt, updatedAt }`
- **Auth Flow & Store (`frontend/src/store/auth-store.ts`, `frontend/src/services/auth-api.ts`)**:
  - `login()`: `POST /auth/login` returning `{ accessToken, refreshToken?, user: { id, email, name? } }`
  - `logout()`: `POST /auth/logout`
  - `getCurrentUser()`: `GET /auth/me`

---

## 2. What Dev 2 Implemented That Backend Must Integrate With

Dev 2 implemented the Test Engine & Test Intermediate Representation (Test IR) v1 contract in TypeScript with Zod validation, alongside Playwright automation runner placeholders:

- **Canonical Test IR Schema (`automation/src/ir/schema.ts`, `automation/src/ir/types.ts`)**:
  - Top-level schema `TestIRSchema`:
    - `version`: literal `"1"`
    - `id`: string (min 1)
    - `name`: string (min 1)
    - `description`: optional string
    - `actions`: non-empty array (`min(1)`) of `TestAction`
  - Discriminated union on `type` for `TestAction`:
    - `navigate`: `{ type: 'navigate', url: string }`
    - `click`: `{ type: 'click', target: LocatorTarget }`
    - `fill`: `{ type: 'fill', target: LocatorTarget, value: string }`
    - `select`: `{ type: 'select', target: LocatorTarget, value: string }`
    - `check`: `{ type: 'check', target: LocatorTarget }`
    - `uncheck`: `{ type: 'uncheck', target: LocatorTarget }`
    - `press`: `{ type: 'press', target?: LocatorTarget, key: string }`
    - `wait`: `{ type: 'wait', durationMs: number }`
    - `assertText`: `{ type: 'assertText', target: LocatorTarget, text: string }`
    - `assertVisible`: `{ type: 'assertVisible', target: LocatorTarget }`
    - `assertUrl`: `{ type: 'assertUrl', url: string }`
    - `screenshot`: `{ type: 'screenshot', name?: string }`
  - Discriminated union on `strategy` for `LocatorTarget`:
    - `role`: `{ strategy: 'role', role: string, name?: string }`
    - `text`: `{ strategy: 'text', value: string }`
    - `label`: `{ strategy: 'label', value: string }`
    - `placeholder`: `{ strategy: 'placeholder', value: string }`
    - `testId`: `{ strategy: 'testId', value: string }`
    - `css`: `{ strategy: 'css', value: string }`
- **Architectural Decision Records**:
  - `ADR-001-test-ir.md`: Confirms Test IR v1 as canonical contract. Rejects XPath; enforces strict action typing and version `"1"`.
  - `ADR-002-authenticated-runner.md`: Explains that the runner executes `TestIR` actions with an injected `storageState.json` or unauthenticated session.
- **Reference Example (`automation/examples/test-ir/login-smoke.json`)**:
  - Conforms strictly to `TestIRSchema` with `version: "1"`, `actions`, and locator strategies (`label`, `placeholder`, `role`).

---

## 3. Current Authentication Flow

- Identity provider: **Supabase Auth (`auth.users`)**.
- Backend does not maintain a custom authentication system or custom credentials table.
- Requests supply authentication via the `Authorization: Bearer <supabase_jwt>` header.
- Token validation extracts:
  - `user_id` (`auth.uid()`)
  - `email`
  - User claims/metadata
- Security rule: User identity in request bodies (such as `owner_id`) is strictly forbidden/ignored; `owner_id` is always derived directly from the verified session token.
- Supabase client integration: Scoped PostgREST queries inherit the bearer token so that PostgreSQL Row Level Security (RLS) is evaluated in the context of the calling user.

---

## 4. Current Test IR Contract

The backend must store and validate Test IR matching Dev 2's canonical schema:
- Test IR is stored in `public.tests.test_ir` as JSONB.
- The `ir_version` column in `public.tests` tracks schema version (integer `1`).
- Pydantic models in Python mirror Dev 2's Zod schema:
  - `LocatorTarget`: Discriminated union on `strategy` (`role`, `text`, `label`, `placeholder`, `testId`, `css`).
  - `TestAction`: Discriminated union on `type` (`navigate`, `click`, `fill`, `select`, `check`, `uncheck`, `press`, `wait`, `assertText`, `assertVisible`, `assertUrl`, `screenshot`).
  - `TestIR`: `{ version: "1", id: str, name: str, description: Optional[str], actions: List[TestAction] }`.

---

## 5. Existing Database Schema

Defined in `backend/migrations/001_initial_schema.sql` and verified by `docs/architecture/rls-test-plan.md`:

```sql
-- Profiles Table
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Projects Table
CREATE TABLE IF NOT EXISTS public.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    base_url TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tests Table
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

### RLS Policies
- `projects`: `owner_id = auth.uid()` for SELECT, INSERT, UPDATE, DELETE.
- `tests`: `EXISTS (SELECT 1 FROM projects WHERE projects.id = tests.project_id AND projects.owner_id = auth.uid())` for SELECT, INSERT, UPDATE, DELETE.

---

## 6. Existing API Assumptions

- FastAPI mounted in `backend/app/main.py`.
- Health endpoints exist at `/health` and `/health/db`.
- Frontend expects endpoints accessible under `/api/v1` (`api-client.ts`), while specification docs and standard conventions also reference root `/projects` and `/tests`.
- Error response format:
  ```json
  {
    "error": {
      "message": "Human readable description",
      "code": "ERROR_CODE",
      "details": null
    }
  }
  ```

---

## 7. Mismatches Discovered & Reconciliation

| Component | Inconsistency / Mismatch | Reconciliation Strategy |
| :--- | :--- | :--- |
| **Project URL field** | `database-api-contract.md` references `target_base_url`, whereas `001_initial_schema.sql` and `seed.sql` use `base_url`. | Use `base_url` as primary field in Pydantic schema and DB column. Add `target_base_url` as alias in request schemas to support both smoothly. |
| **Test Title field** | `database-api-contract.md` mentions `title`, whereas `001_initial_schema.sql`, `seed.sql`, Dev 1 (`domain.ts`), and Dev 2 (`schema.ts`) use `name`. | Use `name` as canonical attribute. Support `title` as alias in request schemas so clients sending `title` or `name` succeed. |
| **Test IR steps vs actions** | Dev 1 (`frontend/src/types/test-ir.ts`) drafted `steps: TestStep[]`, whereas Dev 2 implemented canonical `actions: TestAction[]` in `schema.ts`. | Canonical is Dev 2's `actions: TestAction[]` with `version: "1"`. Backend enforces Dev 2's schema strictly. |
| **Route Prefixes** | Frontend `api-client.ts` uses `/api/v1` base, while `database-api-contract.md` lists `/projects`. | Mount routes under both `/api/v1` and `/` so `/api/v1/projects` and `/projects` both resolve seamlessly without breaking frontend or direct clients. |
| **Supabase Client RLS** | Initial `get_supabase_client()` used global key without forwarding user JWT to PostgREST. | Add user-scoped client dependency that forwards `Authorization: Bearer <token>` to PostgREST so Supabase evaluates `auth.uid()` and enforces RLS in DB. |

---

## 8. Chosen API Request/Response Contract

### 8.1 Project Endpoints

#### `POST /projects` (and `/api/v1/projects`)
- **Auth**: Required Bearer token.
- **Request Body**:
  ```json
  {
    "name": "E-Commerce App",
    "description": "Store test suite",
    "base_url": "https://store.example.com"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "data": {
      "id": "uuid",
      "name": "E-Commerce App",
      "description": "Store test suite",
      "base_url": "https://store.example.com",
      "owner_id": "user-uuid",
      "created_at": "ISO-8601",
      "updated_at": "ISO-8601"
    }
  }
  ```

#### `GET /projects` (and `/api/v1/projects`)
- **Query Params**: `page=1`, `page_size=20`, `search=` (optional)
- **Response**: `200 OK`
  ```json
  {
    "data": [ ... ],
    "meta": {
      "page": 1,
      "page_size": 20,
      "total": 1
    }
  }
  ```

#### `GET /projects/{project_id}`
- **Response**: `200 OK` (`{ "data": { ... } }`)
- **Errors**: `404 Not Found` if project does not exist or is not owned by user.

#### `PATCH /projects/{project_id}`
- **Request Body**: Partial (`name?`, `description?`, `base_url?`)
- **Response**: `200 OK` (`{ "data": { ... } }`)
- **Errors**: `404 Not Found` if inaccessible.

#### `DELETE /projects/{project_id}`
- **Response**: `204 No Content`
- **Errors**: `404 Not Found` if inaccessible.

---

### 8.2 Test Endpoints

#### `POST /projects/{project_id}/tests` (and `/api/v1/projects/{project_id}/tests`)
- **Auth**: Required Bearer token.
- **Ownership Check**: Verifies parent `project_id` is owned by caller.
- **Request Body**:
  ```json
  {
    "name": "Login smoke test",
    "description": "Verifies login",
    "test_ir": {
      "version": "1",
      "id": "login-smoke",
      "name": "Login smoke test",
      "description": "Verifies login",
      "actions": [
        { "type": "navigate", "url": "/login" },
        { "type": "fill", "target": { "strategy": "label", "value": "Email" }, "value": "user@example.com" },
        { "type": "click", "target": { "strategy": "role", "role": "button", "name": "Login" } },
        { "type": "assertVisible", "target": { "strategy": "role", "role": "heading", "name": "Dashboard" } }
      ]
    }
  }
  ```
- **Response**: `201 Created` (`{ "data": { ... } }`)

#### `GET /projects/{project_id}/tests`
- **Query Params**: `page=1`, `page_size=20`, `search=` (optional)
- **Response**: `200 OK` (`{ "data": [ ... ], "meta": { "page": 1, "page_size": 20, "total": 1 } }`)

#### `GET /tests/{test_id}`
- **Response**: `200 OK` (`{ "data": { ... } }`)
- **Errors**: `404 Not Found` if test belongs to another user's project or does not exist.

#### `PATCH /tests/{test_id}`
- **Request Body**: Partial (`name?`, `description?`, `test_ir?`)
- **Response**: `200 OK` (`{ "data": { ... } }`)
- **Errors**: `404 Not Found` if inaccessible.

#### `DELETE /tests/{test_id}`
- **Response**: `204 No Content`
- **Errors**: `404 Not Found` if inaccessible.

---

## 9. Files to Create / Modify

### Files to Create
1. `backend/app/schemas/__init__.py`
2. `backend/app/schemas/project.py` (Pydantic models for project create, update, response)
3. `backend/app/schemas/test_ir.py` (Pydantic models for canonical Test IR v1 actions & locators)
4. `backend/app/schemas/test.py` (Pydantic models for test create, update, response)
5. `backend/app/schemas/common.py` (Pagination, ApiResponse, ApiError schemas)
6. `backend/app/dependencies/__init__.py`
7. `backend/app/dependencies/auth.py` (Supabase JWT authentication dependency)
8. `backend/app/services/__init__.py`
9. `backend/app/services/project_service.py` (Project business logic & RLS client execution)
10. `backend/app/services/test_service.py` (Test business logic & ownership validation)
11. `backend/app/api/__init__.py`
12. `backend/app/api/routes/__init__.py`
13. `backend/app/api/routes/projects.py` (Project CRUD routes)
14. `backend/app/api/routes/tests.py` (Test CRUD routes)
15. `backend/tests/test_projects_crud.py` (Integration tests for Project CRUD, ownership & RLS)
16. `backend/tests/test_tests_crud.py` (Integration tests for Test CRUD, ownership, spoofing & Test IR validation)

### Files to Modify
1. `backend/app/main.py` (Include API routers for `/api/v1` and `/`, register error handlers)
2. `backend/app/db/supabase.py` (Add user-scoped Supabase/PostgREST client creation helper)
3. `backend/app/config.py` (Add optional JWT secret / environment settings if needed)
