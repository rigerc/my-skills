# `ink-testing-library` API reference (repository v4.0.0)

Source: https://github.com/vadimdemedes/ink-testing-library/blob/master/source/index.ts
README: https://github.com/vadimdemedes/ink-testing-library/blob/master/readme.md

The repository's source declares `render(tree: ReactElement)`; it returns the following members:

| Member | Type / behavior | Typical use |
| --- | --- | --- |
| `lastFrame()` | `() => string \| undefined`; alias of `stdout.lastFrame()` | Assert the latest stdout write |
| `frames` | `string[]`; same array as `stdout.frames` | Assert a render history |
| `rerender(tree)` | `(ReactElement) => void` | Re-render the root with new props/components |
| `unmount()` | `() => void` | Unmount current component |
| `cleanup()` | `() => void` | Dispose instance-specific Ink resources (present in v4 source; not in README) |
| `stdin` | Mock input stream | Simulate keystrokes via `stdin.write(string)` |
| `stdout` | Mock output stream with `.frames` and `.lastFrame()` | Inspect stdout writes |
| `stderr` | Mock error-output stream with `.frames` and `.lastFrame()` | Inspect stderr writes |

There is also a **module-level** `cleanup()` export, which iterates library-created instances and invokes their `unmount()` and `cleanup()` methods. Prefer per-test cleanup and verify semantics with the installed version before relying on global cleanup.

## Construction details verified in the v4 source

- Mock stdout has a `columns` getter set to **100**. It records every stream `.write()` string into `stdout.frames` and remembers the last one.
- Mock stderr likewise records `.write()` strings into `stderr.frames`.
- Mock stdin is an `EventEmitter` with `isTTY = true`. `stdin.write(data)` saves and emits data events and supports `read()` for code expecting readable input. It is a **mock**, not a fully fledged physical terminal.
- `render()` delegates to Ink's `render` using the mock streams, with `{ debug: true, exitOnCtrlC: false, patchConsole: false }`.
- The reviewed `render()` signature has **one argument**. Do not pass a second options object unless the installed library actually supports one.

## Choosing the right stream

`lastFrame()` and `stdout.lastFrame()` both read **stdout**. If a component writes to stderr, inspect `stderr.lastFrame()` or `stderr.frames`; they are independent from stdout.

Normal `console.error()` behavior is not inherently equivalent to `stderr.write` on the mock stream: the library renders Ink with `patchConsole: false`. Mock or route process console separately if console diagnostics are what the test intends to capture.

## Timing and snapshots

`stdout.frames` records stream writes, not guaranteed one-to-one React component commits or human-perceived screens. For tests of a completed async operation, assert eventual output instead of a specific number of writes. Terminal UI output may have ANSI codes, wrapping, newlines, and control sequences depending on what the app emits; base expected strings on tested behavior.

## Version caveat

The published package version inspected is **4.0.0**; its repository `package.json` lists Node `>=18`, `ink` `^5.0.0` and `react` `^18.3.1` as its development environment (not a blanket compatibility guarantee). Compare installed package type declarations before using undocumented features such as instance `cleanup()` or a different framework major.
