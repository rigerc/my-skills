---
name: tui-vhs-audit
description: Audit terminal user interfaces (TUIs) by scripting realistic keyboard journeys with Charmbracelet VHS, taking named PNG screenshots at key states and viewport sizes, visually reviewing layout and accessibility, and delivering evidence-backed findings. Use for TUI visual QA, regressions, navigation audits, clipping/overflow checks, empty/error/help states, or terminal UI screenshot requests.
---

# Audit TUI applications with VHS screenshots

Use a **capture → inspect → reproduce → report** loop. VHS's `Screenshot` directive captures a PNG of the visible terminal; keyboard actions and `Wait+Screen` make screen states reproducible. **A valid PNG is evidence that a frame was captured, not evidence that the UI is correct.** You MUST open and inspect the resulting screenshots (or contact sheet followed by individual frames) before recording findings or claiming visual review.

## Workflow

1. **Understand the target.** Inspect its README, launch flags, keybindings, fixtures, and existing tests. Identify a safe, reproducible command, working directory, the default and narrow viewport sizes, and visible state markers. Prefer deterministic data. Ask for information only if the app truly cannot be located or launched; otherwise proceed with available context.
2. **Decide coverage.** Plan initial, focus/selection, navigation, help/modal, and empty/error/loading/long-content states as applicable. Run a desktop and constrained viewport. Add steps for keyboard-only paths and tab order. Test a failure path when fixture data permits. Refer to [audit rubric](references/audit-rubric.md).
3. **Prepare scenarios.** Create a JSON plan following [plan schema](references/plan-schema.md); see [`examples/demo-plan.json`](examples/demo-plan.json). Keep launch instructions local, fixture-backed and non-destructive. The `launch` string executes as a shell command; review it before rendering.
4. **Generate reproducible tapes:**

   ```sh
   python3 scripts/audit_tui.py prepare examples/demo-plan.json
   ```

   By default this creates `<target Git root>/.tui-audit/` with one `.tape` per scenario/viewport, `Screenshot screens/NN-state.png` directives, and a `manifest.json`. The tool adds `/.tui-audit/` to the **target repository's** root `.gitignore` if missing, without replacing existing rules. It does **not** launch the app or VHS. For `prepare`, the target repo is discovered from the plan's `cwd` (relative to the plan); `run` and `inspect` discover it from the command's current directory. Run those commands from inside the same target repository. An explicit `--out PATH` overrides this default; only the default path gets automatic ignore management.

5. **Review the generated tapes** for shell safety, correct navigation, realistic input, specific `Wait+Screen` markers and screenshot timing. Use `vhs manual` to verify version-specific syntax if necessary. When the uploaded `vhs-cli` skill is installed, you may use its `scripts/run_workflow.py simple path/to/audit.tape` for heuristic linting, but its existence is not a prerequisite.
6. **Capture screenshots (expanded workflow only):**

   ```sh
   python3 scripts/audit_tui.py run --yes
   ```

   `--yes` confirms the tapes were reviewed. This requires local `vhs`, `ttyd` and `ffmpeg`; the target app and any fixtures must also be available in the VHS shell. For batch audits, `--keep-going` continues after failures. If these dependencies are missing, deliver the tapes and explicitly say no screenshots were rendered; do **not** fabricate findings.

7. **Inventory screenshots and create audit report scaffold:**

   ```sh
   python3 scripts/audit_tui.py inspect
   ```

   Outputs `inspection.json`, `audit-report.md`, and (when Pillow is installed) `contact-sheet.png`. Inspection validates PNG existence, dimensions, and optional decode/near-blank warnings. It does not automatically decide whether text is clipped, color contrast is sufficient, or navigation works. On repeat inspection, an existing edited report is preserved and a new `audit-report.new.md` is produced; use `--overwrite-report` only when intentional. A missing capture is a **capture failure**, not automatically a defect in the app.
