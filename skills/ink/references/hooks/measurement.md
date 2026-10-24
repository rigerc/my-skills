# Terminal dimensions and element metrics (Ink 8)

## useWindowSize()

Returns `{columns, rows}` in terminal cells. The component re-renders on a window resize (in interactive mode).

```tsx
import {Box, Text, useWindowSize} from 'ink';

function Layout() {
  const {columns, rows} = useWindowSize();
  return <Box flexDirection={columns >= 90 ? 'row' : 'column'}>
    <Text>{columns} columns, {rows} rows</Text>
  </Box>;
}
```

**Ink 8 typing change:** `useStdout().stdout` is a generic `stream.Writable`, so `stdout.columns` is not in its TypeScript surface. Do not use `useStdout` to subscribe to resize events.

## useBoxMetrics(ref)

Tracks a `<Box>` across layout updates. Use a persistent ref and `hasMeasured` to avoid treating pre-layout zeros as actual size.

```tsx
import {useRef} from 'react';
import {Box, Text, useBoxMetrics} from 'ink';

function MeasuredPanel() {
  const ref = useRef(null);
  const {width, height, clientWidth, clientHeight, left, top, hasMeasured} = useBoxMetrics(ref);
  return <Box ref={ref} flexDirection="column">
    <Text>{hasMeasured ? `size ${width}x${height}, content ${clientWidth}x${clientHeight}` : 'Measuring…'}</Text>
  </Box>;
}
```

Return fields: `width`, `height`, `left`, `top`, `clientWidth`, `clientHeight`, `hasMeasured`. `left`/`top` are relative to the **parent**, not terminal viewport. `clientWidth`/`clientHeight` exclude borders but **not padding**. Until measurement or after ref detach, metrics reset to zero.

## measureElement(ref) (non-reactive)

Imported directly from `ink`. Returns `{x, y, width, height, clientWidth, clientHeight}` for an attached `<Box>` ref. Read it **after layout** (an effect or event callback); calling during render returns zeros. `x/y` are relative to the **live layout region**, not the whole terminal. Neither coordinates API includes ancestor `contentOffsetX/Y` corrections.

**Which one?** Use `useBoxMetrics` for reactive layouts; `measureElement` for one-off measurements in effects and callbacks. See [scrolling](../layout/scrolling.md).

Sources: [v8 docs](https://github.com/vadimdemedes/ink/blob/v8.0.0/readme.md#useboxmetricsref), [v8 release](https://github.com/vadimdemedes/ink/releases/tag/v8.0.0).
