---
name: write-ui-test-cases
description: Write manual UI test cases in BDD format (GIVEN/WHEN/THEN/AND) from a requirement, user story, bug, or design. Grounds every UI element in a design or spec, audits existing cases for reuse before creating new ones, chains reusable preconditions, and outputs reviewable cases with titles, priorities, steps, expected results, and test data. Use when asked to write, draft, generate, or format UI test cases or a test suite for a story or bug.
metadata:
  version: 0.1.0
---

# Write UI Test Cases

Author manual UI test cases in BDD format (`GIVEN` / `WHEN` / `THEN` / `AND`) grounded in requirements and UI designs, with reuse-first auditing and precondition chaining.

## When to use

- Writing new manual UI test cases for a user story, requirement, operational task, or bug fix.
- Expanding or reviewing a UI test suite for direct entry, negative, boundary, or regression coverage.
- Converting requirements, design screens, or acceptance criteria into structured, reviewable BDD test cases.

## Input template

When starting from a prompt, gather:

- **Feature / Page / Flow**: [feature, page, or user flow]
- **Context**: [brief business context, screen name, or scenario]
- **Existing reference / candidate precondition**: [precondition test case ID or URL, if any]

## Step 0a: Get the full requirement context

When the source is an issue tracker ticket (for example, Jira), never fetch only the default fields. Default field sets often omit comments, attachments, subtasks, and linked issues that carry requirement-defining details (such as UI/UX interaction rules posted in a comment).

- Request full fields (e.g., `summary`, `description`, `comment`, `attachment`, `issuelinks`, `subtasks`, or `*all`).
- **Read every comment**: design or UX input relayed in comments is authoritative until contradicted.
- **Note any attachments** (screenshots, design files) in `Context Sources`, and follow any design tool links (e.g., Figma) via the UI verification rule below.
- **Read every subtask summary and status**: a completed UI or implementation subtask is a direct build-status signal—do not let an empty code search silently override it; if they disagree, report the discrepancy and investigate.
- **Read every linked issue summary** (and full linked tickets when materially relevant) for shared scope or constraints.

## Step 0: Ground in project context

Never write or propose a test case from a ticket summary alone. Read the available project requirement, design, and technical context first, and state which sources you used.

- **Prefer live/current project docs over a stale uploaded snapshot**; if you must fall back to a snapshot, state so explicitly.
- Read in this order when available:
  1. **Requirement / behavior spec** (module specs, feature `.feature` / `.md` files).
  2. **Baseline / blueprint catalog** (authoritative product spec statements).
  3. **Technical / API contract** (endpoints, payloads, validation rules, sync behavior).
  4. **Design** (UI specs, screen flows, screenshots, or live design files). Take UI labels, field names, states, and error copy from the design instead of inventing wording.
  5. **Grooming / open questions** (decisions already made and open questions).
- **Source precedence**: if the project defines a source precedence, follow it. A newer document does not automatically override an established baseline, and silence in a newer document is not removal of scope. Log conflicts explicitly and ask the product owner rather than picking silently.
- If a relevant spec, technical, or design file is missing or does not cover the ticket, say so explicitly instead of guessing.

## UI / feature existence verification

**Why this exists**: AI-assisted test authoring can invent plausible-sounding buttons, screens, or features that do not exist in the product.

**Rule**: every specific UI noun in a test case—a button label, screen/page name, menu item, field name, status/badge label, or named feature/flow—must trace to at least one of:

1. An actual design screen/frame (local screenshot or live lookup via a design tool such as Figma).
2. The baseline/blueprint catalog.
3. The requirement or technical specification text, when it explicitly names that UI element.

- **Use a design tool automatically**: when local design docs are missing, stale, or ambiguous and a design link/file is available, look up the live design to confirm the exact label before writing the step, and record this in `Context Sources`.
- **No reference = flag it, never invent it**: if you cannot ground a UI element through any source:
  - Use a clearly marked placeholder: `WHEN User clicks [UNVERIFIED — button name not confirmed in design/spec]`.
  - Set `UI Reference Verified: ⚠️ NO — {specific noun} not found in design/spec/requirement docs, needs PO/designer confirmation`.
  - Ask before finalizing rather than guessing.

## Reuse-first rule

Do not create a new test case until you have checked whether an existing case already covers the scenario. Show the reuse audit in your output.

1. **Search first** (if a test management tool is available): search by feature name, alternative-language terms, module, screen name, and linked requirement.
2. **Read the candidates**: inspect the actual steps/flow of every plausible hit. Never judge coverage from the title alone.
3. **Classify every scenario into exactly one of**:
   - `REUSE` — an existing case already covers it. Create nothing; reference that case's ID/URL.
   - `EXTEND` — an existing case is close. Propose updating that case instead of creating a new one.
   - `CALL` — the scenario is new, but part of its flow (login, setup, navigation, precondition) already exists. Create the new case and call the existing flow as a precondition step.
   - `NEW` — genuinely uncovered, with nothing reusable.
