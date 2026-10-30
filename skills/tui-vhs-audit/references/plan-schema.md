# Audit plan schema

A UTF-8 JSON file with these required top-level fields:

| Field | Type | Meaning |
|---|---|---|
| `app_id` | slug | Name used in reports (letters, digits, hyphens, underscores). |
| `cwd` | path (optional, default `.`) | Target working directory, **relative to the plan file**, not the generated tapes. Must exist. |
| `launch` | string | Non-empty shell command used to launch TUI, e.g. `python3 -m my_app --fixture demo`. It is not escaped as a single executable; it is intentionally a shell command. |
| `viewports` | array | One or more `{id, width, height, font_size}` objects (pixel width/height, font pixel size). |
| `scenarios` | array | One or more `{id, description?, steps, exit_actions?}` objects. |

Each `steps` member has:

| Field | Type | Meaning |
|---|---|---|
| `id` | slug | Unique within scenario; used in screenshot filename. |
| `actions` | list (optional) | Consecutive keyboard operations, see below. |
| `wait_for` | string (optional) | Literal text to match anywhere on screen via `Wait+Screen`. The generator escapes regular-expression metacharacters. A unique marker is best. |
| `settle_ms` | int (optional) | Milliseconds before wait/screenshot; defaults to `250` (0–30000). |
| `screenshot` | bool (optional) | Capture current state, default `true`. |
| `inspect_for` | string (optional) | Short note to reviewer, added to report coverage table. |

Actions take one of these shapes: `{"key":"Down"}`, `{"key":"Tab", "repeat":2}`, `{"key":"Ctrl+C"}`, or `{"text":"?"}`. Text is typed into the terminal; it is not pasted through the OS clipboard. Supported keys are arrows, Enter, Escape, Tab, Backspace, Delete, Insert, Space, PageUp, PageDown, ScrollUp/ScrollDown, or control/alt/shift combinations such as `Ctrl+C`. Repeat is 1–30.

Scenario-level `exit_actions` defaults to `[{"key":"Ctrl+C"}]`; use a different sequence if the TUI has a safe quit command, or `[]` if the app must be left running. The final action occurs after all screenshots.

Scenario and viewport IDs must also produce unique combined `<scenario>--<viewport>` names. Plans with colliding names are rejected before writing or replacing any audit files.

Generated layout for a plan with a `navigation` scenario and a `small` viewport:

```text
audit-out/
  manifest.json
  navigation--small/
    audit.tape
    recording.gif           # after successful VHS render
    screens/
      01-start.png           # after successful VHS render
      02-selected.png
  render-results.json        # after run
  inspection.json            # after inspect
  contact-sheet.png          # after inspect with Pillow installed
  audit-report.md            # report scaffold, not a completed review
```

The generated tapes use `Output recording.gif` because VHS expects an output and the GIF helps debug timing; PNG screenshots are the primary evidence. Audit output directories should be outside the application repository when possible to avoid recursive test fixtures and accidental commits.

Each screenshot is followed by a 250ms pause so VHS can capture its queued frame before the next action or exit. This pause is independent of the step's `settle_ms`.

## Suggested coverage plan

- Desktop initial screen → first-level selection → detail → escape/back.
- Small viewport initial screen → keyboard focus → help/modal → dismiss.
- If supported, empty dataset / validation error / loading or spinner / long list / search with zero results.
- Sample at least one screen after scrolling or pagination when a view is longer than the terminal.

For noninteractive command-line apps, use the provided `vhs-cli` workflow instead of this TUI-focused capture matrix.
