# Stdio hooks — Ink 8

Ink 8 accepts **generic Node.js streams** in `render()` options. These are not guaranteed to be TTY streams. Prefer [useWindowSize](./measurement.md) for terminal dimensions; never rely on typed `useStdout().stdout.columns` or `.rows`.

## useStdin()

```tsx
import {useEffect} from 'react';
import {useStdin} from 'ink';

function RawListener() {
  const {stdin, isRawModeSupported, setRawMode} = useStdin();
  useEffect(() => {
    if (!isRawModeSupported) return;
    setRawMode(true);
    const onData = (data: Buffer | string) => { /* handle bytes */ };
    stdin.on('data', onData);
    return () => { stdin.off('data', onData); setRawMode(false); };
  }, [stdin, isRawModeSupported, setRawMode]);
  return null;
}
```

- `stdin: stream.Readable`, `isRawModeSupported: boolean`, `setRawMode(boolean)`.
- `setRawMode()` **throws when unsupported**: guard it. Ink's wrapper reference-counts raw-mode requests; do not call `process.stdin.setRawMode()` directly.
- Prefer `useInput` and `usePaste` for ordinary keyboard/paste interactions; don't race them with manual stdin parsing.
- Do not change raw mode or register listeners during React render; subscribe in an effect and clean up.

## useStdout() and useStderr()

```tsx
import {useEffect} from 'react';
import {useStdout, useStderr} from 'ink';

function Report() {
  const {write: writeOut} = useStdout();
  const {write: writeErr} = useStderr();
  useEffect(() => {
    writeOut('Starting...\n');
    writeErr('Diagnostic log\n');
  }, [writeOut, writeErr]);
  return null;
}
```

Both expose a generic `stream.Writable` and a `write(data: string)` helper that preserves Ink's output. Avoid direct `process.stdout.write()` while the TUI is mounted, and avoid calling `write` on every render.

### Responsive terminal dimensions

```tsx
import {Box, Text, useWindowSize} from 'ink';

function Responsive() {
  const {columns} = useWindowSize(); // subscribes to terminal resizing
  return <Box flexDirection={columns >= 80 ? 'row' : 'column'}>
    <Text>Adaptive layout</Text>
  </Box>;
}
```

Use [measurement.md](./measurement.md) for reactive window and Box metrics.

Sources: [v8 release](https://github.com/vadimdemedes/ink/releases/tag/v8.0.0), [v8 docs](https://github.com/vadimdemedes/ink/blob/v8.0.0/readme.md).
