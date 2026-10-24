# useAnimation(options?) — Ink 8

Use the built-in animation clock for progress spinners and time-based effects; Ink shares a timer among active animations.

```tsx
import {Text, useAnimation, useIsScreenReaderEnabled} from 'ink';

const frames = ['-', '\\', '|', '/'];

function Spinner() {
  const screenReader = useIsScreenReaderEnabled();
  const {frame} = useAnimation({interval: 100, isActive: !screenReader});
  return <Text>{screenReader ? 'Working…' : frames[frame % frames.length]}</Text>;
}
```

- Options: `interval?: number` milliseconds (default `100`), `isActive?: boolean` (default `true`).
- Return: `{frame, time, delta, reset}`. `frame` counts ticks, `time` is elapsed milliseconds, `delta` measures elapsed milliseconds since the previous tick and accounts for skipped frames, `reset()` resets all three.
- Setting `isActive: false` stops the animation; re-enabling it resets timing.
- Avoid excessive animation frames and endless animations in screen-reader mode. See `rules/performance.md` in the skill root.

Source: https://github.com/vadimdemedes/ink/blob/v8.0.0/readme.md#useanimationoptions
