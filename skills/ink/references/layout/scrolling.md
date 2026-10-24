# Scrollable views with content offsets (Ink 8)

Ink 8 adds `contentOffsetX`/`contentOffsetY` on `<Box>` for **scrolling without moving the layout node**. Offsets are numeric terminal-cell positions (fractional values are truncated). Use `overflow="hidden"`, track viewport and content sizes separately, and clamp offsets.

```tsx
import {useRef, useState} from 'react';
import type {ReactNode} from 'react';
import {Box, Text, useBoxMetrics, useInput} from 'ink';

function ScrollView({height, children}: {height: number; children: ReactNode}) {
  const viewportRef = useRef(null);
  const contentRef = useRef(null);
  const {clientHeight} = useBoxMetrics(viewportRef);
  const {height: contentHeight} = useBoxMetrics(contentRef);
  const [requestedOffset, setRequestedOffset] = useState(0);
  const maxOffset = Math.max(0, contentHeight - clientHeight);
  const offset = Math.min(requestedOffset, maxOffset);

  useInput((_input, key) => {
    if (key.downArrow) setRequestedOffset(Math.min(maxOffset, offset + 1));
    if (key.upArrow) setRequestedOffset(Math.max(0, offset - 1));
  });

  return <Box ref={viewportRef} height={height} overflow="hidden"
      flexDirection="column" contentOffsetY={offset}>
    <Box ref={contentRef} flexDirection="column" flexShrink={0}>
      {children}
    </Box>
  </Box>;
}
```

**Important details**

- Put padding on the **content** wrapper instead of the viewport: `clientHeight` excludes borders **but includes padding**, so viewport padding makes simple `contentHeight - clientHeight` bounds wrong.
- Prevent content compression with `flexShrink={0}`; without it, Yoga may shrink children so there is nothing to scroll.
- `contentOffsetX` shifts children left; `contentOffsetY` shifts children up. Clip with `overflow="hidden"`.
- Offsets change rendering but **do not change layout coordinates** returned by `useBoxMetrics` or `measureElement`; adjust when hit-testing mouse positions.
- For accessibility, offer meaningful text and avoid hiding status information solely off-screen.

Upstream: https://github.com/vadimdemedes/ink/blob/v8.0.0/readme.md#contentoffsetx
