# ADR: Test IR v1

## Status

Proposed

## Context

The project requires an automation system to run end-to-end tests across the application. To decouple test definitions from the Playwright runner's exact implementation details, we need a stable architecture contract. This contract will be defined as a "Test Intermediate Representation" (Test IR). 

By establishing an IR, test definition tools (like test generators or manual UI tools) can produce JSON that describes *what* to do, while the Playwright engine focuses entirely on *how* to do it.

## Decision

We are introducing **Test IR v1**, a JSON-serializable schema and TypeScript types designed as a strongly typed, validated contract representing browser automation actions. 

We will use **Zod** as the validation library because:
- It allows us to define the runtime schema and compile-time TypeScript types from a single source of truth.
- It provides a robust, developer-friendly way to validate incoming JSON (with discriminated unions mapping cleanly to our actions and locator strategies).

## Goals

* **Stable automation contract:** A clear API for any tool generating tests.
* **Separation of concerns:** Strict decoupling between test definition (IR) and Playwright execution.
* **Runtime validation:** The system must reject invalid test structures early with clear errors.
* **Extensibility:** A discriminated-union action model allows easily adding new actions.
* **Type safety:** Strong TS inference guarantees valid types for the executor.

## Non-goals

* Complete 1:1 mapping of all Playwright features (we will only support what we need).
* Implementation of the execution engine itself (this ADR only establishes the contract).
* Test IR backward compatibility with v2 (since this is v1, we focus on establishing the baseline).

## Test IR structure

### Test Object
- `version` (literal `"1"`): Required version marker.
- `id` (string): Unique identifier for the test.
- `name` (string): Human-readable name.
- `description` (string, optional): Extra context for the test.
- `actions` (array of `TestAction`): Must contain at least one action.

### Actions
Each action is defined as an object with a `type` discriminator. Supported actions:
- `navigate` (url: string)
- `click` (target: LocatorTarget)
- `fill` (target: LocatorTarget, value: string)
- `select` (target: LocatorTarget, value: string)
- `check` (target: LocatorTarget)
- `uncheck` (target: LocatorTarget)
- `press` (target?: LocatorTarget, key: string)
- `wait` (durationMs: number)
- `assertText` (target: LocatorTarget, text: string)
- `assertVisible` (target: LocatorTarget)
- `assertUrl` (url: string)
- `screenshot` (name?: string)

### Locator Strategies
Instead of hardcoding Playwright syntax, locators are abstracted:
- `role` (role: string, name?: string)
- `text` (value: string)
- `label` (value: string)
- `placeholder` (value: string)
- `testId` (value: string)
- `css` (value: string)

## Validation rules

* `version` must be strictly `"1"`.
* The test ID, name, and URL string fields cannot be empty (`min(1)`).
* `actions` must have at least one element.
* Each action's `type` field acts as a discriminated union key and must be a known action.
* Locator target strategy must be a known strategy and contain the necessary fields (e.g., `text` requires `value`).

## Example

```json
{
  "version": "1",
  "id": "login-smoke",
  "name": "Login smoke test",
  "actions": [
    { "type": "navigate", "url": "/login" },
    {
      "type": "fill",
      "target": { "strategy": "label", "value": "Email" },
      "value": "user@example.com"
    },
    {
      "type": "click",
      "target": { "strategy": "role", "role": "button", "name": "Login" }
    },
    {
      "type": "assertVisible",
      "target": { "strategy": "role", "role": "heading", "name": "Dashboard" }
    }
  ]
}
```

## Invalid examples

**Missing Version:**
```json
{
  "id": "bad-test",
  "name": "Bad",
  "actions": [{ "type": "navigate", "url": "/" }]
}
```

**Invalid Locator Strategy:**
```json
{
  "version": "1",
  "id": "bad-test",
  "name": "Bad",
  "actions": [
    {
      "type": "click",
      "target": { "strategy": "xpath", "value": "//div" }
    }
  ]
}
```
*(Rejected because "xpath" is not in the allowed strategies list).*

## Future considerations

- **More actions:** hover, dragAndDrop, fileUpload, etc.
- **Complex Assertions:** RegExp matching for text, count assertions.
- **Data-driven tests:** Variables and environment references in strings.
