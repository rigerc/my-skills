# tui-vhs-audit skill

A portable agent skill that extends a VHS recording workflow into a reproducible TUI visual audit: plan states, capture screenshots, inventory PNGs, review visual defects and report findings with evidence.

## Quick start

```sh
# Run from this skill's root directory.
python3 scripts/audit_tui.py prepare examples/demo-plan.json

# Review the generated audit.tape files, then run with VHS installed:
python3 scripts/audit_tui.py run --yes

# Create contact sheet and report scaffold:
python3 scripts/audit_tui.py inspect
```

By default, the tool stores tapes, GIFs, screenshots, and reports under `<audited Git repository>/.tui-audit/` and adds `/.tui-audit/` to that repository's root `.gitignore` if needed. `prepare` finds the repository from the plan's `cwd`; `run` and `inspect` find it from the current working directory. Execute `run` and `inspect` from inside the audited repository. `--out PATH` is available for legacy/custom workflows; when using it, you are responsible for ignoring that location.

Modify `examples/demo-plan.json` to launch your own application in a fixture environment. The example uses `examples/demo_tui.py` so it can run without external application dependencies on Unix-like systems. The tool does not automatically evaluate screenshots as visually correct: inspect the PNGs and complete `audit-report.md` using `references/audit-rubric.md`.

**Dependencies:** Python 3.10+; VHS, ttyd and ffmpeg for rendering; Pillow optionally for contact sheets. No pip packages needed for plan generation or basic screenshot inventory.

A second `inspect` preserves existing `audit-report.md` and writes `audit-report.new.md`; pass `--overwrite-report` to replace it intentionally.

An authorized `run` clears the whole batch's previous screenshots, recordings, and generated inventory before capturing again, so skipped runs cannot retain stale evidence. `prepare --force` and `run` preserve an existing edited `audit-report.md`; later `inspect` writes an `audit-report.new.md` scaffold. Review new captures and update the report after each rerun.

**Testing:** `python3 -m unittest discover -s tests -v`
