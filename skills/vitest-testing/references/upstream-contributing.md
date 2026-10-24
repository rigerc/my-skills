# Working inside github.com/vitest-dev/vitest (the Vitest source repository)

**This is a special mode.** These instructions apply only if the checkout itself is `vitest-dev/vitest`, not to unrelated projects testing with the Vitest framework. Re-read the current upstream `AGENTS.md`, `AI_POLICY.md`, and `CONTRIBUTING.md` before making changes: repository policy can evolve.

Sources:
- https://github.com/vitest-dev/vitest/blob/main/AGENTS.md
- https://github.com/vitest-dev/vitest/blob/main/AI_POLICY.md
- https://github.com/vitest-dev/vitest/blob/main/CONTRIBUTING.md

## Contribution and communication constraints

- The repo's agent guide forbids posting PRs, issues, or comments without an explicit manual approval by the human operator. Never present auto-generated text as a human-authored maintainer/contributor statement; do not post on the operator's behalf without the required review.
- The AI contribution policy allows AI assistance for code/exploration but requires contributors to understand what they submit and to write public discussions in their own voice.
- The pull-request policy restricts who may submit PRs and which issues qualify. Read the latest eligibility rules before attempting a PR.

## Repo-specific development

- This is a pnpm workspace monorepo (not a typical app consuming Vitest). Follow its pinned pnpm version.
- Initialize with `pnpm install`, then `pnpm build`; use `pnpm dev` for watch builds if useful.
- Checks include `pnpm typecheck`, `pnpm lint`, `pnpm lint:fix` and `CI=true pnpm test:ci`.
- Unit test filter: `CI=true pnpm test name-of-test.test.ts` in `test/unit`. For suite-local tests, use the suite's own package scripts.
- **Do not put `--` between `pnpm test` and file filters.** Its agent guide warns this can accidentally run all tests.
- `CI=true pnpm test:browser:playwright` runs browser tests (ensure browser dependencies exist).
- **Upstream test rule: do not mock anything in tests.** This supersedes this skill's generic mocking advice for other projects. Prefer integration-style checks and the provided test utilities.
- Use `runInlineTests` for multi-file fixtures (in `test/test-utils/index.ts`), `runVitest` for programmatic tests, and assert reported outputs/errors. Tests may execute **built** `dist` output: rebuild affected packages after source changes, especially runtime code and `@vitest/mocker`.
- Never mutate committed test fixtures in tests that run in parallel. Remove accidental `.only` tests. Prefer inline snapshots for relevant error output per repo convention.
- Before committing, run project-standard lint/typecheck, targeted tests and the applicable builds. Docs changes may require a full build before `pnpm docs:build` and updates to the maintained sidebar or generated CLI docs.

Treat repo-local guidelines as authoritative; this page is a dated operational summary, not a replacement for checking the source files.
