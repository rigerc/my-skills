# Configuration

## Render Options

### stdout / stdin / stderr

Custom generic Node.js `Readable`/`Writable` streams for output, input, and errors (Ink 8):

```jsx
render(<MyApp />, {
	stdout: customWriteStream,
	stdin: customReadStream,
	stderr: customErrorStream,
});
```

### exitOnCtrlC

Type: `boolean` | Default: `true`

Listen for Ctrl+C and exit. Needed when stdin is in raw mode (Ctrl+C is ignored by default in raw mode).

### patchConsole

Type: `boolean` | Default: `true`

Patch `console.*` methods so output doesn't mix with Ink's output. When enabled, Ink intercepts console calls, clears main output, renders console output, then rerenders the main output.

### debug

Type: `boolean` | Default: `false`

Render each update as separate output instead of replacing previous output. Useful for debugging render cycles.

### maxFps

Type: `number` | Default: `30`

Maximum frames per second. Controls how frequently the UI can update. Lower values reduce CPU usage for frequently-updating components.

```jsx
render(<MyApp />, {maxFps: 10}); // Throttle to 10fps
```

### incrementalRendering

Type: `boolean` | Default: `false`

Only update changed lines instead of redrawing the entire output. Reduces flickering and improves performance for frequently updating UIs.

```jsx
render(<MyApp />, {incrementalRendering: true});
```

### concurrent

Type: `boolean` | Default: `false`

Enable React Concurrent Rendering mode:
- Suspense boundaries work with async data fetching
- `useTransition` and `useDeferredValue` hooks are functional
- Updates can be interrupted for higher priority work

```jsx
render(<MyApp />, {concurrent: true});
```

**Note:** Ink does not support reusing a mounted stdout instance to change `concurrent` (or `interactive` / `alternateScreen`). Unmount before creating a fresh render with changed options.

### onRender

Do not call `console.log` (or emit console output) within an `onRender` callback: it can recursively trigger Ink output.

Type: `({renderTime: number}) => void`

Callback after each render with metrics:

```jsx
const metrics = [];
render(<MyApp />, {
	onRender: ({renderTime}) => {
		// Record timing, but avoid console writes that trigger Ink re-renders
		metrics.push(renderTime);
	},
});
```

### isScreenReaderEnabled

Type: `boolean` | Default: `process.env['INK_SCREEN_READER'] === 'true'`

Enable screen reader support. See [Accessibility](../accessibility/REFERENCE.md).

### kittyKeyboard

Type: `object` | Default: `undefined`

Enable the kitty keyboard protocol for enhanced keyboard input. See also [`useInput`](../hooks/input.md).

```jsx
render(<MyApp />, {kittyKeyboard: {mode: 'auto'}});
```

#### kittyKeyboard.mode

- `'auto'`: Detect terminal support with heuristic precheck
- `'enabled'`: Force enable (stdin and stdout must be TTYs)
- `'disabled'`: Never enable

#### kittyKeyboard.flags

Default: `['disambiguateEscapeCodes']`

Available flags:
- `'disambiguateEscapeCodes'`
- `'reportEventTypes'`
- `'reportAlternateKeys'`
- `'reportAllKeysAsEscapeCodes'`
- `'reportAssociatedText'`

## interactive / alternateScreen

Ink automatically enables interactivity only when a TTY is available and CI is not detected. In non-interactive mode it writes the final dynamic frame at unmount; keyboard/TTY features should not be assumed.

```jsx
render(<MyApp />, {alternateScreen: true}); // full-screen TTY; restored on exit
```

`interactive` can override detection but should usually be left unset. `alternateScreen` requires interactive mode; scrollback is unavailable in the alternate buffer. Terminal lifecycle options are effectively fixed for a given mounted stdout; unmount before recreating the instance with different options.

## CI Mode

When running on CI (detected via `CI` environment variable):
- Only the last frame is rendered on exit
- Terminal resize events are not listened to

Opt out with `CI=false`:

```bash
CI=false node my-cli.js
```

## Environment Variables

| Variable | Effect |
|----------|--------|
| `CI` | Enables CI rendering mode |
| `INK_SCREEN_READER` | Set to `'true'` to enable screen reader support |
| `DEV` | Enables React DevTools integration |

## React DevTools

Enable with `DEV=true`:

```bash
DEV=true my-cli
npx react-devtools  # In another terminal
```

You can inspect and change props live.

## Project Setup

**Minimum versions for Ink 8:** Node.js >=22 and React >=19.3.0 (including `@types/react` >=19.3 for TypeScript). Prefer pinned or semver-compatible dependencies over floating `latest` in production.


### package.json (TypeScript)

```json
{
	"type": "module",
	"scripts": {
		"build": "tsc",
		"start": "node dist/index.js"
	},
	"dependencies": {
		"ink": "^8.0.0",
		"react": "^19.3.0"
	},
	"devDependencies": {
		"@types/react": "^19.3.0",
		"typescript": "latest"
	}
}
```

### Babel Setup (JavaScript)

```bash
npm install --save-dev @babel/preset-react
```

```json
{
	"presets": ["@babel/preset-react"]
}
```
