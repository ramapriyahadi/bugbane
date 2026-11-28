# 🐞 bugbane

The bane of bugs — agent skills for QA engineers.

> **Status:** early — skills are being added one PR at a time.

## Layout

- `skills/core/` — tool-agnostic QA skills (test case design, formatting, review, estimation, gap analysis)
- `skills/manual/` — manual QA workflows (UI test identifiers, design annotation, test run review)
- `skills/katalon/` — Katalon Studio automation & CI/CD
- `skills/playwright/` — Playwright automation
- `skills/appium/` — Appium mobile automation
- `skills/ops/` — QA operations (release health, reminders, subtasks, velocity)
- `skills/meta/` — agent-team orchestration and skill management

## Skills

| Skill | Folder | What it does |
|---|---|---|
| [write-ui-test-cases](skills/core/write-ui-test-cases/SKILL.md) | core | Write BDD manual UI test cases grounded in design/spec, with reuse audit and precondition chaining |

_Skills are added one PR at a time._

## Install

```bash
npx skills add ramapriyahadi/bugbane
npx skills add ramapriyahadi/bugbane --skill <name>
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for layout, naming, versioning, and generic content rules.

## License

MIT
