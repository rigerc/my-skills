---
name: ink-testing-library
description: >-
  Write, improve, and debug automated tests for React-based Ink terminal/CLI
  components using the ink-testing-library package. Use when testing rendered
  terminal output, interactive keyboard input, rerenders, asynchronous UI
  changes, stdout/stderr frames, or teardown in Ink apps. Do not use for browser
  React DOM tests or when only a one-shot renderToString assertion is needed.
compatibility: >-
  Node.js >=18; an existing React + Ink project with ink-testing-library and
  a TSX/JSX-capable test runner. Examples use Vitest; adapt to the project's runner.
metadata:
  source: https://github.com/vadimdemedes/ink-testing-library
  library-version-reviewed: "4.0.0"
---

# Test Ink terminal interfaces with ink-testing-library

Use `ink-testing-library` to test **observable terminal behavior**: text produced by Ink components, input handling, and successive frames. This package does **not** render HTML and does not expose Testing Library DOM queries such as `screen.getByRole`.

## Workflow

1. **Inspect the project**: determine its Ink, React, Node, test-runner and `ink-testing-library` versions; follow its current module/JSX conventions. The upstream `ink-testing-library` 4.0.0 repository uses Node >=18 and develops against Ink 5 + React 18; check compatibility rather than assuming all majors work identically.
2. **Select the behavior**: specify the frame text to assert, the input or props to change, and when the state should become visible. Prefer user-observable outcomes over private hook state.
3. **Render in the test**: import `render` from `ink-testing-library`, mount a JSX element, and use its return object. It provides `lastFrame`, `frames`, `rerender`, `unmount`, `cleanup`, `stdin`, `stdout`, and `stderr` in the reviewed source.
4. **Drive the component**: use `rerender(<Component ... />)` for new props; use `stdin.write('x')` for simulated input. Use key-specific sequences only after checking the project's Ink version and input handlers.
5. **Assert the resulting output**: use `expect(lastFrame()).toBe(...)` for small deterministic strings, `toContain`/regular expressions for variable terminal layouts, or `frames` to check transitions. Read `stderr.lastFrame()` only for output actually written to Ink's stderr stream.
6. **Handle asynchronous updates**: if a promise, timer, `useEffect`, or event-driven state change delays rendering, wait for the expected condition with the project's runner (e.g., `vi.waitFor`). Do not make arbitrary sleeps the default or assert the next frame synchronously when scheduling is uncertain.
7. **Tear down every instance**: call `unmount()` in `finally` or in test cleanup. Where supported by the installed version, call the instance's `cleanup()` as well to release Ink's per-stream bookkeeping. The package also exports a global `cleanup()` in the reviewed v4 source, but prefer explicit ownership to avoid test leakage.
8. **Run the project's actual test command** and fix failing tests; avoid claiming tests passed unless they were executed. If a failure is environmental (TTY, React/Ink version, test transform), report it separately from behavior failures.

## Minimal example (Vitest, TSX)

```tsx
import React from 'react';
import {Text} from 'ink';
import {render} from 'ink-testing-library';
import {expect, it} from 'vitest';

const Greeting = ({name}: {name: string}) => <Text>Hello {name}</Text>;

it('renders new props', () => {
  const view = render(<Greeting name="Ada" />);

  try {
    expect(view.lastFrame()).toBe('Hello Ada');
    view.rerender(<Greeting name="Lin" />);
    expect(view.lastFrame()).toBe('Hello Lin');
  } finally {
    view.unmount();
    view.cleanup(); // available in ink-testing-library v4; verify on other versions
  }
});
```

For a runnable interactive example, see [examples/counter.test.tsx](examples/counter.test.tsx). Read [references/recipes.md](references/recipes.md) for keyboard input, frame-history assertions, async rendering, and troubleshooting; consult [references/api.md](references/api.md) for the precise v4 API and limits.

## Essential rules

- **No DOM assertions**: `ink-testing-library` captures terminal **strings**, not DOM nodes. Avoid `@testing-library/react` APIs for Ink interfaces.
- **No invented helpers**: `render` is the core function; `waitFor`, `fireEvent`, `screen`, and `userEvent` are **not** exports of this library. Use the test runner's waiting utilities when applicable.
- **Frames are snapshots of writes, not semantic steps**: React may batch or emit extra renders. Avoid assertions that depend on an exact frame count unless the feature specifically requires it.
- **`lastFrame()` can be `undefined`** when no output has yet been written; poll for the intended condition when behavior is asynchronous.
- **Terminal presentation matters**: columns and ANSI formatting may affect string equality. The reviewed implementation uses 100 columns; adjust assertions for wrapped or colored output rather than assuming a real terminal width.
- **Use source-appropriate teardown**: `unmount` and `cleanup` are distinct operations in the reviewed implementation; inspect installed typings if older versions differ.
- **Keep examples in the project's preferred test framework**, not necessarily Vitest. Do not add or migrate a test runner merely to use this skill.

## Source of truth

- [Repository and README](https://github.com/vadimdemedes/ink-testing-library)
- [Source implementation (master)](https://github.com/vadimdemedes/ink-testing-library/blob/master/source/index.ts)
- [Ink framework](https://github.com/vadimdemedes/ink)

The linked implementation and installed package may differ. Check local type declarations for version-specific behavior, especially when using newer Ink/React releases.
