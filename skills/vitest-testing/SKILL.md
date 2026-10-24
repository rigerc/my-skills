---
name: vitest-testing
description: Write, configure, debug, migrate, and review JavaScript/TypeScript tests with Vitest and Vite. Use for Vitest unit tests, async assertions, mocks/spies, fake timers, DOM or Browser Mode tests, coverage, CI, workspaces, flaky tests, Jest migration, or contributions to vitest-dev/vitest.
license: MIT
metadata:
  source: https://github.com/vitest-dev/vitest
  checked: "2026-10-22"
---

# Vitest testing

Use this skill to produce **small, deterministic tests with verified outcomes**. Follow the target project's conventions rather than imposing a fresh setup. Reference the project's installed Vitest version before choosing an API; the current upstream development line may differ from the released version.

## First identify which repository you are in

1. Inspect `package.json`, package manager lockfile, Node/Vite/Vitest versions, `vite.config.*`, `vitest.config.*`, `tsconfig*.json`, test scripts, nearby `*.test.*` / `*.spec.*` files, and relevant `AGENTS.md` or contributor instructions. Never overwrite existing configuration blindly.
2. **Ordinary application/library using Vitest:** follow the workflow below and the `references/` files as needed.
3. **The upstream `vitest-dev/vitest` monorepo itself:** first read [references/upstream-contributing.md](references/upstream-contributing.md). Its testing rules (including no mocks in upstream tests), pnpm commands, and posting/approval policies take precedence over generic examples in this skill.
4. If tests are on an older major release, consult the corresponding versioned documentation. Do not assume Vitest 5-only behavior works with Vitest 4 or earlier.

## Workflow for application/library tests

1. **Determine scope.** Identify the behavior, relevant module/public contract, expected edge cases, and whether the test belongs to unit, integration, DOM, or real-browser coverage. Reproduce a reported bug with a minimal failing assertion where feasible.
2. **Preserve project setup.** Prefer existing Vite plugins, aliases, `setupFiles`, utilities, test naming, and package-manager commands. Use a separate `vitest.config.*` only when necessary; a standalone Vitest config does not automatically inherit settings from an existing `vite.config.*`.
3. **Choose environment.** Default is `node`. Use installed `jsdom` or `happy-dom` for simulated DOM; use **Browser Mode with a browser provider** for real browser behavior. Browser Mode is not a `test.environment` value. See [configuration and browser mode](references/configuration.md).
4. **Write a focused test.** Import `test`, `describe`, `expect`, lifecycle helpers, and `vi` explicitly from `vitest` unless globals are already enabled. Prefer behavior-driven names and assertions of outputs/effects. Cover success, failure, and boundary cases that matter; use `test.for` for similar cases.
5. **Control external dependencies.** Prefer explicit inputs, lightweight fixtures, and dependency injection. For app code that requires stubs, use `vi.fn`/`vi.spyOn` and targeted `vi.mock`; avoid replacing whole modules if a narrow seam suffices. `vi.mock` is hoisted and (in Vitest 5) must appear at module top level. Browser Mode cannot spy on sealed native-ESM namespace exports. See [mocking patterns](references/mocking.md).
6. **Clean up.** Restore spies and globals/timers after tests. Avoid sharing mutable state across tests; prefer isolated setup and temporary directories. In Vitest 5 `clearMocks` defaults to `true`, but that clears call history, **not** mock implementations.
7. **Validate in increasing scope.** Run the changed test file once (`vitest run path/to/file.test.ts`), then the relevant suite, then the full test command when practical. Run coverage/typechecks/lint as appropriate. Never claim a test passed unless its command actually ran successfully. See [verification and troubleshooting](references/troubleshooting.md).
8. **Report concisely.** State which files changed, scenarios covered, commands run and their results, any unrun verification, and residual risks. Avoid adding snapshots for logic that is clearer with explicit assertions. Remove `.only` before finishing.

## Fast usage reference

```sh
# Install into an app using npm; follow the existing package manager instead.
npm install -D vitest

# Development watch mode
npx vitest

# One-shot/CI run
npx vitest run

# Focus a file, or a test name
npx vitest run src/math.test.ts
npx vitest run src/math.test.ts -t 'rejects invalid input'

# Coverage: first install a matching @vitest/coverage-v8 package
npx vitest run --coverage

# All CLI options for the installed version
npx vitest --help
```

For the current Vitest 5 documentation, Node.js >=22.12.0 and Vite >=6.4.0 are required (subject to the installed package's engine/peer constraints). Yarn users must install `vite` explicitly as a peer dependency. Tests are normally discovered via `.test.` or `.spec.` filenames, with `test`/`expect` imported from `vitest`.

## Minimal example

```ts
import { expect, test } from 'vitest'
import { add } from './add'

test.for([
  { a: 1, b: 2, result: 3 },
  { a: -2, b: 2, result: 0 },
])('add($a, $b) returns $result', ({ a, b, result }) => {
  expect(add(a, b)).toBe(result)
})
```

For real projects, match the file-extension and module-resolution conventions already in use. For optional starter files, see `assets/`. These files are **examples**, not replacements for project configuration.

## Reference routing

- Environment, setup, Browser Mode, coverage, workspace projects, CI: [references/configuration.md](references/configuration.md)
- Mock factories, spies, fetch, timers, async behavior, Browser Mode gotchas: [references/mocking.md](references/mocking.md)
- Test-running strategy, flakiness, migration, failure triage: [references/troubleshooting.md](references/troubleshooting.md)
- Making changes **inside the Vitest repository**: [references/upstream-contributing.md](references/upstream-contributing.md)

## Canonical sources

- Repository: https://github.com/vitest-dev/vitest
- Getting started: https://vitest.dev/guide/
- Writing tests: https://vitest.dev/guide/learn/writing-tests
- Mocking: https://vitest.dev/guide/mocking
- Browser Mode: https://vitest.dev/guide/browser/
- Coverage: https://vitest.dev/guide/coverage
- Vitest 5 migration: https://vitest.dev/guide/migration

Check the official docs for changes when answering version-sensitive questions.
