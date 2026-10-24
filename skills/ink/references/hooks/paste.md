# usePaste(handler, options?) — bracketed paste

Use `usePaste()` for multi-character pasted text, including newlines. Ink automatically enables terminal bracketed paste mode while the hook is active.

```tsx
import {useState} from 'react';
import {Text, useInput, usePaste} from 'ink';

function Editor() {
  const [value, setValue] = useState('');
  useInput((input, key) => {
    if (key.return) { /* submit */ return; }
    if (key.backspace || key.delete) { setValue(s => s.slice(0, -1)); return; }
    if (input) setValue(s => s + input);
  });
  usePaste(text => {
    setValue(s => s + text); // one callback for the entire pasted string
  });
  return <Text>{value}</Text>;
}
```

- `usePaste((text: string) => void, {isActive?: boolean})` returns `void`.
- Paste content is routed separately from `useInput` when a paste handler is active; avoid processing it twice.
- A pasted string may include line breaks or escape sequences; display/sanitize carefully for your use case.
- Requires an interactive terminal with bracketed paste support. For piped or CI input, provide a separate non-interactive mode rather than expecting keyboard hooks to work.

Source: https://github.com/vadimdemedes/ink/blob/v8.0.0/readme.md#usepastehandler-options
