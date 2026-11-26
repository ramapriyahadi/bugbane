# Contributing to bugbane

Thank you for contributing to **bugbane**. Every skill in this repository is generic, English-only, and ready to use across coding agents.

## Layout

Skills live under `skills/<folder>/<name>/SKILL.md`, with optional `references/`, `templates/`, and `scripts/` subdirectories.

Allowed `<folder>` values:

- `core/` — tool-agnostic QA skills (test case writing, review, requirement clarification, estimation, automation planning)
- `manual/` — manual QA workflows (UI test identifiers, design annotation, test run review)
- `katalon/` — Katalon Studio authoring, code review, CI/CD, and test case maintenance
- `playwright/` — Playwright test automation
- `appium/` — Appium mobile test automation
- `ops/` — QA operations (release health, test run reminders, subtasks, velocity reporting)
- `meta/` — agent-team orchestration and bugbane skill management

## Naming

- Use **verb-first kebab-case** (for example, `write-ui-test-cases`, `review-test-suite`).
- Add a **tool prefix** only for tool-specific skills (for example, `katalon-review-mr`, `playwright-fix-flaky`).
- Maximum length: **64 characters**.
- The skill folder name **must** match the `name` field in `SKILL.md` frontmatter.

## Versioning

Every skill declares `metadata.version` using semantic versioning (`MAJOR.MINOR.PATCH`). New skills start at `0.1.0`.

- **PATCH** (`0.1.x`): wording fixes, typos, clarifications.
- **MINOR** (`0.x.0`): new capability, section, or reference.
- **MAJOR** (`x.0.0`): changed behavior or output contract.

Any change to a skill's files must bump `metadata.version`. CI enforces this against the base branch.

## Generic Content Rules

- **English only.** Both the skill instructions and the default output must be in English.
- **No private or company-specific content.** Never include company, product, client, or people names, internal hostnames, private repo names, or internal ticket keys.
- **Tool-agnostic by default.** Core skills must work from plain text input (requirements, diffs, test cases). External integrations (Jira, test management tools, CI) belong in an optional `## Optional integrations` section written as *"If `<tool>` is available..."*.

## Adding a Skill

1. Create a branch from `main` using the structural branch naming convention (`skill/<name>`).
2. Copy `templates/SKILL.md` to `skills/<folder>/<name>/SKILL.md`.
3. Add `"./skills/<folder>/<name>"` to the matching `bugbane-<folder>` plugin in `.claude-plugin/marketplace.json`.
4. Add a row to the **Skills** table in `README.md`.
5. Run the validator locally:

```bash
python3 scripts/validate_skills.py --base origin/main
```

## Branching & Pull Requests

**bugbane** uses a **trunk-based branching model** with protected `main` and short-lived topic branches:

- **`main`** is protected: direct pushes, force-pushes, and branch deletion are blocked. All changes must go through a Pull Request with the `validate` CI check passing and review conversations resolved. Merged branches are automatically deleted.
- **Topic branches** must use one of the enforced structural prefixes in lowercase kebab-case (`<prefix>/<kebab-case-topic>`):
  - `skill/<skill-name>` — adding or updating a skill (for example, `skill/write-ui-test-cases`)
  - `feat/<topic>` — repository features, tooling, or marketplace capabilities
  - `fix/<topic>` — bug fixes in skills, scripts, or templates
  - `chore/<topic>` — maintenance, CI/CD, or configuration updates
  - `docs/<topic>` — documentation updates (`README.md`, `CONTRIBUTING.md`)
- Branches outside `main` and the approved prefixes (`skill/*`, `feat/*`, `fix/*`, `chore/*`, `docs/*`) are rejected by GitHub repository rulesets and CI.

## PR Checklist

- [ ] Branch name follows `<prefix>/<kebab-case-topic>` (`skill/`, `feat/`, `fix/`, `chore/`, or `docs/`).
- [ ] Skill lives at `skills/<folder>/<name>/SKILL.md` with an allowed `<folder>`.
- [ ] `name` is verb-first kebab-case, ≤ 64 chars, and matches the folder name.
- [ ] `description` is ≤ 1024 chars and contains no `<` or `>`.
- [ ] `metadata.version` is valid semver (`0.1.0` for new skills, bumped for edits).
- [ ] Content is English-only, generic, and free of company/internal references.
- [ ] External tools are in `## Optional integrations` (for core/manual/ops skills).
- [ ] `.claude-plugin/marketplace.json` and `README.md` are updated.
- [ ] `python3 scripts/validate_skills.py --base origin/main` passes with 0 errors.
