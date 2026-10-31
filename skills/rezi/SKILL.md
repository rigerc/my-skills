---
name: rezi
description: Build, extend, and troubleshoot Rezi TypeScript terminal user interfaces (TUIs). Use for @rezi-ui/core, @rezi-ui/node, create-rezi, ui.* widget trees, screens, routing, keyboard/focus behavior, forms, tables, overlays, testing, native rendering, and Rezi framework contributions.
---

# Rezi — TypeScript terminal UI development

Use this skill to **create or maintain Rezi applications** and to **contribute to the Rezi framework itself**. Rezi is a declarative TUI framework for Node.js and Bun, with a TypeScript widget API backed by the native Zireael renderer. It is **not React, a browser UI, or the Rezi résumé service**.

## First: determine the work context

1. **Application work**: the user wants to scaffold an app, build a TUI screen, edit app state, wire input, or test UI behavior. Inspect `package.json`, existing app entry points, and installed `@rezi-ui/*` versions. Match the app's structure and version.
2. **Framework contribution**: the user wants to add/change a `ui.*` widget or modify Rezi internals. Inspect `AGENTS.md`, `CLAUDE.md`, `docs/dev/code-standards.md`, `docs/dev/testing.md`, the target code, and neighboring tests **in the source checkout** before editing. Follow public API/JSX parity, portability, and protocol guardrails below.
3. **Standalone design or explanation**: provide a copyable TypeScript example using the actual Rezi API. If not in a source checkout, consult this skill's bundled documentation and clearly distinguish suggestions from code verified by running.

**Source priority**: current project source/types > installed package exports > documentation matching that version > bundled references. Rezi is in beta; do not assume a bundled API example overrides local types. Check widget stability tier when relevant.

## Rezi app workflow

1. **Start from a working app shape.** For new projects, prefer `npm create rezi my-app` (templates: `minimal`, `cli-tool`, `starship`) and `npm run start`. For existing projects, preserve their scripts, architecture, and package manager. Manual dependency installation uses `@rezi-ui/core` and `@rezi-ui/node`; `@rezi-ui/jsx` is optional.
2. **Model state and events.** Define a typed `State` and, as complexity grows, an `Action` union with a pure reducer. Use `createNodeApp<State>({ initialState })`, `app.view(...)`, and immutable `app.update(...)` transitions; use the same dispatch paths for button presses and keybindings.
3. **Compose with `ui.*`.** Prefer `ui.page`, `ui.header`, `ui.panel`, `ui.row`, `ui.column`, `ui.box`, and semantic widgets over manual ANSI printing. Distinguish **layout containers**, **focusable widgets** (unique IDs), and **layers** (overlays). Use `intent` for button semantics and semantic theme recipes instead of hard-coded colors when possible.
4. **Handle keyboard and focus.** Register shortcuts through `app.keys(...)`; use stable focus IDs; ensure modal focus trapping and restoration; be deliberate about input-widget shortcuts and dismissal. Consult `references/workflows/rezi-keybindings.md` and `references/workflows/rezi-modal-dialogs.md`.
5. **Choose presentation mode correctly.** `config.screen = { mode: "alt" }` means fullscreen alternate buffer; `{ mode: "inline", inlineRows: N }` preserves terminal scrollback. **Do not confuse** `screen.mode: "inline"` with `executionMode: "inline"` (backend execution location).
6. **Test the user-facing behavior** (state, render, focus, input, errors) rather than implementation details. Use headless rendering where sufficient; if a bug depends on real terminal behavior, add PTY/e2e evidence when feasible.
7. **Report precise verification**: what changed, commands actually executed, what passed/failed, and untested terminal/platform paths.

### Minimal, verified-from-source application pattern

This pattern is adapted from `examples/hello-counter/src/index.ts` in the supplied repository:

