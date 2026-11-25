# Test Management Integration Reference

Tool-specific guidance for `write-ui-test-cases` when connected to a test management tool.

## Katalon TestOps (worked example)

### Searching for existing cases

- `find_test_cases`: use `COMMON` filters on `name` or `path` across multiple vocabularies (feature name, screen name, module).
- `find_test_cases_by_requirement`: find cases already linked to the requirement/ticket.
- `find_test_folders`: locate the target platform-specific feature folder (never a generic sprint folder).

### Reading steps & retrieval retry

- Call `read_test_cases` with `content_type: "FLOW"`.
- If a bulk `FLOW` or `BOTH` read omits a case, retry that ID individually with `FLOW`, then `BOTH`, then `NONE` for metadata (`SCRIPT` only when script evidence is relevant).
- A step row with `name: ""` and a populated `expectedResult` can be a TestOps serialization artifact; verify in the rendered UI before flagging as malformed BDD.

### Call Test Case step payload

```json
{
  "name": "GIVEN User is logged in as Customer",
  "context": {
    "expectedResult": "User is on the Home page",
    "data": ""
  },
  "action": {
    "type": "call",
    "test_case_id": 123456
  }
}
```

- Add `"version": <n>` inside `action` to pin a specific version; omit it to always call the latest version.
- `UPDATE_CONTENT` replaces the entire step list. Always re-supply existing Call Test Case steps with their `action` object, or they will be silently dropped.

### Status restoration after edits

Any update (`RENAME`, `UPDATE_DESCRIPTION`, `UPDATE_PRECONDITION`, `UPDATE_CONTENT`, `UPDATE_AUTOMATION_STATUS`) resets `status` to `DRAFT`:

1. Read the case back to confirm `FLOW` steps are intact.
2. Apply and verify `automationStatus: TO_BE_ASSESSED` first.
3. Restore `status: PUBLISHED` **last**.
4. Re-read both status fields and re-read the target suite's `testCases` collection to confirm membership.

## Other test management tools

For tools like **TestRail**, **Xray**, or **Zephyr**, map the same concepts:

- **Call Test Case** → shared steps, called test cases, or precondition links.
- **Suite membership** → verify the case is attached to the target test plan/suite/cycle after creation.
- **Status restoration** → re-check workflow/approval status after bulk or API updates.
