# Vitest Testing — Agent Skill

An original, portable [Agent Skills](https://agentskills.io/specification) package informed by the public [Vitest repository](https://github.com/vitest-dev/vitest) and its official guides. It is not published by or affiliated with the Vitest maintainers.

## Install

Unzip and place the `vitest-testing/` directory in your agent's supported skills directory, for example:

```text
<your-project>/.agents/skills/vitest-testing/SKILL.md
```

For agents that use another skill directory (e.g., `.claude/skills/`), follow that agent's instructions. Keep the full folder, including `references/` and `assets/`, together; installing only `SKILL.md` will break the linked resources. Restart/reload agent skill discovery if necessary.

## Scope

- Vitest configuration, tests, async assertions, mocks, fake timers, coverage and CI
- DOM vs Browser Mode selection; common debugging and migration issues
- Explicit special-case contributor guardrails for the actual Vitest monorepo
- Starter snippets under `assets/` intended for adaptation, not automatic overwrite; `add.ts` and `example.test.ts` form a small runnable pair

## Example prompts

- `Use vitest-testing to add tests for the validateToken function and run the targeted tests.`
- `Use vitest-testing to configure browser tests for this Vite React app.`
- `Use vitest-testing to debug why vi.mock is not intercepting this module.`
- `Use vitest-testing to migrate our test suite from Vitest 4 to 5.`

## Version context

Compiled against Vitest 5-era public docs and default-branch source on **2026-10-22**. Check installed versions and current official documentation before modifying a project; upstream `main` may contain prerelease changes. This skill contains no automatically executing scripts.

## Source links

- https://github.com/vitest-dev/vitest
- https://vitest.dev/guide/
- https://vitest.dev/guide/mocking
- https://vitest.dev/guide/browser/
- https://vitest.dev/guide/coverage
- https://vitest.dev/guide/migration
- https://agentskills.io/specification