8. **Visually inspect each screenshot** (read/view PNGs, not just filenames or image metadata), confirm whether the intended state appeared, and revisit any suspicious screenshots at their original resolution. Check small and large viewport differences. Use keyboard recordings and the application's documented keybindings to distinguish UI failures from audit script errors. Revise the plan/tapes and recapture when needed.
9. **Deliver an evidence-backed report** by editing `audit-report.md`: summary, tested versions/terminal sizes, coverage, critical/high/medium/low findings, direct screenshot links, exact reproduction steps, observed vs expected behavior, recommended fix and remaining untested areas. Indicate separately: *tapes prepared*, *VHS successfully rendered*, *screenshots inventoried*, *screenshots visually reviewed*. Never mark a state as visually reviewed if you have only inspected metadata.

## VHS tape pattern

```tape
Output recording.gif
Set Shell bash
Set Width 1100
Set Height 650
Set FontSize 20
Set TypingSpeed 1ms

Type "./my-tui --sample-data"
Enter
Wait+Screen /Dashboard/
Sleep 250ms
Screenshot screens/01-dashboard.png
Sleep 250ms

Down
Sleep 250ms
Wait+Screen /Details/
Screenshot screens/02-selection.png
Sleep 250ms

Type "?"
Wait+Screen /Help/
Screenshot screens/03-help.png
Sleep 250ms
Ctrl+C
```

The screenshots are the primary audit artifacts; the recording GIF is optional supporting evidence automatically generated by these tapes. The generator creates screenshot directories in advance and runs VHS from each tape directory so paths are deterministic. **Do not assert the sample markers or keybindings exist in another app.** Replace them after inspecting the real application.

## Review principles

- **Reproduction:** Each finding needs an exact viewport, scenario, key sequence, and PNG. Prioritize demonstrable user impact over cosmetic preferences.
- **Visual quality:** Inspect clipped headings, long labels, borders, scroll indicators, columns, input field widths, focus cues, selected state, disabled state, overlays, prompt/cursor visibility, contrast, and empty/error messages. See `references/audit-rubric.md`.
- **Terminal realities:** Pixel sizes and font size determine the character grid. Test small viewports and long content; colors depend on theme/terminal rendering. Mouse-dependent behavior is outside this keyboard-centered workflow.
- **Output hygiene:** Generated tapes, GIFs, PNGs, reports, logs and contact sheets live under `<target repo>/.tui-audit/` by default, excluded from Git by the root ignore rule. Review screenshots in that directory and do not commit evidence containing sensitive information. A custom `--out` is an opt-out: configure its ignore rules yourself.
- **Timing:** Prefer `Wait+Screen /unique-state-marker/` to arbitrary sleeps. A marker already visible before an action can cause a false pass; add a short settling delay and stronger state marker. Some applications require longer startup. VHS `Wait` generally defaults to a 15-second timeout. Keep a short pause after each `Screenshot`: VHS queues capture of the next frame, so immediate input or exit can change or lose the captured state. The generator adds 250ms after each screenshot.
- **Safety:** Treat tapes like shell scripts. Never run unknown commands, mutating production actions, live secrets, privileged commands, clipboard-sensitive steps or untrusted remote code. Use disposable data. `Hide` only suppresses video frames and is **not** secret redaction.
- **Honest limitations:** Static screenshots cannot verify animation, screen-reader behavior, full keyboard accessibility, actual color-contrast ratios, application state persistence or business-logic correctness. Use additional tests when those outcomes matter.

## Contents

- `scripts/audit_tui.py`: plan preparation, explicit local rendering and screenshot inventory/report generation.
- `examples/demo-plan.json` and `examples/demo_tui.py`: a self-contained example; the tiny example TUI is not the user's target.
- `references/plan-schema.md`: supported JSON fields and recording behavior.
- `references/audit-rubric.md`: test coverage and severity grading.
- `references/troubleshooting.md`: TUI/VHS capture issues and interpreting failures.
- `tests/test_audit_tui.py`: no-VHS unit tests for plan validation, tape generation, and PNG inspection.

**Sources:** [VHS official README / command reference](https://github.com/charmbracelet/vhs#vhs-command-reference), [VHS queued screenshot implementation](https://github.com/charmbracelet/vhs/blob/v0.12.1/screenshot.go#L44-L48). This skill complements, but does not require, the provided `vhs-cli` skill.
