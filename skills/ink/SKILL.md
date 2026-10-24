---
name: ink
description: Use when building, debugging, testing, or reviewing an Ink (React terminal CLI) application. Covers Ink 8 APIs, Node and React compatibility, components, input/paste, focus, terminal dimensions, scrolling, lifecycle, accessibility, and testing.
metadata:
   references: core, components, hooks, layout, testing, accessibility
---

# Ink Platform Skill

Consolidated skill for building CLI applications with Ink (React for CLIs). **Target: stable Ink v8.0.0 (2026-10-03), Node.js >=22, React >=19.3.0** (and matching `@types/react` for TypeScript). Read a relevant reference before writing code; do not assume the `master` branch documents the installed stable release. Source: https://github.com/vadimdemedes/ink/blob/v8.0.0/readme.md. Use decision trees below to load only the references needed for the task.

## Critical Rules

**Follow these rules in all Ink code:**

1. **All text must be wrapped in `<Text>`.** Raw strings outside `<Text>` will throw an error.
2. **`<Text>` only allows text nodes and nested `<Text>`.** You cannot nest `<Box>` inside `<Text>`.
3. **`<Box>` is always `display: flex`.** Think of every `<Box>` as `<div style="display: flex">`.
4. **Use `useApp().exit()` to exit.** Never call `process.exit()` directly from within components.
5. **Install both `ink` and `react`.** They are peer dependencies: `npm install ink react`.
6. **`<Static>` only renders new items.** Changes to previously rendered items are ignored.
7. **Terminal width:** use `useWindowSize()` for responsive/reactive dimensions; do not access `.columns` on `useStdout().stdout` in Ink 8 TypeScript.
8. **Focus and cursor are separate:** `useFocus()` returns `{isFocused, focus(id)}`; `useCursor()` returns `{setCursorPosition({x,y} | undefined)}`.
9. **Width constraints:** `minWidth` and `maxWidth` accept numbers, not percentages, in Ink 8.
10. **Use `usePaste()`** to handle full pasted text separately from ordinary keypresses.

## How to Use This Skill

### Reference File Structure

Core references follow a 5-file pattern. Cross-cutting concepts are single-file guides.

`./references/core/` contains:

| File | Purpose | When to Read |
|------|---------|--------------|
| `REFERENCE.md` | Overview, when to use, quick start | **Always read first** |
| `api.md` | render(), renderToString(), Instance, measureElement | Writing code |
| `configuration.md` | Render options, environment vars | Configuring an app |
| `patterns.md` | Common patterns, best practices | Implementation guidance |
| `gotchas.md` | Pitfalls, limitations, debugging | Troubleshooting |

Component, hook, and concept references in `./references/<area>/` have `REFERENCE.md` as the entry point.

### Reading Order

1. Start with `core/REFERENCE.md` for project overview
2. Then read additional files relevant to your task:
   - Building UI -> `components/REFERENCE.md` + specific component files
   - Handling input/paste -> `hooks/input.md` + `hooks/paste.md`
   - Layout/positioning -> `layout/REFERENCE.md`; scrolling -> `layout/scrolling.md`
   - App lifecycle / child process handoff -> `hooks/app-lifecycle.md`
   - Terminal size and element measurement -> `hooks/measurement.md`
   - Spinners / time-driven UI -> `hooks/animation.md`
   - Focus management -> `hooks/focus.md`
   - Testing -> `testing/REFERENCE.md`
   - Accessibility -> `accessibility/REFERENCE.md`
   - Troubleshooting -> `core/gotchas.md`
   - **Best practices / rules** -> `rules/RULES.md` + specific rule files

### Example Paths

```
./references/core/REFERENCE.md             # Start here
./references/core/api.md                   # render(), renderToString()
./references/components/text.md            # <Text> component
./references/components/box.md             # <Box> component (layout, borders)
./references/hooks/input.md                # useInput hook
./references/hooks/paste.md                # usePaste hook
./references/hooks/measurement.md          # useWindowSize and useBoxMetrics
./references/hooks/animation.md            # useAnimation
./references/layout/scrolling.md           # scroll offsets and viewport metrics
./references/layout/patterns.md            # Common layout recipes
./references/testing/REFERENCE.md          # ink-testing-library
./rules/RULES.md                           # Best practices entry point
./rules/performance.md                     # FPS, Static, memoization
./rules/components.md                      # Per-component rules
./rules/hooks.md                           # Per-hook rules
./rules/core.md                            # render(), errors, environment
```