```ts
import { ui } from "@rezi-ui/core";
import { createNodeApp } from "@rezi-ui/node";

type State = { count: number };
const app = createNodeApp<State>({ initialState: { count: 0 } });

app.view((state) =>
  ui.page({
    p: 1,
    gap: 1,
    header: ui.header({ title: "Counter" }),
    body: ui.panel("Counter", [
      ui.row({ gap: 1, items: "center" }, [
        ui.text(`Count: ${state.count}`, { variant: "heading" }),
        ui.button({
          id: "increment",
          label: "+1",
          intent: "primary",
          onPress: () => app.update((prev) => ({ ...prev, count: prev.count + 1 })),
        }),
      ]),
    ]),
  }),
);

app.keys({ q: () => app.stop() });
await app.run();
```

**Important**: `onPress` is for `ui.button`; APIs such as `ui.input` use their own typed callbacks. Do not invent callback names, event structures, or factory signatures—check local widget type declarations and examples.

## Selective recipe index

Open **only** the relevant reference(s); do not load all ten workflows by default.

| Task | Open this bundled reference | Then check the current repo's source |
|---|---|---|
| Build a screen/page | `references/workflows/rezi-create-screen.md` | `packages/create-rezi/templates/`, `packages/core/src/widgets/ui.ts` |
| Add a custom core widget | `references/workflows/rezi-add-widget.md` | `packages/core/src/widgets/types/`, layout/render handlers, exports |
| Multi-screen routing/guards | `references/workflows/rezi-routing.md` | `packages/core/src/router/` |
| Keyboard shortcuts/focus | `references/workflows/rezi-keybindings.md` | `packages/core/src/keybindings/` |
| Forms and validation | `references/workflows/rezi-forms.md` | `packages/core/src/forms/`, widget types |
| Data tables, sorting/selection | `references/workflows/rezi-data-table.md` | table widget, events, test fixtures |
| Modal dialogs/overlays | `references/workflows/rezi-modal-dialogs.md` | overlay widgets, focus management |
| Widget/app behavior tests | `references/workflows/rezi-write-tests.md` | `packages/core/src/testing/`, neighboring tests |
| Layout/drawlist/debug | `references/workflows/rezi-debug-rendering.md` | layout, renderer, backend |
| Diagnose slowness | `references/workflows/rezi-perf-profiling.md` | widget renderer, bench scripts |

Bundled guides provide more context: `references/docs/quickstart.md`, `recommended-patterns.md`, `widget-catalog.md`, `input-and-focus.md`, `routing.md`, `testing.md`, `screen-modes.md`, `widget-authoring.md`, `code-standards.md`, and `design-system.md`. These are snapshots from the supplied repository; prefer any newer local copies.

## Framework-contribution guardrails

- Keep `@rezi-ui/core` runtime-agnostic: no `node:*`, `Buffer`, or `worker_threads` imports. Node/Bun terminal I/O belongs to `@rezi-ui/node`.
- Edit canonical widget types/factories and all affected layout/render/input code. Keep `@rezi-ui/jsx` in parity where applicable. Update public exports, docs, and tests for a changed public API.
- Do not hand-edit generated drawlist writers. When drawlist bytes/fields change: update `scripts/drawlist-spec.ts`, run `npm run codegen` and `npm run codegen:check`, update protocol documentation and tests.
- Follow deterministic layout/reconciliation, immutable state, callback safety, async cancellation, and degradation behavior. Use keyed list items and virtualize large collections when appropriate.
- Respect the source repository's `docs/dev/testing.md` policy: choose the lowest-fidelity test that proves the behavior; PTY is needed when the contract depends on actual terminal I/O.

### Validation commands

**In a generated or consumer app**, inspect `package.json` scripts first and run the appropriate build/typecheck/tests. Do not assume framework monorepo commands exist there.

**In the Rezi source monorepo**:

```bash
npm ci
npm run build
npm test
npm run test:e2e                   # when real terminal interactions change
npm run check:core-portability    # when core imports/boundaries change
npm run codegen:check             # when drawlist protocol changes
```

For a focused Rezi test, the repository also provides:

```bash
node scripts/run-tests.mjs --filter "widget"
```

Do not claim that tests passed unless they were actually run. If a native dependency or terminal is unavailable, specify the limitation and report the checks that were possible.

## Finish every implementation with

A concise summary of affected files and observable behavior, tests actually run (including errors), relevant compatibility notes, and remaining issues. Do not fabricate performance measurements, package capabilities, or terminal support.
