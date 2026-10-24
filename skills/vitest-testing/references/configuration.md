# Configuration, environments, Browser Mode, coverage and CI

## Baseline decisions

- First inspect current `vite.config.*` and `vitest.config.*`. Vitest can read Vite configuration, but a separate `vitest.config.*` takes precedence; explicitly merge or reapply relevant Vite plugins/aliases if needed.
- Keep existing framework plugins for React, Vue, Svelte and other frameworks; do not discard them by adding a standalone test config.
- For Node code, use default `environment: 'node'`. For a simulated DOM, install `jsdom` or `happy-dom` and set `test.environment` accordingly. File-level override: `// @vitest-environment jsdom`.
- In Vitest 5, Node >=22.12.0 and Vite >=6.4.0; check exact `engines` and Vite peer ranges in the installed version. If using Yarn, install `vite` explicitly.
- Prefer explicit named imports from `vitest`; if project enables `globals: true`, ensure TypeScript sees `vitest/globals`.

## Example for a new, simple project

```ts
// vitest.config.ts — adapt rather than overwrite existing config
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/*.{test,spec}.{ts,tsx,js,jsx}'],
  },
})
```

Vitest discovers `.test.` and `.spec.` files by default, so you can usually omit `include`. `setupFiles` can initialize shared test helpers; avoid side effects that leak state.

## Real-browser tests

Use Browser Mode when validating browser APIs, component interactions, or rendering in an actual engine. It is **not** a `jsdom` replacement in the same config switch.

1. For a new project, try `npx vitest init browser`. Otherwise install `@vitest/browser-playwright` (recommended for CI) and a matching Vitest version.
2. Configure a provider plus at least one browser instance:

```ts
import { defineConfig } from 'vitest/config'
import { playwright } from '@vitest/browser-playwright'

export default defineConfig({
  test: {
    browser: {
      enabled: true,
      provider: playwright(),
      instances: [{ browser: 'chromium' }],
      headless: true,
    },
  },
})
```

3. Install required browser binaries using your provider's instructions before CI runs. For separate Node/Browser suites, configure named `test.projects` with non-overlapping file patterns; see https://vitest.dev/guide/projects.
4. Browser Mode's native ESM module namespaces are sealed; `vi.spyOn(moduleNamespace, 'export')` cannot patch them. Prefer `vi.mock('./module', { spy: true })` declared at top level when appropriate.

Docs: https://vitest.dev/guide/browser/

## Coverage

Install a matching-version provider, typically `@vitest/coverage-v8`, and run `vitest run --coverage`. V8 is the default provider; Istanbul is available via `@vitest/coverage-istanbul` for unsupported engines or other requirements. To count unimported source files as uncovered, add `test.coverage.include`, e.g. `['src/**/*.{ts,tsx}']`, and exclude generated files as appropriate. Do not conflate a coverage percentage with behavioral correctness.

Docs: https://vitest.dev/guide/coverage

## Scripts and CI

Typical project scripts:

```json
{
  "scripts": {
    "test": "vitest",
    "test:ci": "vitest run",
    "test:coverage": "vitest run --coverage"
  }
}
```

CI should install dependencies from a committed lockfile, use a supported Node version, run the project typecheck/lint where relevant, and invoke its non-watch test command. With Browser Mode, install the browser/provider dependencies too. Use the package manager already present in the repo. An optional GitHub Actions starting point is under `assets/ci-vitest.yml`.