## Quick Decision Trees

### "I need to display content"

```
Display content?
├─ Plain or styled text -> components/text.md
├─ Container with layout -> components/box.md
├─ Container with borders -> components/box.md (borderStyle)
├─ Container with background color -> components/box.md (backgroundColor)
├─ Line breaks within text -> components/utilities.md (Newline)
├─ Flexible spacer -> components/utilities.md (Spacer)
├─ Permanent log output (completed items) -> components/utilities.md (Static)
└─ Transform text output (uppercase, gradient) -> components/utilities.md (Transform)
```

### "I need user input"

```
User input?
├─ Keyboard shortcuts/arrow keys -> hooks/input.md (useInput)
├─ Raw stdin access -> hooks/stdio.md (useStdin)
├─ Pasted text / bracketed paste -> hooks/paste.md (usePaste)
├─ Tab/Shift+Tab focus cycling -> hooks/focus.md (useFocus)
├─ Programmatic focus control -> hooks/focus.md (useFocusManager)
└─ Cursor positioning (IME) -> hooks/focus.md (useCursor)
```

### "I need layout/positioning"

```
Layout?
├─ Horizontal row of elements -> layout/REFERENCE.md (flexDirection: row)
├─ Vertical stack of elements -> layout/REFERENCE.md (flexDirection: column)
├─ Centering content -> layout/patterns.md
├─ Spacing between elements -> layout/REFERENCE.md (gap, margin, padding)
├─ Fixed width/height -> components/box.md (width, height)
├─ Percentage sizing -> components/box.md (width: "50%", not min/max width)
├─ Min/max constraints -> components/box.md (minWidth, maxWidth, maxHeight)
├─ Push elements apart -> components/utilities.md (Spacer)
├─ Flex grow/shrink -> layout/REFERENCE.md (flexGrow, flexShrink)
├─ Wrapping content -> layout/REFERENCE.md (flexWrap)
├─ Overflow control -> components/box.md (overflow)
├─ Scrollable view -> layout/scrolling.md (contentOffsetY, useBoxMetrics)
├─ Terminal resize -> hooks/measurement.md (useWindowSize)
└─ Complex nested layouts -> layout/patterns.md
```

### "I need to manage app lifecycle"

```
App lifecycle?
├─ Mount and render -> core/api.md (render)
├─ Render to string (no terminal) -> core/api.md (renderToString)
├─ Exit the app programmatically -> hooks/app-lifecycle.md (useApp, exit)
├─ Wait for app to finish -> core/api.md (waitUntilExit)
├─ Wait for writes to flush -> hooks/app-lifecycle.md (waitUntilRenderFlush)
├─ Run interactive child editor -> hooks/app-lifecycle.md (suspendTerminal)
├─ Re-render with new props -> core/api.md (rerender)
├─ Unmount the app -> core/api.md (unmount)
├─ Full-screen app -> core/configuration.md (alternateScreen)
└─ Write to stdout/stderr outside Ink -> hooks/stdio.md
```

### "I need to test my CLI"

```
Testing?
├─ Render and check output -> testing/REFERENCE.md
├─ Simulate user input -> testing/REFERENCE.md (stdin.write)
├─ Snapshot testing -> testing/REFERENCE.md
└─ Check last rendered frame -> testing/REFERENCE.md (lastFrame)
```

### "I need accessibility"

```
Accessibility?
├─ Screen reader support -> accessibility/REFERENCE.md
├─ ARIA roles (checkbox, button, etc.) -> accessibility/REFERENCE.md
├─ ARIA state (checked, disabled, etc.) -> accessibility/REFERENCE.md
├─ Custom screen reader labels -> accessibility/REFERENCE.md (aria-label)
└─ Hide from screen readers -> accessibility/REFERENCE.md (aria-hidden)
```

### "I need to debug/troubleshoot"

```
Troubleshooting?
├─ Text rendering issues -> core/gotchas.md
├─ Layout problems -> core/gotchas.md + layout/REFERENCE.md
├─ Input not working -> core/gotchas.md + hooks/input.md
├─ Process not exiting -> core/gotchas.md
├─ CI rendering issues -> core/configuration.md (CI mode)
├─ Console output mixing -> core/configuration.md (patchConsole)
└─ Performance/flickering -> core/configuration.md + rules/performance.md
```

