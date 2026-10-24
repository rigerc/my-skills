---
name: vhs-cli
description: Create and verify reproducible terminal recordings using Charmbracelet VHS. Use for .tape authoring, CLI/TUI demos, GIF/MP4/WebM recording, terminal screenshots, and ASCII golden fixtures. Offers simple (lint without rendering) and expanded (render, inspect, review) workflows.
---

# VHS CLI

Write terminal recordings as deterministic `.tape` files using [Charmbracelet VHS](https://github.com/charmbracelet/vhs). Choose the appropriate workflow **before** acting. Keep the recording sandboxed, use fixtures, and never display real credentials.

## Choose a workflow

**Simple — validate only**: Use when the user asks for a tape, quick edit, syntax sanity check, or the rendering environment is unavailable. Write/update the tape, run the preflight linter, fix reported errors, optionally run `vhs manual` to confirm uncertain syntax. Deliver the `.tape` file. **Do not claim the VHS parser accepted it or that output was rendered.**

```sh
python3 scripts/run_workflow.py simple path/to/demo.tape
# or strict: warnings fail
python3 scripts/run_workflow.py simple path/to/demo.tape --strict
```

**Expanded — render and inspect**: Use when the user requests an actual GIF/video/screenshot, asks for quality review, or explicitly wants a tested recording. Begin with the simple checks, check dependencies, run VHS, inspect all requested outputs, view the output/contact sheet when an image viewer is available, then revise and rerender if necessary.

```sh
python3 scripts/run_workflow.py expanded path/to/demo.tape
# For a single GIF or PNG, create a sampled-frame contact sheet:
python3 scripts/run_workflow.py expanded path/to/demo.tape --contact-sheet path/to/contact.png
```

The scripts are relative to this installed skill directory; invoke them with their actual paths. `expanded` requires `vhs`, `ttyd`, and `ffmpeg` on PATH; image metadata and contact sheets require Pillow, while MP4/WebM metadata benefits from `ffprobe`. When inspection dependencies are unavailable, report partial inspection rather than a clean bill of health.

## Authoring process (both workflows)

1. Inspect the repository, existing `.tape` files, README instructions, target command help, and available fixture data. Identify output formats, working directory, CLI versus interactive TUI, and expected visible success markers.
2. Run the intended demo steps safely **before writing the tape**, if the tool is available. Prefer deterministic sample input and a throwaway project directory. Do not execute untrusted commands without appropriate review.
3. Start from the closest template under `assets/templates/`; place `Output`, `Require`, and initial `Set` instructions in the header.
4. Type commands with `Type` + `Enter`; use `Wait+Line` or `Wait+Screen` with **specific output markers** for synchronization. Use `Sleep` only for pacing and final hold. `Wait` defaults to checking the last line, and screen content (including echoed commands) can cause early matches.
5. Set font, dimensions, and theme for legibility. Never mix `Width` with `Columns`, or `Height` with `Rows`. `Set TypingSpeed` is the exception that can change after interaction starts.
6. Run the selected workflow. Fix issues and rerun until checks pass, or document limitations and deliver partial artifacts honestly.

## Expanded review contract

In addition to the successful preflight and zero exit status from VHS:

- Confirm each declared artifact exists and is nonempty; inspect duration, resolution, frame count, and stream metadata where supported.
- **Visually examine** the GIF, video, or sampled frames for unreadable type, clipping, blank opening/ending, incorrect prompts, accidental secrets, and excessively long waits. Contact sheets are a sampling aid, not automated proof of visual quality.
- For animated output, check beginning, middle, and ending frames. If the behavior depends on animation timing, play the entire animation.
- Correct the `.tape`, rerun VHS and inspect again. If the runtime cannot access the target CLI or viewer, explicitly note what was and was not checked.
- Report three distinct states: `tape linted`, `VHS rendered`, and `visually reviewed` — only claim the states actually achieved.

## VHS essentials

```tape
Output demo.gif
Set Width 1000
Set Height 500
Set FontSize 24
Set Theme "Catppuccin Frappe"
Set TypingSpeed 75ms

Type "printf 'Hello from VHS!\\n'"
Enter
Wait+Screen /Hello from VHS!/
Sleep 2s
```

`Output` supports multiple formats (e.g. GIF, MP4, WebM, PNG frames, ASCII golden files). `Require binary` fails early for missing demo dependencies. `Hide` and `Show` pause and resume capture; **they do not protect secrets stored in a tape**. `Screenshot path.png` saves the current frame. `Source another.tape` reuses commands. `Env KEY "value"` sets demo environment variables, not secret-safe storage.

Local rendering requires VHS, `ttyd`, and `ffmpeg`. Install VHS with `brew install vhs` or from its official releases; refer to official install instructions for other platforms. The official Docker image includes VHS dependencies, **not necessarily the CLI being demonstrated**:

```sh
docker run --rm -v "$PWD:/vhs" ghcr.io/charmbracelet/vhs demo.tape
```

## Reference selection

- `references/commands.md`: existing VHS command reference.
- `references/recording-patterns.md`: reliable waits, isolated setup, TUI interaction, and golden files.
- `references/troubleshooting.md`: timeouts, blank output, missing tools, rendering inspection.
- `references/ci-integration.md`: deterministic CI and Docker patterns.
- `assets/templates/`: task-specific starter tapes.

## Limits and safety

The Python linter is a **conservative heuristic**, not the official VHS parser: warnings may be false positives and valid VHS syntax may not be recognized. `simple` does not render or verify actual command behavior. Expanded inspection uses metadata checks and optional visual review; it cannot assert application correctness or comprehensive visual quality automatically. Avoid commands that modify production systems, leaked tokens, live customer data, external dependencies without pinning, and destructive cleanup outside a throwaway directory.

Official documentation: https://github.com/charmbracelet/vhs and https://github.com/charmbracelet/vhs#vhs-command-reference