4. **Report the reuse audit before generating cases**:

   | Scenario | Decision | Existing Test Case | Reason |
   |---|---|---|---|
   | ... | REUSE / EXTEND / CALL / NEW | [ID](URL) or — | ... |

5. If a search returns nothing, state which queries you ran.
6. Duplicating an existing case is a defect. When unsure between `NEW` and `EXTEND`, ask instead of creating.

### Retrieval-limitation retry rule

An empty or incomplete step-read response is a retrieval result, not proof that a test case has no steps:

1. When a bulk read omits a case, retry reading that ID individually.
2. If the individual read is empty, try alternate content/metadata modes.
3. Compare with suite membership and exact case ID/name. Report unreadable cases as `Steps unreadable`, not as empty or malformed.
4. Do not update, duplicate, or remove an unreadable case speculatively; record the attempted retrieval modes.
5. A later successful individual read supersedes an earlier bulk omission and must be used.

### Direct coverage gap gate

Reuse is required, but a reused post-trigger case does not replace coverage of the feature's entry flow:

1. Map each requirement behavior to an existing case after reading its steps, not only its title.
2. Keep a reused post-trigger case when it covers the behavior, but add or extend a direct entry case when the suite otherwise lacks the user-facing entry point, selection/validation rules, or primary error branch.
3. For sync or batch flows, explicitly check the entry screen/modal, allowed and disallowed selections, maximum quantity rules, status progression, and documented error responses. Mark each as `REUSE`, `EXTEND`, `CALL`, or `NEW`.
4. Any new data-state prerequisite must either call an existing setup case or use a focused reusable setup case with an explicit approved fixture in `Test Data`. Never hide an unknown provisioning method in a plain-text step.
5. Do not pad a suite with unrelated regression cases; every case must map to a ticket behavior or a required release-safety check.

## Reusable precondition steps (Call Test Case)

When a precondition or sub-flow already exists as a test case, invoke it as a structured **Call Test Case** step rather than duplicating its steps inline or pasting a bare URL.

- Fill in both the human-readable `GIVEN` step label and expected result so a manual tester can execute the case without opening the callee.
- Prefer calling small, focused, reusable cases (login, create record, open screen, setup data) over duplicating steps inline.
- When updating a case via a full-replace API, always re-supply existing Call Test Case steps; omitting them silently drops the call.
- Only call a test case you have verified exists. Never invent a test case ID.
- A precondition case does not have to be from the same platform; if a cross-platform precondition fits, reference it for review.
- Legacy raw URLs, ID-only references, or small self-contained inline `GIVEN` steps are acceptable when the state is clear; do not rewrite them solely for uniformity.
- If a structured call cannot be used for a new dependency, use a raw URL (never Markdown link syntax) and record the limitation.

### True chaining within a batch

When generating a batch of related cases that form sequential stages of one scenario (e.g., input blocked → save fails → restriction lifts → action succeeds), do not give every case the same generic login/setup precondition:

- Chain each case's `GIVEN` to call the **immediately preceding stage** in the sequence.
- If the predecessor is a new case in the same batch, create cases in dependency order (or hold the chain in draft and wire IDs after creation).
- If the predecessor already exists as a published case, call it directly.
- Fall back to a bare login/setup precondition only for fresh entry points with no predecessor scenario.
- State the resulting chains explicitly in your output (e.g., `[existing TC 1001] → [new case A] → [new case B]`).
- If the feature is not implemented in the frontend yet (verified from code, not assumed), state that plainly and base the chain on acceptance criteria and QA judgment.

### Reusable setup case for a required data state

When a case needs a specific data state after authentication (for example, an account with no active notifications), do not leave it as an unchained plain-text `AND` step after login:

1. Search for an existing setup case and inspect candidates (`REUSE` / `EXTEND` / `CALL` / `NEW`).
2. If none exists, create a focused reusable setup case in the same feature folder. Name it after the state and reusable outcome, not the ticket key.
3. Document the approved fixture, seed, or manual preparation method in `Test Data`. Never invent backend operations; if provisioning is unknown, flag it for confirmation.
4. In the feature case, call the setup case as a structured `GIVEN` Call Test Case before calling login or opening the target screen. Keep login as a separate reusable step when authentication is required.
5. Include the setup case in the story/requirement suite when needed for execution, and verify both case IDs are present in the suite.

## Generality rule (titles must be reusable)

A test case is a regression asset that outlives its originating ticket. Its **Title** (`Scenario` and `ExpectedResult` segments) must describe a general, reusable check—never a one-off reference to a ticket, migration, or technical change.