### "I want best practices / production-ready code"

```
Best practices?
├─ General rules (critical) -> rules/RULES.md
├─ Performance (FPS, Static, memoization) -> rules/performance.md
├─ Per-component patterns & anti-patterns -> rules/components.md
├─ Per-hook patterns & gotchas -> rules/hooks.md
└─ render() / errors / environment behavior -> rules/core.md
```

### Troubleshooting Index

- Text outside `<Text>` -> `core/gotchas.md`
- `<Box>` inside `<Text>` -> `core/gotchas.md`
- Process hanging/not exiting -> `core/gotchas.md`
- Console.log mixing with output -> `core/configuration.md`
- Layout misalignment -> `layout/REFERENCE.md`
- Input not received -> `hooks/input.md` + `rules/hooks.md`
- Focus not cycling -> `hooks/focus.md` + `rules/hooks.md`
- CI output issues -> `core/configuration.md` + `rules/core.md`
- Flickering/performance -> `core/configuration.md` + `rules/performance.md`
- Anti-patterns / pitfalls -> `rules/components.md`, `rules/hooks.md`, `rules/core.md`

## Product Index

### Core
| Area | Entry File | Description |
|------|------------|-------------|
| Core | `./references/core/REFERENCE.md` | Overview, quick start, project setup |
| API | `./references/core/api.md` | render, renderToString, Instance |
| Config | `./references/core/configuration.md` | Render options, environment variables |
| Patterns | `./references/core/patterns.md` | Common patterns and recipes |
| Gotchas | `./references/core/gotchas.md` | Pitfalls and debugging |

### Components
| Component | Entry File | Description |
|-----------|------------|-------------|
| Overview | `./references/components/REFERENCE.md` | All components at a glance |
| Text | `./references/components/text.md` | Text display and styling |
| Box | `./references/components/box.md` | Layout, borders, backgrounds |
| Utilities | `./references/components/utilities.md` | Newline, Spacer, Static, Transform |

### Hooks
| Hook | Entry File | Description |
|------|------------|-------------|
| Overview | `./references/hooks/REFERENCE.md` | All hooks at a glance |
| Input | `./references/hooks/input.md` | useInput for keyboard handling |
| App Lifecycle | `./references/hooks/app-lifecycle.md` | useApp for exit control |
| Stdio | `./references/hooks/stdio.md` | useStdin, useStdout, useStderr |
| Paste | `./references/hooks/paste.md` | usePaste, bracketed paste |
| Measurement | `./references/hooks/measurement.md` | useWindowSize, useBoxMetrics |
| Animation | `./references/hooks/animation.md` | useAnimation |
| Focus | `./references/hooks/focus.md` | useFocus, useFocusManager, useCursor |

### Cross-Cutting Concepts
| Concept | Entry File | Description |
|---------|------------|-------------|
| Layout | `./references/layout/REFERENCE.md` | Yoga/Flexbox layout system |
| Layout Patterns | `./references/layout/patterns.md` | Common layout recipes |
| Scrolling | `./references/layout/scrolling.md` | Ink 8 content offsets and clipping |
| Testing | `./references/testing/REFERENCE.md` | ink-testing-library |
| Accessibility | `./references/accessibility/REFERENCE.md` | Screen reader & ARIA support |

### Best Practices (Rules)
| Rule File | Entry File | Description |
|-----------|------------|-------------|
| Overview | `./rules/RULES.md` | Entry point + 10 critical rules |
| Performance | `./rules/performance.md` | FPS tuning, Static, memoization, incremental rendering |
| Components | `./rules/components.md` | Box, Text, Static, Transform, Newline, Spacer rules |
| Hooks | `./rules/hooks.md` | useInput, useApp, useFocus, useCursor, useStdin rules |
| Core | `./rules/core.md` | render(), renderToString(), errors, CI, Kitty protocol |

## Resources

**Repository**: https://github.com/vadimdemedes/ink
**npm**: https://www.npmjs.com/package/ink
**Testing Library**: https://github.com/vadimdemedes/ink-testing-library
**Create Ink App**: https://github.com/vadimdemedes/create-ink-app
