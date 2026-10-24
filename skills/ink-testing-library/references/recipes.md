# Testing recipes and troubleshooting

These examples use Vitest for `expect`/`vi.waitFor`; adapt assertion and polling APIs to AVA, Jest, or the test runner already configured in the project.

## Static output and prop-driven updates

```tsx
import {render} from 'ink-testing-library';
import {expect, it} from 'vitest';

it('shows changed status', () => {
  const view = render(<Status status="pending" />);
  try {
    expect(view.lastFrame()).toContain('pending');
    view.rerender(<Status status="complete" />);
    expect(view.lastFrame()).toContain('complete');
  } finally {
    view.unmount();
    view.cleanup();
  }
});
```

Here `Status` is the project's actual component; substitute its real props. Use exact string equality only when the terminal layout is stable.

## Keyboard input

```tsx
import React, {useState} from 'react';
import {Text, useInput} from 'ink';
import {render} from 'ink-testing-library';
import {expect, it, vi} from 'vitest';

const Confirm = () => {
  const [confirmed, setConfirmed] = useState(false);
  useInput(input => {
    if (input === 'y') setConfirmed(true);
  });
  return <Text>{confirmed ? 'Confirmed' : 'Continue? (y/n)'}</Text>;
};

it('reacts to a key', async () => {
  const view = render(<Confirm />);
  try {
    expect(view.lastFrame()).toContain('Continue?');
    view.stdin.write('y');
    await vi.waitFor(() => expect(view.lastFrame()).toContain('Confirmed'));
  } finally {
    view.unmount();
    view.cleanup();
  }
});
```

`stdin.write` sends bytes to the mock stream. It is not a DOM click or text-input setter. For Enter, arrows, Escape, Ctrl combinations, or focus navigation, check `useInput` and the key decoding behavior of the installed Ink version; do not guess that a human-readable string like `'Enter'` works.

## Asynchronous status change

```tsx
const view = render(<AsyncTask />);
try {
  await vi.waitFor(() => {
    expect(view.lastFrame()).toContain('Finished');
  }, {timeout: 2000});
} finally {
  view.unmount();
  view.cleanup();
}
```

Here `AsyncTask` is illustrative. For HTTP operations mock the client dependency so the test is deterministic. Prefer runner-aware polling over fixed sleep durations. If using fake timers, advance them consistently with React updates and resolve promises as needed.

## Frame history

```tsx
const view = render(<Status status="waiting" />);
try {
  view.rerender(<Status status="done" />);
  expect(view.frames.some(frame => frame.includes('waiting'))).toBe(true);
  expect(view.frames.some(frame => frame.includes('done'))).toBe(true);
  expect(view.lastFrame()).toContain('done');
} finally {
  view.unmount();
  view.cleanup();
}
```

Check **meaningful observed states**, not that `frames.length === 2` unless the exact emission count is part of the contract.

## Stderr

```tsx
const view = render(<MyApp />);
try {
  // Trigger a behavior that writes specifically through Ink's stderr stream.
  expect(view.stderr.lastFrame()).toContain('message');
} finally {
  view.unmount();
  view.cleanup();
}
```

`MyApp` is a placeholder. Do not claim `console.error()` automatically writes to `view.stderr`: the library disables Ink's console patching.

## Common failures

| Symptom | Likely cause | Remediation |
| --- | --- | --- |
| `screen.getByText is not a function` | Using browser Testing Library APIs | Assert against `lastFrame()` / `frames` instead |
| `lastFrame()` is `undefined` | No frame emitted yet | Wait for a known condition and verify component actually renders text |
| Keyboard write has no effect | Missing `useInput`, not focused, or wrong input encoding | Verify component wiring and Ink key-decoder/version; start with plain characters |
| Flaky async assertion | React update scheduled later than assertion | Use framework wait/polling and mock external dependencies |
| Unexpected whitespace/color | Terminal layout / ANSI sequences | Normalize with an explicit utility if needed, or assert stable substrings |
| Output looks different on CI | Terminal behavior, React/Ink version, Unicode support | Inspect actual captured strings and project versions; assert a stable contract |
| Leaked handlers / later test interference | Mounted instances survive tests | Teardown each `render` in `finally` or test hook |
| TypeScript cannot compile JSX | JSX transform / runner configuration mismatch | Follow the project's established TSX setup; do not add arbitrary Babel settings |

## Test review checklist

- The test asserts observable terminal output before and after a meaningful action.
- The test uses only APIs provided by `ink-testing-library` and the installed test runner.
- Async expectations wait for their condition without introducing nondeterministic sleeps.
- Each instance is unmounted even on assertion failure.
- It does not assume DOM, real TTY dimensions, stdout/stderr equivalence, or exact render counts.
