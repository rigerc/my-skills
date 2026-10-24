# Verification, failures, performance and migration

## Verification ladder

1. Reproduce the observed failure before modifying behavior when feasible.
2. Run the smallest relevant `vitest run path/to/file.test.ts`, or use a precise `-t` test name filter.
3. Re-run the containing suite without focusing or skipping tests.
4. Run project-standard CI test script, plus typecheck/lint/build when the change requires them. TypeScript transform alone does **not** typecheck tests.
5. Optionally measure coverage with an installed matching provider. Inspect untested branches instead of claiming completeness from one percentage.
6. Report exactly what was executed and whether it passed, failed, or could not be run.

Use `npx vitest --help` to inspect flags for the installed version. Tests in different files are generally parallel/isolated; same-file tests are sequential unless concurrency is requested. Parallel or concurrency bugs may be due to shared resources, flaky timers, tests mutating fixtures, or dependencies with global state.

## Triage by symptom

| Symptom | First checks |
| --- | --- |
| No tests found | Filename `.test.` / `.spec.`, `include`/`exclude`, workspace root, active project filter |
| Import/transform failure | Existing Vite plugin/alias, TypeScript path mapping, ESM/CJS package boundary, missing peer dependency |
| DOM APIs missing | `environment: 'jsdom'` / `happy-dom` and installed environment package; consider real Browser Mode for actual browser behavior |
| Browser tests don't run | Provider installed, browser `instances` configured, browser binaries installed, file assigned to browser project |
| Mock doesn't take effect | `vi.mock` hoisting, module import order, module internal self-calls, `vi.doMock` and dynamic imports |
| Spying on module export fails in browser | Browser native ESM namespaces are sealed; use supported `vi.mock` approach |
| Flaky tests | Unawaited promises, wall-clock time, network, shared mutable fixtures, parallel collisions, incomplete cleanup |
| Coverage package failure | Match coverage provider to installed Vitest version, `v8` vs `istanbul`, compatible runtime |
| Passing tests but TS errors | Vite transpilation doesn't typecheck; run `tsc` or `vitest typecheck` where supported |

## Vitest 5-specific checks (2026)

- Requires Node >=22.12.0 and Vite >=6.4.0 according to the current guide (verify exact package support range); Yarn installs Vite separately.
- `clearMocks` is now enabled by default, clearing invocation history before each test without resetting implementations.
- `vi.mock`, `vi.unmock`, and `vi.hoisted` must be at module top level; `vi.doMock` and `vi.doUnmock` remain dynamic.
- Inline `test.projects` inherit root config by default in Vitest 5; check for unexpected plugin or setup-file inheritance.
- Some CLI name matching, benchmarking, and Browser Mode semantics changed between versions: consult the migration guide instead of assuming 4.x behavior.

Migration guide: https://vitest.dev/guide/migration
CLI guide: https://vitest.dev/guide/cli
Debugging guide: https://vitest.dev/guide/debugging
