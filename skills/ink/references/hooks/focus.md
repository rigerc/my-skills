# Focus management and terminal cursor (Ink 8)

**Do not confuse focused elements with the physical terminal cursor.** Focus controls keyboard navigation. `useCursor()` positions the cursor for IME/text composition.

## useFocus(options?)

```tsx
import {Text, useFocus} from 'ink';

function FocusItem({id, label}: {id: string; label: string}) {
  const {isFocused, focus} = useFocus({id, autoFocus: false, isActive: true});
  // focus accepts an ID: focus('settings'), NOT a zero-argument focus().
  return <Text color={isFocused ? 'green' : undefined}>{isFocused ? '> ' : '  '}{label}</Text>;
}
```

- Options: `id?: string`, `autoFocus?: boolean` (default `false`), `isActive?: boolean` (default `true`). Keep IDs unique; multiple components sharing an ID act as one focus stop.
- Return: `{isFocused: boolean, focus: (id: string) => void}`. **No `id` in the return value.**
- Tab/Shift+Tab cycle through registered, active focusable components. `autoFocus` applies only when no focus already exists. Registration order, not visual reorder, controls traversal.
- To capture keystrokes in a focused input, use `useInput(handler, {isActive: isFocused})`.

## useFocusManager()

```tsx
import {useFocusManager} from 'ink';

function Navigation() {
  const {focus, focusNext, focusPrevious, enableFocus, disableFocus, activeId} = useFocusManager();
  // Use these in input callbacks or effects, not unconditionally during render.
  return null;
}
```

- `focus(id)` — focus an existing ID; `focusNext()` / `focusPrevious()` — cycle.
- `enableFocus()` / `disableFocus()` — globally enable/disable focus traversal. Disabling also blurs current focus.
- `activeId` is the current focus ID or `undefined`.
- Focus management can intercept Tab/Shift+Tab; disable it if implementing independent key handling.

## useCursor() — terminal cursor and IME

**Correct Ink 8 API:**

```tsx
import {Box, Text, useCursor} from 'ink';

function Prompt({value, focused}: {value: string; focused: boolean}) {
  const {setCursorPosition} = useCursor();
  // Use terminal-cell width (e.g. `string-width`) for emoji and wide Unicode.
  if (focused) setCursorPosition({x: 2 + value.length, y: 1});
  else setCursorPosition(undefined);

  return <Box flexDirection="column">
    <Text>Input:</Text>
    <Text>{'> '}{value}</Text>
  </Box>;
}
```

`setCursorPosition({x, y})` uses **0-based coordinates relative to Ink's rendered output**, not the absolute terminal viewport. Pass `undefined` to hide the cursor. Call from the render function as upstream examples do; Ink coordinates the cursor with commits. When the text contains emoji, combining characters or CJK, compute the display width using `string-width` rather than `.length`.

**Incorrect:** `useCursor(true)`, `const {id} = useFocus()`, or `focus()` without an ID.

## Accessibility

The focus state is separate from the `aria-*` properties used by screen-reader output. See [accessibility](../accessibility/REFERENCE.md).

Source: https://github.com/vadimdemedes/ink/blob/v8.0.0/readme.md#usefocusoptions
