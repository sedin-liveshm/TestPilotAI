# TestPilot AI — RLS Security Test Plan

**Document Version:** 1.0.0  
**Task ID:** D03-09  
**Author:** Senior Backend Architect (Developer 3)  
**Status:** Approved Security Verification Specification  

---

## 1. Overview & Objective

This document specifies the formal security test suite for validating PostgreSQL Row Level Security (RLS) enforcement across `profiles`, `projects`, and `tests` tables.

The core security principle of TestPilot AI is **strict multi-tenant isolation**:
- Every authenticated user (`auth.uid()`) can only access data they explicitly own.
- No user can view, insert, update, or delete another user's projects or test suites.
- Permissive policies such as `USING (true)` are strictly forbidden on protected tables.

---

## 2. Test Setup & Fixtures

### Test Users
- **User A**: `email = user_a@example.com`, `id = USER_A_UUID` (Authenticated Session A)
- **User B**: `email = user_b@example.com`, `id = USER_B_UUID` (Authenticated Session B)
- **Anon**: Unauthenticated Request (No JWT Bearer Token)

### Test Fixtures
- **Project A**: `id = PROJECT_A_UUID`, `owner_id = USER_A_UUID`
- **Project B**: `id = PROJECT_B_UUID`, `owner_id = USER_B_UUID`
- **Test A**: `id = TEST_A_UUID`, `project_id = PROJECT_A_UUID`
- **Test B**: `id = TEST_B_UUID`, `project_id = PROJECT_B_UUID`

---

## 3. Security Test Matrix

| Test ID | Operator | Action | Target Entity | Expected Result | RLS Policy Evaluated |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TEST 1** | Anonymous | `SELECT * FROM projects` | All Projects | **DENIED** (0 rows returned / 401 Error) | `Projects select policy` |
| **TEST 2** | User A | `SELECT * FROM projects WHERE id = Project A` | Project A | **ALLOWED** (1 row returned) | `auth.uid() = owner_id` |
| **TEST 3** | User A | `SELECT * FROM projects WHERE id = Project B` | Project B | **DENIED** (0 rows returned) | `auth.uid() = owner_id` |
| **TEST 4** | User B | `SELECT * FROM projects WHERE id = Project A` | Project A | **DENIED** (0 rows returned) | `auth.uid() = owner_id` |
| **TEST 5** | User A | `UPDATE projects SET name = 'Hacked' WHERE id = Project B` | Project B | **DENIED** (0 rows updated) | `Projects update policy` |
| **TEST 6** | User A | `DELETE FROM projects WHERE id = Project B` | Project B | **DENIED** (0 rows deleted) | `Projects delete policy` |
| **TEST 7** | User A | `SELECT * FROM tests WHERE id = Test A` | Test A | **ALLOWED** (1 row returned) | `Tests select policy` (EXISTS project owner check) |
| **TEST 8** | User A | `SELECT * FROM tests WHERE id = Test B` | Test B | **DENIED** (0 rows returned) | `Tests select policy` (EXISTS project owner check) |
| **TEST 9** | User A | `INSERT INTO projects (owner_id, name) VALUES (User B, 'Spoof')` | Project Creation | **DENIED** (WITH CHECK violation) | `Projects insert policy` (`auth.uid() = owner_id`) |
| **TEST 10** | User A | `INSERT INTO tests (project_id, name) VALUES (Project B, 'Inject')` | Test Creation | **DENIED** (WITH CHECK violation) | `Tests insert policy` (EXISTS project owner check) |

---

## 4. Execution Procedures & SQL Test Queries

### TEST 1: Unauthenticated Read
```sql
-- Executed as anon role
SELECT * FROM public.projects;
-- Verified: Returns 0 rows.
```

### TEST 2 & TEST 3: User A Isolation Read
```sql
-- Executed as User A (auth.uid() = USER_A_UUID)
SELECT * FROM public.projects;
-- Verified: Returns ONLY Project A. Project B is filtered out seamlessly by RLS.
```

### TEST 4: User B Cross-Read Attempt
```sql
-- Executed as User B (auth.uid() = USER_B_UUID)
SELECT * FROM public.projects WHERE id = 'PROJECT_A_UUID';
-- Verified: Returns 0 rows.
```

### TEST 5: User A Cross-Update Attempt
```sql
-- Executed as User A (auth.uid() = USER_A_UUID)
UPDATE public.projects SET name = 'Tampered' WHERE id = 'PROJECT_B_UUID';
-- Verified: 0 rows modified.
```

### TEST 6: User A Cross-Delete Attempt
```sql
-- Executed as User A (auth.uid() = USER_A_UUID)
DELETE FROM public.projects WHERE id = 'PROJECT_B_UUID';
-- Verified: 0 rows deleted.
```

### TEST 7 & TEST 8: Test Level Inherited RLS Read
```sql
-- Executed as User A (auth.uid() = USER_A_UUID)
SELECT * FROM public.tests;
-- Verified: Returns ONLY Test A (belonging to Project A). Test B is inaccessible.
```

### TEST 9: Project Identity Spoofing Prevention
```sql
-- Executed as User A (auth.uid() = USER_A_UUID)
INSERT INTO public.projects (owner_id, name, base_url)
VALUES ('USER_B_UUID', 'Spoofed Project', 'https://example.com');
-- Verified: Raises exception: new row violates row-level security policy for table "projects".
```

### TEST 10: Test Injection into Foreign Project Prevention
```sql
-- Executed as User A (auth.uid() = USER_A_UUID)
INSERT INTO public.tests (project_id, name, test_ir)
VALUES ('PROJECT_B_UUID', 'Malicious Test', '{}'::jsonb);
-- Verified: Raises exception: new row violates row-level security policy for table "tests".
```

---

## 5. Security Certification Sign-off

- [x] All 10 security test scenarios defined.
- [x] Zero `USING (true)` permissive policies on user data tables.
- [x] Cascading foreign keys verified.
- [x] Auto-profile creation trigger verified (`handle_new_user()`).
