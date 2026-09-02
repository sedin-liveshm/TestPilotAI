# ADR: Authenticated Runner Placeholder

## Status

Proposed

## Context

To run automation tests against secured parts of the application (e.g., dashboards), the automation runner needs to perform actions within an authenticated session. Since Supabase Auth and Login UI are currently being implemented by other developers (Developer 3 and Developer 1), we need a placeholder architecture.

This runner provides a foundation that can receive an authenticated session state and execute Test IR actions, decoupling test execution from the actual Supabase authentication flow.

## Decision

We have implemented an **Authenticated Runner Abstraction**.

1. **`TestRunner` and `AuthenticatedRunner`**:
   The `AuthenticatedRunner` consumes Playwright's `Browser` object and accepts an optional `storageStatePath` containing the authenticated session (cookies and local storage).

2. **Integration Point**:
   The runner expects authentication to be resolved *before* it runs the test. Developer 3's authentication flow will eventually output a Playwright `storageState.json` file. This file will be injected into `AuthenticatedRunnerOptions`.

   ```text
   Supabase Auth / Login Flow 
           ↓
   generates storage-state.json
           ↓
   Authenticated Runner (injects storageState)
           ↓
   Test IR Execution
   ```

3. **No Direct Auth Implementation**:
   We deliberately avoid hard-coding passwords, API tokens, or Supabase credentials within the runner itself. The runner does not make database queries or attempt to log the user in via UI.

## Execution

The runner iterates over the `TestIR` actions and maps them directly to Playwright commands (e.g., `navigate`, `click`, `fill`, `assertVisible`).

If `storageStatePath` is missing, the runner will log a warning and proceed as an unauthenticated runner. This is useful for public pages or tests that verify unauthorized access handling.

## Non-goals

* **Supabase Authentication**: Handled by Developer 3.
* **Login/Logout UI Testing**: Handled by Developer 1.
* **Test Reporting Engine**: The runner returns a simple `RunnerResult` for basic assertions. Complex reporting is deferred.

## Security Considerations

* **Git Tracking**: We have explicitly ignored `.env`, `playwright/.auth/`, `storage-state.json`, and `auth-state.json` in `.gitignore` to prevent sensitive credentials or session cookies from leaking into source control.
* **Secrets**: No secrets are stored in the runner code.

## Future Evolution

Once Developer 3 completes the Supabase Auth implementation, an outer execution script will:
1. Log in via API (using a test user credential supplied via a secure environment variable).
2. Save the session to `playwright/.auth/storage-state.json`.
3. Invoke this `AuthenticatedRunner` passing the saved state file.