- **Bad**: `MOB-Order History-View Order List After Read Replica Migration-Orders Displayed Correctly`
- **Good**: `MOB-Order History-View Order List-Orders Displayed Correctly`
- Ticket or technical-change context may go in **Description** when helpful, but never hardcode the ticket key in the title, description, or steps. Keep traceability through requirement linkage and the test suite.
- **Exception — genuinely one-off scenarios** (one-time data migration/backfill, bug-reproduction pinned to a fixed defect, cutover/rollback drill): a specific title is valid; state why in `Reuse Decision` / `Context Sources`.
- Before finalizing titles, re-read them as if the originating ticket no longer existed.

## Project terminology & glossary

- Use familiar, project-approved wording in metadata (`Test Case Name`, `Description`, `Pre-condition`) and in `Test Steps`, `Expected Results`, and `Test Data`.
- Keep terms consistent across the case; prefer the official UI/product label over synonyms or shorthand.
- If a term is unfamiliar, inconsistent, or undefined in authoritative sources, flag `⚠️ WARNING (project terminology/glossary)` and propose the standard term. Ask for confirmation only when sources disagree or no approved term can be established.
- Apply this check separately from UI Reference Verification.

## Authoring requirements

- **Language**: generate all content in **English** (`Test Case Name`, `Description`, `Pre-condition`, `Test Steps`, `Expected Results`, `Test Data`).
- **Format**: use BDD keywords (`GIVEN`, `WHEN`, `THEN`, `AND`) with clear UI action language.
- **Scope**: keep each test case as small and focused as possible; include edge cases and negative scenarios.
- **Priority**: decide priority independently based on failure severity and likelihood of blocking the user journey (do not blindly copy the parent ticket's priority):
  - `HIGH`: core happy paths, transaction completions, primary entry points.
  - `MEDIUM` / `LOW`: cosmetic UI, field validations, negative cases, non-blocking alternative flows.
- **Review before creation**: present all drafted test cases for user review before creating them in any test management tool.
- **Folder & defaults** (when using a test management tool): locate the matching feature folder (or propose creating one); set Automation Status to `To Be Assessed` and Status to `Published` once the user approves the draft.
- Ask questions whenever requirements, UI labels, or data states are ambiguous.

## Title format

`Platform-PageName-Scenario-ExpectedResult`

- No spaces around dashes (`-`), but keep spaces between words.
- Use a 3-letter platform prefix: `MOB` (mobile), `WEB` (web), `E2E` (hybrid/cross-platform).

## Test suite creation & naming

When authoring cases for a story, requirement, or bug, create one corresponding Test Suite:

- **Format**: `Platform-Type-TicketKey-RequirementSummary`
- **Example**: `WEB-FEATURE-SHOP-97-Customer can filter order history by status`
- **Platform**: `MOB`, `WEB`, or `E2E`.
- **Type**: `BUG` for bug tickets; `FEATURE` for stories or requirements.
- No spaces around the dashes separating segments (spaces within words in the summary are fine).

## BDD column placement & folder gate

- **Test Steps** may contain only `GIVEN` preconditions and `WHEN`/`AND` actions or triggers. Never put `THEN` assertions or negative checks in Test Steps.
- **Expected Results** must hold every assertion, prefixed with `THEN` for the first outcome and `AND` for additional outcomes from the same action. Reject any row whose step starts with `THEN` or whose Expected Result is empty for an assertion step.
- Place cases in a **platform-specific feature folder**, never a generic sprint folder. If no suitable feature folder exists, propose one and ask for confirmation.

## Suite membership & bug coverage gate

Before considering a generated suite ready, verify that the cases are actually associated with the suite—do not rely on suite name or `Published` status alone.

- Re-read the target suite and confirm every case ID is present. Report:
  - `Suite Membership: ✅ VERIFIED — [case IDs]` or
  - `⚠️ ACTION REQUIRED — suite returned no associated test cases`
- **Bug suites**: include at least one focused regression case proving the old defect is fixed and the intended behavior is shown. State the exact expected value/unit (e.g., value displays `%` and the obsolete unit is not shown) rather than a vague "displays correctly".
- Resolve the active sprint and target folder live; never assume a historical sprint folder.

## Post-creation self-review gate

After the user approves the draft and cases/suites are created or updated:

1. Read back every created or updated case's steps (retrying individually if a bulk read omits them) and read back the target suite to verify steps, status, automation status, folder path, and suite membership.
2. Run `review-test-suite` (if installed; otherwise run the same checklist inline) to verify: requirement coverage, direct entry/negative/boundary scenarios, BDD column placement, reusable setup chaining, true chaining, exact UI copy, generality, duplication, priority, and folder/sprint alignment.
3. Present a compact review summary in chat before any correction or further update. If a finding needs a product, design, data, or ownership decision, show `Confirmation Needed` and stop.
4. Apply corrections only when explicitly authorized, then re-read affected steps and suite membership.

### Post-update status restoration

Some test management tools reset `Published` cases to `Draft` on any edit. After every rename, description, precondition, or step update:

1. Read the case back and confirm all steps were preserved.
2. Set `Automation Status` first, then restore `Status: Published` **last** (so metadata updates do not re-reset publication status).
3. Re-read both status fields and confirm steps are intact.
4. Re-read the target suite to confirm membership.

### Legacy representation guard

Distinguish authored defects from tool serialization differences:

- For legacy cases, a raw URL, ID-only reference, or small inline `GIVEN` is acceptable when clear; do not flag or rewrite solely for uniformity.
- For new or materially updated cases, use structured Call Test Case steps for reusable prerequisites, data-state setups, and multi-step sub-flows.
- A step row with an empty action name and a populated expected result may be a tool serialization artifact; verify in the rendered UI before flagging it as malformed BDD.
- Report unreadable cases separately from authored findings.

### Alignment contract with `review-test-suite`

- Build a requirement-to-case/step coverage map before claiming completeness; a title match is never enough.
- Apply the direct-coverage gate: a reused post-trigger case does not replace a direct entry, validation, negative, or boundary case.
- Classify each proposed case as `FEATURE-SCOPE` or `HELPER-ONLY`, keeping helper cases in the suite only when needed for execution. Audit duplicates by action, state, material data/boundary, and oracle—not by similar names.
- Keep review output compact and fail-focused, including Requirements Coverage Validation and a merged **Gap Analysis, Detailed Findings & Proposed Corrections** section, using decisions: `✅ READY FOR PASS FLOW`, `✅ READY FOR PASS FLOW (REVIEWER-FIXED FINDINGS)`, `⚠️ AWAITING FIX AUTHORIZATION`, or `❌ AUTHOR ACTION REQUIRED`.

> Tracker pass-flow actions (comments, transitions, worklogs) are out of scope for this skill.

## Output format

```markdown
Test Case Name: <Platform-PageName-Scenario-ExpectedResult>
Priority: <HIGH | MEDIUM | LOW>
Pre-condition: <Name and URL/ID of called test case, or empty>
Reuse Decision: <REUSE / EXTEND / CALL / NEW — with referenced case if any>
Chain: <e.g., "→ TC 1001 (existing)" or "→ [prior case in this batch]" or "— entry point, no predecessor scenario">
Context Sources: <files, design links, or specs read>
UI Reference Verified: <✅ YES — grounded in [source] | ⚠️ NO — {noun} unverified, needs PO/designer confirmation>
Description: <concise summary of what the case verifies>
Test Steps:
| Step | Expected Result | Test Data |
|---|---|---|
| GIVEN <precondition label> — Call Test Case → <existing ID> | | <if needed> |
| WHEN <action> | THEN <expected condition> | <if needed> |
| AND <next action> | THEN <expected condition> | <if needed> |
| AND Check <verification> | THEN <additional expected condition> | <if needed> |
```

## Optional: requirement doc sync

If a writable requirements folder or repository is available and authoring surfaces a detail not yet captured (a UI flow/field/state confirmed from design, or a clarified edge case):

- Edit only the consulted files with small, reviewable diffs (prefer appending a short dated note).
- Never resolve a source-precedence conflict by editing the doc—log it and ask the product owner.
- Make no edit if nothing new surfaced.
- Whenever a requirement file is updated, end your response with a short `📄 Requirement Docs Updated` block listing the file(s) and a one-line summary.

## Optional integrations

- **Test management tool** (e.g., Katalon TestOps, TestRail, Xray, Zephyr): see [references/test-management-integration.md](references/test-management-integration.md) for search, Call Test Case payloads, status restoration, and suite membership checks.
- **Issue tracker** (e.g., Jira): fetch full fields per Step 0a.
- **Design tool** (e.g., Figma): verify exact UI labels per UI / feature existence verification.

## Response keywords

- `LGTM` — proceed to create the approved test cases in the target test management tool.

## Quality checklist

- [ ] Full requirement context (comments, attachments, subtasks, linked issues) read.
- [ ] Every UI noun grounded in design, baseline, or spec (or flagged `[UNVERIFIED]`).
- [ ] Reuse-first audit table included before proposing new cases.
- [ ] Titles follow `Platform-PageName-Scenario-ExpectedResult` and are ticket-agnostic.
- [ ] Test Steps contain only `GIVEN`/`WHEN`/`AND`; Expected Results start with `THEN`.
- [ ] Priority reflects user-journey impact, not blindly copied from the ticket.
