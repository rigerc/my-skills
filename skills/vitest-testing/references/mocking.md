# Reliable mocking and asynchronous test patterns

These examples describe testing **applications using Vitest**. Do not apply them to Vitest's own upstream test suite, which has a repository-level no-mocking rule.

## Spies, stubs, and dependency injection

Prefer a seam in production code over mocking unrelated internals. Use `vi.fn` for a standalone fake function, and `vi.spyOn(object, 'method')` to observe or replace one object method where the runtime allows it.

```ts
import { afterEach, expect, test, vi } from 'vitest'

afterEach(() => vi.restoreAllMocks())

test('tracks a collaborator', () => {
  const notify = vi.fn()
  notify('ready')
  expect(notify).toHaveBeenCalledExactlyOnceWith('ready')
})
```

`vi.clearAllMocks()` clears calls/results; `vi.resetAllMocks()` also resets implementations; `vi.restoreAllMocks()` restores original spied methods. Select the appropriate scope rather than treating these as interchangeable. In Vitest 5 `clearMocks: true` is the default.

## Module mock factories

`vi.mock` calls are hoisted and must be at **file top level** in Vitest 5. Avoid placing them within `test`, `beforeEach`, or `describe` callbacks. The `import()` form enables type-checking and Vitest handles the import at transform time:

```ts
import { expect, test, vi } from 'vitest'
import { getUser } from './api'

vi.mock(import('./api'), () => ({
  getUser: vi.fn(),
}))

test('receives a mocked user', async () => {
  vi.mocked(getUser).mockResolvedValue({ id: 1, name: 'Ada' })
  await expect(getUser(1)).resolves.toMatchObject({ name: 'Ada' })
})
```

Use `vi.hoisted(() => ({ ... }))` for values needed inside hoisted mock factories. For per-test dynamic module mocking, use `vi.doMock` with a subsequent dynamic import. Mocked exports do **not** replace internal references inside the real module to other functions in that module; refactor dependencies into separate modules or inject them where necessary.

In Browser Mode, imported module namespaces are sealed, so `vi.spyOn` on namespace exports is unsupported. For export spies that retain implementation, consider `vi.mock('./api', { spy: true })`. See https://vitest.dev/guide/mocking/modules and https://vitest.dev/guide/browser/.

## Promises and errors

Always await asynchronous code and promise matchers:

```ts
await expect(fetchUser('missing')).rejects.toThrow('not found')
await expect(fetchUser('known')).resolves.toMatchObject({ id: 'known' })
```

For callback or event driven code, wait for a documented completion signal rather than adding arbitrary sleeps.

## Fake timers and system time

```ts
import { afterEach, expect, test, vi } from 'vitest'

afterEach(() => {
  vi.useRealTimers()
  vi.unstubAllGlobals()
  vi.unstubAllEnvs()
})

test('uses a deterministic clock', () => {
  vi.useFakeTimers()
  vi.setSystemTime(new Date('2026-01-01T00:00:00.000Z'))
  expect(Date.now()).toBe(Date.parse('2026-01-01T00:00:00.000Z'))
})
```

Use `vi.advanceTimersByTimeAsync` for timers with promises when relevant. Beware of fake timers around real network requests or libraries that expect their own timers to progress.

## HTTP and global boundaries

Prefer explicit request stubs or a request-interception tool configured for the project. Avoid live network calls in unit tests; make every unexpected request fail where possible. `vi.stubGlobal('fetch', fakeFetch)` may be appropriate for narrow code paths; restore with `vi.unstubAllGlobals()` (or enable `unstubGlobals: true`).

Official mocking guide: https://vitest.dev/guide/mocking
